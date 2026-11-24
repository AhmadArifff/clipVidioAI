# Peta Tata Kelola & Aturan Kerja ClipVidio AI (`.agents` Rules & Docs Map)

Selamat datang di direktori tata kelola aturan, dokumentasi fitur, dan memori proyek **ClipVidio AI** (`Clipper-Vidio-YT`). Seluruh dokumen disusun secara modular mengadopsi Standar V2 agar hemat token, bebas halusinasi lintas-fitur, dan mudah dilacak antar-sesi.

> [!NOTE]
> Berkas auto-load utama di setiap sesi baru adalah [`AGENTS.md`](../AGENTS.md) di root workspace.

---

## 1. Aturan Mutlak (Selalu Aktif)
Setiap sesi pengembangan AI Agent **WAJIB** mematuhi dua dokumen inti ini:
* **[rules/00-core-guardrails.md](./rules/00-core-guardrails.md)**: Larangan keras (kebocoran API key/cookies, FFmpeg pad dipakai ganda tanpa `asplit`, bypass kontrak 5-titik `RenderSettings`, duplikasi logika antar jalur render, dan larangan otomasi browser tanpa izin).
* **[rules/01-workflow-discipline.md](./rules/01-workflow-discipline.md)**: Siklus OODA, Protokol **Docs-First Retrieval & Self-Enrichment (Rule #29)**, pembersihan berkas scratch/zombie code, higienitas komentar kode (bebas em dash & jargon AI internal), dan verifikasi wajib.

---

## 2. Peta Aturan Berdasarkan Area Kerja (*Task-Based Rules*)

| Jika Anda Sedang Mengerjakan... | Buka & Patuhi Dokumen: | Cakupan Utama |
| :--- | :--- | :--- |
| **Backend FastAPI, Routers & Services** (`apps/api/backend/routers/`, `services/`, `schemas/`) | **[rules/10-architecture.md](./rules/10-architecture.md)** | Pemisahan Router -> Schema (Pydantic) -> Service -> Engine, SSE progress streaming, error handling aman. |
| **FFmpeg, Subtitle ASS/SRT & Audio DSP** (`apps/api/backend/video_engine.py`, `silence_cutter_service.py`, `video_qa_service.py`) | **[rules/20-ffmpeg-video-engine.md](./rules/20-ffmpeg-video-engine.md)** | Aturan pad tunggal (`asplit`/`split`), phase-safe mono, 48 kHz stereo, BT.709, faststart, safe zone 9:16, dan fallback GPU -> CPU. |
| **Frontend React Studio & Live Preview** (`apps/web/src/components/`, `types.ts`, `locales/`) | **[rules/30-ui-frontend.md](./rules/30-ui-frontend.md)** | Paritas WYSIWYG Preview 320px vs Kanvas 1080x1920, Safe Zone Overlay, i18n (`id.ts` & `en.ts`), localStorage persistence, dan anti-overflow mobile. |
| **Keamanan API Keys, Cookies & Proxy** (`routers/cookies.py`, `services/ai_service.py`, `.env`) | **[rules/40-security-cookies-keys.md](./rules/40-security-cookies-keys.md)** | Isolasi `.env`, ephemeral cookies file cleanup, sanitasi path upload media, dan pencegahan GitHub Secret Scanning false-positive. |

---

## 3. Dokumentasi Fitur Standar V2 (*Feature Docs SSOT*)
Pusat dokumentasi 10-bagian per modul fitur (setara `menu-docs/` pada `adminShuttleV3`):
* **[feature-docs/README.md](./feature-docs/README.md)**: Indeks seluruh modul fitur ClipVidio AI dan status dokumentasinya.
* **[feature-docs/TEMPLATE-FEATURE-DOC.md](./feature-docs/TEMPLATE-FEATURE-DOC.md)**: Template baku 10 Bagian (Ringkasan Eksekutif, Mermaid & Call Chain, Kontrak Parameter, Logika Inti, Edge Cases, Smoke Test, Q&A, Changelog, Peta Alur UI Per-Kontrol, & Scope Guard).

---

## 4. Basis Pengetahuan, Disambiguasi & Bank Bug (*Knowledge Base*)
* **[knowledge/README.md](./knowledge/README.md)**: Tata kelola pengetahuan dan standar pencatatan bug baru.
* **[knowledge/cross-feature-disambiguation.md](./knowledge/cross-feature-disambiguation.md)**: **[CRITICAL]** Kamus Disambiguasi 6 Keluarga Fitur Kembar Anti-Halusinasi (Single vs Merged vs WASM, PIP Sumber vs Reaction Cam, ASS vs PNG Title, dll.).
* **[knowledge/domain-reference/README.md](./knowledge/domain-reference/README.md)**: 4 dokumen arsitektur inti ClipVidio AI.
* **[knowledge/bug-cases.md](./knowledge/bug-cases.md)**: Riwayat kasus bug produksi nyata ClipVidio AI dan pola pencegahannya.
* **[04-case-bank/index.json](./04-case-bank/index.json)**: Indeks Case-Bank terverifikasi untuk sinkronisasi ke Master Hub.

---

## 5. SOP & Alur Kerja (*Workflows*)
* **[workflows/task-review-protocol.md](./workflows/task-review-protocol.md)**: Evaluasi pra-development sebelum fitur besar.
* **[workflows/post-dev-qa.md](./workflows/post-dev-qa.md)**: SOP QA Pasca-Development Hemat Token (Tier 1 Fast Python/FFmpeg Kernel via `qa-kernel.py` + Tier 2 Playwright On-Demand).
* **[workflows/playwright-testing.md](./workflows/playwright-testing.md)**: Panduan pengujian visual browser Playwright saat diminta pengguna.
* **[workflows/anti-slop-verification.md](./workflows/anti-slop-verification.md)**: Daftar periksa kualitas visual dan copywriting.

---

## 6. Pelacak Status Sesi & Skrip Otomasi
* **[02-session-state/active-session.json](./02-session-state/active-session.json)**: Single Source of Truth milestone (`M1` s.d terbaru), tujuan aktif, dan batasan terkunci.
* **[scripts/qa-kernel.py](./scripts/qa-kernel.py)**: Runner QA otomatis Tier 1 (`.\.venv\Scripts\python.exe .agents\scripts\qa-kernel.py`).
* **[scripts/sync-docs.js](./scripts/sync-docs.js)**: Skrip mirroring `feature-docs/` + 4 dokumen fondasi global ke portal `documentasi-projects` (`node .agents/scripts/sync-docs.js`).
