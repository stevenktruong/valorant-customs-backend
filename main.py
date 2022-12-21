import json, os.path
from datetime import datetime, timedelta, time

from Match import Match
from util import aggregate_matches, filter_players
from constants.misc import *
from constants.players import *
from constants.valorant import *

output_dir = "./out"

data = {}
matches: list[Match] = []
with open("./data.json", mode="r") as f:
    data = json.load(f)
    matches = sorted([Match(match_json) for match_json in data], key=lambda m: m.time)
    f.close()

if __name__ == "__main__":
    with open(os.path.join(output_dir, "data-frame-friendly.json"), mode="w") as f:
        out_json = {i: match_json for i, match_json in enumerate(data)}
        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "individual.json"), mode="w") as f:
        out_json = {
            player_name: PLAYER_INFO[player_name].copy()
            | {WINRATE: None, WINS: 0, GAMES: 0, TOP_AGENTS: [], TOP_ROLES: []}
            for player_name in PLAYER_NAMES
        }

        player_agent_stats = {
            player_name: {
                AGENTS: {agent_name: 0 for agent_name in AGENT_NAMES},
                ROLES: {role_name: 0 for role_name in ROLE_NAMES},
            }
            for player_name in PLAYER_NAMES
        }

        for match in matches:
            for player_name in filter_players(match.all_players):
                player_stats = match.all_players[player_name]
                player_entry = out_json[player_name]

                # Update winrate
                if match.player_did_win(player_name):
                    player_entry[WINS] += 1
                if match.player_did_play(player_name):
                    player_entry[GAMES] += 1
                if player_entry[GAMES] != 0:
                    player_entry[WINRATE] = round(
                        100 * player_entry[WINS] / player_entry[GAMES]
                    )

                # Update agents and roles
                player_agent_stats[player_name][AGENTS][player_stats.agent] += 1
                player_agent_stats[player_name][ROLES][
                    AGENT_NAME_TO_ROLE[player_stats.agent]
                ] += 1

        for player_name in PLAYER_NAMES:
            for role_name in ROLE_NAMES:
                if (
                    player_agent_stats[player_name][ROLES][role_name]
                    / out_json[player_name][GAMES]
                    > 0.3
                ):
                    out_json[player_name][TOP_ROLES].append(role_name)

            agents_sorted_by_plays = sorted(
                player_agent_stats[player_name][AGENTS],
                key=lambda agent_name: (
                    -player_agent_stats[player_name][AGENTS][agent_name],
                    agent_name,
                ),
            )
            out_json[player_name][TOP_AGENTS] = [
                {
                    AGENT: agent_name,
                    FULL_BODY_IMAGE_URL: AGENT_NAME_TO_FULL_BODY_IMAGE_URL[agent_name],
                }
                for agent_name in agents_sorted_by_plays[:3]
            ]

        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "teammate-synergy.json"), mode="w") as f:
        out_json = {
            player_name: {
                teammate_name: {
                    TEAMMATE_NAME: teammate_name,
                    WINRATE: None,
                    WINS: 0,
                    GAMES: 0,
                }
                for teammate_name in PLAYER_NAMES
            }
            for player_name in PLAYER_NAMES
        }

        for match in matches:
            for player_name in filter_players(match.winning_players):
                for teammate_name in filter_players(match.winning_players):
                    if player_name == teammate_name:
                        continue
                    out_json[player_name][teammate_name][WINS] += 1
                    out_json[player_name][teammate_name][GAMES] += 1
            for player_name in filter_players(match.losing_players):
                for teammate_name in filter_players(match.losing_players):
                    if player_name == teammate_name:
                        continue
                    out_json[player_name][teammate_name][GAMES] += 1
        for player_name in out_json:
            for teammate_name in out_json[player_name]:
                if out_json[player_name][teammate_name][GAMES] != 0:
                    out_json[player_name][teammate_name][WINRATE] = round(
                        100
                        * out_json[player_name][teammate_name][WINS]
                        / out_json[player_name][teammate_name][GAMES]
                    )

        for player_name in out_json:
            out_json[player_name] = sorted(
                out_json[player_name].values(), key=lambda x: x[TEAMMATE_NAME]
            )
        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "easiest-matchups.json"), mode="w") as f:
        out_json = {
            player_name: {
                opponent_name: {
                    OPPONENT_NAME: opponent_name,
                    WINRATE: None,
                    WINS: 0,
                    GAMES: 0,
                }
                for opponent_name in PLAYER_NAMES
            }
            for player_name in PLAYER_NAMES
        }

        for match in matches:
            for player_name in filter_players(match.winning_players):
                for opponent_name in filter_players(match.losing_players):
                    out_json[player_name][opponent_name][WINS] += 1
                    out_json[player_name][opponent_name][GAMES] += 1
            for player_name in filter_players(match.losing_players):
                for opponent_name in filter_players(match.winning_players):
                    out_json[player_name][opponent_name][GAMES] += 1
        for player_name in out_json:
            for opponent_name in out_json[player_name]:
                if out_json[player_name][opponent_name][GAMES] != 0:
                    out_json[player_name][opponent_name][WINRATE] = round(
                        100
                        * out_json[player_name][opponent_name][WINS]
                        / out_json[player_name][opponent_name][GAMES]
                    )

        for player_name in out_json:
            out_json[player_name] = sorted(
                out_json[player_name].values(), key=lambda x: x[OPPONENT_NAME]
            )
        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "maps.json"), mode="w") as f:
        out_json = {map: 0 for map in MAPS}
        for match in matches:
            out_json[match.map] += 1
        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "portion-of-stats.json"), mode="w") as f:
        metrics = {
            KILLS: lambda player_stats: player_stats.kills,
            DEATHS: lambda player_stats: player_stats.deaths,
            ASSISTS: lambda player_stats: player_stats.assists,
            FIRST_KILLS: lambda player_stats: player_stats.first_kills,
            FIRST_DEATHS: lambda player_stats: player_stats.first_deaths,
        }

        out_json = {
            player_name: {
                metric: {
                    PERCENTAGE: None,
                    COMMITTED: 0,
                    WITNESSED: 0,
                }
                for metric in metrics
            }
            for player_name in PLAYER_NAMES
        }

        for match in matches:
            for player_name in match.all_players:
                player_stats = match.all_players[player_name]
                for metric, fn in metrics.items():
                    if player_name in PLAYER_NAMES:
                        out_json[player_name][metric][COMMITTED] += fn(player_stats)
                for player_name_to_update in filter_players(match.all_players):
                    for metric, fn in metrics.items():
                        out_json[player_name_to_update][metric][WITNESSED] += fn(
                            player_stats
                        )

        for player_name in out_json:
            for metric in metrics:
                if out_json[player_name][metric][WITNESSED] == 0:
                    continue
                out_json[player_name][metric][PERCENTAGE] = round(
                    100
                    * out_json[player_name][metric][COMMITTED]
                    / out_json[player_name][metric][WITNESSED]
                )

        json.dump(out_json, f, indent=2)
        f.close()

    with open(os.path.join(output_dir, "winrate-over-time.json"), mode="w") as f:

        def winrate(matches: list[Match], accumulator):
            block_data = {
                player_name: {WINRATE: None, WINS: 0, GAMES: 0}
                for player_name in PLAYER_NAMES
            }
            for match in matches:
                for winner_name in filter_players(match.winning_players):
                    block_data[winner_name][WINS] += 1
                for player_name in filter_players(match.all_players):
                    block_data[player_name][GAMES] += 1
            for player_name, player_stats in block_data.items():
                if player_stats[GAMES] != 0:
                    player_stats[WINRATE] = round(
                        100 * player_stats[WINS] / player_stats[GAMES]
                    )
            return block_data

        out_json = aggregate_matches(matches, winrate)
        json.dump(out_json, f, indent=2, default=str)
        f.close()

    with open(
        os.path.join(output_dir, "cumulative-winrate-over-time.json"), mode="w"
    ) as f:

        def cumulative_winrate(matches: list[Match], accumulator):
            if len(accumulator) > 0:
                block_data = {
                    player_name: accumulator[-1]["data"][player_name].copy()
                    for player_name in PLAYER_NAMES
                }
            else:
                block_data = {
                    player_name: {WINRATE: None, WINS: 0, GAMES: 0}
                    for player_name in PLAYER_NAMES
                }
            for match in matches:
                for winner_name in filter_players(match.winning_players):
                    block_data[winner_name][WINS] += 1
                for player_name in filter_players(match.all_players):
                    block_data[player_name][GAMES] += 1
            for player_name, player_stats in block_data.items():
                if player_stats[GAMES] != 0:
                    player_stats[WINRATE] = round(
                        100 * player_stats[WINS] / player_stats[GAMES]
                    )
            return block_data

        out_json = aggregate_matches(matches, cumulative_winrate)
        json.dump(out_json, f, indent=2, default=str)
        f.close()

    with open(
        os.path.join(output_dir, "running-winrate-over-time.json"), mode="w"
    ) as f:

        out_json = []

        last_date = datetime.combine(datetime.today(), time.max)
        curr_date = datetime.combine(datetime(year=2022, month=10, day=9), time.max)
        time_increment = timedelta(weeks=1)

        curr_block_start_date = curr_date - timedelta(days=60)

        i = 0
        j = 0
        while j <= len(matches):
            # Blocks look like (curr_block_start_date, curr_date]; should correspond to [i, j)
            while j < len(matches) and matches[j].time <= curr_date:
                j += 1
            while i < len(matches) and matches[i].time < curr_block_start_date:
                i += 1
            if i == len(matches) or curr_date > last_date:
                break

            block_data = {
                player_name: {WINRATE: None, WINS: 0, GAMES: 0}
                for player_name in PLAYER_NAMES
            }

            for match in matches[i:j]:
                for winner_name in filter_players(match.winning_players):
                    block_data[winner_name][WINS] += 1
                for player_name in filter_players(match.all_players):
                    block_data[player_name][GAMES] += 1
            for player_name, player_stats in block_data.items():
                if player_stats[GAMES] != 0:
                    player_stats[WINRATE] = round(
                        100 * player_stats[WINS] / player_stats[GAMES]
                    )

            out_json.append({"block_end_time": curr_date, "data": block_data})

            curr_date += time_increment
            curr_block_start_date += time_increment

        # Individually compute the present day

        json.dump(out_json, f, indent=2, default=str)
        f.close()
