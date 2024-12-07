# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from ast import literal_eval


class Company(models.Model):
    _inherit = 'res.company'
	
    in_credit_account_id = fields.Many2one('account.account',string="Credit Account")
    in_debit_account_id = fields.Many2one('account.account',string="Debit Account")
    
    out_credit_account_id = fields.Many2one('account.account',string="Credit Account ")
    out_debit_account_id = fields.Many2one('account.account',string="Debit Account ")
    
    deposite_account_id = fields.Many2one('account.account',string="Deposite Account")
    specific_journal_id = fields.Many2one('account.journal',string="Specific Journal")

    pdc_for_customer = fields.Many2one('account.account', string="PDC Account for customer")
    pdc_for_vendor = fields.Many2one('account.account', string="PDC Account for Vendor")
    pdc_cheque = fields.Boolean(string="Allow PDC Option")
    	        
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    in_credit_account_id = fields.Many2one('account.account',string="Credit Account",related="company_id.in_credit_account_id",readonly=False)
    in_debit_account_id = fields.Many2one('account.account',string="Debit Account",related="company_id.in_debit_account_id",readonly=False)
    
    out_credit_account_id = fields.Many2one('account.account',string="Credit Account ",related="company_id.out_credit_account_id",readonly=False)
    out_debit_account_id = fields.Many2one('account.account',string="Debit Account ",related="company_id.out_debit_account_id",readonly=False)
    
    # out_credit_account_id = fields.Many2one('account.account', string="Outgoing Credit Account", related="company_id.out_credit_account_id", readonly=False)
    # out_debit_account_id = fields.Many2one('account.account', string="Outgoing Debit Account", related="company_id.out_debit_account_id", readonly=False)


    deposite_account_id = fields.Many2one('account.account',string="Deposite Account",related="company_id.deposite_account_id",readonly=False)
    specific_journal_id = fields.Many2one('account.journal',string="Specific Journal",related="company_id.specific_journal_id",readonly=False)

    pdc_for_customer = fields.Many2one('account.account', string="PDC Account For Customer",related="company_id.pdc_for_customer",readonly=False)
    pdc_for_vendor = fields.Many2one('account.account', string="PDC Account For Vendor",related="company_id.pdc_for_vendor",readonly=False)
    pdc_cheque = fields.Boolean(string="Allow PDC Option",related="company_id.pdc_cheque",readonly=False)

    