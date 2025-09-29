from odoo import fields, models, api

class Partner(models.Model):
    _inherit = 'res.partner'

    kelompok = fields.Text(string="Kelompok")
