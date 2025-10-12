import string
from odoo import models, fields # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from odoo.exceptions import UserError # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)

class ConfirmationWizard(models.TransientModel):
    _name = 'confirmation.wizard'
    message = fields.Char(readonly=True)

    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        res['message'] = self.env.context.get('message')
        return res

    def submit(self):
        target_model = self.env.context.get('target_model')
        target_id = self.env.context.get('target_id')
        target_method = self.env.context.get('target_method')
        try: target_args = self.env.context.get('target_args')
        except: target_args = []
        target = self.env[self.env.context.get('target_model')].browse(target_id)
        if not target: raise UserError(f'Target record not found ({target_model = }, {target_id = }).')
        if not hasattr(target, target_method): raise UserError(f'Can\'t access target method ({target_method = }).')
        to_invoke = getattr(target, target_method)
        if callable(to_invoke): to_invoke(*target_args)