"""
Unit tests for :py:mod:`mlbids.playerids`.
"""

import datetime

import pandas as pd
import requests

from mlbids import playeridmap


class TestSFBBData:
    """
    Unit tests for :py:class:`mlbids.playerids.SFBBData`.
    """
    sfbb_data = playeridmap.SFBBData()

    def test_base_address(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBData.base_address`.
        """
        res = requests.get(
            self.sfbb_data.base_address,
            headers=playeridmap.HEADERS
        )
        res.raise_for_status()
        assert res.status_code == 200

    def test_soup(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBData._soup`.
        """
        soup = playeridmap.get_soup(self.sfbb_data.base_address)
        assert soup

    def test_element(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBData._element`.
        """
        css = "div.entry-content > div > table tr:nth-child(2) > td:first-child"
        assert len(self.sfbb_data._soup.select(css)) == 1

    def test_urls(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBData.urls`.
        :return:
        """
        elems = self.sfbb_data._element.select("a")
        assert len(elems) == 5
        assert all(e.attrs.get("href") for e in elems)

        for url in self.sfbb_data.urls:
            res = requests.get(url, headers=playeridmap.HEADERS)
            assert res.status_code == 200


class TestPlayerIDMap:
    """
    Unit tests for :py:class:`mlbids.playeridmap.PlayerIDMap`.
    """
    playerid_map = playeridmap.PlayerIDMap()

    def test_columns(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap._columns`.
        """
        assert len(playeridmap.PlayerIDMap._columns) == 43

    def test_columns_map(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap._columns_map`.
        """
        assert len(playeridmap.PlayerIDMap._columns_map) == 43
        assert set(
            playeridmap.PlayerIDMap._columns_map.values()
        ) == set(playeridmap.PlayerIDMap._columns)

    def test_read_data(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap.read_data`.
        """
        url = self.playerid_map._sfbb.urls.web_view
        res = requests.get(url, headers=playeridmap.HEADERS)
        soup = playeridmap.get_soup(url)
        assert soup

        assert len(pd.read_html(res.text)) == 1
        df = self.playerid_map.read_data()
        assert set(df.columns) == set(self.playerid_map._columns)

        assert all(
            isinstance(x, datetime.datetime) for x in df.loc[:, "Birthdate"]
        )
        assert all(
            isinstance(x, list) for x in df.loc[:, "AllPositions"]
        )
        assert all(
            isinstance(x, bool) for x in df.loc[:, "Active"]
        )
        for col in self.playerid_map._integer_columns:
            assert all(
                isinstance(x, int) for x in df.loc[:, col]
            )
