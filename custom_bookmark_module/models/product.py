from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    authors_2 = fields.Char(string="Authors 2")
    main_distributor = fields.Char(string="Main Distributor")
    dept = fields.Char(string="Department")
    date_of_publish = fields.Char(string="Date of Publish")
    lang_of_origin = fields.Char(string="Language of Origin")
    pos_label = fields.Char(string="Point of Sale Label")
    price_category = fields.Float(string="Price Category")
