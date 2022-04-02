"""

"""

import builtins
import datetime
import json
import math
import os
import typing

import pandas as pd
import requests

from ._sfbb import HEADERS
from ._sfbb import SFBBTools


class PlayerIDMap:
    """

    """
    _integer_columns = [
        "BaseballHQID", "BaseballProspectusID", "CBSID", "ESPNID", "FanduelID",
        "MLBID", "NFBCID", "OttoneuID", "RotowireID", "YahooID"
    ]

    def __init__(self):
        self._sfbb = SFBBTools()

    class _DFReformat(typing.NamedTuple):
        """
        Contains information for reformating the ``DataFrame`` column labels

        .. py:attribute:: columns
            Ordering of the new DataFrame column labels

        .. py:attribute:: column_map
            Mapping of the original DataFrame column labels to the new column labels
        """
        columns: builtins.tuple[str]
        column_map: builtins.dict[str, str]

    @classmethod
    def __load_reformat(cls, columns_path: str, columnmap_path: str) -> _DFReformat:
        """
        :param columns_path: Path to JSON file containing the new ``DataFrame`` column labels
        :param columnmap_path: Path to JSON file containing the ``DataFrame`` column label mappings
        :return: JSON data for reformatting the ``DataFrame`` column labels
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
        :return: JSON data for reformatting the player ID map ``DataFrame`` column labels
        """
        reformat = cls.__load_reformat(
            os.path.join("mlbids", "data", "playeridmap_columns.json"),
            os.path.join("mlbids", "data", "playeridmap_columnmap.json")
        )
        return reformat

    @classmethod
    def _changelog_reformat(cls) -> _DFReformat:
        """
        :return: JSON data for reformatting the player ID map CHANGELOG ``DataFrame`` column labels
        """
        reformat = cls.__load_reformat(
            os.path.join("mlbids", "data", "changelog_columns.json"),
            os.path.join("mlbids", "data", "changelog_columnmap.json")
        )
        return reformat

    @property
    def excel_download(self) -> str:
        """
        :return: The URL for downloading the player ID map and CHANGELOG as an Excel workbook
        """
        return self._sfbb.urls.excel_download

    @property
    def web_view(self) -> str:
        """
        :return: The URL for viewing the player ID map
        """
        return self._sfbb.urls.web_view

    @property
    def csv_download(self) -> str:
        """
        :return: The URL for downloading the player ID map as a CSV file
        """
        return self._sfbb.urls.csv_download

    @property
    def changelog_web_view(self) -> str:
        """
        :return: The URL for viewing the player ID map CHANGELOG
        """
        return self._sfbb.urls.changelog_web_view

    @property
    def changelog_csv_download(self) -> str:
        """
        :return: The URL for downloading the player ID map CHANGELOG as a CSV file
        """
        return self._sfbb.urls.changelog_csv_download

    def save_excel(self, path: str) -> str:
        """
        Writes hte player ID map to an Excel workbook.

        :param path: Location to which the Excel workbook should be downloaded
        :return: The aboluste file path to the downlaoded Excel workbook
        """
        res = requests.get(self.excel_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

    def save_csv(self, path: str) -> str:
        """
        Writes the player ID map to a CSV file.

        :param path: Location to which the CSV file should be downloaded
        :return: The absolute file path to the downloaded CSV file
        """
        res = requests.get(self.csv_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

    def save_changelog_csv(self, path: str) -> str:
        """
        Writes the player ID map CHANGELOG to a CSV file.

        :param path: Location to which the CSV file should be downloaded
        :return: The absolute file path to the downloaded CSV file
        """
        res = requests.get(self.changelog_csv_download, headers=HEADERS)

        with open(path, "wb") as file:
            file.write(res.content)

        return os.path.abspath(path)

    @staticmethod
    def __reformat_birthdate(birthdate: str) -> datetime.datetime:
        """
        Converts the *birthdate* string representation to a ``datetime.datetime`` object.
        Used for formatting the **Birthdate** column of the ``DataFrame`` returned by
        :py:meth:`PlayerIDMap.read_data` and :py:meth:`PlayerIDMap.read_csv`.

        :param birthdate: The string representation of the date
        :return: The ``datetime.datetime`` representation of the date
        """
        try:
            return datetime.datetime.strptime(birthdate, "%m/%d/%Y")
        except ValueError:
            return datetime.datetime.strptime(birthdate, "%m/%d/%y")

    @staticmethod
    def __reformat_active(active: str) -> bool:
        """
        Converts the *active* string representation to a Boolean.
        Used for formatting the **Active** column of the ``DataFrame`` returned by
        :py:meth:`PlayerIDMap.read_data` and :py:meth:`PlayerIDMap.read_csv`.

        :param active: The string representation of the active status
        :return: The Boolean representatino of the active status
        :raise ValueError: The active status was not recognized
        """
        active = active.upper()
        if active == "Y":
            return True
        if active == "N":
            return False
        raise ValueError

    def _format_playeridmap_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        :param df: The raw ``DataFrame``
        :return: The reformatted ``DataFrame``
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
        :param df: The raw ``DataFrame``
        :return: The reformatted ``DataFrame``
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
