from datetime import datetime, timedelta

from aiohttp import ClientSession

from config import settings
from data.schemas import BillzRequestSchema


class Billz:
    __base_url = "https://api-admin.billz.ai/"

    __access_token: str = None
    __access_token_expire: datetime = None

    async def login_billz(self) -> None:
        if self.__access_token and self.__access_token_expire > datetime.now():
            return
        async with ClientSession(base_url=Billz.__base_url) as session:
            async with session.post(
                    'v1/auth/login',
                    json={"secret_token": settings.BILLZ_TOKEN},
                    ssl=False,
                    headers={"Content-Type": "application/json"},
            ) as response:
                response = await response.json()
                self.__access_token = response['data']['access_token']
                self.__access_token_expire = datetime.now() + timedelta(days=15)

    async def send_request(self, operation: BillzRequestSchema, request_method: str = 'GET', data: dict = None) -> dict:
        await self.login_billz()
        headers = {'Authorization': f'Bearer {self.__access_token}'}
        async with ClientSession(base_url=Billz.__base_url) as session:
            try:
                async with session.request(
                        method=request_method,
                        url=operation.path,
                        headers=headers,
                        json=data if data else {},
                        ssl=False
                ) as response:
                    return await response.json()
            except Exception as e:
                return {'error': str(e)}

    async def get_all_products(self):
        return await self.send_request(
            BillzRequestSchema(path='v2/product-search-with-filters'),
            request_method='POST',
            data={"search": "", "status": "all", "order": [""], "group_variations": True, "product_field_filters": [],
                  "field_search_key": "", "archived_list": False, "brand_ids": [], "supplier_ids": [],
                  "measurement_unit_ids": [], "is_free_price": None, "supply_price_from": 1, "retail_price_from": 1,
                  "shop_ids": ["fac0d3fd-4d70-4082-88f4-2da77752f071"], "statistics": True, "limit": 10000, "page": 1}
        )


billz = Billz()
