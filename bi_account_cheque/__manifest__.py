# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Cheque Life Cycle Management/ Post Dated Check Odoo',
    'version': '17.0.0.0',
    'category': 'Accounting',
    'summary': 'Post Dated Cheque management PDC cheque management account check post dated check PDC check customer check vendor check writing account check writing account cheque writing incoming check outgoing check print cheque print check bank cheque printing check',
    'description' :"""Account Cheque management
    Account Cheque Life Cycle Management Odoo
    write cheque management Odoo,
    cheque management system Odoo
    write cheque system on Odoo
    incoming cheque management Odoo
    outgoing cheque management Odoo
    life cycle of cheque system Odoo
    life cycle of cheque management system Odoo
    complete cycle of cheque Odoo
    cheque incoming cycle odoo
    cheque outgoing cycle odoo
    deposit cheque Odoo, cashed cheque, reconcile cheque, cheque write management, cheque submit, cheque submission
    register cheque, cheque register management
    Bounce cheque, cheque Bounce management
    reconcile cheque with payment,
    reconcile cheque with advance payment
    Account reconcilation with cheque management
    return cheque management
    cheque return management
    journal entry from the cheque management system
    write cheque with reconcile system
    Accounting write cheque management system
    Transfer cheque managament odoo

    Account check management
    Account check Life Cycle Management Odoo
    write check management Odoo,
    check management system Odoo
    write check system on Odoo
    incoming check management Odoo
    outgoing check management Odoo
    life cycle of check system Odoo
    life cycle of check management system Odoo
    complete cycle of check Odoo
    check incoming cycle odoo
    check outgoing cycle odoo
    deposit check Odoo, cashed check, reconcile check, check write management, check submit, check submission
    register check, check register management
    Bounce check, check Bounce management
    Account reconcilation with check management
    return check management
    check return management
    journal entry from the check management system
    write check with reconcile system
    Accounting write check manahement system
    Transfer cheque management odoo
    PDC cheque management
    PDC check management 
    post dated cheque management
    post dated check managament

    """,
    'author': 'BrowseInfo',
    'website': 'https://www.browseinfo.com',
    'depends': ['base','sale_management','account_accountant','account','mail'],
    'data': [
            'data/account_data_view.xml',
            'data/standard_dynamic_cheque_views.xml',
            'security/ir.model.access.csv',
            'security/account_cheque_security.xml',
            'report/account_cheque_report_view.xml',
            'report/account_cheque_report_template_view.xml',
            'report/dynamic_cheque_report_view.xml',
            'wizard/dynamic_cheque_report_wiz_view.xml',
            'wizard/register_cheque_payment_view.xml',
            'views/account_cheque_view.xml',
            'views/res_config_settings.xml',
            'views/dynamic_cheque_view.xml',
            'views/account_invoice_view.xml',
            
             ],
    'demo': [],
    'test': [],
    'license':'OPL-1',
    'installable': True,
    'auto_install': False,
    "price": 89,
    "currency": "EUR",
    'live_test_url':'https://youtu.be/RebVdk5DzIw',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
