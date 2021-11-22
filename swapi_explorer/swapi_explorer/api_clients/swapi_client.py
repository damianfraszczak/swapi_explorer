"""Star Wars API client module."""
import asyncio
from typing import Dict, List, Optional, Tuple

import aiohttp
from aiohttp import ClientSession

from swapi_explorer.api_clients.utils import (
    load_from_url_async_cached,
    load_referenced_fields_async,
)


class SWAPIClient:
    """Star Wars API client."""

    BASE_URL: str = "https://swapi.dev"
    REFERENCED_FIELDS_TO_LOAD: List[str] = ["homeworld"]

    async def _process_people_data_async(
        self, people_data: List[Dict], session: ClientSession
    ) -> None:
        """Process people data to include additional data.

        It iterates over 'people_data' and tries to update keys with the
        response from the remote URL currently assigned to its value.

        :param people_data: People list returned from API.
        :param session: AioHttp session object.
        """
        load_referenced_fields_coros = [
            load_referenced_fields_async(
                data=person,
                referenced_fields=self.REFERENCED_FIELDS_TO_LOAD,
                session=session,
            )
            for person in people_data
        ]
        await asyncio.gather(*load_referenced_fields_coros)

    async def get_people_data_page_async(
        self, url: str, session: ClientSession
    ) -> Tuple[List[Dict], Optional[str]]:
        """Load people data from API and augment it with referenced fields.

        :param url: str representing API url to laod.
        :param session: AioHttp session object.

        :return Tuple containing parsed response for provided 'url' and string
        representing url for next page.

        """
        people_response: Dict = await load_from_url_async_cached(
            url=url, session=session
        )
        people_data: Optional[List[Dict]] = people_response.get("results")
        await self._process_people_data_async(people_data=people_data, session=session)
        return people_data, people_response.get("next")

    async def _get_all_people_data_async(self) -> List:
        url: str = self.get_people_api_url()
        result: List[Dict] = []
        async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            while url:
                people, url = await self.get_people_data_page_async(
                    url=url, session=session
                )
                result.extend(people)
        return result

    def get_people_api_url(self):
        return f"{self.BASE_URL}/api/people/"

    def get_all_people_async(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        people: Dict = loop.run_until_complete(self._get_all_people_data_async())
        loop.close()
        return people
