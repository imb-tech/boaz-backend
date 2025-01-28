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


@billz_router.post('/')
async def billz_proxy(operation: BillzRequestSchema):
    path = operation.path
    if path == 'v2/products':
        if not product_data or product_data['expire_fetch'] < datetime.now(timezone.utc):
            product_data.update(await billz.send_request(operation))
            product_data['expire_fetch'] = datetime.now(timezone.utc) + timedelta(
                minutes=settings.BILLZ_EXPIRE_DATA_MINUTES)

        return JSONResponse(content=product_data)
    return JSONResponse(content=await billz.send_request(operation))
