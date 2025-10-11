from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

import asyncio

from samsungtvws import SamsungTVWS

from .const import (
    DOMAIN,
    CONF_MEDIA_PLAYER,
    CONF_APP_ID,
    CONF_SOURCE_OFF,
    CONF_SELECT_DELAY,
    CONF_RETRIES,
    CONF_RETRY_SLEEP,
    CONF_RESOURCE,
    CONF_NAME,
    DEFAULT_SELECT_DELAY,
    DEFAULT_RETRIES,
    DEFAULT_RETRY_SLEEP,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    data = entry.data
    options = entry.options or {}
    cfg = {**data, **options}

    entity = FrameArtSwitch(
        hass=hass,
        unique_id=f"{cfg.get(CONF_RESOURCE)}-art",
        name=cfg.get(CONF_NAME, "The Frame Art"),
        host=cfg[CONF_RESOURCE],
        media_player=cfg.get(CONF_MEDIA_PLAYER),
        app_id=cfg.get(CONF_APP_ID, "TV/HDMI"),
        source_off=cfg.get(CONF_SOURCE_OFF),
        select_delay=float(cfg.get(CONF_SELECT_DELAY, DEFAULT_SELECT_DELAY)),
        retries=int(cfg.get(CONF_RETRIES, DEFAULT_RETRIES)),
        retry_sleep=float(cfg.get(CONF_RETRY_SLEEP, DEFAULT_RETRY_SLEEP)),
    )
    async_add_entities([entity])

class FrameArtSwitch(SwitchEntity):
    _attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        unique_id: str,
        name: str,
        host: str,
        media_player: Optional[str],
        app_id: Optional[str],
        source_off: Optional[str],
        select_delay: float,
        retries: int,
        retry_sleep: float,
    ) -> None:
        self.hass = hass
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._host = host
        self._mp = media_player
        self._app_id = app_id
        self._source_off = source_off
        self._delay = max(0.0, select_delay)
        self._retries = max(0, retries)
        self._retry_sleep = max(0.05, retry_sleep)
        self._tv = SamsungTVWS(self._host, timeout=5.0)
        self._attr_is_on = False

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self._host)},
            "name": self._attr_name,
            "manufacturer": "Samsung",
            "model": "The Frame",
        }

    def _get_attr(self, key: str):
        st = self.hass.states.get(self._mp) if self._mp else None
        return None if st is None else st.attributes.get(key)

    async def _wait_attr(self, key: str, expected: str) -> bool:
        for _ in range(self._retries + 1):
            val = self._get_attr(key)
            if val == expected:
                return True
            await asyncio.sleep(self._retry_sleep)
        _LOGGER.debug("[%s] attendu %s='%s' mais lu '%s'", self.entity_id, key, expected, self._get_attr(key))
        return False

    async def _call_select_source(self, label: str) -> bool:
        try:
            await self.hass.services.async_call(
                "media_player",
                "select_source",
                {"entity_id": self._mp, "source": label},
                blocking=True,
            )
            _LOGGER.debug("[%s] media_player.select_source('%s') envoyé", self.entity_id, label)
            return True
        except Exception as err:
            _LOGGER.warning("[%s] Echec select_source('%s'): %s", self.entity_id, label, err)
            return False

    async def _call_select_app(self, app_id: str) -> bool:
        try:
            await self.hass.services.async_call(
                "samsungtv_smart",
                "select_app",
                {"entity_id": self._mp, "app": app_id},
                blocking=True,
            )
            _LOGGER.debug("[%s] samsungtv_smart.select_app(app='%s') envoyé", self.entity_id, app_id)
            return True
        except Exception as err1:
            _LOGGER.debug("[%s] select_app(app=...) non dispo: %s", self.entity_id, err1)
        try:
            await self.hass.services.async_call(
                "samsungtv_smart",
                "select_app",
                {"entity_id": self._mp, "app_id": app_id},
                blocking=True,
            )
            _LOGGER.debug("[%s] samsungtv_smart.select_app(app_id='%s') envoyé", self.entity_id, app_id)
            return True
        except Exception as err2:
            _LOGGER.debug("[%s] select_app(app_id=...) non dispo: %s", self.entity_id, err2)
        ok = await self._call_select_source(app_id)
        if ok:
            _LOGGER.debug("[%s] Fallback select_source('%s') utilisé comme app", self.entity_id, app_id)
        return ok

    async def _select_after_art_off(self) -> None:
        if not self._mp:
            return
        if self._source_off:
            if self._delay > 0:
                await asyncio.sleep(self._delay)
            if await self._call_select_source(self._source_off):
                await self._wait_attr("source", self._source_off)
        if self._app_id:
            if self._delay > 0:
                await asyncio.sleep(self._delay)
            if await self._call_select_app(self._app_id):
                await self._wait_attr("app_id", self._app_id)

    async def async_turn_on(self, **kwargs: Any) -> None:
        try:
            await self.hass.async_add_executor_job(lambda: self._tv.art().set_artmode("on"))
            self._attr_is_on = True
            self._attr_available = True
            _LOGGER.debug("[%s] Art Mode ON", self.entity_id)
            self.async_write_ha_state()
        except Exception as err:
            self._attr_available = False
            _LOGGER.warning("[%s] Impossible d'activer Art Mode: %s", self.entity_id, err)

    async def async_turn_off(self, **kwargs: Any) -> None:
        set_ok = False
        try:
            await self.hass.async_add_executor_job(lambda: self._tv.art().set_artmode("off"))
            set_ok = True
            self._attr_is_on = False
            self._attr_available = True
            _LOGGER.debug("[%s] Art Mode OFF", self.entity_id)
            self.async_write_ha_state()
        except Exception as err:
            self._attr_available = False
            _LOGGER.warning("[%s] Impossible de désactiver Art Mode: %s", self.entity_id, err)

        if set_ok:
            await self._select_after_art_off()

    async def async_update(self) -> None:
        try:
            info = await self.hass.async_add_executor_job(lambda: self._tv.art().get_artmode())
            self._attr_is_on = (info == "on")
            self._attr_available = True
        except Exception as err:
            self._attr_available = False
            _LOGGER.debug("[%s] Update Art Mode KO: %s", self.entity_id, err)
