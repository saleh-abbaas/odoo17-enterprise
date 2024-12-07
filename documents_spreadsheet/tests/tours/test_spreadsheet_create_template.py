# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ..common import SpreadsheetTestCommon

from odoo.tests import tagged
from odoo.tests.common import HttpCase
from odoo.tools import file_open, misc

@tagged("post_install", "-at_install")
class TestSpreadsheetCreateTemplate(SpreadsheetTestCommon, HttpCase):

    @classmethod
    def setUpClass(cls):
        super(TestSpreadsheetCreateTemplate, cls).setUpClass()
        data_path = misc.file_path('documents_spreadsheet/demo/files/res_partner_spreadsheet.json')
        with file_open(data_path, 'rb') as f:
            cls.spreadsheet = cls.env["documents.document"].create({
                "handler": "spreadsheet",
                "folder_id": cls.folder.id,
                "raw": f.read(),
                "name": "Res Partner Test Spreadsheet"
            })

    def test_01_spreadsheet_create_template(self):
        self.start_tour("/web", "documents_spreadsheet_create_template_tour", login="admin")
