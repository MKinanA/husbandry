from odoo import models, fields, api # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
class HusbandryInspection(models.Model):
    _name = 'husbandry.inspection'

    name = fields.Char(string="Reference", required=True)
    note = fields.Text(string="Note")
    date = fields.Date(string="Inspection Date")
    livestock_id = fields.Many2one('husbandry.livestock', string="Livestock")
    weight = fields.Float(string="Current Weight (kg)")
    age = fields.Float(string="Current Age")
    image_front = fields.Binary(string="Front Image")
    image_right = fields.Binary(string="Right Image")
    image_left = fields.Binary(string="Left Image")
    image_back = fields.Binary(string="Back Image")

    """@api.model
    def create(self, vals):
        result = super().create(vals)
        result.name = str(result.id).zfill(3)
        return result"""

    @api.model
    def get_view(self, view_id=None, view_type='form', toolbar=False, submenu=False, **unused_kwargs):
        print('\nget_view method on HusbandryInspection called')
        res = super().get_view(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
           res['arch'] = """
                <form string="Inspection">
                    <sheet>
                        <group>
                            <group>
                                <field name="name"/>
                                <field name="age"/>
                                <field name="note"/>
                            </group>
                            <group>
                                <field name="livestock_id"/>
                                <field name="weight"/>
                                <field name="date"/>
                            </group>
                        </group>
                        <notebook>
                            <page string="Images">
                                <group>
                                    <field name="image_front" widget="image"/>
                                    <field name="image_right" widget="image"/>
                                    <field name="image_left" widget="image"/>
                                    <field name="image_back" widget="image"/>
                                </group>
                            </page>
                        </notebook>
                    </sheet>
                </form>
        """
        elif view_type == 'list':
             res['arch'] = """
                <list string="Inpsection">
                    <field name="name"/>
                    <field name="date"/>
                    <field name="livestock_id"/>
                </list>
        """
        elif view_type == 'search':
             res['arch'] = """
                <search string="Inpsection">
                    <field name="name"/>
                    <field name="date"/>
                    <field name="livestock_id"/>
                </search>
        """
        from lxml import etree
        doc = etree.XML(res['arch'])
        View = self.env['ir.ui.view'].sudo()
        res['arch'], res['fields'] = View.postprocess_and_fields(doc, self._name)
        return res
