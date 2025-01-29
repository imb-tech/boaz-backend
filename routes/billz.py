import json
import re
from datetime import datetime, timedelta, timezone

from starlette.responses import JSONResponse, Response

from config import settings
from data.schemas import BillzRequestSchema
from integrator.tunnel import billz
from utils import router

billz_router = router(
    '/billz', tags=['billz'],
)

product_data = {}


async def refresh_products(operation):
    global product_data
    if not product_data or product_data['expire_fetch'] < datetime.now(timezone.utc):
        product_data.update(await billz.send_request(operation))
        product_data['expire_fetch'] = datetime.now(timezone.utc) + timedelta(
            minutes=settings.BILLZ_EXPIRE_DATA_MINUTES)
    product_data_for_response = product_data.copy()
    del product_data_for_response['expire_fetch']
    return product_data_for_response


@billz_router.post('')
async def billz_proxy(operation: BillzRequestSchema):
    global product_data
    path = operation.path
    if path == 'v2/products':
        products = await refresh_products(operation)
        return JSONResponse(content=products)
    elif path.startswith('v2/products?search='):
        if not product_data:
            product_data = await refresh_products(operation)
        query = path[18:]

        def clean_string(text):
            return re.sub(r'[.,-_]', '', text)

        def clean_pattern(pattern):
            return re.sub(r'[.,-_]', '', pattern)

        cleaned_pattern = clean_pattern(query)
        matching_products = [
            product for product in product_data['products'] if
            re.search(cleaned_pattern, clean_string(product["name"]), re.IGNORECASE)
        ]
        if path.startswith(f'v2/product?search={query}&limit='):
            limit = path[len(f'v2/product?search={query}&limit='):]
            if limit.isdigit():
                return {'count': int(limit), 'products': matching_products[int(limit):]}

        return {'count': len(matching_products), 'products': matching_products}

    return JSONResponse(content=await billz.send_request(operation))
