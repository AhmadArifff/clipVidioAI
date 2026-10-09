import json
import logging
import os
import re
import urllib.error
import urllib.request
from typing import List, Optional, Tuple

from google import genai

from backend.config import logger

KNOWN_FLASH_MODELS = [
    'gemini-2.5-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash',
    'gemini-2.0-flash-lite',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b',
]

KNOWN_OPENROUTER_MODELS = [
    'deepseek/deepseek-chat',
    'deepseek/deepseek-r1',
    'meta-llama/llama-3.3-70b-instruct',
    'anthropic/claude-3.5-haiku',
    'openai/gpt-4o-mini',
    'google/gemini-2.0-flash-001',
    'qwen/qwen-2.5-72b-instruct',
    'mistralai/mistral-small-24b-instruct-2501',
]


def parse_api_keys(raw_keys: Optional[str]) -> List[str]:
    """Parse comma or newline-separated API keys into a sanitized list of unique keys."""
    if not raw_keys:
        return []
    parts = re.split(r'[,;\n\r]+', raw_keys)
    seen = set()
    sanitized: List[str] = []
    for p in parts:
        cleaned = p.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            sanitized.append(cleaned)
    return sanitized


def parse_gemini_model_sort_key(name: str) -> Tuple[int, int, int, str]:
    """Sort key for Gemini models: parses major and minor versions (e.g. 3.7, 3.6, 3.5, 2.5, 2.0, 1.5),
    tier (standard > lite/8b > preview/exp), so newest and most capable models come first."""
    name_clean = (name or "").split('/')[-1].lower()
    m = re.search(r'(\d+)(?:\.(\d+))?', name_clean)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2)) if m.group(2) is not None else 0
    else:
        major, minor = 0, 0

    if 'lite' in name_clean or '8b' in name_clean:
        tier = 2
    elif 'exp' in name_clean or 'preview' in name_clean:
        tier = 1
    else:
        tier = 3

    return (major, minor, tier, name_clean)


def get_flash_models_for_key(client: genai.Client) -> List[str]:
    """Dynamically query all available flash models for the given API key.
    Discovers newer versions (e.g., 3.7, 3.6, 3.5) and earlier versions (2.5, 2.0, 1.5),
    merging with known fallback models and sorting in descending order of version/capability."""
    discovered = []
    try:
        models_page = client.models.list()
        for m in models_page:
            name = m.name or ""
            short_name = name.split('/')[-1]
            if "gemini" in short_name.lower() and "flash" in short_name.lower():
                if m.supported_actions and "generateContent" not in m.supported_actions:
                    continue
                # Exclude non-text, specialized, or non-generative tasks
                exclude_keywords = [
                    'tuning', 'thinking', 'vision', 'image', 'tts',
                    'omni', 'customtools', 'embed', 'realtime', 'robotics'
                ]
                if not any(x in short_name.lower() for x in exclude_keywords):
                    if short_name not in discovered:
                        discovered.append(short_name)
    except Exception as e:
        logger.warning(f"Could not dynamically list models: {e}")

    # Combine discovered with known flash models, preserving uniqueness
    combined_pool = list(dict.fromkeys(discovered + KNOWN_FLASH_MODELS))
    # Sort descending so newest versions (e.g. 2.5, 2.0, 1.5) are prioritized
    ordered = sorted(combined_pool, key=parse_gemini_model_sort_key, reverse=True)
    # Cap to top 4 distinct models to prevent excessive fallback cycles
    return ordered[:4]


def list_available_gemini_models(api_key: str = "") -> List[str]:
    """Fetches list of available Gemini models using the user's API key, prioritizing Flash models (newest first)."""
    default_models = [
        'gemini-2.5-flash',
        'gemini-2.5-flash-lite',
        'gemini-2.0-flash',
        'gemini-2.0-flash-lite',
        'gemini-1.5-flash',
        'gemini-2.5-pro'
    ]
    all_keys = parse_api_keys(api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEYS"))
    key_to_use = all_keys[0] if all_keys else ""
    if not key_to_use or key_to_use.lower() == "mock":
        return default_models
    try:
        client = genai.Client(api_key=key_to_use)
        models_page = client.models.list()
        
        flash_models = []
        pro_models = []
        other_models = []
        
        for m in models_page:
            name = m.name or ""
            if "gemini" in name.lower():
                if m.supported_actions and "generateContent" not in m.supported_actions:
                    continue
                
                short_name = name.split('/')[-1]
                exclude_keywords = [
                    'tuning', 'thinking', 'vision', 'image', 'tts',
                    'omni', 'customtools', 'embed', 'realtime', 'robotics'
                ]
                if any(x in short_name.lower() for x in exclude_keywords):
                    continue
                
                if "flash" in short_name.lower():
                    if short_name not in flash_models:
                        flash_models.append(short_name)
                elif "pro" in short_name.lower():
                    if short_name not in pro_models:
                        pro_models.append(short_name)
                elif any(x in short_name.lower() for x in ['lite', 'exp']):
                    if short_name not in other_models:
                        other_models.append(short_name)
        
        # Sort flash models by version descending (e.g. 3.7, 3.6, 3.5, 2.5, 2.0, 1.5)
        ordered_flash = sorted(
            list(dict.fromkeys(flash_models + KNOWN_FLASH_MODELS)),
            key=parse_gemini_model_sort_key,
            reverse=True
        )
        ordered_pro = sorted(pro_models, key=parse_gemini_model_sort_key, reverse=True)
        ordered_other = sorted(other_models, key=parse_gemini_model_sort_key, reverse=True)
        
        final_list = ordered_flash + ordered_pro + ordered_other
        if not final_list:
            final_list = default_models
            
        return final_list
    except Exception as e:
        logger.error(f"Error listing Gemini models: {e}")
        return default_models


def list_available_openrouter_models(api_key: str = "") -> List[str]:
    """Returns available OpenRouter models, querying remote registry if api_key is supplied."""
    if not api_key:
        return KNOWN_OPENROUTER_MODELS

    clean_key = api_key.strip()
    if clean_key.lower() == "mock":
        return KNOWN_OPENROUTER_MODELS

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {clean_key}",
                "HTTP-Referer": "https://github.com/AhmadArifff/clipVidioAI",
                "X-Title": "ClipVidio AI",
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_models = data.get("data", [])
            ids = [m.get("id") for m in raw_models if isinstance(m, dict) and m.get("id")]
            if ids:
                # Prioritize popular models
                prioritized = [m for m in KNOWN_OPENROUTER_MODELS if m in ids]
                remaining = [m for m in ids if m not in prioritized]
                return prioritized + remaining[:30]
    except Exception as e:
        logger.warning(f"Could not query OpenRouter remote models: {e}")

    return KNOWN_OPENROUTER_MODELS


def call_openrouter_chat_completion(
    api_key: str,
    model: str,
    prompt: str,
    timeout: float = 120.0
) -> str:
    """Execute a completion request to OpenRouter API and return the raw output text content."""
    clean_key = api_key.strip()
    if not clean_key:
        raise ValueError("OpenRouter API key is empty.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an expert AI video editor and viral content strategist. "
                    "Analyze dialogue, engagement spikes, and context to extract viral clip moments. "
                    "Respond STRICTLY in valid JSON matching this schema: "
                    '{"summary": "...", "clips": [{"title": "...", "start_time": 0.0, "end_time": 0.0, '
                    '"hook_time": 0.0, "virality_score": 90, "key_quotes": ["..."], "title_suggestion": "...", '
                    '"caption_suggestion": "...", "hashtag_suggestion": "..."}]}. '
                    "Do NOT wrap in markdown formatting if possible."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Authorization": f"Bearer {clean_key}",
            "HTTP-Referer": "https://github.com/AhmadArifff/clipVidioAI",
            "X-Title": "ClipVidio AI",
            "Content-Type": "application/json",
            "User-Agent": "ClipVidio-AI/1.0",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read().decode("utf-8")
            data = json.loads(body)
            choices = data.get("choices", [])
            if not choices:
                raise ValueError(f"OpenRouter returned empty choices: {body[:200]}")
            message = choices[0].get("message", {})
            content = message.get("content", "")
            return content
    except urllib.error.HTTPError as e:
        error_body = ""
        try:
            error_body = e.read().decode("utf-8")
        except Exception:
            pass
        if e.code == 429:
            raise RuntimeError(f"OpenRouter rate limit reached (429): {error_body}")
        elif e.code in (401, 403):
            raise PermissionError(f"OpenRouter unauthorized or invalid API key ({e.code}): {error_body}")
        elif e.code == 402:
            raise RuntimeError(f"OpenRouter payment required or insufficient credits (402): {error_body}")
        else:
            raise RuntimeError(f"OpenRouter HTTP Error {e.code}: {error_body or e.reason}")
    except Exception as e:
        raise RuntimeError(f"OpenRouter request failed: {e}")


class AIRouterService:
    """Enterprise AI Router Service managing multiple providers (Gemini, OpenRouter)
    and dynamic API key rotation."""

    @staticmethod
    def parse_keys(raw: Optional[str]) -> List[str]:
        return parse_api_keys(raw)

    @staticmethod
    def list_models(provider: str = "gemini", api_key: str = "") -> List[str]:
        p = (provider or "gemini").lower().strip()
        if p == "openrouter":
            return list_available_openrouter_models(api_key)
        return list_available_gemini_models(api_key)

    @staticmethod
    def call_openrouter(api_key: str, model: str, prompt: str, timeout: float = 120.0) -> str:
        return call_openrouter_chat_completion(api_key=api_key, model=model, prompt=prompt, timeout=timeout)

