from odoo import fields, models, api
from odoo.exceptions import UserError


class VehicleType(models.Model):
    _name = 'vehicle.type'
    _description = 'Vehicle Type'

    code = fields.Char(string='Code')
    name = fields.Char(string='Name', required=True)

    @api.constrains('name')
    def _check_unique_vehicle_type(self):
        for vehicle_type in self:
            if self.search_count([('id', '!=', vehicle_type.id), ('name', 'ilike', vehicle_type.name.strip())]):
                raise UserError('Vehicle type with this name already exists!')