import io
import random
from abc import ABC, abstractmethod
from typing import Literal

import mtg_parser
import pandas as pd
from requests import Session
from requests.adapters import HTTPAdapter, Retry

from ..exceptions import BadRequestError
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
                    name=row["Name"].lower(),
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


def make_requests_session():
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)

    session = Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers = {
        "User-Agent": random.choice(
            [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.1",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.3",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            ]
        ),
    }

    return session


class PlainParser(Parser):
    def __init__(self, repo: Repository, user: UserDB):
        super().__init__(repo, user)

    def parse_collection(self, collection: str | bytes) -> list[CardDB]:
        raise NotImplementedError

    def parse_decklist(self, decklist: str | bytes) -> list[str]:
        if isinstance(decklist, bytes):
            decklist = decklist.decode("utf-8")

        if not decklist.startswith("http"):  # type: ignore
            decklist = [  # type: ignore
                item.strip() if item[0].isdigit() else f"1 {item.strip()}"  # type: ignore
                for item in decklist.split("\n")  # type: ignore
            ]
            decklist = "\n".join(decklist)  # type: ignore
            decklist = mtg_parser.parse_deck(decklist)  # type: ignore
        else:
            session = make_requests_session()
            decklist = mtg_parser.parse_deck(decklist, session=session)  # type: ignore

        if decklist is None:
            return []

        return [card.name.lower() for card in decklist]  # type: ignore


class ParserFactory:
    @staticmethod
    def create(format_: ParserFormat, repo: Repository, user: UserDB) -> Parser:
        if format_ == "manabox":
            return ManaboxParser(repo, user)

        return PlainParser(repo, user)
