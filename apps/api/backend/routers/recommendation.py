import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException

from backend.schemas.recommendation import (
    ClipSettingsRecommendationRequest,
    ClipSettingsRecommendationResponse,
    ViralArchetype,
)
from backend.services.recommendation_service import (
    generate_smart_settings_recommendation,
    get_all_viral_archetypes,
)

logger = logging.getLogger("clipvidio")

router = APIRouter(prefix="/api/clips", tags=["recommendation"])


@router.get("/viral-archetypes", response_model=List[ViralArchetype])
async def list_viral_archetypes():
    """
    Returns list of 5 predefined viral archetypes (MrBeast, Hormozi, Rogan, Vox, Daily Vlog).
    """
    try:
        return get_all_viral_archetypes()
    except Exception as e:
        logger.error(f"Error listing viral archetypes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend-settings", response_model=ClipSettingsRecommendationResponse)
async def recommend_clip_settings(
    request: ClipSettingsRecommendationRequest,
    x_gemini_api_key: Optional[str] = Header(None, alias="x-gemini-api-key")
):
    """
    Analyzes clip details (title, transcript, duration, speakers) and returns
    tailored studio settings recommendation to optimize retention and engagement.
    """
    try:
        recommendation = await generate_smart_settings_recommendation(
            transcript=request.transcript,
            title=request.title,
            duration=request.duration or 30.0,
            speaker_count=request.speaker_count or 1,
            primary_topic=request.primary_topic or "",
            language=request.language or "id",
            api_key=x_gemini_api_key
        )
        return recommendation
    except Exception as e:
        logger.error(f"Failed to generate settings recommendation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to recommend clip settings: {e}")
