from sqlmodel import Field, Relationship, SQLModel

from .bases import CircleBase


class CircleUserLinkDB(SQLModel, table=True):  # type: ignore
    user_id: int | None = Field(default=None, foreign_key="userdb.id", primary_key=True)
    circle_id: int | None = Field(
        default=None, foreign_key="circledb.id", primary_key=True
    )


class CircleDB(CircleBase, table=True):  # type: ignore
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(unique=True, index=True)
    members: list["UserDB"] = Relationship(  # type: ignore
        back_populates="circles", link_model=CircleUserLinkDB
    )
