from odoo import fields, models

class PendingRepairType(models.Model):
    _name = 'pending.repair.type'
    _description = 'Pending Repair Type'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    repair_type_id = fields.Many2one('repair.type', string="Repair Type")
    name = fields.Char(string='Work Order #', translate=True)
    categ_id = fields.Many2one("service.category", string="Category")
    issue_date = fields.Date(string="Issue Date")
    state = fields.Selection([('complete','Complete'),('in-complete','Pending')], string="Status")
    user_id = fields.Many2one('res.users', string="By")

PendingRepairType()