from datetime import datetime, timedelta

from aiohttp import ClientSession

from config import settings
from data.schemas import BillzRequestSchema


class Billz:
    __base_url = "https://api-admin.billz.ai/v1/"

    __access_token: str = None
    __access_token_expire: datetime = None

    async def login_billz(self) -> None:
        if self.__access_token and self.__access_token_expire > datetime.now():
            return
        async with ClientSession(base_url=Billz.__base_url) as session:
            async with session.post(
                    'v1/auth/login',
                    data={"secret_key": settings.BILLZ_TOKEN}
            ) as response:
                response = await response.json()
                self.__access_token = response['data']['access_token']
                self.__access_token_expire = datetime.now() + timedelta(days=15)

    async def send_request(self, operation: BillzRequestSchema) -> dict:
        await self.login_billz()
        headers = {'Authorization': f'Bearer {self.__access_token}'}
        async with ClientSession(base_url=Billz.__base_url) as session:
            async with session.request(
                    method=operation.method,
                    url=operation.path,
                    headers=headers,
                    data=operation.body,
            ) as response:
                return await response.json()


billz = Billz()
