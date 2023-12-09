from odoo import fields, models


class DamageTypeOtherLine(models.Model):
    _name = 'damage.type.other.line'
    _description = 'Damage Type Other Line'

    breakdown_id = fields.Many2one('fleet.breakdown', string="Breakdown")
    description = fields.Text(string="Damage Description", help="Description of the damage type other")

DamageTypeOtherLine()