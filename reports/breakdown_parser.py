from odoo import api, models


class ReportQwebBreakdown (models. AbstractModel):
    _name = 'report.fleet_extended.breakdown_qweb'
    _description = 'Fleet Breakdown Report'

    def _get_last_work_order(self, vehicle_id):
        work_order_obj = self.env['fleet.vehicle.log.services']
        work_order_rec = work_order_obj.search([('vehicle_id', '=', vehicle_id), ('state', '=', 'done')], order='id desc', limit=1)
        work_order_name = ''
        if work_order_rec:
            work_order_name = work_order_rec.name or ''
        return work_order_name

    @api.model
    def _get_report_values(self, docids, data=None):
        if data is None:
            data = {}
        if not docids:
            docids = data.get('docids', [])
        docs = self.env['fleet.breakdown'].browse(docids)
        return{'doc_ids': docids,
               'doc_model': 'fleet.breakdown',
               'docs': docs,
               'get_last_work_order': self._get_last_work_order}