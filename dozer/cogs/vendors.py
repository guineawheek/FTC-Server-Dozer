import discord
import aiohttp
import async_timeout
from bs4 import BeautifulSoup


class VendorSearcher:
    base_url = ""

    def __init__(self, http_session=None):
        if not http_session:
            http_session = aiohttp.ClientSession()
        self.http = http_session

    async def get_soup(self, url):
        async with async_timeout.timeout(5) as _, self.http.get(url) as response:
            return BeautifulSoup(response.text(), 'html.parser')

    async def search(self, query: str) -> dict:
        pass


def setup(bot):
    pass
