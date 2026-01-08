"""Config flow for Kodi Stream Details integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_POLL_INTERVAL,
    CONF_SOURCE_ENTITY,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    MAX_POLL_INTERVAL,
    MIN_POLL_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


def _get_kodi_entities(hass: HomeAssistant) -> list[str]:
    """Get all Kodi media_player entities."""
    entity_registry = er.async_get(hass)
    kodi_entities = []

    for entity_id, entry in entity_registry.entities.items():
        if entry.domain == "media_player" and entry.platform == "kodi":
            kodi_entities.append(entity_id)

    return sorted(kodi_entities)


class KodiStreamDetailsConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kodi Stream Details."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return KodiStreamDetailsOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        # Get available Kodi entities (this is synchronous, no executor needed)
        kodi_entities = _get_kodi_entities(self.hass)

        if not kodi_entities:
            return self.async_abort(reason="no_kodi_entities")

        if user_input is not None:
            source_entity = user_input[CONF_SOURCE_ENTITY]

            # Check if this entity is already configured
            await self.async_set_unique_id(source_entity)
            self._abort_if_unique_id_configured()

            # Validate the entity exists
            if source_entity not in kodi_entities:
                errors["base"] = "invalid_entity"
            else:
                # Get a friendly name for the config entry
                entity_registry = er.async_get(self.hass)
                entry = entity_registry.async_get(source_entity)
                if entry:
                    title = entry.name or entry.original_name or source_entity
                else:
                    title = source_entity
                title = title.replace("media_player.", "").replace("_", " ").title()

                return self.async_create_entry(
                    title=f"{title} Stream Details",
                    data={CONF_SOURCE_ENTITY: source_entity},
                )

        # Build schema with available Kodi entities
        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE_ENTITY): vol.In(kodi_entities),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )


class KodiStreamDetailsOptionsFlow(OptionsFlow):
    """Handle options flow for Kodi Stream Details."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values
        current_poll_interval = self.config_entry.options.get(
            CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL
        )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current_poll_interval,
                ): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_POLL_INTERVAL, max=MAX_POLL_INTERVAL),
                ),
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )
