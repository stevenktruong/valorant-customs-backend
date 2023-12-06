from config import TAG_TO_PLAYER_NAME

# Account identifiers from VALORANT; used for player locations
# Deprecated: tracker.gg uses the `platformUserIdentifier` with the player tag now
# player_ids = {
#     "RujpEbc0IH314j9VAhPjv0pEBI3OU1q5jPlWMRruJGpkeIrt6rk1ZjyklEnNCzaIIhNfxybDmTPS6g": BRANDON,
#     "zVBj-5l3XxSjxwtH-NLvgj-KCcjCNnU8ePJzG1XMn7GbX9D_Z8qUh8wjITvhm69_X0Oa--XluO_vYQ": BREE,
#     "RReD4zGGEQBPZ01t7etkv8VDpaca8kmLMqR9X4t2htNfxLciKXzQUNKc4FBlA5h2a35_65kT6DdIRA": BRIAN,
#     "Bm4jdT7LyDkfAamnd3Pxfr79kkrgW-PDXyYhjnCKlHNhqzBSYa3ObumWCjxk07i9Jm1VA-ogVY86QQ": CADE,
#     "x4VQ1y3s1A4GOSoFjHnYrOuRKUW2nM5B7Lyy-L_1hPEFj-_Wde6ZYN4f2_4uz9t5Ga7XkWZpzZ4Tfw": DARWIN,
#     "Wdp0gZUTzYZCB6mlGYJjb3uVbSHIYIjrDZh3xd__8rMlDIW_Zf44wrjePXBLLya2r6ltYjX6aKH2KQ": ELKE,
#     "C_tY6a_w5RZM-Q4-o4lXmYWyHwR47CdIhc6RqdojrFvYP4__H6fTcEsl9NyeERHG5GhU77fjdPVvaQ": JOSH,
#     "HdmC1fwo6fs0IR5aF8YPr_d8Y9O4mGvLEte-ZobPyIIGY_rgprMUsKVcU1bgNGrO64cY0mVe3wLyIA": LINDSEY,
#     # "cc0hfNaF5_tny7jaSf8N7Bar87EQJt3fLsy85NKGFHBjixtmXfwYgZ9iaIqfaHSwyDvb6HbzOCCuCQ": SEQUENTIAL,
#     "QUesI_kn1ehLlxurIHZtD9Ww-9qESBRQ_RodxkG7q_jWaVB5p7eh1VxnKUiuRmW_ABu8l2Elqr7MtQ": SOPHIE,
#     "g5ab9-AFyFHyaAzvd2E3YDPxyd_o7XMBQ3oMJEKvVcoCdD5DSWijihWgt4lO3RdeQ6glRVQVQZowTQ": STEVE,  # Selintt
#     "9AEt5kjyF3Ho7ZiXaaZA03mCw8_CCF4dP6J8QExrVssTB_5HDXaDhrsgwPzs_Y0o3QVxmN2iqoVpyA": STEVE,  # alomeirca
#     "ocm6y5CVE3L4l1dIcYoyKzZombwCuVx3vP7pqFe79wCdk_oCAUcaJ0mf7MGwK2lGMx4kt9xirfEq6Q": STEVEN,
#     "Ef0d2--EnEXjUkAjOCdoG8l-I6xhsTiwBYfO_hGiNc1ageb7ojel5_ih2GbI68EijY3i_wxgL0_E_A": SUN,  # sun
#     "7c53ICB_o_VMrncGWc3mkMb6T0xS_1m79SFToMdrIGJYSYuccj03anR-tu1Leb8Nb_RQ4qI74hJUkg": SUN,  # sun emoji
#     "QkVviF0Z7UsFptwr0fg-KEMlgbeL7Wg-WpcISvEKUc7CGkBrCt9e1t82Ma7wFwc_CL2Oi0R6Gn0-Fg": SUSI,  # SusTwins
#     "io1l9zvfIf2_bH7FBZ0r6P3TJDWrNBisCwSN7NjyXAzasL-_W6FuhMGWfFNZZWDGRy8TI7g4hxw4hA": SUSI,  # Susi sushiserver
#     "0JBuaLG15FiA7fEkE3ps24-anUziLtNoowIDmEV7ZBH5wu8gwojY3LKKYtAbKJM90UJY9Tmg7OhLwQ": SUSU,
#     "LISiqRtWZpeNmJqirqfyBDFfgTMUNHFz-TuTmNqCGZ4OZSnHcx20SnJc1mDG28w40LHbkCO6ftm3YA": TANG,
#     "fxBAnDFK0NgQ00iLw-G2hML2r4E3HAV11OIb-DTCMm77OHfSPogllCktnjup6AglEp2RrNNcgzWdYQ": YANG,
# }


def username_to_name(username):
    if username in TAG_TO_PLAYER_NAME:
        return TAG_TO_PLAYER_NAME[username].value
    else:
        return username


def side(team: str, round: int):
    if round < 13:
        return "attackers" if team == "red" else "defenders"
    else:
        return "attackers" if team == "blue" else "defenders"
