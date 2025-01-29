import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

import routes  # noqa
from config import settings
from utils import router

app = FastAPI()
router.apply_routers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    app.redis = await redis.StrictRedis.from_url(settings.REDIS_URL)


@app.on_event("shutdown")
async def shutdown():
    await getattr(app, 'redis').close()
    await app.redis.close()


register_tortoise(
    app,
    db_url=settings.DATABASE_URL,
    modules={"models": ["data.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.get("/")
async def root():
    return {"message": "FastAPI with Tortoise-ORM and Redis"}
