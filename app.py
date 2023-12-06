import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_cors import CORS

import api
from config import CONFIG_PATH, MATCH_IDS_PATH, OUT_MIN, OUT_MIN_DASHBOARD_PATH
from data_providers import fetch_all, get_matches
from generate_datasets import generate_datasets
from locks import database_lock

app = Flask(__name__)
CORS(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


def refresh_datasets():
    app.logger.info("Refreshing datasets")
    with database_lock:
        fetch_all()
        matches = get_matches()
        generate_datasets(matches=matches, output_dir=OUT_MIN, minified=True)
    app.logger.info("Done")


# Make sure out-min is populated before starting the server and
# refresh the dataset if match-ids.txt or config.py is newer than the
# last refreshed dataset.
if not os.path.exists(OUT_MIN):
    os.mkdir(OUT_MIN)

if (
    not os.path.exists(OUT_MIN_DASHBOARD_PATH)
    or (os.path.getmtime(OUT_MIN_DASHBOARD_PATH) < os.path.getmtime(MATCH_IDS_PATH))
    or os.path.getmtime(CONFIG_PATH) < os.path.getmtime(MATCH_IDS_PATH)
):
    refresh_datasets()

# Refresh datasets every midnight
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_datasets, "cron", day="*", hour=0, minute=0, second=0)
scheduler.start()

app.add_url_rule(
    "/dashboard",
    view_func=api.datasets.dashboard,
    methods=["GET"],
)
app.add_url_rule(
    "/wall-of-shame",
    view_func=api.datasets.wall_of_shame,
    methods=["GET"],
)

app.add_url_rule("/match/all", view_func=api.match.all_match_ids, methods=["GET"])
app.add_url_rule("/match", view_func=api.match.add_url, methods=["POST"])
app.add_url_rule("/match", view_func=api.match.remove_url, methods=["DELETE"])
