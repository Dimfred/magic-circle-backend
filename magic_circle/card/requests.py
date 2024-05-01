from typing import Optional

from fastapi import HTTPException
from pydantic import model_validator

from ..requests import PaginatedIn
from .parser import ParserFormat


class CardsGetIn(PaginatedIn):
    usernames: Optional[list[str]]
    decklist: Optional[str]
    decklist_format: Optional[ParserFormat]

    @model_validator(mode="before")
    def validate_decklist(cls, values):
        if values.get("decklist") and not values.get("decklist_format"):
            raise HTTPException(
                detail="decklist_format is required when decklist is provided",
                status_code=422,
            )
        return values
