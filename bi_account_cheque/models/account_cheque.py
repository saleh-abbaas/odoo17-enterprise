# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
import odoo.addons.decimal_precision as dp
from datetime import date, datetime
from odoo.exceptions import UserError
import json
from odoo.tools import float_is_zero, float_compare
import ast

class AccountCheque(models.Model):
	_name = "account.cheque"
	_description = 'Account Cheque'
	_order = 'id desc'

	sequence = fields.Char(string='Sequence', readonly=True ,copy=True, index=True)
	name = fields.Char(string="Name", required=True)
	bank_account_id = fields.Many2one('account.account','Bank Account')
	account_cheque_type = fields.Selection([('incoming','Incoming'),('outgoing','Outgoing')],string="Cheque Type")
	cheque_number = fields.Char(string="Cheque Number",required=True)
	re_amount = fields.Float(string="Remaining Amount",compute='_get_outstanding_info',)
	
	amount = fields.Float(string="Amount",required=True)
	cheque_date = fields.Date(string="Cheque Date",default=datetime.now().date())
	cheque_given_date = fields.Date(string="Cheque Given Date")
	cheque_receive_date = fields.Date(string="Cheque Receive Date")
	cheque_return_date = fields.Date(string="Cheque Return Date")
	payee_user_id = fields.Many2one('res.partner',string="Payee",required=True)
	credit_account_id = fields.Many2one('account.account',string="Credit Account")
	debit_account_id = fields.Many2one('account.account',string="Debit Account")
	comment = fields.Text(string="Comment")
	attchment_ids = fields.One2many('ir.attachment','account_cheque_id',string="Attachment")
	status = fields.Selection([('draft','Draft'),('registered','Registered'),('bounced','Bounced'),('return','Returned'),('cashed','Done'),('cancel','Cancel')],string="Status",default="draft",copy=False, tracking=True, index=True)
	
	status1 = fields.Selection([('draft','Draft'),('registered','Registered'),('bounced','Bounced'),('return','Returned'),('deposited','Deposited'),('transfered','Transfered'),('cashed','Done'),('cancel','Cancel')],string="Status ",default="draft",copy=False, tracking=True, index=True)
	
	journal_id = fields.Many2one('account.journal',string="Journal",required=True)
	company_id = fields.Many2one('res.company',string="Company",required=True)
	journal_items_count =  fields.Integer(compute='_active_journal_items',string="Journal Items") 
	invoice_ids = fields.One2many('account.move','account_cheque_id',string="Invoices",compute="_count_account_invoice")
	attachment_count  =  fields.Integer('Attachments', compute='_get_attachment_count')
	in_count = fields.Boolean('Incoice',compute='_get_in_count')
	is_partial = fields.Boolean(string='Not reconciled')

	def _valid_field_parameter(self, field, name):
		# EXTENDS models
		return name == 'tracking' or super()._valid_field_parameter(field, name)

	
	@api.model 
	def default_get(self, flds): 
		result = super(AccountCheque, self).default_get(flds)
		res = self.env.user.company_id
		user_company_id = self.env.user.company_id
		if self._context.get('default_account_cheque_type') == 'incoming':
			result['credit_account_id'] = user_company_id.in_credit_account_id.id
			result['debit_account_id'] = user_company_id.in_debit_account_id.id
			result['journal_id'] = user_company_id.specific_journal_id.id
			result['company_id'] = user_company_id.id
		else:
			result['credit_account_id'] = user_company_id.out_credit_account_id.id
			result['debit_account_id'] = user_company_id.out_debit_account_id.id
			result['journal_id'] = user_company_id.specific_journal_id.id 
			result['company_id'] = user_company_id.id
		return result 
		
	
	def open_payment_matching_screen(self):

		# Open reconciliation view for customers/suppliers
		move_line_id = False
		account_move_line_ids = self.env['account.move.line'].search([('partner_id', '=', self.payee_user_id.id)])
		for move_line in account_move_line_ids:
			if move_line.account_id.reconcile:
				move_line_id = move_line.id
				break

		action_values = self.env['ir.actions.act_window']._for_xml_id('account_accountant.action_move_line_posted_unreconciled')
		action_context = {'company_ids': [self.company_id.id], 'partner_ids': [self.payee_user_id.id]}

		if self.account_cheque_type == 'incoming':
			action_context.update({'mode': 'customers'})
		elif self.account_cheque_type == 'outgoing':
			action_context.update({'mode': 'suppliers'})

		if account_move_line_ids:
			context = ast.literal_eval(action_values['context'])
			context.update({'search_default_partner_id': self.payee_user_id.id})
			action_values['context'] = context

		return action_values

	def _get_in_count(self):
		self.in_count = False
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				if self.sequence :
					ref = self.sequence + '- ' + self.cheque_number + '- ' + 'Registered'
				else:
					ref = self.cheque_number + '- ' + 'Registered'
				reference = ref
				if self.account_cheque_type == 'incoming':				
					credit_account = line.search([('ref','=',reference),('account_id','=',self.credit_account_id.id)])
					if credit_account:
						for record in credit_account:
							if record.reconciled == True:
								self.write({'status1':'cashed'})
				if self.account_cheque_type == 'outgoing':
					debit_account = line.search([('ref','=',reference),('account_id','=',self.debit_account_id.id)])
					if debit_account:
						for record in debit_account:
							if record.reconciled == True:
								self.write({'status':'cashed'})    

		if self.amount != self.re_amount:
			self.write({'is_partial':True}) 
		else:
			self.write({'is_partial':False}) 



	def _get_outstanding_info(self):

		for record in self:
			if record.account_cheque_type == 'incoming' :
				if record.status1 in ('return','deposited','transfered','cashed','bounced'):
					record.re_amount = 0.0
				else:
					record.re_amount = record.amount
			if record.account_cheque_type == 'outgoing': 
				if record.status in ('return','transfered','cashed','bounced'):
					record.re_amount = 0.0
				else:
					record.re_amount = record.amount
			for move in record.payee_user_id.invoice_ids:
				move.invoice_outstanding_credits_debits_widget = json.dumps(False)
				move.invoice_has_outstanding = False

				if move.state != 'posted' \
						or move.payment_state not in ('not_paid', 'partial') \
						or not move.is_invoice(include_receipts=True):
					continue

				pay_term_lines = move.line_ids\
					.filtered(lambda line: line.account_id.account_type in ('asset_receivable', 'liability_payable'))

				domain = [
					('account_id', 'in', pay_term_lines.account_id.ids),
					('move_id.state', '=', 'posted'),('move_id.account_cheque_id','=',record.id),
					('partner_id', '=', move.commercial_partner_id.id),
					('reconciled', '=', False),
					'|', ('amount_residual', '!=', 0.0), ('amount_residual_currency', '!=', 0.0),
				]

				payments_widget_vals = {'outstanding': True, 'content': [], 'move_id': move.id}

				if move.is_inbound():
					domain.append(('balance', '<', 0.0))
					payments_widget_vals['title'] = _('Outstanding credits')
				else:
					domain.append(('balance', '>', 0.0))
					payments_widget_vals['title'] = _('Outstanding debits')

				for lines in self.env['account.move.line'].search(domain):

					if record.account_cheque_type == 'incoming' :
						if record.status1 not in ('return','deposited','transfered','cashed','bounced'):

							for line in lines:
								# get the outstanding residual value in invoice currency
								if line.currency_id and line.currency_id == move.currency_id:
									amount_to_show = abs(line.amount_residual_currency)
								else:
									currency = line.company_id.currency_id
									amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
																	   line.date or fields.Date.today())
									
								if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
									continue
								record.re_amount = amount_to_show
					if record.account_cheque_type == 'outgoing' :
						if record.status not in ('return','transfered','cashed','bounced'):
							for line in lines:
								# get the outstanding residual value in invoice currency
								if line.currency_id and line.currency_id == move.currency_id:
									amount_to_show = abs(line.amount_residual_currency)
								else:
									currency = line.company_id.currency_id
									amount_to_show = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
																	   line.date or fields.Date.today())
									
								if float_is_zero(amount_to_show, precision_rounding=move.currency_id.rounding):
									continue
								record.re_amount = amount_to_show
		
	def _count_account_invoice(self):
		invoice_list = []
		self.invoice_ids = None
		for invoice in self.payee_user_id.invoice_ids:
			if invoice.state != 'cancel':
				if invoice.payment_state != 'paid':
					if self.account_cheque_type == 'incoming':
						if invoice.move_type == 'out_invoice':
							invoice_list.append(invoice.id)
							if invoice_list:
								self.invoice_ids = [(6, 0, invoice_list)]
							else:
								self.invoice_ids = None
					if self.account_cheque_type == 'outgoing':
						if invoice.move_type == 'in_invoice':
							invoice_list.append(invoice.id)
							if invoice_list:
								self.invoice_ids = [(6, 0, invoice_list)]
							else:
								self.invoice_ids = None

			if invoice.has_reconciled_entries == True :
				if self.account_cheque_type == 'incoming' and self.status1 == 'cancel':
					invoice.button_cancel()
				if self.account_cheque_type == 'outgoing' and  self.status == 'cancel':
					invoice.button_cancel()

		return
		
	def _active_journal_items(self):
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)
		item_count = len(list_of_move_line)
		journal_items.journal_items_count = item_count
		return
		
	def action_view_jornal_items(self):
		self.ensure_one()
		list_of_move_line = []
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
		for move in journal_item_ids:
			for line in move.line_ids:
				list_of_move_line.append(line.id)
		return {
			'name': 'Journal Items',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'account.move.line',
			'domain': [('id', 'in' , list_of_move_line)],
		}
		
	def _get_attachment_count(self):
		for cheque in self:
			attachment_ids = self.env['ir.attachment'].search([('account_cheque_id','=',cheque.id)])
			cheque.attachment_count = len(attachment_ids)
		
	def attachment_on_account_cheque(self):
		self.ensure_one()
		return {
			'name': 'Attachment.Details',
			'type': 'ir.actions.act_window',
			'view_mode': 'tree,form',
			'res_model': 'ir.attachment',
			'domain': [('account_cheque_id', '=', self.id)],
		}

		
	def set_to_submit(self):

		if self.amount:
			account_move_obj = self.env['account.move']
			move_lines = []
			if self.account_cheque_type == 'incoming':
				vals = {
						'commercial_partner_id':self.payee_user_id.id,
						'date' : self.cheque_receive_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' :self.cheque_number + '- ' + 'Registered' ,
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)

				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id, 
						'debit' : self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))

				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.credit_account_id.id, 
						'credit' : self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})

				account_move._post(soft=False)
				self.status1 = 'registered'
			else:
				vals = {
						'commercial_partner_id':self.payee_user_id.id,
						'date' : self.cheque_given_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Registered',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id, 
						'debit' : self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.credit_account_id.id, 
						'credit' : self.amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				self.status = 'registered'
			return account_move
		else:
			raise UserError(_('Please Enter Amount Of Cheque'))

	def set_to_bounced(self):
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			journal_item_ids.button_cancel()

		account_move_obj = self.env['account.move']
		move_lines = []
		if self.re_amount:
			if self.account_cheque_type == 'incoming':
				vals = {
						'date' : self.cheque_receive_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Bounced',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.credit_account_id.id, 
						'debit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.payee_user_id.property_account_receivable_id.id, 
						'credit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move.button_cancel()
				self.status1 = 'bounced'
			else:
				vals = {
						'date' : self.cheque_given_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Bounced',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.payee_user_id.property_account_payable_id.id, 
						'debit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id, 
						'credit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move.button_cancel()
				self.status = 'bounced'
			return account_move      

	def set_to_return(self):
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			journal_item_ids.button_cancel()

		account_move_obj = self.env['account.move']
		move_lines = []
		list_of_move_line = [] 
		if self.re_amount:

			for journal_items in self:
				journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			
			matching_dict = []
			for move in journal_item_ids:
				for line in move.line_ids:
					if line.full_reconcile_id:
						matching_dict.append(line)
										
			if len(matching_dict) != 0:
				rec_id = matching_dict[0].full_reconcile_id.id
				a = self.env['account.move.line'].search([('full_reconcile_id','=',rec_id)])
				
				for move_line in a:
					move_line.remove_move_reconcile()
			
			if self.account_cheque_type == 'incoming':
				vals = {
						'date' : self.cheque_receive_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Returned',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.credit_account_id.id, 
						'debit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id, 
						'credit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move.button_cancel()
				self.status1 = 'return'
				self.cheque_return_date = datetime.now().date()
			else:
				vals = {
						'date' : self.cheque_given_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Returned',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.credit_account_id.id, 
						'debit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.payee_user_id.id,
						'account_id' : self.debit_account_id.id, 
						'credit' : self.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : self.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move.button_cancel()
				self.status = 'return'
				self.cheque_return_date = datetime.now().date()
			return account_move           

				  

	def set_to_deposite(self):
		account_move_obj = self.env['account.move']
		move_lines = []
		if self.re_amount:
			if self.account_cheque_type == 'incoming':
				vals = {
						'date' : self.cheque_receive_date,
						'journal_id' : self.journal_id.id,
						'company_id' : self.company_id.id,
						'state' : 'draft',
						'ref' : self.cheque_number + '- ' + 'Deposited',
						'account_cheque_id' : self.id
				}
				account_move = account_move_obj.create(vals)
				res = self.env.user.company_id
				if res.deposite_account_id:
					debit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.env.user.company_id.deposite_account_id.id, 
							'debit' : self.re_amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, debit_vals))
					credit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.credit_account_id.id, 
							'credit' : self.re_amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, credit_vals))
				else:
					debit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.credit_account_id.id, 
							'debit' : self.re_amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, debit_vals))
					credit_vals = {
							'partner_id' : self.payee_user_id.id,
							'account_id' : self.debit_account_id.id, 
							'credit' : self.re_amount,
							'date_maturity' : datetime.now().date(),
							'move_id' : account_move.id,
							'company_id' : self.company_id.id,
					}
					move_lines.append((0, 0, credit_vals))				
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				self.status1 = 'deposited'
				return account_move          
				
	def set_to_cancel(self): 
		for journal_items in self:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			journal_item_ids.button_cancel()

		if self.account_cheque_type == 'incoming':   
			self.status1 = 'cancel' 
		else:
			self.status = 'cancel'

class ChequeWizard(models.TransientModel):
	_name = 'cheque.wizard'
	_description = 'Cheque Wizard'

	@api.model 
	def default_get(self, flds): 
		result = super(ChequeWizard, self).default_get(flds)
		account_cheque_id = self.env['account.cheque'].browse(self._context.get('active_id'))
		if account_cheque_id.account_cheque_type == 'outgoing':
			result['is_outgoing'] = True
		return result
		
	def create_cheque_entry(self):
		account_cheque = self.env['account.cheque'].browse(self._context.get('active_ids'))
		account_move_obj = self.env['account.move']
		move_lines = []
		if account_cheque.re_amount:
			if account_cheque.account_cheque_type == 'incoming':
				vals = {
						'date' : self.chequed_date,
						'journal_id' : self.cash_journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Cashed',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.debit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.bank_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				account_cheque.status1 = 'cashed'
			else:
				vals = {
						'date' : self.chequed_date,
						'journal_id' : self.cash_journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Cashed',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : account_cheque.credit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : account_cheque.payee_user_id.id,
						'account_id' : self.bank_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_move._post(soft=False)
				account_cheque.status = 'cashed'
			return account_move

	cash_journal_id = fields.Many2one('account.journal',string="Cash Journal",required=True,domain=[('type', '=', 'cash')])
	chequed_date = fields.Date(string="Cheque Date")
	bank_account_id = fields.Many2one('account.account',string="Bank Account")
	is_outgoing = fields.Boolean(string="Is Outgoing",default=False)
	
class ChequeTransferedWizard(models.TransientModel):
	_name = 'cheque.transfered.wizard'
	_description = 'Cheque Transfered Wizard'

	def create_ckeck_transfer_entry(self):
		account_cheque = self.env['account.cheque'].browse(self._context.get('active_ids'))
		account_move_obj = self.env['account.move']
		move_lines = []
		for journal_items in account_cheque:
			journal_item_ids = self.env['account.move'].search([('account_cheque_id','=',journal_items.id)])
			journal_item_ids.button_cancel()

		if account_cheque.re_amount:
			if account_cheque.account_cheque_type == 'incoming':
				vals = {
						'date' : self.transfered_date,
						'journal_id' : account_cheque.journal_id.id,
						'company_id' : account_cheque.company_id.id,
						'state' : 'draft',
						'ref' : account_cheque.cheque_number + '- ' + 'Transfered',
						'account_cheque_id' : account_cheque.id
				}
				account_move = account_move_obj.create(vals)
				debit_vals = {
						'partner_id' : self.contact_id.id,
						'account_id' : account_cheque.credit_account_id.id, 
						'debit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, debit_vals))
				credit_vals = {
						'partner_id' : self.contact_id.id,
						'account_id' : account_cheque.debit_account_id.id, 
						'credit' : account_cheque.re_amount,
						'date_maturity' : datetime.now().date(),
						'move_id' : account_move.id,
						'company_id' : account_cheque.company_id.id,
				}
				move_lines.append((0, 0, credit_vals))
				account_move.write({'line_ids' : move_lines})
				account_cheque.status1 = 'transfered'
				account_cheque.payee_user_id = self.contact_id.id
				return account_move
		
	transfered_date = fields.Date(string="Transfered Date")
	contact_id = fields.Many2one('res.partner',string="Contact")
	
class AccountMoveLine(models.Model):
	_inherit='account.move'

	account_cheque_id  =  fields.Many2one('account.cheque', 'Journal Item')


class ReportWizard(models.TransientModel):
	_name = "report.wizard"
	_description = 'Report Wizard'

	from_date = fields.Date('From Date', required = True)
	to_date = fields.Date('To Date',required = True)
	cheque_type = fields.Selection([('incoming','Incoming'),('outgoing','Outgoing')],string="Cheque Type",default='incoming')
	
	
	def submit(self):
		inc_temp = []
		out_temp = []
		temp = [] 
		
		if self.cheque_type == 'incoming':
			in_account_cheque_ids = self.env['account.cheque'].search([(str('cheque_date'),'>=',self.from_date),(str('cheque_date'),'<=',self.to_date),('account_cheque_type','=','incoming')])
		
			if not in_account_cheque_ids:
				raise UserError(_('There Is No Any Cheque Details.'))
			else:
				for inc in in_account_cheque_ids:
					temp.append(inc.id)
			
		if self.cheque_type == 'outgoing':
			out_account_cheque_ids = self.env['account.cheque'].search([(str('cheque_date'),'>=',self.from_date),(str('cheque_date'),'<=',self.to_date),('account_cheque_type','=','outgoing')])
			
			if not out_account_cheque_ids:
				raise UserError(_('There Is No Any Cheque Details.'))
			else:
				for out in out_account_cheque_ids:
					temp.append(out.id)
							   
		data = temp
		in_data = inc_temp
		out_data = out_temp
		datas = {
			'ids': self._ids,
			'model': 'account.cheque',
			'form': data,
			'from_date':self.from_date,
			'to_date':self.to_date,
			'cheque_type' : self.cheque_type,
		}
		return self.env.ref('bi_account_cheque.account_cheque_report_id').report_action(self,data=datas)

class IrAttachment(models.Model):
	_inherit='ir.attachment'

	account_cheque_id  =  fields.Many2one('account.cheque', 'Attchments')
	
