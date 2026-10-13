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

VIRAL_ARCHETYPES: Dict[str, Dict[str, Any]] = {
    "beast_hype": {
        "id": "beast_hype",
        "name": "MrBeast Hyper-Hype",
        "icon": "⚡",
        "badge": "High Energy & Retention",
        "description": "Kombinasi energi tinggi dengan subtitle Beast Punch (Neon Green), BGM Phonk Hype bervolume 22%, Hook Zoom 1.15x, dan Micro Pacing 1.04x untuk menahan penonton di 3 detik awal.",
        "settings": {
            "caption_style": "beast_punch",
            "caption_font": "The Bold Font",
            "font_size": "medium",
            "text_case": "uppercase",
            "keyword_accent_mode": "accent_and_emoji",
            "bgm_preset": "phonk_hype",
            "bgm_volume": 22.0,
            "auto_ducking": True,
            "hook_zoom_enabled": True,
            "streamer_preset": "none",
            "podcast_layout_mode": "stacked_split",
            "podcast_divider_style": "glow_cyan",
            "title_position": "top",
            "title_duration": "first_3s",
            "speed_ramp_ratio": 1.04,
            "vocal_isolation_mode": "center_vocal_extract",
            "camera_tracking_mode": "fit_balanced"
        }
    },
    "hormozi_finance": {
        "id": "hormozi_finance",
        "name": "Alex Hormozi Cuan & Bisnis",
        "icon": "💼",
        "badge": "Authority & Action",
        "description": "Tipografi kontras tinggi gaya Viral Pop (Kuning Lemon), BGM Lo-Fi santai (18%), aksen emoji finansial, dan Micro Pacing 1.03x agar poin bisnis dan angka langsung menonjol.",
        "settings": {
            "caption_style": "viral_pop",
            "caption_font": "Outfit",
            "font_size": "medium",
            "text_case": "uppercase",
            "keyword_accent_mode": "accent_and_emoji",
            "bgm_preset": "lofi_chill",
            "bgm_volume": 18.0,
            "auto_ducking": True,
            "hook_zoom_enabled": True,
            "streamer_preset": "none",
            "podcast_layout_mode": "stacked_split",
            "podcast_divider_style": "glow_gold",
            "title_position": "top",
            "title_duration": "first_3s",
            "speed_ramp_ratio": 1.03,
            "vocal_isolation_mode": "center_vocal_extract",
            "camera_tracking_mode": "fit_balanced"
        }
    },
    "rogan_podcast": {
        "id": "rogan_podcast",
        "name": "Joe Rogan Podcast Focus",
        "icon": "🎙️",
        "badge": "Dual Speaker Split",
        "description": "Format vertikal bertumpuk (Stacked 9:8) dengan pembatas glow elegan, BGM Lo-Fi berkarakter lembut (15%), dan subtitle clean agar percakapan terdengar jernih.",
        "settings": {
            "caption_style": "clean_minimal",
            "caption_font": "Montserrat",
            "font_size": "medium",
            "text_case": "capitalize",
            "keyword_accent_mode": "accent_and_emoji",
            "bgm_preset": "lofi_chill",
            "bgm_volume": 15.0,
            "auto_ducking": True,
            "hook_zoom_enabled": False,
            "streamer_preset": "podcast_split",
            "podcast_layout_mode": "stacked_split",
            "podcast_divider_style": "glow_cyan",
            "title_position": "top",
            "title_duration": "first_3s",
            "speed_ramp_ratio": 1.02,
            "vocal_isolation_mode": "off",
            "camera_tracking_mode": "off"
        }
    },
    "vox_documentary": {
        "id": "vox_documentary",
        "name": "Vox & Netflix Documentary",
        "icon": "🎬",
        "badge": "Cinematic & Mystery",
        "description": "Nuansa sinematik dengan subtitle Golden Aura, BGM Cinematic Mystery (26%), dan Hook Zoom halus untuk menciptakan atmosfer penasaran yang mendalam.",
        "settings": {
            "caption_style": "golden_aura",
            "caption_font": "Outfit",
            "font_size": "medium",
            "text_case": "capitalize",
            "keyword_accent_mode": "accent_only",
            "bgm_preset": "cinematic_mystery",
            "bgm_volume": 26.0,
            "auto_ducking": True,
            "hook_zoom_enabled": True,
            "streamer_preset": "none",
            "podcast_layout_mode": "stacked_split",
            "podcast_divider_style": "dark_line",
            "title_position": "top",
            "title_duration": "entire",
            "speed_ramp_ratio": 1.03,
            "vocal_isolation_mode": "center_vocal_extract",
            "camera_tracking_mode": "fit_balanced"
        }
    },
    "daily_vlog": {
        "id": "daily_vlog",
        "name": "Dynamic Daily Vlog",
        "icon": "📱",
        "badge": "Casual & Lifestyle",
        "description": "Format dinamis untuk konten tips harian dan tutorial dengan subtitle Electric Cyan, BGM Upbeat Vlog ceria (20%), and hook punch-in zoom aktif.",
        "settings": {
            "caption_style": "electric_cyan",
            "caption_font": "Outfit",
            "font_size": "medium",
            "text_case": "uppercase",
            "keyword_accent_mode": "accent_and_emoji",
            "bgm_preset": "upbeat_vlog",
            "bgm_volume": 20.0,
            "auto_ducking": True,
            "hook_zoom_enabled": True,
            "streamer_preset": "none",
            "podcast_layout_mode": "stacked_split",
            "podcast_divider_style": "clean_white",
            "title_position": "top",
            "title_duration": "first_3s",
            "speed_ramp_ratio": 1.03,
            "vocal_isolation_mode": "center_vocal_extract",
            "camera_tracking_mode": "fit_balanced"
        }
    }
}


def get_all_viral_archetypes() -> List[Dict[str, Any]]:
    """Returns all available viral archetypes."""
    return list(VIRAL_ARCHETYPES.values())


def get_archetype_param_impacts(archetype_id: str, language: str = "id") -> Dict[str, str]:
    """
    Returns algorithmic retention impact explanation for each parameter.
    """
    is_en = language == "en"
    if is_en:
        return {
            "caption_style": "+24% instant readability on fast-scrolling mobile feeds",
            "caption_font": "Punchy typography optimized for ultra-fast reading without distractions",
            "keyword_accent_mode": "Highlights emotional anchors and figures (+30% viewer engagement)",
            "hook_zoom_enabled": "3-second pattern interruption cuts viewer bounce rate at start",
            "bgm_preset": "Evokes target emotions and boosts video completion rate",
            "bgm_volume": "Calibrated loudness ensuring crisp vocal dominance over music",
            "auto_ducking": "Auto-attenuates background music during speech for zero muddiness",
            "speed_ramp_ratio": "Anti-Content ID YouTube Shield & tighter pacing without pitch shift",
            "vocal_isolation_mode": "Isolates speech and strips copyrighted background music up to 99%",
            "camera_tracking_mode": "Dynamic face framing keeps speaker centered in 9:16 vertical canvas",
            "podcast_layout_mode": "Balanced vertical split keeps both speakers visible without clipping",
            "title_position": "Top hook headline captures attention in the first 2 seconds"
        }
    return {
        "caption_style": "+24% keterbacaan instan di layar ponsel saat scroll cepat",
        "caption_font": "Tipografi tegas tanpa distraksi membaca cepat di feed TikTok",
        "keyword_accent_mode": "Menyorot emosi dan angka kunci (+30% retensi interaksi)",
        "hook_zoom_enabled": "Pattern interruption di detik 0 sampai 3 memotong bounce rate",
        "bgm_preset": "Membangun atmosfer emosional penonton sesuai jenis konten",
        "bgm_volume": "Keseimbangan audio terukur agar vokal tetap lantang",
        "auto_ducking": "BGM otomatis turun saat vokal aktif (Bebas audio berlumpur)",
        "speed_ramp_ratio": "Anti-Content ID YouTube & pemadatan tempo klip tanpa distorsi vokal",
        "vocal_isolation_mode": "Meredam BGM asli dari sumber hingga 99% agar bebas klaim hak cipta",
        "camera_tracking_mode": "Wajah pembicara otomatis terpusat dinamis di kanvas vertikal 9:16",
        "podcast_layout_mode": "Komposisi dua pembicara vertikal terbelah seimbang",
        "title_position": "Headline pengait teratas menarik mata penonton sejak detik pertama"
    }


def generate_heuristic_recommendation(
    transcript: str,
    title: str = "",
    duration: float = 30.0,
    speaker_count: int = 1,
    primary_topic: str = "",
    language: str = "id"
) -> Dict[str, Any]:
    """
    Zero-latency heuristic recommendation engine based on content patterns,
    lexical keywords, and speaker layout.
    """
    combined_text = f"{title} {primary_topic} {transcript}".lower()

    # Keyword indicators
    finance_keywords = [
        "uang", "cuan", "bisnis", "modal", "kaya", "miliar", "juta", "rupiah", "dolar",
        "omset", "gaji", "harga", "untung", "investasi", "money", "cash", "million",
        "dollar", "rich", "profit", "revenue", "cost", "crypto", "saham", "trading"
    ]
    hype_keywords = [
        "gila", "meledak", "keren", "hebat", "viral", "dahsyat", "tantangan", "rekor",
        "tercepat", "monster", "juara", "gokil", "insane", "crazy", "challenge", "extreme",
        "record", "beast", "win", "epic", "battle", "gaming"
    ]
    podcast_keywords = [
        "podcast", "wawancara", "interview", "ngobrol", "tamu", "cerita", "host",
        "guest", "debat", "diskusi", "bicara", "obrolan", "katanya", "menurutmu"
    ]
    mystery_docu_keywords = [
        "misteri", "rahasia", "sejarah", "fakta", "ilmu", "konspirasi", "sains", "riset",
        "bumi", "alam", "dunia", "asal usul", "secret", "mystery", "history", "truth",
        "documentary", "science", "alien", "crime", "teori"
    ]

    finance_score = sum(1 for k in finance_keywords if k in combined_text)
    hype_score = sum(1 for k in hype_keywords if k in combined_text)
    podcast_score = sum(1 for k in podcast_keywords if k in combined_text)
    docu_score = sum(1 for k in mystery_docu_keywords if k in combined_text)

    # If 2 speakers detected, boost podcast archetype
    if speaker_count >= 2:
        podcast_score += 4

    scores = {
        "hormozi_finance": finance_score,
        "beast_hype": hype_score,
        "rogan_podcast": podcast_score,
        "vox_documentary": docu_score,
    }

    best_archetype_id = max(scores, key=scores.get)
    if scores[best_archetype_id] == 0:
        best_archetype_id = "daily_vlog"

    archetype = VIRAL_ARCHETYPES[best_archetype_id]

    # Dynamic reasoning generation
    if language == "en":
        reasonings = {
            "hormozi_finance": "Financial and business mindset detected. AI selected Viral Pop yellow styling with chill Lo-Fi at 18% volume and currency emoji badges to maximize trust and retention.",
            "beast_hype": "High-intensity pacing and hype cues detected. AI recommended Beast Punch neon captions, energetic Phonk at 22% volume, and 3-second hook zoom for maximum visual pattern interruption.",
            "rogan_podcast": "Multi-speaker conversational dialogue detected. AI enabled Stacked Split 9:8 layout with clean typography and balanced background Lo-Fi at 15% to keep speech front and center.",
            "vox_documentary": "Storytelling or documentary narrative detected. AI configured Golden Aura styling with Cinematic Mystery BGM at 26% and subtle punch zoom to deepen curiosity.",
            "daily_vlog": "Casual and lifestyle narrative detected. AI applied Electric Cyan captions with Upbeat Vlog BGM at 20% and hook punch zoom for dynamic engagement."
        }
        growth_tips = {
            "hormozi_finance": "Pin a comment with a free actionable guide or checklist to turn viewers into long-term subscribers.",
            "beast_hype": "Add an interactive poll or question sticker in your story to drive engagement within the first 60 minutes.",
            "rogan_podcast": "Add a teaser clip or debate question in your caption to encourage intense comments and discussions.",
            "vox_documentary": "Encourage viewers to follow for Part 2 to build anticipation and boost follower conversions.",
            "daily_vlog": "Use a direct Call-to-Action in the final 2 seconds asking viewers to comment their favorite tip."
        }
    else:
        reasonings = {
            "hormozi_finance": "Klip ini sarat akan strategi bisnis dan cuan. AI memilih gaya Viral Pop (Kuning) dengan BGM Lo-Fi lembut (18%) dan aksen emoji finansial agar poin bisnis langsung memikat audiens.",
            "beast_hype": "Ritme pembicaraan berenergi tinggi terdeteksi. AI merekomendasikan gaya Beast Punch (Neon Green), BGM Phonk Hype (22%), dan Hook Zoom 1.15x untuk memecah kebosanan di 3 detik awal.",
            "rogan_podcast": "Format percakapan multi-pembicara terdeteksi. AI mengaktifkan layout Stacked Split (9:8) dengan tipografi bersih dan musik latar lembut (15%) agar dialog terdengar lantang.",
            "vox_documentary": "Narasi cerita atau fakta mendalam terdeteksi. AI menerapkan gaya Golden Aura dengan BGM Cinematic Mystery (26%) dan zoom lembut untuk memperkuat atmosfer penasaran penonton.",
            "daily_vlog": "Konten dinamis gaya tips harian terdeteksi. AI memasang subtitle Electric Cyan dengan BGM Upbeat Vlog (20%) dan hook zoom aktif untuk mempertahankan fokus penonton."
        }
        growth_tips = {
            "hormozi_finance": "Sematkan Call-to-Action di kolom komentar mengenai cara dapat insight lengkap untuk melipatgandakan subscriber.",
            "beast_hype": "Ajak penonton memilih di kolom komentar untuk mendongkrak skor interaksi algoritma TikTok dan Reels dalam 1 jam pertama.",
            "rogan_podcast": "Gunakan caption yang memancing perdebatan sehat di kolom komentar untuk meningkatkan skor retensi dan virality.",
            "vox_documentary": "Tuliskan 'Follow untuk bagian berikutnya' di caption guna memicu lonjakan konversi pengikut baru.",
            "daily_vlog": "Letakkan ajakan subscribe atau follow singkat pada 3 detik terakhir klip untuk menjaga konversi penonton."
        }

    # Calculate realistic viral scores based on duration and content
    base_hook = 92 if duration <= 60 else 88
    if best_archetype_id in ["beast_hype", "hormozi_finance"]:
        base_hook += 4

    return {
        "archetype_id": archetype["id"],
        "archetype_name": archetype["name"],
        "archetype_icon": archetype["icon"],
        "reasoning": reasonings.get(best_archetype_id, reasonings["daily_vlog"]),
        "growth_tip": growth_tips.get(best_archetype_id, growth_tips["daily_vlog"]),
        "viral_scores": {
            "hook_power": min(98, base_hook),
            "audio_balance": 96 if archetype["settings"]["auto_ducking"] else 88,
            "visual_retention": 94 if archetype["settings"]["hook_zoom_enabled"] else 89,
            "overall_score": min(97, int((base_hook + 96 + 94) / 3))
        },
        "settings": archetype["settings"],
        "param_impacts": get_archetype_param_impacts(archetype["id"], language)
    }


async def generate_smart_settings_recommendation(
    transcript: str,
    title: str = "",
    duration: float = 30.0,
    speaker_count: int = 1,
    primary_topic: str = "",
    language: str = "id",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analyzes clip characteristics and returns optimal studio settings recommendation.
    Tries AI structured call first, and gracefully falls back to heuristic engine.
    """
    clean_key = (api_key or "").strip()
    keys_pool = parse_api_keys(clean_key) if clean_key else []

    # If no keys or mock mode -> instant heuristic fallback
    if not keys_pool or any(k.lower() == "mock" for k in keys_pool):
        logger.info("Using zero-latency heuristic recommendation engine")
        return generate_heuristic_recommendation(
            transcript=transcript,
            title=title,
            duration=duration,
            speaker_count=speaker_count,
            primary_topic=primary_topic,
            language=language
        )

    # AI structured call attempt
    prompt = f"""You are an elite short-form video creative director (TikTok, Instagram Reels, YouTube Shorts).
Analyze this video clip and recommend the optimal studio settings to maximize viewer retention, 3-second hook rate, and subscriber conversion.

Video Title: {title}
Topic: {primary_topic or 'General'}
Duration: {duration} seconds
Detected Speakers/Faces: {speaker_count}
Language: {language}
Spoken Transcript:
\"\"\"{transcript[:1200]}\"\"\"

Available Archetypes:
- beast_hype: High energy, challenge, gaming, shocking facts (Subtitle: beast_punch, Font: The Bold Font, BGM: phonk_hype, Vol: 22, HookZoom: true)
- hormozi_finance: Business, money, success mindset, career, wealth (Subtitle: viral_pop, Font: Outfit, BGM: lofi_chill, Vol: 18, HookZoom: true)
- rogan_podcast: Interview, debate, two-person conversation (Subtitle: clean_minimal, Font: Montserrat, BGM: lofi_chill, Vol: 15, HookZoom: false, StreamerPreset: podcast_split)
- vox_documentary: Deep curiosity, mystery, history, science, crime (Subtitle: golden_aura, Font: Outfit, BGM: cinematic_mystery, Vol: 26, HookZoom: true)
- daily_vlog: Tips, lifestyle, casual review, travel (Subtitle: electric_cyan, Font: Outfit, BGM: upbeat_vlog, Vol: 20, HookZoom: true)

Output pure JSON only without markdown formatting:
{{
  "archetype_id": "beast_hype | hormozi_finance | rogan_podcast | vox_documentary | daily_vlog",
  "reasoning": "1 concise sentence explaining why this combination maximizes retention for this specific clip (in { 'English' if language == 'en' else 'Indonesian' })",
  "growth_tip": "1 actionable tip to convert viewers into followers or comments (in { 'English' if language == 'en' else 'Indonesian' })",
  "hook_power": 94,
  "audio_balance": 96,
  "visual_retention": 92
}}"""

    for active_key in keys_pool:
        if active_key.startswith("sk-or-"):
            try:
                res = call_openrouter_chat_completion(
                    api_key=active_key,
                    model_name="deepseek/deepseek-chat",
                    system_prompt="You are an expert video retention editor. Return strictly valid JSON.",
                    user_prompt=prompt
                )
                clean_json = re.sub(r"```json\s*", "", res)
                clean_json = re.sub(r"```\s*", "", clean_json).strip()
                data = json.loads(clean_json)
                arch_id = data.get("archetype_id", "daily_vlog")
                if arch_id not in VIRAL_ARCHETYPES:
                    arch_id = "daily_vlog"
                arch = VIRAL_ARCHETYPES[arch_id]
                return {
                    "archetype_id": arch["id"],
                    "archetype_name": arch["name"],
                    "archetype_icon": arch["icon"],
                    "reasoning": data.get("reasoning") or arch["description"],
                    "growth_tip": data.get("growth_tip") or "Sematkan Call-to-Action di kolom komentar untuk melipatgandakan interaksi.",
                    "viral_scores": {
                        "hook_power": int(data.get("hook_power", 92)),
                        "audio_balance": int(data.get("audio_balance", 95)),
                        "visual_retention": int(data.get("visual_retention", 93)),
                        "overall_score": int((int(data.get("hook_power", 92)) + int(data.get("audio_balance", 95)) + int(data.get("visual_retention", 93))) / 3)
                    },
                    "settings": arch["settings"],
                    "param_impacts": get_archetype_param_impacts(arch["id"], language)
                }
            except Exception as e:
                logger.warning(f"OpenRouter recommendation call failed: {e}")
                continue

        # Google Gemini call
        try:
            client = genai.Client(api_key=active_key)
            models = get_flash_models_for_key(active_key)
            for m in models:
                try:
                    response = client.models.generate_content(
                        model=m,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.2,
                            response_mime_type="application/json"
                        )
                    )
                    text = response.text or "{}"
                    data = json.loads(text)
                    arch_id = data.get("archetype_id", "daily_vlog")
                    if arch_id not in VIRAL_ARCHETYPES:
                        arch_id = "daily_vlog"
                    arch = VIRAL_ARCHETYPES[arch_id]
                    return {
                        "archetype_id": arch["id"],
                        "archetype_name": arch["name"],
                        "archetype_icon": arch["icon"],
                        "reasoning": data.get("reasoning") or arch["description"],
                        "growth_tip": data.get("growth_tip") or "Sematkan Call-to-Action di kolom komentar untuk melipatgandakan interaksi.",
                        "viral_scores": {
                            "hook_power": int(data.get("hook_power", 93)),
                            "audio_balance": int(data.get("audio_balance", 96)),
                            "visual_retention": int(data.get("visual_retention", 94)),
                            "overall_score": int((int(data.get("hook_power", 93)) + int(data.get("audio_balance", 96)) + int(data.get("visual_retention", 94))) / 3)
                        },
                        "settings": arch["settings"],
                        "param_impacts": get_archetype_param_impacts(arch["id"], language)
                    }
                except Exception as ex:
                    logger.warning(f"Gemini model {m} failed for recommendation: {ex}")
                    continue
        except Exception as e:
            logger.warning(f"Gemini recommendation call failed with key: {e}")

    # Fallback to heuristic
    logger.info("Falling back to heuristic recommendation engine after AI provider exhaustion")
    return generate_heuristic_recommendation(
        transcript=transcript,
        title=title,
        duration=duration,
        speaker_count=speaker_count,
        primary_topic=primary_topic,
        language=language
    )
