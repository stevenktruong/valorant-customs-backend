import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_cors import CORS

import api
from generate_datasets import generate_datasets
from locks import database_lock
from parse_scrape import parse_scrape
from scrape import scrape_all

app = Flask(__name__)
CORS(app)

gunicorn_logger = logging.getLogger("gunicorn.error")
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)


def refresh_datasets():
    app.logger.info("Refreshing datasets")
    with database_lock:
        scrape_all()
        matches = parse_scrape("./scrape.jsonl")
        generate_datasets(matches=matches, output_dir="./out-min", minified=True)
    app.logger.info("Done")


# Make sure out-min is populated before starting the server and
# refresh the dataset if tracker-urls.txt or config.py is newer than the
# last refreshed dataset.
if not os.path.exists("out-min"):
    os.mkdir("out-min")

if (
    not os.path.exists("out-min/dashboard.json")
    or (
        os.path.getmtime("out-min/dashboard.json")
        < os.path.getmtime("tracker-urls.txt")
    )
    or os.path.getmtime("config.py") < os.path.getmtime("tracker-urls.txt")
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

app.add_url_rule("/match/all", view_func=api.match.all_urls, methods=["GET"])
app.add_url_rule("/match", view_func=api.match.add_url, methods=["POST"])
app.add_url_rule("/match", view_func=api.match.remove_url, methods=["DELETE"])
