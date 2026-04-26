from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry, ConfigEntryAuthFailed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import SadalesTiklsApiAuthError, SadalesTiklsApiClient, SadalesTiklsApiError
from .const import CONF_API_KEY, CONF_MNR, CONF_MPNR, CONF_OEIC, DOMAIN

_LOGGER = logging.getLogger(__name__)


class SadalesTiklsCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.api = SadalesTiklsApiClient(
            api_key=entry.data[CONF_API_KEY],
            oeic=entry.data[CONF_OEIC],
            mp_nr=entry.data[CONF_MPNR],
            m_nr=entry.data[CONF_MNR],
            session=async_get_clientsession(hass),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(hours=6),
        )

    async def _async_update_data(self) -> dict:
        try:
            return await self.api.async_fetch_yesterday_consumption()
        except SadalesTiklsApiAuthError as err:
            raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
        except SadalesTiklsApiError as err:
            raise UpdateFailed(str(err)) from err

    async def async_shutdown(self) -> None:
        return None
