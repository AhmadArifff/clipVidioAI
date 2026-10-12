from backend.routers.analyze import router as analyze_router
from backend.routers.audio import router as audio_router
from backend.routers.backgrounds import router as backgrounds_router
from backend.routers.cookies import router as cookies_router
from backend.routers.copywriting import router as copywriting_router
from backend.routers.downloads import router as downloads_router
from backend.routers.media import router as media_router
from backend.routers.recommendation import router as recommendation_router
from backend.routers.render import router as render_router
from backend.routers.system import router as system_router

__all__ = [
    "analyze_router",
    "audio_router",
    "backgrounds_router",
    "cookies_router",
    "copywriting_router",
    "downloads_router",
    "media_router",
    "recommendation_router",
    "render_router",
    "system_router",
]

