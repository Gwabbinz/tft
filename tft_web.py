import requests
import time
import pytz
import json
from datetime import datetime, timezone

# Min API key
API_KEY = "RGAPI-0ef808f7-db8d-4671-a04b-d5c8950e10b3"

# URLs
ACCOUNT_URL = "https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
MATCH_HISTORY_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids"
MATCH_INFO_URL = "https://europe.api.riotgames.com/tft/match/v1/matches/{matchId}"


def save_scores_to_file(scores, filename="Desktop/game-data.json"):
    """Save scores to a JSON file."""
    with open(filename, "w") as file:
        json.dump(scores, file, indent=4)


def load_scores_from_file(filename="Desktop/game-data.json"):
    """Load scores from a JSON file."""
    try:
        with open(filename, "r") as file:
            content = file.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_account_info(game_name, tag_line):
    url = ACCOUNT_URL.format(gameName=game_name, tagLine=tag_line)
    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Account details including PUUID
    else:
        print(f"Error fetching account info: {response.status_code}")
        print(response.json())
        return None


def get_match_history(puuid, count=10):
    url = f"{MATCH_HISTORY_URL}?count={count}".format(puuid=puuid)
    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # List of match IDs
    else:
        print(f"Error fetching match history: {response.status_code}")
        print(response.json())
        return None


def get_match_info(match_id):
    url = MATCH_INFO_URL.format(matchId=match_id)
    headers = {"X-Riot-Token": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Match details
    else:
        print(f"Error fetching match info: {response.status_code}")
        print(response.json())
        return None


def extract_player_stats(match_info, target_puuid):
    """
    Extract placement, most-used trait, and time before elimination for a specific player.
    """
    participants = match_info["info"]["participants"]
    for participant in participants:
        if participant["puuid"] == target_puuid:
            # Extract relevant fields
            placement = participant["placement"]
            time_eliminated = participant["time_eliminated"]
            
            # Find the most-used trait
            traits = participant["traits"]
            if traits:
                most_used_trait = max(traits, key=lambda t: t["num_units"])
                most_used_trait_name = most_used_trait["name"]
            else:
                most_used_trait_name = "No traits used"

            return {
                "placement": placement,
                "most_used_trait": most_used_trait_name,
                "time_eliminated": time_eliminated,
            }
    return None


trait_mapping = {
    "TFT13_Rebel": "Rebel",
    "TFT13_Challenger": "Quickstrikers",
    "TFT13_Martialist": "Artillerist",
    "TFT13_FormSwapper": "FormSwapper",
    "TFT13_Ambassador": "Emissary",
    "TFT13_Pugilist": "PitFighter",
    "TFT13_Invoker": "Visionary",
    "TFT13_Scrap": "Scrap",
    "TFT13_Cabal": "BlackRose",
    "TFT13_Bruiser": "Bruiser",
    "TFT13_Sorcerer": "Sorcerer",
    "TFT13_Titan": "Sentinel",
    "TFT13_Warband": "Conqueror",
    "TFT13_Ambusher": "Ambusher",
    "TFT13_BloodHunter": "Warwich",
    "TFT13_Academy": "Academy",
    "TFT13_Infused": "Dominator"
}


def map_traits(riot_trait):
    return trait_mapping.get(riot_trait, riot_trait)


if __name__ == "__main__":
    accounts = [
        {"game_name": "HC999", "tag_line": "EUW"},
    {"game_name": "FireFreak12", "tag_line": "EUW"},
    {"game_name": "HiddenShadow", "tag_line": "Hello"},
    {"game_name": "Shachomo", "tag_line": "EUW"},
    {"game_name": "DanTheIntern", "tag_line": "EUW"},
    {"game_name": "Ulle fra campen", "tag_line": "888"},
    {"game_name": "Numsedask", "tag_line": "EUW"},
    {"game_name": "Mof fra campen", "tag_line": "EUW"},
    {"game_name": "Cg112", "tag_line": "EUNE"},
    {"game_name": "Smokeman7", "tag_line": "EUW"}
    ]

    game_ids = load_scores_from_file()  # Load existing game IDs

    while True:
        for account in accounts:
            game_name = account["game_name"]
            tag_line = account["tag_line"]

            # Step 1: Fetch account info
            account_info = get_account_info(game_name, tag_line)
            if account_info:
                puuid = account_info["puuid"]

                # Step 2: Fetch match history
                match_history = get_match_history(puuid, count=10)
                if match_history:
                    for match_id in match_history:
                        # Check if this game_id already exists for the specific user
                        existing_ids = [entry['match_id'] for entry in game_ids.get(game_name, [])]
                        if match_id in existing_ids:
                            continue

                                
                        match_info = get_match_info(match_id)
                        time.sleep(1)
                        if match_info:
                            player_stats = extract_player_stats(match_info, puuid)

                            # Prepare timestamp for score
                            utc_timestamp = match_info["info"]["game_datetime"]
                            if utc_timestamp > 1000000000000:
                                utc_timestamp = utc_timestamp / 1000

                            utc_time = datetime.fromtimestamp(utc_timestamp, tz=timezone.utc)
                            european_time = utc_time.astimezone(pytz.timezone('Europe/Paris'))
                            formatted_time = european_time.strftime('%d %b - %H:%M')

                            # Prepare score entry
                            if game_name not in game_ids:
                                game_ids[game_name] = []
                            game_ids[game_name].append({
                                "match_id": match_id,
                                "placement": player_stats["placement"],
                                "most_used_trait": map_traits(player_stats["most_used_trait"]),
                                "timestamp": formatted_time,
                            })

                            # Save updated game IDs to file
                            save_scores_to_file(game_ids)

                            print(f"Updated scores for {game_name}: {game_ids[game_name]}")
        time.sleep(120)
