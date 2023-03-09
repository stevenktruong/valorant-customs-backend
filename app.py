import logging
import os
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask
from flask_cors import CORS

from api import *
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
        matches_json = process_scrape()
        generate_datasets(
            matches_json=matches_json, output_dir="./out-min", minified=True
        )
    app.logger.info("Done")


# Make sure out-min is populated before starting the server and
# refresh the dataset if tracker-urls.txt is newer than the dataset
if not os.path.exists("out-min"):
    os.mkdir("out-min")

if not os.path.exists("out-min/dashboard.json") or (
    os.path.getmtime("out-min/dashboard.json") < os.path.getmtime("tracker-urls.txt")
):
    refresh_datasets()

# Refresh datasets every midnight
scheduler = BackgroundScheduler()
scheduler.add_job(refresh_datasets, "cron", day="*", hour=0, minute=0, second=0)
scheduler.start()

app.add_url_rule(
    "/dashboard",
    view_func=get.dashboard,
    methods=["GET"],
)
app.add_url_rule(
    "/wall-of-shame",
    view_func=get.wall_of_shame,
    methods=["GET"],
)

app.add_url_rule("/add", view_func=put.add_url, methods=["PUT"])
