import calendar
import json
from datetime import date, datetime, timedelta, tzinfo
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, tools, exceptions, _ # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from odoo.exceptions import UserError, ValidationError # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from odoo.tools import float_compare, float_is_zero # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
import pytz


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    outstanding_credits_debits_widget = fields.Text(compute='_get_outstanding_info_JSON', groups="account.group_account_move,husbandry.group_husbandry_customer")
    payments_widget = fields.Text(compute='_get_payment_info_JSON', groups="account.group_account_move,husbandry.group_husbandry_customer")
    has_outstanding = fields.Boolean(compute='_get_outstanding_info_JSON', groups="account.group_account_move,husbandry.group_husbandry_customer")


    @api.model
    def get_view(self, view_id=None, view_type='form', toolbar=False, submenu=False, **unused_kwargs):
        print('\nget_view method on AccountInvoice called')
        res = super(AccountInvoice, self).get_view(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        View = self.env['ir.ui.view'].sudo()
        from lxml import etree
        if res.get('view_id'):
           view_id = res['view_id']
        if view_id:
           root_view = {'arch': View.browse(view_id).get_combined_arch()}
           res['arch'] = root_view['arch']
        doc = etree.XML(res['arch'])
        if self.env.ref('husbandry.group_husbandry_customer') in self.env.user.groups_id:
            if view_type == 'form':
                for node in doc.xpath("//form"):
                    node.set('create', 'false')
                    node.set('edit', 'false')
                    node.set('delete', 'false')
                    node.set('copy', 'false')
                doc = View.apply_inheritance_specs(doc, etree.XML("""
                <data>
                    <xpath expr="//header" position="replace">
                        <header>
                            <button name="preview_invoice" type="object" string="Preview"/>
                            <field name="state" widget="statusbar" nolabel="1" statusbar_visible="draft,open,paid"/>
                        </header>
                    </xpath>
                </data>
                """), view_id)
            if view_type == 'list':
                for node in doc.xpath("//list"):
                    node.set('create', 'false')
                    node.set('copy', 'false')
                    node.set('delete', 'false')
        res['arch'], res['fields'] = View.postprocess_and_fields(doc, self._name)
        return res