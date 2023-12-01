from odoo import fields, models, api, _


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    shared_mobility_card = fields.Char(string="Shared Mobility Card")

    def _compute_attached_docs_count(self):
        for contract in self:
            contract.doc_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'fleet.vehicle'), ('res_id', '=', contract.id)])

    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'fleet.vehicle'), ('res_id', 'in', self.ids)]
        result = {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'target': 'current',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d, 'create': True}" % (self._name, self.id)
        }
        return result

    @api.depends('driver_id')
    def _compute_mobility_card(self):
        for vehicle in self:
            employee = self.env['hr.employee']
            if vehicle.driver_id:
                employee = employee.search([('address_home_id', '=', vehicle.driver_id.id)], limit=1)
                if not employee:
                    employee = employee.search([('user_id.partner_id', '=', vehicle.driver_id.id)], limit=1)
                vehicle.mobility_card = employee.mobility_card
                vehicle.shared_mobility_card = False
            else:
                vehicle.mobility_card = False

###  ------------------------------------------------------------------------------------------------------------------------------- ###
###  ------------------------------------------------------ EXTENDED --------------------------------------------------------------- ###

    state = fields.Selection([('inspection', 'Draft'),
                              ('in_progress', 'In Service'),
                              ('contract', 'On Contract'),
                              ('rent', 'On Rent'), 
                              ('complete', 'Completed'),
                              ('released', 'Released'),
                              ('breakdown', 'Breakdown')],
                             string='Vehicle State', default='inspection')
    work_order_close = fields.Boolean(string='Work Order Close', default=True)
    vehicle_type_id = fields.Many2one('vehicle.type', string='Vehicle Type')
    driver_identification_no = fields.Char(string='Driver ID', size=64)
    driver_contact_no = fields.Char(string='Driver Contact No.', size=64)

    ### Engine ###
    engine_no = fields.Char(string='Engine No', size=64)

    ### Tires ###
    tire_season = fields.Selection(selection=[('summer_tires', 'Summer Tires'),('winter_tires', 'Winter Tires')])
    tire_size = fields.Char(string='Tire Size', size=64)
    tire_srno = fields.Char(string='Tire S/N', size=64)
    tire_issuance_date = fields.Date(string='Tire Issuance Date')
    is_tire_season_set = fields.Boolean(string='Is Tire Season set?')
    is_tire_size_set = fields.Boolean(string='Is Tire Size set?')
    is_tire_srno_set = fields.Boolean(string='Is Tire Serial no. set?')
    is_tire_issue_set = fields.Boolean(string='Is Tire Issue set?')
    tire_history_ids = fields.One2many('tire.history', 'vehicle_id', string="Tire History", readonly=True)

    ### Battery ###
    battery_name = fields.Char(string='Battery Name', size=64)
    battery_size = fields.Char(string='Battery Size', size=64)
    battery_srno = fields.Char(string='Battery S/N', size=64)
    battery_issuance_date = fields.Date(string='Battery Issuance Date')
    is_battery_name_set = fields.Boolean(string='Is battery Name set?')
    is_battery_size_set = fields.Boolean(string='Is battery Size set?')
    is_battery_srno_set = fields.Boolean(string='Is battery Srno set?')
    is_battery_issue_set = fields.Boolean(string='Is battery Issue set?')
    battery_history_ids = fields.One2many('battery.history', 'vehicle_id', string="Battrey History", readonly=True)

    ### Services ###
    last_service_date = fields.Date(string='Last Service', readonly=True)
    last_change_status_date = fields.Date(string='Last Status Changed Date', readonly=True)
    last_service_by_id = fields.Many2one('res.partner', string="Last Service By")
    next_service_date = fields.Date(string='Next Service', readonly=True)
    due_odometer = fields.Float(string='Next Service Odometer', readonly=True)
    due_odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], string='Due Odometer Units', help='Unit of the odometer')
    work_order_ids = fields.One2many('fleet.vehicle.log.services', 'vehicle_id', string='Service Order')
    pending_repair_type_ids = fields.One2many('pending.repair.type', 'vehicle_id', string='Pending Repair Types', readonly=True)

    @api.model
    def create(self, vals):
        if not vals.get('last_change_status_date', False):
            vals.update({'last_change_status_date': fields.Date.today()})

        if vals.get('tire_name', False):
            vals.update({'is_tire_name_set': True})
        if vals.get('tire_size', False):
            vals.update({'is_tire_size_set': True})
        if vals.get('tire_srno', False):
            vals.update({'is_tire_srno_set': True})
        if vals.get('tire_issuance_date', False):
            vals.update({'is_tire_issue_set': True})

        if vals.get('battery_name', False):
            vals.update({'is_battery_name_set': True})
        if vals.get('battery_size', False):
            vals.update({'is_battery_size_set': True})
        if vals.get('battery_srno', False):
            vals.update({'is_battery_srno_set': True})
        if vals.get('battery_issuance_date', False):
            vals.update({'is_battery_issue_set': True})

        return super(FleetVehicle, self).create(vals)

    def update_history(self):
        mod_obj = self.env['ir.model.data']
        wizard_view = ""
        res_model = ""
        view_name = ""
        context = self.env.context
        context = dict(context)
        if context.get('history', False):
            if context.get('history', False) == 'tire':
                wizard_view = "update_tire_info_form_view"
                res_model = "update.tire.info"
                view_name = "Update Tire Info"
            elif context.get('history', False) == 'battery':
                wizard_view = "update_battery_info_form_view"
                res_model = "update.battery.info"
                view_name = "Update Battery Info"

        model_data_ids = mod_obj.search([('model', '=', 'ir.ui.view'), ('name', '=', wizard_view)])
        resource_id = model_data_ids.read(['res_id'])[0]['res_id']
        context.update({'vehicle_ids': self._ids})
        return {
            'name': view_name,
            'context': self._context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': res_model,
            'views': [(resource_id, 'form')],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

    @api.onchange('driver_id')
    def get_driver_id_no(self):
        if self.driver_id:
            driver = self.driver_id
            self.driver_identification_no = driver.d_id or ''
            self.driver_contact_no = driver.mobile
        else:
            self.driver_identification_no = ''
            self.driver_contact_no = ''