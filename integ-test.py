import os
import shutil
import time

from config import MATCH_IDS_PATH
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
        print("--- Attempting to fetch test match data")
        start = time.perf_counter()
        with open(MATCH_IDS_PATH, mode="x") as f:
            f.writelines(map(lambda x: f"{x}\n", TEST_MATCH_IDS))
        fetch_all()
        end = time.perf_counter()
        print(f"Done in {end - start}s")

        print("--- Attempting to parse the match data")
        start = time.perf_counter()
        matches = get_matches()
        end = time.perf_counter()
        print(f"Done in {end - start}s")

        print("--- Attempting to generate datasets")
        start = time.perf_counter()
        os.mkdir("out-min")
        generate_datasets(matches, "out-min")
        end = time.perf_counter()
        print(f"Done in {end - start}s")

        print("Integration test passed. Cleaning up")
    finally:
        os.chdir("..")
        shutil.rmtree(INTEG_TEST_DIR_NAME)
