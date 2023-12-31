from http import HTTPStatus
from typing import Any, Optional

import requests
import urllib3

from league_rpc_linux.colors import Colors
from league_rpc_linux.const import (
    ALL_GAME_DATA_URL,
    BASE_SKIN_URL,
    CHAMPION_NAME_CONVERT_MAP,
    DDRAGON_CHAMPION_DATA,
    GAME_MODE_CONVERT_MAP,
)
from league_rpc_linux.kda import get_gold, get_level
from league_rpc_linux.latest_version import get_latest_version
from league_rpc_linux.polling import wait_until_exists
from league_rpc_linux.username import get_summoner_name

urllib3.disable_warnings()


def get_specific_champion_data(name: str) -> dict[str, Any]:
    response = requests.get(
        url=DDRAGON_CHAMPION_DATA.format_map(
            {"version": get_latest_version(), "name": name}
        ),
        timeout=15,
    )
    return response.json()


def gather_ingame_information() -> tuple[str, str, int, str, int, int]:
    """
    Get the current playing champion name.
    """
    all_game_data_url = ALL_GAME_DATA_URL
    your_summoner_name = get_summoner_name()

    champion_name: str | None = None
    skin_id: int | None = None
    skin_name: str | None = None
    game_mode: str | None = None  # Set if the game mode was never found.. Maybe you are playing something new?
    level: int | None = None
    gold: int | None = None

    if response := wait_until_exists(
        url=all_game_data_url,
        custom_message="Did not find game data.. Will try again in 5 seconds",
    ):
        parsed_data = response.json()
        game_mode = GAME_MODE_CONVERT_MAP.get(
            parsed_data["gameData"]["gameMode"],
            parsed_data["gameData"]["gameMode"],
        )

        if game_mode == "TFT":
            # If the currentGame is TFT.. gather the relevant information
            level = get_level()
        else:
            # If the gamemode is LEAGUE gather the relevant information.
            champion_name, skin_id, skin_name = gather_league_data(
                parsed_data=parsed_data, summoners_name=your_summoner_name
            )
            if game_mode == "Arena":
                level, gold = get_level(), get_gold()
            print("-" * 50)
            if champion_name:
                print(
                    f"{Colors.yellow}Champion name found {Colors.green}({CHAMPION_NAME_CONVERT_MAP.get(champion_name, champion_name)}),{Colors.yellow} continuing..{Colors.reset}"
                )
            if skin_name:
                print(
                    f"{Colors.yellow}Skin detected: {Colors.green}{skin_name},{Colors.yellow} continuing..{Colors.reset}"
                )
            if game_mode:
                print(
                    f"{Colors.yellow}Game mode detected: {Colors.green}{game_mode},{Colors.yellow} continuing..{Colors.reset}"
                )
            print("-" * 50)

    # Returns default values if information was not found.
    return (
        (champion_name or ""),
        (skin_name or ""),
        (skin_id or 0),
        (game_mode or ""),
        (level or 0),
        (gold or 0),
    )


def gather_league_data(
    parsed_data: dict[str, Any],
    summoners_name: str,
) -> tuple[Optional[str], int, Optional[str]]:
    """
    If the gamemode is LEAGUE, gather the relevant information and return it to RPC.
    """
    champion_name: Optional[str] = None
    skin_id: int = 0
    skin_name: Optional[str] = None

    skin_ids = []

    for player in parsed_data["allPlayers"]:
        if player["summonerName"] == summoners_name:
            raw_champion_name = player["rawChampionName"].split("_")[-1]
            champion_data = get_specific_champion_data(name=raw_champion_name)

            champion_name = champion_data["data"][raw_champion_name]["id"]

            skin_id = player["skinID"]

            skin_ids = [
                i["num"] for i in champion_data["data"][raw_champion_name]["skins"]
            ]

            if skin_id:
                while skin_id not in skin_ids:
                    skin_id -= 1

                for i in champion_data["data"][raw_champion_name]["skins"]:
                    if skin_id == i["num"]:
                        skin_name = i["name"]
                        break
            break
        continue
    return champion_name, skin_id, skin_name


def get_skin_asset(
    champion_name: str,
    skin_id: int,
) -> str:
    """
    Returns the URL for the skin/default skin of the champion.
    If a chroma has been selected, it will return the base skin for that chroma.
        Since RIOT does not have individual images for each chroma.
    """

    while skin_id:
        url = f"{BASE_SKIN_URL}{champion_name}_{skin_id}.jpg"
        if not check_url(url):
            skin_id -= 1
            continue
        return url

    url = f"{BASE_SKIN_URL}{champion_name}_0.jpg"
    return url


def check_url(url: str) -> bool:
    """
    Sends a HEAD request to the URL and,
    returns a boolean value depending on if the request,
    was successful (200 OK) or not.
    """
    return requests.head(url, timeout=15).status_code == HTTPStatus.OK
