from odoo import models, fields, api # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
class HusbandryType(models.Model):
    _name = 'husbandry.type'

    name = fields.Char(string="Type", required=True)
