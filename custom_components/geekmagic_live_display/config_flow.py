"""Config flow for GeekMagic Live Display."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST
from homeassistant.data_entry_flow import FlowResult

from .api import GeekMagicClient, GeekMagicError
from .const import DOMAIN


class GeekMagicLiveDisplayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for GeekMagic Live Display."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            client = GeekMagicClient(self.hass, user_input[CONF_HOST])
            try:
                device_info = await client.async_validate()
            except GeekMagicError:
                errors["base"] = "cannot_connect"
            else:
                model = device_info.get("m", "GeekMagic SmallTV")
                version = device_info.get("v", "")
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"{model} {version}".strip(),
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )
