from config import PlayerName
from constants import *
from Match import Match
from util import filter_players

from .DatasetGenerator import DatasetGenerator

ASSISTED_NAME = "assisted_name"


class AssistsGivenPerStandardGameGenerator(DatasetGenerator):
    def __init__(self):
        super().__init__("assists-given-per-standard-game")
        self.out_json = {
            player_name: {
                assisted_name: {
                    ASSISTED_NAME: assisted_name,
                    ASSISTS_PER_STANDARD_GAME: None,
                    ASSISTS: 0,
                    ROUNDS: 0,
                }
                for assisted_name in PlayerName
            }
            for player_name in PlayerName
        }

    def accumulate(self, match: Match):
        for player_name in filter_players(match.all_players):
            for assistant_name in filter_players(match.all_players):
                if match.players_in_same_team(player_name, assistant_name):
                    if player_name == assistant_name:
                        continue
                    self.out_json[player_name][assistant_name][ROUNDS] += len(
                        match.rounds
                    )
        for _round in match.rounds:
            # This will overwrite the round() function otherwise
            for kill in _round.kills:
                if kill.killer_name == kill.victim_name:
                    continue
                assisted_name = kill.killer_name
                if not isinstance(assisted_name, PlayerName):
                    continue
                for player_name in filter_players(kill.assistants):
                    self.out_json[player_name][assisted_name][ASSISTS] += 1

    def finalize(self, minified=False):
        for player_name in PlayerName:
            for assistant_name in PlayerName:
                if self.out_json[player_name][assistant_name][ROUNDS] != 0:
                    self.out_json[player_name][assistant_name][
                        ASSISTS_PER_STANDARD_GAME
                    ] = (
                        round(
                            10
                            * 25
                            * self.out_json[player_name][assistant_name][ASSISTS]
                            / self.out_json[player_name][assistant_name][ROUNDS]
                        )
                        / 10
                    )

        for player_name in self.out_json:
            self.out_json[player_name] = {
                k: v
                for k, v in sorted(
                    self.out_json[player_name].items(),
                    key=lambda x: x[1][ASSISTED_NAME],
                )
            }

        return self.out_json
