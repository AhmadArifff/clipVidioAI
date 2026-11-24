# Domain 01: Ingestion & AI Viral Analysis Pipeline

## Alur End-to-End (`/api/analyze` SSE)
1. **Akuisisi Sumber**:
   * **YouTube URL**: `youtube_service.py::fetch_video_metadata()` (judul, durasi, channel, retention heatmap) + `fetch_transcript()` (multi-tier: YouTube Transcript API -> Supadata residential -> Auto-Whisper fallback).
   * **Upload Lokal / Google Drive**: `routers/media.py` / `gdrive_service.py` -> `compute_audio_energy_heatmap()` + `transcribe_local_video_file()`.
2. **Smart Token Optimization (`compact_transcript`)**:
   * Untuk video panjang (> 30 menit), segmen dipadatkan maksimal 950 baris sambil mempertahankan 180 detik intro, 180 detik outro, puncak heatmap tertinggi, dan sampel merata.
3. **AI Viral Selection Prompt (`routers/analyze.py`)**:
   * **Zero-Translation Rule**: 100% output mengikuti bahasa asli video (ID tetap ID, EN tetap EN).
   * **Zero-Fluff 3-Second Hook**: Dilarang mulai dari sapaan/filler; mulai langsung di konflik atau pertanyaan pemicu penasaran.
   * **3-Way Psychological Framing**: Kontroversial/Kritis, Sangat Bagus/Respect, atau Lucu/Absurd.
   * **Open Loop + Muted Hook Gate**: Setiap klip wajib menyertakan `open_loop_question` (rasa penasaran 0-3 detik), `payoff_time` (detik jawaban/klimaks tuntas), dan `muted_hook_overlay` (teks layar <= 6 kata yang paham meski tanpa suara).
4. **AI Social Copywriting (`services/copywriting_service.py`)**:
   * Menghasilkan 3 variasi Hook Title (Curiosity, Contrarian, Action), caption TikTok/Reels & YouTube Shorts, `pinned_comment` pemicu diskusi, serta 12-15 hashtag.
