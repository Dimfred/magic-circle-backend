from contextlib import asynccontextmanager

import pandas as pd
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel

from . import factory, utils
from .card.routes import router as card_router
from .circle.db import CircleDB
from .common import db_engine, scryfall_rate_limiter
from .config import config
from .deps import aget_repo
from .exceptions import BadRequestError
from .health.routes import router as health_router
from .user.db import UserDB
from .user.routes import router as user_router
from .user_session.db import UserSessionDB


################################################################################
# STARTUP
@asynccontextmanager
async def lifespan(_):  # type: ignore
    utils.init_logger(config.APP_LOG_LEVEL, config.APP_LOGGING_IGNORE)

    if config.APP_ENV == "dev":
        async with db_engine.begin() as c:
            await c.run_sync(SQLModel.metadata.create_all)

    async for repo in aget_repo():
        await repo.circle.first_or_create(
            where=CircleDB.name == "OGCircle", orm=CircleDB(name="OGCircle")
        )

        if config.APP_ENV == "dev":
            for username in ("admin", "admin2"):
                user = await repo.user.first_or_create(
                    where=UserDB.username == username,
                    username=username,
                    password=username,
                )
                await repo.user_session.first_or_create(
                    where=UserSessionDB.user_id == user.id,
                    user_id=user.id,
                    user=user,
                    key=username,
                )

        await repo.commit()

    await scryfall_rate_limiter.release()

    yield


app = factory.create_app(lifespan=lifespan)

################################################################################
# ROUTES
app.include_router(health_router)
app.include_router(card_router)
app.include_router(user_router)

# override all operation ids with function name
for route in app.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name


################################################################################
# BadRequest: 400  # noqa: ERA001
@app.exception_handler(IntegrityError)
@app.exception_handler(pd.errors.ParserError)
@app.exception_handler(RuntimeError)
async def handle_bad_request(_, e):
    logger.error(e)

    return JSONResponse(content={"detail": str(e)}, status_code=400)


################################################################################
# Internal: 500  # noqa: ERA001
@app.exception_handler(Exception)
@app.exception_handler(NotImplementedError)
async def handle_internal_general_error(_, e):  # pragma: no cover
    logger.error("500: !!!!!!!!!!!!!!!!!! UNHANDLED !!!!!!!!!!!!!!!!!!")
    logger.exception(e)

    return JSONResponse(content={"detail": "InternalServerError"}, status_code=500)
