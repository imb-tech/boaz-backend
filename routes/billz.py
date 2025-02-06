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
            except:
                return self.__product_data

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
    products: list = (await billz_control.refresh_products())['products']
    try:
        if product_id:
            products = [p for p in products if p['id'] == product_id]

        if category_id:
            products = [p for p in products if any(c['id'] == category_id for c in p.get('categories', []))]

        if search:

            if ' ' not in search:
                filtered_with_sku = billz_control.filter_with_sku(search)
                if filtered_with_sku:
                    products = filtered_with_sku

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
    #     path = operation.path
    #     if path == 'v2/products':
    #         products = await refresh_products(operation)
    #         return JSONResponse(content=products)
    #     elif path.startswith('v2/products?search='):
    #         products = await refresh_products(operation)
    #         query_part = path[len('v2/product?search='):]
    #         limit = None
    #         if '&limit=' in query_part:
    #             query, limit_part = query_part.split('&limit=', 1)
    #             if limit_part.isdigit():
    #                 limit = int(limit_part)
    #                 print(limit)
    #         else:
    #             query = query_part
    #
    #         def clean_string(text):
    #             return re.sub(r'[.,-_]', '', text)
    #
    #         def clean_pattern(pattern):
    #             return re.sub(r'[.,-_]', '', pattern)
    #
    #         cleaned_pattern = clean_pattern(query)
    #         matching_products = [
    #             product for product in products['products']
    #             if re.search(cleaned_pattern, clean_string(product["name"]), re.IGNORECASE)
    #         ]
    #
    #         return {
    #             'count': len(matching_products),
    #             'products': matching_products[:limit] if limit else matching_products
    #         }
    return JSONResponse(content=await billz.send_request(operation))
