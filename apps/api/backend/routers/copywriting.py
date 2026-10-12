import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.config import logger
from backend.schemas.copywriting import (
    GenerateCopyRequest,
    HookTitles,
    PlatformCaptions,
    SocialCopyDeck,
)
from backend.services.copywriting_service import generate_ai_copy_deck

router = APIRouter(tags=["copywriting"])


@router.post("/api/clips/generate-copy", response_model=SocialCopyDeck)
def generate_clip_social_copy(req: GenerateCopyRequest):
    """
    Generates an optimized viral copywriting deck (3 hook titles, multi-platform captions,
    and 12-15 hashtags) for a clip using Gemini or OpenRouter, with graceful heuristic fallback.
    """
    if not req.transcript and not req.title:
        raise HTTPException(
            status_code=400,
            detail="Transcript or title must be provided to generate copywriting deck."
        )

    try:
        deck_dict = generate_ai_copy_deck(
            transcript=req.transcript,
            title=req.title or "",
            topic=req.topic or "",
            language=req.language or "id",
            provider=req.ai_provider or "gemini",
            api_key=req.api_key,
            model=req.model
        )

        return SocialCopyDeck(
            hook_titles=HookTitles(**deck_dict["hook_titles"]),
            captions=PlatformCaptions(**deck_dict["captions"]),
            hashtags=deck_dict["hashtags"],
            hashtags_formatted=deck_dict["hashtags_formatted"],
        )
    except Exception as e:
        logger.error(f"Error in generate_clip_social_copy: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate copywriting deck: {str(e)}"
        )
