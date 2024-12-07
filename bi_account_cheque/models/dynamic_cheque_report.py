# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _
from num2words import num2words
import re

class DynamicChequeReport(models.AbstractModel):
	_name='report.bi_account_cheque.custom_report'
	_description="Dynamic Cheque Report "


	def get_payment_account_invoice(self, payment_id):
		invoice_ids = self.env['account.move'].search([('id', 'in', payment_id.reconciled_bill_ids.ids)])
		return invoice_ids



	def get_amount_in_word_line(self, cheque_id, cheque_format):
		amount = str("{0:.2f}".format(cheque_id.amount))    
		split_amount  = amount.split(".")
		first_amount_n2w = num2words(split_amount[0],lang=self._context.get('lang'))
		if split_amount[1] != "00":
			amount_word = first_amount_n2w + " Rupees " + num2words(split_amount[1], lang=self._context.get('lang')) + " paisa "
		else:
			amount_word = first_amount_n2w
		first_line = (amount_word[0:cheque_format.amount_word_fline])
		s1 = cheque_format.amount_word_fline
		s2 = cheque_format.amount_word_fline + cheque_format.amount_word_sline
		second_line = (amount_word[s1:s2])
		localdict = {
			'first_line' : first_line,
			'second_line': second_line
		}
		return localdict


	def _get_report_values(self, docids, data=None):
		active_ids = data.get('ids')
		wizard_id = data.get('form')[0]
		docids = wizard_id.get('id')
		wizard  = self.env['dynamic.cheque.report.wizard'].browse(docids)
		cheque_id = self.env['account.cheque'].browse(active_ids)
		return {
				'doc_model': 'dynamic.cheque',
				'cheque_format' : wizard.cheque_format,
				'cheque_id' : cheque_id,
				'get_account_invoice': self.get_payment_account_invoice,
				'get_amount_in_word_line': self.get_amount_in_word_line,
				}