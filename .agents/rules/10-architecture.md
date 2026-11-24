# Standar Arsitektur Backend FastAPI & Monorepo (`ClipVidio AI`)

## 1. Pemisahan 4-Layer Backend (`apps/api/backend/`)
1. **Routers (`routers/*.py`)**: Thin HTTP/SSE controllers. Bertanggung jawab atas parsing request, validasi skema Pydantic, SSE progress streaming (`StreamingResponse`), dan HTTP error mapping. Tidak boleh menaruh logika FFmpeg mentah di dalam router.
2. **Schemas (`schemas/*.py`)**: Kontrak payload request/response berbasis Pydantic v2 (`ConfigDict(extra="ignore")` untuk backward compatibility dengan client lama).
3. **Services (`services/*.py`)**: Orkestrasi bisnis dan pipeline berat:
   * `ai_service.py`: Multi-key Gemini rotation & OpenRouter fallback.
   * `render_service.py`: Batch job state (`RENDER_BATCHES`), download segmen, silence cutting, transkripsi/ASS/SRT, pemanggilan `video_engine`, post-render QA (`video_qa_service`), dan packaging ZIP.
   * `silence_cutter_service.py`: Deteksi dan pemangkasan dead air + re-timing word timestamps.
   * `video_qa_service.py`: Audit otomatis MP4 pasca-render (Frame 0, LUFS, True Peak, Leading Silence, Freeze, AV Sync).
   * `copywriting_service.py`: Pembuatan hook titles, captions, pinned comment, hashtags, dan `metadata.txt`.
   * `youtube_service.py` / `gdrive_service.py` / `download_service.py`: Akuisisi media dan transkrip.
4. **Core Engine (`video_engine.py`)**: Konstruksi filtergraph FFmpeg, face tracking OpenCV (`YuNet`), generator subtitle `.ass`/`.srt`, rendering title PNG emoji, dan eksekusi FFmpeg GPU/CPU fallback.

## 2. Aturan Async & Non-Blocking
* Semua operasi blocking (FFmpeg subprocess, `yt-dlp`, OpenCV, Pillow, Whisper) **WAJIB** dijalankan di luar event loop FastAPI menggunakan `await asyncio.to_thread(...)`.
* Progress real-time ke Frontend dikirim melalui `RENDER_BATCHES` (polling `/api/render-batch-status/{batch_id}`) atau SSE `_sse(...)` pada endpoint `/api/analyze`.

## 3. Resiliensi & Graceful Degradation
* Jika fitur opsional gagal (misal emoji PNG overlay, silence cutter tanpa jeda, atau QA probe timeout), sistem wajib mencatat `logger.warning(...)` dan melakukan fallback aman ke jalur inti agar render MP4 tetap selesai tanpa crash 500.
