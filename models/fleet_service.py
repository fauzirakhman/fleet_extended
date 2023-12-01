from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, ustr
from odoo.tools.float_utils import float_compare
from datetime import datetime, timedelta
import time

class FleetVehicleLogServices(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    _order = 'id desc'
    _rec_name = 'name'

    name = fields.Char(string='Work Order', size=32, readonly=True, translate=True, copy=False, default="New")
    source_service_id = fields.Many2one('fleet.vehicle.log.services', string="Service", copy=False)
    date_open = fields.Date(string='Open Date', help="When Work Order will confirm this date will be set.")
    date_complete = fields.Date(string='Issued Complete ', help='Date when the service is completed')
    date_close = fields.Date(string='Date Close', help="Closing Date of Work Order")
    closed_by = fields.Many2one('res.users', string='Closed By')
    etic = fields.Boolean(string='Estimated Time', help="Estimated Time In Completion", default=True)
    state = fields.Selection(selection_add=[('draft', 'Draft'), ('confirm', 'Open'), ('done', 'Done'), ('cancel', 'Cancel')], string='Status', default='draft', readonly=True)
    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'HIGH'), ('low', 'LOW')], default='normal', string='Work Priority')
    team_id = fields.Many2one('res.partner', string="Teams")
    vehicle_type_id = fields.Many2one('vehicle.type', string='Vehicle Type')
    already_closed = fields.Boolean("Already Closed?")
    next_service_date = fields.Date(string='Next Service Date')
    next_service_odometer = fields.Float(string='Next Odometer Value', readonly=True)
    repair_line_ids = fields.One2many('service.repair.line', 'service_id', string='Repair Lines')

    @api.onchange('vehicle_id')
    def _onchange_get_vehicle_info(self):
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.update({"vehicle_type_id": vehicle.vehicle_type_id.id or False})

    @api.onchange('service_type_id')
    def get_repair_line(self):
        repair_lines = []
        if self.service_type_id:
            for repair_type in self.service_type_id.repair_type_ids:
                repair_lines.append((0, 0, {'repair_type_id': repair_type.id}))
            self.repair_line_ids = repair_lines

    @api.constrains('date', 'date_complete')
    def check_complete_date(self):
        for vehicle in self:
            if vehicle.date and vehicle.date_complete:
                if vehicle.date_complete < vehicle.date:
                    raise UserError('Estimated date should be greater than issue date.')

    def _compute_get_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([('vehicle_id', '=', record.vehicle_id.id)], limit=1, order='value desc')
            record.odometer = vehicle_odometer.value if vehicle_odometer else 0.0

    def _compute_set_odometer(self):
        fleet_vehicle_odometer_obj = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search([('vehicle_id', '=', record.vehicle_id.id)], limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise UserError('You cannnot enter odometer less than previous ' 'odometer %s !') % vehicle_odometer.value
            if record.odometer:
                data = {
                    'value': record.odometer,
                    'date': fields.Date.context_today(record),
                    'vehicle_id': record.vehicle_id.id
                }
                fleet_vehicle_odometer_obj.create(data)

    def action_confirm(self):
        sequence = self.env['ir.sequence'].next_by_code('service.order.sequence')
        context = self.env.context.copy()
        for work_order in self:
            if work_order.vehicle_id:
                if work_order.vehicle_id.state == 'in_progress':
                    raise UserError("Previous work order is not complete, complete that work order first then you can confirm this work order!")
                elif work_order.vehicle_id.state == 'draft' or work_order.vehicle_id.state == 'complete':
                    raise UserError("Confirm work order can only when vehicle status is in Inspection or Released!")
                work_order.vehicle_id.write({'state': 'in_progress', 
                                             'last_change_status_date': fields.Date.today(), 
                                             'work_order_close': False})
            work_order.write({'state': 'confirm', 
                              'name': sequence, 
                              'date_open': time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            pending_repair_resource_id = self.env.ref('fleet_extended.continue_pending_repair_form_view').id
            context.update({'work_order_id': work_order.id, 
                            'vehicle_id': work_order.vehicle_id and work_order.vehicle_id.id or False})
            if work_order.vehicle_id:
                for pending_repair in work_order.vehicle_id.pending_repair_type_ids:
                    if pending_repair.state == 'in-complete':
                        return {
                                'name': ('Previous Repair Types'),
                                'context': context,
                                'view_type': 'form',
                                'view_mode': 'form',
                                'res_model': 'continue.pending.repair',
                                'views': [(pending_repair_resource_id, 'form')],
                                'type': 'ir.actions.act_window',
                                'target': 'new',
                        }
        return True

    def action_done(self):
        context = dict(self.env.context)
        odometer_increment = 0.0
        for work_order in self:
            for repair_line in work_order.repair_line_ids:
                if repair_line.complete is True:
                    continue
                elif repair_line.complete is False:
                    pending_repair_resource_id = self.env.ref("fleet_extended.pending_repair_confirm_form_view")
                    context.update({'work_order_id': work_order.id})
                    return {
                        'name': ('WO Close Forcefully'),
                        'context': context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'pending.repair.confirm',
                        'views': [(pending_repair_resource_id.id, 'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }

        increment_ids = self.env['next.increment.number'].search([('vehicle_id', '=', work_order.vehicle_id.id)])
        if not increment_ids:
            return {
                'name': _('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        if increment_ids:
            odometer_increment = increment_ids[0].number

        next_service_day_ids = self.env['next.service.days'].search([('vehicle_id', '=', work_order.vehicle_id.id)])
        if not next_service_day_ids:
            return {
                'name': _('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }

        work_order_vals = {}
        for work_order in self:
            user = self.env.user
            if work_order.odometer == 0:
                raise UserError("Please set the current Odometer of vehicle in the work order!")
            odometer_increment += work_order.odometer
            next_service_date = datetime.strptime(str(fields.Date.today()), DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=next_service_day_ids[0].days)
            work_order_vals.update({'state': 'done',
                                    'next_service_odometer': odometer_increment,
                                    'already_closed': True,
                                    'closed_by': user,
                                    'date_close': fields.Date.today(),
                                    'next_service_date': next_service_date})
            work_order.write(work_order_vals)
            if work_order.vehicle_id:
                work_order.vehicle_id.write({'state': 'complete',
                                             'last_service_by_id': work_order.team_id and work_order.team_id.id or False,
                                             'last_service_date': fields.Date.today(),
                                             'next_service_date': next_service_date,
                                             'due_odometer': odometer_increment,
                                             'due_odometer_unit': work_order.odometer_unit,
                                             'last_change_status_date': fields.Date.today(),
                                             'work_order_close': True})
                if work_order.already_closed:
                    for repair_line in work_order.repair_line_ids:
                        for pending_repair_line in work_order.vehicle_id.pending_repair_type_ids:
                            if repair_line.repair_type_id.id == pending_repair_line.repair_type_id.id and work_order.name == pending_repair_line.name:
                                if repair_line.complete is True:
                                    pending_repair_line.unlink()

    def action_reopen(self):
        for order in self:
            service_type_id = False
            # try:
            #     service_type_id = self.env.ref('fleet.type_service_service_8')
            # except ValueError:
            #     pass
            # if not service_type_id:
            #     service_type_obj = self.env['fleet.service.type']
            #     service_type_id = service_type_obj.search([('name', '=', 'Repair and maintenance')])
            #     if not service_type_id:
            #         service_type_id = service_type_obj.create({"name": "Repair and maintenance", "category":"service"})
            order.write({'state': 'done'})
            new_reopen_service = order.copy()
            new_reopen_service.write({
                'source_service_id': order.id,
                'date_open': False,
                'date_close': False,
                'service_type_id': service_type_id.id,
                'amount': False,
                'team_id': False,
                'closed_by': False,
                'repair_line_ids': [(6, 0, [])],
            })
            return {
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': new_reopen_service.id,
            }

    @api.ondelete(at_uninstall=False)
    def _unlink_if_state_draft(self):
        if any(state not in 'draft' for state in self.mapped('state')):
            raise UserError('You cannot delete Work Order which in Confirmed or Done state!')

FleetVehicleLogServices()