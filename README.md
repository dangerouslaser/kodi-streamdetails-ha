# Kodi Stream Details for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/dangerouslaser/kodi-streamdetails-ha.svg)](https://github.com/dangerouslaser/kodi-streamdetails-ha/releases)
[![License](https://img.shields.io/github/license/dangerouslaser/kodi-streamdetails-ha.svg)](LICENSE)

A custom Home Assistant integration that exposes detailed stream metadata from Kodi as individual sensors. Perfect for automations based on video quality, audio codec, HDR type, and more.

## Features

- **26 individual sensors** for video, audio, subtitle, and playback information
- **Links to existing Kodi integration** - no duplicate configuration needed
- **Real-time updates** via polling (WebSocket support planned)
- **Automatic codec normalization** - friendly names for codecs like "Dolby TrueHD Atmos"
- **HDR detection** - Dolby Vision, HDR10, HDR10+, HLG, SDR
- **Atmos detection** - Properly detects Dolby Atmos and DTS:X object audio
- **Multi-instance support** - Monitor multiple Kodi players

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top right corner
3. Select "Custom repositories"
4. Add `https://github.com/dangerouslaser/kodi-streamdetails-ha` with category "Integration"
5. Click "Install"
6. Restart Home Assistant

### Manual Installation

1. Download the latest release from [GitHub](https://github.com/dangerouslaser/kodi-streamdetails-ha/releases)
2. Extract and copy the `custom_components/kodi_streamdetails` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Kodi Stream Details"
4. Select the Kodi media player entity to monitor
5. Done! Sensors will appear under the same device as your Kodi player

## Sensors

### Video Sensors

| Sensor | Description | Example State |
|--------|-------------|---------------|
| Video Codec | Normalized video codec | `hevc` |
| Video Resolution | Derived from width | `4K`, `1080p`, `720p` |
| Video Width | Width in pixels | `3840` |
| Video Height | Height in pixels | `2160` |
| Aspect Ratio | Formatted ratio | `2.39:1`, `16:9` |
| HDR Type | Dynamic range format | `dolbyvision`, `hdr10`, `sdr` |
| 3D Mode | Stereoscopic mode | `2d`, `sbs`, `tab` |
| Duration | Runtime in seconds | `7139` |

### Audio Sensors

| Sensor | Description | Example State |
|--------|-------------|---------------|
| Audio Codec | Normalized codec with Atmos | `truehd_atmos`, `dtshd_ma` |
| Audio Channels | Channel layout | `7.1`, `5.1`, `2.0` |
| Audio Language | ISO 639-2 code | `eng`, `spa` |
| Audio Track Name | Full track name | `TrueHD Atmos 7.1` |
| Audio Bitrate | Bitrate in bps | `0` (lossless) |
| Audio Stream Index | Current stream index | `0` |
| Audio Stream Count | Total audio tracks | `3` |
| Audio Is Default | Default track flag | `on`, `off` |
| Audio Is Original | Original language flag | `on`, `off` |

### Subtitle Sensors

| Sensor | Description | Example State |
|--------|-------------|---------------|
| Subtitles Enabled | Active state | `on`, `off` |
| Subtitle Language | Current language | `eng`, `off` |
| Subtitle Track Name | Full track name | `English (SDH)` |
| Subtitle Stream Index | Current index | `0` |
| Subtitle Stream Count | Total subtitle tracks | `5` |
| Subtitle Is Forced | Forced subtitle flag | `on`, `off` |
| Subtitle Is SDH/CC | Accessibility flag | `on`, `off` |

### Playback Sensor

| Sensor | Description | Example State |
|--------|-------------|---------------|
| Playback Type | Content type | `movie`, `episode`, `idle` |

## Example Automations

### Announce Dolby Vision Content

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

### Cinema Mode for 4K Content

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

### Notify on Atmos Audio

```yaml
automation:
  - alias: "Notify Atmos Audio"
    trigger:
      - platform: state
        entity_id: sensor.kodi_living_room_audio_codec
    condition:
      - condition: template
        value_template: "{{ 'atmos' in trigger.to_state.state }}"
    action:
      - service: notify.mobile_app
        data:
          message: "Playing with Dolby Atmos audio!"
```

## Requirements

- Home Assistant 2024.1.0 or newer
- [Kodi integration](https://www.home-assistant.io/integrations/kodi/) configured and working

## How It Works

This integration uses Kodi's JSON-RPC API through the native Home Assistant Kodi integration:

- **Video data** comes from `Player.GetItem` → `streamdetails` (only source for HDR type)
- **Audio/Subtitle data** comes from `Player.GetProperties` (includes Atmos detection and track names)

The integration polls every 5 seconds by default.

## Troubleshooting

### Sensors show "unavailable"

- Ensure your Kodi media player is online and reachable
- Check that the Kodi integration is working correctly
- Verify Kodi's JSON-RPC interface is enabled (Settings → Services → Control)

### No Atmos detection

- Atmos metadata requires `Player.GetProperties` which this integration uses
- Ensure your media files have proper Atmos flags in their metadata

### Missing HDR type

- HDR type detection requires Kodi 19 (Matrix) or newer
- Not all video files contain HDR metadata

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
