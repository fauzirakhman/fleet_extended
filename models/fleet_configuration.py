from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class ColorColor(models.Model):
    _name = 'color.color'
    _description = 'Colors'

    code = fields.Char(string='Code', translate=True)
    name = fields.Char(string='Name', required=True, translate=True)

    @api.constrains('name')
    def check_color(self):
        for rec in self:
            if self.env['color.color'].search_count([('name', 'ilike', rec.name.strip()), ('id', '!=', rec.id)]):
                raise ValidationError("This color already exist")

ColorColor()


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

VehicleType()


class ServiceCategory(models.Model):
    _name = 'service.category'
    _description = 'Service Category'

    name = fields.Char(string="Service Category", translate=True)

    @api.constrains('name')
    def check_name(self):
        for category in self:
            if self.search_count([('id', '!=', category.id), ('name', 'in', category.name.strip())]):
                raise ValidationError('Service Category with this name already exists!')

ServiceCategory()


class NextIncrementNumber(models.Model):
    _name = 'next.increment.number'
    _description = 'Next Increment Number'

    name = fields.Char(string='Name', size=64, translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Id')
    number = fields.Float(string='Odometer Increment')

    @api.constrains('number')
    def check_odometer_number(self):
        for rec in self:
            if rec.number < 0.0:
                raise ValidationError('You cannot add negative value for odometer number of vehicle!')

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        next_number = self.env['next.increment.number']
        for increment in self:
            if next_number.search_count([('vehicle_id', '=', increment.vehicle_id.id), ('id', '!=', increment.id)]):
                raise ValidationError('You cannot add more than one odometer increment configuration for same vehicle!')

NextIncrementNumber()


class NextServiceDays(models.Model):
    _name = 'next.service.days'
    _description = 'Next Service days'

    name = fields.Char(string='Name', translate=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Id')
    days = fields.Integer(string='Days')

    @api.constrains('days')
    def check_service_days(self):
        for rec in self:
            if rec.days < 0:
                raise ValidationError('You cannot add negative value next service days!')

    @api.constrains('vehicle_id')
    def _check_vehicle_id(self):
        for service in self:
            if self.search_count([('vehicle_id', '=', service.vehicle_id.id), ('id', '!=', service.id)]):
                raise ValidationError('You can not add more than one next service days configuration for same vehicle!')

NextServiceDays()


class RepairType(models.Model):
    _name = 'repair.type'
    _description = 'Repair Type'

    name = fields.Char(string='Repair Type', translate=True)

    @api.constrains('name')
    def check_name(self):
        for repair in self:
            if self.search_count([('id', '!=', repair.id), ('name', 'ilike', repair.name.strip())]):
                raise ValidationError('Repair type with this name already exists!')

RepairType()


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    category = fields.Selection(selection_add=[('contract', 'Contract'), ('service', 'Service'), ('both', 'Both')], required=False, string='Category', help='Choose wheter the service refer to contracts, vehicle services or both')
    repair_type_ids = fields.Many2many('repair.type', 'fleet_service_repair_type_rel', 'service_type_id', 'repair_type_id', string='Repair Type')

    @api.constrains('name')
    def check_name(self):
        for service in self:
            if self.search_count([('id', '!=', service.id), ('name', 'ilike', service.name.strip())]):
                raise UserError('Service type with this name already exists!')

FleetServiceType()


class DamageType(models.Model):
    _name = 'damage.type'
    _description = 'Damage Type'

    name = fields.Char(string='Name', translate=True)
    code = fields.Char(string='Code')

    @api.constrains('name', 'code')
    def _check_duplicate_damage_type(self):
        for damage in self:
            if self.search_count([('name', 'ilike', damage.name.strip()), ('code', 'ilike', damage.code.strip()), ('id', '!=', damage.id)]):
                raise ValidationError("You cannot add duplicate damage types!")

DamageType()