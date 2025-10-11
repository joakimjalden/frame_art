from __future__ import annotations
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_NAME
from homeassistant.helpers import entity_registry as er
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_MEDIA_PLAYER,
    CONF_APP_ID,
    CONF_SOURCE_OFF,
    CONF_SELECT_DELAY,
    CONF_RETRIES,
    CONF_RETRY_SLEEP,
    CONF_RESOURCE,
    DEFAULT_SELECT_DELAY,
    DEFAULT_RETRIES,
    DEFAULT_RETRY_SLEEP,
)

def _samsungtv_smart_entities(hass: HomeAssistant) -> list[str]:
    ent_reg = er.async_get(hass)
    out: list[str] = []
    for ent in ent_reg.entities.values():
        if ent.domain == "media_player" and ent.platform == "samsungtv_smart":
            out.append(ent.entity_id)
    return sorted(out)

class FrameArtConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            # unique id by host
            await self.async_set_unique_id(f"frame_art_{user_input[CONF_RESOURCE]}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input.get(CONF_NAME) or "Frame Art", data=user_input)

        mp_choices = _samsungtv_smart_entities(self.hass)
        schema = vol.Schema({
            vol.Required("resource"): str,
            vol.Required("media_player"): vol.In(mp_choices) if mp_choices else str,
            vol.Optional("name", default="The Frame Art"): str,
            vol.Optional("source_off", default=""): str,
            vol.Optional("app_id", default="TV/HDMI"): str,
            vol.Optional("select_delay", default=DEFAULT_SELECT_DELAY): vol.Coerce(float),
            vol.Optional("retries", default=DEFAULT_RETRIES): vol.Coerce(int),
            vol.Optional("retry_sleep", default=DEFAULT_RETRY_SLEEP): vol.Coerce(float),
        })
        if not mp_choices:
            # Show a friendly hint if dependency isn't set up yet
            self._set_placeholders({"hint": "Installe et configure l’intégration 'SamsungTV Smart (ollo69)' avant de continuer."})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, import_config):
        return await self.async_step_user(import_config)

    async def async_get_options_flow(self, config_entry):
        return FrameArtOptionsFlow(config_entry)

class FrameArtOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, entry: config_entries.ConfigEntry) -> None:
        self.entry = entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        return await self.async_step_options(user_input)

    async def async_step_options(self, user_input=None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = {**self.entry.data, **(self.entry.options or {})}
        mp_choices = _samsungtv_smart_entities(self.hass)
        schema = vol.Schema({
            vol.Required("media_player", default=data.get("media_player","")): vol.In(mp_choices) if mp_choices else str,
            vol.Optional("source_off", default=data.get("source_off","")): str,
            vol.Optional("app_id", default=data.get("app_id","TV/HDMI")): str,
            vol.Optional("select_delay", default=data.get("select_delay", DEFAULT_SELECT_DELAY)): vol.Coerce(float),
            vol.Optional("retries", default=data.get("retries", DEFAULT_RETRIES)): vol.Coerce(int),
            vol.Optional("retry_sleep", default=data.get("retry_sleep", DEFAULT_RETRY_SLEEP)): vol.Coerce(float),
        })
        return self.async_show_form(step_id="options", data_schema=schema)
