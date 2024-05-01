from sqlmodel import Field, Relationship, SQLModel

from .bases import UserSessionBase


class UserSessionDB(UserSessionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    key: str = Field(unique=True)

    user_id: int | None = Field(default=None, foreign_key="userdb.id")
    user: "UserDB" = Relationship(back_populates="sessions")  # type: ignore
