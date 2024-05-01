from sqlmodel import SQLModel


class CircleBase(SQLModel):
    name: str
