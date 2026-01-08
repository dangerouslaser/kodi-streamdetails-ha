"""Constants for the Kodi Stream Details integration."""

from typing import Final

DOMAIN: Final = "kodi_streamdetails"

# Configuration
CONF_SOURCE_ENTITY: Final = "source_entity"
CONF_POLL_INTERVAL: Final = "poll_interval"
DEFAULT_POLL_INTERVAL: Final = 5
MIN_POLL_INTERVAL: Final = 1
MAX_POLL_INTERVAL: Final = 60

# Video codec normalization
VIDEO_CODEC_MAP: Final = {
    "hevc": "hevc",
    "h265": "hevc",
    "h264": "h264",
    "avc1": "h264",
    "avc": "h264",
    "vp9": "vp9",
    "vp8": "vp8",
    "av1": "av1",
    "mpeg2video": "mpeg2",
    "mpeg2": "mpeg2",
    "vc1": "vc1",
    "wmv3": "vc1",
}

VIDEO_CODEC_DISPLAY: Final = {
    "hevc": "HEVC / H.265",
    "h264": "H.264 / AVC",
    "vp9": "VP9",
    "vp8": "VP8",
    "av1": "AV1",
    "mpeg2": "MPEG-2",
    "vc1": "VC-1",
}

# Audio codec normalization
AUDIO_CODEC_MAP: Final = {
    "truehd_atmos": "truehd_atmos",
    "truehd": "truehd",
    "eac3_atmos": "eac3_atmos",
    "eac3": "eac3",
    "ec3": "eac3",
    "ac3": "ac3",
    "dtshd_ma": "dtshd_ma",
    "dtshd_hra": "dtshd_hra",
    "dtsx": "dtsx",
    "dca": "dts",
    "dts": "dts",
    "aac": "aac",
    "flac": "flac",
    "pcm": "pcm",
    "pcm_s16le": "pcm",
    "pcm_s24le": "pcm",
    "pcm_s32le": "pcm",
    "opus": "opus",
    "vorbis": "vorbis",
    "mp3": "mp3",
    "mp2": "mp2",
}

AUDIO_CODEC_DISPLAY: Final = {
    "truehd_atmos": "Dolby TrueHD Atmos",
    "truehd": "Dolby TrueHD",
    "eac3_atmos": "Dolby Digital+ Atmos",
    "eac3": "Dolby Digital+",
    "ac3": "Dolby Digital",
    "dtshd_ma": "DTS-HD MA",
    "dtshd_hra": "DTS-HD HRA",
    "dtsx": "DTS:X",
    "dts": "DTS",
    "aac": "AAC",
    "flac": "FLAC",
    "pcm": "PCM",
    "opus": "Opus",
    "vorbis": "Vorbis",
    "mp3": "MP3",
    "mp2": "MP2",
}

# HDR type mapping
HDR_TYPE_MAP: Final = {
    "dolbyvision": "dolbyvision",
    "hdr10": "hdr10",
    "hdr10plus": "hdr10plus",
    "hlg": "hlg",
    "": "sdr",
}

HDR_TYPE_DISPLAY: Final = {
    "dolbyvision": "DV",
    "hdr10": "HDR10",
    "hdr10plus": "HDR10+",
    "hlg": "HLG",
    "sdr": "SDR",
}

# Resolution thresholds (based on width)
RESOLUTION_THRESHOLDS: Final = [
    (3840, "4K"),
    (1920, "1080p"),
    (1280, "720p"),
    (720, "480p"),
    (0, "SD"),
]

# Common aspect ratios for display
ASPECT_RATIO_NAMES: Final = {
    2.39: "2.39:1",
    2.35: "2.35:1",
    2.40: "2.40:1",
    1.85: "1.85:1",
    1.78: "16:9",
    1.77: "16:9",
    1.33: "4:3",
    1.34: "4:3",
    2.00: "2:1",
    2.20: "2.20:1",
    1.90: "1.90:1",
}

# Sensor definitions
SENSOR_TYPES: Final = {
    # Video sensors
    "video_codec": {
        "name": "Video Codec",
        "icon": "mdi:video",
    },
    "video_resolution": {
        "name": "Video Resolution",
        "icon": "mdi:television",
    },
    "video_width": {
        "name": "Video Width",
        "icon": "mdi:arrow-expand-horizontal",
        "unit": "px",
    },
    "video_height": {
        "name": "Video Height",
        "icon": "mdi:arrow-expand-vertical",
        "unit": "px",
    },
    "video_aspect": {
        "name": "Aspect Ratio",
        "icon": "mdi:aspect-ratio",
    },
    "video_hdr_type": {
        "name": "HDR Type",
        "icon": "mdi:hdr",
    },
    "video_stereo_mode": {
        "name": "3D Mode",
        "icon": "mdi:video-3d",
    },
    "video_duration": {
        "name": "Duration",
        "icon": "mdi:timer-outline",
        "unit": "s",
    },
    # Audio sensors
    "audio_codec": {
        "name": "Audio Codec",
        "icon": "mdi:surround-sound",
    },
    "audio_channels": {
        "name": "Audio Channels",
        "icon": "mdi:speaker-multiple",
    },
    "audio_language": {
        "name": "Audio Language",
        "icon": "mdi:translate",
    },
    "audio_name": {
        "name": "Audio Track Name",
        "icon": "mdi:music-box",
    },
    "audio_bitrate": {
        "name": "Audio Bitrate",
        "icon": "mdi:speedometer",
        "unit": "bps",
    },
    "audio_stream_index": {
        "name": "Audio Stream Index",
        "icon": "mdi:format-list-numbered",
    },
    "audio_stream_count": {
        "name": "Audio Stream Count",
        "icon": "mdi:playlist-music",
    },
    "audio_is_default": {
        "name": "Audio Is Default",
        "icon": "mdi:check-circle",
    },
    "audio_is_original": {
        "name": "Audio Is Original",
        "icon": "mdi:star",
    },
    # Subtitle sensors
    "subtitle_enabled": {
        "name": "Subtitles Enabled",
        "icon": "mdi:subtitles",
    },
    "subtitle_language": {
        "name": "Subtitle Language",
        "icon": "mdi:translate",
    },
    "subtitle_name": {
        "name": "Subtitle Track Name",
        "icon": "mdi:subtitles-outline",
    },
    "subtitle_stream_index": {
        "name": "Subtitle Stream Index",
        "icon": "mdi:format-list-numbered",
    },
    "subtitle_stream_count": {
        "name": "Subtitle Stream Count",
        "icon": "mdi:playlist-plus",
    },
    "subtitle_is_forced": {
        "name": "Subtitle Is Forced",
        "icon": "mdi:alert-circle",
    },
    "subtitle_is_impaired": {
        "name": "Subtitle Is SDH/CC",
        "icon": "mdi:closed-caption",
    },
    # Playback sensor
    "playback_type": {
        "name": "Playback Type",
        "icon": "mdi:play-circle",
    },
}

# ISO 639-2 language code to name mapping (common languages)
LANGUAGE_NAMES: Final = {
    "eng": "English",
    "spa": "Spanish",
    "fra": "French",
    "deu": "German",
    "ita": "Italian",
    "por": "Portuguese",
    "jpn": "Japanese",
    "kor": "Korean",
    "zho": "Chinese",
    "chi": "Chinese",
    "rus": "Russian",
    "ara": "Arabic",
    "hin": "Hindi",
    "tha": "Thai",
    "vie": "Vietnamese",
    "pol": "Polish",
    "nld": "Dutch",
    "swe": "Swedish",
    "nor": "Norwegian",
    "dan": "Danish",
    "fin": "Finnish",
    "tur": "Turkish",
    "heb": "Hebrew",
    "ces": "Czech",
    "hun": "Hungarian",
    "ron": "Romanian",
    "ell": "Greek",
    "ukr": "Ukrainian",
    "ind": "Indonesian",
    "msa": "Malay",
    "und": "Undetermined",
}
