
{
    'name': 'Product Auto Fill',
    'version': '1.0',
    'category': 'Product',
    'summary': 'Auto-fill product fields before saving',
    'author': 'Ghaith',
    'depends': ['product','account'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_view.xml',
        'views/account_move.xml',
        'wizard/fetch_product_view.xml',
    ],
    'installable': True,
    'application': False,
}

