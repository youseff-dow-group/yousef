from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    line_number = fields.Integer(string="Line", compute='_compute_line_number', store=True)
    product_barcode = fields.Char(
        string='Barcode',
        related='product_id.barcode',
        store=True,
        readonly=True,
    )
    product_cost = fields.Float(
        string='Cost',
        related='product_id.standard_price',
        store=True,
        readonly=True,
    )

    @api.depends('move_id.line_ids')
    def _compute_line_number(self):
        for record in self:
            if record.move_id:
                for index, line in enumerate(record.move_id.line_ids.filtered(lambda l: l.display_type == 'product'), start=1):
                    line.line_number = index
