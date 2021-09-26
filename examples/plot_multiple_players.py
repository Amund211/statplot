#!/usr/bin/env python3
"""
Plot the stats of multiple players in a single graph and saves it to `IMAGES_DIR`
Usage:
    python3 plot_multiple_players.py <stat_type> <uuid1> ... <uuidN>

Run `python3 plot_multiple_players.py` to see a list of all avaliable stat types
"""
import sys
from pathlib import Path
from typing import Callable, Union

import matplotlib.pyplot as plt
from asyncpixel.models import Player

from statplot.data_getters import DirTreeIsoJson
from statplot.players import get_username
from statplot.plotting import add_heads_to_legend

current_dir = Path(__file__).parent
HEAD_DIR = current_dir / "heads"
DATA_DIR = current_dir / "downloaded_data"
IMAGES_DIR = current_dir / "images"
USERNAME_CACHE_PATH = current_dir / "username_cache.json"

store = DirTreeIsoJson(DATA_DIR)


class AllTime:
    def __getattr__(self, name):
        return self

    def __int__(self):
        return 0


def div(dividend, divisor):
    if dividend == 0:
        return 0
    elif divisor == 0:
        return dividend
    else:
        return dividend / divisor


EZLVLCOST = {1: 500, 2: 1000, 3: 2000, 4: 3500}

EZXP = sum(EZLVLCOST.values())
EZLVLS = len(EZLVLCOST)

PRESTIGEXP = EZXP + 96 * 5000


def bw_star_from_exp(exp):
    exp += 500  # You don't have to level up to level 1
    prestiges = int(exp // PRESTIGEXP)
    progressxp = int(exp % PRESTIGEXP)
    if progressxp >= EZXP:
        progressxp -= EZXP
        progresslvls = EZLVLS + progressxp // 5000
        return progresslvls + prestiges * 100
    else:
        progresslvls = 0
        for lvl in range(1, EZLVLS + 1):
            # lvls 1,2,3,4 require different amounts of exp
            if progressxp >= EZLVLCOST[lvl]:
                progresslvls += 1
                progressxp -= EZLVLCOST[lvl]
            else:
                return progresslvls + prestiges * 100


# Plot params
fontsize = 12
plt.rcParams.update(
    {
        "text.usetex": False,
        "axes.titlesize": fontsize,
        "axes.labelsize": fontsize,
        "ytick.labelsize": fontsize,
        "xtick.labelsize": fontsize,
        "lines.linewidth": 2,
        # "lines.markersize": 7,
        "lines.markersize": 3,
        "legend.fontsize": fontsize,
        "legend.handlelength": 1.5,
        "figure.figsize": (10, 6),
        "figure.titlesize": 20,
    }
)


def plot_single_player(
    uuid: str, get_stat: Callable[Player, Union[int, float]], session: bool
):
    """
    Plot the stats of the given player

    If session is True, each base stat will be the increase since the first record
    """
    files = store.find_files(uuid)

    data = {
        time: player
        for time, file in files.items()
        if (player := store.get_data(file)) is not None
    }

    if session:
        session_start = data[min(data.keys())]
    else:
        # Mock object that will return 0 for any property so that we get all time stats
        session_start = AllTime()

    date_list = []
    stat_list = []

    for date, player in data.items():
        date_list.append(date)
        stat_list.append(get_stat(player, session_start))

    username = get_username(uuid, USERNAME_CACHE_PATH)
    (artist,) = plt.plot_date(date_list, stat_list, label=username)

    return (artist, uuid)


GET_STAT_MAP = {
    "bwfkdr": lambda p, q: div(
        p.stats.bedwars.final_kills - q.stats.bedwars.final_kills,
        p.stats.bedwars.final_deaths - q.stats.bedwars.final_deaths,
    ),
    "bwfinals": lambda p, q: p.stats.bedwars.final_kills - q.stats.bedwars.final_kills,
    "bwkills": lambda p, q: p.stats.bedwars.kills - q.stats.bedwars.kills,
    "bwbeds": lambda p, q: p.stats.bedwars.beds_broken - q.stats.bedwars.beds_broken,
    "bwstars": lambda p, q: bw_star_from_exp(
        p.raw["stats"]["Bedwars"]["Experience"]
        - q.raw["stats"]["Bedwars"]["Experience"]
    ),
    "bwwlr": lambda p, q: div(
        p.stats.bedwars.wins - q.stats.bedwars.wins,
        p.stats.bedwars.losses - q.stats.bedwars.losses,
    ),
    "bwwinstreak": lambda p, q: p.raw["stats"]["Bedwars"]["winstreak"]
    - q.raw["stats"]["Bedwars"]["winstreak"],
}

TITLE_MAP = {
    "bwfkdr": "Bedwars FKDR",
    "bwfinals": "Bedwars Final Kills",
    "bwkills": "Bedwars Kills",
    "bwbeds": "Bedwars Beds Broken",
    "bwstars": "Bedwars Stars",
    "bwwlr": "Bedwars WLR (wins/loss)",
    "bwwinstreak": "Bedwars Winstreak",
}

assert set(GET_STAT_MAP.keys()) == set(TITLE_MAP.keys())


def main():
    if len(sys.argv) < 2 or (stat_type := sys.argv[1].strip("-")) not in GET_STAT_MAP:
        stat_type_options = "\n\t".join(GET_STAT_MAP.keys())
        print(
            "You must provide a stat type as the first argument. Prepend - for session"
            f"One of\n\t{stat_type_options}",
            file=sys.stderr,
        )
        sys.exit(1)

    session = sys.argv[1].startswith("-")

    uuids = sys.argv[2:]
    get_stat = GET_STAT_MAP[stat_type]
    items = [plot_single_player(uuid, get_stat, session) for uuid in uuids]
    add_heads_to_legend(
        plt.gca(),
        items,
        HEAD_DIR,
        {"pad_width": 2},
    )
    plt.title(("Session " if session else "") + TITLE_MAP[stat_type])
    plt.grid()

    filename = f"{'session' if session else ''}_{stat_type}_{'_'.join(uuids)}.png"
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(IMAGES_DIR / filename))


if __name__ == "__main__":
    main()
