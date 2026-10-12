from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class GenerateCopyRequest(BaseModel):
    transcript: str = Field(..., description="Clip spoken dialogue transcript")
    title: Optional[str] = Field("", description="Base clip title or topic")
    topic: Optional[str] = Field("", description="Optional video topic or context")
    language: Optional[str] = Field("id", description="Target language code: 'id' or 'en'")
    ai_provider: Optional[str] = Field("gemini", description="AI Provider: 'gemini' or 'openrouter'")
    api_key: Optional[str] = Field(None, description="Optional custom API key")
    model: Optional[str] = Field(None, description="Optional preferred model")


class HookTitles(BaseModel):
    curiosity: str = Field(description="Curiosity-driven hook title")
    contrarian: str = Field(description="Shock or contrarian hook title")
    action: str = Field(description="Actionable or solution hook title")


class PlatformCaptions(BaseModel):
    tiktok_reels: str = Field(description="Punchy TikTok & Reels caption with Call to Action")
    youtube_shorts: str = Field(description="Informative YouTube Shorts description")


class SocialCopyDeck(BaseModel):
    hook_titles: HookTitles
    captions: PlatformCaptions
    hashtags: List[str]
    hashtags_formatted: str
