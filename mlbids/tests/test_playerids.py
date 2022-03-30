"""
Unit tests for :py:mod:`mlbids.playerids`.
"""

import bs4
import requests

from mlbids import playerids


class TestPlayerIDMap:
    """
    Unit tests for :py:class:`mlbids.playerids.PlayerIDMap`.
    """
    playerid_map = playerids.PlayerIDMap()

    def test_base_address(self):
        """
        Unit test for :py:meth:`mlbids.playerids.PlayerIDMap.base_address`.
        """
        res = requests.get(
            self.playerid_map.base_address,
            headers=self.playerid_map.headers
        )
        assert res.status_code == 200

    def test_soup(self):
        """
        Unit test for :py:meth:`mlbids.playerids.PlayerIDMap._soup`.
        """
        res = requests.get(
            self.playerid_map.base_address,
            headers=self.playerid_map.headers
        )
        soup = bs4.BeautifulSoup(res.text, features="lxml")
        assert soup

    def test_element(self):
        """
        Unit test for :py:meth:`mlbids.playerids.PlayerIDMap._element`.
        """
        css = "div.entry-content > div > table tr:nth-child(2) > td:first-child"
        assert len(self.playerid_map._soup.select(css)) == 1

    def test_urls(self):
        """
        Unit test for :py:meth:`mlbids.playerids.PlayerIDMap.urls`.
        :return:
        """
        elems = self.playerid_map._element.select("a")
        assert len(elems) == 5
        assert all(e.attrs.get("href") for e in elems)

        for url in self.playerid_map.urls:
            res = requests.get(url, headers=self.playerid_map.headers)
            assert res.status_code == 200
