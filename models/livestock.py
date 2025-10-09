from odoo import models, fields, api, http, tools # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from odoo.exceptions import AccessError, UserError, ValidationError # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)

from datetime import date, datetime, timedelta, tzinfo
import pytz

states = [
    ('draft', 'Draft'),
    ('saleable', 'Saleable'),
    ('onbook', 'On Book'),
    ('soldout', 'Sold Out'),
    ('cancel','Cancel'),
]
exclude_for_readonly = 'draft'
readonly_on_not_draft_states = {state[0]: [('readonly', True)] for state in states if state[0] != exclude_for_readonly}
attrs_based_on_state = lambda state, states = readonly_on_not_draft_states: ' '.join((f'{attr[0]}="{int(attr[1]) if isinstance(attr[1], int) else attr[1]}"' for attr in states[state]) if state in states else '')
xml_readonly_on_not_draft_states = ' or '.join(f'state == \'{state[0]}\'' for state in states if state[0] != exclude_for_readonly) # {'readonly': [*['|'] * (len([state for state in states if state[0] != exclude_for_readonly]) - 1), *[('state', '==', state[0]) for state in states if state[0] != exclude_for_readonly]]}

class HusbandryLivestock(models.Model):
    _name = 'husbandry.livestock'
    _inherits = {'product.template': 'product_tmpl_id'}

    owner_ids = fields.Many2many('res.partner', string="Owner", states=readonly_on_not_draft_states)
    weight = fields.Float(string="Weight (kg)", states=readonly_on_not_draft_states)
    age = fields.Float(string="Age", states=readonly_on_not_draft_states)
    origin = fields.Char(string="Origin", states=readonly_on_not_draft_states)
    vendor_id = fields.Many2one('res.partner', string="Vendor", default=lambda self: self.env.user.partner_id.id, states=readonly_on_not_draft_states)
    purchase_price = fields.Float(related='product_tmpl_id.list_price', string="Purchase Price (Rp)", readonly=False, states=readonly_on_not_draft_states)
    type_id = fields.Many2one('husbandry.type', string="Type", states=readonly_on_not_draft_states)
    product_tmpl_id = fields.Many2one('product.template', string="Saleable Product", readonly=True, required=True)
    image_front = fields.Binary(string="Front Image", states=readonly_on_not_draft_states)
    image_right = fields.Binary(string="Right Image", states=readonly_on_not_draft_states)
    image_left = fields.Binary(string="Left Image", states=readonly_on_not_draft_states)
    image_back = fields.Binary(string="Back Image", states=readonly_on_not_draft_states)
    reference = fields.Char(string="Reference", states=readonly_on_not_draft_states)
    jatah = fields.Char(string="Jatah", states=readonly_on_not_draft_states)
    kelompok = fields.Text(string="Kelompok", states=readonly_on_not_draft_states)

    invoice_id = fields.Many2one('account.move', string="Invoice", readonly=True, )

    state = fields.Selection(states, string="State", readonly=True, default="draft")

    _sql_constraints = [
        ('unique_product_tmpl_id', 'unique(product_tmpl_id)', 'Each product can only be linked to one livestock.'),
    ]

    def get_inspections(self): return [inspection for inspection in http.request.env['husbandry.inspection'].search([], order='date') if inspection.livestock_id.id == self.id]
    def get_last_inspection(self): return last_inspection[0] if len(last_inspection := self.get_inspections()) >= 1 else None

    def get_last_image(self):
        images = []
        for inspection in self.get_inspections() + [self]: images += [eval(f'inspection.{image_property}') for image_property in inspection._fields if all(not image_property.startswith(x) for x in ['<', '_']) and 'binary' in inspection._fields[image_property].type.lower() and 'image' in image_property]
        for image in images:
            if image: return image

    @property
    def last_weight(self):
        for inspection in self.get_inspections():
            if (weight := inspection.weight): return weight
        return self.weight

    @property
    def last_age(self):
        for inspection in self.get_inspections():
            if (age := inspection.age): return age
        return self.age

    @api.model
    def create(self, vals):
        record = super().create(vals)
        record.product_tmpl_id.update({
            'sale_ok': False,
            'purchase_ok': False,
            'livestock_id': record.id,
        })
        return record

    @api.model
    def get_view(self, view_id=None, view_type='form', toolbar=False, submenu=False, **unused_kwargs):
        print(f'\nget_view method on HusbandryLivestock called,\n{self.state = }\n{attrs_based_on_state(self.state) = }\n')
        res = super().get_view(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            res['arch'] = """
                <form string="Livestock">
            """
            if self.env.ref('husbandry.group_husbandry_customer') in self.env.user.groups_id:
                res['arch'] = """
                    <form string="Livestock" create='false' edit='false' delete='false' copy='false'>
                """ 
            res['arch'] = res['arch'] + """

                    <header>
                        <button name="create_invoice" string="Buy (coming soon)" type="object" invisible="state != 'saleable'" class="disabled"/>
                        """f"""<field name="state" widget="statusbar" statusbar_visible="{','.join(map(lambda state: state[0], states))}" />""""""
                    </header>
              """f"""<sheet>
                        <group>
                            <group>
                                <field name="name" string="Name (Livestock ID)"/>
                                <field name="reference" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="weight" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="age" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="origin" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="product_tmpl_id" invisible="1"/>
                                <button name="create_product" string="Make Saleable" type="object" invisible="state != 'draft'"/>
                            </group>
                            <group>
                                <field name="create_date" string="Registration Date" readonly="1"/>
                                <field name="owner_ids" widget="many2many_tags" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="vendor_id" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="kelompok" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="type_id" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="jatah" readonly="{xml_readonly_on_not_draft_states}"/>
                                <field name="purchase_price" groups="base.group_erp_manager" readonly="{xml_readonly_on_not_draft_states}"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Images">
                                <group col="4">
                                    <field name="image_front" widget="image" string="Image 1" options="{{'size': [320, 180]}}" readonly="{xml_readonly_on_not_draft_states}"/>
                                    <field name="image_right" widget="image" string="Image 2" options="{{'size': [320, 180]}}" readonly="{xml_readonly_on_not_draft_states}"/>
                                    <field name="image_left" widget="image" string="Image 3" options="{{'size': [320, 180]}}" readonly="{xml_readonly_on_not_draft_states}"/>
                                    <field name="image_back" widget="image" string="Image 4" options="{{'size': [320, 180]}}" readonly="{xml_readonly_on_not_draft_states}"/>
                                </group>
                            </page>
                        </notebook>
                    </sheet>""""""
                </form>
        """
        elif view_type == 'list':
            res['arch'] = """
                <list string="Livestock">
            """
            if self.env.ref('husbandry.group_husbandry_customer') in self.env.user.groups_id:
                res['arch'] = """
                    <list string="Livestock" create='false' edit='false' delete='false' copy='false'>
                """ 
            res['arch'] = res['arch'] + """
                
                    <field name="name" string="Name (Livestock ID)"/>
                    <!--<field name="create_date" string="Registration Date" readonly="1"/>-->
                    <field name="weight" string="Berat"/>
                    <field name="vendor_id"/>
                    <field name="owner_ids" widget="many2many_tags"/>
                    <field name="purchase_price" />
                    <field name="state" />
                </list>
        """
        elif view_type == 'kanban':
            res['arch'] = """
                <kanban class="o_kanban_mobile">
            """
            if self.env.ref('husbandry.group_husbandry_customer') in self.env.user.groups_id:
                res['arch'] = """
                    <kanban class="o_kanban_mobile" create='false' edit='false' delete='false' copy='false'>
                """ 
            res['arch'] = res['arch'] + """
                
                    <field name="name" string="Name (Livestock ID)"/>
                    <field name="weight" string="Berat"/>
                    <field name="vendor_id"/>
                    <field name="owner_ids"/>
                    <field name="purchase_price" />
                    <field name="state" />
                    <templates>
                        <t t-name="kanban-box">
                            <div t-attf-class="oe_kanban_card oe_kanban_global_click">
                                <div class="o_kanban_record_top mb16">
                                    <div class="o_kanban_record_headings mt4">
                                        <strong class="o_kanban_record_title"><span><t t-esc="record.name.value"/></span></strong>
                                    </div>
                                    <field name="state" widget="label_selection" options="{'classes': {'draft': 'default', 'cancel': 'muted', 'done': 'success'}}"/>
                                </div>
                                <div class="o_kanban_record_bottom">
                                    <div class="oe_kanban_bottom_left text-default">
                                        <span><field name="vendor_id" /></span>
                                    </div>
                                    <div class="oe_kanban_bottom_right">
                                        <span><t t-esc="record.weight.value"/> KG - RP <t t-esc="record.purchase_price.value"/></span>
                                    </div>
                                </div>
                            </div>
                        </t>
                    </templates>
                </kanban>
        """
        elif view_type == 'search':
             res['arch'] = """
                <search string="Livestock">
                    <field name="name" string="Name (Livestock ID)"/>
                    <field name="create_date" string="Registration Date" readonly="1"/>
                    <field name="reference"/>
                    <field name="weight" string="Berat"/>
                    <field name="kelompok"/>
                </search>
        """
        from lxml import etree
        doc = etree.XML(res['arch'])
        View = self.env['ir.ui.view'].sudo()
        res['arch'], res['fields'] = View.postprocess_and_fields(doc, self._name)
        return res

    # @api.multi
    def create_product(self):
        # if not self.product_tmpl_id:
        #    name = self.name
        #    if self.type_id:
        #       name = name + " - " + self.type_id.name
        #    category_id = self.env.ref('product.product_category_all')
        #    # uom_id = self.env.ref('product.product_uom_unit')
        #    self.sudo().product_tmpl_id = self.sudo().product_tmpl_id.create({'name': name, 'list_price': self.purchase_price, 'categ_id': category_id.id, })# 'uom_po_id': uom_id.id, 'uom_id': uom_id.id,})
        self.state = 'saleable'

    # @api.multi
    def create_invoice(self):
        account_id = False
        product = self.product_tmpl_id
        if product.id:
            account_id = product.property_account_income_id.id
        if not account_id:
            account_id = product.categ_id.property_account_income_categ_id.id
        if not account_id:
            raise UserError(
                ('There is no income account defined for this product: "%s". \
                   You may have to install a chart of account from Accounting \
                   app, settings menu.') % (product.name,))

        if self.purchase_price <= 0.00:
            raise UserError(('The value of the deposit amount must be \
                             positive.'))
        else:
            amount = self.purchase_price
            name = product.name

        # user_tz = pytz.timezone("Asia/Jakarta")
        # date_due = datetime.strftime(pytz.utc.localize(datetime.datetime.utcnow() + timedelta(days=2)).astimezone(user_tz),"%Y-%m-%d %H:%M:%S")
        date_due = (datetime.now()+timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")

        invoice = self.env['account.move'].create({
            'name': self.name,
            # 'origin': self.reference,
            'invoice_origin': self.reference,
            # 'type': 'out_invoice',
            'move_type': 'out_invoice',
            'reference': False,
            'account_id': self.vendor_id.property_account_receivable_id.id,
            'partner_id': self.env.user.partner_id.id,
            # 'date_due': date_due,
            'invoice_date_due': date_due,
            # 'invoice_line_ids': [(0, 0, {
            'line_ids': [(0, 0, {
                'name': name,
                'origin': self.reference,
                'account_id': account_id,
                'price_unit': amount,
                'quantity': 1.0,
                'discount': 0.0,
                # 'uom_id': product.uom_id.id,
                'product_tmpl_id': product.id,
            })],
        })
        invoice.compute_taxes()
        self.invoice_id = invoice
        self.invoice_id.action_invoice_open()
        self.state = 'onbook'

        form_view = self.env.ref('account.move_form')
        tree_view = self.env.ref('account.move_list')
        value = {
            'domain': str([('id', '=', self.invoice_id.id)]),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.move',
            'view_id': False,
            'views': [(form_view and form_view.id or False, 'form'),
                      (tree_view and tree_view.id or False, 'list')],
            'type': 'ir.actions.act_window',
            'res_id': self.invoice_id.id,
            'target': 'current',
            'nodestroy': True
        }
        return value

    # @api.multi
    def paid_invoice(self):
        self.state = 'soldout'

class Product(models.Model):
    _inherit = 'product.template'
    livestock_id = fields.Many2one('husbandry.livestock', required=False, ondelete='cascade')