from odoo import models, fields, api
class HusbandryType(models.Model):
    _name = 'husbandry.type'

    name = fields.Char(string="Type", required=True)
