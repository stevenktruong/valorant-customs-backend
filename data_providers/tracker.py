import json
import os.path
import time
from random import uniform

import jsonlines
import undetected_chromedriver as uc
from dateutil.parser import isoparse
from selenium.webdriver.common.by import By

from config import PROXY
from constants import *
from data_providers.DataProvider import DataProvider

from .util import username_to_name


class TrackerProvider(DataProvider):
    def fetch(self, match_id: str, driver=None):
        raise DeprecationWarning("Attempted to fetch from tracker.gg")

        if driver is None:
            driver = self.new_driver()

        api_url = f"https://api.tracker.gg/api/v2/valorant/standard/matches/{match_id}"
        driver.get(api_url)

        return json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)["data"]

    def parse(self, match_json):
        match = {
            "time": round(isoparse(match_json["metadata"]["dateStarted"]).timestamp()),
            "match_id": match_json["attributes"]["id"],
            "map": match_json["metadata"]["mapName"],
            "score_red": None,
            "score_blue": None,
            "team_red": [],
            "team_blue": [],
            "rounds": [
                {
                    "winning_team": "",
                    "winning_side": "",
                    "win_method": "",
                    "duration": None,
                    "player_stats": [],
                    "damage_events": [],
                    "kills": [],
                }
                for _ in range(match_json["metadata"]["rounds"])
            ],
        }

        for segment in match_json["segments"]:
            match segment["type"]:
                case "round-summary":
                    round_index = segment["attributes"]["round"] - 1
                    match["rounds"][round_index]["winning_team"] = segment["stats"][
                        "winningTeam"
                    ]["value"].lower()
                    match["rounds"][round_index]["win_method"] = segment["stats"][
                        "roundResult"
                    ]["value"].lower()
                    match["rounds"][round_index]["plant"] = (
                        {
                            "planter_name": username_to_name(
                                segment["metadata"]["plant"][
                                    "platformUserIdentifier"
                                ].split("#")[0]
                            ),
                            "location": {
                                "x": segment["metadata"]["plant"]["location"]["x"],
                                "y": segment["metadata"]["plant"]["location"]["y"],
                            },
                            "site": segment["metadata"]["plant"]["site"],
                            "round_time": segment["metadata"]["plant"]["roundTime"],
                            "player_locations": [
                                {
                                    "player_name": username_to_name(
                                        d["platformUserIdentifier"].split("#")[0]
                                    ),
                                    "angle": d["viewRadians"],
                                    "location": {
                                        "x": d["location"]["x"],
                                        "y": d["location"]["y"],
                                    },
                                }
                                for d in segment["metadata"]["plant"]["playerLocations"]
                            ],
                        }
                        if segment["metadata"]["plant"]
                        else None
                    )

                    match["rounds"][round_index]["defuse"] = (
                        {
                            "defuser_name": username_to_name(
                                segment["metadata"]["defuse"][
                                    "platformUserIdentifier"
                                ].split("#")[0]
                            ),
                            "location": {
                                "x": segment["metadata"]["defuse"]["location"]["x"],
                                "y": segment["metadata"]["defuse"]["location"]["y"],
                            },
                            "site": segment["metadata"]["defuse"]["site"],
                            "round_time": segment["metadata"]["defuse"]["roundTime"],
                            "player_locations": [
                                {
                                    "player_name": username_to_name(
                                        d["platformUserIdentifier"].split("#")[0]
                                    ),
                                    "angle": d["viewRadians"],
                                    "location": {
                                        "x": d["location"]["x"],
                                        "y": d["location"]["y"],
                                    },
                                }
                                for d in segment["metadata"]["defuse"][
                                    "playerLocations"
                                ]
                            ],
                        }
                        if segment["metadata"]["defuse"]
                        else None
                    )
                    match["rounds"][round_index]["exploded"] = (
                        round(segment["metadata"]["exploded"])
                        if segment["metadata"]["exploded"]
                        else None
                    )

                case "player-round":
                    round_index = segment["attributes"]["round"] - 1
                    player_name = username_to_name(
                        segment["attributes"]["platformUserIdentifier"].split("#")[0]
                    )
                    match["rounds"][round_index]["player_stats"].append(
                        {
                            "player_name": player_name,
                            "team": segment["metadata"]["teamId"].lower(),
                            "side": segment["metadata"]["teamSide"] + "s",
                            "score": segment["stats"]["score"]["value"],
                            "kills": segment["stats"]["kills"]["value"],
                            "deaths": segment["stats"]["deaths"]["value"],
                            "assists": segment["stats"]["assists"]["value"],
                            "damage": segment["stats"]["damage"]["value"],
                            "loadout_value": segment["stats"]["loadoutValue"]["value"],
                            "remaining_credits": segment["stats"]["remainingCredits"][
                                "value"
                            ],
                            "spent_credits": segment["stats"]["spentCredits"]["value"],
                        }
                    )

                case "player-round-damage":
                    round_index = segment["attributes"]["round"] - 1
                    giver_name = username_to_name(
                        segment["attributes"]["platformUserIdentifier"].split("#")[0]
                    )
                    receiver_name = username_to_name(
                        segment["attributes"]["opponentPlatformUserIdentifier"].split(
                            "#"
                        )[0]
                    )
                    match["rounds"][round_index]["damage_events"].append(
                        {
                            "giver_name": giver_name,
                            "receiver_name": receiver_name,
                            "damage": segment["stats"]["damage"]["value"],
                            "legshots": segment["stats"]["legshots"]["value"],
                            "bodyshots": segment["stats"]["bodyshots"]["value"],
                            "headshots": segment["stats"]["headshots"]["value"],
                        }
                    )

                case "player-round-kills":
                    round_index = segment["attributes"]["round"] - 1
                    killer_name = username_to_name(
                        segment["attributes"]["platformUserIdentifier"].split("#")[0]
                    )
                    victim_name = username_to_name(
                        segment["attributes"]["opponentPlatformUserIdentifier"].split(
                            "#"
                        )[0]
                    )

                    match segment["metadata"]["finishingDamage"]["damageType"]:
                        case "Melee":
                            weapon = "Melee"
                        case "Bomb":
                            weapon = "Bomb"
                        case "Weapon":
                            weapon = segment["metadata"]["weaponName"]
                            if not weapon:
                                # Happens only with Chamber abilities AFAIK
                                weapon = "Ability"
                        case _:
                            # Ability
                            weapon = segment["metadata"]["finishingDamage"][
                                "damageItem"
                            ]

                    player_locations = [
                        {
                            "player_name": username_to_name(
                                d["platformUserIdentifier"].split("#")[0]
                            ),
                            "angle": d["viewRadians"],
                            "location": {
                                "x": d["location"]["x"],
                                "y": d["location"]["y"],
                            },
                        }
                        for d in segment["metadata"]["playerLocations"]
                    ]

                    killer_location = None
                    for d in player_locations:
                        if d["player_name"] == killer_name:
                            killer_location = d

                    match["rounds"][round_index]["kills"].append(
                        {
                            "killer_name": killer_name,
                            "victim_name": victim_name,
                            "assistants": [
                                username_to_name(
                                    d["platformUserIdentifier"].split("#")[0]
                                )
                                for d in segment["metadata"]["assistants"]
                            ],
                            "killer_location": killer_location,
                            "victim_location": {
                                "x": segment["metadata"]["opponentLocation"]["x"],
                                "y": segment["metadata"]["opponentLocation"]["y"],
                            },
                            "player_locations": player_locations,
                            "weapon_name": weapon,
                            "game_time": segment["metadata"]["gameTime"],
                            "round_time": segment["metadata"]["roundTime"],
                        }
                    )

                case "player-summary":
                    player_name = username_to_name(
                        segment["attributes"]["platformUserIdentifier"].split("#")[0]
                    )
                    match[f"team_{segment['metadata']['teamId'].lower()}"].append(
                        {
                            "player_name": player_name,
                            "agent": segment["metadata"]["agentName"],
                            "average_combat_score": round(
                                segment["stats"]["scorePerRound"]["value"]
                            ),
                            "kills": segment["stats"]["kills"]["value"],
                            "deaths": segment["stats"]["deaths"]["value"],
                            "assists": segment["stats"]["assists"]["value"],
                            "kill_deaths": round(segment["stats"]["kdRatio"]["value"]),
                            # "kill_assist_survive_traded": round(
                            #     segment["stats"]["kast"]["value"]
                            # ),
                            "plants": segment["stats"]["plants"]["value"],
                            "defuses": segment["stats"]["defuses"]["value"],
                            "first_kills": segment["stats"]["firstKills"]["value"],
                            "first_deaths": segment["stats"]["firstDeaths"]["value"],
                            "multi_kills": segment["stats"]["multiKills"]["value"],
                            # "headshot_accuracy": round(
                            #     segment["stats"]["hsAccuracy"]["value"]
                            # ),
                            # "econ": segment["stats"]["econRating"]["value"],
                        }
                    )

                case "team-summary":
                    if segment["attributes"]["teamId"] == "Red":
                        match["score_red"] = segment["stats"]["roundsWon"]["value"]
                    else:
                        match["score_blue"] = segment["stats"]["roundsWon"]["value"]

                case "player-loadout":
                    # Stats on how players performed on pistol/eco/force/full buy rounds
                    pass
                case other:
                    print(f"Missed type: {segment['type']}")

        for i in range(len(match["rounds"])):
            match["rounds"][i]["kills"].sort(key=lambda x: x["round_time"])
            if (
                match["rounds"][i]["player_stats"][0]["team"]
                == match["rounds"][i]["winning_team"]
            ):
                match["rounds"][i]["winning_side"] = match["rounds"][i]["player_stats"][
                    0
                ]["side"]
            else:
                match["rounds"][i]["winning_side"] = (
                    "attackers"
                    if match["rounds"][i]["player_stats"][0]["side"] == "defenders"
                    else "defenders"
                )

            # Some surrender rounds are marked as elimination
            # Not the most robust method, but no-kill rounds are extremely rare
            if len(match["rounds"][i]["kills"]) == 0:
                match["rounds"][i]["win_method"] = "surrendered"
                match["rounds"][i]["duration"] = 0
                continue

            round_start = (
                match["rounds"][i]["kills"][0]["game_time"]
                - match["rounds"][i]["kills"][0]["round_time"]
            )

            if (
                i < len(match["rounds"]) - 1
                and len(match["rounds"][i + 1]["kills"]) > 0
            ):
                # round end = (next round first kill game time) - (next round first kill round time) - (buy phase)
                round_end = (
                    match["rounds"][i + 1]["kills"][0]["game_time"]
                    - match["rounds"][i + 1]["kills"][0]["round_time"]
                    - 1000 * 30
                    - 1000
                    * (
                        15 if i + 1 == 12 or i + 1 == 24 else 0
                    )  # First round of the half has a longer buy phase
                )
            else:
                # round end is just the end of the match for the last round or rounds before surrenders
                round_end = match_json["metadata"]["duration"]

            match["rounds"][i]["duration"] = round_end - round_start

        return match

    def new_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--headless")
        if PROXY:
            options.add_argument(f"--proxy-server={PROXY}")
        return uc.Chrome(options=options)


def scrape_all(driver=None):
    """Deprecated: Relying on the unofficial VALORANT API now."""
    tracker = TrackerProvider()

    # Starting from 10/11/22
    urls = []
    if os.path.exists("./tracker-urls.txt"):
        with open("./tracker-urls.txt", mode="r") as f:
            urls = [line.rstrip() for line in f]

    matches = []
    if os.path.exists("./scrape.jsonl"):
        with jsonlines.open("./scrape.jsonl", mode="r") as f:
            for match in f:
                matches.append(match)

    for match in matches:
        if match["tracker_url"] in urls:
            urls.remove(match["tracker_url"])

    if len(urls) == 0:
        return

    if driver is None:
        driver = tracker.new_driver()

    new_matches = []
    for i, url in enumerate(urls, start=1):
        print(
            f"[{'0' if i <= 9 and len(urls) >= 10 else ''}{i}/{len(urls)}]: Scraping {url}... ",
            end="",
        )
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                time.sleep(3 + uniform(-0.25, 0.25))
                match_json = tracker.fetch(url, driver=driver)
                new_matches.append(match_json)

                print("Success")
                break
            except Exception as e:
                if retries == 0:
                    print("Failed")
                    break
                print(e)
                continue

    print("Saving... ", end="")
    with jsonlines.open("./scrape.jsonl", mode="a") as f:
        f.write_all(new_matches)
    print("Done")

    driver.close()
