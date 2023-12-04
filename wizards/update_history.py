from odoo import api, fields, models
from odoo.exceptions import ValidationError

class UpdateTireInfo(models.TransientModel):
    _name = 'update.tire.info'
    _description = 'Update Tire Info'

    previous_tire_season = fields.Selection(string="Previous Tire Season", selection=[('summer_tires', 'Summer Tires'),('winter_tires', 'Winter Tires')])
    new_tire_season = fields.Selection(string="New Tire Season", selection=[('summer_tires', 'Summer Tires'),('winter_tires', 'Winter Tires')])
    previous_tire_size = fields.Char(string='Previous Tire Size')
    new_tire_size = fields.Char(string="New Tire Size")
    previous_tire_sn = fields.Char(string='Previous Tire S/N')
    new_tire_sn = fields.Char(string="New Tire S/N")
    previous_tire_issue_date = fields.Date(string='Previous Tire Issuance Date')
    new_tire_issue_date = fields.Date(string='New Tire Issuance Date')
    changed_date = fields.Date(string='Change Date',default=fields.Date.today())
    note = fields.Text('Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Temp Bool for making ' 'previous Tire info readonly')
    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('previous_tire_issue_date', 'new_tire_issue_date')
    def check_new_tire_issue_date(self):
        for vehicle in self:
            if vehicle.previous_tire_issue_date and vehicle.new_tire_issue_date and vehicle.new_tire_issue_date < vehicle.previous_tire_issue_date:
                raise ValidationError('New tire issuance date should be greater than previous tire issuance date.')

    @api.constrains('changed_date', 'new_tire_issue_date')
    def check_tire_changed_date(self):
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_tire_issue_date and vehicle.changed_date < vehicle.new_tire_issue_date:
                raise ValidationError('Tire change date should be greater than new tire issuance date.')

    @api.model
    def default_get(self, fields):
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateTireInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_tire_season': vehicle.tire_season or False,
                'previous_tire_size': vehicle.tire_size or "",
                'previous_tire_sn': vehicle.tire_srno or "",
                "previous_tire_issue_date": vehicle.tire_issuance_date,
                'vehicle_id': vehicle.id
            })
        return res

    def set_new_tire_info(self):
        vehicle_obj = self.env['fleet.vehicle']
        tire_history_obj = self.env['tire.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'tire_season': wiz_data.new_tire_season or False,
                    'tire_size': wiz_data.new_tire_size or "",
                    'tire_srno': wiz_data.new_tire_sn or "",
                    'tire_issuance_date': wiz_data.new_tire_issue_date
                })
                tire_history_obj.create({
                    'previous_tire_season': wiz_data.previous_tire_season or False,
                    'new_tire_season': wiz_data.new_tire_season or False,
                    'previous_tire_size': wiz_data.previous_tire_size or "",
                    'new_tire_size': wiz_data.new_tire_size or "",
                    'previous_tire_sn': wiz_data.previous_tire_sn or "",
                    'new_tire_sn': wiz_data.new_tire_sn or "",
                    'previous_tire_issue_date': wiz_data.previous_tire_issue_date or False,
                    'new_tire_issue_date': wiz_data.new_tire_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True

UpdateTireInfo()


class UpdateBatteryInfo(models.TransientModel):
    _name = 'update.battery.info'
    _description = 'Update Battery Info'

    previous_battery_name = fields.Char(string='Previous Battery Name')
    new_battery_name = fields.Char(string="New Battery Name")
    previous_battery_size = fields.Char(string='Previous Battery Size')
    new_battery_size = fields.Char(string="New Battery Size")
    previous_battery_sn = fields.Char(string='Previous Battery S/N')
    new_battery_sn = fields.Char(string="New Battery S/N")
    previous_battery_issue_date = fields.Date(string='Previous Battery Issuance Date')
    new_battery_issue_date = fields.Date(string='New Battery Issuance Date')
    changed_date = fields.Date(string='Change Date', default=fields.Date.today())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Temp Bool for making previous Battery info readonly')
    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('previous_battery_issue_date', 'new_battery_issue_date')
    def check_new_battery_issue_date(self):
        for vehicle in self:
            if vehicle.previous_battery_issue_date and vehicle.new_battery_issue_date and \
                    vehicle.new_battery_issue_date < vehicle.previous_battery_issue_date:
                raise ValidationError('New battery issuance date should be greater than previous battery issuance date.')

    @api.constrains('changed_date', 'new_battery_issue_date')
    def check_battery_changed_date(self):
        for vehicle in self:
            if vehicle.changed_date and vehicle.new_battery_issue_date \
                    and vehicle.changed_date < vehicle.new_battery_issue_date:
                raise ValidationError('Battery change date should be greater than new battery issuance date.')

    @api.model
    def default_get(self, fields):
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateBatteryInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_battery_name': vehicle.battery_name or "",
                'previous_battery_size': vehicle.battery_size or "",
                'previous_battery_sn': vehicle.battery_srno or "",
                "previous_battery_issue_date": vehicle.battery_issuance_date,
                'vehicle_id': vehicle.id
            })
        return res

    def set_new_battery_info(self):
        vehicle_obj = self.env['fleet.vehicle']
        battery_history_obj = self.env['battery.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'battery_name': wiz_data.new_battery_name or "",
                    'battery_size': wiz_data.new_battery_size or "",
                    'battery_srno': wiz_data.new_battery_sn or "",
                    'battery_issuance_date': wiz_data.new_battery_issue_date
                })
                battery_history_obj.create({
                    'previous_battery_name': wiz_data.previous_battery_name or "",
                    'new_battery_name': wiz_data.new_battery_name or "",
                    'previous_battery_size': wiz_data.previous_battery_size or "",
                    'new_battery_size': wiz_data.new_battery_size or "",
                    'previous_battery_sn': wiz_data.previous_battery_sn or "",
                    'new_battery_sn': wiz_data.new_battery_sn or "",
                    'previous_battery_issue_date': wiz_data.previous_battery_issue_date or False,
                    'new_battery_issue_date': wiz_data.new_battery_issue_date or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True

UpdateBatteryInfo()


class UpdateColorInfo(models.TransientModel):
    _name = 'update.color.info'
    _description = 'Update Color Info'

    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')
    previous_color_id = fields.Many2one('color.color', string="Previous Color")
    current_color_id = fields.Many2one('color.color', string="New Color")
    changed_date = fields.Date(string='Change Date', default=fields.Date.today())
    note = fields.Text(string='Notes', translate=True)
    temp_bool = fields.Boolean(default=True, string='Temp Bool for making previous color readonly')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")

    @api.constrains('changed_date')
    def check_color_changed_date(self):
        for vehicle in self:
            if vehicle.changed_date and vehicle.vehicle_id.acquisition_date:
                if vehicle.changed_date < vehicle.vehicle_id.acquisition_date:
                    raise ValidationError('Color change date should be greater than vehicle registration date.')

    @api.model
    def default_get(self, fields):
        vehicle_obj = self.env['fleet.vehicle']
        res = super(UpdateColorInfo, self).default_get(fields)
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            res.update({
                'previous_color_id': vehicle.vehicle_color_id.id or False,
                'vehicle_id': vehicle.id or False
            })
        return res

    def set_new_color_info(self):
        vehicle_obj = self.env['fleet.vehicle']
        color_history_obj = self.env['color.history']
        if self._context.get('active_id', False):
            vehicle = vehicle_obj.browse(self._context['active_id'])
            for wiz_data in self:
                vehicle.write({
                    'vehicle_color_id': wiz_data.current_color_id.id or False
                })
                color_history_obj.create({
                    'previous_color_id': wiz_data.previous_color_id.id or False,
                    'current_color_id': wiz_data.current_color_id.id or False,
                    'note': wiz_data.note or '',
                    'changed_date': wiz_data.changed_date,
                    'workorder_id': wiz_data.workorder_id.id or False,
                    'vehicle_id': vehicle.id
                })
        return True

UpdateColorInfo