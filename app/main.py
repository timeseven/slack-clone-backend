from contextlib import asynccontextmanager

from arq import create_pool
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from loguru import logger
from socketio.asgi import ASGIApp

from app.core.arq_worker import REDIS_SETTINGS
from app.core.config import settings
from app.core.response import error_response
from app.core.routes import api_router
from app.modules.notifications.realtime.socketio_app import sio
from app.modules.notifications.realtime.socketio_manager import socketio_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("starting...")
        app.state.arq_redis = await create_pool(REDIS_SETTINGS)
    except Exception as e:
        logger.error(f"Redis PubSub start failed: {e}")
        app.state.arq_redis = None

    yield

    try:
        logger.info("stopping...")
        if app.state.arq_redis:
            await app.state.arq_redis.close()
    except Exception as e:
        logger.error(f"Redis PubSub stop failed: {e}")


fastapi_app = FastAPI(
    default_response_class=ORJSONResponse,
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

if settings.all_cors_origins:
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@fastapi_app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"New request: {request.method} {request.url}")
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.exception("Unhandled error occurred")
        raise e


@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    formatted_errors = []
    for error in exc.errors():
        loc = error.get("loc", [])
        error_msg = error.get("msg")
        if "ctx" in error and "error" in error["ctx"]:
            error_msg = str(error["ctx"]["error"])
        if len(loc) > 1:
            field = loc[1]
        elif loc:
            field = loc[0]
        else:
            field = "body"
        formatted_errors.append({field: error_msg})
    return error_response(status_code=422, message=formatted_errors)


@fastapi_app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    print(">>>>>>>>>>>>", exc, exc.status_code)
    return error_response(status_code=exc.status_code, message=exc.detail)


fastapi_app.include_router(api_router, prefix=settings.API_V1_STR)

socketio_manager.setup_event_handlers()
app = ASGIApp(sio, other_asgi_app=fastapi_app)
