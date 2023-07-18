# Valorant Customs Stats

## Dashboards

-   [Website](https://valorant-customs-graphs.vercel.app/)
-   [Power BI](https://app.powerbi.com/view?r=eyJrIjoiNGUzNzMyOTctNTg2OC00YTEyLThmNjktOTJiOTE3ZGM0NjI3IiwidCI6IjlkZGFhY2ExLTM4OWYtNGNiMS1hMTEzLTA4MWJlNmNjMjVmYyIsImMiOjZ9)

## Documentation

### Datasets

| Dataset                                   | Description                                                                   |
| :---------------------------------------- | :---------------------------------------------------------------------------- |
| `assists-given-per-standard-game.json`    | Average assists given per 25-round game                                       |
| `assists-received-per-standard-game.json` | Average assists received per 25-round game                                    |
| `cumulative-winrate-over-time.json`       | Cumulative win rate calculated every 2 weeks                                  |
| `data-frame-friendly.json`                | Format more easily converted to a data frame for autobalancing                |
| `easiest-matchups.json`                   | Win rate when a certain player is on the opposing team                        |
| `individual.json`                         | Individual stats, e.g., per match, per agent, etc.                            |
| `maps.json`                               | Overall play count on each map                                                |
| `meta.json`                               | Extra data for the front-end                                                  |
| `portion-of-stats.json`                   | E.g., portion of kills from the player out of all kills in all of their games |
| `roles.json`                              | Overall role count                                                            |
| `running-winrate-over-time.json`          | Win rate in the past 60 days calculated every 2 weeks                         |
| `teammate-synergy.json`                   | Win rate when a certain player is on the same team                            |
| `winrate-over-time.json`                  | Win rate over each 2 week block                                               |

### Dataset Generation

All data is derived from [tracker.gg](https://tracker.gg/valorant) until Riot releases the API for personal use. All datasets used for dashboards can be found in the `out` directory. To generate them yourself:

1. Run `scrape.py` to scrape the raw data. It will be saved to a huge minified file (~70 MB) called `scrape.json`. For an example of what each match looks like in a readable format, see `tracker-sample.json`.
2. Run `process_scrape.py` to transform the data into something the main Python script can handle. See `data.json` for the output and `Match.py` for its representation in the main script.
3. Run `make_datasets.py` to generate all the smaller datasets used by the front-end.

### Credits

| Contributor       | Role                |
| :---------------- | :------------------ |
| **Steven Truong** | Developer           |
| **Lindsey Wong**  | Unknown Subordinate |
