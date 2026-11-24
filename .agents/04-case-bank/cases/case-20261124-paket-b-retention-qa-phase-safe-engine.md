# Case Study: Paket B Retention & QA Engine, Phase-Safe Audio, Smart Silence Jumpcut, & .agents Standar V2

## 1. Identifikasi Kasus
* **ID Kasus**: `CASE-20261124-PAKET-B-RETENTION-QA-ENGINE`
* **Komponen Terdampak**:
  * Backend Video & Audio: `apps/api/backend/video_engine.py`, `apps/api/backend/services/silence_cutter_service.py`, `apps/api/backend/services/video_qa_service.py`, `apps/api/backend/services/render_service.py`, `apps/api/backend/schemas/render.py`
  * AI Analyzer: `apps/api/backend/schemas/analyze.py`, `apps/api/backend/routers/analyze.py`, `apps/api/backend/utils/text.py`
  * Frontend Studio & QA UI: `apps/web/src/types.ts`, `apps/web/src/components/ClipStudioSection.tsx`, `apps/web/src/components/BatchRenderProgressModal.tsx`, `apps/web/src/App.tsx`, `apps/web/src/locales/id.ts`, `apps/web/src/locales/en.ts`
  * Tata Kelola Agen: `AGENTS.md`, `.agents/feature-docs/`, `.agents/knowledge/`, `.agents/scripts/qa-kernel.py`, `.agents/scripts/sync-docs.js`
* **Tanggal Analisis**: 24 November 2026
* **Status**: VERIFIED_PRODUCTION_PASS

---

## 2. Masalah yang Diselesaikan & Inspirasi Skill Global
Audit terhadap 16 skill global baru (`showtime`, `reelmimic`, `motlab`, `herk-edit-kit`, `motionmaxxing`, dan standar tata kelola `.agents/` V2) mengidentifikasi 6 celah produksi pada pipeline Shorts/Reels ClipVidio AI:
1. **Inverted-Phase Vocal Cancellation**: `center_vocal_extract` sebelumnya menjumlahkan `0.5*L + 0.5*R` tanpa mengecek fase stereo, yang dapat menghapus vokal hingga `-91 dB` pada rekaman mikrofon stereo terbalik.
2. **Dead Air & Jeda Panjang di Awal/Tengah Klip**: Klip talking-head mentah sering memiliki hening 0.6s hingga 2s yang menurunkan retensi 3 detik pertama.
3. **Ketiadaan Automated Post-Render QA**: Output MP4 sebelumnya hanya dicek eksistensi file (`is_valid_mp4`), tanpa audit Frame 0 hitam, Integrated LUFS, True Peak, sample rate 48 kHz, leading silence, atau frozen frames.
4. **Keterbacaan & Safe Zone 9:16**: Belum tersedia preset subtitle kotak kontras tinggi (`BorderStyle=3`), floor durasi anti-flash `>= 0.40s`, overlay visual Safe Zone TikTok/Shorts/Reels, maupun ekspor sidecar `.srt` dan cover `.jpg`.
5. **Analisis Hook Tanpa Open Loop**: AI Analyzer sebelumnya belum secara eksplisit mengeluarkan struktur Open Loop, timestamp payoff, dan teks hook 3 detik untuk audiens mute.
6. **Drift Dokumentasi & Sisa Template Laravel di `.agents/`**: Direktori `.agents/` masih memuat aturan Laravel lama dan belum memiliki `feature-docs/` Standar V2, kamus disambiguasi, serta runner QA CLI.

---

## 3. Implementasi Arsitektural & Bug Produksi yang Tertangkap

### A. Fase 1: Audio, Caption, Safe Zone, & Export Polish
* **Phase-Safe Stereo-to-Mono (`detect_safe_mono_pan`)**: Membandingkan `volumedetect` kanal `L`, `R`, dan `0.5*L+0.5*R`. Jika selisih jatuh > 6 dB, sistem otomatis memilih kanal terkuat (`pan=stereo|c0=c0|c1=c0`).
* **Broadcast Audio Lock**: Mengunci `-ar 48000 -ac 2` pada kedua jalur encoder (GPU & CPU fallback) dan menambahkan `highpass=f=120` pada rantai BGM untuk kejernihan speaker ponsel.
* **High-Contrast Box & Anti-Flash**: Menambahkan preset `high_contrast_box` (`BorderStyle=3`, plat gelap `&H380A0A0F` + highlight emas `#FFE600`) dan menaikkan floor durasi chunk subtitle menjadi `0.40s`.
* **Safe Zone 9:16 & Kalibrasi Reaction Cam**: Menambahkan tombol overlay Safe Zone (`x: 64..916, y: 220..1440`) di Preview Studio serta menyelaraskan margin Reaction Cam PIP antara FFmpeg (`m_x_left=56, m_x_right=156, m_y_bottom=380, m_y_top=220`) dan DOM preview.
* **Auto Sidecar `.srt` + Sharpest Cover `.jpg`**: Dihasilkan otomatis di jalur single maupun merged dan dibundel ke dalam ZIP batch export.

### B. Fase 2: Retention, QA Gate, & Open-Loop AI
* **Smart Silence Jumpcut (`silence_cutter_service.py`)**: 3 mode (`off`, `natural` >= 0.55s, `snappy` >= 0.35s) dengan pemotongan 1-pass `trim`/`atrim`, 5ms anti-click `afade`, adaptive natural breath, fallback `silencedetect`, dan re-timing otomatis seluruh word timestamps.
* **Automated Post-Render Video QA (`video_qa_service.py`)**: Mengaudit integritas stream, Frame 0 luma/flat check, Integrated LUFS & True Peak (`ebur128`), leading silence 3 detik awal, dan `freezedetect`, lalu menampilkannya sebagai badge `PASS`/`WARN`/`FAIL` di `BatchRenderProgressModal.tsx`.
* **Open-Loop & Muted Hook Gate**: Menambahkan `framing_type`, `open_loop_question`, `payoff_time`, dan `muted_hook_overlay` pada `schemas/analyze.py`, `routers/analyze.py`, serta kartu klip di `App.tsx`.

### C. Dua Bug Laten yang Tertangkap Selama Implementasi & QA Kernel
1. **Unmuted Reaction Cam `UnboundLocalError`**: Di `video_engine.py`, saat `reaction_cam_mute_audio=False`, kode lama mengakses `audio_inputs_to_mix.append(...)` sebelum list tersebut dideklarasikan. Diperbaiki dengan menampung `rc_audio_idx_to_mix` (dilindungi `check_has_audio`) lalu mencampurnya setelah inisialisasi `audio_inputs_to_mix = []`.
2. **Lazy Import `cv2` & `numpy` pada `extract_cover_thumbnail`**: Tertangkap langsung oleh `qa-kernel.py` Check #5 (`name 'cv2' is not defined`) karena `video_engine.py` memakai lazy import di dalam fungsi. Diperbaiki dengan mengimpor `cv2` dan `numpy as np` secara lokal di dalam fungsi.

---

## 4. Verifikasi & Approval Gate
* **Tier-1 QA Kernel (`.\.venv\Scripts\python.exe .agents\scripts\qa-kernel.py`)**: `6 PASSED, 0 FAILED`
  * Phase-safe check: `L=-9.9dB, R=-9.9dB, L+R=-91.0dB -> pan=stereo|c0=c0|c1=c0`.
  * Silence Jumpcut: `trimmed 3.40s (6.00s -> 2.60s), first word at 0.12s`.
  * E2E Render + Unmuted RC + High-Contrast Box + BGM Ducking + SRT + Cover + QA: `PASS | -14.0 LUFS | TP -9.3 dB | 48kHz | Frame 0 OK`.
  * Anti-Slop Rule R-02: Zero em dashes di seluruh file modifikasi & baru.
* **Frontend TypeScript + Vite Build (`npm run build --prefix apps/web`)**: `0 errors`, bundle terbangun bersih dalam 3.42s.
* **Sync Script Syntax (`node --check .agents/scripts/sync-docs.js`)**: `0 errors`.
* **Dual Approval**: `qa-engineer` & `tech-critic` -> `VERIFIED_PRODUCTION_PASS`.
