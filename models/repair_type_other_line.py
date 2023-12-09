from odoo import fields, models


class RepairTypeOtherLine(models.Model):
    _name = 'repair.type.other.line'
    _description = 'Repair Type Other Line'

    breakdown_id = fields.Many2one('fleet.breakdown', string="Breakdown")
    description = fields.Text(string="Repair Description", help="Description of the repair type other")

RepairTypeOtherLine()