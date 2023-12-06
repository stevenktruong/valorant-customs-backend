import os
import shutil
from data_providers import fetch_all, get_matches

from generate_datasets import generate_datasets

TEST_MATCH_IDS = [
    "61cc8a7a-fb97-4955-b109-76aab9ae2e3b",
]

INTEG_TEST_DIR_NAME = "integ-test"

if __name__ == "__main__":
    if os.path.exists(INTEG_TEST_DIR_NAME):
        shutil.rmtree(INTEG_TEST_DIR_NAME)

    os.mkdir(INTEG_TEST_DIR_NAME)
    os.chdir(INTEG_TEST_DIR_NAME)

    try:
        print("Attempting to scrape test URL")
        with open("match-ids.txt", mode="x") as f:
            f.writelines(map(lambda x: f"{x}\n", TEST_MATCH_IDS))
            f.close()
        fetch_all()
        print("Done")

        print("Attempting to parse the scrape")
        matches = get_matches()
        print("Done")

        print("Attempting to generate datasets")
        os.mkdir("out-min")
        generate_datasets(matches, "out-min")
        print("Done")

        print("Integration test passed. Cleaning up")
    finally:
        os.chdir("..")
        shutil.rmtree(INTEG_TEST_DIR_NAME)
