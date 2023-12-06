import json
from pprint import pprint
from deepdiff import DeepDiff
from data_providers import ApiProvider, TrackerProvider

# Test against samples:
# fcfce360-0978-475d-a8c2-5244344cd921 (knife kills; 30 rounds)
# ac42d58e-ae9d-4ec7-9ccc-59d26d7180af
# 5d876e9b-ecbd-4d71-85ea-f4110d3806d4 (30 rounds)
# 61cc8a7a-fb97-4955-b109-76aab9ae2e3b (timer ran out on a round)

match_id = "61cc8a7a-fb97-4955-b109-76aab9ae2e3b"

api = ApiProvider()
tracker = TrackerProvider()


a = api.parse(json.load(open(f"samples/{match_id}/api.json", mode="r")))
b = tracker.parse(json.load(open(f"samples/{match_id}/tracker.json", mode="r")))

with open("api-out.json", mode="w") as f:
    json.dump(a, f)

with open("tracker-out.json", mode="w") as f:
    json.dump(b, f)

print("Comparing rounds:")
for i in range(len(a["rounds"])):
    print(f"-- {i}")
    f = lambda d: d["rounds"][i]
    pprint(DeepDiff(f(a), f(b), ignore_order=True, math_epsilon=500))
    print()

print("Comparing Red team:")
f = lambda d: d["team_red"]
pprint(DeepDiff(f(a), f(b), ignore_order=True))
print()

print("Comparing Blue team:")
f = lambda d: d["team_blue"]
pprint(DeepDiff(f(a), f(b), ignore_order=True))
print()
