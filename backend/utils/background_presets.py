from typing import List, Dict, Any, Optional
from pathlib import Path

# Built-in background presets catalog
BUILTIN_BACKGROUND_PRESETS: List[Dict[str, Any]] = [
    # ── 1. Ambient & Classic ──────────────────────────────────────────
    {
        "id": "blur_ambient",
        "name": "Ambient Blur",
        "category": "ambient",
        "type": "blur",
        "description": "Video asli diperbesar dan di-blur dinamis dengan saturasi sinematik",
        "preview_color": "linear-gradient(135deg, #1e293b, #0f172a)",
        "value": "blurred"
    },
    {
        "id": "obsidian_black",
        "name": "Obsidian Black",
        "category": "color",
        "type": "color",
        "description": "Latar hitam pekat minimalis elegan",
        "preview_color": "#09090b",
        "value": "#09090b"
    },
    {
        "id": "deep_slate",
        "name": "Deep Slate",
        "category": "color",
        "type": "color",
        "description": "Warna zinc/slate gelap profesional",
        "preview_color": "#18181b",
        "value": "#18181b"
    },
    {
        "id": "navy_midnight",
        "name": "Midnight Navy",
        "category": "color",
        "type": "color",
        "description": "Nuansa biru malam gelap sinematik",
        "preview_color": "#0f172a",
        "value": "#0f172a"
    },

    # ── 2. Cinematic Gradients ────────────────────────────────────────
    {
        "id": "gradient_neon_indigo",
        "name": "Neon Indigo",
        "category": "gradient",
        "type": "gradient",
        "description": "Gradasi ungu elektrik ke indigo modern",
        "preview_color": "linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%)",
        "value": "indigo_dark",
        "c0": "#1e1b4b",
        "c1": "#0f172a"
    },
    {
        "id": "gradient_cyber_emerald",
        "name": "Cyber Emerald",
        "category": "gradient",
        "type": "gradient",
        "description": "Gradasi hijau neon gelap estetika hacker",
        "preview_color": "linear-gradient(180deg, #064e3b 0%, #022c22 100%)",
        "value": "emerald_dark",
        "c0": "#064e3b",
        "c1": "#022c22"
    },
    {
        "id": "gradient_sunset_ruby",
        "name": "Sunset Ruby",
        "category": "gradient",
        "type": "gradient",
        "description": "Gradasi crimson ruby mewah hangat",
        "preview_color": "linear-gradient(180deg, #831843 0%, #3b0764 100%)",
        "value": "ruby_sunset",
        "c0": "#831843",
        "c1": "#3b0764"
    },
    {
        "id": "gradient_solar_amber",
        "name": "Solar Amber",
        "category": "gradient",
        "type": "gradient",
        "description": "Gradasi amber keemasan gelap",
        "preview_color": "linear-gradient(180deg, #78350f 0%, #1c1917 100%)",
        "value": "amber_solar",
        "c0": "#78350f",
        "c1": "#1c1917"
    },

    # ── 3. Motion & Viral Loops ──────────────────────────────────────
    {
        "id": "minecraft_parkour",
        "name": "Minecraft Parkour",
        "category": "motion",
        "type": "preset",
        "description": "Gameplay parkour Minecraft halus untuk retensi video shorts",
        "preview_color": "linear-gradient(135deg, #15803d, #14532d)",
        "value": "minecraft_parkour",
        "media_file": "minecraft_parkour.mp4"
    },
    {
        "id": "subway_surfers",
        "name": "Subway Runner",
        "category": "motion",
        "type": "preset",
        "description": "Gameplay subway runner loop kecepatan tinggi",
        "preview_color": "linear-gradient(135deg, #eab308, #ca8a04)",
        "value": "subway_surfers",
        "media_file": "subway_surfers.mp4"
    },
    {
        "id": "gta_mega_ramp",
        "name": "GTA Mega Ramp",
        "category": "motion",
        "type": "preset",
        "description": "Aksi stunt mobil ramp GTA 5 sinematik",
        "preview_color": "linear-gradient(135deg, #0284c7, #0369a1)",
        "value": "gta_mega_ramp",
        "media_file": "gta_mega_ramp.mp4"
    },
    {
        "id": "synthwave_neon_grid",
        "name": "Synthwave Grid",
        "category": "motion",
        "type": "preset",
        "description": "Loop wireframe jalan neon 80s retro wave",
        "preview_color": "linear-gradient(135deg, #d946ef, #6366f1)",
        "value": "synthwave_grid",
        "media_file": "synthwave_grid.mp4"
    },
    {
        "id": "lofi_aesthetic_rain",
        "name": "Lo-Fi Rainy Window",
        "category": "motion",
        "type": "preset",
        "description": "Suasana jendela hujan tenang estetis",
        "preview_color": "linear-gradient(135deg, #475569, #1e293b)",
        "value": "lofi_rain",
        "media_file": "lofi_rain.mp4"
    }
]

def get_preset_by_id(preset_id: str) -> Optional[Dict[str, Any]]:
    """Finds a background preset by its unique ID."""
    clean_id = (preset_id or "").strip().lower()
    for p in BUILTIN_BACKGROUND_PRESETS:
        if p["id"].lower() == clean_id or p.get("value", "").lower() == clean_id:
            return p
    return None


def get_all_background_presets() -> List[Dict[str, Any]]:
    """Returns the complete list of built-in background presets."""
    return BUILTIN_BACKGROUND_PRESETS


get_background_preset_by_id = get_preset_by_id

