from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.sql.expression import Select, SelectOfScalar

from .card.repo import CardRepo
from .circle.repo import CircleRepo
from .user.repo import UserRepo
from .user_session.repo import UserSessionRepo

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True
AsyncSession.not_autoflush = True


class Repository(AsyncSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.circle = CircleRepo(self)
        self.user = UserRepo(self)
        self.user_session = UserSessionRepo(self)
        self.card = CardRepo(self)
