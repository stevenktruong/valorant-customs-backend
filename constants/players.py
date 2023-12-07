# Player names used as keys in output JSON
from enum import Enum


class PlayerName(str, Enum):
    def __str__(self):
        return self.value

    BRANDON = "brandon"
    BREE = "bree"
    BRIAN = "brian"
    CADE = "cade"
    DARWIN = "darwin"
    ELKE = "elke"
    IRAM = "iram"
    JASON = "jason"
    JOSH = "josh"
    LINDSEY = "lindsey"
    SOPHIE = "sophie"
    STEVE = "steve"
    STEVEN = "steven"
    SUN = "sun"
    SUSI = "susi"
    SUSU = "susu"
    TANG = "tang"
    YANG = "yang"
