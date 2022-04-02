"""
Unit tests for :py:mod:`mlbids._sfbb`.
"""


import requests

from mlbids import _sfbb


class TestSFBBData:
    """
    Unit tests for :py:class:`mlbids.playerids.SFBBTools`.
    """
    sfbb_data = _sfbb.SFBBTools()

    def test_base_address(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools.base_address`.
        """
        res = requests.get(
            self.sfbb_data.base_address,
            headers=_sfbb.HEADERS
        )
        res.raise_for_status()
        assert res.status_code == 200

    def test_soup(self):
        """
        Unit test for :py:meth:`mlbids.playerids.SFBBTools._soup`.
        """
        soup = _sfbb.get_soup(self.sfbb_data.base_address)
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
        """
        elems = self.sfbb_data._element.select("a")
        assert len(elems) == 5
        assert all(e.attrs.get("href") for e in elems)

        for url in self.sfbb_data.urls:
            res = requests.get(url, headers=_sfbb.HEADERS)
            assert res.status_code == 200
