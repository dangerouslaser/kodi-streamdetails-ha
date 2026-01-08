"""Data coordinator for Kodi Stream Details."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    AUDIO_CODEC_DISPLAY,
    AUDIO_CODEC_MAP,
    ASPECT_RATIO_NAMES,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
    HDR_TYPE_DISPLAY,
    HDR_TYPE_MAP,
    LANGUAGE_NAMES,
    RESOLUTION_THRESHOLDS,
    VIDEO_CODEC_DISPLAY,
    VIDEO_CODEC_MAP,
)

_LOGGER = logging.getLogger(__name__)


class KodiStreamDetailsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch stream details from Kodi."""

    def __init__(
        self,
        hass: HomeAssistant,
        source_entity_id: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )
        self.source_entity_id = source_entity_id
        self._kodi = None

    async def _get_kodi_connection(self) -> Any:
        """Get the Kodi connection from the media_player entity."""
        # Return cached connection if available
        if self._kodi is not None:
            return self._kodi

        # Get the entity from the state machine to verify it exists
        state = self.hass.states.get(self.source_entity_id)
        if state is None:
            raise UpdateFailed(f"Entity {self.source_entity_id} not found")

        # Try to get the entity from the media_player domain data
        entity = None

        # Method 1: Try entity_components (newer HA versions)
        entity_components = self.hass.data.get("entity_components", {})
        mp_component = entity_components.get("media_player")
        if mp_component is not None:
            if hasattr(mp_component, "get_entity"):
                entity = mp_component.get_entity(self.source_entity_id)
            elif hasattr(mp_component, "entities"):
                for ent in mp_component.entities:
                    if ent.entity_id == self.source_entity_id:
                        entity = ent
                        break

        # Method 2: Try media_player domain directly
        if entity is None:
            mp_data = self.hass.data.get("media_player")
            if mp_data is not None:
                if hasattr(mp_data, "get_entity"):
                    entity = mp_data.get_entity(self.source_entity_id)
                elif hasattr(mp_data, "entities"):
                    for ent in mp_data.entities:
                        if ent.entity_id == self.source_entity_id:
                            entity = ent
                            break

        # Method 3: Search through all data for entity platforms
        if entity is None:
            for key, value in self.hass.data.items():
                if hasattr(value, "get_entity"):
                    try:
                        entity = value.get_entity(self.source_entity_id)
                        if entity is not None:
                            break
                    except Exception:
                        pass
                elif hasattr(value, "entities"):
                    try:
                        for ent in value.entities:
                            if hasattr(ent, "entity_id") and ent.entity_id == self.source_entity_id:
                                entity = ent
                                break
                        if entity is not None:
                            break
                    except Exception:
                        pass

        if entity is None:
            raise UpdateFailed(
                f"Could not find entity object for {self.source_entity_id}. "
                "Make sure the Kodi integration is fully loaded."
            )

        # Get the Kodi connection - it's stored as _kodi on the entity
        kodi = getattr(entity, "_kodi", None)
        if kodi is None:
            # Try alternate attribute names
            kodi = getattr(entity, "kodi", None)
            if kodi is None:
                kodi = getattr(entity, "_player", None)

        if kodi is None:
            raise UpdateFailed(
                f"Could not get Kodi connection from entity {self.source_entity_id}. "
                "The entity may not be a Kodi media player."
            )

        # Cache for future use
        self._kodi = kodi
        return kodi

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Kodi."""
        try:
            kodi = await self._get_kodi_connection()

            # Get active players
            players = await kodi.call_method("Player.GetActivePlayers")

            if not players:
                return self._empty_state()

            player_id = players[0]["playerid"]
            player_type = players[0].get("type", "video")

            # Get item with stream details
            item_result = await kodi.call_method(
                "Player.GetItem",
                {
                    "playerid": player_id,
                    "properties": ["streamdetails", "title", "showtitle", "season", "episode", "type"],
                },
            )

            # Get current stream selection
            props = await kodi.call_method(
                "Player.GetProperties",
                {
                    "playerid": player_id,
                    "properties": [
                        "currentaudiostream",
                        "currentsubtitle",
                        "subtitleenabled",
                        "audiostreams",
                        "subtitles",
                    ],
                },
            )

            return self._parse_stream_data(item_result, props, player_type)

        except UpdateFailed:
            raise
        except Exception as err:
            _LOGGER.error("Error fetching Kodi data: %s", err)
            raise UpdateFailed(f"Error fetching Kodi data: {err}") from err

    def _parse_stream_data(
        self, item_result: dict[str, Any], props: dict[str, Any], player_type: str
    ) -> dict[str, Any]:
        """Parse and normalize stream details."""
        item = item_result.get("item", {})
        streamdetails = item.get("streamdetails", {})

        # Video from streamdetails (only source for hdrtype)
        video_streams = streamdetails.get("video", [])
        video = video_streams[0] if video_streams else {}

        # Audio/subtitles from Player.GetProperties (richer data, Atmos detection)
        audio_streams = props.get("audiostreams", [])
        subtitle_streams = props.get("subtitles", [])
        current_audio = props.get("currentaudiostream", {})
        current_subtitle = props.get("currentsubtitle", {})
        subtitle_enabled = props.get("subtitleenabled", False)

        # Normalize values
        video_codec_raw = video.get("codec", "")
        video_codec = self._normalize_video_codec(video_codec_raw)
        video_width = video.get("width", 0)
        video_height = video.get("height", 0)
        video_aspect_raw = video.get("aspect", 0)
        video_hdr_raw = video.get("hdrtype", "")
        video_duration = video.get("duration", 0)

        audio_codec_raw = current_audio.get("codec", "") if current_audio else ""
        audio_codec = self._normalize_audio_codec(audio_codec_raw)
        audio_channels_raw = current_audio.get("channels", 0) if current_audio else 0
        audio_language = current_audio.get("language", "") if current_audio else ""

        subtitle_language = current_subtitle.get("language", "") if subtitle_enabled and current_subtitle else "off"

        # Determine playback type
        playback_type = item.get("type", "unknown")
        if playback_type == "unknown" and player_type == "audio":
            playback_type = "song"

        return {
            # Video (from streamdetails)
            "video_codec": video_codec,
            "video_codec_raw": video_codec_raw,
            "video_codec_display": VIDEO_CODEC_DISPLAY.get(video_codec, video_codec.upper() if video_codec else None),
            "video_width": video_width if video_width else None,
            "video_height": video_height if video_height else None,
            "video_resolution": self._derive_resolution(video_width),
            "video_aspect": self._format_aspect(video_aspect_raw),
            "video_aspect_raw": video_aspect_raw if video_aspect_raw else None,
            "video_hdr_type": HDR_TYPE_MAP.get(video_hdr_raw, video_hdr_raw or "sdr"),
            "video_hdr_type_raw": video_hdr_raw,
            "video_hdr_type_display": HDR_TYPE_DISPLAY.get(
                HDR_TYPE_MAP.get(video_hdr_raw, "sdr"), "SDR"
            ),
            "video_stereo_mode": video.get("stereomode", "") or "2d",
            "video_duration": video_duration if video_duration else None,
            "video_duration_formatted": self._format_duration(video_duration),
            # Audio (from Player.GetProperties - includes Atmos detection)
            "audio_codec": audio_codec,
            "audio_codec_raw": audio_codec_raw,
            "audio_codec_display": AUDIO_CODEC_DISPLAY.get(audio_codec, audio_codec.upper() if audio_codec else None),
            "audio_channels": self._format_channels(audio_channels_raw),
            "audio_channels_raw": audio_channels_raw if audio_channels_raw else None,
            "audio_language": audio_language if audio_language else None,
            "audio_language_name": LANGUAGE_NAMES.get(audio_language, audio_language),
            "audio_name": current_audio.get("name", "") if current_audio else None,
            "audio_bitrate": current_audio.get("bitrate", 0) if current_audio else None,
            "audio_bitrate_formatted": self._format_bitrate(current_audio.get("bitrate", 0) if current_audio else 0),
            "audio_stream_index": current_audio.get("index", 0) if current_audio else None,
            "audio_stream_count": len(audio_streams),
            "audio_streams": audio_streams,
            "audio_is_default": "on" if current_audio and current_audio.get("isdefault", False) else "off",
            "audio_is_original": "on" if current_audio and current_audio.get("isoriginal", False) else "off",
            # Subtitles (from Player.GetProperties - includes track names)
            "subtitle_enabled": "on" if subtitle_enabled else "off",
            "subtitle_language": subtitle_language if subtitle_language else None,
            "subtitle_language_name": LANGUAGE_NAMES.get(subtitle_language, subtitle_language) if subtitle_enabled else None,
            "subtitle_name": current_subtitle.get("name", "") if subtitle_enabled and current_subtitle else None,
            "subtitle_stream_index": current_subtitle.get("index", 0) if subtitle_enabled and current_subtitle else None,
            "subtitle_stream_count": len(subtitle_streams),
            "subtitle_streams": subtitle_streams,
            "subtitle_is_forced": "on" if current_subtitle and current_subtitle.get("isforced", False) else "off",
            "subtitle_is_impaired": "on" if current_subtitle and current_subtitle.get("isimpaired", False) else "off",
            # Playback
            "playback_type": playback_type,
        }

    def _empty_state(self) -> dict[str, Any]:
        """Return empty state when nothing is playing."""
        return {
            "video_codec": None,
            "video_codec_raw": None,
            "video_codec_display": None,
            "video_width": None,
            "video_height": None,
            "video_resolution": None,
            "video_aspect": None,
            "video_aspect_raw": None,
            "video_hdr_type": None,
            "video_hdr_type_raw": None,
            "video_hdr_type_display": None,
            "video_stereo_mode": None,
            "video_duration": None,
            "video_duration_formatted": None,
            "audio_codec": None,
            "audio_codec_raw": None,
            "audio_codec_display": None,
            "audio_channels": None,
            "audio_channels_raw": None,
            "audio_language": None,
            "audio_language_name": None,
            "audio_name": None,
            "audio_bitrate": None,
            "audio_bitrate_formatted": None,
            "audio_stream_index": None,
            "audio_stream_count": 0,
            "audio_streams": [],
            "audio_is_default": "off",
            "audio_is_original": "off",
            "subtitle_enabled": "off",
            "subtitle_language": "off",
            "subtitle_language_name": None,
            "subtitle_name": None,
            "subtitle_stream_index": None,
            "subtitle_stream_count": 0,
            "subtitle_streams": [],
            "subtitle_is_forced": "off",
            "subtitle_is_impaired": "off",
            "playback_type": "idle",
        }

    def _normalize_video_codec(self, codec: str) -> str | None:
        """Normalize video codec string."""
        if not codec:
            return None
        codec_lower = codec.lower()
        return VIDEO_CODEC_MAP.get(codec_lower, codec_lower)

    def _normalize_audio_codec(self, codec: str) -> str | None:
        """Normalize audio codec string."""
        if not codec:
            return None
        codec_lower = codec.lower()
        # Handle PCM variants
        if codec_lower.startswith("pcm"):
            return "pcm"
        return AUDIO_CODEC_MAP.get(codec_lower, codec_lower)

    def _derive_resolution(self, width: int) -> str | None:
        """Derive resolution label from video width."""
        if not width:
            return None
        for threshold, label in RESOLUTION_THRESHOLDS:
            if width >= threshold:
                return label
        return "SD"

    def _format_aspect(self, aspect: float) -> str | None:
        """Format aspect ratio to human-readable string."""
        if not aspect:
            return None
        # Check for known aspect ratios (with tolerance)
        for known_aspect, name in ASPECT_RATIO_NAMES.items():
            if abs(aspect - known_aspect) < 0.05:
                return name
        # Format as X.XX:1
        return f"{aspect:.2f}:1"

    def _format_channels(self, channels: int) -> str | None:
        """Format channel count to standard notation."""
        if not channels:
            return None
        # Standard channel layouts
        channel_map = {
            1: "1.0",
            2: "2.0",
            3: "2.1",
            6: "5.1",
            7: "6.1",
            8: "7.1",
        }
        return channel_map.get(channels, f"{channels}.0")

    def _format_duration(self, seconds: int) -> str | None:
        """Format duration in seconds to HH:MM:SS."""
        if not seconds:
            return None
        hours, remainder = divmod(seconds, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def _format_bitrate(self, bitrate: int) -> str | None:
        """Format bitrate to human-readable string."""
        if not bitrate:
            return None
        if bitrate >= 1000000:
            return f"{bitrate / 1000000:.1f} Mbps"
        if bitrate >= 1000:
            return f"{bitrate / 1000:.0f} kbps"
        return f"{bitrate} bps"
