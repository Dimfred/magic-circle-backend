import io
from abc import ABC, abstractmethod
from typing import Literal

import mtg_parser
import pandas as pd

from ..repo import Repository
from ..user.db import UserDB
from .bases import Rarity
from .db import CardDB

ParserFormat = Literal["manabox", "plain"]


class Parser(ABC):
    def __init__(self, repo: Repository, user: UserDB):
        self.repo = repo
        self.user = user

    @abstractmethod
    def parse_collection(self, collection: str | bytes) -> list[CardDB]:
        pass

    @abstractmethod
    def parse_decklist(self, decklist: str | bytes) -> list[str]:
        pass


class ManaboxParser(Parser):
    def __init__(self, repo: Repository, user: UserDB):
        super().__init__(repo, user)

    def parse_collection(self, collection: str | bytes) -> list[CardDB]:
        if isinstance(collection, bytes):
            collection = collection.decode("utf-8")

        cards = []

        df = pd.read_csv(io.StringIO(collection))
        for _, row in df.iterrows():
            card = self.repo.card.create(
                orm=CardDB(
                    name=row["Name"],
                    foil=row["Foil"] == "foil",
                    quantity=row["Quantity"],
                    language=row["Language"],
                    set_code=row["Set code"],
                    set_name=row["Set name"],
                    rarity=Rarity(row["Rarity"]),
                    condition=row["Condition"],
                    scryfall_id=row["Scryfall ID"],
                    owner_id=self.user.id,
                )
            )
            cards.append(card)

        return cards

    def parse_decklist(self, decklist: str | bytes) -> list[str]:
        raise NotImplementedError


class PlainParser(Parser):
    def __init__(self, repo: Repository, user: UserDB):
        super().__init__(repo, user)

    def parse_collection(self, collection: str | bytes) -> list[CardDB]:
        raise NotImplementedError

    def parse_decklist(self, decklist: str | bytes) -> list[str]:
        if isinstance(decklist, bytes):
            decklist = decklist.decode("utf-8")

        return [card.name for card in mtg_parser.decklist.parse_deck(decklist)]


class ParserFactory:
    @staticmethod
    def create(format_: ParserFormat, repo: Repository, user: UserDB) -> Parser:
        if format_ == "manabox":
            return ManaboxParser(repo, user)

        return PlainParser(repo, user)
