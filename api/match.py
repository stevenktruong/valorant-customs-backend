import logging
import os
import shutil
from threading import Thread
from urllib.parse import urlparse

import jsonlines
from flask import request

from generate_datasets import generate_datasets
from locks import database_lock
from parse_scrape import parse_scrape
from scrape import scrape_url
from util import is_valid_tracker_url

logger = logging.getLogger("app")


def all_urls():
    urls = []
    with open("./tracker-urls.txt", mode="r") as f:
        urls = [line.rstrip() for line in f]
        f.close()

    return {"tracker_urls": urls}


def add_url():
    if "url" not in request.form:
        return "Missing tracker URL", 400

    # E.g., https://tracker.gg/valorant/match/770f73b1-95db-48ce-94f3-809d5cb5b00d
    tracker_url = request.form["url"].strip()
    if not is_valid_tracker_url(tracker_url):
        return "Invalid tracker URL", 400

    if not database_lock.acquire(block=False):
        return (
            "Currently updating data; please try again in a few seconds",
            423,
        )

    urls = []
    with open("./tracker-urls.txt", mode="r") as f:
        urls = [line.rstrip() for line in f]
        f.close()

    if tracker_url in urls:
        database_lock.release()
        return "Match is already included on the dashboard", 200

    Thread(
        target=add_url_job,
        kwargs={"tracker_url": tracker_url},
    ).start()
    return "Add request received", 202


def remove_url():
    if "url" not in request.form:
        return "Missing tracker URL to remove", 400

    # E.g., https://tracker.gg/valorant/match/770f73b1-95db-48ce-94f3-809d5cb5b00d
    tracker_url = request.form["url"].strip()
    if not is_valid_tracker_url(tracker_url):
        return "Invalid tracker URL", 400

    if not database_lock.acquire(block=False):
        return (
            "Currently updating data; please try again in a few seconds",
            423,
        )

    urls = []
    with open("./tracker-urls.txt", mode="r") as f:
        urls = [line.rstrip() for line in f]
        f.close()

    if tracker_url not in urls:
        return "Match already wasn't included on the dashboard", 404

    Thread(
        target=remove_url_job,
        kwargs={"tracker_url": tracker_url},
    ).start()
    return "Remove request received", 202


def add_url_job(tracker_url: str):
    try:
        logger.info(f"Processing {tracker_url}")

        logger.info("Begin scraping")
        match_json = scrape_url(tracker_url)

        logger.info("Updating scrape.jsonl")
        with jsonlines.open("./scrape.jsonl", mode="a") as f:
            f.write(match_json)
            f.close()

        logger.info("Adding URL to tracker-urls.txt")
        with open("./tracker-urls.txt", mode="a") as f:
            f.write(f"{tracker_url}\n")
            f.close()

        logger.info("Processing updated scraped data")
        matches = parse_scrape("./scrape.jsonl")

        logger.info("Updating out-min")
        generate_datasets(matches=matches, output_dir="./out-min", minified=True)

        logger.info("Successfully added URL")
    except Exception as e:
        logger.exception("Failed to add URL")
    finally:
        database_lock.release()


def remove_url_job(tracker_url: str):
    try:
        logger.info(f"Removing {tracker_url}")

        logger.info("Backing up and overwriting tracker-urls.txt")
        shutil.copy2("./tracker-urls.txt", "./tracker-urls.txt.old")
        with open("./tracker-urls.txt.old", mode="r") as old:
            with open("./tracker-urls.txt", mode="w") as new:
                for url in old:
                    if url.rstrip() != tracker_url:
                        new.write(url)
                new.close()
            old.close()
        os.remove("./tracker-urls.txt.old")

        logger.info("Backing up and overwriting scrape.jsonl")
        match_id = urlparse(tracker_url).path.split("/")[-1]
        shutil.copy2("./scrape.jsonl", "./scrape.jsonl.old")
        with jsonlines.open("./scrape.jsonl.old") as old:
            with jsonlines.open("./scrape.jsonl", mode="w") as new:
                for match in old:
                    if match["attributes"]["id"] != match_id:
                        new.write(match)
                old.close()
            new.close()
        os.remove("./scrape.jsonl.old")

        logger.info("Processing updated scraped data")
        matches = parse_scrape("./scrape.jsonl")

        logger.info("Updating out-min")
        generate_datasets(matches=matches, output_dir="./out-min", minified=True)

        logger.info("Successfully removed URL")
    except Exception as e:
        logger.exception("Failed to remove URL")
    finally:
        database_lock.release()
