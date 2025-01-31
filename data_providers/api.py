from urllib import parse

import requests
from dotenv import dotenv_values
from sys import exit

from data_providers.DataProvider import DataProvider
from data_providers.util import side, username_to_name

API_KEY = dotenv_values()["API_KEY"]
BASE_URL = "https://api.henrikdev.xyz/"


end_type_to_win_method = {
    "Eliminated": "elimination",
    "Bomb detonated": "detonate",
    "Bomb defused": "defuse",
    "Round timer expired": "time",
    "Surrendered": "surrender",
}


def round_duration(round_json):
    post_round_duration = 7000
    match end_type_to_win_method[round_json["end_type"]]:
        case "elimination":
            last_kill_time_in_round = 0
            for player_json in round_json["player_stats"]:
                if len(player_json["kill_events"]) == 0:
                    continue
                for kill_json in player_json["kill_events"]:
                    # Round ends when the last person on the losing term dies
                    if round_json["winning_team"] != kill_json["victim_team"]:
                        last_kill_time_in_round = max(
                            last_kill_time_in_round,
                            kill_json["kill_time_in_round"],
                        )
            return last_kill_time_in_round + post_round_duration

        case "detonate":
            return (
                round_json["plant_events"]["plant_time_in_round"]
                + 45000  # bomb explodes after 45 seconds
                + post_round_duration
            )

        case "defuse":
            return (
                round_json["defuse_events"]["defuse_time_in_round"]
                + post_round_duration
            )

        case "time":
            return 100000 + post_round_duration  # 1:40 min

        case "surrender":
            return 0

        case _:
            raise ValueError(
                f"Unhandled end type: {end_type_to_win_method[round_json['end_type']]}"
            )


class ApiProvider(DataProvider):
    def __init__(self):
        self.api_key = API_KEY

    def fetch(self, match_id: str):
        fetched_json = requests.get(
            parse.urljoin(
                BASE_URL, f"/valorant/v2/match/{match_id}?api_key={self.api_key}"
            ),
        ).json()
        try:
            return fetched_json["data"]
        except:
            print(fetched_json)
            exit(1)

    def parse(self, match_json):
        all_player_names = [
            username_to_name(d["name"]) for d in match_json["players"]["all_players"]
        ]
        n_rounds = match_json["metadata"]["rounds_played"]

        match_data = {
            "map": match_json["metadata"]["map"],
            "time": match_json["metadata"]["game_start"],
            "match_id": match_json["metadata"]["matchid"],
            "score_red": match_json["teams"]["red"]["rounds_won"],
            "score_blue": match_json["teams"]["blue"]["rounds_won"],
            "team_red": [],
            "team_blue": [],
            "rounds": [],
        }

        # Populate teams
        for team in ["red", "blue"]:
            match_data[f"team_{team}"] = {
                username_to_name(d["name"]): {
                    "player_name": username_to_name(d["name"]),
                    "agent": d["character"],
                    "average_combat_score": round(d["stats"]["score"] / n_rounds),
                    "kills": d["stats"]["kills"],
                    "deaths": d["stats"]["deaths"],
                    "assists": d["stats"]["assists"],
                    "kill_deaths": round(d["stats"]["kills"] / d["stats"]["deaths"]),
                    "plants": 0,
                    "defuses": 0,
                    "first_kills": 0,
                    "first_deaths": 0,
                    "multi_kills": 0,
                    # TODO: Calculate KAST and HS percentage
                }
                for d in match_json["players"][team]
            }

        for i, round_json in enumerate(match_json["rounds"]):
            round_data = {
                "winning_team": round_json["winning_team"].lower(),
                "winning_side": side(round_json["winning_team"].lower(), i + 1),
                "win_method": end_type_to_win_method[round_json["end_type"]],
                "duration": round_duration(round_json)
                - (4500 if i == len(match_json["rounds"]) - 1 else 0),
                "plant": None,
                "defuse": None,
                "player_stats": [],
                "damage_events": [],
                "kills": [],
            }

            if round_data["win_method"] == "surrender":
                continue

            if round_json["bomb_planted"]:
                planter_name = username_to_name(
                    round_json["plant_events"]["planted_by"]["display_name"].split("#")[
                        0
                    ]
                )
                planter_team = round_json["plant_events"]["planted_by"]["team"].lower()
                plant_data = {
                    "planter_name": planter_name,
                    "location": {
                        "x": round_json["plant_events"]["plant_location"]["x"],
                        "y": round_json["plant_events"]["plant_location"]["y"],
                    },
                    "site": round_json["plant_events"]["plant_site"],
                    "round_time": round_json["plant_events"]["plant_time_in_round"],
                    "player_locations": [
                        {
                            "player_name": username_to_name(
                                d["player_display_name"].split("#")[0]
                            ),
                            "angle": d["view_radians"],
                            "location": {
                                "x": d["location"]["x"],
                                "y": d["location"]["y"],
                            },
                        }
                        for d in round_json["plant_events"]["player_locations_on_plant"]
                    ],
                }
                match_data[f"team_{planter_team}"][planter_name]["plants"] += 1
                round_data["plant"] = plant_data

            if round_json["bomb_defused"]:
                defuser_name = username_to_name(
                    round_json["defuse_events"]["defused_by"]["display_name"].split(
                        "#"
                    )[0]
                )
                defuser_team = round_json["defuse_events"]["defused_by"]["team"].lower()
                defuse_data = {
                    "defuser_name": defuser_name,
                    "location": {
                        "x": round_json["defuse_events"]["defuse_location"]["x"],
                        "y": round_json["defuse_events"]["defuse_location"]["y"],
                    },
                    "site": round_data["plant"]["site"],
                    "round_time": round_json["defuse_events"]["defuse_time_in_round"],
                    "player_locations": [
                        {
                            "player_name": username_to_name(
                                d["player_display_name"].split("#")[0]
                            ),
                            "angle": d["view_radians"],
                            "location": {
                                "x": d["location"]["x"],
                                "y": d["location"]["y"],
                            },
                        }
                        for d in round_json["defuse_events"][
                            "player_locations_on_defuse"
                        ]
                    ],
                }
                match_data[f"team_{defuser_team}"][defuse_data["defuser_name"]][
                    "defuses"
                ] += 1
                round_data["defuse"] = defuse_data

            round_data["exploded"] = (
                round_data["plant"]["round_time"] + 45000
                if round_json["end_type"] == "Bomb detonated"
                else None
            )

            player_stats_data = {
                player_name: {
                    "player_name": None,
                    "team": None,
                    "side": None,
                    "score": None,
                    "kills": 0,
                    "deaths": 0,
                    "assists": 0,
                    "damage": None,
                    "loadout_value": None,
                    "remaining_credits": None,
                    "spent_credits": None,
                }
                for player_name in all_player_names
            }

            earliest_kill_json = {}
            for player_stats_json in round_json["player_stats"]:
                # Everything except kills, deaths, assists is assignable up front
                player_name = username_to_name(
                    player_stats_json["player_display_name"].split("#")[0]
                )
                player_team = player_stats_json["player_team"].lower()
                player_stats_data[player_name]["player_name"] = player_name
                player_stats_data[player_name]["team"] = player_team
                player_stats_data[player_name]["side"] = side(
                    player_stats_json["player_team"].lower(), i + 1
                )
                player_stats_data[player_name]["score"] = player_stats_json["score"]
                player_stats_data[player_name]["kills"] = player_stats_json["kills"]
                player_stats_data[player_name]["damage"] = player_stats_json["damage"]
                player_stats_data[player_name]["loadout_value"] = player_stats_json[
                    "economy"
                ]["loadout_value"]
                player_stats_data[player_name]["remaining_credits"] = player_stats_json[
                    "economy"
                ]["remaining"]
                player_stats_data[player_name]["spent_credits"] = player_stats_json[
                    "economy"
                ]["spent"]

                if player_stats_json["kills"] > 2:
                    match_data[f"team_{player_team}"][player_name]["multi_kills"] += 1

                for damage_event_json in player_stats_json["damage_events"]:
                    receiver_name = username_to_name(
                        damage_event_json["receiver_display_name"].split("#")[0]
                    )
                    # Self-damage and bomb damage don't count as damage for per-player round stats on tracker.gg
                    if (
                        player_name == receiver_name
                        and damage_event_json["damage"] != 999
                    ):
                        player_stats_data[player_name]["damage"] -= damage_event_json[
                            "damage"
                        ]
                    round_data["damage_events"].append(
                        {
                            "giver_name": player_name,
                            "receiver_name": receiver_name,
                            "damage": damage_event_json["damage"],
                            "legshots": damage_event_json["legshots"],
                            "bodyshots": damage_event_json["bodyshots"],
                            "headshots": damage_event_json["headshots"],
                        }
                    )

                for kill_json in player_stats_json["kill_events"]:
                    if (
                        earliest_kill_json == {}
                        or kill_json["kill_time_in_round"]
                        < earliest_kill_json["kill_time_in_round"]
                    ):
                        earliest_kill_json = kill_json

                    killer_name = username_to_name(
                        kill_json["killer_display_name"].split("#")[0]
                    )
                    victim_name = username_to_name(
                        kill_json["victim_display_name"].split("#")[0]
                    )
                    assistants = [
                        username_to_name(d["assistant_display_name"].split("#")[0])
                        for d in kill_json["assistants"]
                    ]

                    weapon = None
                    if "damage_weapon_name" not in kill_json:
                        # AFAIK, this only occurs with Chamber's utility
                        weapon = "Ability"
                    elif (
                        not kill_json["damage_weapon_name"]
                        and kill_json["damage_weapon_id"] == ""
                    ):
                        weapon = "Bomb" if killer_name == victim_name else "Melee"

                    if not weapon:
                        if kill_json["damage_weapon_id"] in [
                            "Ability1",
                            "Ability2",
                            "GrenadeAbility",
                            "Ultimate",
                        ]:
                            weapon = kill_json["damage_weapon_id"]
                        else:
                            weapon = kill_json["damage_weapon_name"]

                    # Aggregate deaths and assistants
                    player_stats_data[victim_name]["deaths"] += 1
                    for assistant_name in assistants:
                        player_stats_data[assistant_name]["assists"] += 1

                    killer_location = None
                    player_locations = []
                    for player_location_json in kill_json["player_locations_on_kill"]:
                        location_data = {
                            "player_name": username_to_name(
                                player_location_json["player_display_name"].split("#")[
                                    0
                                ]
                            ),
                            "location": {
                                "x": player_location_json["location"]["x"],
                                "y": player_location_json["location"]["y"],
                            },
                            "angle": player_location_json["view_radians"],
                        }

                        if location_data["player_name"] == killer_name:
                            killer_location = location_data

                        player_locations.append(location_data)

                    round_data["kills"].append(
                        {
                            "killer_name": killer_name,
                            "victim_name": victim_name,
                            "assistants": assistants,
                            "killer_location": killer_location,
                            "victim_location": {
                                "x": kill_json["victim_death_location"]["x"],
                                "y": kill_json["victim_death_location"]["y"],
                            },
                            "player_locations": player_locations,
                            "weapon_name": weapon,
                            "game_time": kill_json["kill_time_in_match"],
                            "round_time": kill_json["kill_time_in_round"],
                        }
                    )

                round_data["player_stats"] = list(player_stats_data.values())

            first_kill_killer_name = username_to_name(
                earliest_kill_json["killer_display_name"].split("#")[0]
            )
            first_kill_killer_team = earliest_kill_json["killer_team"].lower()

            first_kill_victim_name = username_to_name(
                earliest_kill_json["victim_display_name"].split("#")[0]
            )
            first_kill_victim_team = earliest_kill_json["victim_team"].lower()

            match_data[f"team_{first_kill_killer_team}"][first_kill_killer_name][
                "first_kills"
            ] += 1
            match_data[f"team_{first_kill_victim_team}"][first_kill_victim_name][
                "first_deaths"
            ] += 1

            match_data["rounds"].append(round_data)

        for team in ["red", "blue"]:
            match_data[f"team_{team}"] = list(match_data[f"team_{team}"].values())
        return match_data
