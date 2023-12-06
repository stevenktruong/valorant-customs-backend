from datetime import datetime
from typing import Optional

from pytz import timezone

from constants import *


class Player:
    def __init__(self, player_json):
        self.player_name: str = player_json["player_name"]
        self.agent: Agent = Agent(player_json["agent"])
        self.average_combat_score: int = player_json["average_combat_score"]
        self.kills: int = player_json["kills"]
        self.deaths: int = player_json["deaths"]
        self.assists: int = player_json["assists"]
        self.kill_deaths: float = player_json["kill_deaths"]
        # self.kill_assist_survive_traded: int = player_json["kill_assist_survive_traded"]
        self.plants: int = player_json["plants"]
        self.defuses: int = player_json["defuses"]
        self.first_kills: int = player_json["first_kills"]
        self.first_deaths: int = player_json["first_deaths"]
        self.multi_kills: int = player_json["multi_kills"]
        # self.econ: int = player_json["econ"]

    def __hash__(self):
        return self.player_name.__hash__()


class PlayerRoundStats:
    def __init__(self, player_round_stats_json):
        self.team: Team = player_round_stats_json["team"]
        self.side: Side = player_round_stats_json["side"]
        self.score: int = player_round_stats_json["score"]
        self.kills: int = player_round_stats_json["kills"]
        self.deaths: int = player_round_stats_json["deaths"]
        self.assists: int = player_round_stats_json["assists"]
        self.damage: int = player_round_stats_json["damage"]
        self.loadout_value: int = player_round_stats_json["loadout_value"]
        self.remaining_credits: int = player_round_stats_json["remaining_credits"]
        self.spent_credits: int = player_round_stats_json["spent_credits"]


# TODO: Need more consistent naming. Maybe just "Damage" or add "Event" to the other classes
class DamageEvent:
    def __init__(self, damage_event_json):
        self.giver_name: str = damage_event_json["giver_name"]
        self.receiver_name: str = damage_event_json["receiver_name"]
        self.damage: int = damage_event_json["damage"]
        self.legshots: int = damage_event_json["legshots"]
        self.bodyshots: int = damage_event_json["bodyshots"]
        self.headshots: int = damage_event_json["headshots"]


class Location:
    def __init__(self, location_json):
        self.x: int = location_json["x"]
        self.y: int = location_json["y"]


class LocationWithAngle(Location):
    def __init__(self, location_with_angle_json):
        super().__init__(location_with_angle_json["location"])
        self.angle: float = location_with_angle_json["angle"]


class Kill:
    def __init__(self, kill_json):
        self.killer_name: str = kill_json["killer_name"]
        self.victim_name: str = kill_json["victim_name"]
        self.killer_location: Optional[LocationWithAngle] = (
            LocationWithAngle(kill_json["killer_location"])
            if kill_json["killer_location"]
            else None
        )
        self.victim_location: Location = Location(kill_json["victim_location"])
        self.player_locations: dict[PlayerName, LocationWithAngle] = {
            player_locations_json["player_name"]: LocationWithAngle(
                player_locations_json
            )
            for player_locations_json in kill_json["player_locations"]
        }
        self.assistants: list[str] = kill_json["assistants"]
        self.weapon_name: str = kill_json["weapon_name"]
        self.game_time: int = kill_json["game_time"]
        self.round_time: int = kill_json["round_time"]
        # self.damage: int = kill_json["damage"]


class Plant:
    def __init__(self, plant_json):
        self.planter_name: str = plant_json["planter_name"]
        self.location: Location = Location(plant_json["location"])
        self.site: str = plant_json["site"]
        self.round_time: int = plant_json["round_time"]
        self.player_locations: dict[str, LocationWithAngle] = {
            player_locations_json["player_name"]: LocationWithAngle(
                player_locations_json
            )
            for player_locations_json in plant_json["player_locations"]
        }


class Defuse:
    def __init__(self, defuse_json):
        self.defuser_name: str = defuse_json["defuser_name"]
        self.location: Location = Location(defuse_json["location"])
        self.site: str = defuse_json["site"]
        self.round_time: int = defuse_json["round_time"]
        self.player_locations: dict[PlayerName, LocationWithAngle] = {
            player_locations_json["player_name"]: LocationWithAngle(
                player_locations_json
            )
            for player_locations_json in defuse_json["player_locations"]
        }


class Round:
    def __init__(self, round_json):
        self.winning_team: Team = round_json["winning_team"]
        self.winning_side: Side = round_json["winning_side"]
        self.win_method: WinMethod = round_json["win_method"]
        self.duration: int = round_json["duration"]  # milliseconds
        self.player_stats: dict[str, PlayerRoundStats] = {
            player_round_stats_json["player_name"]: PlayerRoundStats(
                player_round_stats_json
            )
            for player_round_stats_json in round_json["player_stats"]
        }
        self.damage_events: list[DamageEvent] = [
            DamageEvent(damage_event_json)
            for damage_event_json in round_json["damage_events"]
        ]
        self.kills: list[Kill] = [Kill(kill_json) for kill_json in round_json["kills"]]
        self.plant: Optional[Plant] = (
            Plant(round_json["plant"]) if round_json["plant"] else None
        )
        self.defuse: Optional[Defuse] = (
            Defuse(round_json["defuse"]) if round_json["defuse"] else None
        )
        self.explode_time: Optional[float] = round_json["exploded"]

    def player_did_die(self, player_name):
        for kill in self.kills:
            if player_name == kill.victim_name:
                return True
        return False


class Match:
    def __init__(self, match_json):
        self.time: datetime = datetime.fromtimestamp(
            match_json["time"], tz=timezone("US/Pacific")
        )
        self.id: str = match_json["match_id"]
        self.map: MapName = match_json["map"]
        self.score_red: int = match_json["score_red"]
        self.score_blue: int = match_json["score_blue"]
        # Teams can include people not listed in PlayerName
        self.team_red: dict[str, Player] = {
            player_json["player_name"]: Player(player_json)
            for player_json in match_json["team_red"]
        }
        self.team_blue: dict[str, Player] = {
            player_json["player_name"]: Player(player_json)
            for player_json in match_json["team_blue"]
        }
        self.rounds: list[Round] = [
            Round(round_json) for round_json in match_json["rounds"]
        ]

        self.all_players = self.team_red | self.team_blue
        if self.score_red > self.score_blue:
            self.winning_team = Team.RED
            self.winning_players: dict[str, Player] = self.team_red
            self.losing_players: dict[str, Player] = self.team_blue
        else:
            self.winning_team = Team.BLUE
            self.winning_players: dict[str, Player] = self.team_blue
            self.losing_players: dict[str, Player] = self.team_red

    def player_did_play(self, player_name):
        return player_name in self.all_players

    def all_players_did_play(self, *PlayerName):
        return all([self.player_did_play(player_name) for player_name in PlayerName])

    def player_did_win(self, player_name):
        return player_name in self.winning_players

    def all_players_did_win(self, *PlayerName):
        return all([self.player_did_win(player_name) for player_name in PlayerName])

    def player_did_lose(self, player_name):
        return player_name in self.losing_players

    def all_players_did_lose(self, *PlayerName):
        return all([self.player_did_lose(player_name) for player_name in PlayerName])

    def players_in_same_team(self, *PlayerName):
        return all([player_name in self.team_red for player_name in PlayerName]) or all(
            [player_name in self.team_blue for player_name in PlayerName]
        )
