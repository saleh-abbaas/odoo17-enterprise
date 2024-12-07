# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _


class DynamicCheque(models.Model):
	_name = "dynamic.cheque"
	_description = 'Dynamic Cheque'
	_rec_name = "cheque_name"



	cheque_name = fields.Char(string="Cheque Format",required=True)
	cheque_height = fields.Float(string="Height")
	cheque_width = fields.Float(string="Width")
	account_pay = fields.Boolean(string="A/C Pay")
	account_top_margin = fields.Float(string="Top Margin")
	account_left_margin = fields.Float(string="Left Margin")
	account_font = fields.Float(string="Font Size")
	cheque_top_margin = fields.Float(string="Top Margin ")
	cheque_left_margin = fields.Float(string="Left Margin ")
	cheque_font = fields.Float(string="Font Size ")
	cheque_char_speace = fields.Float(string="Character Spacing")
	payee_top_margin = fields.Float(string="Top Margin  ")
	payee_left_margin = fields.Float(string="Left Margin  ")
	payee_width = fields.Float(string="Width ")
	payee_font = fields.Float(string="Font Size  ")
	amount_first_tmargin = fields.Float(string="First Line Top Margin")
	amount_first_lmargin = fields.Float(string="First Line Left Margin")
	amount_first_line_width = fields.Float(string="First Line Width")
	amount_word_fline= fields.Integer(string="No. of Word in First Line")
	amount_second_tmargin = fields.Float(string="Second Line Top Margin")
	amount_second_lmargin = fields.Float(string="Second Line Left Margin")
	amount_second_line_width = fields.Float(string="Second Line Width")
	amount_word_sline= fields.Integer(string="No. of Word in Second Line")
	amount_font = fields.Float(string="Font Size   ")
	currency_name = fields.Boolean(string="Currency Name")
	currency_name_position = fields.Selection([('before','Before'),('after','After')],string="Currency Name Position", default='before')
	af_top_tmargin = fields.Float(string="Top Margin   ")
	af_left_tmargin = fields.Float(string="Left Margin   ")
	af_width = fields.Float(string="Width  ")
	af_font = fields.Float(string="Font Size    ")
	currency_symbol = fields.Boolean(string="Currency Symbol")
	currency_symbol_position = fields.Selection([('before','Before'),('after','After')],string="Currency Symbol Position", default='before')
	company_name = fields.Boolean(string="Company Name")
	company_font = fields.Float(string="Font Size     ")
	company_top_margin = fields.Float(string="Top Margin    ")
	company_left_margin = fields.Float(string="Left Margin    ")
	signature_width = fields.Float(string="Width   ")
	signature_height = fields.Float(string="Height ")
	signature_top_margin = fields.Float(string="Top Margin     ")
	signature_left_margin = fields.Float(string="Left Margin     ")
	signature_image_medium = fields.Binary(string="Signature Logo")
	

class report_paperformat(models.Model):
	_inherit = "report.paperformat"

	custom_report = fields.Boolean('Temp Formats', default=False)




# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: