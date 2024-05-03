from sqlmodel import and_, delete, not_, or_, select
from sqlmodel_repository import AsyncRepository

from .db import CardDB


class CardRepo(AsyncRepository[CardDB]):
    def __init__(self, db):
        super().__init__(db, CardDB)

    async def delete_all(self, owner_id: int):
        """Delete all cards owned by a user."""
        stmt = delete(CardDB).where(CardDB.owner_id == owner_id)  # type: ignore
        await self.db.exec(stmt)

    def all_cards_owned_by_someone_else(
        self, card_names: list[str], owner_id: int, *, exact_name: bool
    ):
        """Show all cards that another user owns, but not the user who queries."""
        return or_(
            *(
                and_(
                    self._match_card_name(card_name, exact_name=exact_name),
                    not_(
                        self._user_owns_card(card_name, owner_id, exact_name=exact_name)
                    ),  # type: ignore
                    self._other_user_owns_card(
                        card_name, owner_id, exact_name=exact_name
                    ),
                )
                for card_name in card_names
            )
        )

    def _match_card_name(self, card_name: str, *, exact_name: bool):
        if exact_name:
            return CardDB.name == card_name

        return CardDB.name.ilike(f"%{card_name}%")  # type: ignore

    def _user_owns_card(self, card_name: str, owner_id: int, *, exact_name: bool):
        """Check whether a user owns a specific card."""
        q = select(CardDB.name, CardDB.owner_id)

        if exact_name:
            q = q.where(and_(CardDB.name == card_name, CardDB.owner_id == owner_id))
        else:
            q = q.where(
                and_(CardDB.name.ilike(f"%{card_name}%"), CardDB.owner_id == owner_id)  # type: ignore
            )

        return q.exists()

    def _other_user_owns_card(self, card_name: str, owner_id: int, *, exact_name: bool):
        """Check whether any other user owns a specific card."""
        q = select(CardDB.name, CardDB.owner_id)
        if exact_name:
            q = q.where(and_(CardDB.name == card_name, CardDB.owner_id != owner_id))
        else:
            q = q.where(
                and_(CardDB.name.ilike(f"%{card_name}%"), CardDB.owner_id != owner_id)  # type: ignore
            )

        return q.exists()
