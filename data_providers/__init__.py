import time
import jsonlines, os

from data_providers.tracker import TrackerProvider
from data_providers.api import ApiProvider
from Match import Match


def fetch_all():
    """
    Fetch all matches listed in match-ids.txt but not in api-out.jsonl or tracker-data.jsonl.
    """

    api = ApiProvider()

    # Starting from 12/2/23
    match_ids = []
    if os.path.exists("match-ids.txt"):
        with open("match-ids.txt", mode="r") as f:
            match_ids.extend([line.rstrip() for line in f])
        f.close()

    matches = []
    if os.path.exists("api-data.jsonl"):
        with jsonlines.open("api-data.jsonl", mode="r") as f:
            matches.extend([match for match in f])
        f.close()

    if os.path.exists("tracker-data.jsonl"):
        with jsonlines.open("tracker-data.jsonl", mode="r") as f:
            matches.extend([match for match in f])
        f.close()

    for match in matches:
        if match["metadata"]["matchid"] in match_ids:
            match_ids.remove(match["metadata"]["matchid"])

    if len(match_ids) == 0:
        return

    new_matches = []
    for i, match_id in enumerate(match_ids, start=1):
        print(
            f"[{'0' if i <= 9 and len(match_ids) >= 10 else ''}{i}/{len(match_ids)}]: Fetching {match_id}... ",
            end="",
        )
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                time.sleep(2.5)
                match_json = api.fetch(match_id)
                new_matches.append(match_json)

                print("Success")
                break
            except Exception as e:
                if retries == 0:
                    print("Failed")
                    break
                print(e)
                continue

    print("Saving... ", end="")
    with jsonlines.open("api-data.jsonl", mode="a") as f:
        f.write_all(new_matches)
        f.close()
    print("Done")


def get_matches() -> list[Match]:
    """
    Gets a representation of all matches tracked sorted from oldest to newest.

    There are two datasets:
    - tracker-data.jsonl  scraped data from tracker.gg
    - api-data.jsonl      data from the unofficial API

    tracker.gg has been getting better at blocking scrape attempts, so we have
    to migrate over to the unofficial API. This will read both datasets, parse
    them, and merge them.
    """
    api = ApiProvider()
    tracker = TrackerProvider()

    matches_json = []
    if os.path.exists("tracker-data.jsonl"):
        with jsonlines.open("tracker-data.jsonl", mode="r") as f:
            matches_json.extend([tracker.parse(match_json) for match_json in f])
            f.close()

    if os.path.exists("api-data.jsonl"):
        with jsonlines.open("api-data.jsonl", mode="r") as f:
            matches_json.extend([api.parse(match_json) for match_json in f])
            f.close()

    return [Match(match_json) for match_json in matches_json]


# Result from attempting to call the API on 12/3/23, 6:22pm:
# Matches seem to be kept for about 3 months, but there was one on 1/23 that still existed.
# 9026099d-b7ab-4208-bf6d-8427b7c2c062 -- 404
# 1e31a061-81b9-44b4-b4e9-85ba682d4db1 -- 404
# e22f48be-9cfc-4837-ab07-d9260be54d74 -- 404
# e878e0c4-cab8-4a69-99e5-b29f18abc703 -- 404
# 418ce446-f8ea-45c0-98f6-14486358add3 -- 404
# 8a8ec4e8-849a-4a1b-b0fc-ab1490464dcc -- 404
# 1b911cb0-1fb4-4087-9c07-466b9991c8fe -- 404
# bc4f5855-dfbd-4589-905b-4335ca59a130 -- 404
# d29487f4-d110-41bb-9257-f63258364ac3 -- 404
# e4a9cf52-8764-455f-81d7-921e8c8270c2 -- 404
# 59ebc14d-3a1c-40d6-9b8d-7233a288bdce -- 404
# 94b3fc6b-074f-40e1-a2dc-294d68eaddce -- 404
# 387cb7f5-1fe3-4a03-bbba-f95674aa1c10 -- 404
# 873b74bb-f145-4c2d-a49f-12620f81672a -- 404
# f5d502ba-5679-407a-9a13-22abbd824fea -- 404
# 8ee749de-433b-4964-87dc-c13e9e04e904 -- 404
# 507ae798-5f65-443d-9583-497f9a881c7f -- 404
# 3fd2b076-1388-43be-97c7-3ee8d241e241 -- 404
# 741ba201-156c-4f0b-9629-2011ca71ef10 -- 404
# cefa9d9c-1a3f-43bb-aa11-c7622f444f60 -- 404
# 49ff121d-24d9-4905-ae72-d58d0950d1a6 -- 404
# 5855ee79-8347-47ca-ab50-099b9d1b5bc2 -- 404
# 59b8f560-e5ff-4763-b103-0a8a249374ea -- 404
# b84af821-c189-4538-99ac-3086cae68583 -- 404
# 894ecb6a-94ab-4b93-b0e3-c2328d1745de -- 404
# ae45fd0b-e967-4ed3-a8cc-bf35c14e76a2 -- 404
# 72685740-ed00-4125-af65-47d8af2a40bc -- 404
# 6d1465a7-37a3-43c9-a832-bda48012e926 -- 404
# 3d080224-fb11-4ca6-8365-af39f3e7e34a -- 404
# 03b78866-1920-4f2b-a6bc-6da429bc1628 -- 404
# f027ef8a-781e-489f-af88-67c08863d19b -- 404
# a294da99-b803-4326-98c2-da9b30c2e8df -- 404
# 67bfc918-cf0e-4dec-94bb-05e74be59a09 -- 404
# f9fb55cc-b96c-49f3-a02c-9585887bb23f -- 404
# 30014bd6-5637-4883-9943-92aba1999ed9 -- 404
# 0230fd80-2538-4fba-8178-f740af345562 -- 404
# 03824d2a-6b32-47d3-8d92-41aaac4cdecc -- 404
# 731284fb-6e14-40e4-8171-914176f699b2 -- 404
# 6df1e7ff-d33d-4ea9-abd0-e97f33fa5900 -- 404
# 046c8909-4212-4fab-9ad6-26f75e25492a -- 404
# 8293a75b-c366-43cc-840d-da3cadbcdef2 -- 404
# 6c87a77f-488e-4a8a-a0ad-9aa0cd1b808a -- 404
# e8380c75-fe6c-42d6-84f3-78d3f6f88fc4 -- 404
# bf09a9fe-8f9f-41b5-bcbb-6b8301ab26d7 -- 404
# b5909ed7-9e7f-4317-8d84-b08ba97edfa1 -- 404
# 1a525de2-118e-45d9-983e-7c29b8e3d014 -- 404
# 2a5da951-ed3d-4505-a47d-245a1ecd29d8 -- 404
# a5cdf99a-dec4-4c70-87bf-dc0614ec9a72 -- 404
# c23c3452-b57e-4b19-a8dd-f0d8e75ca083 -- 404
# 1130fc3a-89c2-4318-9e4d-3d28824d8292 -- 404
# b82d43e9-5b05-4c1b-a45e-8b357bb9109a -- 404
# 2e0c5bc4-af8a-4044-ba2f-94673f0de9d4 -- 404
# c9930cfa-d79b-4da3-a643-d6a7d1f6c83e -- 200
# 8f2cbb25-fec7-48e7-b3f7-446bf444080c -- 404
# 7fc820f4-9191-4f92-8121-f33a47c046d3 -- 404
# e0e9eba6-c3c9-4963-9fb6-66fb9db1e6af -- 404
# 9cc3048f-e28a-4577-b1c9-fa1a3495ee60 -- 404
# 9eba2d2e-a48f-4b24-b1dd-fce1b779449a -- 404
# 536889a5-d5a2-41d4-be3f-467f81e818ed -- 404
# af80e60b-1b96-40f0-9283-a37e58a34468 -- 404
# 657e3142-f0aa-4b5a-8e7e-e861793efcdf -- 404
# 953472e5-4fc4-42dc-a387-99d3839472c2 -- 404
# 318eae24-0bff-40e7-b819-049770b948b7 -- 404
# faa22e0f-af93-4bb7-9f83-c3d6b60cb32c -- 404
# 7433d77b-cfb1-4194-99b3-4635e67f4c45 -- 404
# ee3039fe-1ee3-4e51-bdb0-bc0219d8cb11 -- 404
# b030f339-0329-49a2-98b2-515961726d92 -- 404
# ef2dd0ae-4fa8-4d27-8ef7-df99b4bf39b8 -- 404
# 11b24d94-a872-4e9d-a9fe-4859c5c21189 -- 404
# 5d04b37c-2253-48bd-aedc-188483157600 -- 404
# 210d3cbd-ddd3-488e-8c02-e098ecb1c3d0 -- 404
# ede12260-15ea-4741-a905-c8591ef2d30c -- 404
# 0746aaef-93f6-4576-9f8b-c91e4789125c -- 404
# c6ef86a1-613f-4f24-9bdf-ee0694f4a80b -- 404
# 1b9c6dfa-1159-44e1-86dc-424e1a3d54f8 -- 404
# 3a0aed4d-8ba2-4adf-be6c-dce876f9e407 -- 404
# d5696cb0-5f0a-48ce-9fc3-bec5b2b8163d -- 404
# b826109c-b845-4677-bf5b-7f0c6385e89e -- 404
# 4c7c4c5f-e929-4557-b353-1693baa1785f -- 404
# c11a8c95-0621-4adc-911d-f3627fc9f1c1 -- 404
# 36ff4933-9919-46c1-988c-20e0cb3fecd7 -- 404
# c2b34a8d-b01b-4aeb-8c0c-0bd6571065c2 -- 404
# 977e29ac-9547-46ef-9350-bfa6082d5ca1 -- 404
# b272a019-b12d-46f2-bf84-dac19e8bb0b1 -- 404
# 6a92a673-4246-445f-a6c8-81798db3bc3a -- 404
# 2b2643a7-490d-4695-af1e-183dd5fb09b0 -- 404
# 53e2516d-62ed-4fcb-a302-4ba0b3ee8b0d -- 404
# b101a483-72fc-4287-ba92-7b4a53cdf477 -- 404
# 8f54a0d2-ee64-4164-8dde-78b6de49283c -- 404
# 761f8a71-c320-462e-8f79-0a72befa6685 -- 404
# 770f73b1-95db-48ce-94f3-809d5cb5b00d -- 404
# 16daa2fe-bbe0-4e3e-a723-7dbffa704b6c -- 404
# 03c65e2d-b05b-46fc-b822-25316d74278b -- 404
# 39213ee4-f33c-4405-b94c-8d2601c6d11d -- 404
# efe64592-b7ef-4124-ac6a-bee0a8ea9c46 -- 404
# f4f10f8e-9c1d-46ce-b037-8c51badc5e46 -- 404
# ac6c7382-e879-45e7-b363-68493951efd1 -- 404
# 130ad8fe-b7c7-4e3d-85f1-24c30900d274 -- 404
# aaaa5b87-1c6c-4c9c-9c3b-b2b4b5611df0 -- 404
# 8855c889-f69c-4415-a463-adef4772c1c4 -- 404
# 6fedfd5b-46f7-4eb2-8430-77d1d0412f0e -- 404
# 9fb502fd-3a91-4d68-a8ee-dcb950b10ed9 -- 404
# df3954eb-ee9b-4ddd-bb2b-2b7d800d4b01 -- 404
# 984816f6-3ccc-48c8-abfd-cd4b64e1e54e -- 404
# 32e6bfb6-4dc4-45e5-9df7-fa04fb7ddf61 -- 404
# f1d8ebe1-5b91-4a67-9bc2-160def5ea7a7 -- 404
# 1086a217-dcbe-49b8-9029-a515d521782e -- 404
# 7ca938b4-38e2-48d9-8e4b-7c7bde0e36e2 -- 404
# 55eecc97-26bc-4c9c-a1d5-b726ebf39900 -- 404
# 49c4060e-cd22-4149-8308-6fb2e7ade6cb -- 404
# 4045bc5d-0cdb-493e-b0f6-96885117ae2b -- 404
# a863ecb3-6d2c-4de9-904d-a39f7e4c7da8 -- 404
# bee79b3f-5f47-4b78-8017-2a5e5c882426 -- 404
# d6df7490-edd5-407c-940a-57aeb6a34424 -- 404
# bbff5b24-96a0-42ce-9982-e14732d7de38 -- 404
# eefd846b-f12f-4fdc-8b2d-1969d679553a -- 404
# 1a087f8d-1dd6-4d24-8981-83c35be2f9cd -- 404
# 36133877-7ddd-4c22-bedf-5adea4400788 -- 404
# 86414d9a-271b-4ca6-835d-130940af3747 -- 404
# f0a14d51-b3e2-4925-a356-06f211ed1dc5 -- 404
# a29901bf-2d75-4227-96bb-64573d06d0c5 -- 404
# 8d2828b9-64ab-4ca0-8950-9a0da9d4e7f2 -- 404
# 2103edc3-a47e-4b47-94b8-efbaacb895ee -- 404
# 53b58245-2f69-4c49-9a1c-975ca73f67b3 -- 404
# afedda77-3a2c-40f2-8735-69a6d4e97f68 -- 404
# a996d6b4-eb28-4b1e-bfe5-02a921a4d540 -- 404
# 280b67ef-4a29-4be0-8bf4-cc530deb5b5f -- 404
# b0668b95-9d3e-4566-9f29-1fa7c3ebf690 -- 404
# c0bb3ab1-7555-457e-9412-403b3cbdccc6 -- 404
# d25e7221-62ac-4a36-bbeb-26c4cc034192 -- 404
# 117f2580-022c-47fa-baa8-e58c6df54b15 -- 404
# 390b57cb-df62-48fd-be66-08b79377b235 -- 404
# 61b3cfe9-bec7-4ded-b2af-c2d9664ac548 -- 404
# ec43c688-2e7f-4b1b-93a3-136bd13ef45b -- 404
# 4a1fecbf-7a73-4995-8135-f1217a7cfac7 -- 404
# 733aaa46-9632-4761-8354-b9063a618e6f -- 404
# 0d3ee71d-b8d6-4e54-9fbf-dde0a1aa3bf7 -- 404
# 9b6efcd1-f960-43f7-80ae-faa53b9a8705 -- 404
# 06c2b633-5573-4bbe-845e-6d3b1f514b8c -- 404
# 7695a1f4-d5a2-4221-ab0e-8a406696372e -- 404
# 52d51706-d2db-49d3-9b31-ab9de73ccb47 -- 200
# cc5e2e14-1d36-4650-bc2d-6bdbbc36bed4 -- 200
# 21313c40-bae9-4c62-a0c7-323f8fd2b907 -- 200
# eec67531-b302-455e-9d61-d22efc3412d1 -- 200
# 46daf41a-ee9c-4a07-9bb3-bc4cee7b142a -- 200
# a33a38ba-809c-47e6-843c-978bbbe7f8b1 -- 404
# 1c4748bd-35bd-4f8f-a3e8-5d0739df6169 -- 200
# 5d876e9b-ecbd-4d71-85ea-f4110d3806d4 -- 200
# a2d7512a-60c3-4835-8958-58944d8c3d70 -- 200
# f272663f-a96a-4ab3-9244-c66b8319cc4d -- 200
# e1a5fa96-1a29-4ac6-9d44-a1cdd3a5cbbc -- 200
# 5cb3e9b2-b906-498d-bdf5-64f155c97870 -- 200
# fcfce360-0978-475d-a8c2-5244344cd921 -- 200
# 05899825-ce5c-4a4d-bfff-a7af1ebd73c5 -- 200
# 22119e5c-d7af-42d8-bd31-2c5315b9e40a -- 200
# b68681f9-108f-4484-a29d-f036c9ee2618 -- 200
# 79827dba-a9c0-4bae-82af-47df6cc5c30a -- 200
# 3e0837bf-66df-4466-bfbd-997b41f35b57 -- 200
# ac42d58e-ae9d-4ec7-9ccc-59d26d7180af -- 200

# TODO: Update server code to start calling API instead.
# - tracker-data.jsonl should never change again
# - maybe separate match-ids.txt into tracker.gg and API files
# - replace the last few tracker-data.jsonl lines to API and make sure the website stats don't change
# - document which match ids were handled by tracker.gg
