"""Start wars importer module."""
import asyncio
import tempfile
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
import petl
from aiohttp import ClientSession
from dateutil import parser
from django.core.files.base import ContentFile, File
from petl import MemorySource, Table, appendcsv, tocsv

from swapi_explorer.api_clients.swapi_client import SWAPIClient
from swapi_explorer.explorer.models import PeopleCollection
from swapi_explorer.explorer.utils import get_random_filename


def convert_iso_timestamp(iso_timestamp: str, format: str):
    """Convert iso timestampt string to different format."""
    parsed_date: datetime = parser.parse(iso_timestamp)
    return datetime.strftime(parsed_date, format)


class StarWarsImporter:
    """Star wars importer"""

    FIELDS_TO_RENAME: Dict = {"created": "date"}
    PEOPLE_FIELDS: List[str] = [
        "name",
        "height",
        "mass",
        "hair_color",
        "skin_color",
        "eye_color",
        "birth_year",
        "gender",
        "homeworld",
        "date",
    ]
    DATE_FORMAT: str = "%Y-%m-%d"

    def _load_people(self) -> List[Dict]:
        """Load people from API"""
        return SWAPIClient().get_all_people_async()

    def _convert_people_into_table(self, people: List[Dict]) -> Table:
        """Convert people API response into PETL table."""
        return petl.fromdicts(people)

    def _process_table(self, table: Table) -> Table:
        """Do ETL on table."""
        table = petl.rename(table, self.FIELDS_TO_RENAME)
        table = petl.cut(table, *self.PEOPLE_FIELDS)
        table = petl.convert(
            table,
            {
                "date": lambda date: convert_iso_timestamp(
                    iso_timestamp=date, format=self.DATE_FORMAT
                ),
                "homeworld": lambda homeworld: homeworld["name"],
            },
        )
        return table

    def _save_table(self, table: Table, source, append: bool = False) -> None:
        """Save table to the source."""
        if append:
            appendcsv(table=table, source=source)
        else:
            tocsv(table=table, source=source)

    async def import_people_page_by_page_async(self, source: Any) -> None:
        """Import people data in page chunks.

        It downloads each page and then does the ETL process on each page
        separately. It utilizes a temporary file to append the following pages.
        For big datasets, it is not efficient to load all the available data
        into memory as it can break application.
        """
        client = SWAPIClient()
        url: str = client.get_people_api_url()
        append: bool = False
        async with ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            while url:
                people, url = await client.get_people_data_page_async(
                    url=url, session=session
                )
                table: Table = self._convert_people_into_table(people=people)
                table = self._process_table(table=table)
                self._save_table(table=table, source=source, append=append)
                append = True

    def import_people(self) -> PeopleCollection:
        """Import people.

        It imports people by downloading all people data first and than does
        the ETL process on the whole dataset.
        It utilizes 'MemorySource' to collect data.
        It can be used only for smaller datasets as it stores data in memory.
        """
        people: List[Dict] = self._load_people()
        table: Table = self._convert_people_into_table(people=people)
        table = self._process_table(table=table)
        source: MemorySource = MemorySource()
        self._save_table(source=source, table=table, append=False)
        collection: PeopleCollection = PeopleCollection.objects.create()
        collection.csv_file.save(
            name=get_random_filename(), content=ContentFile(source.getvalue())
        )
        return collection

    def import_people_page_by_page(self) -> PeopleCollection:
        """Import people data in page chunks.

        It downloads each page and then does the ETL process on each page
        separately. It utilizes a temporary file to append the following pages.
        For big datasets, it is not efficient to load all the available data
        into memory as it can break application.

        It manages asyncio loop.
        """
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        with tempfile.NamedTemporaryFile() as file:
            loop.run_until_complete(
                self.import_people_page_by_page_async(source=file.name)
            )
            loop.close()
            collection: PeopleCollection = PeopleCollection.objects.create()
            collection.csv_file.save(name=get_random_filename(), content=File(file))
            return collection
