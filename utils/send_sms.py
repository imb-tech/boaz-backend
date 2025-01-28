from redis.asyncio import Redis


async def send_otp(phone_number: str, code: int, redis: Redis):
    await redis.set(f'code:{phone_number}', code)
