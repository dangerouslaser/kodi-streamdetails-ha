"""Sensor platform for Kodi Stream Details."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SOURCE_ENTITY, DOMAIN, SENSOR_TYPES
from .coordinator import KodiStreamDetailsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kodi Stream Details sensors from a config entry."""
    coordinator: KodiStreamDetailsCoordinator = hass.data[DOMAIN][entry.entry_id]
    source_entity_id = entry.data[CONF_SOURCE_ENTITY]

    # Get device info from the source Kodi entity
    device_info = await _get_device_info(hass, source_entity_id, entry)

    # Create all sensor entities
    entities = [
        KodiStreamDetailsSensor(
            coordinator=coordinator,
            sensor_type=sensor_type,
            device_info=device_info,
            source_entity_id=source_entity_id,
        )
        for sensor_type in SENSOR_TYPES
    ]

    async_add_entities(entities)


async def _get_device_info(
    hass: HomeAssistant, source_entity_id: str, entry: ConfigEntry
) -> DeviceInfo:
    """Get device info from the source Kodi entity."""
    from homeassistant.helpers import device_registry as dr, entity_registry as er

    entity_registry = er.async_get(hass)
    device_registry = dr.async_get(hass)

    # Get the source entity
    source_entry = entity_registry.async_get(source_entity_id)

    if source_entry and source_entry.device_id:
        # Get the device from the source entity
        device = device_registry.async_get(source_entry.device_id)
        if device:
            # Return device info that links to the same device
            return DeviceInfo(
                identifiers=device.identifiers,
            )

    # Fallback: create our own device info based on entity ID
    entity_name = source_entity_id.replace("media_player.", "").replace("_", " ").title()
    return DeviceInfo(
        identifiers={(DOMAIN, source_entity_id)},
        name=f"{entity_name} Stream Details",
        manufacturer="Kodi",
        model="Stream Details",
    )


class KodiStreamDetailsSensor(CoordinatorEntity[KodiStreamDetailsCoordinator], SensorEntity):
    """Sensor for Kodi stream details."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: KodiStreamDetailsCoordinator,
        sensor_type: str,
        device_info: DeviceInfo,
        source_entity_id: str,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_device_info = device_info
        self._attr_unique_id = f"{source_entity_id}_{sensor_type}"
        self._attr_translation_key = sensor_type

        # Get sensor config from SENSOR_TYPES
        sensor_config = SENSOR_TYPES.get(sensor_type, {})
        self._attr_name = sensor_config.get("name", sensor_type.replace("_", " ").title())
        self._attr_icon = sensor_config.get("icon")
        self._attr_native_unit_of_measurement = sensor_config.get("unit")

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        data = self.coordinator.data

        # For certain sensors, show display name as state value
        if self._sensor_type == "video_codec":
            return data.get("video_codec_display") or data.get("video_codec")
        if self._sensor_type == "video_hdr_type":
            return data.get("video_hdr_type_display") or data.get("video_hdr_type")
        if self._sensor_type == "audio_codec":
            return data.get("audio_codec_display") or data.get("audio_codec")

        return data.get(self._sensor_type)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return additional attributes based on sensor type."""
        if self.coordinator.data is None:
            return None

        data = self.coordinator.data
        attrs: dict[str, Any] = {}

        # Add relevant attributes based on sensor type
        if self._sensor_type == "video_codec":
            if data.get("video_codec_raw"):
                attrs["raw_codec"] = data["video_codec_raw"]
            if data.get("video_codec"):
                attrs["normalized"] = data["video_codec"]

        elif self._sensor_type == "video_resolution":
            if data.get("video_width"):
                attrs["width"] = data["video_width"]
            if data.get("video_height"):
                attrs["height"] = data["video_height"]

        elif self._sensor_type == "video_aspect":
            if data.get("video_aspect_raw"):
                attrs["raw_aspect"] = data["video_aspect_raw"]

        elif self._sensor_type == "video_hdr_type":
            if data.get("video_hdr_type_raw"):
                attrs["raw_hdrtype"] = data["video_hdr_type_raw"]
            if data.get("video_hdr_type"):
                attrs["normalized"] = data["video_hdr_type"]

        elif self._sensor_type == "video_duration":
            if data.get("video_duration_formatted"):
                attrs["formatted"] = data["video_duration_formatted"]

        elif self._sensor_type == "audio_codec":
            if data.get("audio_codec_raw"):
                attrs["raw_codec"] = data["audio_codec_raw"]
            if data.get("audio_codec"):
                attrs["normalized"] = data["audio_codec"]

        elif self._sensor_type == "audio_channels":
            if data.get("audio_channels_raw"):
                attrs["raw_channels"] = data["audio_channels_raw"]

        elif self._sensor_type == "audio_language":
            if data.get("audio_language_name"):
                attrs["language_name"] = data["audio_language_name"]

        elif self._sensor_type == "audio_bitrate":
            if data.get("audio_bitrate_formatted"):
                attrs["formatted"] = data["audio_bitrate_formatted"]

        elif self._sensor_type == "audio_stream_count":
            if data.get("audio_streams"):
                attrs["streams"] = data["audio_streams"]

        elif self._sensor_type == "subtitle_language":
            if data.get("subtitle_language_name"):
                attrs["language_name"] = data["subtitle_language_name"]

        elif self._sensor_type == "subtitle_stream_count":
            if data.get("subtitle_streams"):
                attrs["streams"] = data["subtitle_streams"]

        elif self._sensor_type == "playback_type":
            attrs["media_type"] = data.get("playback_type")

        return attrs if attrs else None

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
