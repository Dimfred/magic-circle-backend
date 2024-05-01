from fastapi import APIRouter

from ..deps import Repo
from ..exceptions import UnauthorizedError
from ..user_session.responses import UserSessionOut
from ..utils import urlsafe_unique_token
from .deps import User
from .requests import UserCreateIn, UserLoginIn
from .responses import UserOut

router = APIRouter(prefix="/user")


@router.get("", response_model=UserOut)
async def get_user(user=User):
    return user


@router.post("/register", response_model=UserSessionOut)
async def register_user(req: UserCreateIn, repo=Repo):
    user = repo.user.create(orm=req)
    user_session = repo.user_session.create(key=urlsafe_unique_token(), user=user)
    await repo.commit()

    return user_session


@router.post("/login", response_model=UserSessionOut)
async def login_user(req: UserLoginIn, repo=Repo):
    userdb = await repo.user.first_from_orm(req)
    if userdb is None:
        raise UnauthorizedError("Unknown user or wrong password")

    session = repo.user_session.create(key=urlsafe_unique_token(), user=userdb)
    await repo.commit()

    return session


@router.get("/all", dependencies=[User], response_model=list[UserOut])
async def get_all_users(repo=Repo):
    return await repo.user.all()
