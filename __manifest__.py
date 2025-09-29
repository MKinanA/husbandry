{
    'name': 'Poultry and Livestock (Husbandry)',
    'version': '1.0',
    'category': 'Custom',

    'author': 'Farrell Raafi',
    'website': 'http://odooabc.com',

    'depends': ['base','product', 'om_account_accountant'],
    'data': [
        'security/security.xml',
        'views/husbandry.xml',
        'views/menu.xml',
        'security/ir.model.access.csv',
    ],
}
