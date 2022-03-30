"""

"""

import collections
import typing

import bs4
import requests


class PlayerIDMap:
    """

    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    def __init__(self):
        """

        """
        self._base_address = "https://www.smartfantasybaseball.com/tools/"

    class URLs(typing.NamedTuple):
        excel_download: str
        web_view: str
        csv_download: str

        changelog_web_view: str
        changelog_csv_download: str

    @property
    def base_address(self) -> str:
        """

        :return:
        """
        return self._base_address

    @property
    def _soup(self) -> bs4.BeautifulSoup:
        """

        :return:
        """
        res = requests.get(self.base_address, headers=self.headers)
        soup = bs4.BeautifulSoup(res.text, features="lxml")
        return soup

    @property
    def _element(self) -> bs4.Tag:
        """

        :return:
        """
        css = "div.entry-content > div > table tr:nth-child(2) > td:first-child"
        element = self._soup.select_one(css)
        return element

    @property
    def urls(self) -> URLs:
        """

        :return:
        """
        data = collections.defaultdict()
        hrefs = [e.attrs.get("href") for e in self._element.select("a")]

        (
            data["excel_download"],
            data["web_view"],
            data["csv_download"],
            data["changelog_web_view"],
            data["changelog_csv_download"]
        ) = hrefs

        return self.URLs(**data)
