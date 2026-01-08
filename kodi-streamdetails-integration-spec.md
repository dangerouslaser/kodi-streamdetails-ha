# Kodi Stream Details Integration for Home Assistant

## Overview

A custom Home Assistant integration that extends the native Kodi integration by exposing detailed stream metadata as discrete sensors. The integration "links" to an existing `media_player.kodi` entity and creates child sensors for video, audio, and subtitle stream properties.

## Goals

- Expose all `streamdetails` properties from Kodi's JSON-RPC API as individual sensors
- Link to existing Kodi integration devices (no duplicate configuration)
- Support multiple Kodi instances
- Real-time updates via Kodi WebSocket notifications
- Graceful handling of playback states (stopped, paused, playing, nothing loaded)

---

## Configuration

### Config Flow (UI-based setup)

1. User adds integration via Home Assistant UI
2. Integration discovers existing Kodi `media_player` entities
3. User selects which Kodi entity to link
4. Integration creates sensor entities as children of the selected device

```yaml
# Example resulting config entry
kodi_streamdetails:
  source_entity: media_player.kodi_living_room
```

### Options Flow

- **Polling interval**: Fallback polling rate if WebSocket unavailable (default: 5 seconds)
- **Sensor prefix**: Custom prefix for sensor names (default: uses source entity name)

---

## Entity Structure

All sensors are linked to the parent Kodi device for logical grouping in the UI.

### Device Relationship

```
Device: Kodi Living Room (from native integration)
├── media_player.kodi_living_room (native)
├── sensor.kodi_living_room_video_codec (this integration)
├── sensor.kodi_living_room_video_resolution (this integration)
├── sensor.kodi_living_room_audio_codec (this integration)
└── ... (additional sensors)
```

---

## Sensor Definitions

### Video Stream Sensors

| Sensor ID Suffix | State Value | Attributes | Notes |
|------------------|-------------|------------|-------|
| `video_codec` | `hevc`, `h264`, `vp9`, `av1`, etc. | `raw_codec` | Normalized codec name |
| `video_resolution` | `4K`, `1080p`, `720p`, `480p`, `SD` | `width`, `height` | Derived from width |
| `video_width` | Integer (pixels) | — | Raw width value |
| `video_height` | Integer (pixels) | — | Raw height value |
| `video_aspect` | `2.39:1`, `1.78:1`, `1.33:1`, etc. | `raw_aspect` | Formatted aspect ratio |
| `video_hdr_type` | `dolbyvision`, `hdr10`, `hdr10plus`, `hlg`, `sdr` | `raw_hdrtype` | See HDR mapping below |
| `video_stereo_mode` | `2d`, `sbs`, `tab`, `mvc` | — | 3D format if applicable |
| `video_duration` | Integer (seconds) | `formatted` (HH:MM:SS) | Total runtime |

### Audio Stream Sensors

Data sourced from `Player.GetProperties` (`currentaudiostream`, `audiostreams`) which provides richer metadata than `streamdetails`, including Atmos detection.

| Sensor ID Suffix | State Value | Attributes | Notes |
|------------------|-------------|------------|-------|
| `audio_codec` | `truehd_atmos`, `truehd`, `eac3_atmos`, `dtshd_ma`, etc. | `raw_codec`, `display_name` | Normalized codec with Atmos detection |
| `audio_channels` | `7.1`, `5.1`, `2.0`, `1.0` | `raw_channels` | Formatted channel layout |
| `audio_language` | `eng`, `spa`, `jpn`, etc. | `language_name` | ISO 639-2 code |
| `audio_name` | Full track name | — | e.g., "TrueHD Atmos 7.1 - TrueHD ATMOS 7.1" |
| `audio_bitrate` | Integer (bps) or `0` | `formatted` | May be 0 for lossless codecs |
| `audio_stream_index` | Integer | — | Currently selected stream index |
| `audio_stream_count` | Integer | `streams` (list) | Total available audio streams |
| `audio_is_default` | `on` / `off` | — | Whether this is the default track |
| `audio_is_original` | `on` / `off` | — | Whether this is the original language track |

### Subtitle Stream Sensors

Data sourced from `Player.GetProperties` (`currentsubtitle`, `subtitles`) which provides track names and flags.

| Sensor ID Suffix | State Value | Attributes | Notes |
|------------------|-------------|------------|-------|
| `subtitle_enabled` | `on` / `off` | — | Whether subtitles are active |
| `subtitle_language` | `eng`, `spa`, `off`, etc. | `language_name` | Current subtitle language |
| `subtitle_name` | Full track name | — | e.g., "English (SDH)", "French (Canadian)" |
| `subtitle_stream_index` | Integer | — | Currently selected stream index |
| `subtitle_stream_count` | Integer | `streams` (list) | Total available subtitle streams |
| `subtitle_is_forced` | `on` / `off` | — | Whether this is a forced subtitle track |
| `subtitle_is_impaired` | `on` / `off` | — | Whether this is an SDH/CC track |

### Playback State Sensor

| Sensor ID Suffix | State Value | Attributes | Notes |
|------------------|-------------|------------|-------|
| `playback_type` | `movie`, `episode`, `musicvideo`, `song`, `unknown`, `idle` | `media_type` | Content type being played |

---

## HDR Type Mapping

Kodi's `hdrtype` field values mapped to sensor states:

| Kodi `hdrtype` | Sensor State | Display Name |
|----------------|--------------|--------------|
| `dolbyvision` | `dolbyvision` | DV |
| `hdr10` | `hdr10` | HDR10 |
| `hdr10plus` | `hdr10plus` | HDR10+ |
| `hlg` | `hlg` | HLG |
| `` (empty) | `sdr` | SDR |

---

## Audio Codec Normalization

Map Kodi's codec strings to friendly names. Note: Atmos detection requires using `Player.GetProperties` (`currentaudiostream`), not `streamdetails`—the latter only returns base codec without Atmos flag.

| Kodi Codec | Normalized | Display Name |
|------------|------------|--------------|
| `truehd_atmos` | `truehd_atmos` | Dolby TrueHD Atmos |
| `truehd` | `truehd` | Dolby TrueHD |
| `eac3_atmos` | `eac3_atmos` | Dolby Digital+ Atmos |
| `eac3` | `eac3` | Dolby Digital+ |
| `ac3` | `ac3` | Dolby Digital |
| `dtshd_ma` | `dtshd_ma` | DTS-HD MA |
| `dtshd_hra` | `dtshd_hra` | DTS-HD HRA |
| `dtsx` | `dtsx` | DTS:X |
| `dca` | `dts` | DTS |
| `dts` | `dts` | DTS |
| `aac` | `aac` | AAC |
| `flac` | `flac` | FLAC |
| `pcm*` | `pcm` | PCM |
| `opus` | `opus` | Opus |

---

## Video Codec Normalization

| Kodi Codec | Normalized | Display Name |
|------------|------------|--------------|
| `hevc` | `hevc` | HEVC / H.265 |
| `h264` / `avc1` | `h264` | H.264 / AVC |
| `vp9` | `vp9` | VP9 |
| `av1` | `av1` | AV1 |
| `mpeg2video` | `mpeg2` | MPEG-2 |
| `vc1` | `vc1` | VC-1 |

---

## Resolution Derivation

Derive resolution label from video width. Width is used instead of height because height varies with aspect ratio (e.g., a 2.39:1 cinemascope 4K film is 3840×1600, not 3840×2160).

```python
def derive_resolution(width: int) -> str:
    if width >= 3840:
        return "4K"
    elif width >= 1920:
        return "1080p"
    elif width >= 1280:
        return "720p"
    elif width >= 720:
        return "480p"
    else:
        return "SD"
```

| Width | Aspect Ratio | Actual Resolution | Derived Label |
|-------|--------------|-------------------|---------------|
| 3840 | 16:9 | 3840×2160 | 4K |
| 3840 | 2.39:1 | 3840×1600 | 4K |
| 4096 | DCI | 4096×2160 | 4K |
| 1920 | 16:9 | 1920×1080 | 1080p |
| 1920 | 2.39:1 | 1920×800 | 1080p |
| 1280 | 16:9 | 1280×720 | 720p |

---

## Implementation Architecture

### Component Structure

```
custom_components/
└── kodi_streamdetails/
    ├── __init__.py           # Integration setup, WebSocket listener
    ├── manifest.json
    ├── config_flow.py        # UI configuration
    ├── const.py              # Constants, mappings
    ├── coordinator.py        # DataUpdateCoordinator
    ├── sensor.py             # Sensor entity definitions
    ├── strings.json          # UI strings
    └── translations/
        └── en.json
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     Home Assistant                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              DataUpdateCoordinator                       │    │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │    │
│  │  │ WebSocket       │    │ Polling Fallback            │ │    │
│  │  │ (Player.OnPlay, │ OR │ (kodi.call_method every N s)│ │    │
│  │  │  Player.OnStop) │    │                             │ │    │
│  │  └────────┬────────┘    └──────────────┬──────────────┘ │    │
│  │           │                            │                 │    │
│  │           └────────────┬───────────────┘                 │    │
│  │                        ▼                                 │    │
│  │              ┌─────────────────┐                         │    │
│  │              │ Parse & Normalize│                        │    │
│  │              │ Stream Details   │                        │    │
│  │              └────────┬────────┘                         │    │
│  │                       ▼                                  │    │
│  │              ┌─────────────────┐                         │    │
│  │              │ Update Sensors  │                         │    │
│  │              └─────────────────┘                         │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

### JSON-RPC Methods Used

**Get active players:**
```json
{
  "jsonrpc": "2.0",
  "method": "Player.GetActivePlayers",
  "id": 1
}
```

**Get current item with stream details:**
```json
{
  "jsonrpc": "2.0",
  "method": "Player.GetItem",
  "params": {
    "playerid": 1,
    "properties": ["streamdetails", "file", "title", "showtitle", "season", "episode"]
  },
  "id": 2
}
```

**Get playback properties (for current audio/subtitle stream):**
```json
{
  "jsonrpc": "2.0",
  "method": "Player.GetProperties",
  "params": {
    "playerid": 1,
    "properties": ["currentaudiostream", "currentsubtitle", "subtitleenabled", "audiostreams", "subtitles"]
  },
  "id": 3
}
```

### Example Responses

**Player.GetItem response (for video stream details with HDR type):**
```json
{
  "item": {
    "streamdetails": {
      "video": [
        {
          "codec": "hevc",
          "aspect": 1.78,
          "width": 3840,
          "height": 2160,
          "duration": 7139,
          "stereomode": "",
          "hdrtype": "dolbyvision"
        }
      ],
      "audio": [
        {
          "codec": "truehd",
          "channels": 8,
          "language": "eng"
        }
      ]
    }
  }
}
```

**Player.GetProperties response (for audio/subtitle with Atmos detection):**
```json
{
  "currentaudiostream": {
    "bitrate": 0,
    "channels": 8,
    "codec": "truehd_atmos",
    "index": 0,
    "isdefault": true,
    "isimpaired": false,
    "isoriginal": false,
    "language": "eng",
    "name": "TrueHD Atmos 7.1 - TrueHD ATMOS 7.1",
    "samplerate": 0
  },
  "audiostreams": [
    {
      "bitrate": 0,
      "channels": 8,
      "codec": "truehd_atmos",
      "index": 0,
      "isdefault": true,
      "isimpaired": false,
      "isoriginal": false,
      "language": "eng",
      "name": "TrueHD Atmos 7.1 - TrueHD ATMOS 7.1"
    }
  ],
  "currentsubtitle": {
    "index": 0,
    "isdefault": false,
    "isforced": false,
    "isimpaired": false,
    "language": "eng",
    "name": "English (SDH)"
  },
  "subtitleenabled": false
}
```

**Key insight:** `streamdetails.audio` returns `"codec": "truehd"` while `currentaudiostream` returns `"codec": "truehd_atmos"`. The integration uses `Player.GetProperties` for audio/subtitle data to capture Atmos and track metadata.

---

## Coordinator Implementation

```python
class KodiStreamDetailsCoordinator(DataUpdateCoordinator):
    """Coordinator to fetch stream details from Kodi."""

    def __init__(self, hass: HomeAssistant, source_entity_id: str) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
        )
        self.source_entity_id = source_entity_id
        self._kodi_entity = None

    async def _async_update_data(self) -> dict:
        """Fetch data from Kodi."""
        try:
            # Get active players
            players = await self._call_kodi_method("Player.GetActivePlayers")
            
            if not players:
                return self._empty_state()
            
            player_id = players[0]["playerid"]
            
            # Get item with stream details
            item = await self._call_kodi_method(
                "Player.GetItem",
                playerid=player_id,
                properties=["streamdetails", "title", "showtitle", "season", "episode"]
            )
            
            # Get current stream selection
            props = await self._call_kodi_method(
                "Player.GetProperties",
                playerid=player_id,
                properties=[
                    "currentaudiostream",
                    "currentsubtitle", 
                    "subtitleenabled",
                    "audiostreams",
                    "subtitles"
                ]
            )
            
            return self._parse_stream_data(item, props)
            
        except Exception as err:
            raise UpdateFailed(f"Error fetching Kodi data: {err}")

    async def _call_kodi_method(self, method: str, **params) -> dict:
        """Call Kodi JSON-RPC method via HA service."""
        result = await self.hass.services.async_call(
            "kodi",
            "call_method",
            {
                "entity_id": self.source_entity_id,
                "method": method,
                **params
            },
            blocking=True,
            return_response=True
        )
        return result

    def _parse_stream_data(self, item: dict, props: dict) -> dict:
        """Parse and normalize stream details.
        
        Video data comes from streamdetails (has hdrtype).
        Audio/subtitle data comes from Player.GetProperties (has Atmos detection, track names).
        """
        streamdetails = item.get("item", {}).get("streamdetails", {})
        
        # Video from streamdetails (only source for hdrtype)
        video = streamdetails.get("video", [{}])[0] if streamdetails.get("video") else {}
        
        # Audio/subtitles from Player.GetProperties (richer data, Atmos detection)
        audio_streams = props.get("audiostreams", [])
        subtitle_streams = props.get("subtitles", [])
        current_audio = props.get("currentaudiostream", {})
        current_subtitle = props.get("currentsubtitle", {})
        
        return {
            # Video (from streamdetails)
            "video_codec": self._normalize_video_codec(video.get("codec", "")),
            "video_width": video.get("width", 0),
            "video_height": video.get("height", 0),
            "video_resolution": self._derive_resolution(video.get("width", 0)),
            "video_aspect": self._format_aspect(video.get("aspect", 0)),
            "video_hdr_type": video.get("hdrtype", "") or "sdr",
            "video_stereo_mode": video.get("stereomode", "") or "2d",
            "video_duration": video.get("duration", 0),
            
            # Audio (from Player.GetProperties - includes Atmos detection)
            "audio_codec": self._normalize_audio_codec(current_audio.get("codec", "")),
            "audio_channels": self._format_channels(current_audio.get("channels", 0)),
            "audio_language": current_audio.get("language", ""),
            "audio_name": current_audio.get("name", ""),
            "audio_bitrate": current_audio.get("bitrate", 0),
            "audio_stream_index": current_audio.get("index", 0),
            "audio_stream_count": len(audio_streams),
            "audio_streams": audio_streams,
            "audio_is_default": current_audio.get("isdefault", False),
            "audio_is_original": current_audio.get("isoriginal", False),
            
            # Subtitles (from Player.GetProperties - includes track names)
            "subtitle_enabled": props.get("subtitleenabled", False),
            "subtitle_language": current_subtitle.get("language", "") if props.get("subtitleenabled") else "off",
            "subtitle_name": current_subtitle.get("name", "") if props.get("subtitleenabled") else "",
            "subtitle_stream_index": current_subtitle.get("index", 0),
            "subtitle_stream_count": len(subtitle_streams),
            "subtitle_streams": subtitle_streams,
            "subtitle_is_forced": current_subtitle.get("isforced", False),
            "subtitle_is_impaired": current_subtitle.get("isimpaired", False),
            
            # Playback
            "playback_type": item.get("item", {}).get("type", "unknown"),
        }

    def _empty_state(self) -> dict:
        """Return empty state when nothing is playing."""
        return {
            "video_codec": None,
            "video_width": None,
            "video_height": None,
            "video_resolution": None,
            "video_aspect": None,
            "video_hdr_type": None,
            "video_stereo_mode": None,
            "video_duration": None,
            "audio_codec": None,
            "audio_channels": None,
            "audio_language": None,
            "audio_name": None,
            "audio_bitrate": None,
            "audio_stream_index": None,
            "audio_stream_count": 0,
            "audio_streams": [],
            "audio_is_default": False,
            "audio_is_original": False,
            "subtitle_enabled": False,
            "subtitle_language": "off",
            "subtitle_name": None,
            "subtitle_stream_index": None,
            "subtitle_stream_count": 0,
            "subtitle_streams": [],
            "subtitle_is_forced": False,
            "subtitle_is_impaired": False,
            "playback_type": "idle",
        }
```

---

## Sensor Entity Definition

```python
class KodiStreamDetailsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for Kodi stream details."""

    def __init__(
        self,
        coordinator: KodiStreamDetailsCoordinator,
        sensor_type: str,
        device_info: DeviceInfo,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_device_info = device_info
        self._attr_unique_id = f"{coordinator.source_entity_id}_{sensor_type}"
        self._attr_name = f"{device_info['name']} {SENSOR_NAMES[sensor_type]}"

    @property
    def native_value(self):
        """Return sensor state."""
        return self.coordinator.data.get(self._sensor_type)

    @property
    def extra_state_attributes(self):
        """Return additional attributes."""
        return SENSOR_ATTRIBUTES.get(self._sensor_type, {}).get(
            self.coordinator.data, {}
        )
```

---

## WebSocket Event Handling (Optional Enhancement)

For real-time updates without polling, subscribe to Kodi WebSocket notifications:

```python
async def async_setup_websocket_listener(hass, coordinator):
    """Set up WebSocket listener for Kodi events."""
    
    # Events to listen for
    KODI_EVENTS = [
        "Player.OnPlay",
        "Player.OnStop", 
        "Player.OnPause",
        "Player.OnResume",
        "Player.OnAVChange",  # Triggered when audio/subtitle stream changes
    ]
    
    async def handle_kodi_event(event):
        """Handle Kodi WebSocket event."""
        if event.data.get("method") in KODI_EVENTS:
            await coordinator.async_request_refresh()
    
    # Subscribe to Kodi events
    hass.bus.async_listen("kodi_event", handle_kodi_event)
```

**Note:** The native Kodi integration may not expose all WebSocket events. If not available, fall back to polling.

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Nothing playing | All sensors show `None` or `idle` |
| Audio-only content | Video sensors show `None`, audio sensors populate |
| No audio streams | Audio sensors show `None` |
| Multiple video streams | Use first video stream (primary) |
| Kodi unavailable | Sensors show `unavailable` |
| Playback paused | Sensors retain current values |
| Live TV / PVR | May have limited or no stream details |

---

## Example Automations

### Announce HDR Content

```yaml
automation:
  - alias: "Announce Dolby Vision Content"
    trigger:
      - platform: state
        entity_id: sensor.kodi_living_room_video_hdr_type
        to: "dolbyvision"
    action:
      - service: tts.speak
        target:
          entity_id: tts.piper
        data:
          message: "Now playing in Dolby Vision"
```

### Adjust Lights Based on Resolution

```yaml
automation:
  - alias: "Cinema Mode for 4K Content"
    trigger:
      - platform: state
        entity_id: sensor.kodi_living_room_video_resolution
        to: "4K"
    action:
      - service: scene.turn_on
        target:
          entity_id: scene.cinema_mode
```

### Voice Query Integration

```yaml
# Use with voice assistant for queries like "What quality is this?"
intent_script:
  GetPlaybackQuality:
    speech:
      text: >
        {% set codec = states('sensor.kodi_living_room_audio_codec') %}
        {% set hdr = states('sensor.kodi_living_room_video_hdr_type') %}
        {% set codec_name = {
          'truehd_atmos': 'Dolby TrueHD Atmos',
          'truehd': 'Dolby TrueHD',
          'eac3_atmos': 'Dolby Digital Plus Atmos',
          'eac3': 'Dolby Digital Plus',
          'dtshd_ma': 'DTS HD Master Audio',
          'dtsx': 'DTS X',
          'ac3': 'Dolby Digital'
        }.get(codec, codec | upper) %}
        {% set hdr_name = {
          'dolbyvision': 'DV',
          'hdr10': 'HDR10',
          'hdr10plus': 'HDR10+',
          'hlg': 'HLG',
          'sdr': 'SDR'
        }.get(hdr, hdr | upper) %}
        Playing at {{ states('sensor.kodi_living_room_video_resolution') }}
        in {{ hdr_name }}
        with {{ codec_name }} audio.
```

---

## Manifest

```json
{
  "domain": "kodi_streamdetails",
  "name": "Kodi Stream Details",
  "codeowners": [],
  "config_flow": true,
  "dependencies": ["kodi"],
  "documentation": "https://github.com/your-repo/kodi-streamdetails",
  "iot_class": "local_polling",
  "requirements": [],
  "version": "1.0.0"
}
```

---

## Future Enhancements

1. **Player controls as services**: Switch audio/subtitle streams via HA service calls
2. **Media browser integration**: Show stream details in HA media browser
3. **Diagnostic sensors**: Kodi version, connection status, player state
4. **Lovelace card**: Custom card displaying stream details with icons
5. **Multiple active players**: Support Kodi instances with multiple simultaneous players
6. **Direct WebSocket connection**: Bypass native integration for lower latency updates

---

## References

- [Kodi JSON-RPC API Documentation](https://kodi.wiki/view/JSON-RPC_API/v12)
- [Home Assistant Custom Integration Development](https://developers.home-assistant.io/docs/creating_integration_manifest)
- [DataUpdateCoordinator Pattern](https://developers.home-assistant.io/docs/integration_fetching_data)
