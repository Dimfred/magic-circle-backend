from .bases import UserBase


class UserCreateIn(UserBase):
    password: str


class UserLoginIn(UserCreateIn):
    pass
