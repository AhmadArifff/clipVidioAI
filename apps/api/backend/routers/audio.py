import asyncio
import logging
import os
import re
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, File, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse

from backend.config import logger
from backend.utils.audio_presets import BUILTIN_AUDIO_PRESETS, get_audio_preset_by_id

router = APIRouter(tags=["Audio & BGM"])

BASE_BACKEND_DIR = Path(__file__).resolve().parent.parent
AUDIO_DIR = BASE_BACKEND_DIR / "audio"
UPLOADS_AUDIO_DIR = AUDIO_DIR / "uploads"
PRESETS_AUDIO_DIR = AUDIO_DIR / "presets"

# Pastikan direktori selalu siap
UPLOADS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
PRESETS_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

MAX_AUDIO_BYTES = 50 * 1024 * 1024  # 50 MB
ALLOWED_AUDIO_EXTS = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}


def _is_safe_audio_path(target_path: Path) -> bool:
    """Memastikan path file berada di dalam folder audio yang diizinkan."""
    try:
        resolved = target_path.resolve()
        allowed_roots = [UPLOADS_AUDIO_DIR.resolve(), PRESETS_AUDIO_DIR.resolve(), AUDIO_DIR.resolve()]
        return any(resolved == root or resolved.is_relative_to(root) for root in allowed_roots)
    except Exception:
        return False


async def _save_chunked_audio_file(file: UploadFile, save_path: Path, max_bytes: int) -> int:
    """Menyimpan file audio unggahan secara streaming chunked untuk mencegah memory exhaustion."""
    total_written = 0
    chunk_size = 1024 * 1024  # 1 MB
    try:
        with open(save_path, "wb") as f:
            while chunk := await file.read(chunk_size):
                total_written += len(chunk)
                if total_written > max_bytes:
                    f.close()
                    if save_path.exists():
                        save_path.unlink()
                    limit_mb = round(max_bytes / (1024 * 1024))
                    raise HTTPException(
                        status_code=413,
                        detail=f"Ukuran file audio melebihi batas maksimum yang diizinkan ({limit_mb} MB)."
                    )
                f.write(chunk)
        return total_written
    except HTTPException:
        raise
    except Exception as e:
        if save_path.exists():
            try:
                save_path.unlink()
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file audio: {str(e)}")


@router.get("/api/audio/presets")
def get_audio_presets():
    """Mengambil katalog lengkap preset musik latar bawaan serta berkas yang diunggah pengguna."""
    user_uploads = []
    if UPLOADS_AUDIO_DIR.exists():
        for f in sorted(UPLOADS_AUDIO_DIR.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext not in ALLOWED_AUDIO_EXTS:
                continue

            user_uploads.append({
                "id": f"custom_{f.name}",
                "name": f.stem.replace("_", " ").title(),
                "category": "custom",
                "description": f"File audio kustom ({ext[1:].upper()})",
                "file": f.name,
                "saved_name": f.name,
                "file_path": str(f),
                "url": f"/api/audio/file/{f.name}",
                "size_bytes": f.stat().st_size,
                "created_at": f.stat().st_mtime
            })

    # Tambahkan url streaming untuk preset bawaan jika ada filenya
    presets_with_url = []
    for p in BUILTIN_AUDIO_PRESETS:
        item = dict(p)
        if item.get("file"):
            preset_file = PRESETS_AUDIO_DIR / item["file"]
            if preset_file.exists():
                item["url"] = f"/api/audio/file/{item['file']}"
                item["size_bytes"] = preset_file.stat().st_size
        presets_with_url.append(item)

    return {
        "success": True,
        "presets": presets_with_url,
        "user_uploads": user_uploads
    }


@router.post("/api/upload-bgm")
@router.post("/api/audio/upload")
async def upload_audio_media(file: UploadFile = File(...)):
    """
    Mengunggah file musik latar (BGM) kustom.
    Format yang didukung: .mp3, .wav, .m4a, .aac, .ogg, .flac (Maksimal 50 MB).
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Tidak ada file audio yang dipilih.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Format audio tidak didukung. Format yang diizinkan: {', '.join(sorted(ALLOWED_AUDIO_EXTS))}"
        )

    safe_original_stem = re.sub(r"[^a-zA-Z0-9_\-]", "_", os.path.splitext(file.filename)[0])[:40]
    unique_name = f"bgm_{uuid.uuid4().hex[:8]}_{safe_original_stem}{ext}"
    target_path = UPLOADS_AUDIO_DIR / unique_name

    saved_bytes = await _save_chunked_audio_file(file, target_path, MAX_AUDIO_BYTES)
    logger.info(f"Custom BGM uploaded: {unique_name} ({saved_bytes} bytes)")

    return {
        "success": True,
        "id": f"custom_{unique_name}",
        "name": file.filename,
        "filename": file.filename,
        "saved_name": unique_name,
        "file": unique_name,
        "file_path": str(target_path),
        "category": "custom",
        "url": f"/api/audio/file/{unique_name}",
        "size_bytes": saved_bytes
    }


@router.get("/api/audio/file/{filename:path}")
def stream_audio_file(filename: str, request: Request):
    """
    Menyajikan file audio dengan dukungan HTTP 206 Partial Content (Byte-Range)
    agar preview playback dan seeking di browser berjalan instan.
    """
    clean_name = os.path.basename(filename)
    file_path = UPLOADS_AUDIO_DIR / clean_name
    if not file_path.exists():
        file_path = PRESETS_AUDIO_DIR / clean_name

    if not file_path.exists() or not _is_safe_audio_path(file_path):
        raise HTTPException(status_code=404, detail="File audio tidak ditemukan.")

    file_size = file_path.stat().st_size
    ext = os.path.splitext(clean_name)[1].lower()

    media_type_map = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".aac": "audio/aac",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac"
    }
    media_type = media_type_map.get(ext, "audio/mpeg")

    range_header = request.headers.get("range")
    if not range_header:
        def iter_full():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 256):
                    yield chunk

        return StreamingResponse(
            iter_full(),
            status_code=200,
            media_type=media_type,
            headers={
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
                "Content-Disposition": f'inline; filename="{clean_name}"'
            }
        )

    # Range parsing
    range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)
    if not range_match:
        return Response(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

    if start >= file_size or end >= file_size or start > end:
        return Response(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            headers={"Content-Range": f"bytes */{file_size}"}
        )

    content_length = end - start + 1

    def iter_range():
        with open(file_path, "rb") as f:
            f.seek(start)
            bytes_left = content_length
            while bytes_left > 0:
                chunk_size = min(1024 * 256, bytes_left)
                data = f.read(chunk_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data

    return StreamingResponse(
        iter_range(),
        status_code=206,
        media_type=media_type,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(content_length),
            "Content-Disposition": f'inline; filename="{clean_name}"'
        }
    )


@router.delete("/api/audio/{filename}")
def delete_user_audio(filename: str):
    """Menghapus file audio yang diunggah pengguna."""
    clean_name = os.path.basename(filename)
    file_path = UPLOADS_AUDIO_DIR / clean_name

    if not file_path.exists() or not _is_safe_audio_path(file_path):
        raise HTTPException(status_code=404, detail="File audio tidak ditemukan.")

    try:
        file_path.unlink()
        logger.info(f"Custom audio deleted: {clean_name}")
        return {"success": True, "message": f"File audio {clean_name} berhasil dihapus."}
    except Exception as e:
        logger.error(f"Gagal menghapus file audio {clean_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal menghapus file: {str(e)}")
