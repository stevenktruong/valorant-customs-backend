# Valorant Customs Stats

[Dashboard](https://www.valoquestionmark.com/)

## Documentation

### Setup

Before you can run anything, you need to install all dependencies. It's recommended to do this in a virtual environment:

```bash
python3.12 -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

After you run this once, next time you only need to run

```bash
source env/bin/activate
```

before you can use the available scripts. Note that Python 3.12 is required.

### Usage

You can start the backend with `gunicorn app:app`. In addition to the API, the backend does the following:

-   On startup, if `match-ids.txt` or `config.py` is newer than `out-min/dashboard.json`, the server will automatically update all the datasets.
-   Every midnight PST, the datasets are refreshed (after enough time, older matches will be excluded from some stats).

### API Endpoints

Each API endpoint is registered via `add_url_rule` in `app.py`.

| Method    | Endpoint        | Parameters | Description                                                                               |
| :-------- | :-------------- | :--------- | :---------------------------------------------------------------------------------------- |
| `GET`     | `dashboard`     |            | Returns data used to make graphs on the dashboard.                                        |
| `GET`     | `wall-of-shame` |            | Returns data used to make the Wall of Shame leaderboards.                                 |
| `POST`    | `match`         | `url`      | Attempt to add the match corresponding to the tracker.gg URL `url` to the dashboard.      |
| `DELETE ` | `match`         | `url`      | Attempt to remove the match corresponding to the tracker.gg URL `url` from the dashboard. |
| `GET`     | `match/all`     |            | Returns a list of all the tracker.gg URLs tracked by the dashboard.                       |

### Data

<!-- TODO: Write blurb about API, data_providers; test changes to make sure dashboard doesn't change (drastically) -->

All data is derived from either [tracker.gg](https://tracker.gg/valorant) or the [unofficial VALORANT API](https://github.com/Henrik-3/unofficial-valorant-api). `samples` contain example JSON from these sources. Since bot detection has improved, scraping from tracker.gg is now deprecated, so data from there can no longer (reliably) be scraped. Consequently, previously scraped data needs to be manually acquired, and all future matches will be fetched via the unofficial API.

Code for fetching and parsing from each data source can be found in `data_providers`.

`tracker-match-ids.txt` contains all the matches that were scraped from tracker.gg and will no longer be updated. `match-ids.txt` contains all matches fetched from the unofficial API and will be updated.

Each line in `tracker-data.jsonl` and `api-data.jsonl` is mapped to a `Match` object, which exposes all data with an API (see `Match.py`). To see examples of how to use it, see `notebooks/example.ipynb`.

#### Datasets

From the main scraped data, we generate smaller datasets with derived statistics that we're interested in. Each of these datasets corresponds to a `DatasetGenerator` implementation in `dataset_generators`. Each `DatasetGenerator` needs to implement three methods:

| Method                   | Description                                                                                                                         |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `__init__` (constructor) | The argument passed into the superclass constructor is the name of the dataset, e.g., it's used as a key in `dashboard.json`.       |
| `accumulate`             | Processes the next match and updates `out_json` accordingly.                                                                        |
| `finalize`               | Performs any other computations needed to make the dataset, e.g., compute the win rate from the games counted through `accumulate`. |

Once a `DatasetGenerator` is implemented, it needs to be included somewhere in `generate_datasets.py`.

All datasets used for dashboards can be found in the `out-min` directory. To generate them manually, run `generate_datasets.py` to generate all the smaller datasets used by the front-end. They will appear in `out-min`.

### Testing

There is a simple integration test in `integ-test.py` which tests the codebase against a database with one match to handle. API endpoints can be tested using [Bruno](https://www.usebruno.com/); there's already configuration for it included.

### Onboarding Players

New players should be registered as an enum in `constants/player.py` and all their aliases in `config.py`. In addition to changes in this codebase, we also need to register them in the frontend (profile picture, colors, current tag, etc.).

## Credits

| Contributor       | Role                |
| :---------------- | :------------------ |
| **Steven Truong** | Developer           |
| **Lindsey Wong**  | Unknown Subordinate |
