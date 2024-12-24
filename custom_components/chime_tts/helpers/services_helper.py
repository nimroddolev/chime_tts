"""TTS services.yaml helper functions for Chime TTS."""
import os
import yaml
import aiofiles
import aiofiles.os
import logging
# import voluptuous as vol
from homeassistant.core import HomeAssistant, SupportsResponse
from .filesystem import FilesystemHelper
from ..const import (
    DOMAIN,
    SERVICE_SAY,
    SERVICE_SAY_URL,
    DEFAULT_CHIME_OPTIONS,
    CUSTOM_CHIMES_PATH_KEY,
)
filesystem_helper = FilesystemHelper()
_LOGGER = logging.getLogger(__name__)

class ChimeTTSServicesHelper:
    """Helper services YAML file functions for Chime TTS."""

    _data = {}

    async def async_update_services_yaml(self,
                                         hass,
                                         say_service_func,
                                         say_url_service_func):
        """Update the list of chimes for the say and say-url services."""
        custom_chimes_options = await filesystem_helper.async_get_chime_options_from_path(self._data[CUSTOM_CHIMES_PATH_KEY])
        await self._async_update_chime_lists(hass=hass, custom_chime_options=custom_chimes_options)
        hass.services.async_remove(DOMAIN, SERVICE_SAY)
        hass.services.async_register(DOMAIN, SERVICE_SAY, say_service_func)
        hass.services.async_remove(DOMAIN, SERVICE_SAY_URL)
        hass.services.async_register(DOMAIN,
                                    SERVICE_SAY_URL,
                                    say_url_service_func,
                                    supports_response=SupportsResponse.ONLY)

    async def _async_update_chime_lists(self, hass: HomeAssistant, custom_chime_options: str):
        """Modify the chime path drop down options."""

        services_yaml = await self._async_parse_services_yaml()
        if not services_yaml:
            return

        try:
            # Chime Paths
            final_options: list = DEFAULT_CHIME_OPTIONS + custom_chime_options
            final_options = sorted(final_options, key=lambda x: x['label'].lower())
            if not custom_chime_options:
                final_options.append({"label": "*** Add a local folder path in the configuration for your own custom chimes ***", "value": None})

            # New chimes detected?
            if final_options != services_yaml['say']['fields']['chime_path']['selector']['select']['options']:
                # Update `say` and `say_url` chime path fields
                services_yaml['say']['fields']['chime_path']['selector']['select']['options'] = list(final_options)
                services_yaml['say']['fields']['end_chime_path']['selector']['select']['options'] = list(final_options)
                services_yaml['say_url']['fields']['chime_path']['selector']['select']['options'] = list(final_options)
                services_yaml['say_url']['fields']['end_chime_path']['selector']['select']['options'] = list(final_options)
        except Exception as e:
            _LOGGER.error("Unexpected error updating services.yaml: %s", str(e))
        await self._async_save_services_yaml(services_yaml)

    async def _async_parse_services_yaml(self):
        """Load the services.yaml file into a dictionary."""
        services_file_path = os.path.join(os.path.dirname(__file__), '../services.yaml')

        try:
            async with aiofiles.open(services_file_path) as file:
                services_yaml = yaml.safe_load(await file.read())
                return services_yaml
        except FileNotFoundError:
            _LOGGER.error("services.yaml file not found at %s", services_file_path)
            return
        except yaml.YAMLError as e:
            _LOGGER.error("Error parsing services.yaml: %s", str(e))
            return
        except Exception as e:
            _LOGGER.error("Unexpected error reading services.yaml: %s", str(e))
            return

    async def _async_save_services_yaml(self, services_yaml):
        """Save a dictionary to the services.yaml file."""

        services_file_path = os.path.join(os.path.dirname(__file__), '../services.yaml')

        try:
            async with aiofiles.open(services_file_path, mode='w') as file:
                await file.write(yaml.safe_dump(services_yaml, default_flow_style=False, sort_keys=False))

            _LOGGER.info("Updated services.yaml chime options.")
        except Exception as e:
            _LOGGER.error("Unexpected error updating services.yaml: %s", str(e))

    # async def async_get_schema_for_service(self, service_name: str):
    #     """Modify the chime path drop down options."""

    #     service_yaml = await self._async_parse_services_yaml()
    #     if not service_yaml or service_name not in service_yaml:
    #         return
    #     service_info = service_yaml[service_name]
    #     fields = service_info.get('fields', {})
    #     schema = {}

    #     # Process each field in the service
    #     for field_name, field_info in fields.items():
    #         selector = field_info.get('selector', {})

    #         if selector and selector.get('text'):
    #             multiline = selector['text'].get('multiline', False)
    #             if multiline:
    #                 schema[vol.Required(field_name)] = vol.All(vol.Coerce(str), vol.Length(max=1024))
    #             else:
    #                 schema[vol.Required(field_name)] = vol.Coerce(str)
    #         elif selector and selector.get('select'):
    #             options = [option['value'] for option in selector['select']['options']]
    #             schema[vol.Required(field_name)] = vol.In(options)
    #         elif selector and selector.get('boolean'):
    #             schema[vol.Required(field_name)] = vol.Coerce(bool)
    #         elif selector and selector.get('number'):
    #             number_selector = selector['number']
    #             schema[vol.Required(field_name)] = vol.All(
    #                 vol.Coerce(float),
    #                 vol.Range(
    #                     min=number_selector.get('min', None),
    #                     max=number_selector.get('max', None),
    #                 ),
    #             )
    #         else:
    #             schema[vol.Required(field_name)] = vol.Coerce(str)  # Default to string if selector type is missing

    #     return schema
