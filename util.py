from datetime import datetime, timedelta
from typing import Callable
from urllib.parse import urlparse

from pytz import timezone

from config import PLAYER_NAMES
from constants import *
from Match import Match


class IntervalData:
    def __init__(self, block_start_time, data):
        self.block_start_time: datetime = block_start_time
        self.data = data


def aggregate_matches(
    matches: list[Match],
    # Second argument of aggregate_fn is the output from the previous block; None if it's the first block
    aggregate_fn: Callable[[list[Match], any], any],
    # Default first time is October 3rd, 2022, which is the week before the first tracked customs
    start_date: datetime = datetime(
        year=2022, month=10, day=3, tzinfo=timezone("US/Pacific")
    ),
    interval: timedelta = timedelta(weeks=1),
) -> list[IntervalData]:
    """Aggregate matches into time intervals. `matches` must be sorted from oldest to newest."""
    out = []

    curr_block_start_i = 0
    curr_block_start_date = start_date
    curr_block_end_date = start_date + interval

    i = 0
    while i <= len(matches):
        # Current time block is the time interval [curr_block_start_date, curr_block_end_date)
        # If we reach the end of the list or matches[i] is outside the current time block
        if i == len(matches) or matches[i].time >= curr_block_end_date:
            out.append(
                {
                    "block_start_time": curr_block_start_date,
                    "data": aggregate_fn(matches[curr_block_start_i:i], out),
                }
            )
            curr_block_start_date = curr_block_end_date
            curr_block_end_date = curr_block_start_date + interval
            curr_block_start_i = i
        i += 1

    return out


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
