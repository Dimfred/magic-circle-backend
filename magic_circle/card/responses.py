from ..user.responses import UserOut
from .bases import CardBase


class CardOut(CardBase):
    owner: UserOut
