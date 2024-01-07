import glob
import os
import sys
import time

import psutil
import pypresence

from league_rpc_linux.colors import Colors


def processes_exists(process_names: list[str]) -> bool:
    """
    Given an array of process names.
    Give a boolean return value if any of the names was a running process in the machine.
    """
    return any(process_exists(process_name) for process_name in process_names)


def process_exists(process_name: str) -> bool:
    """
    Checks if the given process name is running or not.
    """
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def check_league_client_process(wait_for_league: int):
    """
    Checks league client processes.
    """
    league_processes = ["LeagueClient.exe", "LeagueClientUx.exe"]

    print(f"{Colors.yellow}Checking if LeagueClient.exe is running...")
    time.sleep(1)
    if wait_for_league == -1:
        print(
            f"{Colors.yellow}Will wait {Colors.green}indefinitely{Colors.yellow} for League to start... Remember, forever is a long time.. use {Colors.green}CTRL + C{Colors.yellow} if you would like to quit.{Colors.reset}"
        )

    wait_time = 0
    while True:
        if not processes_exists(process_names=league_processes):
            if wait_for_league == -1:
                time.sleep(10)
                continue
            elif wait_time >= wait_for_league:
                print(
                    f"{Colors.red}League Client is not running! Exiting after waiting {wait_for_league} seconds.{Colors.reset}"
                )
                if not wait_for_league:
                    print(
                        f"{Colors.green}Want to add waiting time for League? Use --wait-for-league <seconds>. (-1 = infinite, or until CTRL + C)"
                    )
                sys.exit()
            else:
                print(
                    f"{Colors.yellow}Will wait for League to start. Time left: {wait_for_league - wait_time} seconds..."
                )
                time.sleep(5)
                wait_time += 5
                continue
        break

    print(f"{Colors.green}League client is running!{Colors.dgray}(1/2){Colors.reset}")


def check_discord_process(
    process_names: list[str], client_id: str, wait_for_discord: int
) -> pypresence.Presence:
    """
    Checks if discord process is running.
    Connects to Discord Rich Presence if it is found.
    """
    print(f"{Colors.yellow}Checking if Discord is running...{Colors.reset}")

    look_for_processes = f"({Colors.green}{', '.join(process_names)}{Colors.blue})"

    time.sleep(1)

    if wait_for_discord == -1:
        print(
            f"{Colors.yellow}Will wait {Colors.green}indefinitely{Colors.yellow} for Discord to start... Remember, forever is a long time.. use {Colors.green}CTRL + C{Colors.yellow} if you would like to quit.{Colors.reset}"
        )

    wait_time = 0
    while True:
        if not processes_exists(process_names=process_names):
            if wait_for_discord == -1:
                time.sleep(10)
                continue
            elif wait_time >= wait_for_discord:
                print(
                    f"""{Colors.red}Discord not running!
            {Colors.blue}Could not find any process with the names {look_for_processes} running on your system.
            Is your Discord process named something else? Try --add-process <name>{Colors.reset}"""
                )

                if not wait_for_discord:
                    print(
                        f"{Colors.green}Want to add waiting time for discord? Use --wait-for-discord <seconds>. (-1 = infinite, or until CTRL + C)"
                    )
                sys.exit()
            else:
                print(
                    f"{Colors.yellow}Will wait for Discord to start. Time left: {wait_for_discord - wait_time} seconds..."
                )
                time.sleep(5)
                wait_time += 5
                continue
        break

    print(f"{Colors.green}Discord is running! {Colors.dgray}(2/2){Colors.reset}")

    pipe = 0
    for _ in range(5):
        time.sleep(3)
        try:
            rpc = pypresence.Presence(client_id, pipe=pipe)
            rpc.connect()
            break
        except pypresence.exceptions.InvalidID:
            print(
                f"{Colors.red}Invalid Client ID. Make sure your Discord Application ID is correct."
            )
            sys.exit()
        except pypresence.exceptions.DiscordError:
            # Sometimes when starting discord, an error can occur saying that you logged out.
            # Weird but can be ignored since it usually works a second or so after.
            time.sleep(1)
            continue
        except pypresence.exceptions.DiscordNotFound:
            # Sometimes when starting discord, an error can occur saying that you logged out.
            # Weird but can be ignored since it usually works a second or so after.
            print(
                f"{Colors.red}Pypresence (RPC) Could not find Discord installed and running on this machine."
            )
            sys.exit()
        except pypresence.exceptions.PipeClosed:
            # The pipe was closed. Catch this exception and re-connect your instance
            time.sleep(1)
            continue
        except ConnectionRefusedError:
            ipcs = check_discord_ipc()
            if pipe + 1 < len(ipcs):
               # Failed to connect, retry with next one
               pipe += 1
               continue

            print(
                f"""
            {Colors.red}PyPresence encountered some problems, and could not connect to your Discord's RPC
            {Colors.blue}
            1. One or more of the processes this script was looking for was found {look_for_processes}
                But Pypresence still was unable to detect a running discord-ipc
            2. You may not have a discord ipc running. Try {Colors.reset}``{Colors.green}ls $XDG_RUNTIME_DIR | grep discord-ipc-{Colors.reset}``{Colors.blue} There should only be one result {Colors.reset}``{Colors.green}discord-ipc-0={Colors.reset}``
            {Colors.blue}3. Try restarting Discord. (Make sure the process is stopped before doing that.){Colors.reset}
                """
            )
            # If process names were not found, but ipc exists. Try removing them & restarting
            if len(ipcs) > 1:
                print(
                    f"""
                {Colors.red}Detected multiple ipc's running.{Colors.reset}
                You seem to have more than 1 ipc running (which is unusual).
                If you know that discord is running, but pypresence keep failing to connect.
                It might be cause you have multiple ipc's running. try removing the following ipc's and {Colors.green}restart discord.{Colors.reset}
                {Colors.yellow}ipc's: {' , '.join(ipcs)}{Colors.reset}
                run: ``{Colors.green}rm  {' '.join(ipcs)}{Colors.reset}``
                Or you just don't have discord up and running..
                        """
                )
            print(
                f"{Colors.red}Raising Exception found by PyPresence, and exiting..{Colors.reset}"
            )
            sys.exit()
    else:
        print(
            f"{Colors.red}Discord process was found but RPC could not be connected.{Colors.reset}"
        )
        sys.exit()
    return rpc


def check_discord_ipc() -> list[str]:
    """
    Checks if there are any discord-ipc's running.
    """
    # Path to check for Discord IPC sockets

    xdg_runtime_dir = os.environ.get("XDG_RUNTIME_DIR")

    if not xdg_runtime_dir:
        # If for some reason this environmental variable is not set.. just ignore this function.
        return []

    ipc_pattern = "discord-ipc-*"
    list_of_ipcs: list[str] = []

    for ipc_socket in glob.glob(os.path.join(xdg_runtime_dir, ipc_pattern)):
        if os.path.exists(ipc_socket):
            list_of_ipcs.append(ipc_socket)
    return list_of_ipcs


def player_state() -> str | None:
    """
    Returns the player state
    """
    current_state: str | None = None

    if processes_exists(process_names=["LeagueClient.exe", "LeagueClientUx.exe"]):
        if process_exists("League of Legends.exe"):
            current_state = "InGame"
        else:
            current_state = "InLobby"
    return current_state
