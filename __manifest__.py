{
    'name': 'Poultry and Livestock (Husbandry)',
    # 'version': '1.0',
    # 'category': 'Custom',

    'author': 'Farrell Raafi',
    'website': 'http://odooabc.com',

    'depends': [
        'base',
        'product',
        'om_account_accountant', # https://apps.odoo.com/apps/modules/18.0/om_account_accountant
    ],
    'data': [
        'security/security.xml',
        'views/husbandry.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
        'views/account_invoice.xml',
        'views/husbandry_inspection.xml',
        'views/husbandry_livestock.xml',
    ],

    'application': True,
    'installable': True,
}
