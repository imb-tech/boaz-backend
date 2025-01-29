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

product_data = {}


async def get_products(operation):
    if not product_data or product_data['expire_fetch'] < datetime.now(timezone.utc):
        product_data.update(await billz.send_request(operation))
        product_data['expire_fetch'] = datetime.now(timezone.utc) + timedelta(
            minutes=settings.BILLZ_EXPIRE_DATA_MINUTES)
    return product_data


@billz_router.post('')
async def billz_proxy(operation: BillzRequestSchema):
    path = operation.path
    if path == 'v2/products':
        products = await get_products(operation)
        return JSONResponse(content=products)
    elif path.startswith('v2/product?search='):
        query = path[18:]

        def clean_string(text):
            return re.sub(r'[.,-_]', '', text)

        # Function to clean the user input pattern
        def clean_pattern(pattern):
            return re.sub(r'[.,-_]', '', pattern)

        user_pattern = "Plastik"
        cleaned_pattern = clean_pattern(user_pattern)
        matching_products = [
            product for product in product_data['products'] if
            re.search(cleaned_pattern, clean_string(product["name"]), re.IGNORECASE)
        ]

        return matching_products

    return JSONResponse(content=await billz.send_request(operation))
