from odoo import models, fields, api
from odoo.exceptions import ValidationError


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