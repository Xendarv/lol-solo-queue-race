"""
League of Legends Ranked Progress Tracker

Small side project that tracks ranked Solo Queue progress for a few summoners.
The goal is to make it easy to see progress over time, not to perfectly model MMR.

This pulls data from the Riot Games API, converts rank + LP into a rough numeric
score, stores snapshots in an Excel file, and generates a simple progression chart.

Author: Peter N
"""

import os
from datetime import date

import requests
import pandas as pd
import matplotlib.pyplot as plt


# Basic configuration
API_KEY = "insert API KEY Here"
REGION = "europe"
REGION_1 = "euw1"

# Make sure it is SummonerName/TagLine
SUMMONERS = [
    #"SummonerName/TagLine",
    "Xéndarv/EUW 1",
    "Miyuki Shiba/EUW",
    "Boυnce/EUW",
]

DATA_FILE = "ranked_progress.xlsx"
OUTPUT_IMAGE = "ranked_race.png"


#Iron to Master mapped as 400 intervals
#GM+ has dynamic values but left at 200lp intervals for start of season
#Division offset accounts for 4-1
TIER_BASE = {
    "IRON": 0,
    "BRONZE": 400,
    "SILVER": 800,
    "GOLD": 1200,
    "PLATINUM": 1600,
    "EMERALD": 2000,
    "DIAMOND": 2400,
    "MASTER": 2800,
    "GRANDMASTER": 3000,
    "CHALLENGER": 3200,
}

DIVISION_OFFSET = {
    "IV": 0,
    "III": 100,
    "II": 200,
    "I": 300,
}


def riot_get(url: str) -> dict:
    """Simple wrapper around Riot API GET requests."""
    if not API_KEY:
        raise RuntimeError("RIOT_API_KEY environment variable not set")

    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_summoner_id(summoner_name: str) -> str:
    """Look up the encrypted PUUID Riot uses internally."""
    url = (
        f"https://{REGION}.api.riotgames.com/"
        f"riot/account/v1/accounts/by-riot-id/{summoner_name}"
    )
    print(url)
    print(riot_get(url))
    return riot_get(url)["puuid"]


def get_ranked_info(summoner_id: str) -> dict | None:
    """Return Solo Queue ranked info if available."""
    url = (
        f"https://{REGION_1}.api.riotgames.com/"
        f"lol/league/v4/entries/by-puuid/{summoner_id}"
    )
    entries = riot_get(url)

    for entry in entries:
        if entry["queueType"] == "RANKED_SOLO_5x5":
            return entry

    return None


def rank_to_score(entry: dict) -> int:
    """Convert tier, division, and LP into a single comparable number."""
    tier = entry["tier"]
    rank = entry["rank"]
    lp = entry["leaguePoints"]

    return TIER_BASE[tier] + DIVISION_OFFSET[rank] + lp


def load_existing_data() -> pd.DataFrame:
    """Load previous runs if the file already exists."""
    if os.path.exists(DATA_FILE):
        return pd.read_excel(DATA_FILE)
    return pd.DataFrame()


def save_data(df: pd.DataFrame) -> None:
    """Persist progress data so it can be appended over time."""
    df.to_excel(DATA_FILE, index=False)


def plot_progress(df: pd.DataFrame) -> None:
    """Generate a simple line chart showing ranked progress."""
    if df.empty:
        print("No data available to plot.")
        return

    plt.figure(figsize=(10, 6))

    for summoner in df["summoner"].unique():
        player_df = df[df["summoner"] == summoner]
        plt.plot(
            player_df["date"],
            player_df["score"],
            marker="o",
            label=summoner,
        )

    plt.title("Ranked Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Rank Score")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE)
    plt.close()


def main() -> None:
    today = date.today().isoformat()
    rows = []

    print("Fetching ranked data...")

    for summoner in SUMMONERS:
        summoner_id = get_summoner_id(summoner)
        ranked = get_ranked_info(summoner_id)

        if not ranked:
            print(f"No ranked Solo Queue data for {summoner}")
            continue

        rows.append({
            "date": today,
            "summoner": summoner,
            "tier": ranked["tier"],
            "rank": ranked["rank"],
            "lp": ranked["leaguePoints"],
            "score": rank_to_score(ranked),
        })

    if not rows:
        print("No ranked data collected.")
        return

    new_data = pd.DataFrame(rows)
    existing_data = load_existing_data()
    combined_data = pd.concat([existing_data, new_data], ignore_index=True)

    save_data(combined_data)
    plot_progress(combined_data)

    print("Done.")


if __name__ == "__main__":
    main()
