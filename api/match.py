import logging
import os
import shutil
import traceback
from threading import Thread
from urllib.parse import urlparse

import jsonlines
from flask import request

from config import API_DATA_PATH, MATCH_IDS_PATH, OUT_MIN
from data_providers import api, get_matches
from generate_datasets import generate_datasets
from locks import database_lock
from util import is_valid_tracker_url

logger = logging.getLogger("app")


def all_match_ids():
    match_ids = []
    with open(MATCH_IDS_PATH, mode="r") as f:
        match_ids = [line.rstrip() for line in f]

    return {"match_ids": match_ids}


def add_url():
    if "url" not in request.form:
        return "Missing tracker URL", 400

    # E.g., https://tracker.gg/valorant/match/770f73b1-95db-48ce-94f3-809d5cb5b00d
    tracker_url = request.form["url"].strip()
    if not is_valid_tracker_url(tracker_url):
        return "Invalid tracker URL", 400
    match_id = urlparse(tracker_url).path.split("/")[-1]

    if not database_lock.acquire(block=False):
        return (
            "Currently updating data; please try again in a few seconds",
            423,
        )

    match_ids = []
    with open(MATCH_IDS_PATH, mode="r") as f:
        match_ids = [line.rstrip() for line in f]

    if match_id in match_ids:
        database_lock.release()
        return "Match is already included on the dashboard", 200

    Thread(
        target=add_url_job,
        kwargs={"match_id": match_id},
    ).start()
    return "Add request received", 202


def remove_url():
    if "url" not in request.form:
        return "Missing tracker URL to remove", 400

    # E.g., https://tracker.gg/valorant/match/770f73b1-95db-48ce-94f3-809d5cb5b00d
    tracker_url = request.form["url"].strip()
    if not is_valid_tracker_url(tracker_url):
        return "Invalid tracker URL", 400
    match_id = urlparse(tracker_url).path.split("/")[-1]

    if not database_lock.acquire(block=False):
        return (
            "Currently updating data; please try again in a few seconds",
            423,
        )

    match_ids = []
    with open(MATCH_IDS_PATH, mode="r") as f:
        urls = [line.rstrip() for line in f]

    if match_id not in match_ids:
        return "Match already wasn't included on the dashboard", 404

    Thread(
        target=remove_url_job,
        kwargs={"match_id": match_id},
    ).start()
    return "Remove request received", 202


def add_url_job(match_id: str):
    try:
        logger.info(f"Processing {match_id}")

        logger.info("Begin fetching")
        match_json = api.fetch(match_id)

        logger.info("Updating api-data.jsonl")
        with jsonlines.open(API_DATA_PATH, mode="a") as f:
            f.write(match_json)

        logger.info("Adding URL to match_ids.txt")
        with open(MATCH_IDS_PATH, mode="a") as f:
            f.write(f"{match_id}\n")

        logger.info("Processing updated data")
        matches = get_matches()

        logger.info("Updating out-min")
        generate_datasets(matches=matches, output_dir=OUT_MIN, minified=True)

        logger.info("Successfully added URL")
    except Exception:
        logger.exception(f"Failed to add URL")
    finally:
        database_lock.release()


def remove_url_job(match_id: str):
    try:
        logger.info(f"Removing {match_id}")

        logger.info("Backing up and overwriting match_ids.txt")
        shutil.copy2(MATCH_IDS_PATH, f"{MATCH_IDS_PATH}.old")
        with open(f"{MATCH_IDS_PATH}.old", mode="r") as old:
            with open(MATCH_IDS_PATH, mode="w") as new:
                for url in old:
                    if url.rstrip() != match_id:
                        new.write(url)
        os.remove(f"{MATCH_IDS_PATH}.old")

        logger.info("Backing up and overwriting api-data.jsonl")
        shutil.copy2(API_DATA_PATH, f"{API_DATA_PATH}.old")
        with jsonlines.open(f"{API_DATA_PATH}.old") as old:
            with jsonlines.open(API_DATA_PATH, mode="w") as new:
                for match_json in old:
                    if match_json["metadata"]["matchid"] != match_id:
                        new.write(match_json)
        os.remove(f"{API_DATA_PATH}.old")

        logger.info("Processing updated data")
        matches = get_matches()

        logger.info("Updating out-min")
        generate_datasets(matches=matches, output_dir=OUT_MIN, minified=True)

        logger.info("Successfully removed URL")
    except Exception:
        logger.exception(f"Failed to remove URL: {traceback.format_exc()}")
    finally:
        database_lock.release()
