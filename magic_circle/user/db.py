from sqlmodel import Field, Relationship

from ..circle.db import CircleUserLinkDB
from .bases import UserBase


class UserDB(UserBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    username: str = Field(unique=True, index=True)
    password: str

    sessions: list["UserSessionDB"] = Relationship(back_populates="user")  # type: ignore
    cards: list["CardDB"] = Relationship(back_populates="owner")  # type: ignore
    circles: list["CircleDB"] = Relationship(  # type: ignore
        back_populates="members", link_model=CircleUserLinkDB
    )
