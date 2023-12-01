from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ServiceRepairLine(models.Model):
    _name = 'service.repair.line'
    _description = 'Service Repair Line'

    @api.constrains('date', 'target_date')
    def check_target_completion_date(self):
        for vehicle in self:
            if vehicle.issue_date and vehicle.target_date:
                if vehicle.target_date < vehicle.issue_date:
                    raise ValidationError('Target Completion Date Should Be Greater Than Issue Date.')

    @api.constrains('target_date', 'date_complete')
    def check_etic_date(self):
        for vehicle in self:
            if vehicle.target_date and vehicle.date_complete:
                if vehicle.target_date > vehicle.date_complete:
                    raise ValidationError('Repairs target completion date should be less than estimated date.')

    service_id = fields.Many2one('fleet.vehicle.log.services', ondelete='cascade')
    repair_type_id = fields.Many2one('repair.type', string='Repair Type')
    categ_id = fields.Many2one('service.category', string='Category')
    issue_date = fields.Date(string='Issued Date ')
    date_complete = fields.Date(related='service_id.date_complete', string="Complete Date")
    target_date = fields.Date(string='Target Completion')
    complete = fields.Boolean(string='Completed')

ServiceRepairLine()