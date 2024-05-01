from sqlmodel_repository import AsyncRepository

from .db import CircleDB


class CircleRepo(AsyncRepository[CircleDB]):
    def __init__(self, db):
        super().__init__(db, CircleDB)
