from urllib.parse import urlparse

from config import PlayerName
from constants import *
from Match import Location


def filter_players(player_list) -> list[PlayerName]:
    return [
        PlayerName(player_name)
        for player_name in player_list
        if player_name in PlayerName
    ]


def is_valid_tracker_url(tracker_url: str) -> bool:
    url = urlparse(tracker_url)
    if url.hostname != "tracker.gg":
        return False

    url_split_path = url.path.split("/")
    return (
        len(url_split_path) == 4
        and url_split_path[1] == "valorant"
        and url_split_path[2] == "match"
    )


def transform_coordinates(location: Location, map_name, scale):
    parameters = COORDINATE_TRANSFORMATIONS[map_name]
    return (
        scale * (location.y * parameters[X_COEFFICIENT] + parameters[X_SHIFT]),
        scale * (location.x * parameters[Y_COEFFICIENT] + parameters[Y_SHIFT]),
    )
