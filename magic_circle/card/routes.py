from pathlib import Path

import webp
from fastapi import APIRouter, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, Response
from loguru import logger
from sqlmodel import and_, not_, or_

from ..common import scryfall
from ..config import config
from ..deps import Repo
from ..exceptions import BadRequestError, NotFoundError
from ..user.db import UserDB
from ..user.deps import User
from .db import CardDB
from .parser import ParserFactory, ParserFormat
from .requests import CardsGetIn
from .responses import CardOut

router = APIRouter(prefix="/cards")


@router.patch("")
async def upload_cards(file: UploadFile, format_: ParserFormat, repo=Repo, user=User):
    parser = ParserFactory.create(format_, repo, user)

    content = await file.read()
    if content is None:
        raise BadRequestError("Empty file")

    await repo.card.delete_all(user.id)
    await run_in_threadpool(parser.parse_collection, content)
    await repo.commit()


@router.delete("")
async def delete_cards(repo=Repo, user=User):
    await repo.card.delete_all(user.id)
    await repo.commit()


@router.post("", response_model=list[CardOut])
async def get_cards(req: CardsGetIn, repo=Repo, user=User):
    and_clause = []
    query_kwargs = {
        "offset": req.offset,
        "limit": req.max_page,
        "order_by": [CardDB.name],
        "relationships": [CardDB.owner],
    }

    cards = []
    if req.decklist and req.decklist_format is not None:
        parser = ParserFactory.create(req.decklist_format, repo, user)
        cards = parser.parse_decklist(req.decklist)
        if req.exact_match:
            if req.ignore_owned_cards:
                and_clause.append(
                    repo.card.all_cards_owned_by_someone_else(
                        cards, user.id, exact_name=True
                    )
                )
            else:
                and_clause.append(or_(*(CardDB.name == card for card in cards)))

        elif req.ignore_owned_cards:
            and_clause.append(  # type: ignore
                repo.card.all_cards_owned_by_someone_else(
                    cards, user.id, exact_name=False
                )
            )
        else:
            and_clause.append(
                or_(*(CardDB.name.ilike(f"%{card}%") for card in cards))  # type: ignore
            )

    userdbs = []
    if req.usernames is not None:
        userdbs = await repo.user.all(
            where=or_(*(UserDB.username == user for user in req.usernames))
        )
        and_clause.append(or_(*(CardDB.owner_id == userdb.id for userdb in userdbs)))

    if len(and_clause) > 1:
        query_kwargs["where"] = and_(*and_clause)
    elif len(and_clause) == 1:
        query_kwargs["where"] = and_clause[0]

    return await repo.card.all(**query_kwargs)


@router.get("/{scryfall_id}")
async def get_image(scryfall_id: str):
    save_path = Path(config.APP_CACHE_PATH + f"/{scryfall_id}.webp")

    if not save_path.exists():
        res = await scryfall.card_by_id(scryfall_id)
        if res.status_code != 200:  # noqa: PLR2004
            return Response(res.text, res.status_code)

        j = res.json()
        if "image_uris" not in j:
            if "card_faces" not in j:
                logger.error("!!! MISSING IMAGE URI AND CARD FACES !!!")
                logger.error(j)
                return Response("Missing image", 404)

            img_url = j["card_faces"][0]["image_uris"]["normal"]
        else:
            img_url = j["image_uris"]["normal"]

        image = await scryfall.get_image(img_url)
        image = webp.WebPPicture.from_pil(image)
        image.save(save_path)

    return FileResponse(save_path)
