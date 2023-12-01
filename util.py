from urllib.parse import urlparse

from config import PLAYER_NAMES
from constants import *
from Match import Location


def is_player_of_interest(player_name):
    return player_name in PLAYER_NAMES


def filter_players(player_list):
    return list(filter(is_player_of_interest, player_list))


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
