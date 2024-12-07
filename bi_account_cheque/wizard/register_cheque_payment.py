# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from odoo.http import request
from datetime import timedelta,date


	
class RegisterChequePayment(models.TransientModel):
	_name = "register.cheque.payment"
	_description = "Register Cheque Payment Wizard" 


	partner_id = fields.Many2one('res.partner',string="Partner")
	payment_amount = fields.Float("Payment Amount")
	currency_id = fields.Many2one('res.currency',string="Currency",default=lambda self:self.env.user.company_id.currency_id)
	cheque_reference = fields.Char("Cheque Reference",required=True)
	cheque_number = fields.Char("Cheque Number",required=True)
	journal_id = fields.Many2one('account.journal',string="Payment Journal",domain=[('cheque_payment','=',True)],required=True)

	payment_date = fields.Date("Payment Date",default=fields.Date.today(),required=True)
	received_date = fields.Date("Received/Given  Date",required=True)
	credit_account_id = fields.Many2one('account.account',string="Credit Account")
	debit_account_id = fields.Many2one('account.account',string="Debit Account")
	bank_account_id = fields.Many2one('account.account',string="Bank Account")



	
	@api.model
	def default_get(self, fields):
		rec = super(RegisterChequePayment, self).default_get(fields)
		active_ids = self._context.get('active_ids')
		active_model = self._context.get('active_model')
		invoice_type= self._context.get('invoice_obj.default_type')
		# Check for selected invoices ids
		if not active_ids or active_model != 'account.move':
			return rec
		invoice = self.env['account.move'].browse(active_ids)
		user_company_id = self.env.user.company_id
		res = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
		
		if invoice.move_type =='out_invoice':     
			rec.update({'partner_id':invoice.partner_id.id,
						'payment_amount':invoice.amount_residual,
						'bank_account_id' : user_company_id.pdc_for_customer.id,
						})
		else:
			rec.update({'partner_id':invoice.partner_id.id,
						'payment_amount':invoice.amount_residual,
						'bank_account_id' : user_company_id.pdc_for_vendor.id,
						})
		return rec


	def create_register_cheque(self):
		invoice_obj = self.env['account.cheque']
		active_ids = self._context.get('active_ids')
		invoice = self.env['account.move'].browse(active_ids)
		user_company_id = self.env.user.company_id
		res = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
		
		if invoice.move_type == 'out_invoice':
			invoice_create_obj = invoice_obj.create({
								'account_cheque_type':'incoming',
								'payee_user_id': self.partner_id.id,
								'amount': self.payment_amount,
								'bank_account_id': self.bank_account_id.id,
								'name': self.cheque_reference,
								'cheque_number': self.cheque_number,
								'cheque_receive_date' :self.received_date,
								'journal_id':self.journal_id.id,
								'credit_account_id':user_company_id.in_credit_account_id.id,
								'debit_account_id':user_company_id.in_debit_account_id.id,
						})
			return {
					'res_model':'account.cheque',
					'view_mode':'form',
					'view_id':self.env.ref("bi_account_cheque.account_incoming_cheque_form_view").id,
					'res_id': invoice_create_obj.id,
					'target':'current',
					'type':'ir.actions.act_window'
			}	
		else: 

			invoice_create = invoice_obj.create({
									'account_cheque_type':'outgoing',
									'payee_user_id': self.partner_id.id,
									'amount': self.payment_amount,
									'bank_account_id': self.bank_account_id.id,
									'name': self.cheque_reference,
									'cheque_number': self.cheque_number,
									'cheque_given_date' :self.received_date,
									'journal_id':self.journal_id.id,
									'credit_account_id':user_company_id.out_credit_account_id.id,
									'debit_account_id':user_company_id.out_debit_account_id.id,
							})
			return {
					'res_model':'account.cheque',
					'view_mode':'form',
					'view_id':self.env.ref("bi_account_cheque.account_outgoing_cheque_form_view").id,
					'res_id': invoice_create.id,
					'target':'current',
					'type':'ir.actions.act_window'
			}   

			



			
				
			
		
		
	