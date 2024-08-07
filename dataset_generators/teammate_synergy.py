from config import PlayerName
from constants import *
from Match import Match
from util import filter_players

from .DatasetGenerator import DatasetGenerator

TEAMMATE_NAME = "teammate_name"


class TeammateSynergyGenerator(DatasetGenerator):
    def __init__(self):
        super().__init__("teammate-synergy")
        self.out_json = {
            player_name: {
                teammate_name: {
                    TEAMMATE_NAME: teammate_name,
                    WINRATE: None,
                    WINS: 0,
                    GAMES: 0,
                }
                for teammate_name in PlayerName
            }
            for player_name in PlayerName
        }

    def accumulate(self, match: Match):
        for player_name in filter_players(match.winning_players):
            for teammate_name in filter_players(match.winning_players):
                if player_name == teammate_name:
                    continue
                self.out_json[player_name][teammate_name][WINS] += 1
                self.out_json[player_name][teammate_name][GAMES] += 1
        for player_name in filter_players(match.losing_players):
            for teammate_name in filter_players(match.losing_players):
                if player_name == teammate_name:
                    continue
                self.out_json[player_name][teammate_name][GAMES] += 1

    def finalize(self, minified=False):
        for player_name in self.out_json:
            for teammate_name in self.out_json[player_name]:
                if self.out_json[player_name][teammate_name][GAMES] != 0:
                    self.out_json[player_name][teammate_name][WINRATE] = round(
                        100
                        * self.out_json[player_name][teammate_name][WINS]
                        / self.out_json[player_name][teammate_name][GAMES]
                    )

        for player_name in self.out_json:
            if minified:
                for teammate_name in PlayerName:
                    del self.out_json[player_name][teammate_name][WINS]
                    del self.out_json[player_name][teammate_name][GAMES]

            self.out_json[player_name] = sorted(
                self.out_json[player_name].values(),
                key=lambda x: x[TEAMMATE_NAME],
            )

        return self.out_json
