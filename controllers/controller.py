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

FARM_CATALOG_ENDPOINT = 'farm-catalog'
FARM_CATALOG_ROUTE_PREFIX = f'{ROUTE_PREFIX}/{FARM_CATALOG_ENDPOINT}'
DKM_CATALOG_ENDPOINT = 'dkm-catalog'
DKM_CATALOG_ROUTE_PREFIX = f'{ROUTE_PREFIX}/{DKM_CATALOG_ENDPOINT}'
CATALOG_ITEM_ENDPOINT = 'catalog-item'
CATALOG_ITEM_ROUTE_PREFIX = f'{ROUTE_PREFIX}/{CATALOG_ITEM_ENDPOINT}'

FALLBACK_IMAGE = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACXBIWXMAAAWJAAAFiQFtaJ36AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAQSURBVHgBAQUA+v8AAAAAAAAFAAFkeJU4AAAAAElFTkSuQmCC'

PRICE_RANGE_DIFF = 3_000_000
PRICE_RANGES_COUNT = 9
PRICE_RANGES = [[(price_range * PRICE_RANGE_DIFF) if price_range > 0 else None, ((price_range + 1) * PRICE_RANGE_DIFF) if price_range < (PRICE_RANGES_COUNT - 1) else None] for price_range in range(PRICE_RANGES_COUNT)]

def log(x, label=None):
    print(f'{f'[{label}] ' if label != None else ''}{type(x).__name__}({x})')
    return x

def format(string: str, **kwargs): return string.format(**kwargs, **get_safe_globals(globals()))

class Controller(http.Controller):

    @http.route(ROUTE_PREFIX)
    def root(self): return http.request.redirect(FARM_CATALOG_ROUTE_PREFIX)

    def catalog(self, title: str, table: str, sql_filters: list[tuple], **kwargs): return format(
        (STATIC_PATH/'catalog.html').read_text(),
        title=title,
        type_filters=to_json([{'name': type.name, 'value': type.id} for type in http.request.env['husbandry.type'].search([])]),
        price_filters=to_json([{
            'name': f'Rp{price_range[0]:,} - {price_range[1]:,}' if price_range[0] and price_range[1] else f'> Rp{price_range[0]:,}' if price_range[0] else f'< Rp{price_range[1]:,}',
            'value': f'{price_range[0] or ''}-{price_range[1] or ''}',
        } for price_range in PRICE_RANGES]),
        cards='\n'.join(format(
            (STATIC_PATH/'catalog_card.html').read_text(),
            **self.get_product_data(product),
        ) for product in http.request.env[table].search([*['|'] * (len(sql_filters) - 1), *sql_filters])
            if (str(product.type_id.id) == str(kwargs['type']) if 'type' in kwargs else True)
            and (float(kwargs['price'].split('-')[0] or '-inf') <= product.purchase_price <= float(kwargs['price'].split('-')[1] or 'inf') if 'price' in kwargs else True)
            and ((str(kwargs['owner']).lower() in [str(product.owner_id.id), str(product.owner_id.name).lower()] if 'owner_id' in dir(product) else False) if 'owner' in kwargs and 'owner' else True)
            and (kwargs['hideall'] != True if 'hideall' in kwargs else True)
        ),
    )

    @http.route(f'{FARM_CATALOG_ROUTE_PREFIX}', auth='public', website=True)
    def farm_catalog(self, **kwargs): return self.catalog(
        'Farm Catalog',
        'husbandry.livestock',
        [('state', '=', 'saleable'), ('state', '=', 'onbook')],
        **kwargs,
    )

    @http.route(f'{DKM_CATALOG_ROUTE_PREFIX}', auth='public', website=True)
    def dkm_catalog(self, **kwargs): return self.catalog(
        'DKM Catalog',
        'husbandry.livestock.purchased',
        [],
        hideall='masjid' not in kwargs,
        owner=kwargs['masjid'] if 'masjid' in kwargs else False,
        **{key: value for key, value in kwargs.items() if key != 'owner'},
    )

    @http.route(f'{CATALOG_ITEM_ROUTE_PREFIX}/<int:id>')
    def catalog_item(self, id: int, **kwargs): return format(
        (STATIC_PATH/'catalog_item.html').read_text(),
        **self.get_product_data(product),
    ) if (product := http.request.env['husbandry.livestock'].browse(id)) else None

    @staticmethod
    def get_product_data(product: HusbandryLivestock): return {
        'product_details_url': f'{CATALOG_ITEM_ROUTE_PREFIX}/{product.id}',
        'inspections': product.get_inspections(),
        'last_inspection_date': (last_inspection_date if (last_inspection := product.get_last_inspection()) and (last_inspection_date := last_inspection.date) else product.create_date.date()).strftime('%d/%m/%Y'),
        'image': f'data:image/*;base64,{(product.get_last_image() or FALLBACK_IMAGE).decode()}',
        'weight_formatted': f'{product.last_weight:,}',
        'age_rounded': f'{round(product.last_age):,}',
        'purchase_price_formatted': f'{product.purchase_price:,}',
        'book_api': f'{ROUTE_PREFIX}/{product.id}/book',
        'images': '\n'.join(format(
            (STATIC_PATH/'catalog_item_image.html').read_text(),
            image=f'data:image/*;base64,{image.decode()}'
        ) for image in product.get_images()),
        **{product_attr: eval(f'product.{product_attr}') for product_attr in dir(product) if all(not product_attr.startswith(x) for x in ['<', '_'])},
    }

    @http.route(f'{ROUTE_PREFIX}/<int:id>/book')
    def book(self, id: int, **kwargs):
        http.request.env['husbandry.livestock'].browse(id).book()
        return to_json(True)

    @http.route(f'{STATIC_ROUTE_PREFIX}/<path:subpath>')
    def static(self, subpath: Path | str, **kwargs):
        if str((STATIC_PATH/subpath).resolve()).startswith(str(STATIC_PATH)):
            try: return (STATIC_PATH/subpath).read_text()
            except UnicodeDecodeError: return (STATIC_PATH/subpath).read_bytes()