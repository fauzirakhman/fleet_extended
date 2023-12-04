from odoo import fields, models
from odoo.tools import ustr, format_date


class WizardWBreakdownCancelReason(models.TransientModel):
    _name = 'breakdown.cancel.reason'
    _description = 'Fleet Breakdown Cancel Reason'

    reason = fields.Char(string='Reason', required=True)

    def cancel_breakdown(self):
        if self._context.get('active_id', False) and \
                self._context.get('active_model', False):
            user = self.env.user
            line = '---------------------------------------------------------'
            line += '--------------------------'
            notes = 'Your fleet Breakdown is cancelled by' + " " + user.name + " " + 'on' + " " + ustr(format_date(self.env, fields.Date.today(), self.env.user.lang, date_format=False))
            breakdown_rec = self.env[self._context['active_model']].browse(self._context['active_id'])
            for wiz in self:
                if breakdown_rec.fleet_id:
                    breakdown_rec.fleet_id.write({
                        'state': 'inspection',
                        'last_change_status_date': fields.Date.today()
                    })
                breakdown_rec.write({
                    'cancel_note': notes + '\n' + line + '\n' + wiz.reason,
                    'state': 'cancel', 'date_cancel': fields.Date.today(),
                    'cancel_by_id': user and user.id or False
                })