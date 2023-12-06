from config import PlayerName
from constants import *
from Match import Match
from util import filter_players

from .DatasetGenerator import DatasetGenerator


class IndividualGenerator(DatasetGenerator):
    def __init__(self):
        super().__init__("individual")
        self.out_json = {
            player_name: {
                WINRATE: None,
                WINS: 0,
                GAMES: 0,
                MAPS: {
                    map_name: {ACS: None, SCORE: 0, ROUNDS: 0} for map_name in MapName
                },
                AGENTS: {
                    agent: {
                        ROLE: agent.role_name,
                        WINRATE: None,
                        WINS: 0,
                        GAMES: 0,
                    }
                    for agent in Agent
                },
                ROLES: {
                    role_name: {WINRATE: None, WINS: 0, GAMES: 0}
                    for role_name in RoleName
                },
                TOP_AGENTS: [],
                TOP_ROLES: [],
            }
            for player_name in PlayerName
        }

    def accumulate(self, match: Match):
        for player_name in filter_players(match.all_players):
            player_stats = match.all_players[player_name]
            player_entry = self.out_json[player_name]

            # Update winrate
            if match.player_did_win(player_name):
                player_entry[WINS] += 1
                player_entry[AGENTS][player_stats.agent][WINS] += 1
                player_entry[ROLES][player_stats.agent.role_name][WINS] += 1
            if match.player_did_play(player_name):
                player_entry[GAMES] += 1
                player_entry[MAPS][match.map][
                    SCORE
                ] += player_stats.average_combat_score * len(match.rounds)
                player_entry[MAPS][match.map][ROUNDS] += len(match.rounds)
                player_entry[AGENTS][player_stats.agent][GAMES] += 1
                player_entry[ROLES][player_stats.agent.role_name][GAMES] += 1

    def finalize(self, minified=False):
        for player_name in PlayerName:
            player_entry = self.out_json[player_name]

            if player_entry[GAMES] != 0:
                player_entry[WINRATE] = round(
                    100 * player_entry[WINS] / player_entry[GAMES]
                )

            for map_name in MapName:
                if player_entry[MAPS][map_name][ROUNDS] != 0:
                    player_entry[MAPS][map_name][ACS] = round(
                        player_entry[MAPS][map_name][SCORE]
                        / player_entry[MAPS][map_name][ROUNDS]
                    )

            for agent in Agent:
                if player_entry[AGENTS][agent][GAMES] != 0:
                    player_entry[AGENTS][agent][WINRATE] = round(
                        100
                        * player_entry[AGENTS][agent][WINS]
                        / player_entry[AGENTS][agent][GAMES]
                    )

            for role_name in RoleName:
                if player_entry[ROLES][role_name][GAMES] != 0:
                    player_entry[ROLES][role_name][WINRATE] = round(
                        100
                        * player_entry[ROLES][role_name][WINS]
                        / player_entry[ROLES][role_name][GAMES]
                    )

        for player_name in PlayerName:
            player_entry = self.out_json[player_name]

            for role_name in RoleName:
                if player_entry[GAMES] != 0:
                    if (
                        player_entry[ROLES][role_name][GAMES] / player_entry[GAMES]
                        > 0.3
                    ):
                        self.out_json[player_name][TOP_ROLES].append(role_name)

            # Convert key from Enum.Agent to a true string
            for agent in Agent:
                self.out_json[player_name][AGENTS][agent.name] = self.out_json[
                    player_name
                ][AGENTS].pop(agent)

            agents_sorted_by_plays = sorted(
                self.out_json[player_name][AGENTS],
                key=lambda agent_name: (
                    -self.out_json[player_name][AGENTS][agent_name][GAMES],
                    agent_name,
                ),
            )
            self.out_json[player_name][TOP_AGENTS] = [
                agent_name for agent_name in agents_sorted_by_plays[:3]
            ]

            if minified:
                del self.out_json[player_name][WINS]
                for map_name in MapName:
                    del self.out_json[player_name][MAPS][map_name][SCORE]
                    del self.out_json[player_name][MAPS][map_name][ROUNDS]
                for agent_name in Agent:
                    del self.out_json[player_name][AGENTS][agent_name.name][WINRATE]
                    del self.out_json[player_name][AGENTS][agent_name.name][WINS]

        return self.out_json
