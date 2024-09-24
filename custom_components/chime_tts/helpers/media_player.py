"""Media player classes to handle different pre-playback, playback & post-playback."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_ENTITY_ID, SERVICE_TURN_ON
from homeassistant.components.media_player.const import (
    ATTR_MEDIA_VOLUME_LEVEL,
    ATTR_MEDIA_ANNOUNCE,
    ATTR_GROUP_MEMBERS,
)

_LOGGER = logging.getLogger(__name__)

class ChimeTTSMediaPlayer:
    """Base media player class."""

    hass: HomeAssistant
    entity_id: str
    platform: str
    initial_volume_level: float
    target_volume_level: float
    initially_playing: bool
    announce_supported: bool
    join_supported: bool

    def __init__(self, hass: HomeAssistant, entity_id: str, target_volume_level):
        """Initialise the class."""
        self.hass: HomeAssistant = hass
        self.entity_id: str = entity_id
        self.platform = self.get_platform()

        # Initialise state and values
        self.turn_on()
        self.initially_playing = (self.get_state() == "playing"
                                  # Check that media_player is actually playing (HomePods can incorrectly have the state "playing" when no media is playing)
                                  and self.get_entity().attributes.get("media_duration", -1) != 0)
        self.initial_volume_level: float = self.get_current_volume_level()
        self.announce_supported = self.get_supported_feature(ATTR_MEDIA_ANNOUNCE)
        self.join_supported = self.get_supported_feature(ATTR_GROUP_MEMBERS)

        # Extract target volume level
        # From dictionary
        if isinstance(target_volume_level, dict) and entity_id in target_volume_level:
            self.target_volume_level = float(target_volume_level[entity_id])
        # From array of dicts
        elif isinstance(target_volume_level, list):
            for volume_level_dict in target_volume_level:
                if entity_id in volume_level_dict:
                    self.target_volume_level = float(volume_level_dict[entity_id])
        # From float
        elif isinstance(target_volume_level, float):
            self.target_volume_level = target_volume_level
        # Default
        else:
            self.target_volume_level = -1

    # Service Calls

    def turn_on(self):
        """Turn on the media player if it is currently off."""
        if self.get_state() == "off":
            _LOGGER.info('Turning on "%s"...', self.entity_id)
            try:
                self.hass.async_create_task(
                    self.hass.services.async_call(
                        domain="media_player",
                        service=SERVICE_TURN_ON,
                        service_data={CONF_ENTITY_ID: self.entity_id},
                        blocking=True
                    )
                )
            except Exception as error:
                _LOGGER.error("Error calling media_player.turn_on: %s", str(error))


    # Getters & Setters

    def get_entity(self):
        """media_player entity object."""
        return self.hass.states.get(self.entity_id)

    def get_state(self):
        """media_player entity state."""
        return self.get_entity().state

    def get_platform(self):
        """media_player entity integration platform."""
        entity_registry = self.hass.data["entity_registry"]
        for entity in entity_registry.entities.values():
            if entity.entity_id == self.entity_id:
                return entity.platform
        return None

    def get_supported_feature(self, feature: str):
        """Whether a feature is supported by the media_player device."""
        if self.get_entity() is None or self.get_entity().attributes is None:
            return False
        supported_features = self.get_entity().attributes.get("supported_features", 0)
        if feature is ATTR_MEDIA_VOLUME_LEVEL:
            return bool(supported_features & 2)
        if feature is ATTR_MEDIA_ANNOUNCE:
            return bool(supported_features & 1048576)
        if feature is ATTR_GROUP_MEMBERS:
            return bool(supported_features & 524288)
        return False

    def get_should_change_volume(self):
        """Boolean for whether the media player's volume level should be changed."""
        return self.target_volume_level >= 0 and self.target_volume_level != self.initial_volume_level

    @property
    def target_volume_level(self) -> float:
        """Media player's target volume level."""
        return self._target_volume_level

    @target_volume_level.setter
    def target_volume_level(self, value):
        """Store the media player's target volume level."""
        if isinstance(value, dict):
            value = float(value.get(self.entity_id, -1.0))
        self._target_volume_level = float(value) if value and float(value) > 0 else -1.0

    def get_current_volume_level(self) -> float:
        """Media player's current volume level."""
        return float(self.get_entity().attributes.get(ATTR_MEDIA_VOLUME_LEVEL, -1.0))

    @property
    def initial_volume_level(self) -> float:
        """Media player's initial volume level."""
        return self._initial_volume_level

    @initial_volume_level.setter
    def initial_volume_level(self, value: float):
        """Store the media player's initial volume level."""
        self._initial_volume_level = float(value if float(value) >= 0 else -1.0)
