import asyncio as aio

from .collection.db import CollectionDB
from .deps import DRepo, inject


@inject
async def main(repo=DRepo):
    res = await repo.collection.all(relationships=[CollectionDB.chain])
    print(res)


if __name__ == "__main__":
    aio.run(main())
