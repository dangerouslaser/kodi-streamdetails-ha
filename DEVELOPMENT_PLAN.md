# Kodi Stream Details Integration - Development Plan

## Overview

Build a HACS-compatible Home Assistant custom integration that exposes Kodi stream metadata (video, audio, subtitle) as individual sensors by linking to existing Kodi media_player entities.

---

## Phase 1: Project Setup & Repository Structure

### 1.1 Create HACS-compliant directory structure

```
kodi-sensors-ha/
├── custom_components/
│   └── kodi_streamdetails/
│       ├── __init__.py
│       ├── manifest.json
│       ├── config_flow.py
│       ├── const.py
│       ├── coordinator.py
│       ├── sensor.py
│       ├── strings.json
│       └── translations/
│           └── en.json
├── hacs.json
├── README.md
├── LICENSE
├── .github/
│   └── workflows/
│       ├── validate.yml      # HACS validation
│       └── release.yml       # Automated releases
└── info.md                   # HACS info page
```

### 1.2 Create HACS metadata

- `hacs.json` with render_readme, homeassistant version requirements
- GitHub repository topics: `home-assistant`, `hacs-integration`, `kodi`

---

## Phase 2: Core Integration Foundation

### 2.1 Create `manifest.json`

- Domain: `kodi_streamdetails`
- Dependencies: `["kodi"]`
- Config flow: `true`
- IOT class: `local_polling`
- Version: `0.1.0`

### 2.2 Create `const.py`

Define all constants:
- Domain name
- Sensor type definitions
- Codec normalization mappings (video/audio)
- HDR type mappings
- Resolution thresholds
- Channel format mappings
- Sensor name display strings

### 2.3 Create `__init__.py`

- `async_setup_entry()` - Set up coordinator and forward to sensor platform
- `async_unload_entry()` - Clean up
- Device info retrieval from parent Kodi entity

---

## Phase 3: Configuration Flow

### 3.1 Create `config_flow.py`

Implement ConfigFlow class:
- Discover existing `media_player.kodi*` entities
- Present dropdown selector to user
- Validate selected entity exists and is Kodi
- Store config entry with `source_entity` reference

### 3.2 Create `strings.json` and `translations/en.json`

- Config flow step titles/descriptions
- Selector labels
- Error messages

### 3.3 Options Flow (Optional for v1)

- Polling interval override
- Sensor name prefix customization

---

## Phase 4: Data Coordinator

### 4.1 Create `coordinator.py`

Implement `KodiStreamDetailsCoordinator(DataUpdateCoordinator)`:

**Core methods:**
- `_async_update_data()` - Main polling method
- `_call_kodi_method()` - Wrapper for `kodi.call_method` service
- `_parse_stream_data()` - Parse JSON-RPC responses
- `_empty_state()` - Return idle/nothing playing state

**Kodi API calls:**
1. `Player.GetActivePlayers` - Check if anything is playing
2. `Player.GetItem` - Get streamdetails (video codec, HDR, resolution)
3. `Player.GetProperties` - Get current audio/subtitle streams (Atmos detection)

**Helper methods:**
- `_normalize_video_codec()` - Map codec strings (hevc, h264, avc1, etc.)
- `_normalize_audio_codec()` - Map codec strings with Atmos detection
- `_derive_resolution()` - Width → 4K/1080p/720p/480p/SD
- `_format_aspect()` - Float → "2.39:1" string
- `_format_channels()` - Integer → "7.1" string

---

## Phase 5: Sensor Entities

### 5.1 Create `sensor.py`

Implement base `KodiStreamDetailsSensor(CoordinatorEntity, SensorEntity)`:
- Unique ID from source entity + sensor type
- Device info linking to parent Kodi device
- State from coordinator data
- Extra attributes per sensor type

### 5.2 Define all sensor types

**Video sensors (8):**
- `video_codec` - with `raw_codec` attribute
- `video_resolution` - with `width`, `height` attributes
- `video_width`
- `video_height`
- `video_aspect` - with `raw_aspect` attribute
- `video_hdr_type` - with `raw_hdrtype` attribute
- `video_stereo_mode`
- `video_duration` - with `formatted` (HH:MM:SS) attribute

**Audio sensors (10):**
- `audio_codec` - with `raw_codec`, `display_name` attributes
- `audio_channels` - with `raw_channels` attribute
- `audio_language` - with `language_name` attribute
- `audio_name`
- `audio_bitrate` - with `formatted` attribute
- `audio_stream_index`
- `audio_stream_count` - with `streams` list attribute
- `audio_is_default` (binary)
- `audio_is_original` (binary)

**Subtitle sensors (7):**
- `subtitle_enabled` (binary)
- `subtitle_language` - with `language_name` attribute
- `subtitle_name`
- `subtitle_stream_index`
- `subtitle_stream_count` - with `streams` list attribute
- `subtitle_is_forced` (binary)
- `subtitle_is_impaired` (binary)

**Playback sensors (1):**
- `playback_type` - with `media_type` attribute

### 5.3 Implement `async_setup_entry()`

- Create coordinator instance
- Build device info from parent Kodi entity
- Instantiate all sensor entities
- Add entities to HA

---

## Phase 6: Device Linking

### 6.1 Link sensors to parent Kodi device

- Retrieve device registry entry for source Kodi entity
- Use same `device_info` identifiers so sensors appear under existing Kodi device
- Sensors should NOT create a new device

### 6.2 Handle edge cases

- Source entity doesn't exist
- Source entity removed after setup
- Multiple Kodi instances

---

## Phase 7: State Handling & Edge Cases

### 7.1 Playback states

| State | Behavior |
|-------|----------|
| Nothing playing | All sensors → `None` or `idle` |
| Paused | Retain current values |
| Stopped | Reset to idle state |
| Audio-only | Video sensors → `None` |
| No subtitles | Subtitle sensors show `off`/`0` |

### 7.2 Error handling

- Kodi unavailable → sensors show `unavailable`
- JSON-RPC errors → log and retry
- Missing fields → graceful defaults

---

## Phase 8: Testing

### 8.1 Manual testing checklist

- [ ] Config flow discovers Kodi entities
- [ ] Sensors created and linked to correct device
- [ ] Video playback populates all video sensors
- [ ] Audio codec shows Atmos when applicable
- [ ] Subtitle enabled/disabled states work
- [ ] HDR types detected correctly (DV, HDR10, SDR)
- [ ] Resolution derived correctly from width
- [ ] Idle state clears sensors
- [ ] Multiple Kodi instances work independently

### 8.2 Automated tests (optional for v1)

- pytest fixtures for mock Kodi responses
- Config flow tests
- Coordinator data parsing tests

---

## Phase 9: Documentation

### 9.1 README.md

- Installation instructions (HACS + manual)
- Configuration steps with screenshots
- Sensor reference table
- Example automations
- Troubleshooting

### 9.2 info.md (HACS display)

- Brief description
- Feature highlights
- Requirements

---

## Phase 10: HACS Submission

### 10.1 Pre-submission checklist

- [ ] All HACS validation checks pass
- [ ] hassfest validation passes
- [ ] Repository has required files (README, LICENSE, hacs.json)
- [ ] Proper versioning in manifest.json
- [ ] GitHub release created

### 10.2 Submit to HACS default repository

- Open PR to https://github.com/hacs/default
- Follow submission guidelines

---

## Implementation Order

1. **Phase 1** - Project setup (repository, directories)
2. **Phase 2** - const.py, manifest.json, basic __init__.py
3. **Phase 4** - coordinator.py (core data fetching)
4. **Phase 5** - sensor.py (entity definitions)
5. **Phase 3** - config_flow.py (UI setup)
6. **Phase 6** - Device linking refinement
7. **Phase 7** - Edge case handling
8. **Phase 8** - Testing
9. **Phase 9** - Documentation
10. **Phase 10** - HACS submission

---

## Key Technical Decisions

### Data Sources
- **Video streams**: `Player.GetItem` → `streamdetails` (only source for HDR type)
- **Audio/Subtitle**: `Player.GetProperties` (has Atmos detection, track names)

### Polling Strategy
- Default 5-second polling via DataUpdateCoordinator
- WebSocket listener enhancement deferred to v2

### Device Architecture
- Sensors attach to existing Kodi device (no new device created)
- Each config entry = one linked Kodi media_player

### Binary Sensors
- Use `on`/`off` strings instead of BinarySensorEntity for consistency
- All "boolean" sensors are still regular sensors

---

## Version Roadmap

### v0.1.0 (MVP)
- Config flow setup
- All 26 sensors
- Polling updates
- Basic error handling

### v1.0.0
- Options flow (polling interval)
- Full documentation
- HACS default repo submission

### v1.1.0+ (Future)
- WebSocket real-time updates
- Audio/subtitle stream switching services
- Diagnostic sensors
