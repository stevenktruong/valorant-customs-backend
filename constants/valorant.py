# Sides
ATTACKERS = "attackers"
DEFENDERS = "defenders"

# Win methods
SURRENDERED = "surrendered"
ELIMINIATION = "elimination"
DEFUSE = "defuse"
DETONATE = "detonate"
TIME = "time"

# Keys for coordinate transformation JSON
X_COEFFICIENT = "x_coefficient"
Y_COEFFICIENT = "y_coefficient"
X_SHIFT = "x_shift"
Y_SHIFT = "y_shift"

# Agent names
ASTRA = "Astra"
BREACH = "Breach"
BRIMSTONE = "Brimstone"
CHAMBER = "Chamber"
CYPHER = "Cypher"
DEADLOCK = "Deadlock"
FADE = "Fade"
GEKKO = "Gekko"
HARBOR = "Harbor"
ISO = "Iso"
JETT = "Jett"
KAYO = "KAY/O"
KILLJOY = "Killjoy"
NEON = "Neon"
OMEN = "Omen"
PHOENIX = "Phoenix"
RAZE = "Raze"
REYNA = "Reyna"
SAGE = "Sage"
SKYE = "Skye"
SOVA = "Sova"
VIPER = "Viper"
YORU = "Yoru"

# Roles
CONTROLLER = "Controller"
DUELIST = "Duelist"
INITIATOR = "Initiator"
SENTINEL = "Sentinel"

# Map names
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

AGENT_NAMES = [
    ASTRA,
    BREACH,
    BRIMSTONE,
    CHAMBER,
    CYPHER,
    DEADLOCK,
    FADE,
    GEKKO,
    HARBOR,
    ISO,
    JETT,
    KAYO,
    KILLJOY,
    NEON,
    OMEN,
    PHOENIX,
    RAZE,
    REYNA,
    SAGE,
    SKYE,
    SOVA,
    VIPER,
    YORU,
]

ROLE_NAMES = [CONTROLLER, DUELIST, INITIATOR, SENTINEL]

AGENT_NAME_TO_ROLE = {
    ASTRA: CONTROLLER,
    BREACH: INITIATOR,
    BRIMSTONE: CONTROLLER,
    CHAMBER: SENTINEL,
    CYPHER: SENTINEL,
    DEADLOCK: SENTINEL,
    FADE: INITIATOR,
    GEKKO: INITIATOR,
    HARBOR: CONTROLLER,
    ISO: DUELIST,
    JETT: DUELIST,
    KAYO: INITIATOR,
    KILLJOY: SENTINEL,
    NEON: DUELIST,
    OMEN: CONTROLLER,
    PHOENIX: DUELIST,
    RAZE: DUELIST,
    REYNA: DUELIST,
    SAGE: SENTINEL,
    SKYE: INITIATOR,
    SOVA: INITIATOR,
    VIPER: CONTROLLER,
    YORU: DUELIST,
}

# All maps
MAP_NAMES = [
    ASCENT,
    BIND,
    BREEZE,
    FRACTURE,
    HAVEN,
    ICEBOX,
    LOTUS,
    PEARL,
    SPLIT,
    SUNSET,
]

# Linear transformations are from https://valorant-api.com/v1/maps
COORDINATE_TRANSFORMATIONS = {
    ASCENT: {
        X_COEFFICIENT: 7e-05,
        Y_COEFFICIENT: -7e-05,
        X_SHIFT: 0.813895,
        Y_SHIFT: 0.573242,
    },
    SPLIT: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.842188,
        Y_SHIFT: 0.697578,
    },
    FRACTURE: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.556952,
        Y_SHIFT: 1.155886,
    },
    BIND: {
        X_COEFFICIENT: 5.9e-05,
        Y_COEFFICIENT: -5.9e-05,
        X_SHIFT: 0.576941,
        Y_SHIFT: 0.967566,
    },
    BREEZE: {
        X_COEFFICIENT: 7e-05,
        Y_COEFFICIENT: -7e-05,
        X_SHIFT: 0.465123,
        Y_SHIFT: 0.833078,
    },
    LOTUS: {
        X_COEFFICIENT: 7.2e-05,
        Y_COEFFICIENT: -7.2e-05,
        X_SHIFT: 0.454789,
        Y_SHIFT: 0.917752,
    },
    SUNSET: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.5,
        Y_SHIFT: 0.515625,
    },
    PEARL: {
        X_COEFFICIENT: 7.8e-05,
        Y_COEFFICIENT: -7.8e-05,
        X_SHIFT: 0.480469,
        Y_SHIFT: 0.916016,
    },
    ICEBOX: {
        X_COEFFICIENT: 7.2e-05,
        Y_COEFFICIENT: -7.2e-05,
        X_SHIFT: 0.460214,
        Y_SHIFT: 0.304687,
    },
    HAVEN: {
        X_COEFFICIENT: 7.5e-05,
        Y_COEFFICIENT: -7.5e-05,
        X_SHIFT: 1.09345,
        Y_SHIFT: 0.642728,
    },
}
