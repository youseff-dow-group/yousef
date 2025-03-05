from odoo import models, fields, api



class Picking(models.Model):
    _inherit = 'stock.picking'
    _rec_name = "origin"


