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
        'views/catalog.xml',
        'views/confirm_livestock_sale_wizard.xml',
    ],

    'application': True,
    'installable': True,
}
