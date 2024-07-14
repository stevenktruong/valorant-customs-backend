from enum import Enum


class Team(str, Enum):
    def __str__(self):
        return self.value

    RED = "red"
    BLUE = "blue"


class Side(str, Enum):
    def __str__(self):
        return self.value

    ATTACKERS = "attackers"
    DEFENDERS = "defenders"


class WinMethod(str, Enum):
    def __str__(self):
        return self.value

    SURRENDER = "surrender"
    ELIMINIATION = "elimination"
    DEFUSE = "defuse"
    DETONATE = "detonate"
    TIME = "time"


# Keys for coordinate transformation JSON
X_COEFFICIENT = "x_coefficient"
Y_COEFFICIENT = "y_coefficient"
X_SHIFT = "x_shift"
Y_SHIFT = "y_shift"


class RoleName(str, Enum):
    def __str__(self):
        return self.value

    CONTROLLER = "Controller"
    DUELIST = "Duelist"
    INITIATOR = "Initiator"
    SENTINEL = "Sentinel"


class Agent(Enum):
    role_name: RoleName

    def __new__(cls, name, role_name):
        obj = object.__new__(cls)
        obj._value_ = name
        obj.role_name = role_name
        return obj

    def __lt__(self, other):
        if isinstance(other, Agent):
            return self.value < other.value

    def __str__(self):
        return self.value

    ASTRA = "Astra", RoleName.CONTROLLER
    BREACH = "Breach", RoleName.INITIATOR
    BRIMSTONE = "Brimstone", RoleName.CONTROLLER
    CHAMBER = "Chamber", RoleName.SENTINEL
    CLOVE = "Clove", RoleName.CONTROLLER
    CYPHER = "Cypher", RoleName.SENTINEL
    DEADLOCK = "Deadlock", RoleName.SENTINEL
    FADE = "Fade", RoleName.INITIATOR
    GEKKO = "Gekko", RoleName.INITIATOR
    HARBOR = "Harbor", RoleName.CONTROLLER
    ISO = "Iso", RoleName.DUELIST
    JETT = "Jett", RoleName.DUELIST
    KAYO = "KAY/O", RoleName.INITIATOR
    KILLJOY = "Killjoy", RoleName.SENTINEL
    NEON = "Neon", RoleName.DUELIST
    OMEN = "Omen", RoleName.CONTROLLER
    PHOENIX = "Phoenix", RoleName.DUELIST
    RAZE = "Raze", RoleName.DUELIST
    REYNA = "Reyna", RoleName.DUELIST
    SAGE = "Sage", RoleName.SENTINEL
    SKYE = "Skye", RoleName.INITIATOR
    SOVA = "Sova", RoleName.INITIATOR
    VIPER = "Viper", RoleName.CONTROLLER
    YORU = "Yoru", RoleName.DUELIST


class MapName(str, Enum):
    def __str__(self):
        return self.value

    ABYSS = "Abyss"
    ASCENT = "Ascent"
    BIND = "Bind"
    BREEZE = "Breeze"
    FRACTURE = "Fracture"
    HAVEN = "Haven"
    ICEBOX = "Icebox"
    LOTUS = "Lotus"
    PEARL = "Pearl"
    SPLIT = "Split"
    SUNSET = "Sunset"


# Linear transformations are from https://valorant-api.com/v1/maps
COORDINATE_TRANSFORMATIONS: dict[MapName, dict[str, float]] = {
    MapName.ASCENT: {
        X_COEFFICIENT: 8.1e-05,
        Y_COEFFICIENT: -8.1e-05,
        X_SHIFT: 0.5,
        Y_SHIFT: 0.5,
    },
    MapName.SPLIT: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.842188,
        Y_SHIFT: 0.697578,
    },
    MapName.FRACTURE: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.556952,
        Y_SHIFT: 1.155886,
    },
    MapName.BIND: {
        X_COEFFICIENT: 5.9e-05,
        Y_COEFFICIENT: -5.9e-05,
        X_SHIFT: 0.576941,
        Y_SHIFT: 0.967566,
    },
    MapName.BREEZE: {
        X_COEFFICIENT: 7e-05,
        Y_COEFFICIENT: -7e-05,
        X_SHIFT: 0.465123,
        Y_SHIFT: 0.833078,
    },
    MapName.LOTUS: {
        X_COEFFICIENT: 7.2e-05,
        Y_COEFFICIENT: -7.2e-05,
        X_SHIFT: 0.454789,
        Y_SHIFT: 0.917752,
    },
    MapName.SUNSET: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.5,
        Y_SHIFT: 0.515625,
    },
    MapName.PEARL: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.480469,
        Y_SHIFT: 0.916016,
    },
    MapName.ICEBOX: {
        X_COEFFICIENT: 7.2e-05,
        Y_COEFFICIENT: -7.2e-05,
        X_SHIFT: 0.460214,
        Y_SHIFT: 0.304687,
    },
    MapName.HAVEN: {
        X_COEFFICIENT: 7.5e-05,
        Y_COEFFICIENT: -7.5e-05,
        X_SHIFT: 1.09345,
        Y_SHIFT: 0.642728,
    },
}
