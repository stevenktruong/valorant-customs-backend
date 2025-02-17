import json
import os.path

from data_providers import get_matches
from dataset_generators import *
from Match import Match


def generate_datasets(matches: list[Match], output_dir, minified=False):
    matches.sort(key=lambda m: m.time)

    dashboard_generators: list[DatasetGenerator] = [
        AssistsGivenPerStandardGameGenerator(),
        AssistsReceivedPerStandardGameGenerator(),
        EasiestMatchupsGenerator(),
        IndividualGenerator(),
        MapsGenerator(),
        MetaGenerator(),
        RecentLobbyWinRatesGenerator(),
        RolesGenerator(),
        RunningWinrateOverTimeGenerator(),
        TeamSynergyDataGenerator(),
        TeammateSynergyGenerator(),
    ]
    wall_of_shame_generator = WallOfShameGenerator()
    teammate_synergy_data_generator = TeamSynergyDataGenerator()

    all_generators = dashboard_generators + [
        wall_of_shame_generator,
        teammate_synergy_data_generator,
    ]

    for match in matches:
        for generator in all_generators:
            generator.accumulate(match)

    # Data for api/dashboard
    dashboard_json = {}
    for generator in dashboard_generators:
        dashboard_json["_".join(generator.name.split("-"))] = generator.finalize(
            minified=minified
        )

    # Data for api/wall-of-shame
    wall_of_shame_generator.finalize()
    wall_of_shame_generator.generate(output_dir=output_dir, minified=minified)

    # Data for training one of the balancing algorithms
    teammate_synergy_data_generator.finalize()
    teammate_synergy_data_generator.generate(output_dir=output_dir, minified=minified)

    indent = 2
    separators = None
    if minified:
        indent = None
        separators = (",", ":")

    with open(os.path.join(output_dir, "dashboard.json"), mode="w") as f:
        json.dump(dashboard_json, f, indent=indent, separators=separators)


if __name__ == "__main__":
    matches = get_matches()
    generate_datasets(matches=matches, output_dir="./out-min", minified=True)
