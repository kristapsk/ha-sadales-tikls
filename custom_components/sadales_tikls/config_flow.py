from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import SadalesTiklsApiAuthError, SadalesTiklsApiClient, SadalesTiklsApiError
from .const import CONF_API_KEY, CONF_MNR, CONF_MPNR, CONF_OEIC, DEFAULT_NAME, DOMAIN


class SadalesTiklsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(f"{user_input[CONF_OEIC]}_{user_input[CONF_MPNR]}_{user_input[CONF_MNR]}")
            self._abort_if_unique_id_configured()

            api = SadalesTiklsApiClient(
                api_key=user_input[CONF_API_KEY],
                oeic=user_input[CONF_OEIC],
                mp_nr=user_input[CONF_MPNR],
                m_nr=user_input[CONF_MNR],
                session=async_get_clientsession(self.hass),
            )
            try:
                await api.async_fetch_yesterday_consumption()
            except SadalesTiklsApiAuthError:
                errors["base"] = "invalid_auth"
            except SadalesTiklsApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): str,
                vol.Required(CONF_OEIC): str,
                vol.Required(CONF_MPNR): str,
                vol.Required(CONF_MNR): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
