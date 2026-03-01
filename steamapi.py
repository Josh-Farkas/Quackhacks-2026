import os
from dotenv import load_dotenv
import time
import requests
import sys
import threading

STEAM_API_BASE = "https://api.steampowered.com"
UPDATE_PERIOD = 60 * 3 # Seconds

# ── Configuration ──────────────────────────────────────────────────────────────
VANITY_URL = "YOUR_URL_HERE" # Username/vanity URL, e.g. "gaben" (used if STEAM_ID is blank)
GAME_DATA_FILE_NAME = "user_game_data.csv"
# ──────────────────────────────────────────────────────────────────────────────

dirname = os.path.dirname(__file__)
GAME_DATA_PATH = os.path.join(dirname, GAME_DATA_FILE_NAME)

load_dotenv(dotenv_path=os.path.join(dirname, '.env'))
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_ID = os.getenv("STEAM_ID")

def update_env():
    global STEAM_API_KEY, STEAM_ID
    load_dotenv(dotenv_path=os.path.join(dirname, '.env'))
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    STEAM_ID = os.getenv("STEAM_ID")

def resolve_vanity_url(api_key: str, vanity_url: str) -> str:
    """Resolve a Steam vanity URL (username) to a 64-bit SteamID."""
    url = f"{STEAM_API_BASE}/ISteamUser/ResolveVanityURL/v1/"
    params = {"key": api_key, "vanityurl": vanity_url}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json().get("response", {})
    if data.get("success") != 1:
        print(f"Error: Could not resolve vanity URL '{vanity_url}'. Make sure the username is correct.")
        sys.exit(1)
    return data["steamid"]



def get_player_summary(api_key: str, steam_id: str) -> dict:
    """Fetch player summary including current game info."""
    url = f"{STEAM_API_BASE}/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": api_key, "steamids": steam_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    players = response.json().get("response", {}).get("players", [])
    if not players:
        print(f"Error: No player found with SteamID '{steam_id}'.")
        sys.exit(1)
    return players[0]


def get_active_game(api_key: str, steam_id: str) -> None:
    """Print the currently active game for a Steam user."""
    player = get_player_summary(api_key, steam_id)

    persona_name = player.get("personaname", "Unknown")
    game_id = player.get("gameid")
    game_name = player.get("gameextrainfo")

    # print(f"\nSteam User : {persona_name}")
    # print(f"Steam ID   : {steam_id}")
    return {"name": game_name, "id": game_id}


def get_game_and_time(api_key: str, steam_id: str):
    """Return a pair of [timestamp, game name]"""
    return [int(time.time()), get_active_game(api_key, steam_id).get("name")]


def write_game_data_to_file(data_pair, file_path=GAME_DATA_PATH):
    with open(file_path, 'a+') as f:
        f.write(f'{data_pair[0]},{data_pair[1]}\n')


def update():
    data = get_game_and_time(STEAM_API_KEY, STEAM_ID)
    write_game_data_to_file(data, GAME_DATA_PATH)


def steam_polling_loop():
    """Threaded loop to update Steam data"""
    while True:
        update()  # or whatever your update function is
        time.sleep(UPDATE_PERIOD)


def start_steam_polling():
    t = threading.Thread(target=steam_polling_loop, daemon=True)
    t.start()


def main():
    steam_id = STEAM_ID
    if not steam_id:
        print(f"Resolving vanity URL '{VANITY_URL}'...")
        steam_id = resolve_vanity_url(STEAM_API_KEY, VANITY_URL)
    start_steam_polling()



if __name__ == "__main__":
    main()