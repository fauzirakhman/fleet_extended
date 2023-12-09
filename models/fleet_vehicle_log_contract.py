from odoo import fields, models, _


class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")

    def _compute_attached_docs_count(self):
        for contract in self:
            contract.doc_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'fleet.vehicle.log.contract'), ('res_id', '=', contract.id)])

    def attachment_tree_view(self):
        self.ensure_one()
        domain = [('res_model', '=', 'fleet.vehicle.log.contract'), ('res_id', 'in', self.ids)]
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