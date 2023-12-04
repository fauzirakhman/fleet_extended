from odoo import fields, models


class TireHistory(models.Model):
    _name = 'tire.history'
    _description = 'Tire History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_tire_season = fields.Selection(string="Previous Tire Season", selection=[('summer_tires', 'Summer Tires'),('winter_tires', 'Winter Tires')])
    new_tire_season = fields.Selection(string="New Tire Season", selection=[('summer_tires', 'Summer Tires'),('winter_tires', 'Winter Tires')])
    previous_tire_size = fields.Char(string='Previous Tire Size', size=124, translate=True)
    new_tire_size = fields.Char(string="New Tire Size", size=124, translate=True)
    previous_tire_sn = fields.Char(string='Previous Tire Serial', size=124, translate=True)
    new_tire_sn = fields.Char(string="New Tire Serial", size=124)
    previous_tire_issue_date = fields.Date(string='Previous Tire Issuance Date')
    new_tire_issue_date = fields.Date(string='New Tire Issuance Date')
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')

TireHistory()


class BatteryHistory(models.Model):
    _name = 'battery.history'
    _description = 'Battery History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_battery_name = fields.Char(string='Previous Battery Name', size=124)
    new_battery_name = fields.Char(string="New Battery Name", size=124)
    previous_battery_size = fields.Char(string='Previous Battery Size', size=124)
    new_battery_size = fields.Char(string="New Battery Size", size=124)
    previous_battery_sn = fields.Char(string='Previous Battery Serial', size=124)
    new_battery_sn = fields.Char(string="New Battery Serial", size=124)
    previous_battery_issue_date = fields.Date(string='Previous Battery Issuance Date')
    new_battery_issue_date = fields.Date(string='New Battery Issuance Date')
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')

BatteryHistory()


class ColorHistory(models.Model):
    _name = 'color.history'
    _description = 'Color History for Vehicle'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    previous_color_id = fields.Many2one('color.color', string="Previous Color")
    current_color_id = fields.Many2one('color.color', string="New Color")
    changed_date = fields.Date(string='Change Date')
    note = fields.Text(string='Notes', translate=True)
    workorder_id = fields.Many2one('fleet.vehicle.log.services', string='Work Order')

ColorHistory()