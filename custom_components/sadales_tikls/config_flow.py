from __future__ import annotations

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SadalesTiklsApiAuthError, SadalesTiklsApiClient, SadalesTiklsApiError
from .const import CONF_API_KEY, CONF_MNR, CONF_MPNR, CONF_OEIC, DEFAULT_NAME, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _clean(value: str) -> str:
    return value.strip().replace("\u00a0", "").replace("\u200b", "").replace("\ufeff", "")


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = {
                CONF_API_KEY: _clean(user_input[CONF_API_KEY]),
                CONF_OEIC: _clean(user_input[CONF_OEIC]),
                CONF_MPNR: _clean(user_input[CONF_MPNR]),
                CONF_MNR: _clean(user_input[CONF_MNR]),
            }

            api = SadalesTiklsApiClient(
                api_key=cleaned[CONF_API_KEY],
                oeic=cleaned[CONF_OEIC],
                mp_nr=cleaned[CONF_MPNR],
                m_nr=cleaned[CONF_MNR],
                session=async_get_clientsession(self.hass),
            )

            try:
                data = await api.async_fetch_yesterday_consumption()
                _LOGGER.debug("Sadales tikls API validation OK: %s", data.get("source_url"))
            except SadalesTiklsApiAuthError as err:
                _LOGGER.error("Sadales tikls AUTH failed: %s", err)
                errors["base"] = "invalid_auth"
            except SadalesTiklsApiError as err:
                _LOGGER.error("Sadales tikls API failed: %s", err)
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Sadales tikls unexpected error")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(
                    f"{cleaned[CONF_OEIC]}_{cleaned[CONF_MPNR]}_{cleaned[CONF_MNR]}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=DEFAULT_NAME, data=cleaned)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_OEIC): str,
                vol.Required(CONF_MPNR): str,
                vol.Required(CONF_MNR): str,
            }),
            errors=errors,
        )
