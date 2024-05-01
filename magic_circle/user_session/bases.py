from sqlmodel import SQLModel


class UserSessionBase(SQLModel):
    key: str
