# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    pdc_cheque = fields.Boolean(string="Allow PDC Option")
    
    @api.model
    def default_get(self, flds):
        result = super(AccountMoveInherit, self).default_get(flds)
        res = self.env['res.config.settings'].sudo().search([], limit=1, order="id desc")
        user_company_id = self.env.user.company_id
        result['pdc_cheque'] = user_company_id.pdc_cheque
        return result 


class AccountJournalInherit(models.Model):
    _inherit = 'account.journal'

    cheque_payment = fields.Boolean(string="Cheque Payment")
