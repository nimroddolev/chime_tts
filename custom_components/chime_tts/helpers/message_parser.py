import logging
from jinja2 import Template
from homeassistant.helpers.template import Template

_LOGGER = logging.getLogger(__name__)

class MessageParser:
    """ Chime TTS helper class to parse text using across the integration."""

    def parse_message_templates(self, hass, message_str):
        """Parse `message` strings containing jinja2 templates."""
        if not message_str:
            return ''
        try:
            message_str = message_str.replace(r"\{\{", "{{").replace(r"\}\}", "}}")
            template = Template(message_str, hass)
            converted_str = template.async_render()
            return converted_str
        except Exception as e:
            raise ValueError(f"Error converting message with template {e}")
