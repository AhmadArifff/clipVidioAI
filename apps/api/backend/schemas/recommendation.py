from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ClipSettingsRecommendationRequest(BaseModel):
    clip_id: Optional[str] = None
    title: str = Field(..., description="Clip title or headline")
    transcript: str = Field(..., description="Spoken text or words of the clip")
    duration: Optional[float] = Field(30.0, description="Duration in seconds")
    speaker_count: Optional[int] = Field(1, description="Estimated number of faces or speakers")
    primary_topic: Optional[str] = Field(None, description="Topic or category of the video")
    language: Optional[str] = Field("id", description="Language code (id or en)")
    aspect_ratio: Optional[str] = Field("9:16", description="Target aspect ratio")


class RecommendedSettingsPayload(BaseModel):
    caption_style: str = "viral_pop"
    caption_font: str = "Outfit"
    font_size: str = "medium"
    text_case: str = "uppercase"
    keyword_accent_mode: str = "accent_and_emoji"
    bgm_preset: str = "lofi_chill"
    bgm_volume: float = 20.0
    auto_ducking: bool = True
    hook_zoom_enabled: bool = True
    streamer_preset: str = "none"
    podcast_layout_mode: str = "stacked_split"
    podcast_divider_style: str = "clean_white"
    title_position: str = "top"
    title_duration: str = "first_3s"
    speed_ramp_ratio: float = 1.03
    vocal_isolation_mode: str = "off"
    camera_tracking_mode: str = "off"


class ViralScores(BaseModel):
    hook_power: int = 90
    audio_balance: int = 95
    visual_retention: int = 92
    overall_score: int = 92


class ViralArchetype(BaseModel):
    id: str
    name: str
    icon: str
    badge: str
    description: str
    settings: RecommendedSettingsPayload


class ClipSettingsRecommendationResponse(BaseModel):
    archetype_id: str
    archetype_name: str
    archetype_icon: str
    reasoning: str
    growth_tip: str
    viral_scores: ViralScores
    settings: RecommendedSettingsPayload
    param_impacts: Optional[Dict[str, str]] = None
