from constants import *
from Match import Match
from util import filter_players

from .DatasetGenerator import DatasetGenerator


class RolesGenerator(DatasetGenerator):
    def __init__(self):
        super().__init__("roles")
        self.out_json = {role_name: 0 for role_name in RoleName}

    def accumulate(self, match: Match):
        for player_name in filter_players(match.all_players):
            player_stats = match.all_players[player_name]
            self.out_json[player_stats.agent.role_name] += 1

    def finalize(self, minified=False):
        return self.out_json
