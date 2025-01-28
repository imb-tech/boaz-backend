from datetime import datetime, timezone
from random import randint

from fastapi import Request, BackgroundTasks, HTTPException
from redis.asyncio import Redis

from data.models import User
from data.schemas import BaseUserSchema, UserPhoneValidateSchema, BearerTokenSchema
from utils import router
from utils.depends import CurrentUser
from utils.send_sms import send_otp
from utils.token_manager import create_jwt_token

user_router = router(
    '/user'
)

waiting_numbers = set()


@user_router.get('', response_model=BaseUserSchema)
async def fetch_user_info(user: CurrentUser):
    return user


OTP_REQUEST_LIMIT = 3
TIME_WINDOW = 60


@user_router.get('/polling')
async def polling_from_phone():
    copied_phones = waiting_numbers.copy()
    waiting_numbers.clear()
    return copied_phones


@user_router.post('/send-sms')
async def create_user(request: Request, user: BaseUserSchema, background_tasks: BackgroundTasks):
    redis: Redis = request.app.redis
    key = f'throttle-{user.phone_number}'
    current_time = datetime.now(timezone.utc).timestamp()

    attempts = await redis.lrange(key, 0, -1)

    valid_attempts = [float(attempt) for attempt in attempts if float(attempt) > current_time - TIME_WINDOW]

    if len(valid_attempts) >= OTP_REQUEST_LIMIT:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")

    await redis.rpush(key, current_time)
    await redis.expire(key, TIME_WINDOW)
    random_code = randint(100000, 999999)
    background_tasks.add_task(send_otp, user.phone_number, random_code, redis)
    waiting_numbers.add((user.phone_number, random_code))

    return {"message": "OTP sent successfully"}


@user_router.post('/verify')
async def user_verify(request: Request, user: UserPhoneValidateSchema):
    if not user.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    redis: Redis = request.app.redis
    key = f'throttle-{user.phone_number}'

    user_cache = await redis.get(f'code:{user.phone_number}')
    if not user_cache:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    if user_cache.decode() != user.code:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    created_user = await User.create()
    generated_token = create_jwt_token({"user_id": user.id})
    await redis.delete(f'code:{user.phone_number}')
    return BearerTokenSchema(token=generated_token, token_type='Bearer')


# @user_router.post('/new-user')
# async def create_new_user(request: Request, user: BaseUserSchema):