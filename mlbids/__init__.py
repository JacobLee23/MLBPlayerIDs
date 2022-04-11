"""

"""

import datetime
import typing

import pandas as pd

from .playeridmap import PlayerIDMap


def _site(columns: list[str]) -> typing.Callable:
    """

    :param columns:
    :return:
    """
    def decorator(method: typing.Callable) -> typing.Callable:
        """

        :param method:
        :return:
        """
        def wrapper(self) -> pd.DataFrame:
            """

            :param self:
            :return:
            """
            if "general" not in self.__dict__ or not isinstance(self.general, pd.DataFrame):
                raise AttributeError("object %r has no attribute 'general'" % self)
            if "data" not in self.__dict__ or not isinstance(self.data, pd.DataFrame):
                raise AttributeError("object %r has no attribute 'data'" % self)
            return self.general.join(self.data.loc[:, columns])
        return wrapper
    return decorator


class PIDMap:
    """

    """
    def __init__(self):
        self._pid_map = PlayerIDMap()
        self._data = self.pid_map.read_data()
        self._changelog = self.pid_map.read_changelog_data()

        self.__info = [
            "Last Name", "First Name", "PlayerName", "LastFirstName", "Birthdate", "PlayerID"
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

    @staticmethod
    def __site_property(columns: list[str], docstring: typing.Optional[str] = None):
        """

        :param columns:
        :param docstring:
        :return:
        """
        def getter(self):
            if "general" not in self.__dict__ or not isinstance(self.general, pd.DataFrame):
                raise AttributeError("object %r has no attribute 'general'" % self)
            if "data" not in self.__dict__ or not isinstance(self.data, pd.DataFrame):
                raise AttributeError("object %r has no attribute 'data'" % self)
            return self.general.join(self.data.loc[:, columns])

        return property(getter, doc=docstring)

    baseballhq = __site_property(["BaseballHQID"])
    baseball_prospectus = __site_property(["BaseballProspectusID"])
    cbs = __site_property(["CBSID", "CBSName"])
    clay_davenport = __site_property(["ClayDavenportID"])
    draft_kings = __site_property(["DraftKingsName"])
    espn = __site_property(["ESPNID", "ESPNName"])
    fanduel = __site_property(["FanduelID", "FanduelName"])
    fangraphs = __site_property(["FanGraphsID", "FanGraphsName"])
    fantasy_pros = __site_property(["FantasyProsName"])
    fantrax = __site_property(["FantraxName"])
    kffl = __site_property(["KFFLName"])
    masterball = __site_property(["MasterballName"])
    mlb = __site_property(["MLBID", "MLBName"])
    nfbc = __site_property(["NFBCID", "NFBCName", "NFBCLastFirstName"])
    ottoneu = __site_property(["OttoneuID"])
    razzball = __site_property(["RazzballName"])
    retrosheet = __site_property(["RetrosheetID"])
    rotowire = __site_property(["RotowireID", "RotowireName"])
    yahoo = __site_property(["YahooID", "YahooName"])

    @property
    def last_update(self) -> datetime.datetime:
        """

        :return:
        """
        return self.changelog.loc[0, "Date"]
