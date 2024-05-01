from depends import Depends as DDepends
from depends import inject  # noqa: F401
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import sessionmaker

from .common import db_engine
from .config import config
from .repo import Repository

make_session = sessionmaker(db_engine, class_=Repository, **config.DB_SESSION_CONFIG)


async def aget_repo():  # pragma: no cover
    async with make_session() as db:
        yield db


Repo = Depends(aget_repo)
DRepo = DDepends(aget_repo)
