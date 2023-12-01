from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError

class FleetBreakdown(models.Model):
    _name = 'fleet.breakdown'
    _description = 'Fleet Breakdown'
    _order = 'id desc'
    _rec_name = 'vehicle_id'

    name = fields.Char(string="Name")
    fleet_id = fields.Integer(string='Fleet ID', help="Take this field for data migration")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env['res.company']._default_currency_id(), string='Currency', help="The optional other currency if it is a multi-currency entry."    )
    vehicle_fmp_id = fields.Char(string='Vehicle ID', size=64)
    vin_no = fields.Char(string='Vin No', size=64, translate=True)
    # color_id = fields.Many2one('color.color', string='Color')
    vehicle_plate = fields.Char(string='Vechicle Plate No.', translate=True)
    report_date = fields.Date(string='Report Date')
    odometer = fields.Float(string='Odometer')
    cost_esitmation = fields.Float(string='Cost Estimation')
    note_for_cause_damage = fields.Text(string='Cause of Damage', translate=True)
    note = fields.Text(string='Note', translate=True)
    cancel_note = fields.Text(string='Cancel Note', translate=True)
    multi_images = fields.Many2many('ir.attachment', 'fleet_breakdown_attachment_rel', 'breakdown_id','attachment_id', string='Multi Images')
    damage_type_ids = fields.Many2many('damage.type', 'fleet_breakdown_damage_type_rel', 'breakdown_id', 'damage_id', string="Damage Type")
    repair_type_ids = fields.Many2many('repair.type', 'fleet_breakdown_repair_type_rel', 'breakdown_id', 'repair_id', string="Repair Type")
    # location_id = fields.Many2one('vehicle.location', string='Location')
    driver_id = fields.Many2one('res.partner', string='Driver')
    breakdown_type = fields.Selection([('general_accident', 'General Accident'), ('insurgent_attack', 'Insurgent Attack')], string='Breakdown Type', default='general_accident')
    contact_no = fields.Char(string='Driver Contact Number')
    odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], string='Odometer Unit', help='Unit of the odometer')
    # province_id = fields.Many2one('res.country.state', 'Registration State')
    # division_id = fields.Many2one('vehicle.divison', 'Division')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('cancel', 'Cancelled')], string='State', default='draft')
    date_cancel = fields.Date(string='Date Cancelled')
    cancel_by_id = fields.Many2one('res.users', string="Cancelled By")

    @api.constrains('cost_esitmation')
    def check_estimation_cost(self):
        for cost in self:
            if cost.cost_esitmation < 0:
                raise ValidationError("Expense to repair cost should not be negative!")

    @api.model
    def default_get(self, fields):
        vehicle_obj = self.env['fleet.vehicle']
        res = super(FleetBreakdown, self).default_get(fields)
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'breakdown':
                    raise UserError("This vehicle is already in breakdown state!")
                elif vehicle.state == 'in_progress' or vehicle.state == 'complete':
                    raise UserError("You cannot breakdown this vehicle which is in Progress or Complete state!")
                elif vehicle.state == 'rent':
                    raise UserError("You cannot breakdown this vehicle which is On Rent.")
                res.update({'contact_no': vehicle.driver_contact_no or ''})
        return res

    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        if self.vehicle_id:
            vehicle = self.vehicle_id
            # self.province_id = vehicle.vehicle_location_id and vehicle.vehicle_location_id.id or False
            self.driver_id = vehicle.driver_id and vehicle.driver_id.id or False
            self.contact_no = vehicle.driver_contact_no or ''
            self.vin_no = vehicle.vin_sn or ''
            self.vehicle_fmp_id = vehicle.name or ''
            # self.color_id = vehicle.vehical_color_id and vehicle.vehical_color_id.id or False
            self.vehicle_plate = vehicle.license_plate or ''
            self.odometer = vehicle.odometer or 0.0
            self.odometer_unit = vehicle.odometer_unit or False
            # self.division_id = vehicle.vehical_division_id and vehicle.vehical_division_id.id or False

    def cancel_breakdown(self):
        return {
            'name': 'Breakdown Cancel Form',
            'res_model': 'breakdown.cancel.reason',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new'
        }

    def confirm_breakdown(self):
        for brkd in self:
            if brkd.vehicle_id:
                brkd.vehicle_id.write({'state': 'breakdown', 'last_change_status_date': fields.Date.today()})
            brkd.write({'state': 'confirm', 'name': self.env['ir.sequence']. next_by_code('vehicle.breakdown.sequnce')})

    def action_set_to_draft(self):
        for brkd in self:
            brkd.write({'state': 'draft'})