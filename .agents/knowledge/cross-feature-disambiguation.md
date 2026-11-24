---
id: "cross-feature-disambiguation"
title: "Kamus Disambiguasi Fitur Kembar & Jalur Paralel ClipVidio AI (Anti-Halusinasi)"
project: "Clipper-Vidio-YT"
category: "00-arsitektur-dan-knowledge"
route: "N/A"
lead_developer: "ClipVidio AI Team"
status: "Active"
last_updated: "2026-11-24"
tags: ["disambiguasi", "render-pipeline", "pip", "title", "studio", "anti-halusinasi"]
---

# Kamus Disambiguasi Fitur Kembar & Jalur Paralel (`ClipVidio AI`)

> **Fungsi Dokumen (Ground-Truth Anti-Halusinasi)**: Di codebase `Clipper-Vidio-YT`, beberapa fitur memiliki nama atau tampilan mirip tetapi berada di jalur kode, endpoint, dan tanggung jawab yang **BERBEDA**. Bacalah tabel ini sebelum mengubah kode agar tidak salah jalur atau lupa menyinkronkan jalur kembarnya!

---

## 1. Keluarga Jalur Render Video (3 Jalur Berbeda)

| Jalur Render | Pemicu di Frontend | File Backend / Service | Catatan Penting (Jangan Terlewat!) |
| :--- | :--- | :--- | :--- |
| **1A. Server Batch Single Clip** (`renderMode = 'separate'`) | `App.tsx` -> `POST /api/render-batch` (`hardwareAccel !== 'browser_wasm'`) | `render_service.py::render_single_batch_clip()` -> `video_engine.py::render_clip_to_mp4()` | Setiap klip terpilih dirender menjadi 1 MP4 terpisah + `.srt` + `cover.jpg` + QA report. **Wajib** meneruskan semua field `RenderSettingsModel`. |
| **1B. Server Merged Compilation** (`renderMode = 'merged'`) | `App.tsx` -> `POST /api/render-batch` (`render_mode = 'merged'`) | `render_service.py::render_merged_batch_clips()` -> `video_engine.py::render_clip_to_mp4()` | Menggabungkan beberapa segmen klip dulu menjadi 1 raw MP4 lalu merender 1 kompilasi utuh. **WAJIB disinkronkan setiap kali ada argumen baru di `render_clip_to_mp4()`!** |
| **1C. Browser WASM Client Render** (`hardwareAccel = 'browser_wasm'`) | `App.tsx` -> `renderClientSideClip()` | `apps/web/src/services/clientRenderer.ts` (`@ffmpeg/ffmpeg`) | Berjalan 100% di browser tanpa membebani CPU server. Fitur berat server-side (YuNet face tracking, silence jumpcut, QA service) berjalan di jalur 1A/1B. |

---

## 2. Keluarga PIP Wajah (2 Konsep yang Sering Tertukar!)

| Fitur | Field Kontrak | Sumber Video Wajah | Fungsi & Tujuan |
| :--- | :--- | :--- | :--- |
| **2A. Streamer Facecam PIP** | `streamerPreset = 'pip_corner'` + `facecamPosition` | **Crop dari sudut video sumber** (misal webcam streamer gaming yang sudah ada di dalam video YouTube) | Memotong area webcam dari video gameplay 16:9 lalu menempatkannya ulang di sudut layar 9:16. |
| **2B. Custom Creator Reaction Cam PIP** | `reactionCamEnabled = true` + `reactionCamFilePath` + `reactionCamPosition/Size/Shape/BorderColor/MuteAudio` | **Upload video rekaman muka kreator sendiri** (`POST /api/reaction-cam/upload`) | Menempelkan wajah Anda sendiri (auto-loop, circle/rounded, muted default) untuk personal branding & perlindungan *Transformative Fair Use*. |

> [!WARNING]
> Jangan pernah menyatukan logika `streamerPreset === 'pip_corner'` dengan `reactionCamEnabled`. Keduanya independen dan bisa dipakai terpisah!

---

## 3. Keluarga Rendering Judul / Hook Title (2 Jalur Berbeda)

| Jalur Title | Kondisi Aktif | Fungsi Pembentuk | Dampak Filtergraph |
| :--- | :--- | :--- | :--- |
| **3A. ASS Subtitle Title** | `title_text` tidak mengandung emoji (`has_emoji(display_title) == False`) | `video_engine.py::generate_ass_file()` (`Style: TitleStyle`) | Dirender langsung lewat filter `subtitles=...ass` bersamaan dengan teks karaoke. |
| **3B. Color Emoji PNG Overlay** | `title_text` mengandung emoji (`has_emoji(display_title) == True`) | `video_engine.py::render_title_overlay_png()` (Pillow + font emoji warna) | `skip_ass_title = True`, lalu file PNG transparan ditumpuk lewat filter `overlay` agar warna emoji tidak rusak menjadi hitam-putih di libass. |

---

## 4. Keluarga Komponen UI Studio (Aktif vs Legacy)

| Komponen | Lokasi | Status |
| :--- | :--- | :--- |
| **`ClipStudioSection.tsx`** | `apps/web/src/components/ClipStudioSection.tsx` | **AKTIF (Utama)** dipakai oleh `App.tsx` sebagai studio utama pengeditan, live phone preview, dan peluncur render. |
| **`ClipStudioModal.tsx`** | `apps/web/src/components/ClipStudioModal.tsx` | **Legacy / Modal pembantu**. Jangan hanya mengedit modal ini tanpa memperbarui `ClipStudioSection.tsx`. |

---

## 5. Keluarga Sumber Transkrip & Timestamp Kata

| Sumber | Fungsi | Karakteristik |
| :--- | :--- | :--- |
| **5A. YouTube / Supadata / Manual SRT** | `youtube_service.py::fetch_transcript()` -> `video_engine.py::transcribe_clip_words()` | Cepat (tanpa download audio penuh), timestamp level kalimat lalu didistribusikan proporsional per karakter kata. |
| **5B. Local Whisper AI Fallback** | `video_engine.py::transcribe_local_video_file()` / `get_whisper_model()` | Aktif otomatis bila YouTube tidak menyediakan caption atau untuk file upload lokal/GDrive. Menggunakan model multilingual (`base`), dilarang memakai `.en` untuk video Bahasa Indonesia. |

---

## 6. Keluarga Pemangkasan Video (Manual Trimmer vs Auto Silence Jumpcut)

| Mekanisme | Lokasi | Kapan Bekerja |
| :--- | :--- | :--- |
| **6A. Clip Trimmer Manual** | `ClipTrimmerModal.tsx` (`start_time`, `end_time`) | Sebelum download segmen: menentukan titik awal & akhir potongan dari video sumber. |
| **6B. Auto-Trim Dead Air (Smart Jumpcut)** | `silence_cutter_service.py` (`silence_cut_mode`: `off` / `natural` / `snappy`) | Sesudah download segmen & transkripsi kata, tepat sebelum generate `.ass`/`.srt` & render final: memangkas jeda hening dengan nafas adaptif + 5 ms micro-fade lalu menggeser ulang (*re-time*) seluruh timestamp kata agar sinkron 100%. |
