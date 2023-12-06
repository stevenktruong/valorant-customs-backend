from constants import PlayerName

TAG_TO_PLAYER_NAME: dict[str, PlayerName] = {
    "JHardRTolkien": PlayerName.BRANDON,
    "ThrobbinWilliams": PlayerName.BRANDON,
    "BigBoiB": PlayerName.BRANDON,
    "Brioche": PlayerName.BREE,
    "brianwoohoo": PlayerName.BRIAN,
    "RhythmKing": PlayerName.CADE,
    "Experiment 421": PlayerName.CADE,
    "ChzGorditaCrunch": PlayerName.DARWIN,
    "Jeff Probst": PlayerName.DARWIN,
    "Mirabel Madrigal": PlayerName.DARWIN,
    "Uzumaki 好き": PlayerName.ELKE,
    "NineTailed Fux": PlayerName.ELKE,
    "march 7 inches": PlayerName.IRAM,
    "kingofwallstreet": PlayerName.JASON,
    "wayson": PlayerName.JASON,
    "bot001341": PlayerName.JOSH,
    "aylindsay": PlayerName.LINDSEY,
    "honey butter": PlayerName.LINDSEY,
    "chushberry": PlayerName.SOPHIE,
    "alomeirca": PlayerName.STEVE,
    "mox": PlayerName.STEVE,
    "Selintt": PlayerName.STEVE,
    "spookslayer1": PlayerName.STEVE,
    "youngsmasher": PlayerName.STEVEN,
    "sun": PlayerName.SUN,
    "sun emoji": PlayerName.SUN,
    "Susi sushiserver": PlayerName.SUSI,
    "SusTwins": PlayerName.SUSI,
    "danielscutiegf": PlayerName.SUSU,
    "tangy": PlayerName.TANG,
    "Tyblerone": PlayerName.YANG,
}

# Relative file/folder paths
CONFIG_PATH = "config.py"
MATCH_IDS_PATH = "match-ids.txt"
TRACKER_DATA_PATH = "tracker-data.jsonl"
API_DATA_PATH = "api-data.jsonl"

OUT_MIN = "out-min"
OUT_MIN_DASHBOARD_PATH = f"{OUT_MIN}/dashboard.json"
OUT_MIN_WALL_OF_SHAME_PATH = f"{OUT_MIN}/wall_of_shame.json"

PROXY = None
