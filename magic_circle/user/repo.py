from sqlmodel import and_
from sqlmodel_repository import AsyncRepository

from ..utils.utils import sha256
from .db import UserDB
from .requests import UserLoginIn


class UserRepo(AsyncRepository[UserDB]):
    def __init__(self, db):
        super().__init__(db, UserDB)

    async def first_or_create(self, *args, **kwargs):
        userdb = await super().first(where=UserDB.username == kwargs["username"])
        if userdb is None:
            userdb = self.create(*args, **kwargs)
            await self.db.commit()
            await self.db.refresh(userdb)

        return userdb

    def create(self, *args, **kwargs):
        if "password" in kwargs and kwargs["password"]:
            kwargs["password"] = sha256(kwargs["password"])

        if "orm" in kwargs and kwargs["orm"]:
            kwargs["orm"].password = sha256(kwargs["orm"].password)

        return super().create(*args, **kwargs)

    async def first_from_orm(self, req: UserLoginIn):
        req.password = sha256(req.password)

        return await super().first(
            where=and_(  # type: ignore
                UserDB.username == req.username, UserDB.password == req.password
            ),
            relationships=[UserDB.sessions],
        )
