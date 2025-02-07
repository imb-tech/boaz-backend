import asyncio
import re
from datetime import datetime, timedelta, timezone

from starlette.responses import JSONResponse

from config import settings
from data.schemas import BillzRequestSchema
from integrator.tunnel import billz
from utils import router

billz_router = router(
    '/billz', tags=['billz'],
)

class BillzControl:
    __product_data: dict = None
    __demo_data: dict = {
            "id": "815e30fd-0c22-4443-84ee-2ca13908ea03",
            "company_id": "24f3bc53-42b6-4b29-bfb9-a33dfbb9ff61",
            "name": "Sayt ishlamadi, qayta yangilang",
            "sku": "M-042",
            "barcode": "2000000006208",
            "retail_price": 0,
            "supply_price": 0,
            "description": "<p class=\"editor-paragraph\"><br></p>",
            "measurement_values": {
                "total_measurement_value": 21,
                "total_active_measurement_value": 21,
                "total_inactive_measurement_value": 0
            },
            "measurement_unit": {
                "id": "88f90a48-c5a9-4f15-99eb-1eef249776c6",
                "name": "Штука",
                "company_id": "",
                "short_name": "шт",
                "precision": "1",
                "is_editable": False,
                "is_default": False
            },
            "shop_measurement_values": [
                {
                    "small_left_measurement_value": 0,
                    "has_trigger": False,
                    "shop_id": "fac0d3fd-4d70-4082-88f4-2da77752f071",
                    "total_measurement_value": 21,
                    "total_min_supply_price": 123500,
                    "total_max_supply_price": 123500,
                    "total_supply_sum": 2593500,
                    "total_active_measurement_value": 21,
                    "total_active_min_supply_price": 123500,
                    "total_active_max_supply_price": 123500,
                    "total_active_supply_sum": 2593500,
                    "total_inactive_measurement_value": 0,
                    "total_inactive_min_supply_price": False,
                    "total_inactive_max_supply_price": False,
                    "total_inactive_supply_sum": 0,
                    "total_sold_measurement_value": 79,
                    "total_imported_measurement_value": 0,
                    "total_transfer_arrived_measurement_value": 0,
                    "total_transfered_measurement_value": 0,
                    "total_in_transfer_measurement_value": 0,
                    "total_in_transfer_min_supply_price": None,
                    "total_in_transfer_max_supply_price": None,
                    "total_in_transfer_supply_sum": 0,
                    "total_written_off_measurement_value": 0,
                    "import_started_measurement_value": 0,
                    "is_small_left": False,
                    "total_retail_sum": 3780000,
                    "total_active_retail_sum": 3780000,
                    "total_inactive_retail_sum": 0
                }
            ],
            "shop_prices": [
                {
                    "shop_id": "fac0d3fd-4d70-4082-88f4-2da77752f071",
                    "retail_price": 180000,
                    "retail_currency": "UZS",
                    "supply_currency": "UZS",
                    "min_supply_price": 123500,
                    "max_supply_price": 123500,
                    "supply_price": 123500,
                    "wholesale_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "prices_list": [],
                    "from_supply_price": 0,
                    "currency_prices": [
                        {
                            "currency": "UZS",
                            "retail_price": 180000,
                            "min_supply_price": 123500,
                            "max_supply_price": 123500,
                            "supply_price": 123500,
                            "wholesale_price": 0,
                            "min_price": 0,
                            "max_price": 0,
                            "prices_list": []
                        }
                    ],
                    "promo_price": 0,
                    "promos": None
                },
                {
                    "shop_id": "3c1b6d19-b33c-48b8-a8c6-813270b8bb12",
                    "retail_price": 180000,
                    "retail_currency": "",
                    "supply_currency": "UZS",
                    "min_supply_price": 0,
                    "max_supply_price": 0,
                    "supply_price": 0,
                    "wholesale_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "prices_list": None,
                    "from_supply_price": 0,
                    "currency_prices": [
                        {
                            "currency": "UZS",
                            "retail_price": 180000,
                            "min_supply_price": 0,
                            "max_supply_price": 0,
                            "supply_price": 0,
                            "wholesale_price": 0,
                            "min_price": 0,
                            "max_price": 0,
                            "prices_list": []
                        }
                    ],
                    "promo_price": 0,
                    "promos": None
                },
                {
                    "shop_id": "57af858a-ca2e-4bee-bea6-d52ed492de8f",
                    "retail_price": 180000,
                    "retail_currency": "UZS",
                    "supply_currency": "UZS",
                    "min_supply_price": 0,
                    "max_supply_price": 0,
                    "supply_price": 0,
                    "wholesale_price": 0,
                    "min_price": 0,
                    "max_price": 0,
                    "prices_list": None,
                    "from_supply_price": 0,
                    "currency_prices": [
                        {
                            "currency": "UZS",
                            "retail_price": 180000,
                            "min_supply_price": 0,
                            "max_supply_price": 0,
                            "supply_price": 0,
                            "wholesale_price": 0,
                            "min_price": 0,
                            "max_price": 0,
                            "prices_list": []
                        }
                    ],
                    "promo_price": 0,
                    "promos": None
                }
            ],
            "prices": {
                "total_supply_price": 0,
                "total_retail_price": 0,
                "total_active_supply_price": 0,
                "total_active_retail_price": 0,
                "total_inactive_supply_price": 0,
                "total_inactive_retail_price": 0
            },
            "product_type_id": "69e939aa-9b8f-46a9-b605-8b2675475b7b",
            "created_at": "2025-01-23 08:59:10",
            "updated_at": "2025-02-06 10:48:59",
            "brand_id": "bc7fc2e0-7338-431b-b485-67f96d841ddc",
            "brand_name": "Minix afshon",
            "base_name": "Elektr isitgich",
            "archived_at": "1970-01-01T06:00:00Z",
            "archived_by": {
                "id": "",
                "name": ""
            },
            "product_supplier_stock": [
                {
                    "supplier_id": "00000000-0000-0000-0000-000000000000",
                    "supplier_name": "",
                    "shop_id": "fac0d3fd-4d70-4082-88f4-2da77752f071",
                    "measurement_value": 21,
                    "min_supply_price": 123500,
                    "max_supply_price": 123500,
                    "retail_price": 180000,
                    "wholesale_price": 0
                }
            ],
            "product_supply_stock": [
                {
                    "shop_id": "fac0d3fd-4d70-4082-88f4-2da77752f071",
                    "shop_name": "BOAZ",
                    "measurement_value": 21,
                    "active_measurement_value": 21,
                    "inactive_measurement_value": 0,
                    "supply_price": 123500,
                    "supplier_ids": [
                        "00000000-0000-0000-0000-000000000000"
                    ]
                }
            ],
            "status": 0,
            "scale_plu": 0,
            "scale_code": 0,
            "is_scalable": False,
            "shop_free_prices": None
        },

    def __init__(self):
        self.__product_data = {}


    async def refresh_products(self) -> dict:
        if not self.__product_data or self.__product_data['expire_fetch'] < datetime.now(timezone.utc):
            try:
                new_data = await billz.get_all_products()
                new_data['expire_fetch'] = datetime.now(timezone.utc) + timedelta(
                    minutes=settings.BILLZ_EXPIRE_DATA_MINUTES
                )
                if 'error' not in new_data:
                    new_data["products"].sort(
                        key=lambda x: datetime.strptime(x["updated_at"], "%Y-%m-%d %H:%M:%S"), reverse=True)
                    self.__product_data = new_data
                else:
                    return self.__demo_data
            except:
                return self.__product_data if self.__product_data else self.__demo_data

        return {k: v for k, v in self.__product_data.items() if k != 'expire_fetch'}


    def search_product(self, patterns: list[str]) -> list:
        matching_products = []
        added_ids = set()
        for pattern in patterns:
            for product in self.__product_data['products']:
                if re.search(
                        pattern,
                        re.sub(r'[.,-_]', '', product["name"].lower()),
                        flags=re.IGNORECASE) and product['id'] not in added_ids:
                    matching_products.append(product)
                    added_ids.add(product['id'])

        return matching_products


    def filter_with_sku(self, sku: str) -> list:
        matching_products = []
        for product in self.__product_data['products']:
            if product['sku'] == sku:
                matching_products.append(product)
        return matching_products



billz_control = BillzControl()

@billz_router.get('/products', tags=['billz'])
async def get_products(
        search: str = None,
        limit: int = 100,
        offset: int = 0,
        product_id: str = None,
        category_id: str = None,
):
    products_result: dict = await billz_control.refresh_products()
    if 'products' in products_result:
        products = products_result['products']
    else:
        products = [products_result]
    try:
        if product_id:
            products = [p for p in products if p['id'] == product_id]

        if category_id:
            products = [p for p in products if any(c['id'] == category_id for c in p.get('categories', []))]

        if search:

            if ' ' not in search:
                products = billz_control.filter_with_sku(search)

            if not products:
                cleaned_pattern = re.sub(r'[.,-_]', '', search).lower()
                matching_products = billz_control.search_product(cleaned_pattern.split(' '))
                products = matching_products
        products = products[offset:limit + offset]
        return {'count': len(products), 'offset': offset, 'products': products}

    except Exception as e:
        return {'error': str(e)}


@billz_router.post('')
async def billz_proxy(operation: BillzRequestSchema):
    return JSONResponse(content=await billz.send_request(operation))
