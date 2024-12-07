# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class DynamicChequeReportWizard(models.TransientModel):
	_name = 'dynamic.cheque.report.wizard'
	_description = "Print Dynamic Cheque Report"


	

	@api.model
	def default_get(self, fields):
		res = super(DynamicChequeReportWizard, self).default_get(fields)
		cheque_format_id = self.env['dynamic.cheque'].search([], limit=1)
		res.update({'cheque_format': cheque_format_id.id})
		return res


	cheque_id = fields.Many2one('account.cheque', string='Cheque Id')	
	cheque_format = fields.Many2one('dynamic.cheque', string='Cheque Format', required = True)


	def dynamic_cheque_button(self):
		self._create_paper_format()
		data = self.read()
		datas = {
			 'ids': self._context.get('active_ids',[]),
			 'model': 'dynamic.cheque.report.wizard',
			 'form': data
		}
		return self.env.ref('bi_account_cheque.dynamic_cheque_report').report_action(self, data=datas)

	@api.model
	def _create_paper_format(self):
		report_action_id = self.env['ir.actions.report'].search([('report_name', '=', 'bi_account_cheque.custom_report')])
		if not report_action_id:
			raise ValidationError('Someone has deleted the reference view of report, Please Update the module!')
		config_rec = self.env['dynamic.cheque'].search([], limit=1)
		if not config_rec:
			raise ValidationError(_("Report format not found! Please Update Module."))
		page_height = self.cheque_format.cheque_height or 80	
		page_width = self.cheque_format.cheque_width or 180

		margin_top =  5
		margin_bottom =  10
		margin_left =  10
		margin_right =  10
		dpi =  90
		header_spacing =  0
		orientation = 'Portrait'
		self._cr.execute(""" DELETE FROM report_paperformat WHERE custom_report=TRUE""")
		paperformat_id = self.env['report.paperformat'].create({
			'name': 'Custom Report',
			'format': 'A4',
			'page_height': 0.0,
			'page_width': 0.0,
			'dpi': dpi,
			'custom_report': True,
			'margin_top': margin_top,
			'margin_bottom': margin_bottom,
			'margin_left': margin_left,
			'margin_right': margin_right,
			'header_spacing': header_spacing,
			'orientation': orientation,
		})
		report_action_id.write({'paperformat_id': paperformat_id.id})
		return True
 
	