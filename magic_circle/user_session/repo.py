from sqlmodel_repository import AsyncRepository

from .db import UserSessionDB


class UserSessionRepo(AsyncRepository[UserSessionDB]):
    def __init__(self, db):
        super().__init__(db, UserSessionDB)
