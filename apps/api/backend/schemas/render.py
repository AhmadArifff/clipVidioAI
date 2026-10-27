from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, ConfigDict

class RenderSettingsModel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspect_ratio: str = "9:16"
    background_style: str = "black"
    # Custom Background Configuration
    background_type: Optional[str] = "preset"   # "blur" | "black" | "color" | "gradient" | "preset" | "custom_upload"
    background_value: Optional[str] = "black"    # hex color ("#09090b"), preset id ("minecraft_parkour"), or gradient
    background_file_path: Optional[str] = None   # Server file path for custom uploaded or preset media
    foreground_scale: Optional[float] = 100.0    # 40.0% to 100.0% of canvas width
    foreground_position_y: Optional[float] = 50.0 # 0% to 100% vertical center
    foreground_border_radius: Optional[Union[int, float]] = 0  # 0 to 48 px corner radius
    foreground_shadow: Optional[bool] = False    # Drop shadow under foreground video
    enable_face_tracking: bool = True
    # v3.6 Smart Camera Tracking (CapCut Style) & Fit to Canvas
    camera_tracking_mode: Optional[str] = "fit_balanced"       # "fit_balanced" | "fit_close_up" | "dynamic_pan_only" | "static_center"
    tracking_smoothness: Optional[Union[float, int]] = 0.15    # 0.05 (cinematic smooth) to 0.45 (rapid), or 1-10 scale
    # v3.6 Comedy Expression FX (PWK Style)
    comedy_effect_preset: Optional[str] = "none"               # "none" | "pwk_snap_zoom" | "pwk_red_blush" | "pwk_funny_fisheye"
    comedy_effect_start_time: Optional[float] = None           # Second in clip when effect triggers (None = auto)
    comedy_effect_duration: Optional[float] = 1.5              # Duration of effect in seconds (default 1.5s)
    comedy_sfx_enabled: Optional[bool] = True                  # Automatic comedy signature SFX sync
    streamer_preset: str = "none"
    facecam_position: Optional[str] = "auto"
    podcast_layout_mode: Optional[str] = "stacked_split"       # "stacked_split" | "left_focus" | "right_focus"
    podcast_divider_style: Optional[str] = "clean_white"       # "clean_white" | "glow_cyan" | "glow_gold" | "dark_line" | "none"
    podcast_host_cx: Optional[float] = None
    podcast_guest_cx: Optional[float] = None
    title_text: Optional[str] = None
    title_prefix: Optional[str] = ""
    title_suffix: Optional[str] = ""
    file_name_prefix: Optional[str] = ""
    file_name_suffix: Optional[str] = ""
    title_position: str = "auto"
    title_duration: Optional[str] = "entire"
    subtitles_enabled: Optional[bool] = True
    caption_style: str = "viral_pop"
    caption_font: str = "Outfit"
    title_font: Optional[str] = "Outfit"
    font_size: str = "medium"
    title_font_size: Optional[str] = "medium"
    font_size_px: Optional[Union[int, float]] = None
    title_font_size_px: Optional[Union[int, float]] = None
    text_case: str = "uppercase"
    title_text_case: Optional[str] = "uppercase"
    title_y_percent: Optional[float] = None
    subtitle_y_percent: Optional[float] = None
    subtitle_position_mode: Optional[str] = "bottom"
    subtitle_center_y_percent: Optional[float] = 50.0
    # Background Music
    bgm_enabled: Optional[bool] = False
    bgm_preset: Optional[str] = "none"           # "none" | "lofi_chill" | "phonk_hype" | "cinematic_mystery" | "upbeat_vlog" | "custom"
    bgm_file_path: Optional[str] = None
    bgm_volume: Optional[float] = 25.0
    bgm_start_offset: Optional[float] = 0.0
    # Hook SFX
    hook_sfx_enabled: Optional[bool] = False
    hook_sfx_file_path: Optional[str] = None
    hook_sfx_volume: Optional[float] = 100.0
    # Raw Audio / Voice Boost
    original_audio_volume: Optional[float] = 100.0
    # Watermark
    watermark_enabled: Optional[bool] = False
    watermark_type: Optional[str] = "image"
    watermark_file_path: Optional[str] = None
    watermark_text: Optional[str] = None
    watermark_size: Optional[float] = 20.0
    watermark_opacity: Optional[float] = 80.0
    watermark_x: Optional[float] = 90.0
    watermark_y: Optional[float] = 8.0
    hardware_accel: Optional[str] = "auto"
    # Subtitle Audio Timing Calibration & Language
    subtitle_offset_ms: Optional[Union[int, float]] = 0        # Timing shift in ms (-1000ms to +1000ms)
    subtitle_language: Optional[str] = "id"      # Subtitle language "id" | "en"
    # Multi-Segment Merged Highlight Video
    render_mode: Optional[str] = "separate"  # "separate" | "merged"
    compilation_title: Optional[str] = None
    # v3.0 Ultra-Quality Render Engine
    video_polish_enabled: Optional[bool] = True    # Micro-sharpening & BT.709 color matrix
    audio_mastering_enabled: Optional[bool] = True # Digital broadcast loudness (-14 LUFS)
    smart_ducking_enabled: Optional[bool] = True   # Sidechain compression ducking BGM under voice
    hook_zoom_enabled: Optional[bool] = True       # Dynamic 1.1x hook punch-in zoom (0-2.5s)
    # v3.1 Subtitle Keyword Emoji Accent & Viral Styling
    keyword_accent_mode: Optional[str] = "accent_and_emoji" # "off" | "accent_only" | "accent_and_emoji"
    # v3.7 Anti-Content ID Shield & Viral Algorithm Booster
    speed_ramp_ratio: Optional[float] = 1.03           # Micro-speed ramping (1.00 = off, 1.02 to 1.06)
    vocal_isolation_mode: Optional[str] = "center_vocal_extract" # "off" | "center_vocal_extract" | "voice_clarity_bandpass"
    # Custom Creator Reaction Cam PIP Overlay (Anti-Copyright Transformative Fair Use)
    reaction_cam_enabled: Optional[bool] = False
    reaction_cam_file_path: Optional[str] = None
    reaction_cam_position: Optional[str] = "bottom_right" # "bottom_right" | "bottom_left" | "top_right" | "top_left"
    reaction_cam_size: Optional[float] = 24.0             # 15.0% to 45.0% of canvas width
    reaction_cam_shape: Optional[str] = "circle"          # "circle" | "rounded_rect"
    reaction_cam_border_color: Optional[str] = "white"    # "white" | "gold" | "cyan" | "none"
    reaction_cam_mute_audio: Optional[bool] = True        # Default True to preserve original dialogue

class RenderBatchRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    video_url: str
    video_id: str
    clips: List[Dict[str, Any]]
    settings: RenderSettingsModel
    transcript: Optional[List[Dict[str, Any]]] = None
    cookies: Optional[str] = None

class RetryBatchRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    clip_indices: Optional[List[int]] = None
    cookies: Optional[str] = None
