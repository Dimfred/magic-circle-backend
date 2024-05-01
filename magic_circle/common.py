from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine

from .config import config
from .scryfall import ScryfallClient
from .utils.ratelimiter import AsyncRedisRateLimiter

db_engine = create_async_engine(config.DB_URL, **config.DB_ENGINE_CONFIG)


redis = Redis.from_url(config.REDIS_URL)
scryfall_rate_limiter = AsyncRedisRateLimiter(
    redis,
    semaphore_value=10,
    redis_namespace="scryfall-ratelimiter",
    sleep_time=0.1,
)
scryfall = ScryfallClient(scryfall_rate_limiter)
