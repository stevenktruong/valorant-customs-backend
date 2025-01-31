from jsonlines import jsonlines

purge = [
    "1d80a772-e546-4f41-931a-2892c41c4809",
    "cf145f01-5d9a-4577-bdf7-093db3ec23d9",
    "1b7ac9f8-69ad-48c4-9da0-6c24b429a402",
]

with jsonlines.open("api-data.jsonl", "r") as f:
    with jsonlines.open("api-data-2.jsonl", "w") as out:
        for x in f:
            print(x["metadata"]["matchid"])
            if x["metadata"]["matchid"] not in purge:
                out.write(x)
