"""API client utils module."""

from typing import Dict, List

from aiocache import Cache, cached
from aiohttp import ClientSession
from api_clients.constants import API_CACHE_TIME


async def load_from_url_async(url: str, session: ClientSession) -> Dict:
    """Load data as JSON from URL.

    :param url: URL to load.
    :param session: AioHttp client session.

    :return Dict - JSON data returned by URL.
    """
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.json()


@cached(
    ttl=API_CACHE_TIME,
    cache=Cache.MEMORY,
    key_builder=lambda f, *args, **kwargs: f"{f.__name__}_{str(args)}_{str(kwargs)}",
)
async def load_from_url_async_cached(
    url: str,
    session: ClientSession,
) -> Dict:
    """Load data as JSON from URL utylizing cache.

    :param url: URL to load.
    :param session: AioHttp client session.

    :return Dict - JSON data returned by URL.
    """
    return await load_from_url_async(url=url, session=session)


async def load_referenced_fields_async(
    data: Dict, referenced_fields: List[str], session
) -> Dict:
    """Load object/dict referenced fields.

    It iterates over `referenced_fields` and tries to update 'data' keys with
    the response from the remote URL currently assigned to its value.

    :param data: Dict object to process.
    :param referenced_fields: List of fields to process.
    :param session: AioHttp client session.

    :return Dict - processed dict 'data'.
    """
    if not referenced_fields:
        return data
    for referenced_field in referenced_fields:
        url = data.get(referenced_field)
        if url:
            data[referenced_field] = await load_from_url_async_cached(
                url=url, session=session
            )
