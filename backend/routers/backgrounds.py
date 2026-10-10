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
from backend.utils.background_presets import BUILTIN_BACKGROUND_PRESETS, get_preset_by_id

router = APIRouter(tags=["Backgrounds"])

BASE_BACKEND_DIR = Path(__file__).resolve().parent.parent
BACKGROUNDS_DIR = BASE_BACKEND_DIR / "backgrounds"
UPLOADS_BG_DIR = BACKGROUNDS_DIR / "uploads"
PRESETS_BG_DIR = BACKGROUNDS_DIR / "presets"

# Pastikan direktori selalu siap
UPLOADS_BG_DIR.mkdir(parents=True, exist_ok=True)
PRESETS_BG_DIR.mkdir(parents=True, exist_ok=True)

MAX_BG_IMAGE_BYTES = 30 * 1024 * 1024      # 30 MB
MAX_BG_VIDEO_BYTES = 500 * 1024 * 1024     # 500 MB

ALLOWED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_VIDEO_EXTS = {".mp4", ".webm", ".mov"}
ALLOWED_ALL_EXTS = ALLOWED_IMAGE_EXTS | ALLOWED_VIDEO_EXTS


def _is_safe_bg_path(target_path: Path) -> bool:
    """Memastikan path file berada di dalam folder backgrounds yang diizinkan."""
    try:
        resolved = target_path.resolve()
        allowed_roots = [UPLOADS_BG_DIR.resolve(), PRESETS_BG_DIR.resolve(), BACKGROUNDS_DIR.resolve()]
        return any(resolved == root or resolved.is_relative_to(root) for root in allowed_roots)
    except Exception:
        return False


async def _save_chunked_file(file: UploadFile, save_path: Path, max_bytes: int) -> int:
    """Menyimpan file unggahan secara streaming chunked untuk mencegah memory exhaustion."""
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
                        detail=f"Ukuran file melebihi batas maksimum yang diizinkan ({limit_mb} MB)."
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
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan file latar belakang: {str(e)}")


@router.get("/api/backgrounds/presets")
def get_background_presets():
    """Mengambil katalog lengkap preset latar belakang bawaan."""
    return {
        "success": True,
        "presets": BUILTIN_BACKGROUND_PRESETS
    }


@router.post("/api/backgrounds/upload")
async def upload_background_media(file: UploadFile = File(...)):
    """
    Mengunggah gambar atau video untuk dijadikan latar belakang short clip kustom.
    Format yang didukung: .png, .jpg, .jpeg, .webp, .mp4, .webm, .mov.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Tidak ada file yang dipilih.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_ALL_EXTS:
        raise HTTPException(
            status_code=400,
            detail=f"Format file tidak didukung. Format yang diizinkan: {', '.join(sorted(ALLOWED_ALL_EXTS))}"
        )

    is_video = ext in ALLOWED_VIDEO_EXTS
    max_limit = MAX_BG_VIDEO_BYTES if is_video else MAX_BG_IMAGE_BYTES
    clean_stem = re.sub(r'[^a-zA-Z0-9_-]', '_', os.path.splitext(file.filename)[0]).strip()
    if not clean_stem:
        clean_stem = "custom_bg"

    unique_id = f"bg_{uuid.uuid4().hex[:10]}"
    saved_filename = f"{unique_id}_{clean_stem}{ext}"
    save_path = UPLOADS_BG_DIR / saved_filename

    try:
        bytes_written = await _save_chunked_file(file, save_path, max_limit)
        logger.info(f"Background uploaded: {file.filename} -> {saved_filename} ({bytes_written} bytes)")

        return {
            "success": True,
            "id": unique_id,
            "filename": file.filename,
            "saved_name": saved_filename,
            "file_path": str(save_path),
            "url": f"/api/backgrounds/file/{saved_filename}",
            "type": "video" if is_video else "image",
            "size_bytes": bytes_written
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving background: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal mengunggah latar belakang: {str(e)}")


@router.get("/api/backgrounds/list")
def list_all_backgrounds():
    """Mengembalikan daftar lengkap gabungan antara preset bawaan dan unggahan kustom pengguna."""
    user_uploads: List[Dict[str, Any]] = []

    if UPLOADS_BG_DIR.exists():
        for f in sorted(UPLOADS_BG_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if not f.is_file():
                continue
            ext = f.suffix.lower()
            if ext not in ALLOWED_ALL_EXTS:
                continue

            is_video = ext in ALLOWED_VIDEO_EXTS
            clean_display_name = re.sub(r'^bg_[a-f0-9]{10}_', '', f.stem).replace('_', ' ').title()

            user_uploads.append({
                "id": f.stem,
                "name": clean_display_name or f.name,
                "category": "user_upload",
                "type": "custom_video" if is_video else "custom_image",
                "saved_name": f.name,
                "file_path": str(f),
                "url": f"/api/backgrounds/file/{f.name}",
                "size_bytes": f.stat().st_size,
                "created_at": f.stat().st_mtime
            })

    return {
        "success": True,
        "presets": BUILTIN_BACKGROUND_PRESETS,
        "user_uploads": user_uploads
    }


@router.get("/api/backgrounds/file/{filename:path}")
def stream_background_file(filename: str, request: Request):
    """
    Menyajikan file background (gambar atau video) dengan dukungan HTTP 206 Partial Content
    agar preview di browser berjalan instan, mulus, dan responsif.
    """
    clean_name = os.path.basename(filename)
    # Cari di folder uploads atau presets
    file_path = UPLOADS_BG_DIR / clean_name
    if not file_path.exists():
        file_path = PRESETS_BG_DIR / clean_name

    if not file_path.exists() or not _is_safe_bg_path(file_path):
        raise HTTPException(status_code=404, detail="File latar belakang tidak ditemukan.")

    file_size = file_path.stat().st_size
    ext = os.path.splitext(clean_name)[1].lower()

    if ext in ALLOWED_IMAGE_EXTS:
        media_type = "image/png" if ext == ".png" else "image/webp" if ext == ".webp" else "image/jpeg"
        return FileResponse(file_path, media_type=media_type, filename=clean_name)

    # Video streaming dengan HTTP range
    media_type = "video/webm" if ext == ".webm" else "video/quicktime" if ext == ".mov" else "video/mp4"
    range_header = request.headers.get("range")
    if not range_header:
        def iter_full():
            with open(file_path, "rb") as f:
                while chunk := f.read(1024 * 512):
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
                chunk_size = min(1024 * 512, bytes_left)
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


@router.delete("/api/backgrounds/{filename}")
def delete_user_background(filename: str):
    """Menghapus file latar belakang yang diunggah pengguna."""
    clean_name = os.path.basename(filename)
    file_path = UPLOADS_BG_DIR / clean_name

    if not file_path.exists() or not _is_safe_bg_path(file_path):
        raise HTTPException(status_code=404, detail="File latar belakang tidak ditemukan.")

    try:
        file_path.unlink()
        logger.info(f"Background deleted: {clean_name}")
        return {"success": True, "message": f"Latar belakang {clean_name} berhasil dihapus."}
    except Exception as e:
        logger.error(f"Gagal menghapus background {clean_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Gagal menghapus file: {str(e)}")
