import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from google import genai
from google.genai import types

from backend.config import logger
from backend.services.ai_service import (
    AIRouterService,
    call_openrouter_chat_completion,
    get_flash_models_for_key,
    parse_api_keys,
)

# Common viral tags pool for heuristic generation
DEFAULT_ID_HASHTAGS = [
    "#fyp",
    "#shorts",
    "#viral",
    "#trending",
    "#reels",
    "#edukasi",
    "#tips",
    "#informasi",
    "#konten",
    "#inspirasi",
    "#foryou",
    "#belajar",
    "#motivasi",
    "#tiktokindonesia",
]

DEFAULT_EN_HASHTAGS = [
    "#fyp",
    "#shorts",
    "#viral",
    "#trending",
    "#reels",
    "#education",
    "#tips",
    "#insights",
    "#foryou",
    "#mindset",
    "#creator",
    "#learn",
    "#motivation",
    "#dailygrowth",
]


def generate_heuristic_copy_deck(
    transcript: str,
    title: str = "",
    topic: str = "",
    language: str = "id"
) -> Dict[str, Any]:
    """Generates an intelligent heuristic copywriting pack when AI models are unavailable or offline."""
    is_id = (language or "id").lower().startswith("id")
    clean_title = (title or "").strip()
    clean_topic = (topic or clean_title or ("Topik Menarik" if is_id else "This Topic")).strip()

    # Extract clean core subject (remove emoji and brackets)
    core_subject = re.sub(r'[^\w\s]', '', clean_topic).strip()
    if not core_subject:
        core_subject = "Topik Menarik" if is_id else "This Topic"

    if is_id:
        curiosity_hook = f"Rahasia di Balik {core_subject}: Yang Jarang Orang Tahu!"
        contrarian_hook = f"Banyak yang Salah Paham Soal {core_subject}!"
        action_hook = f"Cara Tepat Pahami {core_subject} dalam 3 Langkah"

        tiktok_reels = (
            f"Ternyata begini fakta sebenarnya seputar {core_subject}! 💡\n"
            f"Simak sampai habis dan bagikan ke teman yang butuh info ini. "
            f"Komen di bawah pendapat kamu! 👇"
        )
        youtube_shorts = (
            f"Pembahasan mendalam dan insight penting seputar {core_subject}.\n"
            f"Tonton terus untuk tips dan strategi lengkapnya! #shorts #viral #edukasi"
        )
        pinned_comment = (
            f"Kalian di posisi ini setuju nggak sama pendapat di video ini? "
            f"Atau ada pandangan lain? Tulis alasan kalian di bawah ya! 👇"
        )
        hashtags = list(DEFAULT_ID_HASHTAGS)
        # Add niche topic hashtag if clean
        clean_tag = f"#{re.sub(r'[^a-zA-Z0-9]', '', core_subject.lower())}"
        if len(clean_tag) > 2 and clean_tag not in hashtags:
            hashtags.insert(0, clean_tag)
    else:
        curiosity_hook = f"The Hidden Truth Behind {core_subject}: Don't Miss This!"
        contrarian_hook = f"Everything You Thought You Knew About {core_subject} Is Wrong!"
        action_hook = f"How to Master {core_subject} in 3 Simple Steps"

        tiktok_reels = (
            f"Here is what nobody tells you about {core_subject}! 💡\n"
            f"Watch until the end and share this with someone who needs it. "
            f"Drop your thoughts in the comments! 👇"
        )
        youtube_shorts = (
            f"Key takeaways and actionable insights about {core_subject}.\n"
            f"Subscribe for more daily breakdowns and practical advice! #shorts #viral #learn"
        )
        pinned_comment = (
            f"Do you agree with this take or do you see it differently? "
            f"Drop your thoughts and reasons below! 👇"
        )
        hashtags = list(DEFAULT_EN_HASHTAGS)
        clean_tag = f"#{re.sub(r'[^a-zA-Z0-9]', '', core_subject.lower())}"
        if len(clean_tag) > 2 and clean_tag not in hashtags:
            hashtags.insert(0, clean_tag)

    hashtags_slice = hashtags[:15]
    return {
        "hook_titles": {
            "curiosity": curiosity_hook,
            "contrarian": contrarian_hook,
            "action": action_hook,
        },
        "captions": {
            "tiktok_reels": tiktok_reels,
            "youtube_shorts": youtube_shorts,
        },
        "pinned_comment": pinned_comment,
        "hashtags": hashtags_slice,
        "hashtags_formatted": " ".join(hashtags_slice),
    }


def generate_ai_copy_deck(
    transcript: str,
    title: str = "",
    topic: str = "",
    language: str = "id",
    provider: str = "gemini",
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """Generates 3 hook titles, multi-platform captions, and 12-15 viral hashtags using AI (Gemini / OpenRouter),
    falling back gracefully to heuristic generation upon any error."""
    clean_provider = (provider or "gemini").lower().strip()
    is_id = (language or "id").lower().startswith("id")
    lang_name = "Bahasa Indonesia" if is_id else "English"
    lang_code = "id" if is_id else "en"

    system_prompt = (
        f"You are a world-class viral short-form video copywriter and social media growth strategist.\n"
        f"Your task is to craft an irresistible, high-converting social copywriting pack for a short video clip.\n\n"
        f"MANDATORY LANGUAGE RULE: All output MUST be 100% written in {lang_name.upper()} (Language Code: '{lang_code}').\n"
        f"DO NOT translate to any other language.\n\n"
        f"Generate a JSON object with this EXACT structure:\n"
        f"{{\n"
        f'  "hook_titles": {{\n'
        f'    "curiosity": "<Punchy curiosity hook title, max 8 words>",\n'
        f'    "contrarian": "<Shocking or myth-busting contrarian hook title, max 8 words>",\n'
        f'    "action": "<Action-oriented practical solution hook title, max 8 words>"\n'
        f'  }},\n'
        f'  "captions": {{\n'
        f'    "tiktok_reels": "<1-2 sentences punchy caption with hook, emojis, and clear Call to Action (e.g. Komen di bawah!)>",\n'
        f'    "youtube_shorts": "<Informative description summarizing key takeaway with clean spacing>"\n'
        f'  }},\n'
        f'  "pinned_comment": "<Engaging conversation-starter question or debate poll to pin at the top of comments>",\n'
        f'  "hashtags": ["#tag1", "#tag2", "#tag3", ... 12 to 15 relevant niche and trending tags]\n'
        f"}}\n"
    )

    user_prompt = (
        f"Video Clip Context:\n"
        f"- Title: {title or 'Clip Highlight'}\n"
        f"- Topic / Context: {topic or title or 'Discussion'}\n"
        f"- Transcript:\n{transcript[:2000]}\n\n"
        f"Respond ONLY in valid JSON matching the schema."
    )

    # 1. Try OpenRouter if specified
    if clean_provider == "openrouter":
        or_keys = parse_api_keys(api_key or os.environ.get("OPENROUTER_API_KEY"))
        if or_keys:
            use_key = or_keys[0]
            use_model = model or "deepseek/deepseek-chat"
            try:
                raw_response = call_openrouter_chat_completion(
                    api_key=use_key,
                    model=use_model,
                    prompt=f"{system_prompt}\n\n{user_prompt}",
                    timeout=30.0
                )
                parsed = json.loads(re.sub(r'^```json\s*|\s*```$', '', raw_response.strip(), flags=re.DOTALL))
                if isinstance(parsed, dict) and "hook_titles" in parsed:
                    ht = parsed.get("hook_titles", {})
                    cp = parsed.get("captions", {})
                    htags = parsed.get("hashtags", [])
                    pinned_c = parsed.get("pinned_comment") or (
                        "Kalian setuju nggak sama poin ini? Tulis pendapat kalian di bawah ya! 👇"
                        if is_id else "Do you agree with this take? Drop your thoughts below! 👇"
                    )
                    if isinstance(htags, list) and htags:
                        clean_tags = [f"#{t.lstrip('#')}" for t in htags if isinstance(t, str) and t.strip()]
                    else:
                        clean_tags = DEFAULT_ID_HASHTAGS if is_id else DEFAULT_EN_HASHTAGS
                    return {
                        "hook_titles": {
                            "curiosity": ht.get("curiosity") or "Rahasia Menarik" if is_id else "Curious Insight",
                            "contrarian": ht.get("contrarian") or "Mitos Populer Terbantahkan" if is_id else "Busted Myth",
                            "action": ht.get("action") or "Solusi Praktis Cepat" if is_id else "Fast Practical Action",
                        },
                        "captions": {
                            "tiktok_reels": cp.get("tiktok_reels") or "",
                            "youtube_shorts": cp.get("youtube_shorts") or "",
                        },
                        "pinned_comment": pinned_c,
                        "hashtags": clean_tags[:15],
                        "hashtags_formatted": " ".join(clean_tags[:15]),
                    }
            except Exception as e:
                logger.warning(f"OpenRouter copywriting generation failed: {e}, using heuristic fallback")

    # 2. Try Gemini
    gemini_keys = parse_api_keys(api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEYS"))
    if gemini_keys and gemini_keys[0].lower() != "mock":
        use_key = gemini_keys[0]
        use_model = model or "gemini-2.5-flash"
        try:
            client = genai.Client(api_key=use_key)
            response = client.models.generate_content(
                model=use_model,
                contents=f"{system_prompt}\n\n{user_prompt}",
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.3,
                )
            )
            raw_text = response.text or ""
            parsed = json.loads(re.sub(r'^```json\s*|\s*```$', '', raw_text.strip(), flags=re.DOTALL))
            if isinstance(parsed, dict) and "hook_titles" in parsed:
                ht = parsed.get("hook_titles", {})
                cp = parsed.get("captions", {})
                htags = parsed.get("hashtags", [])
                pinned_c = parsed.get("pinned_comment") or (
                    "Kalian setuju nggak sama poin ini? Tulis pendapat kalian di bawah ya! 👇"
                    if is_id else "Do you agree with this take? Drop your thoughts below! 👇"
                )
                if isinstance(htags, list) and htags:
                    clean_tags = [f"#{t.lstrip('#')}" for t in htags if isinstance(t, str) and t.strip()]
                else:
                    clean_tags = DEFAULT_ID_HASHTAGS if is_id else DEFAULT_EN_HASHTAGS
                return {
                    "hook_titles": {
                        "curiosity": ht.get("curiosity") or ("Rahasia Menarik" if is_id else "Curious Insight"),
                        "contrarian": ht.get("contrarian") or ("Mitos Populer Terbantahkan" if is_id else "Busted Myth"),
                        "action": ht.get("action") or ("Solusi Praktis Cepat" if is_id else "Fast Practical Action"),
                    },
                    "captions": {
                        "tiktok_reels": cp.get("tiktok_reels") or "",
                        "youtube_shorts": cp.get("youtube_shorts") or "",
                    },
                    "pinned_comment": pinned_c,
                    "hashtags": clean_tags[:15],
                    "hashtags_formatted": " ".join(clean_tags[:15]),
                }
        except Exception as e:
            logger.warning(f"Gemini copywriting generation failed: {e}, falling back to heuristic")

    # 3. Fallback Heuristic Generator
    return generate_heuristic_copy_deck(
        transcript=transcript,
        title=title,
        topic=topic,
        language=language
    )


def format_clip_metadata_text(clip: Dict[str, Any], copy_deck: Optional[Dict[str, Any]] = None) -> str:
    """Formats a clean, professional metadata.txt content for inclusion in clip ZIP export packages."""
    title = clip.get("title") or "Viral Clip"
    virality = clip.get("virality_score", 90)
    start_t = clip.get("start_time", 0.0)
    end_t = clip.get("end_time", 30.0)
    duration = max(1.0, round(float(end_t) - float(start_t), 1))

    if not copy_deck:
        transcript = clip.get("transcript") or ""
        copy_deck = generate_heuristic_copy_deck(transcript=transcript, title=title)

    ht = copy_deck.get("hook_titles", {})
    cp = copy_deck.get("captions", {})
    pinned_comment = copy_deck.get("pinned_comment") or (
        "Kalian setuju nggak sama pendapat di video ini? Tulis pendapat kalian di bawah ya! 👇"
    )
    hashtags_str = copy_deck.get("hashtags_formatted") or " ".join(copy_deck.get("hashtags", []))

    lines = [
        "============================================================",
        f"CLIP TITLE: {title}",
        f"VIRALITY SCORE: {virality}/100 | DURATION: {duration}s",
        "============================================================",
        "",
        "[HOOK TITLES (3 VARIATIONS)]",
        f"1. Curiosity Hook: {ht.get('curiosity', '-')}",
        f"2. Contrarian Hook: {ht.get('contrarian', '-')}",
        f"3. Action Hook: {ht.get('action', '-')}",
        "",
        "[TIKTOK & INSTAGRAM REELS CAPTION]",
        cp.get("tiktok_reels", "-"),
        "",
        "[YOUTUBE SHORTS DESCRIPTION]",
        cp.get("youtube_shorts", "-"),
        "",
        "[PINNED COMMENT (PEMICU DISKUSI & INTERAKSI TINGGI)]",
        pinned_comment,
        "",
        "[VIRAL HASHTAGS]",
        hashtags_str,
        "",
        "============================================================",
        "Generated by ClipVidio AI Studio (v3.4.0)",
        "============================================================",
    ]
    return "\n".join(lines)
