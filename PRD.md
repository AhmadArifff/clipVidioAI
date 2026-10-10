# PRD: ClipVidio AI — Platform Architecture, Custom Background Engine & Monorepo Transformation

> **Dokumen Spesifikasi Produk (PRD)**  
> **Versi**: 2.0.0  
> **Status**: Approved for Development  
> **Owner**: Ahmad Arif / clipVidioAI Core Team  
> **Governance Engine**: Agentic AI Multi-Role System (.agents)

---

## 1. Executive Summary & Visi Produk

**ClipVidio AI** adalah platform open-source cerdas untuk memotong, menganalisis, dan memproduksi video pendek (*viral short-form clips*) dari YouTube, Google Drive, atau unggahan langsung secara otomatis. Platform ini mengintegrasikan kecerdasan buatan (Google Gemini Flash & OpenRouter Multi-Provider) dengan mesin pengolah video berkinerja tinggi berbasis FFmpeg.

### Latar Belakang Perubahan & Kebutuhan Utama
1. **Kebutuhan Custom Background Multi-Ratio**: Video pendek di platform seperti TikTok, YouTube Shorts, dan Instagram Reels sering kali menggunakan format vertikal 9:16 yang membutuhkan latar belakang menarik (misalnya gameplay loop Minecraft/Subway Surfers, tema aesthetic, atau branding khusus) di belakang video utama yang berukuran 16:9 atau 1:1. Saat ini aplikasi hanya mendukung latar belakang hitam atau ambient blur bawaan.
2. **Kebutuhan Arsitektur Monorepo**: Kode Frontend dan Backend saat ini bercampur di direktori *root*. Diperlukan pemisahan bersih (*Separation of Concerns*) berbasis Monorepo (`apps/web`, `apps/api`, dan `packages/shared`) untuk memudahkan skalabilitas, pemeliharaan dependensi, dan kerja tim.
3. **Penerapan Governance Session-State**: Memastikan seluruh siklus pengembangan terlacak secara persisten melalui `.agents/session-state.json` agar riwayat arsitektur, batasan (*constraints*), dan progres sub-tugas tidak hilang saat sesi berganti (*context drift prevention*).
4. **Transformasi UI/UX & Ikonografi Profesional**: Merombak antarmuka agar berstandar SaaS modern kelas atas (Obsidian/Zinc dark theme, tipografi presisi, micro-interactions halus) dan mengganti semua ikon dengan **Lucide React** yang seragam, bersih, dan mematuhi aturan Anti-Slop (tanpa em dash, WCAG AA contrast).

---

## 2. Fitur 1: Custom Background Multi-Ratio Engine

### 2.1 Spesifikasi Fungsional
Pengguna dapat memilih atau mengunggah latar belakang (*background*) untuk klip video dengan dukungan rasio aspek fleksibel:
* **Pilihan Aspek Rasio**:
  * `9:16` (Vertical / Shorts / TikTok / Reels)
  * `1:1` (Square / Instagram Feed)
  * `4:3` (Classic)
  * `16:9` (Landscape / YouTube Standard)
* **Kategori Background yang Didukung**:
  1. **Ambient Blur**: Menggunakan video asli yang di-blur secara dinamis dengan filter boxblur dan saturasi sinematik.
  2. **Solid Color & Gradients**: Pilihan warna solid gelap/terang atau gradien gradasi modern.
  3. **Curated Preset Loops**: Koleksi latar bawaan seperti gameplay loop (Minecraft Parkour, Subway Surfers, GTA Stunt), Motion Loops (Cyberpunk Neon Grid, Lo-Fi Room, Abstract Waves, Starfield).
  4. **Custom Upload**: Pengguna dapat mengunggah file media sendiri:
     * Format gambar: `.png`, `.jpg`, `.jpeg`, `.webp`
     * Format video looping: `.mp4`, `.webm`, `.mov`
* **Pengaturan Komposisi Video Utama (*Foreground Layout*)**:
  * **Scale Slider**: Menyesuaikan ukuran video utama (50% hingga 100% dari lebar canvas).
  * **Vertical Position**: Penempatan posisi vertikal (Top, Center, Bottom, atau slider koordinat Y).
  * **Frame Polish**: Opsi corner radius (sudut melengkung halus), drop shadow sinematik, dan border outline tipis agar video utama tampil kontras dan profesional di atas latar belakang.

### 2.2 Arsitektur Pipeline FFmpeg
Mesin video engine [backend/video_engine.py](file:///c:/Users/ASUS/Documents/Web%20Dev/improving/Clipper-Vidio-YT/backend/video_engine.py) akan diperluas untuk menerima input media latar:

```
[Input 0: Main Video] ──> [Crop/Scale/Border/Shadow] ──┐
                                                       ├─> [Overlay] ──> [Subtitles/Title] ──> [Final MP4]
[Input 1: Custom BG]  ──> [Loop/Scale to Canvas/Crop] ──┘
```

* **Formula Looping Video Background**: Menggunakan flag `-stream_loop -1` pada input latar video agar looping berjalan mulus sepanjang durasi klip utama.
* **Formula Filtergraph FFmpeg**:
  ```bash
  # Background scale & crop to target canvas (misal 1080x1920)
  [1:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)/2:(ih-1920)/2[bg_base];
  # Foreground scale & optional rounded/shadow
  [0:v]scale=w=1080*scale_val:h=-2[fg_main];
  # Composite overlay
  [bg_base][fg_main]overlay=(W-w)/2:y_pos[layout_base]
  ```

### 2.3 Kontrak API Backend (FastAPI)
* `POST /api/backgrounds/upload`: Endpoint Multipart upload file background (disimpan di `backend/storage/backgrounds/`).
* `GET /api/backgrounds/presets`: Mengambil daftar preset latar belakang bawaan sistem.
* `DELETE /api/backgrounds/{id}`: Menghapus background yang diunggah pengguna.
* Ekstensi pada `RenderSettingsModel`:
  * `background_type`: `"blur" | "solid" | "gradient" | "preset" | "custom_upload"`
  * `background_value`: URL / path file background / kode warna heksadesimal / nama preset
  * `foreground_scale`: Nilai float (0.50 s.d. 1.00)
  * `foreground_position_y`: Nilai persentase (0% s.d. 100%)
  * `foreground_border_radius`: Integer (0px s.d. 48px)
  * `foreground_shadow`: Boolean

---

## 3. Fitur 2: Restrukturisasi Monorepo

### 3.1 Struktur Direktori Sasaran

```
clipVidioAI/
├── apps/
│   ├── web/                     # Frontend Application (React 19 + Vite + TypeScript)
│   │   ├── src/
│   │   │   ├── components/      # UI Components (Modular & Refactored)
│   │   │   ├── hooks/           # Custom React Hooks
│   │   │   ├── services/        # API Client Services
│   │   │   ├── types/           # Local UI Types
│   │   │   └── App.tsx          # Root Layout Shell
│   │   ├── package.json
│   │   └── vite.config.ts
│   │
│   └── api/                     # Backend Application (FastAPI + Python .venv)
│       ├── routers/             # API Routers (clips, render, background, system)
│       ├── services/            # Core Services (render_service, ai_service, etc.)
│       ├── schemas/             # Pydantic Request/Response Models
│       ├── storage/             # Uploaded Media & Backgrounds Storage
│       ├── utils/               # Utilities (proxy, cookies, system)
│       ├── video_engine.py      # Core FFmpeg Video Processing Engine
│       ├── main.py              # FastAPI Application Entrypoint
│       └── requirements.txt
│
├── packages/
│   └── shared/                  # Shared Types & Constants
│       ├── src/
│       │   ├── constants/       # Ratio Presets, Background Presets, AI Models
│       │   └── types/           # Shared TypeScript interfaces
│       └── package.json
│
├── .agents/                     # Multi-Agent Governance & State
│   ├── session-state.json       # Single Source of Truth Session State
│   ├── skills/                  # Registered Specialized Skills
│   ├── rules/                   # Enterprise Guardrails
│   └── workflows/               # SOP & Workflows
│
├── scripts/                     # Unified Orchestration Scripts
│   ├── start-backend.js         # Intelligent Python backend detector & launcher
│   └── clean.js                 # Temporary storage cleaner
│
├── start.bat                    # One-Click Root Launcher (Windows Native)
├── package.json                 # Root Workspaces Configuration
├── tsconfig.json                # Project References Configuration
├── .env.example                 # Environment Variables Template
├── PRD.md                       # Master Product Requirements Document
└── README.md                    # Project Documentation
```

### 3.2 Strategi Migrasi Aman (*Zero Breaking Changes*)
1. Migrasi dilakukan tanpa merusak `start.bat` dan perintah `npm run dev`.
2. Menggunakan npm workspaces bawaan di `package.json` root:
   ```json
   "workspaces": [
     "apps/*",
     "packages/*"
   ]
   ```
3. Script `start-backend.js` dan konfigurasi Vite proxy tetap mengarah ke port 8000 dan 5173.

---

## 4. Fitur 3: Governance Session-State (.agents)

### 4.1 Spesifikasi Session-State
File `.agents/session-state.json` bertindak sebagai *Single Source of Truth* untuk memandu multi-agen Antigravity dan menghindari amnesia konteks pada sesi berkelanjutan:

* **Field Terikat**:
  * `session_id`: Pengidentifikasi unik sesi pengerjaan.
  * `primary_goal`: Sasaran utama proyek yang disepakati pengguna.
  * `current_stage`: Tahap pengerjaan aktif (`planning_and_prd`, `backend_dev`, `monorepo_migration`, `ui_redesign`, `qa_testing`, `done`).
  * `established_constraints`: Batasan permanen yang dikunci (No hardcoded secrets, Native Windows, Anti-slop, No docker).
  * `decomposed_subtasks`: Rincian sub-tugas atomik dengan peran pelaksana (`owner_role`), status (`pending`, `in_progress`, `done`), dependensi, dan riwayat ulasan tim penguji (`reviewed_by`).
  * `pruned_log`: Catatan kompresi konteks tanpa menghilangkan keputusan arsitektur.
  * `open_questions`: Daftar pertanyaan terbuka yang memerlukan konfirmasi pengguna (*Human-in-the-Loop*).

---

## 5. Fitur 4: Redesain UI/UX & Ikonografi Profesional

### 5.1 Standar Visual & Design DNA
* **Warna Tema (Dark Slate / Obsidian Universe)**:
  * Background Utama: `#09090b` (Deep Zinc)
  * Card / Surface Container: `#121215` dengan border halus `rgba(255, 255, 255, 0.08)`
  * Accent Primary: `#6366f1` (Indigo Neon) dan `#8b5cf6` (Electric Violet)
  * Text Colors: `#f8fafc` (Primary High Contrast), `#94a3b8` (Muted), `#64748b` (Subtle)
* **Ikonografi Terpadu**:
  * Mengintegrasikan pustaka **`lucide-react`** secara menyeluruh.
  * Menghapus semua karakter emoji non-standar dan inline SVG yang tidak konsisten pada antarmuka.
  * Ikon seragam dengan stroke `1.75px` dan ukuran proporsional (16px, 18px, 20px).

### 5.2 Kepatuhan Anti-Slop (Mandatory Delivery Gate)
* **Hard Gate**:
  * Bebas dari karakter em dash (R-02).
  * Bebas dari kebocoran layout horizontal pada perangkat mobile (R-03).
  * Kontras rasio warna memenuhi standar WCAG AA minimal 4.5:1 untuk teks normal dan 3:1 untuk teks tebal/komponen grafis (R-25).
  * Semua tombol memiliki affordance interaktif yang jelas dan feedback saat di-klik (R-26).
* **Live Interactive Studio Preview**:
  * Menampilkan pratinjau real-time kanvas vertikal 9:16 di browser.
  * Menggambarkan secara visual letak latar belakang, rasio klip utama, posisi teks judul, dan subtitle sebelum tombol render ditekan.

---

## 6. Fitur 5: High-Speed Render Engine & Real-Time Telemetry Streaming

### 6.1 Real-Time Download Progress Streaming (Anti-Stuck 15%)
* **Latar Belakang & Masalah**:
  Pada pipeline awal, proses `download_clip_segment` dijalankan menggunakan `subprocess.run()` secara blocking, sehingga UI frontend menahan status statis pada angka 15% ("⚡ Memotong (15%)") selama proses pengunduhan berlangsung (10-30 detik). Hal ini menciptakan impresi bahwa sistem mengalami *hang* atau *stuck*.
* **Solusi Arsitektur**:
  * Mengganti proses blocking dengan event stream parser dari `yt-dlp` (`--progress` / hook downloader) untuk menangkap persentase unduhan byte secara granular.
  * Mengirimkan data telemetri real-time via Server-Sent Events (SSE) `/api/render-progress/{batch_id}`:
    `15% -> 20% -> 28% -> 35% -> 40%`.
  * Menampilkan informasi transfer aktif di UI:
    `"⬇️ Mengunduh Segmen HD (28% · 4.2 MB/s · ETA: 6s)"`.

### 6.2 Smart Video Segment Caching (Anti-Redundant Download)
* **Mekanisme Caching**:
  * Menerapkan hashing cache pada folder `temp_downloads/` berbasis format:
    `cache_{video_id}_{start_time}_{end_time}.mp4`.
  * Jika klip dengan rentang waktu tersebut sudah pernah diunduh dan belum kedaluwarsa (*TTL 1 jam*), backend langsung melewati tahap unduh (0 detik) dan langsung masuk ke tahap compositing FFmpeg.

### 6.3 Single-Pass Master Stream Slicing (Batch Render Multi-Klip)
* **Optimasi Batch Rendering**:
  * Untuk batch $\ge$ 3 klip dari video YouTube yang sama, sistem mengunduh master stream satu kali (*Single-Pass*).
  * Pemotongan seluruh klip berikutnya dilakukan secara instan di komputer lokal menggunakan FFmpeg stream-copy (`ffmpeg -ss ... -to ... -c copy`), memangkas total waktu batch render hingga 60%-70%.

### 6.4 Hardware Acceleration Auto-Priority Pipeline
* **Penegakan Prioritas GPU**:
  * Sistem memprioritaskan encoder perangkat keras AMD AMF (`h264_amf`) dan NVIDIA NVENC (`h264_nvenc`) secara otomatis saat terdeteksi.
  * Menggunakan fallback cerdas ke CPU multi-threaded (`-preset veryfast -threads 0`) jika GPU sedang digunakan proses lain.

---

## 7. Milestones & Jadwal Implementasi

| Fase | Sub-Tugas / Deliverable | Output Artefak | Status |
|---|---|---|---|
| **Fase 1** | Inisialisasi Session-State & Dokumen PRD | `.agents/02-session-state/`, `PRD.md` | **Selesai (Verified Pass)** |
| **Fase 2** | Backend Engine: Custom Background API & FFmpeg Pipeline | `apps/api/backend/routers/backgrounds.py`, `video_engine.py` | **Selesai (Verified Pass)** |
| **Fase 3** | Restrukturisasi Arsitektur Monorepo | `apps/web/`, `apps/api/`, `packages/shared/`, root `package.json` | **Selesai (Verified Pass)** |
| **Fase 4** | Redesain UI/UX & Integrasi Ikonografi Lucide | `lucide-react`, `BackgroundCustomizer.tsx`, WYSIWYG Preview | **Selesai (Verified Pass)** |
| **Fase 5** | Refactor Vanilla CSS Background Customizer & Framing Preview Auto-Centering | `apps/web/src/index.css`, `BackgroundCustomizer.tsx`, `ClipStudioSection.tsx` (Auto Centering 4:3/1:1, Full-Bleed Backdrop) | **Selesai (Verified Pass)** |
| **Fase 6** | Pengujian Integrasi, Uji Render FFmpeg, & Delivery Gate Audit | Laporan QA, Verifikasi build 0-error, Launch test via `start.bat` | **Selesai (Verified Pass)** |
| **Fase 7** | High-Speed Render Engine & Real-Time Download Telemetry | `video_engine.py`, `render_service.py`, `ClipStudioSection.tsx` (SSE Progress Streaming, Smart Caching, Single-Pass Slicing) | **Selesai (Verified Pass)** |

---

## 8. Kriteria Penerimaan (Acceptance Criteria)

1. Pengguna dapat mengunggah gambar/video latar belakang atau memilih dari preset yang tersedia.
2. Klip video dapat di-render dengan latar belakang khusus pada rasio aspek 9:16, 1:1, 4:3, dan 16:9 tanpa distorsi visual.
3. Proyek tersusun dalam struktur Monorepo yang bersih dan perintah `start.bat` maupun `npm run dev` tetap berjalan lancar.
4. File `.agents/session-state.json` aktif melacak setiap langkah perubahan dan mempertahankan konsistensi sesi.
5. Tampilan aplikasi terlihat profesional, modern, bebas dari inkonsistensi ikon, dan mematuhi seluruh aturan Anti-Slop.
6. Progress rendering klip memberikan umpan balik persentase dan kecepatan transfer unduhan secara transparan tanpa angka statis 15% yang membingungkan.
