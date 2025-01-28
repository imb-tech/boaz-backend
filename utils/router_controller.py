from typing import List

from fastapi import APIRouter as _APIRouter, FastAPI
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette.responses import JSONResponse


class APIRouter:
    __routers__: List[_APIRouter]

    def __init__(self):
        self.__routers__ = []

    def __call__(self, prefix="", tags=None, dependencies=None, default_response_class=Default(JSONResponse),
                 responses=None, callbacks=None, routes=None, redirect_slashes=True, default=None,
                 dependency_overrides_provider=None, route_class=APIRoute, on_startup=None, on_shutdown=None,
                 lifespan=None, deprecated=None, include_in_schema=True,
                 generate_unique_id_function=Default(generate_unique_id),
                 ) -> _APIRouter:
        api_router = _APIRouter(prefix=prefix, tags=tags, dependencies=dependencies,
                                default_response_class=default_response_class, responses=responses, callbacks=callbacks,
                                routes=routes, redirect_slashes=redirect_slashes, default=default,
                                dependency_overrides_provider=dependency_overrides_provider, route_class=route_class,
                                on_startup=on_startup, on_shutdown=on_shutdown, lifespan=lifespan,
                                deprecated=deprecated, include_in_schema=include_in_schema,
                                generate_unique_id_function=generate_unique_id_function)
        self.__routers__.append(api_router)
        return api_router

    def apply_routers(self, app: FastAPI):
        for api_router in self.__routers__:
            app.include_router(api_router)


router = APIRouter()

__all__ = ["router"]
