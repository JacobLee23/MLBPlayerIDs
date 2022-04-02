"""
Utilities for scraping the `Smart Fantasy Baseball`_ website.

.. _Smart Fantasy Baseball: https://www.smartfantasybaseball.com/
"""

import collections
import typing

import bs4
import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def get_soup(url: str) -> bs4.BeautifulSoup:
    """
    :param url: The URL of the webpage to scrape
    :return: A `BeautifulSoup` object for the passed URL
    """
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="lxml")
    return soup


class SFBBTools:
    """
    Web scraper for the `Tools`_ page of the Smart Fantasy Baseball website.

    .. _Tools: https://www.smartfantasybaseball.com/tools/
    """
    def __init__(self):
        self._base_address = "https://www.smartfantasybaseball.com/tools/"

    class URLs(typing.NamedTuple):
        """
        Contains URLs for view/downloading the player ID map data

        .. py:attribute:: excel_download
            Download player ID map and CHANGELOG as an Excel workbook

        .. py:attribute:: web_view
            View player ID map as a webpage

        .. py:attribute:: csv_download
            Download player ID map as a CSV file

        .. py:attribute:: changelog_web_view
            View player ID map CHANGELOG as a webpage

        .. py:attribute:: changelog_csv_download
            Download player ID map CHANGELOG as a CSV file
        """
        excel_download: str
        web_view: str
        csv_download: str

        changelog_web_view: str
        changelog_csv_download: str

    @property
    def base_address(self) -> str:
        """
        :return: The URL for the `Tools` page of the `Smart Fantasy Baseball` website
        """
        return self._base_address

    @property
    def _soup(self) -> bs4.BeautifulSoup:
        """
        :return: The parsed HTML document of :py:attr:`SFBB.base_address`
        """
        return get_soup(self.base_address)

    @property
    def _element(self) -> bs4.Tag:
        """
        :return: The HTML tag corresponding to the element containing the redirect URLs
        """
        css = "div.entry-content > div > table tr:nth-child(2) > td:first-child"
        element = self._soup.select_one(css)
        return element

    @property
    def urls(self) -> URLs:
        """
        :return: The redirect URLs for viewing/downloading the player ID map
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
