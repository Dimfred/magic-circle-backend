from sqlmodel import delete
from sqlmodel_repository import AsyncRepository

from .db import CardDB


class CardRepo(AsyncRepository[CardDB]):
    def __init__(self, db):
        super().__init__(db, CardDB)

    async def delete_all(self, owner_id: int):
        stmt = delete(CardDB).where(CardDB.owner_id == owner_id)  # type: ignore
        await self.db.exec(stmt)
