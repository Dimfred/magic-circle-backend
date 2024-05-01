from sqlmodel import SQLModel


class UserBase(SQLModel):
    username: str
