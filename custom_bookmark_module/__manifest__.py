
{
    'name': 'Product Auto Fill',
    'version': '1.0',
    'category': 'Product',
    'summary': 'Auto-fill product fields before saving',
    'author': 'Ghaith',
    'depends': ['product'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/fetch_product_view.xml',
    ],
    'installable': True,
    'application': False,
}

