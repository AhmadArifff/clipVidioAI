# PRD: ClipVidio AI - Platform Architecture, Multi-Provider AI Engine & High-Speed Media Pipeline

> **Dokumen Spesifikasi Produk (PRD)**  
> **Versi**: 2.6.0 (Bilingual Subtitle Intelligence & Anti-Delay Audio Sync Architecture)  
> **Status**: Approved for Development  
> **Owner**: Ahmad Arif / clipVidioAI Core Team  
> **Governance Engine**: Agentic AI Multi-Role System (.agents)

---

## 1. Executive Summary & Visi Produk

**ClipVidio AI** adalah platform open-source cerdas untuk memotong, menganalisis, dan memproduksi video pendek (*viral short-form clips*) dari YouTube, Google Drive, atau berkas lokal secara otomatis. Platform ini mengintegrasikan kecerdasan buatan multi-penyedia (Google Gemini Flash & OpenRouter) dengan mesin pengolah video berkinerja tinggi berbasis FFmpeg dan akselerasi perangkat keras kartu grafis (GPU).

Platform ini didesain untuk kreator konten, agensi media sosial, dan streamer yang ingin mengubah video panjang (podcast, webinar, gameplay, vod) menjadi klip vertikal siap tayang untuk TikTok, YouTube Shorts, dan Instagram Reels dalam hitungan detik.

---

## 2. Arsitektur Sistem Terintegrasi

Sistem mengadopsi pola arsitektur **Monorepo Hybrid (TypeScript + Python)** dengan pemisahan peran yang tegas antara antarmuka web, backend pemrosesan media, dan kontrak tipe bersama:

```
clipVidioAI/
├── apps/
│   ├── web/                     # Frontend Application (React 19 + Vite + TypeScript)
│   │   ├── src/
│   │   │   ├── components/      # UI Studio, Trimmer, Batch Progress, Backgrounds
│   │   │   ├── locales/         # Bilingual i18n Dictionary (id.ts, en.ts)
│   │   │   ├── utils/           # Resilient API Client, Helper Functions
│   │   │   ├── types.ts         # Local UI Type Definitions
│   │   │   └── App.tsx          # Master Shell & Workflow Controller
│   │   ├── vite.config.ts       # Vite Dev Server with Graceful Proxy Interceptor
│   │   └── package.json
│   │
│   └── api/                     # Backend API & Media Processing (FastAPI + Python 3.10+)
│       └── backend/
│           ├── routers/         # API Controllers (analyze, clips, render, backgrounds, system)
│           ├── services/        # Business Logic (render_service, ai_service, youtube_service)
│           ├── schemas/         # Pydantic Contracts (analyze, render, backgrounds)
│           ├── utils/           # Proxy rotator, cookies parser, system path safety
│           ├── video_engine.py  # Core FFmpeg Compositor & Hardware Acceleration
│           ├── config.py        # Centralized Environment & Directory Configuration
│           └── main.py          # FastAPI Entrypoint & Static Files Mounter
│
├── packages/
│   └── shared/                  # Shared Contracts & Domain Constants
│       └── src/
│           ├── constants/       # Ratio presets, AI model registries
│           └── index.ts         # Exported domain types
│
├── .agents/                     # Multi-Agent Governance & State Engine
│   ├── session-state.json       # Persistent Single Source of Truth
│   ├── 04-case-bank/            # Verified Production Incident & Solution Bank
│   ├── rules/                   # Enterprise Guardrails
│   └── workflows/               # Standard Operating Procedures
│
├── .env.example                 # Environment Variables Reference
├── start.bat                    # One-Click Root Windows Launcher
└── PRD.md                       # Master Product Requirements Document
```

---

## 3. Modul Utama & Spesifikasi Fungsional

### 3.1 Modul 1: Multi-Provider AI Engine (Enterprise AI Router)

Modul ini bertanggung jawab menganalisis transkrip dialog dari video YouTube/lokal untuk mendeteksi momen bernilai tinggi (*high-retention highlights*).

* **Penyedia AI yang Didukung**:
  1. **Google Gemini (Default)**:
     * Model: `gemini-2.5-flash`, `gemini-2.5-flash-lite`, `gemini-2.0-flash`, `gemini-1.5-flash`, `gemini-2.5-pro`.
     * **Dynamic Multi-Key Rotation**: Menerima daftar API key via `GEMINI_API_KEYS=key1,key2,key3`. Jika satu key terkena limit kuota HTTP 429, router otomatis berpindah ke key cadangan secara transparan.
  2. **OpenRouter (Multi-Model Agregator)**:
     * Model: `deepseek/deepseek-chat` (DeepSeek V3), `deepseek/deepseek-r1`, `meta-llama/llama-3.3-70b-instruct`, `anthropic/claude-3.5-sonnet`, `openai/gpt-4o-mini`.
     * Mengambil model aktif langsung dari registry OpenRouter via endpoint remote.
     * Penanganan error terstruktur untuk status 402 (*insufficient credits*) dan 429 (*rate limit*).
* **Ekstraksi Hasil Analisis**:
  * Judul klip viral yang memancing rasa penasaran (*hook-driven*).
  * Skor viralitas (0 - 100) dan alasan kurasi konten.
  * Timestamp mulai (`start_time`) dan selesai (`end_time`).
  * Ringkasan isi klip.

---

### 3.2 Modul 2: YouTube Anti-Bot & Network Resiliency

YouTube secara berkala memperbarui proteksi anti-bot yang dapat memblokir IP server atau memunculkan halaman bot. Modul ini menjamin unduhan transkrip dan video tetap berjalan 100%:

* **Supadata Cloud Residential Fallback**:
  * Ketika ekstraksi transkrip langsung lokal diblokir oleh YouTube (*IpBlocked* / *RequestBlocked*), sistem otomatis mengalihkan request ke Supadata API (`SUPADATA_API_KEYS`).
  * Menggunakan jaringan IP residential global untuk mengunduh subtitle berformat JSON secara instan.
* **Webshare Rotating Proxy Integration**:
  * Konfigurasi proxy berputar datacenter/residential (`WEBSHARE_USERNAME`, `WEBSHARE_PASSWORD`, `WEBSHARE_LOCATIONS`).
  * Digunakan oleh `yt-dlp` saat mengunduh potongan segmen video dari YouTube jika terjadi pembatasan IP.
* **Handshake Heartbeat & Netscape Cookies Sync**:
  * Menyimpan dan memvalidasi `cookies.txt` akun YouTube.
  * Mengisolasi file cookie ke format Netscape yang valid secara efemeral untuk menghindari deteksi bot dan memastikan unduhan 1080p/4K tanpa batasan usia (*age-restricted*).
* **Multi-Client Emulation**:
  * `yt-dlp` dikonfigurasi dengan extractor visionOS, iOS, dan Android client untuk menjaga stabilitas unduhan.

---

### 3.3 Modul 3: GPU Hardware Acceleration & Video Engine

Mesin video di [apps/api/backend/video_engine.py](file:///c:/Users/ASUS/Documents/Web%20Dev/improving/Clipper-Vidio-YT/apps/api/backend/video_engine.py) dirancang untuk memproses compositing video resolusi tinggi dengan kecepatan maksimal:

* **Encoder yang Didukung & Prioritas Otomatis**:
  1. **AMD AMF (`h264_amf`)**: Dioptimalkan dengan argumen `-quality speed -rc cbr -b:v 6M`. Teruji mencapai kecepatan benchmark **2.86x real-time** pada GPU AMD Radeon.
  2. **NVIDIA NVENC (`h264_nvenc`)**: Dioptimalkan dengan argumen `-preset p4 -cq 23`.
  3. **Intel QuickSync (`h264_qsv`)**: Dioptimalkan dengan `-preset veryfast`.
  4. **CPU Software Fallback (`libx264`)**: Dioptimalkan dengan multi-threading `-preset veryfast -crf 22`. Aktif otomatis jika hardware encoder gagal atau sibuk.
* **Indikator Visual di Antarmuka Studio**:
  * Banner status dinamis di antarmuka Studio yang menampilkan status GPU aktif (misal `⚡ AMD Radeon AMF Terdeteksi & Aktif`).
  * Dropdown encoder otomatis mendeteksi hardware yang didukung dan menonaktifkan opsi yang tidak tersedia di PC pengguna.

---

### 3.4 Modul 4: Custom Background & Multi-Ratio Layout Engine

Memungkinkan pengguna mengubah video 16:9 atau 1:1 menjadi format vertikal 9:16 (Shorts/TikTok/Reels) dengan latar belakang yang menarik:

* **Dukungan Rasio Aspek**:
  * `9:16` (Vertical Full-bleed / Shorts / TikTok / Reels)
  * `1:1` (Square / Instagram Feed)
  * `4:3` (Classic TV / Podcasting)
  * `16:9` (Landscape / YouTube Standard)
* **Kategori Background**:
  * **Ambient Blur**: Mengambil video utama, memperbesar, dan mem-blur dengan filter boxblur sinematik.
  * **Solid Color & Gradients**: Latar belakang warna solid atau gradasi warna modern.
  * **Curated Video Loops**: Latar video gameplay looping (Minecraft Parkour, Subway Surfers, GTA Stunt) atau motion graphic (Cyberpunk Grid, Lo-Fi Room, Abstract Waves).
  * **Custom Upload**: Unggah file gambar (`.png`, `.jpg`, `.webp`) atau video looping (`.mp4`, `.webm`, `.mov`).
* **Kontrol Komposisi Video Utama (Foreground)**:
  * Scale slider (50% hingga 100%).
  * Posisi vertikal (Top, Center, Bottom, atau slider koordinat Y bebas).
  * Rounded border radius (0px s.d. 48px) dan drop shadow sinematik.

---

### 3.5 Modul 5: Tipografi, Subtitle ASS & Watermark Branding

* **Generator Subtitle Berbasis Kata (*Karaoke ASS*)**:
  * Mengonversi transkrip timestamp kata (*word-level timing*) menjadi file subtitle Advanced SubStation Alpha (`.ass`).
  * Gaya subtitle: Bold Yellow, White Clean, Neon Green, Red Punch, Retro Gradient.
  * Posisi teks dapat diatur (bawah, tengah, atas, atau drag-and-drop).
* **Pipeline Font Dinamis**:
  * Backend melayani endpoint `/api/fonts` dan `/api/font-file/{font_name}`.
  * Font dimuat secara asinkron di browser via `FontFace` API dengan proteksi URI encoding (`encodeURI`) agar nama font berspasi (misal *Bebas Neue*, *Outfit*, *Komika Axis*) tidak memicu error sintaks.
  * Dukungan render emoji berwarna (🔥, 🚀, 😱) menggunakan font emoji warna lokal atau jalur kustom `EMOJI_FONT_PATH`.
* **Watermark Branding**:
  * Watermark gambar (logo PNG) atau teks kustom.
  * Pengaturan posisi bebas (drag preview atau slider persentase X/Y), ukuran, dan tingkat transparansi (*opacity*).

---

### 3.6 Modul 6: Audio Compositing (BGM & Hook SFX)

* **Background Music (BGM)**:
  * Pengguna dapat memilih BGM instrumental atau mengunggah audio sendiri.
  * Pengaturan volume independen (0% s.d. 100%) dan start offset audio.
* **Hook Sound Effect (SFX)**:
  * Efek suara kejutan (*whoosh*, *impact*, *bell*, *glitch*) yang diputar persis pada frame 0 (awal klip) untuk meningkatkan retensi penonton.
* **Mixer Audio FFmpeg**:
  * Menggabungkan audio asli video, BGM, dan Hook SFX menggunakan filter `amix=inputs=3:duration=first:dropout_transition=2`.

---

### 3.7 Modul 7: Telemetri Render Real-Time & Caching Cerdas

* **Server-Sent Events (SSE) Progress Streaming**:
  * Menghilangkan fenomena status macet di 15% pada versi lawas.
  * Frontend berlangganan ke `/api/render-progress/{batch_id}` yang mengirimkan status bertahap:
    * `15%`: Menyiapkan unduhan segmen.
    * `20% - 40%`: Mengunduh segmen video dengan informasi ukuran dan estimasi waktu (*live download ETA*).
    * `45% - 65%`: Pemotongan dan ekstraksi audio.
    * `70% - 95%`: Compositing dan encoding FFmpeg GPU (dengan pembacaan telemetri `time=...` dan `speed=...`).
    * `100%`: Berkas MP4 selesai dan tautan unduhan ZIP siap.
* **Smart Segment Caching**:
  * Berkas unduhan disimpan dalam cache berbasis hash `cache_{video_id}_{start}_{end}.mp4`.
  * Verifikasi integritas kontainer MP4 (`is_valid_mp4`) memastikan cache tidak menyimpan berkas audio-only atau berkas yang korup.
* **Multi-Segment Merged Compilation Mode**:
  * Opsi menggabungkan seluruh klip highlight yang dipilih menjadi 1 berkas video panjang berurutan (*compilation video*) lengkap dengan transisi dan penyesuaian offset waktu subtitle.

---

### 3.8 Modul 8: Resiliensi Startup & Keamanan Lingkungan

* **Graceful Vite Proxy Startup Interceptor**:
  * Proxy Vite di `apps/web/vite.config.ts` menangani error `ECONNREFUSED` secara senyap saat backend FastAPI masih dalam detik-detik pertama proses booting.
  * Fungsi `resilientFetch` di frontend secara otomatis melakukan percobaan ulang (*exponential backoff retry*), sehingga tidak ada pesan error merah di terminal.
* **Server Environment Isolation**:
  * Fungsi `is_server_environment()` mendeteksi apakah aplikasi berjalan di Docker, Dokploy, Vercel, atau VPS.
  * Fitur berbahaya seperti restart server dan pembaruan mandiri melalui antarmuka web dinonaktifkan secara otomatis pada lingkungan produksi server demi keamanan.

---

## 4. Matriks Spesifikasi Endpoint API (FastAPI)

| Metode | Endpoint | Deskripsi |
|---|---|---|
| `POST` | `/api/analyze-youtube` | Streaming SSE analisis klip video dengan AI (Gemini / OpenRouter) |
| `GET` | `/api/models` | Mengambil daftar model AI aktif dari Gemini atau OpenRouter |
| `GET` | `/api/hardware-accel` | Mengambil status deteksi akselerasi GPU (AMF, NVENC, QSV, CPU) |
| `POST` | `/api/render-batch` | Mendaftarkan antrean batch render video (terpisah atau kompilasi) |
| `GET` | `/api/render-progress/{id}` | Mengambil status dan telemetri persentase render secara berkala |
| `POST` | `/api/render-batch/{id}/retry` | Mencoba ulang klip tertentu yang gagal pada suatu batch |
| `GET` | `/api/download-rendered/{file}` | Mengunduh berkas video MP4 hasil render |
| `GET` | `/api/download-batch-zip/{id}` | Mengunduh seluruh video dalam satu berkas arsip ZIP |
| `GET` | `/api/fonts` | Mengambil daftar font tipografi yang terpasang |
| `GET` | `/api/font-file/{name}` | Mengunduh berkas biner font untuk pratinjau browser |
| `GET` | `/api/backgrounds/presets` | Mengambil koleksi preset background bawaan |
| `POST` | `/api/backgrounds/upload` | Mengunggah gambar atau video background kustom |
| `GET` | `/api/backgrounds/file/{name}` | Melayani berkas media background statis |
| `GET` | `/api/cookies` | Memeriksa ketersediaan dan status validitas cookie YouTube |
| `POST` | `/api/cookies/upload` | Mengunggah atau memperbarui berkas `cookies.txt` |
| `GET` | `/api/system/version` | Mengambil informasi versi aplikasi dan status update Git |

---

## 5. Ringkasan Variabel Lingkungan (.env)

| Variabel | Sifat | Kegunaan |
|---|---|---|
| `GEMINI_API_KEY` | Wajib (atau OpenRouter) | Kunci API utama Google Gemini AI |
| `GEMINI_API_KEYS` | Opsional | Kunci cadangan Gemini untuk rotasi otomatis kuota 429 |
| `OPENROUTER_API_KEY` | Opsional | Kunci API OpenRouter untuk model alternatif (DeepSeek, LLaMA, dll) |
| `SUPADATA_API_KEYS` | Opsional | Proxy transkrip YouTube cloud saat IP lokal diblokir |
| `WEBSHARE_USERNAME` | Opsional | Kredensial proxy berputar Webshare untuk unduhan video |
| `WEBSHARE_PASSWORD` | Opsional | Token sandi proxy Webshare |
| `WEBSHARE_LOCATIONS` | Opsional | Lokasi server proxy Webshare (misal `US,GB,DE`) |
| `PROXY_URL` | Opsional | URL proxy mandiri kustom (`http://user:pass@host:port`) |
| `EMOJI_FONT_PATH` | Opsional | Jalur berkas font emoji berwarna (.ttf / .otf) |
| `REQUESTS_CA_BUNDLE` | Opsional | Jalur sertifikat SSL custom jika berada di balik firewall inspeksi |
| `SERVER_MODE` | Opsional | Mode server produksi (mengunci fungsi self-update UI) |

---

## 6. Riwayat Milestone & Log Pembaruan Sistem

| Versi | Tanggal | Milestone / Pembaruan Utama | Status |
|---|---|---|---|
| **v1.0.0** | Awal 2026 | Rilis awal Clipper Video YouTube dasar berbasis Streamlit/Script lokal | Selesai |
| **v1.5.0** | Pertengahan 2026 | Migrasi ke FastAPI + React SPA dan pengenalan subtitle ASS karaoke | Selesai |
| **v2.0.0** | Oktober 2026 | Restrukturisasi Monorepo Hybrid (`apps/web`, `apps/api`, `packages/shared`), Custom Background Multi-Ratio, Framing Preview, dan Ikonografi Lucide | Selesai (Verified Pass) |
| **v2.2.0** | Oktober 2026 | Real-Time Download Streaming SSE (Anti-Stuck 15%), Smart Caching Segmen Video, dan Single-Pass Batch Slicing | Selesai (Verified Pass) |
| **v2.3.0** | Oktober 2026 | Pemulihan integrasi bypass YouTube: Supadata Residential Fallback, Webshare Proxying, Netscape Cookies sync, dan VisionOS emulation | Selesai (Verified Pass) |
| **v2.4.0** | Oktober 2026 | Enterprise AI Router Multi-Provider: Integrasi OpenRouter (DeepSeek V3/R1) berdampingan dengan Google Gemini Multi-Key Rotation | Selesai (Verified Pass) |
| **v2.5.0** | Oktober 2026 | GPU Hardware Acceleration (AMD AMF benchmark 2.86x real-time), Card Status GPU Studio, Peredaman Log Proxy Startup, dan Perbaikan FontFace encoding | Selesai (Verified Pass) |
| **v2.6.0** | Oktober 2026 | Bilingual Subtitle Intelligence (Fokus Indonesian & English), Kalibrasi Audio-Text Offset Slider, dan Eliminasi Bentrok Subtitle Ganda | Selesai (Verified Pass) |

---

## 7. Kriteria Kualitas & Governance (Anti-Slop & Quality Gate)

Seluruh pembaruan di masa mendatang wajib mematuhi standar kualitas berikut:

1. **Hard Gate (Mutlak)**:
   * Bebas dari karakter em dash (`-` biasa atau titik dua digunakan sebagai pengganti).
   * Bebas dari kebocoran layout horizontal (*zero horizontal scrollbar leak*) pada semua resolusi layar.
   * Kontras rasio warna memenuhi standar aksesibilitas WCAG AA minimal 4.5:1 untuk teks normal dan 3:1 untuk elemen UI.
   * Tidak ada tautan atau tombol mati tanpa umpan balik interaktif.
2. **Resiliensi Media**:
   * Setiap berkas MP4 hasil unduhan maupun hasil render wajib divalidasi dengan `is_valid_mp4(..., require_video=True)` sebelum dianggap sukses.
   * Jika hardware encoder GPU gagal atau kehabisan alokasi memori VRAM, proses render wajib melakukan *graceful fallback* ke encoder CPU (`libx264`) secara otomatis tanpa menggagalkan tugas pengguna.
3. **Session Consistency**:
   * Setiap perubahan arsitektur atau keputusan fitur baru wajib dicatat dan diselaraskan pada dokumen PRD ini dan `.agents/session-state.json`.

---

## 8. Fitur 6: Bilingual Subtitle Intelligence (Indonesian & English Focus) & Audio-Text Synchronization Engine

### 8.1 Latar Belakang & Analisis Masalah
Berdasarkan investigasi pada kasus video dokumenter (misal insiden Moby Dick `Si0IAa-fgTA`):
1. **Penyebab Terjadinya 2 Subtitle Bertumpuk**:
   * **Subtitle 1 (Putih kecil di bar hitam)**: Berasal langsung dari piksel video asli YouTube (*hardsub* yang sudah dibakar oleh pembuat video asli ke dalam gambar).
   * **Subtitle 2 (Besar tebal dengan warna viral)**: Merupakan subtitle hasil generate filter FFmpeg (`.ass`) buatan ClipVidio AI.
   * Jika video sumber sudah memiliki hardsub bawaan, penambahan subtitle ASS di atasnya menciptakan benturan visual ganda (*cluttered overlapping text*).
2. **Penyebab Muncul Bahasa Inggris padahal Diinginkan Bahasa Indonesia**:
   * Video asli bersumber dari channel berbahasa Inggris yang kemudian di-dubbing atau diberi subtitle Indonesia.
   * Pipeline `prioritize_transcripts()` sebelumnya otomatis memprioritaskan bahasa lisan asli ASR YouTube (`native_asr_lang`), sehingga selalu menarik track bahasa Inggris (`en`) tanpa memberikan kebebasan bagi pengguna untuk memilih Bahasa Indonesia (`id`).
3. **Penyebab Delay Antara Dubbing Suara dan Teks Subtitle**:
   * **Perbedaan Durasi Bahasa**: Waktu pelafalan narasi dubbing Indonesia memiliki panjang suku kata dan ritme bicara berbeda dari teks transkrip bahasa Inggris.
   * **Segmentasi Blok YouTube**: Transkrip YouTube ASR sering kali memberikan rentang waktu per frasa panjang (3-5 detik) alih-alih per kata presisi, menghasilkan jeda (200ms - 500ms) saat kata dianimasikan satu per satu.

### 8.2 Spesifikasi Fungsional: Bilingual Subtitle Selector
* **Pilihan Bahasa Eksklusif (Fokus 2 Bahasa)**:
  Antarmuka Input & Studio menyediakan pemilih bahasa subtitle yang tegas dan intuitif:
  1. `🇮🇩 Bahasa Indonesia (id)` (Default untuk pengguna di Indonesia)
  2. `🇺🇸 English (en)` (Untuk konten global / internasional)
* **Logika Prioritas Pengambilan Transkrip Backend (`youtube_service.py`)**:
  * Ketika pengguna memilih `id`:
    1. Cari track manual Bahasa Indonesia (`id`, `id-ID`).
    2. Cari track auto-generated ASR Bahasa Indonesia.
    3. Cari track terjemahan otomatis ke Bahasa Indonesia (`t.translate('id')`).
    4. Fallback ke bahasa Inggris jika Bahasa Indonesia tidak tersedia sama sekali.
  * Ketika pengguna memilih `en`:
    1. Cari track manual English (`en`, `en-US`, `en-GB`).
    2. Cari track auto-generated ASR English.
    3. Cari track terjemahan otomatis ke English (`t.translate('en')`).

### 8.3 Anti-Delay & Audio-Text Synchronization Calibration
Untuk memastikan teks subtitle beriringan secara presisi dengan suara dubbing narator:
* **Slider Offset Kalibrasi Waktu (*Subtitle Timing Shift*)**:
  * Menambahkan slider presisi di antarmuka Studio:
    `Offset Sinkronisasi Subtitle: [-1000ms s.d. +1000ms]` (Step: 50ms, Default: `0ms`).
  * Jika suara dubbing terasa lebih cepat daripada teks, pengguna cukup menggeser slider ke kiri (misal `-250ms`).
  * Jika teks muncul mendahului suara dubbing, pengguna menggeser slider ke kanan (misal `+200ms`).
* **Kalkulasi Offset pada Generator ASS (`video_engine.py`)**:
  ```python
  offset_sec = float(subtitle_timing_offset_ms or 0) / 1000.0
  adjusted_start = max(0.0, word_start + offset_sec)
  adjusted_end = max(adjusted_start + 0.05, word_end + offset_sec)
  ```
* **Opsi "Tanpa Subtitle (None)" untuk Video yang Sudah Punya Hardsub**:
  * Jika video sumber terdeteksi sudah memiliki subtitle permanen di dalam gambar seperti pada video Moby Dick, pengguna dapat langsung mengklik opsi `Gaya Subtitle: None` agar ClipVidio AI tidak menimpa subtitle kedua, menghasilkan video yang bersih dan rapi.

