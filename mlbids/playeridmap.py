"""

"""

import collections
import datetime
import json
import math
import os
import typing

import bs4
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
    _integer_columns = [
        "BaseballHQID", "BaseballProspectusID", "CBSID", "ESPNID", "FanduelID",
        "MLBID", "NFBCID", "OttoneuID", "RotowireID", "YahooID"
    ]

    def __init__(self):
        """

        """
        self._sfbb = SFBBData()

    class _DFReformat(typing.NamedTuple):
        """

        """
        columns: tuple[str]
        column_map: dict[str, str]

    @classmethod
    def __load_reformat(cls, columns_path: str, columnmap_path: str) -> _DFReformat:
        """

        :param columns_path:
        :param columnmap_path:
        :return:
        """
        with open(columns_path, "r", encoding="utf-8") as file:
            columns = json.load(file)
        with open(columnmap_path, "r", encoding="utf-8") as file:
            column_map = json.load(file)

        reformat = cls._DFReformat(columns=columns, column_map=column_map)
        return reformat

    @classmethod
    def _playeridmap_reformat(cls) -> _DFReformat:
        """

        :return:
        """
        reformat = cls.__load_reformat(
            os.path.join("mlbids", "data", "playeridmap_columns.json"),
            os.path.join("mlbids", "data", "playeridmap_columnmap.json")
        )
        return reformat

    @classmethod
    def _changelog_reformat(cls) -> _DFReformat:
        """

        :return:
        """
        reformat = cls.__load_reformat(
            os.path.join("mlbids", "data", "changelog_columns.json"),
            os.path.join("mlbids", "data", "changelog_columnmap.json")
        )
        return reformat

    @property
    def excel_download(self) -> str:
        """

        :return:
        """
        return self._sfbb.urls.excel_download

    @property
    def web_view(self) -> str:
        """

        :return:
        """
        return self._sfbb.urls.web_view

    @property
    def csv_download(self) -> str:
        """

        :return:
        """
        return self._sfbb.urls.csv_download

    @property
    def changelog_web_view(self) -> str:
        """

        :return:
        """
        return self._sfbb.urls.changelog_web_view

    @property
    def changelog_csv_download(self) -> str:
        """

        :return:
        """
        return self._sfbb.urls.changelog_csv_download

    def save_csv(self, path: str) -> str:
        """

        :param path:
        :return:
        """
        res = requests.get(self.csv_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

    def save_excel(self, path: str) -> str:
        """

        :param path:
        :return:
        """
        res = requests.get(self.excel_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

    def save_changelog_csv(self, path: str) -> str:
        """

        :param path:
        :return:
        """
        res = requests.get(self.changelog_csv_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

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

    @staticmethod
    def __reformat_active(active: str) -> bool:
        """

        :param active:
        :return:
        :raise ValueError:
        """
        active = active.upper()
        if active == "Y":
            return True
        if active == "N":
            return False
        raise ValueError

    def _format_playeridmap_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        :param df:
        :return:
        """
        reformat = self._playeridmap_reformat()

        df.rename(
            index=lambda i: i - df.index[0], columns=reformat.column_map,
            inplace=True
        )
        df = df.reindex(columns=reformat.columns)

        df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        df.loc[:, "Birthdate"] = df.loc[:, "Birthdate"].apply(
            self.__reformat_birthdate
        )
        df.loc[:, "AllPositions"] = df.loc[:, "AllPositions"].apply(
            lambda x: x.split("/")
        )
        df.loc[:, "Active"] = df.loc[:, "Active"].apply(
            self.__reformat_active
        )
        df.loc[:, self._integer_columns] = df.loc[:, self._integer_columns].applymap(
            lambda x: 0 if math.isnan(float(x)) else int(x)
        )

        return df

    def read_data(self) -> pd.DataFrame:
        """

        :return:
        """
        res = requests.get(self.web_view, headers=HEADERS)
        df = pd.read_html(res.text)[0]

        df.rename(columns=df.iloc[0], inplace=True)
        df.drop(
            index=[df.index[0], df.index[1]], columns=[df.columns[0]],
            inplace=True
        )
        df.dropna(axis=1, how="all", inplace=True)

        df = self._format_playeridmap_df(df)

        return df

    def read_csv(self) -> pd.DataFrame:
        """

        :return:
        """
        res = requests.get(self.csv_download, headers=HEADERS)
        temp_path = f"temp-PlayerIDMap-{datetime.datetime.now().microsecond}.csv"
        with open(temp_path, "wb") as file:
            file.write(res.content)

        try:
            df = pd.read_csv(temp_path)
        finally:
            os.remove(os.path.abspath(temp_path))

        df = self._format_playeridmap_df(df)

        return df

    def _format_changelog_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        :param df:
        :return:
        """
        reformat = self._changelog_reformat()

        df.rename(
            index=lambda i: i - df.index[0], columns=reformat.column_map,
            inplace=True
        )
        df = df.reindex(columns=reformat.columns)
        df.loc[:, "Date"] = df.loc[:, "Date"].apply(
            lambda x: datetime.datetime.strptime(x, "%m/%d/%Y")
        )

        return df

    def read_changelog_data(self) -> pd.DataFrame:
        """

        :return:
        """
        res = requests.get(self.changelog_web_view, headers=HEADERS)
        df = pd.read_html(res.text)[0]

        df.rename(columns=df.iloc[0], inplace=True)
        df.drop(index=df.index[0], inplace=True)

        df = self._format_changelog_df(df)

        return df

    def read_changelog_csv(self) -> pd.DataFrame:
        """

        :return:
        """
        res = requests.get(self.changelog_csv_download, headers=HEADERS)
        temp_path = f"temp-Changelog-{datetime.datetime.now().microsecond}.csv"
        with open(temp_path, "wb") as file:
            file.write(res.content)

        try:
            df = pd.read_csv(temp_path)
        finally:
            os.remove(os.path.abspath(temp_path))

        df = self._format_changelog_df(df)

        return df
