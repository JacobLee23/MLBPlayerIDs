"""

"""

import collections
import datetime
import math
import typing

import bs4
import numpy as np
import pandas as pd
import requests


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}


def get_soup(url: str) -> bs4.BeautifulSoup:
    """

    :param url:
    :return:
    """
    res = requests.get(url, headers=HEADERS)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="lxml")
    return soup


class SFBBData:
    """

    """
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
        return get_soup(self.base_address)

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


class PlayerIDMap:
    """

    """
    _columns = (
        "PlayerID", "PlayerName", "Birthdate", "FirstName", "LastName",
        "LastFirstName", "Bats", "Throws", "Team", "League",
        "Position", "AllPositions", "Active",

        "BaseballHQID",
        "BaseballProspectusID",
        "BaseballReferenceID",
        "CBSID", "CBSName",
        "ClayDavenportID",
        "DraftKingsName",
        "ESPNID", "ESPNName",
        "FanduelID", "FanduelName",
        "FanGraphsID", "FanGraphsName",
        "FantasyProsName",
        "FantraxID", "FantraxName",
        "KFFLName",
        "MasterballName",
        "MLBID", "MLBName",
        "NFBCID", "NFBCName", "NFBCLastFirstName",
        "OttoneuID",
        "RazzballName",
        "RetrosheetID",
        "RotowireName", "RotowireID",
        "YahooID", "YahooName"
    )
    _columns_map = {
        "IDPLAYER": "PlayerID", "PLAYERNAME": "PlayerName", "BIRTHDATE": "Birthdate",
        "FIRSTNAME": "FirstName", "LASTNAME": "LastName", "TEAM": "Team",
        "LG": "League", "POS": "Position", "IDFANGRAPHS": "FanGraphsID",
        "FANGRAPHSNAME": "FanGraphsName", "MLBID": "MLBID", "MLBNAME": "MLBName",
        "CBSID": "CBSID", "CBSNAME": "CBSName", "RETROID": "RetrosheetID",
        "BREFID": "BaseballReferenceID", "NFBCID": "NFBCID", "NFBCNAME": "NFBCName",
        "ESPNID": "ESPNID", "ESPNNAME": "ESPNName", "KFFLNAME": "KFFLName",
        "DAVENPORTID": "ClayDavenportID", "BPID": "BaseballProspectusID", "YAHOOID": "YahooID",
        "YAHOONAME": "YahooName", "MSTRBLLNAME": "MasterballName", "BATS": "Bats",
        "THROWS": "Throws", "FANTPROSNAME": "FantasyProsName", "LASTCOMMAFIRST": "LastFirstName",
        "ROTOWIREID": "RotowireID", "FANDUELNAME": "FanduelName", "FANDUELID": "FanduelID",
        "DRAFTKINGSNAME": "DraftKingsName", "OTTONEUID": "OttoneuID", "HQID": "BaseballHQID",
        "RAZZBALLNAME": "RazzballName", "FANTRAXID": "FantraxID", "FANTRAXNAME": "FantraxName",
        "ROTOWIRENAME": "RotowireName", "ALLPOS": "AllPositions", "NFBCLASTFIRST": "NFBCLastFirstName",
        "ACTIVE": "Active"
    }

    _integer_columns = [
        "BaseballHQID", "BaseballProspectusID", "CBSID", "ESPNID", "FanduelID",
        "MLBID", "NFBCID", "OttoneuID", "RotowireID", "YahooID"
    ]

    def __init__(self):
        """

        """
        self._sfbb = SFBBData()

    @staticmethod
    def __reformat_birthdate(birthdate: str) -> datetime.datetime:
        """

        :param birthdate:
        :return:
        """
        try:
            return datetime.datetime.strptime(birthdate, "%m/%d/%Y")
        except ValueError:
            return datetime.datetime.strptime(birthdate, "%m/%d/%y")

    def read_data(self) -> pd.DataFrame:
        """

        :return:
        """
        url = self._sfbb.urls.web_view
        res = requests.get(url, headers=HEADERS)
        soup = get_soup(url)

        title = soup.select_one("div#doc-title > span.name").text

        df = pd.read_html(res.text)[0]
        df.rename(columns=df.iloc[0], inplace=True)
        df.drop(
            index=[df.index[0], df.index[1]], columns=[df.columns[0]],
            inplace=True
        )
        df.dropna(axis=1, how="all", inplace=True)
        df.rename(columns=self._columns_map, inplace=True)
        df = df.reindex(columns=self._columns)

        df.loc[:, "Birthdate"] = df.loc[:, "Birthdate"].apply(
            lambda x: self.__reformat_birthdate(x)
        )
        df.loc[:, "AllPositions"] = df.loc[:, "AllPositions"].apply(
            lambda x: x.split("/")
        )
        df.loc[:, "Active"] = df.loc[:, "Active"].apply(
            lambda x: {"Y": True, "N": False}[x.upper()]
        )
        df.loc[:, self._integer_columns] = df.loc[:, self._integer_columns].applymap(
            lambda x: 0 if math.isnan(float(x)) else int(x)
        )

        return df
