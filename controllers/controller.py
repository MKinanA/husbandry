from odoo import http # pyright: ignore[reportMissingImports, reportAttributeAccessIssue] (ignore any import warnings here)
from pathlib import Path
from json import loads as from_json, dumps as to_json
from ..models.livestock import HusbandryLivestock
from ..helpers.get_odoo_module_path import get_odoo_module_path

private_globals = {*globals(), 'private_globals'} # A snapshot of all keys of `globals()` after declaration of all private consts, anything global declared after this will be exposed and accessible by the internet
get_safe_globals = lambda globals: {key: globals[key] for key in globals if key not in private_globals}

ODOO_MODULE_PATH = get_odoo_module_path(__file__).resolve()
ODOO_MODULE_NAME = ODOO_MODULE_PATH.parts[-1]
ROUTE_PREFIX = f'/{ODOO_MODULE_NAME}'
STATIC_FOLDER = 'static'
STATIC_PATH = ODOO_MODULE_PATH/STATIC_FOLDER
STATIC_ROUTE_PREFIX = f'{ROUTE_PREFIX}/{STATIC_FOLDER}'
FALLBACK_IMAGE = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACXBIWXMAAAWJAAAFiQFtaJ36AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAQSURBVHgBAQUA+v8AAAAAAAAFAAFkeJU4AAAAAElFTkSuQmCC'

def format(string: str, **kwargs): return string.format(**kwargs, **get_safe_globals(globals()))

class Controller(http.Controller):

    @http.route(ROUTE_PREFIX)
    def root(self, **kwargs): return format(
        (STATIC_PATH/'catalog.html').read_text(),
        filters=to_json([{'name': type.name, 'value': type.id} for type in http.request.env['husbandry.type'].search([])]),
        cards='\n'.join(format(
            (STATIC_PATH/'catalog_card.html').read_text(),
            **self.get_product_data(product),
        ) for product in http.request.env['husbandry.livestock'].search(['|', ('state', '=', 'saleable'), ('state', '=', 'onbook')]) if (str(product.type_id.id) == str(kwargs['filter']) if 'filter' in kwargs else True)),
    )

    @staticmethod
    def get_product_data(product: HusbandryLivestock): return {
        'inspections': product.get_inspections(),
        'last_inspection': product.get_last_inspection(),
        'image': f'data:image/*;base64,{(product.get_last_image() or FALLBACK_IMAGE).decode()}',
        'weight_formatted': f'{product.weight:,}',
        'purchase_price_formatted': f'{product.purchase_price:,}',
        'book_api': f'{ROUTE_PREFIX}/{product.id}/book',
        **{product_attr: eval(f'product.{product_attr}') for product_attr in dir(product) if all(not product_attr.startswith(x) for x in ['<', '_'])},
    }

    @http.route(f'{ROUTE_PREFIX}/<int:id>/book')
    def book(self, id: int, **kwargs):
        http.request.env['husbandry.livestock'].browse(id).update({
            'state': 'onbook',
        })
        return to_json(True)

    @http.route(f'{STATIC_ROUTE_PREFIX}/<path:subpath>')
    def static(self, subpath: Path | str, **kwargs):
        if str((STATIC_PATH/subpath).resolve()).startswith(str(STATIC_PATH)):
            try: return (STATIC_PATH/subpath).read_text()
            except UnicodeDecodeError: return (STATIC_PATH/subpath).read_bytes()