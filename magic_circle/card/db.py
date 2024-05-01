from sqlmodel import Field, Relationship

from .bases import CardBase


class CardDB(CardBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    owner_id: int = Field(default=None, foreign_key="userdb.id")
    owner: "UserDB" = Relationship(back_populates="cards")  # type: ignore
