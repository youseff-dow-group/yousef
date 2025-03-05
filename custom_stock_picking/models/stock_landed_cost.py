from odoo import models, fields, api



class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    picking_ids = fields.Many2many(
        'stock.picking', string='Transfers',
        copy=False, domain=[('picking_type_id.code', '=', 'incoming')])


