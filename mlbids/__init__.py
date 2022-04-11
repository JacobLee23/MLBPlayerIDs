"""

"""

import datetime
import typing

import pandas as pd

from .playeridmap import PlayerIDMap


def _site_property(columns: list[str]):
    """

    :param columns:
    :return:
    """
    def getter(self):
        general = self.__getattribute__("general")
        data = self.__getattribute__("data")

        if not isinstance(general, pd.DataFrame):
            raise TypeError
        if not isinstance(data, pd.DataFrame):
            raise TypeError

        return general.join(data.loc[:, columns])
    
    return property(getter)


class PIDMap:
    """

    """
    def __init__(self):
        self._pid_map = PlayerIDMap()
        self._data = self.pid_map.read_data()
        self._changelog = self.pid_map.read_changelog_data()

        self.__info = [
            "LastName", "FirstName", "PlayerName", "LastFirstName", "Birthdate", "PlayerID"
        ]
        self.__general = [
            "Bats", "Throws", "Team", "League", "Position", "AllPositions", "Active"
        ]

    @property
    def pid_map(self) -> PlayerIDMap:
        """

        :return:
        """
        return self._pid_map

    @property
    def data(self) -> pd.DataFrame:
        """

        :return:
        """
        return self._data

    @property
    def changelog(self) -> pd.DataFrame:
        """

        :return:
        """
        return self._changelog

    @property
    def info(self) -> pd.DataFrame:
        """

        :return:
        """
        return self.data.loc[:, self.__info]

    @property
    def general(self) -> pd.DataFrame:
        """

        :return:
        """
        return self.info.join(self.data.loc[:, self.__general])

    baseballhq = _site_property(["BaseballHQID"])
    baseball_prospectus = _site_property(["BaseballProspectusID"])
    cbs = _site_property(["CBSID", "CBSName"])
    clay_davenport = _site_property(["ClayDavenportID"])
    draft_kings = _site_property(["DraftKingsName"])
    espn = _site_property(["ESPNID", "ESPNName"])
    fanduel = _site_property(["FanduelID", "FanduelName"])
    fangraphs = _site_property(["FanGraphsID", "FanGraphsName"])
    fantasy_pros = _site_property(["FantasyProsName"])
    fantrax = _site_property(["FantraxName"])
    kffl = _site_property(["KFFLName"])
    masterball = _site_property(["MasterballName"])
    mlb = _site_property(["MLBID", "MLBName"])
    nfbc = _site_property(["NFBCID", "NFBCName", "NFBCLastFirstName"])
    ottoneu = _site_property(["OttoneuID"])
    razzball = _site_property(["RazzballName"])
    retrosheet = _site_property(["RetrosheetID"])
    rotowire = _site_property(["RotowireID", "RotowireName"])
    yahoo = _site_property(["YahooID", "YahooName"])

    @property
    def last_update(self) -> datetime.datetime:
        """

        :return:
        """
        return self.changelog.loc[0, "Date"]
