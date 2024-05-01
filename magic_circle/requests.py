from pydantic import model_validator
from sqlmodel import SQLModel


class PaginatedIn(SQLModel):
    page: int = 0
    max_page: int = 50

    @property
    def offset(self):
        return self.page * self.max_page

    @model_validator(mode="after")
    def validate_limits(cls, values):
        assert values.page >= 0
        assert 1 <= values.max_page <= 100  # noqa: PLR2004

        return values


class CardFilterIn(SQLModel):
    name: str | None
    set_code: str | None
    set: str | None
