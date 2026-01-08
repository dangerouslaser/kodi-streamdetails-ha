"""The Kodi Stream Details integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_SOURCE_ENTITY, DOMAIN
from .coordinator import KodiStreamDetailsCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Kodi Stream Details from a config entry."""
    source_entity_id = entry.data[CONF_SOURCE_ENTITY]

    # Verify the source entity exists
    state = hass.states.get(source_entity_id)
    if state is None:
        _LOGGER.error(
            "Source Kodi entity %s not found. Please reconfigure the integration.",
            source_entity_id,
        )
        return False

    # Create the coordinator
    coordinator = KodiStreamDetailsCoordinator(
        hass=hass,
        source_entity_id=source_entity_id,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
