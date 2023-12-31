"""
This module contains the fields for extracting information from /lol-lobby/v2/lobby
"""


class LolLobbyLobbyGameConfigDto:
    ALLOWABLE_PREMADE_SIZES = "allowablePremadeSizes"
    CUSTOM_LOBBY_NAME = "customLobbyName"
    CUSTOM_MUTATOR_NAME = "customMutatorName"
    CUSTOM_REWARDS_DISABLED_REASONS = "customRewardsDisabledReasons"
    CUSTOM_SPECTATOR_POLICY = "customSpectatorPolicy"
    CUSTOM_SPECTATORS = "customSpectators"
    CUSTOM_TEAM100 = "customTeam100"
    CUSTOM_TEAM200 = "customTeam200"
    GAME_MODE = "gameMode"
    IS_CUSTOM = "isCustom"
    IS_LOBBY_FULL = "isLobbyFull"
    IS_TEAM_BUILDER_MANAGED = "isTeamBuilderManaged"
    MAP_ID = "mapId"
    MAX_HUMAN_PLAYERS = "maxHumanPlayers"
    MAX_LOBBY_SIZE = "maxLobbySize"
    MAX_TEAM_SIZE = "maxTeamSize"
    PICK_TYPE = "pickType"
    PREMADE_SIZE_ALLOWED = "premadeSizeAllowed"
    QUEUE_ID = "queueId"
    SHOW_POSITION_SELECTOR = "showPositionSelector"


class LolLobbyLobbyParticipantDto:
    ALLOWED_CHANGE_ACTIVITY = "allowedChangeActivity"
    ALLOWED_INVITE_OTHERS = "allowedInviteOthers"
    ALLOWED_KICK_OTHERS = "allowedKickOthers"
    ALLOWED_START_ACTIVITY = "allowedStartActivity"
    ALLOWED_TOGGLE_INVITE = "allowedToggleInvite"
    AUTO_FILL_ELIGIBLE = "autoFillEligible"
    AUTO_FILL_PROTECTED_FOR_PROMOS = "autoFillProtectedForPromos"
    AUTO_FILL_PROTECTED_FOR_SOLOING = "autoFillProtectedForSoloing"
    AUTO_FILL_PROTECTED_FOR_STREAKING = "autoFillProtectedForStreaking"
    BOT_CHAMPION_ID = "botChampionId"
    BOT_DIFFICULTY = "botDifficulty"
    BOT_ID = "botId"
    FIRST_POSITION_PREFERENCE = "firstPositionPreference"
    IS_BOT = "isBot"
    IS_LEADER = "isLeader"
    IS_SPECTATOR = "isSpectator"
    PUUID = "puuid"
    READY = "ready"
    SECOND_POSITION_PREFERENCE = "secondPositionPreference"
    SHOW_GHOSTED_BANNER = "showGhostedBanner"
    SUMMONER_ICON_ID = "summonerIconId"
    SUMMONER_ID = "summonerId"
    SUMMONER_INTERNAL_NAME = "summonerInternalName"
    SUMMONER_LEVEL = "summonerLevel"
    SUMMONER_NAME = "summonerName"
    TEAM_ID = "teamId"


class LolLobbyEligibilityRestriction:
    EXPIRED_TIMESTAMP = "expiredTimestamp"
    RESTRICTION_ARGS = "restrictionArgs"
    RESTRICTION_CODE = "restrictionCode"
    SUMMONER_IDS = "summonerIds"
    SUMMONER_IDS_STRING = "summonerIdsString"


class LolLobbyLobbyDto:
    CAN_START_ACTIVITY = "canStartActivity"
    CHAT_ROOM_ID = "chatRoomId"
    CHAT_ROOM_KEY = "chatRoomKey"
    GAME_CONFIG = "gameConfig"
    INVITATIONS = "invitations"
    LOCAL_MEMBER = "localMember"
    MEMBERS = "members"
    PARTY_ID = "partyId"
    PARTY_TYPE = "partyType"
    RESTRICTIONS = "restrictions"
    WARNINGS = "warnings"
