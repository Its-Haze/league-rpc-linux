from argparse import Namespace
from typing import Any, Optional

from lcu_driver.connection import Connection
from lcu_driver.events.responses import WebsocketEventResponse
from pypresence import Presence

from league_rpc_linux.colors import Colors
from league_rpc_linux.lcu_api.base_data import gather_base_data
from league_rpc_linux.models.client_data import ArenaStats, RankedStats, TFTStats
from league_rpc_linux.models.lcu.current_chat_status import LolChatUser
from league_rpc_linux.models.lcu.current_lobby import (
    LolLobbyLobbyDto,
    LolLobbyLobbyGameConfigDto,
)
from league_rpc_linux.models.lcu.current_queue import LolGameQueuesQueue
from league_rpc_linux.models.lcu.current_summoner import Summoner
from league_rpc_linux.models.module_data import ModuleData
from league_rpc_linux.models.rpc_updater import RPCUpdater

module_data = ModuleData()
rpc_updater = RPCUpdater()

## WS Events ##


@module_data.connector.ready  # type:ignore
async def connect(connection: Connection):
    print(
        f"{Colors.green}Successfully connected to the League Client API.{Colors.reset}"
    )

    print(f"\n{Colors.orange}Gathering base data.{Colors.reset}")
    await gather_base_data(connection, module_data)

    print(f"{Colors.green}Successfully gathered base data.{Colors.reset}")

    print(f"\n{Colors.orange}Updating Discord rpc with base data{Colors.reset}")
    rpc_updater.delay_update(module_data)
    print(f"{Colors.green}Discord RPC successfully updated{Colors.reset}")

    print(f"\n{Colors.cyan}LeagueRPC is ready{Colors.reset}")


@module_data.connector.close  # type:ignore
async def disconnect(_: Connection):
    print(f"{Colors.red}Disconnected from the League Client API.{Colors.reset}")


@module_data.connector.ws.register(  # type:ignore
    "/lol-summoner/v1/current-summoner", event_types=("UPDATE",)
)
async def summoner_updated(_: Connection, event: WebsocketEventResponse) -> None:
    data = module_data.client_data
    event_data: dict[str, Any] = event.data  # type:ignore

    data.summoner_name = event_data[Summoner.DISPLAY_NAME]
    data.summoner_level = event_data[Summoner.SUMMONER_LEVEL]
    data.summoner_id = event_data[Summoner.SUMMONER_ID]
    data.summoner_icon = event_data[Summoner.PROFILE_ICON_ID]

    rpc_updater.delay_update(module_data)


@module_data.connector.ws.register(  # type:ignore
    "/lol-chat/v1/me", event_types=("UPDATE",)
)
async def chat_updated(_: Connection, event: WebsocketEventResponse) -> None:
    data = module_data.client_data
    event_data: dict[str, Any] = event.data  # type:ignore

    match event_data[LolChatUser.AVAILABILITY]:
        case LolChatUser.CHAT:
            data.availability = LolChatUser.ONLINE.capitalize()

        case LolChatUser.AWAY:
            data.availability = LolChatUser.AWAY.capitalize()
        case _:
            ...
    rpc_updater.delay_update(module_data)


@module_data.connector.ws.register(  # type:ignore
    "/lol-gameflow/v1/gameflow-phase", event_types=("UPDATE",)
)
async def gameflow_phase_updated(_: Connection, event: WebsocketEventResponse) -> None:
    data = module_data.client_data
    event_data: Any = event.data  # type:ignore

    data.gameflow_phase = event_data  # returns plain string of the phase
    rpc_updater.delay_update(module_data)


# could be used for lobby instead: /lol-gameflow/v1/gameflow-metadata/player-status
@module_data.connector.ws.register(  # type:ignore
    "/lol-lobby/v2/lobby", event_types=("UPDATE", "CREATE", "DELETE")
)
async def in_lobby(connection: Connection, event: WebsocketEventResponse) -> None:
    data = module_data.client_data
    event_data: Optional[dict[str, Any]] = event.data  # type:ignore

    if event_data is None:
        # Make an early return if data is not present in the event.
        return

    data.queue_id = int(
        event_data[LolLobbyLobbyDto.GAME_CONFIG][
            LolLobbyLobbyGameConfigDto.QUEUE_ID
        ]  # type:ignore
    )
    data.lobby_id = event_data[LolLobbyLobbyDto.PARTY_ID]
    data.players = len(event_data[LolLobbyLobbyDto.MEMBERS])  # type:ignore
    data.max_players = int(
        event_data[LolLobbyLobbyDto.GAME_CONFIG][  # type:ignore
            LolLobbyLobbyGameConfigDto.MAX_LOBBY_SIZE
        ]
    )
    data.map_id = event_data[LolLobbyLobbyDto.GAME_CONFIG][
        LolLobbyLobbyGameConfigDto.MAP_ID
    ]
    data.gamemode = event_data[LolLobbyLobbyDto.GAME_CONFIG][
        LolLobbyLobbyGameConfigDto.GAME_MODE
    ]
    data.is_custom = event_data[LolLobbyLobbyDto.GAME_CONFIG][
        LolLobbyLobbyGameConfigDto.IS_CUSTOM
    ]
    if (
        event_data[LolLobbyLobbyDto.GAME_CONFIG][LolLobbyLobbyGameConfigDto.GAME_MODE]
        == "PRACTICETOOL"
    ):
        data.is_practice = True
        data.max_players = 1
    else:
        data.is_practice = False

    if data.queue_id == -1:
        # custom game / practice tool / tutorial lobby
        if data.is_practice:
            data.queue = "Practice Tool"
        else:
            data.queue = "Custom Game"
        rpc_updater.delay_update(module_data)
        return

    lobby_queue_info_raw = await connection.request(
        "GET", "/lol-game-queues/v1/queues/{id}".format_map({"id": data.queue_id})
    )
    lobby_queue_info = await lobby_queue_info_raw.json()

    data.queue = lobby_queue_info[LolGameQueuesQueue.NAME]
    data.queue_type = lobby_queue_info[LolGameQueuesQueue.TYPE]
    data.queue_is_ranked = lobby_queue_info[LolGameQueuesQueue.IS_RANKED]

    rpc_updater.delay_update(module_data)


# ranked stats
@module_data.connector.ws.register(  # type:ignore
    "/lol-ranked/v1/current-ranked-stats", event_types=("UPDATE",)
)
async def ranked(_: Connection, event: WebsocketEventResponse) -> None:
    data = module_data.client_data
    event_data: dict[str, Any] = event.data  # type:ignore

    data.summoner_rank = RankedStats.from_map(
        obj_map=event_data,
        ranked_type="RANKED_SOLO_5x5",
    )
    data.summoner_rank_flex = RankedStats.from_map(
        obj_map=event_data,
        ranked_type="RANKED_FLEX_SR",
    )

    data.arena_rank = ArenaStats.from_map(obj_map=event_data)
    data.tft_rank = TFTStats.from_map(obj_map=event_data)

    rpc_updater.delay_update(module_data)


###### Debug ######
# This will catch all events and print them to the console.

# @module_data.connector.ws.register(  # type:ignore
#    "/", event_types=("UPDATE", "CREATE", "DELETE")
# )
# async def debug(connection: Connection, event: WebsocketEventResponse) -> None:
#    print(f"DEBUG - {event.type}: {event.uri}")


def start_connector(rpc_from_main: Presence, cli_args: Namespace) -> None:
    module_data.rpc = rpc_from_main
    module_data.cli_args = cli_args
    module_data.connector.start()
