from typing import List, Dict, Any, Optional
from pathlib import Path

# Built-in audio presets catalog
BUILTIN_AUDIO_PRESETS: List[Dict[str, Any]] = [
    {
        "id": "none",
        "name": "Tanpa BGM (Audio Asli)",
        "category": "none",
        "description": "Hanya menggunakan audio asli video tanpa musik latar",
        "file": "",
        "duration": 0,
    },
    {
        "id": "lofi_chill",
        "name": "Lo-Fi Chill Hop",
        "category": "lofi",
        "description": "Beat santai & hangat untuk storytelling, renungan, dan podcast",
        "file": "lofi_chill.mp3",
        "duration": 30,
    },
    {
        "id": "phonk_hype",
        "name": "Phonk Drift",
        "category": "phonk",
        "description": "Ketukan drum intens bertempo cepat untuk motivasi, gaming, dan aksi",
        "file": "phonk_hype.mp3",
        "duration": 30,
    },
    {
        "id": "cinematic_mystery",
        "name": "Cinematic Tension",
        "category": "cinematic",
        "description": "Nuansa dramatis dan misterius untuk teori konspirasi dan dokumenter",
        "file": "cinematic_mystery.mp3",
        "duration": 30,
    },
    {
        "id": "upbeat_vlog",
        "name": "Upbeat Sunny Vlog",
        "category": "upbeat",
        "description": "Musik ceria dan dinamis untuk review produk, tutorial, dan tips praktis",
        "file": "upbeat_vlog.mp3",
        "duration": 30,
    },
]


def get_audio_preset_by_id(preset_id: str) -> Optional[Dict[str, Any]]:
    """Mencari preset audio bawaan berdasarkan ID."""
    target = (preset_id or "").strip().lower()
    for preset in BUILTIN_AUDIO_PRESETS:
        if preset["id"] == target:
            return preset
    return None
