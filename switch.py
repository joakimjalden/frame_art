from samsungtvws import SamsungTVWS
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

import voluptuous as vol

from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchEntity,
)
from homeassistant.const import (
    CONF_NAME,
    CONF_RESOURCE,
    CONF_SWITCHES,
    CONF_TIMEOUT,
 )
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 5.0

SWITCH_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_RESOURCE): cv.string,
        vol.Optional(CONF_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.Coerce(float),
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_SWITCHES): cv.schema_with_slug_keys(SWITCH_SCHEMA)}
)

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Find and return art mode switches for Samsung The Frame TVs."""
    devices: dict[str, Any] = config[CONF_SWITCHES]
    switches = []

    for object_id, device_config in devices.items():

        switches.append(
            ArtSwitch(
                object_id,
                device_config[CONF_RESOURCE],
                device_config.get(CONF_NAME, object_id),
                device_config[CONF_TIMEOUT],
            )
        )

    if not switches:
        _LOGGER.error("No switches added")
        return

    add_entities(switches)


class ArtSwitch(SwitchEntity):
    def __init__(
        self,
        object_id: str,
        resource: str,
        friendly_name: str,
        timeout: float,
    ) -> None:
        """Initialize the switch."""
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._resource = resource
        self._attr_name = friendly_name
        self._attr_is_on = False
        self._timeout = timeout
        self._tv = SamsungTVWS(self._resource, timeout=self._timeout)

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        try:
            self._tv.art().set_artmode('on')
            self._attr_is_on = True
            self._attr_available = True
        except:
            self._attr_available = False

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        try:
            self._tv.art().set_artmode('off')
            self._attr_is_on = False
            self._attr_available = True
        except:
            self._attr_available = False

    def update(self):
        """Update the switch status."""
        try:
            info = self._tv.art().get_artmode()
            if info == 'on':
                self._attr_is_on = True
            else:
                self._attr_is_on = False
            self._attr_available = True
        except:
            self._attr_available = False