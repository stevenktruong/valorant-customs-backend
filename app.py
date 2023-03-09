import atexit
import logging
import time
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

if not os.path.exists("out"):
    os.mkdir("out")

if not os.path.exists("out-min"):
    os.mkdir("out-min")

# Make sure out-min is populated before starting the server
app.logger.info("Initializing datasets")
scrape_all()
process_scrape()
generate_datasets(output_dir="./out-min", minified=True)
app.logger.info("Done. Starting Flask app")

# TODO: Cron job

app.add_url_rule(
    "/api/dashboard",
    view_func=get.dashboard,
    methods=["GET"],
)
app.add_url_rule(
    "/api/wall-of-shame",
    view_func=get.wall_of_shame,
    methods=["GET"],
)

app.add_url_rule("/api/add", view_func=put.add_url, methods=["PUT"])
