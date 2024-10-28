"""Media player helper functions for Chime TTS."""

import logging
import time
import math
from homeassistant.core import HomeAssistant, State
from homeassistant.const import CONF_ENTITY_ID, SERVICE_VOLUME_SET
from .media_player import ChimeTTSMediaPlayer

from homeassistant.components.media_player.const import (
    ATTR_MEDIA_ANNOUNCE,
    ATTR_GROUP_MEMBERS,
    ATTR_MEDIA_VOLUME_LEVEL,
    SERVICE_JOIN,
    SERVICE_UNJOIN,
)
from ..const import (
    ALEXA_MEDIA_PLAYER_PLATFORM,
    SONOS_PLATFORM,
    SPOTIFY_PLATFORM,
    TRANSITION_STEP_MS
)
from ..config import (
        SONOS_SNAPSHOT_ENABLED,
)
_LOGGER = logging.getLogger(__name__)

class MediaPlayerHelper:
    """Media player helper functions for Chime TTS."""

    media_players: list[ChimeTTSMediaPlayer] = []
    joined_media_player_entity_ids: list[str] = []
    unjoined_media_player_entity_ids: list[str] = []
    join_players: bool = False
    unjoin_players: bool = False
    joined_entity_id: str
    announce: bool = False
    fade_audio: bool = False
    sonos_restored: bool = False
    media_dirs_dict: object = {}

    async def async_initialize_media_players(self,
                                             hass: HomeAssistant,
                                             entity_ids,
                                             volume_level,
                                             join_players,
                                             unjoin_players,
                                             announce,
                                             fade_audio):
        """Initialize media player entities."""
        # Service call was from chime_tts.say_url, so media_players are irrelevant
        if len(entity_ids) == 0:
            return []

        self.media_players: list[ChimeTTSMediaPlayer] = []
        self.joined_media_player_entity_ids = []
        self.unjoined_media_player_entity_ids = []
        self.join_players = join_players
        self.unjoin_players = unjoin_players
        self.joined_entity_id = None
        self.announce = announce
        self.fade_audio = fade_audio
        self.sonos_restored = False
        self.media_dirs_dict: object = hass.config.media_dirs or {}

        for entity_id in entity_ids:
            media_player_object = await self.async_get_media_player_object(hass, entity_id, volume_level)
            if media_player_object:
                self.media_players.append(media_player_object)

        if len(self.media_players) == 0:
            _LOGGER.error("No valid media players found")

        return self.media_players

    async def async_get_media_player_object(self,
                                            hass: HomeAssistant,
                                            entity_id: str,
                                            target_volume_level):
        """Create a Chime TTS media player object from a given entity_id."""

        if (hass is None
            or entity_id is None
            or hass.states.get(entity_id) is None):
            return None

        return ChimeTTSMediaPlayer(
            hass=hass,
            entity_id=entity_id,
            target_volume_level=target_volume_level)

    def parse_entity_ids(self, data, hass) -> list[str]:
        """Parse media_player entity_ids into list object."""
        entity_ids: list[str] = data.get(CONF_ENTITY_ID, [])
        if isinstance(entity_ids, str):
            entity_ids = entity_ids.split(",")

        # Find all media_player entities associated with device/s specified
        device_ids = data.get("device_id", [])
        if isinstance(device_ids, str):
            device_ids = device_ids.split(",")
        entity_registry = hass.data["entity_registry"]
        for device_id in device_ids:
            matching_entity_ids = [
                entity.entity_id
                for entity in entity_registry.entities.values()
                if entity.device_id == device_id
                and entity.entity_id.startswith("media_player.")
            ]
            entity_ids.extend(matching_entity_ids)
        entity_ids: list[str] = list(set(entity_ids))
        return entity_ids

    def get_fade_in_out_media_players(self) -> list[ChimeTTSMediaPlayer]:
        """List of media_player objects that should fade out before Chime TTS playback and fade back in when completed."""
        announce_unsupported_media_players: list[ChimeTTSMediaPlayer] = []
        for media_player in self.media_players:
            if (media_player.initially_playing and
                (self.fade_audio or (self.announce and not media_player.announce_supported))):
                announce_unsupported_media_players.append(media_player)
        return announce_unsupported_media_players

    def get_set_volume_media_players(self) -> list[ChimeTTSMediaPlayer]:
        """List of media_player objects whose volume levels need to be changed (without fading) to the target volume level."""
        set_volume_media_players: list[ChimeTTSMediaPlayer] = []
        for media_player in self.media_players:
            if (media_player not in self.get_fade_in_out_media_players()
                and media_player.target_volume_level not in [-1, media_player.initial_volume_level]
                and media_player.platform not in (SPOTIFY_PLATFORM, SONOS_PLATFORM)
            ):
                set_volume_media_players.append(media_player)
        return set_volume_media_players

    def get_media_player_target_volume(self, entity_id):
        """Get the target volume level for a given media_player entity."""
        for media_player in self.media_players:
            if media_player.entity_id == entity_id:
                return media_player.target_volume_level
        return None

    def get_media_player_platform(self, hass: HomeAssistant, entity_id):
        """Get the platform for a given media_player entity."""
        entity_registry = hass.data["entity_registry"]
        for entity in entity_registry.entities.values():
            if entity and entity.entity_id == entity_id:
                _LOGGER.debug("%s", entity.platform)
                return entity.platform
        return None

    def get_media_players_from_entity_ids(self, entity_ids) -> list[ChimeTTSMediaPlayer]:
        """List of media_player objects from a list of entity_ids."""
        media_players: list[ChimeTTSMediaPlayer] = []
        for entity_id in entity_ids:
            media_player = self.get_media_players_from_entity_id(entity_id)
            if media_player:
                media_players.append(media_player)
        return media_players

    def get_media_players_from_entity_id(self, entity_id) -> ChimeTTSMediaPlayer:
        """media_player objects matching a given entity_id."""
        for media_player in self.media_players:
            if media_player.entity_id == entity_id:
                return media_player
        return None

    def get_uniform_target_volume_level(self, entity_ids):
        """Target volume level (if identical between media_players)."""
        uniform_volume_level = -1
        for media_player in self.get_media_players_from_entity_ids(entity_ids):
            media_player_volume = media_player.target_volume_level
            if media_player_volume == -1:
                continue
            if uniform_volume_level == -1:
                uniform_volume_level = media_player_volume
            elif uniform_volume_level != media_player_volume:
                return -1
        return uniform_volume_level

    def get_is_standard_media_player(self, entity_id):
        """Determine whether a media_player can be used with the media_player.play_media service."""
        platform = self.get_platform_from_entity_id(entity_id)
        return platform and platform not in (ALEXA_MEDIA_PLAYER_PLATFORM, SONOS_PLATFORM, SPOTIFY_PLATFORM)

    def get_platform_from_entity_id(self, entity_id):
        """Platform for the media_player with entity_id."""
        media_player: ChimeTTSMediaPlayer = self.get_media_players_from_entity_id(entity_id)
        if media_player:
            return media_player.platform

    def get_is_media_player_alexa(self, entity_id):
        """Determine whether a media_player belongs to the Alexa Media Player platform."""
        return self.get_platform_from_entity_id(entity_id) == ALEXA_MEDIA_PLAYER_PLATFORM

    def get_is_media_player_sonos(self, entity_id):
        """Determine whether a media_player belongs to the Sonos platform."""
        return self.get_platform_from_entity_id(entity_id) == SONOS_PLATFORM

    def get_is_media_player_spotify(self, entity_id):
        """Determine whether a media_player belongs to the Spotify platform."""
        return self.get_platform_from_entity_id(entity_id) == SPOTIFY_PLATFORM

    def get_alexa_media_players_count(self):
        """Count of alexa_media_players."""
        alexa_media_players = [media_player for media_player in self.media_players if media_player.platform == ALEXA_MEDIA_PLAYER_PLATFORM]
        return len(alexa_media_players)

    def get_media_players_of_platform(self, entity_ids: list = [], platform: str = ""):
        """List of media_players belonging to a specific platform."""
        if entity_ids and platform:
            return [entity_id for entity_id in entity_ids if self.get_media_players_from_entity_id(entity_id) and self.get_media_players_from_entity_id(entity_id).platform == platform]
        return []

    def get_supported_feature(self, entity: State, feature: str):
        """Whether a feature is supported by the media_player device."""
        if entity is None or entity.attributes is None:
            return False
        supported_features = entity.attributes.get("supported_features", 0)

        if feature is ATTR_MEDIA_VOLUME_LEVEL:
            return bool(supported_features & 2)

        if feature is ATTR_MEDIA_ANNOUNCE:
            return bool(supported_features & 1048576)

        if feature is ATTR_GROUP_MEMBERS:
            return bool(supported_features & 524288)

        return False

    def get_media_content_id(self, hass: HomeAssistant, file_path: str):
        """Create the media content id for a local media directory file."""
        if not file_path:
            _LOGGER.error("Audio file path missing in call to get_media_content_id")
            return None

        media_source_path = file_path

        media_dir_key = ""
        for name_i, path_i in hass.config.media_dirs.items():
            if file_path.startswith(path_i) and len(media_dir_key) < len(path_i):
                media_dir_key = name_i
        if self.media_dirs_dict.get(media_dir_key, None):
            path = self.media_dirs_dict.get(media_dir_key, None)
            media_source_path = media_source_path[len(f"/{path}") :]
            media_source_path = f"media-source://media_source/{media_dir_key}/{media_source_path}"
            return media_source_path

        # Media file exists outside of a media folder
        return None

    #### ACTIONS ####

    async def async_fade_out_and_pause(self, hass: HomeAssistant, fade_duration: float):
        """Fade out and pause relevant media players."""
        fade_in_out_media_players: list[ChimeTTSMediaPlayer] = self.get_fade_in_out_media_players()
        if len(fade_in_out_media_players) > 0:

            # Fade out media players manually if platform does not support `announce`
            await self.async_set_volume_for_media_players(hass=hass,
                                                          media_players=fade_in_out_media_players,
                                                          volume_key=0,
                                                          fade_duration=fade_duration)

            # Pause playing media_players
            pause_entity_ids = []
            for media_player in fade_in_out_media_players:
                pause_entity_ids.append(media_player.entity_id)
            _LOGGER.debug(" - Pausing %s media_player", str(len(pause_entity_ids)))
            try:
                await hass.services.async_call(
                    domain="media_player",
                    service="media_pause",
                    service_data={CONF_ENTITY_ID: pause_entity_ids},
                    blocking=True
                )
            except Exception as error:
                _LOGGER.warning("Unable to pause media player%s: %s", ("" if len(pause_entity_ids) == 1 else "s"), str(error))

            # Wait until media_players' state = paused
            await self.async_wait_until_media_players_state_is(
                hass=hass,
                media_players=fade_in_out_media_players,
                target_state="paused",
                timeout=1.5
            )

            # Set media players to target volume level for Chime TTS Playback
            playback_media_players = []
            for media_player in fade_in_out_media_players:
                if media_player.platform != SPOTIFY_PLATFORM:
                    playback_media_players.append(media_player)
            await self.async_set_volume_for_media_players(
                hass=hass,
                media_players=playback_media_players,
                volume_key="target_volume_level",
                fade_duration=0
            )

    async def async_resume_playback(self, hass, fade_duration: float):
        """Resume paused media players after Chime TTS playback is completed."""
        fade_in_media_players = self.get_fade_in_out_media_players()
        if len(fade_in_media_players) > 0:
            # 1. Wait until all media_players paused
            if not await self.async_wait_until_media_players_state_is(hass=hass,
                                                                      media_players=fade_in_media_players,
                                                                      target_state="paused",
                                                                      timeout=5):
                _LOGGER.warning("Timed out waiting for %s media_player%s to pause",
                                str(len(fade_in_media_players)),
                                ("" if len(fade_in_media_players) == 1 else "s"))

            # 2. Set media_players volume to 0
            _LOGGER.debug("     - Setting volume to 0")
            resume_entity_ids = []
            for media_player in fade_in_media_players:
                entity_id = media_player.entity_id
                resume_entity_ids.append(entity_id)
            try:
                await hass.services.async_call(
                    domain="media_player",
                    service=SERVICE_VOLUME_SET,
                    service_data={
                        ATTR_MEDIA_VOLUME_LEVEL: 0,
                        CONF_ENTITY_ID: resume_entity_ids
                    },
                    blocking=True
                )
            except Exception as error:
                _LOGGER.warning("Unable to set %s's volume to 0 for: %s. Error: %s",
                                entity_id, (", ".join(map(str, resume_entity_ids))), error)

            # 3a. Restore from Sonos snapshot
            await self.async_sonos_restore(hass)

            # 3b. Call `media_play` until all media_players' states are "playing"
            _LOGGER.debug("   - Resuming %s media_player%s",
                        str(len(resume_entity_ids)),
                        ("" if len(resume_entity_ids) == 1 else "s"))
            retry_duration = 3
            delay_s = 0.25
            paused_media_players = resume_entity_ids.copy()
            while len(paused_media_players) > 0 and retry_duration > 0:
                try:
                    await hass.services.async_call(
                        domain="media_player",
                        service="media_play",
                        service_data={CONF_ENTITY_ID: paused_media_players},
                        blocking=True,
                    )
                except Exception as error:
                    _LOGGER.warning("media_player.play_media failed: %s", error)

                still_paused_media_players = []
                for entity_id in paused_media_players:
                    if hass.states.get(entity_id).state != "playing":
                        still_paused_media_players.append(entity_id)
                    else:
                        _LOGGER.debug("     - ✔️ %s resumed", entity_id)
                paused_media_players = still_paused_media_players

                if len(paused_media_players) > 0:
                    await hass.async_add_executor_job(time.sleep, delay_s)
                retry_duration = retry_duration - delay_s

            for entity_id in paused_media_players:
                _LOGGER.warning("Failed to resume playback on %s", entity_id)
                _LOGGER.debug("     - 𝘅 %s - timed out", entity_id)

            # 4. Fade in all media players at the same time
            await self.async_set_volume_for_media_players(hass=hass,
                                                          media_players=self.get_fade_in_out_media_players(),
                                                          volume_key="initial_volume_level",
                                                          fade_duration=fade_duration)

    async def async_wait_until_media_players_state_is(
            self,
            hass: HomeAssistant,
            media_players: list[ChimeTTSMediaPlayer],
            target_state: str,
            timeout: float = 3.5) -> bool:
        """Wait until the state of a list of media_players equals a target state."""
        def condition(media_player: ChimeTTSMediaPlayer) -> bool:
            return media_player.get_state() == target_state

        _LOGGER.debug(" - Waiting until %s media_player%s %s %s...",
                      len(media_players),
                      ("" if len(media_players) == 1 else "s"),
                      ("is" if len(media_players) == 1 else "are"),
                      target_state)
        return await self._async_wait_until_media_players(hass, media_players, condition, timeout)

    async def async_wait_until_media_players_state_not(
            self,
            hass: HomeAssistant,
            media_players: list[ChimeTTSMediaPlayer],
            target_state: str,
            timeout: float = 3.5) -> bool:
        """Wait until the state of a list of media_players no longer equals a target state."""
        def condition(media_player: ChimeTTSMediaPlayer):
            return media_player.get_state() != target_state

        _LOGGER.debug(" - Waiting until %s media_player%s %s %s...",
                      len(media_players),
                      ("" if len(media_players) == 1 else "s"),
                      ("isn't" if len(media_players) == 1 else "aren't"),
                      target_state)
        return await self._async_wait_until_media_players(hass, media_players, condition, timeout)

    async def async_wait_until_media_players_volume_level_is(self,
                                                             hass: HomeAssistant,
                                                             media_players: list[ChimeTTSMediaPlayer],
                                                             target_volume: str,
                                                             timeout: float = 5) -> bool:
        """Wait for a media_player to have a target volume_level."""
        def condition(media_player: ChimeTTSMediaPlayer) -> bool:
            return media_player.get_current_volume_level() == target_volume

        _LOGGER.debug(" - Waiting until %s media_player%s volume_level %s %s...",
                      len(media_players),
                      ("" if len(media_players) == 1 else "s"),
                      ("is" if len(media_players) == 1 else "are"),
                      target_volume)
        return await self._async_wait_until_media_players(hass, media_players, condition, timeout)

    async def _async_wait_until_media_players(self,
                                              hass: HomeAssistant,
                                              media_players: list[ChimeTTSMediaPlayer],
                                              condition,
                                              timeout: float = 3.5):
        """Wait until the state of a list of media_players equals/no longer equals a target state."""
        # Validation
        if (hass is None or media_players is None or len(media_players) == 0 or condition is None):
            return False

        delay = 0.2
        still_waiting: list[ChimeTTSMediaPlayer] = media_players.copy()
        while len(still_waiting) > 0 and timeout > 0:
            for media_player in media_players:
                if condition(media_player) and media_player in still_waiting:
                    _LOGGER.debug("   ✔ %s", media_player.entity_id)
                    index = still_waiting.index(media_player)
                    try:
                        del still_waiting[index]
                    except Exception as error:
                        _LOGGER.error("Error updating media player %s's state: %s", media_player.entity_id, error)
            timeout = timeout - delay

            if len(still_waiting) > 0:
                await hass.async_add_executor_job(time.sleep, delay)

        # Timeout
        if len(still_waiting) > 0:
            for media_player in still_waiting:
                _LOGGER.debug("   𝘅 %s - Timed out. Current state: %s", media_player.entity_id, str(media_player.get_state()))

        return len(still_waiting) == 0

    async def async_sonos_snapshot(self, hass: HomeAssistant):
        """Take a Sonos snapshot of Sonos media players."""
        if not SONOS_SNAPSHOT_ENABLED:
            return
        sonos_media_player_entity_ids: list[str] = [media_player.entity_id for media_player in self.media_players if media_player.platform == SONOS_PLATFORM]
        if len(sonos_media_player_entity_ids) > 0:
            _LOGGER.debug("Taking a Sonos snapshot of %s media player%s", str(len(sonos_media_player_entity_ids)), "" if len(sonos_media_player_entity_ids) == 1 else "s")
            try:
                await hass.services.async_call(
                    domain="sonos",
                    service="snapshot",
                    service_data={
                        CONF_ENTITY_ID: sonos_media_player_entity_ids,
                        "with_group": True,
                    },
                    blocking=True
                )
            except Exception as error:
                _LOGGER.warning("Unable to create Sonos snapshot: %s", str(error))

    async def async_sonos_restore(self, hass: HomeAssistant):
        """Restore Sonos media_players from snapshot."""
        if not SONOS_SNAPSHOT_ENABLED or self.sonos_restored:
            return

        sonos_media_player_entity_ids: list[str] = [media_player.entity_id for media_player in self.media_players if media_player.platform == SONOS_PLATFORM]
        if len(sonos_media_player_entity_ids) > 0:
            _LOGGER.debug("Restoring %s Sonos media player%s from snapshot", str(len(sonos_media_player_entity_ids)), "" if len(sonos_media_player_entity_ids) == 1 else "s")
            try:
                await hass.services.async_call(
                    domain="sonos",
                    service="restore",
                    service_data={
                        CONF_ENTITY_ID: sonos_media_player_entity_ids,
                        "with_group": True,
                    },
                    blocking=True
                )
                self.sonos_restored = True
            except Exception as error:
                _LOGGER.warning("Unable to restore Sonos snapshot: %s", str(error))

    async def async_set_volume_for_media_players(self,
                                                 hass: HomeAssistant,
                                                 media_players: list[ChimeTTSMediaPlayer],
                                                 volume_key,
                                                 fade_duration: int):
        """Set the volume level for media players either in steps or instantaneously."""
        if not media_players:
            return

        fade_duration /= 1000  # Convert from milliseconds to seconds
        fade_steps = max(math.ceil(fade_duration * 1000 / TRANSITION_STEP_MS), 1)
        delay_s = fade_duration / fade_steps if fade_steps > 1 else 0
        volume_changed_dicts = []

        for media_player in media_players:
            entity_id: str = media_player.entity_id
            current_volume: float = media_player.get_current_volume_level()
            target_volume: float = getattr(media_player, volume_key, 0) if isinstance(volume_key, str) else volume_key

            if target_volume == -1:
                if volume_key == "initial_volume_level":
                    _LOGGER.debug("Initial volume for %s is unknown. Unable to restore volume.", entity_id)
                continue

            if target_volume == current_volume:
                _LOGGER.debug("The volume level for %s is already set to %s", entity_id, str(target_volume))
                continue

            volume_changed_dicts.append({"media_player": media_player, "target_volume": target_volume})

            if fade_steps > 1:
                volume_step: float = (target_volume - current_volume) / fade_steps
                volume_steps: list[float] = [current_volume + volume_step * i for i in range(1, fade_steps + 1)]
                _LOGGER.debug(" - Fading %s %s's volume from %s to %s over %ss",
                            "in" if volume_step > 0 else "out",
                            entity_id,
                            str(current_volume),
                            str(target_volume),
                            str(fade_duration))
                for step in range(fade_steps):
                    new_volume = round(max(volume_steps[step], 0), 4)
                    await self.async_set_volume_action(hass, entity_id, new_volume)
                    await hass.async_add_executor_job(time.sleep, delay_s)
            else:
                if target_volume > current_volume:
                    _LOGGER.debug("Increasing %s's volume from %s to %s", entity_id, str(current_volume), str(target_volume))
                else:
                    _LOGGER.debug("Decreasing %s's volume from %s to %s", entity_id, str(current_volume), str(target_volume))
                await self.async_set_volume_action(hass, entity_id, target_volume)

        await self.async_wait_until_target_volume_reached(hass, volume_changed_dicts)

    async def async_set_volume_action(self, hass: HomeAssistant, entity_id: str, target_volume: float, is_retry: bool = False):
        """Call the media_player.set_volume service with a specific media player & volume level."""
        if is_retry:
            _LOGGER.debug(" - Retry setting %s's volume to %s", entity_id, str(target_volume))
        else:
            _LOGGER.debug(" - Setting %s's volume to %s", entity_id, str(target_volume))
        try:
            await hass.services.async_call(
                domain="media_player",
                service=SERVICE_VOLUME_SET,
                service_data={
                    ATTR_MEDIA_VOLUME_LEVEL: target_volume,
                    CONF_ENTITY_ID: entity_id
                },
                blocking=True,
            )
        except Exception as error:
            _LOGGER.warning("Unable to set %s's volume to %s: %s", entity_id, str(target_volume), error)

    async def async_wait_until_target_volume_reached(self, hass, volume_changed_dicts):
        """Wait until all media players register their new volumes."""
        if not volume_changed_dicts:
            return

        timeout = 5
        delay_s = 0.150
        end_time = time.time() + timeout
        has_debug_log_written = False

        while time.time() < end_time:
            all_volumes_set = True

            for media_player_dict in volume_changed_dicts[:]:  # Iterate over a copy to allow safe removal
                media_player: ChimeTTSMediaPlayer = media_player_dict.get("media_player")
                target_volume = media_player_dict.get("target_volume")

                if media_player and round(media_player.get_current_volume_level(), 3) not in (round(target_volume,3), round(-1,3)):
                    all_volumes_set = False
                    if not has_debug_log_written:
                        _LOGGER.debug("...waiting until new volume levels reached...")
                        has_debug_log_written = True
                    await self.async_set_volume_action(hass, media_player.entity_id, target_volume, True)
                else:
                    _LOGGER.debug(" - ✔️ %s's volume now %s", media_player.entity_id, str(media_player.get_current_volume_level()))
                    volume_changed_dicts.remove(media_player_dict)  # Remove the entry once the volume is set

            if all_volumes_set:
                break

            await hass.async_add_executor_job(time.sleep, delay_s)
            _LOGGER.debug("...")

        # Log the media players which timed out waiting for their new volumes to register
        for media_player_dict in volume_changed_dicts:
            media_player: ChimeTTSMediaPlayer = media_player_dict.get("media_player")
            if media_player:
                target_volume = media_player_dict.get("target_volume")
                current_volume = media_player.get_current_volume_level()
                if current_volume != target_volume:
                    _LOGGER.debug(" - 𝘅 %s (timed out before volume set to %s. Current volume = %s)",
                                media_player.entity_id, str(target_volume), str(current_volume))


    async def async_join_media_players(self, hass: HomeAssistant):
        """Join media players."""
        self.joined_entity_id = None
        if self.join_players is False:
            return None

        # Separate media players into joined and unjoined lists
        joined_count = 0
        for media_player in self.media_players:
            if media_player.join_supported:
                # Assign first supported media_player as speaker leader
                if not self.joined_entity_id:
                    self.joined_entity_id = media_player.entity_id
                else:
                    # Add 2nd+ supported media_player to the joined_supported list
                    self.joined_media_player_entity_ids.append(media_player.entity_id)
                joined_count += 1
            else:
                self.unjoined_media_player_entity_ids.append(media_player.entity_id)

        # Validation
        if joined_count == 0:
            _LOGGER.warning("No media_players were found that support joining speakers into a group. A minimum of 2 is required.")
            return
        if joined_count == 1:
            _LOGGER.warning("Only 1 media_player was found that supports joining speakers into a group. A minimum of 2 is required.")
            return

        # Log the speaker group 'leader' (joined_entity_id)
        _LOGGER.debug(
            "Joined speaker leader: %s, with %s group member%s:",
            str(self.joined_entity_id),
            str(len(self.joined_media_player_entity_ids)),
            ("s" if len(self.joined_media_player_entity_ids) > 1 else ""),
        )
        # Log the speaker group members
        for media_player_entity_id in self.joined_media_player_entity_ids:
            _LOGGER.debug("  - %s", media_player_entity_id)

        # Perform join
        try:
            await hass.services.async_call(
                domain="media_player",
                service=SERVICE_JOIN,
                service_data={
                    CONF_ENTITY_ID: self.joined_entity_id,
                    ATTR_GROUP_MEMBERS: self.joined_media_player_entity_ids,
                },
                blocking=True,
            )
        except Exception as error:
            _LOGGER.warning("Error joining media_player entities: %s", error)
            self.joined_entity_id = None

        return self.joined_entity_id

    async def async_unjoin_media_players(self, hass):
        """Unjoin media players."""
        if self.unjoin_players is True and self.joined_entity_id:
            _LOGGER.debug("   - Calling media_player.unjoin service...")
            media_player_entity_ids: list[str] = (self.joined_media_player_entity_ids + [self.joined_entity_id])
            count = 0
            for entity_id in media_player_entity_ids:
                count += 1
                _LOGGER.debug("     - media_player.unjoin %s/%s: %s", str(count), str(len(media_player_entity_ids)), entity_id)
                try:
                    await hass.services.async_call(
                        domain="media_player",
                        service=SERVICE_UNJOIN,
                        service_data={CONF_ENTITY_ID: entity_id},
                        blocking=True,
                    )
                except Exception as error:
                    _LOGGER.warning(
                        "Error calling unjoin service for %s: %s", entity_id, error
                    )
