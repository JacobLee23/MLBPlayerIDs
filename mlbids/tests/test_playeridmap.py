"""
Unit tests for :py:mod:`mlbids.playerids`.
"""

import datetime
import os

import pandas as pd
import pytest
import requests

from mlbids import playeridmap


class TestSFBBData:
    """
    Unit tests for :py:class:`mlbids.playerids.SFBBTools`.
    """
    sfbb_data = playeridmap.SFBBTools()

    def test_base_address(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools.base_address`.
        """
        res = requests.get(
            self.sfbb_data.base_address,
            headers=playeridmap.HEADERS
        )
        res.raise_for_status()
        assert res.status_code == 200

    def test_soup(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools._soup`.
        """
        soup = playeridmap.get_soup(self.sfbb_data.base_address)
        assert soup

    def test_element(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools._element`.
        """
        css = "div.entry-content > div > table tr:nth-child(2) > td:first-child"
        assert len(self.sfbb_data._soup.select(css)) == 1

    def test_urls(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools.urls`.
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

    def test_playeridmap_reformat(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap._playeridmap_reformat`.
        """
        paths = [
            os.path.join("mlbids", "data", "playeridmap_columns.json"),
            os.path.join("mlbids", "data", "playeridmap_columnmap.json")
        ]
        assert all(os.path.exists(p) for p in paths)

        reformat = self.playerid_map._playeridmap_reformat()
        assert len(reformat.columns) == len(reformat.column_map) == 43
        assert all(isinstance(x, str) for x in reformat.columns)
        assert all(
            isinstance(a, str) and isinstance(b, str)
            for a, b in reformat.column_map.items()
        )
        assert all(x.isupper() for x in reformat.column_map.keys())

    def test_changelog_reformat(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap._changelog_reformat`.
        """
        paths = [
            os.path.join("mlbids", "data", "changelog_columns.json"),
            os.path.join("mlbids", "data", "changelog_columnmap.json")
        ]
        assert all(os.path.exists(p) for p in paths)

        reformat = self.playerid_map._changelog_reformat()
        assert len(reformat.columns) == len(reformat.column_map) == 2
        assert all(isinstance(x, str) for x in reformat.columns)
        assert all(
            isinstance(a, str) and isinstance(b, str)
            for a, b in reformat.column_map.items()
        )
        assert all(x.isupper() for x in reformat.column_map.keys())

    @pytest.mark.parametrize(
        "url", [
            playerid_map.excel_download,
            playerid_map.web_view,
            playerid_map.csv_download,
            playerid_map.changelog_web_view,
            playerid_map.changelog_csv_download
        ]
    )
    def test_sfbb_urls(self, url: str):
        """
        Unit tests for:
        - :py:attr:`mlbids.playeridmap.PlayerIDMap.excel_download`.
        - :py:attr:`mlbids.playeridmap.PlayerIDMap.web_view`.
        - :py:attr:`mlbids.playeridmap.PlayerIDMap.csv_download`.
        - :py:attr:`mlbids.playeridmap.PlayerIDMap.changelog_web_view`.
        - :py:attr:`mlbids.playeridmap.PlayerIDMap.changelog_csv_download`.

        :param url:
        """
        res = requests.get(url, headers=playeridmap.HEADERS)
        assert res.status_code == 200, url

    @pytest.mark.parametrize(
        "df", [playerid_map.read_data()]
    )
    def test_format_playeridmap_df(self, df: pd.DataFrame):
        """
        Unit test for ;py:meth:`mlbids.playeridmap.PlayerIDMap._format_playeridmap_df`.
        """
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

    def test_read_data(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap.read_data`.
        """
        url = self.playerid_map._sfbb.urls.web_view
        res = requests.get(url, headers=playeridmap.HEADERS)
        assert len(pd.read_html(res.text)) == 1

        df = self.playerid_map.read_data()
        assert set(df.columns) == set(self.playerid_map._playeridmap_reformat().columns)

    def test_read_csv(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap.read_csv`.
        """
        df = self.playerid_map.read_csv()
        assert all(df == self.playerid_map.read_data())

    @pytest.mark.parametrize(
        "df", [playerid_map.read_changelog_data()]
    )
    def test_format_changelog_df(self, df: pd.DataFrame):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap._format_changelog_df`.
        """
        assert all(
            isinstance(x, datetime.datetime) for x in df.loc[:, "Date"]
        )

    def test_read_changelog_data(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap.read_changelog_data`.
        """
        url = self.playerid_map.changelog_web_view
        res = requests.get(url, headers=playeridmap.HEADERS)
        assert len(pd.read_html(res.text)) == 1

        df = self.playerid_map.read_changelog_data()
        assert set(df.columns) == set(self.playerid_map._changelog_reformat().columns)

    def test_read_changelog_csv(self):
        """
        Unit test for :py:meth:`mlbids.playeridmap.PlayerIDMap.read_changelog_csv`.
        """
        df = self.playerid_map.read_changelog_csv()
        assert all(df == self.playerid_map.read_changelog_data())
