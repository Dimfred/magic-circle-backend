from fastapi import Depends, Header

from ..deps import Repo
from ..exceptions import UnauthorizedError
from ..user_session.db import UserSessionDB


async def get_user(x_session_key: str = Header(None), repo=Repo):
    userdb = await repo.user_session.first(
        where=UserSessionDB.key == x_session_key, relationships=[UserSessionDB.user]
    )
    if userdb is None:
        raise UnauthorizedError("Unknown key, try to login again")

    return userdb.user


User = Depends(get_user)
