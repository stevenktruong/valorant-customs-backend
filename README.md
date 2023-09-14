# Valorant Customs Stats

[Dashboard](https://www.valoquestionmark.com/)

## Documentation

### Setup

Before you can run anything, you need to install all dependencies. It's recommended to do this in a virtual environment:

```
python -m venv env
source env/bin/activate
python -m pip install -r requirements.txt
```

After you run this once, next time you only need to run

```
source env/bin/activate
```

before you can use the available scripts.

### Usage

You can start the backend with `gunicorn app:app`. In addition to the API, the backend does the following:

-   On startup, if `tracker-urls.txt` is newer than `out-min/dashboard.json`, the server will automatically update all the datasets.
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

All data is derived from [tracker.gg](https://tracker.gg/valorant) until Riot releases the API for personal use. To scrape the data locally, run `scrape.py`. It will be saved to a huge minified file (~70 MB) called `scrape.jsonl` (instead of pure JSON, each line is a JSON object corresponding to a match). For an example of what each line looks like in a readable format, see `tracker-sample.json`.

Each line is mapped to a `Match` object, which has a developer-friendly API. To see an example of how to use it, see `example.ipynb`.

#### Datasets

From the main scraped data, we generate smaller datasets with derived statistics that we're interested in. Each of these datasets corresponds to a `DatasetGenerator` implementation in `dataset_generators`. Each `DatasetGenerator` needs to implement three methods:

| Method                   | Description                                                                                                                         |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------- |
| `__init__` (constructor) | The argument passed into the superclass constructor is the name of the dataset, e.g., it's used as a key in `dashboard.json`.       |
| `accumulate`             | Processes the next match and updates `out_json` accordingly.                                                                        |
| `finalize`               | Performs any other computations needed to make the dataset, e.g., compute the win rate from the games counted through `accumulate`. |

Once a `DatasetGenerator` is implemented, it needs to be included somewhere in `generate_datasets.py`.

All datasets used for dashboards can be found in the `out-min` directory. To generate them manually, run `generate_datasets.py` to generate all the smaller datasets used by the front-end. They will appear in `out-min`.

### Onboarding Players

New players should be registered in `config.py` (along with a constant in `constants/players.py`). In addition to changes in this codebase, we also need to register them in the frontend (profile picture, colors, current tag, etc.).

### Miscellaneous

In the event that the server is detected as a scraper by tracker.gg, a proxy can be configured in `config.py`.

## Credits

| Contributor       | Role                |
| :---------------- | :------------------ |
| **Steven Truong** | Developer           |
| **Lindsey Wong**  | Unknown Subordinate |
