from odoo import fields, models, api # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)

class Partner(models.Model):
    _inherit = 'res.partner'

    kelompok = fields.Text(string="Kelompok")
