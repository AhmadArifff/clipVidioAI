# AGENTS.md: ClipVidio AI Multi-Agent Orchestration & Governance System

> **Universal Agentic Entry File**: File ini dibaca secara otomatis pada setiap awal sesi percakapan di lingkungan Antigravity, Claude Code, Codex, dan Cursor untuk memastikan seluruh agen mematuhi arsitektur **ClipVidio AI (Python FastAPI + FFmpeg + React 19 Vite TypeScript)**, siklus OODA, tata kelola `.agents/` Standar V2, serta katalog 58 skill terdaftar.

---

## 1. Identitas Sistem (System Identity Card)

* **Proyek**: **ClipVidio AI** (`Clipper-Vidio-YT` Monorepo v3.9)
* **Stack Inti**:
  * **Backend API**: Python 3.10+ (`.venv`), FastAPI, Pydantic v2, Uvicorn (`apps/api/backend/`)
  * **Media & Video Engine**: FFmpeg 8.x + FFprobe, OpenCV (`YuNet` face detector), OpenAI Whisper, Pillow (`apps/api/backend/video_engine.py`, `silence_cutter_service.py`, `video_qa_service.py`)
  * **AI Router**: Gemini Multi-Key Rotation + OpenRouter Fallback (`apps/api/backend/services/ai_service.py`)
  * **Frontend Web Studio**: React 19, TypeScript, Vite (`apps/web/src/`)
  * **Shared Contracts**: `packages/shared/` & 5-Point RenderSettings Contract
* **Pusat Tata Kelola Lokal**: [`.agents/README.md`](./.agents/README.md)

---

## 2. Arsitektur & Filosofi Kerja (OODA Loop & Separation of Duty)

Sistem mengadopsi siklus **OODA (Observe -> Orient -> Decide -> Act)** dengan pemisahan peran antara **Builder** (`backend-engineer`, `frontend-engineer`, `multimedia-video-engineer`, `ai-engineer`) dan **Reviewer Independen** (`qa-engineer`, `security-engineer`, `tech-critic`) untuk mencegah halusinasi *self-review*.

### Aturan Operasional Mutlak (Hard Guardrails)
1. **Docs-First Retrieval & Self-Enrichment (Rule #29)**:
   * Sebelum mengubah kode pada fitur apa pun, agen **WAJIB** membaca terlebih dahulu berkas fitur di [`.agents/feature-docs/`](./.agents/feature-docs/README.md), [`.agents/knowledge/cross-feature-disambiguation.md`](./.agents/knowledge/cross-feature-disambiguation.md), dan [`.agents/knowledge/bug-cases.md`](./.agents/knowledge/bug-cases.md).
   * Setiap kali fitur baru selesai atau bug diselesaikan, agen **WAJIB** memperbarui `feature-docs/`, `bug-cases.md` (jika fix bug), dan [`.agents/02-session-state/active-session.json`](./.agents/02-session-state/active-session.json).
2. **FFmpeg Filtergraph Safety**:
   * Setiap stream pad output FFmpeg hanya boleh dikonsumsi **satu kali**. Jika dipakai oleh dua filter (misal `sidechaincompress` dan `amix`), **WAJIB** pecah dengan `asplit=2` atau `split=2`.
   * Audio wajib **phase-safe** sebelum mono summing, terkunci di **AAC 48 kHz stereo**, dan video master bertag **BT.709**, `yuv420p`, `+faststart`.
3. **5-Point RenderSettings Contract Sync**:
   * Setiap parameter studio baru wajib tersinkron di 5 titik sekaligus: `apps/web/src/types.ts` -> `apps/web/src/components/ClipStudioSection.tsx` -> `apps/web/src/App.tsx` -> `apps/api/backend/schemas/render.py` -> `apps/api/backend/services/render_service.py` (single & merged) + `video_engine.py`.
4. **Zero-Secret-Leak & Environment Isolation**:
   * Dilarang keras menaruh API Key (Gemini, OpenRouter, Supadata), proxy credentials, atau isi file `cookies.txt` di kode sumber, log, maupun commit Git.
5. **Anti-Slop Delivery Gate (R-01..R-38)**:
   * Bebas karakter em dash (R-02), bebas overflow horizontal di layar mobile (R-03), kontras WCAG AA >= 4.5:1 / 3:1 (R-25), komentar kode padat fungsional tanpa jargon AI internal, dan verifikasi otomatis via `qa-kernel.py` + `npm run build`.
6. **Circuit Breaker Pengerjaan Ulang**:
   * Jika sebuah task gagal verifikasi >= 3 kali berturut-turut, hentikan loop otomatis dan eskalasikan ke pengguna (*Human-in-the-Loop*).

---

## 3. Peta Direktori Tata Kelola `.agents/`

| Direktori / Berkas | Fungsi Utama |
| :--- | :--- |
| [`.agents/README.md`](./.agents/README.md) | Peta navigasi utama aturan, SOP, feature docs, dan skrip QA |
| [`.agents/rules/`](./.agents/rules/) | Aturan modular per area kerja (Core Guardrails, Workflow, FastAPI, FFmpeg Engine, Frontend WYSIWYG, Security) |
| [`.agents/feature-docs/`](./.agents/feature-docs/README.md) | Dokumentasi Standar V2 (10 Bagian) per modul fitur ClipVidio AI (SSOT) |
| [`.agents/knowledge/domain-reference/`](./.agents/knowledge/domain-reference/README.md) | 4 panduan arsitektur inti (Ingestion AI, FFmpeg Filtergraph, WYSIWYG Sync, RenderSettings Contract) |
| [`.agents/knowledge/cross-feature-disambiguation.md`](./.agents/knowledge/cross-feature-disambiguation.md) | Kamus anti-halusinasi pemisah fitur kembar (Single vs Merged vs WASM, PIP Sumber vs Reaction Cam, ASS vs PNG Title) |
| [`.agents/knowledge/bug-cases.md`](./.agents/knowledge/bug-cases.md) | Bank kasus bug produksi nyata ClipVidio AI & solusi pencegahannya |
| [`.agents/02-session-state/active-session.json`](./.agents/02-session-state/active-session.json) | Pelacak milestone terselesaikan, constraint terkunci, dan status sesi aktif |
| [`.agents/04-case-bank/index.json`](./.agents/04-case-bank/index.json) | Indeks Case-Bank YAML/MD terverifikasi untuk sinkronisasi Hub-and-Spoke |
| [`.agents/workflows/post-dev-qa.md`](./.agents/workflows/post-dev-qa.md) | SOP QA Pasca-Development Hemat Token (Tier 1 `qa-kernel.py` & Tier 2 Playwright On-Demand) |
| [`.agents/scripts/qa-kernel.py`](./.agents/scripts/qa-kernel.py) | Runner CLI Tier-1 verifikasi Python, Pydantic, FFmpeg render, Video QA, & TypeScript |
| [`.agents/scripts/sync-docs.js`](./.agents/scripts/sync-docs.js) | Skrip mirroring `feature-docs/` & 4 fondasi global ke portal dokumentasi SaaS `documentasi-projects` |

---

## 4. Katalog 58 Skill Terdaftar (Workspace `.agents/skills/` & Global `~/.gemini/config/skills/`)

Seluruh agen dapat mengaktifkan 58 skill secara *on-demand (progressive disclosure)*:

1. **Video Post-Production, Retention & Motion Suite (Prioritas Utama ClipVidio AI)**:
   * `herk-edit-kit`: Talking-head post-production (`cut-silences`, review-gated `cut-mistakes`, `short-form-edit` 9:16, `curiosity-and-entertainment` open loops, `quality-gates`).
   * `showtime`: Local offline video studio, standar `platforms.md` (safe zone 9:16, 48 kHz AAC, sidecar `.srt`, poster cover), dan aturan `showtime qa` (frame 0, loudness, speaker loudness >300 Hz, anti-caption-flash).
   * `reelmimic`: Analisis video referensi (`analyze.py`: phase-safe stereo check, `cropdetect`, UI strip crop), 6 engine 2D artistik, dan `music-to-video` beat-grid.
   * `motlab` & `motlab-assets`: Video-as-code `<canvas>`, `cut_pauses.py` dengan micro-fade 5 ms anti-klik, frame markup `selection.json`, dan asset kit reusable.
   * `motionmaxxing`: Senior motion art direction, timing curves terukur, dan `look.py` render inspection (contact sheet, cut strips, gates G0-G5).
   * `hyperframes`: Komposisi HTML+GSAP Studio, dynamic text fitting, dan video beats di atas talking-head.
   * `hypit`: Word-anchored SVML multi-variant viral cloning & UGC factories.
   * `openmotion`: Visual Timeline Studio Editor, `Motion.md` templates, dan Motion Package v0.2.
2. **Creative UI, Design Intelligence & Anti-Slop Suite**:
   * `frontend`, `shadcn-ui`, `21st-dev`, `react-bits`, `magic-ui`, `animate-ui`, `untitled-ui`, `motion`, `animejs`, `motion-design-skill`, `design-dna`, `paint`, `cast`, `_jutsu`.
   * `antislop`, `antislop-ui`, `antislop-copywriting`, `antislop-human`, `antislop-layoutmobile`, `antislop-code`.
3. **Core Engineering, Browser Automation, Architecture & Verification**:
   * `backend`, `pm`, `qa`, `playwright`, `playwright-skill`, `webbrain` (delegasi sesi browser login asli via MCP), `graphify`, `goal-tracker`, `tech-critic`, `agentic-ai`, `ml-vision`.
   * `archify`, `stack-diagram`, `habblaud`, `excel-export`.
4. **Interactive 3D / WebGL & Game Suite**:
   * `3d-configurator-simulator`, `teardown`, `diorama`, `ohmygame-studio`, serta 10 modul `threejs-*`.

---

## 5. Mandatory Delivery Gate (4-Blok PASS/FAIL)

Sebelum menyerahkan hasil pengembangan ke pengguna:
* **Block 1 (Hard Gate)**: Bebas em dash (R-02), bebas overflow mobile (R-03), kontras WCAG AA (R-25), 0 error TypeScript (`npm run build`), dan `qa-kernel.py` lulus.
* **Block 2 (Video & Audio Gate)**: Render FFmpeg bebas error filtergraph, audio 48 kHz phase-safe, frame 0 valid (tidak hitam), dan tidak ada regresi di jalur single maupun merged.
* **Block 3 (Contract & Disambiguation Gate)**: 5 titik kontrak `RenderSettings` selaras dan tidak mencampuradukkan fitur kembar.
* **Block 4 (Self-Enrichment Gate)**: `feature-docs/`, `bug-cases.md` (jika ada fix bug), dan `active-session.json` sudah diperbarui.
