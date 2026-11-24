# Domain Reference Knowledge Base (`ClipVidio AI`)

Panduan arsitektur referensi proyek **ClipVidio AI** (`Clipper-Vidio-YT`) sebagai sumber kebenaran tunggal (*Single Source of Truth*) untuk seluruh sesi perencanaan, implementasi, dan audit QA.

---

## Peta Strategi Pipeline Inti

| Domain | Modul Utama | Engine / Teknologi | Tanggung Jawab Inti |
| :--- | :--- | :--- | :--- |
| **1. Ingestion & AI Analysis** | `routers/analyze.py`, `services/youtube_service.py`, `services/ai_service.py`, `services/copywriting_service.py` | `yt-dlp`, Supadata, Whisper, Gemini Multi-Key, OpenRouter | Mengambil metadata, heatmap retensi, transkrip, lalu menemukan klip viral berbasis 3-Way Framing + Open Loop + Muted Hook + Pinned Comment. |
| **2. FFmpeg Video & Audio Engine** | `video_engine.py`, `services/silence_cutter_service.py`, `services/video_qa_service.py` | FFmpeg 8.x, FFprobe, OpenCV YuNet, Pillow | Framing 9:16/1:1/16:9, Face Tracking, Subtitle ASS/SRT, Reaction Cam PIP, Silence Jumpcut 1-pass, Phase-Safe Audio 48 kHz + Ducking, dan Post-Render QA. |
| **3. Studio WYSIWYG Preview** | `ClipStudioSection.tsx`, `BackgroundCustomizer.tsx`, `HeatmapTimeline.tsx`, `BatchRenderProgressModal.tsx` | React 19, Vite, TypeScript, i18n (`id.ts`/`en.ts`) | Pratinjau interaktif 320px yang presisi dengan kanvas 1080x1920, Safe Zone Overlay, pengaturan audio/caption/reaction cam, dan tampilan QA Badge hasil render. |
| **4. RenderSettings Contract** | `types.ts`, `App.tsx`, `schemas/render.py`, `services/render_service.py`, `video_engine.py` | TypeScript + Pydantic v2 | Menjaga 100% sinkronisasi parameter dari tombol UI sampai flag FFmpeg pada mode single maupun merged. |

---

## Indeks Panduan Domain Terstruktur
1. **[01-ingestion-ai-pipeline.md](./01-ingestion-ai-pipeline.md)**: Alur YouTube/Upload/GDrive -> Heatmap -> Transkrip -> AI Router 3-Way Framing & Open Loop.
2. **[02-ffmpeg-filtergraph-architecture.md](./02-ffmpeg-filtergraph-architecture.md)**: Peta rantai filtergraph video/audio, phase-safe mono, silence cutter, dan QA telemetry.
3. **[03-studio-wysiwyg-sync.md](./03-studio-wysiwyg-sync.md)**: Rumus skala pratinjau 320px vs 1080x1920, Safe Box TikTok/Shorts/Reels, dan persistensi `localStorage`.
4. **[04-render-settings-contract.md](./04-render-settings-contract.md)**: Matriks kontrak 5-titik seluruh parameter `RenderSettings`.
