# Indeks Dokumentasi Fitur ClipVidio AI (Standar V2)

> **Pusat Dokumentasi Fitur & Arsitektur Sistem**: Direktori ini adalah *Single Source of Truth (SSOT)* seluruh modul fitur **ClipVidio AI** (`Clipper-Vidio-YT`) mengikuti **Standar V2 (10 Bagian: 8 Bagian Fondasi + Bagian 9 Peta Alur & Flow Testing Per-Kontrol UI + Bagian 10 Disambiguasi Fitur Kembar)**.

---

## Navigasi Modul Fitur (4 Modul Utama Terdokumentasi)

| No | Kategori | Nama Fitur | Endpoint / Komponen Utama | Status | Berkas Dokumen |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **01** | **Ingestion & Analisis** | YouTube/Upload Ingestion & AI Viral Analyzer (3-Way Framing + Open Loop) | `POST /api/analyze`, `App.tsx`, `routers/analyze.py` | `Done` | [`01-ingestion-analisis/youtube-upload-dan-ai-analyzer.md`](./01-ingestion-analisis/youtube-upload-dan-ai-analyzer.md) |
| **02** | **Clip Studio** | Canvas Framing, Background Customizer & Safe Zone 9:16 | `ClipStudioSection.tsx`, `BackgroundCustomizer.tsx`, `video_engine.py` | `Done` | [`02-clip-studio/canvas-framing-dan-safe-zone.md`](./02-clip-studio/canvas-framing-dan-safe-zone.md) |
| **03** | **Clip Studio** | Subtitle ASS/SRT, High-Contrast Box, Title Emoji & Reaction Cam PIP | `POST /api/reaction-cam/upload`, `ClipStudioSection.tsx`, `video_engine.py` | `Done` | [`02-clip-studio/subtitle-title-dan-reaction-cam.md`](./02-clip-studio/subtitle-title-dan-reaction-cam.md) |
| **04** | **Render & Export** | Batch Render (Single/Merged), Auto-Trim Dead Air Jumpcut, Audio Phase-Safe & Post-Render QA | `POST /api/render-batch`, `render_service.py`, `silence_cutter_service.py`, `video_qa_service.py` | `Done` | [`03-render-export/batch-render-silence-jumpcut-dan-qa.md`](./03-render-export/batch-render-silence-jumpcut-dan-qa.md) |

---

## 4 Dokumen Fondasi Global (Otomatis Disinkronkan via `sync-docs.js`)
1. [`../rules/10-architecture.md`](../rules/10-architecture.md) -> `system-architecture.md`
2. [`../rules/20-ffmpeg-video-engine.md`](../rules/20-ffmpeg-video-engine.md) -> `ffmpeg-video-engine.md`
3. [`../knowledge/bug-cases.md`](../knowledge/bug-cases.md) -> `production-bug-cases.md`
4. [`../knowledge/cross-feature-disambiguation.md`](../knowledge/cross-feature-disambiguation.md) -> `cross-feature-disambiguation.md`

---

## Cara Mirroring ke Portal SaaS (`documentasi-projects`)
```bash
node .agents/scripts/sync-docs.js
```
Skrip akan menyalin seluruh dokumen fitur + 4 fondasi global ke:
`C:\Users\ASUS\Documents\Web Dev\improving\documentasi-projects\content\projects\Clipper-Vidio-YT\`
serta memperbarui `manifest.json`.
