import os
import shutil

from generate_datasets import generate_datasets
from parse_scrape import parse_scrape
from scrape import scrape_all

TEST_URLS = [
    "https://tracker.gg/valorant/match/ec43c688-2e7f-4b1b-93a3-136bd13ef45b",
]

INTEG_TEST_DIR_NAME = "integ-test"

if __name__ == "__main__":
    if os.path.exists(INTEG_TEST_DIR_NAME):
        shutil.rmtree(INTEG_TEST_DIR_NAME)

    os.mkdir(INTEG_TEST_DIR_NAME)
    os.chdir(INTEG_TEST_DIR_NAME)

    try:
        print("Attempting to scrape test URL")
        with open("tracker-urls.txt", mode="x") as f:
            f.writelines(map(lambda x: f"{x}\n", TEST_URLS))
            f.close()
        scrape_all()
        print("Done")

        print("Attempting to parse the scrape")
        matches = parse_scrape("scrape.jsonl")
        print("Done")

        print("Attempting to generate datasets")
        os.mkdir("out-min")
        generate_datasets(matches, "out-min")
        print("Done")

        print("Integration test passed. Cleaning up")
    except Exception as e:
        print(f"Integration test failed: {e}. Cleaning up")
    finally:
        os.chdir("..")
        shutil.rmtree(INTEG_TEST_DIR_NAME)
