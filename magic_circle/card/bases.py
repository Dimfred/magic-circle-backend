from enum import Enum

from sqlmodel import SQLModel


class Rarity(Enum):
    common = "common"
    uncommon = "uncommon"
    rare = "rare"
    mythic = "mythic"
    special = "special"


class CardBase(SQLModel):
    name: str
    foil: bool
    quantity: int
    language: str
    set_code: str
    set_name: str
    rarity: Rarity
    condition: str
    scryfall_id: str
