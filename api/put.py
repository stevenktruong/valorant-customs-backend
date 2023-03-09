import logging
from threading import Thread
from urllib.parse import urlparse
from flask import request
import jsonlines
from locks import database_lock
from generate_datasets import generate_datasets
from process_scrape import process_scrape
from scrape import scrape_url

logger = logging.getLogger("app")


def add_url():
    if "url" not in request.form:
        return "Missing tracker url", 400

    # E.g., https://tracker.gg/valorant/match/770f73b1-95db-48ce-94f3-809d5cb5b00d
    url = urlparse(request.form["url"])
    if url.hostname != "tracker.gg":
        return "Invalid tracker url", 400

    if not database_lock.acquire(block=False):
        return (
            "Currently updating data; please try again in a few seconds",
            423,
        )

    urls = []
    with open("./tracker-urls.txt", mode="r") as f:
        urls = [line.rstrip() for line in f]
        f.close()

    if url.geturl() in urls:
        database_lock.release()
        return "Match is already included on the dashboard", 200

    Thread(
        target=process_url,
        kwargs={"url": url.geturl()},
    ).start()
    return "Request received", 202


def process_url(url: str):
    try:
        logger.info(f"Processing {url}")

        logger.info("Begin scraping")
        match_json = scrape_url(url)

        logger.info("Updating scrape.jsonl")
        with jsonlines.open("./scrape.jsonl", mode="a") as f:
            f.write(match_json)
            f.close()

        logger.info("Adding URL to tracker-urls.txt")
        with open("./tracker-urls.txt", mode="a") as f:
            f.write(f"{url}\n")
            f.close()

        logger.info("Processing scraped data")
        matches_json = process_scrape()

        logger.info("Updating out-min")
        generate_datasets(
            matches_json=matches_json, output_dir="./out-min", minified=True
        )

        logger.info("Successfully processed URL")
    except Exception as e:
        logger.exception("Failed to process URL")
    finally:
        database_lock.release()
