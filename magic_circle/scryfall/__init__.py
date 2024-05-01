from io import BytesIO

from depends import Depends, inject
from httpx import AsyncClient
from PIL import Image
from tenacity import retry, stop_after_attempt, wait_random


async def get_client():
    async with AsyncClient(base_url="https://api.scryfall.com", timeout=5) as client:
        yield client


Client = Depends(get_client)


class ScryfallClient:
    def __init__(self, ratelimiter):
        self.ratelimiter = ratelimiter

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(5))
    @inject
    async def card_by_id(self, id_: str, client: AsyncClient = Client):  # type: ignore
        coro = client.get(f"/cards/{id_}")
        return await self.ratelimiter.limit(coro)

    @retry(wait=wait_random(min=1, max=2), stop=stop_after_attempt(5))
    @inject
    async def get_image(self, url: str, client: AsyncClient = Client):  # type: ignore
        coro = client.get(url)
        res = await self.ratelimiter.limit(coro)
        return Image.open(BytesIO(res.content))
