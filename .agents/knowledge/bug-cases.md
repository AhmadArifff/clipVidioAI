---
id: "production-bug-cases"
title: "Daftar Kasus Bug & Solusi Terverifikasi ClipVidio AI (Bug Knowledge Bank)"
project: "Clipper-Vidio-YT"
category: "00-arsitektur-dan-knowledge"
route: "N/A"
lead_developer: "ClipVidio AI Team"
status: "Active"
last_updated: "2026-11-24"
tags: ["bug-cases", "ffmpeg", "filtergraph", "audio", "reaction-cam", "subtitles", "yt-dlp"]
---

# Riwayat Kasus Bug & Solusi Terverifikasi (`ClipVidio AI`)

Dokumen ini mencatat riwayat kendala teknis nyata yang pernah terjadi di **ClipVidio AI** (`Clipper-Vidio-YT`) beserta akar masalah dan solusi permanennya agar tidak pernah terulang.

---

### Kasus #01: FFmpeg Filtergraph Error `Stream specifier 'v_orig_boosted' matches no streams`
* **Kategori**: FFmpeg Filtergraph / Audio Smart Ducking
* **Gejala (Symptom)**:
  Saat fitur BGM + Smart Auto-Ducking + Vocal Isolation aktif bersamaan, proses render FFmpeg langsung gagal dengan error `Stream specifier 'v_orig_boosted' in filtergraph description ... matches no streams`.
* **Akar Masalah (Root Cause)**:
  Output pad audio `[v_orig_boosted]` dikonsumsi dua kali di filtergraph yang sama (satu kali sebagai referensi sidechain di `sidechaincompress`, satu kali lagi sebagai input campuran di `amix`). Di FFmpeg, setiap labeled pad hanya bisa dikonsumsi tepat 1 kali.
* **Solusi (Fix Applied)**:
  Di `apps/api/backend/video_engine.py`: tambahkan `asplit=2[v_voice_mix][v_voice_sidechain]` ketika `bgm_enabled` dan `smart_ducking_enabled` aktif. Cabang `[v_voice_sidechain]` masuk ke `sidechaincompress`, sedangkan `[v_voice_mix]` masuk ke `amix`.
* **Pelajaran (Takeaway)**:
  Setiap kali satu stream video/audio dipakai oleh lebih dari satu filter, WAJIB pecah memakai `split=2` atau `asplit=2`.

---

### Kasus #02: Video & Subtitle Bertumpuk Ganda pada Detik 0-3 (Duplicate Hook Zoom Overlay)
* **Kategori**: FFmpeg Filtergraph / Hook Zoom
* **Gejala (Symptom)**:
  Pada detik 0 sampai 3 hasil render MP4, muncul dua video bertumpuk (video kotak 1080x1080 di sudut kiri atas menimpa kanvas 9:16 lengkap dengan subtitle ganda), lalu di detik ke-3 video kembali normal.
* **Akar Masalah (Root Cause)**:
  Terdapat dua blok Hook Zoom di `video_engine.py`: blok pertama sudah benar (`trim` 0-2.5s + `scale=1188:2112` + `concat`), namun masih tertinggal blok lama kedua yang melakukan `scale=1232:1232,crop=1080:1080` lalu menempelkannya dengan `overlay=0:0:enable='lte(t,3.0)'`.
* **Solusi (Fix Applied)**:
  Hapus total blok duplikat kedua di `video_engine.py` sehingga hanya ada satu jalur Hook Zoom yang bersih.
* **Pelajaran (Takeaway)**:
  Selalu audit urutan filtergraph secara menyeluruh dan jalankan uji render frame detik `0.5s` vs `4.0s` setiap kali memodifikasi efek transisi/zoom.

---

### Kasus #03: Inverted Stereo Phase Menghilangkan Suara Vokal pada `center_vocal_extract`
* **Kategori**: Audio DSP / Anti-Content ID Shield
* **Gejala (Symptom)**:
  Pada sumber video podcast atau rekaman mikrofon wireless tertentu yang kanal stereo L dan R-nya memiliki fase terbalik (*inverted phase*), mode default `center_vocal_extract` (`pan=stereo|c0=0.5*c0+0.5*c1|c1=0.5*c0+0.5*c1`) menyebabkan suara pembicara saling meniadakan hingga sangat pelan atau hening total.
* **Akar Masalah (Root Cause)**:
  Penjumlahan mentah `0.5*L + 0.5*R` mengasumsikan kedua kanal sefase (*in-phase*). Jika `R = -L`, maka `L + R = 0`.
* **Solusi (Fix Applied)**:
  Di `apps/api/backend/video_engine.py`: implementasikan helper `detect_safe_mono_pan(video_path)` (mengadopsi pelajaran `reelmimic/analyze.py`) yang mengukur mean volume dB dari L, R, dan L+R via FFmpeg `volumedetect`. Jika `L+R` turun > 6 dB dibanding kanal terkuat, sistem otomatis memilih kanal tunggal terkuat (`c0=c0|c1=c0` atau `c0=c1|c1=c1`).
* **Pelajaran (Takeaway)**:
  Jangan pernah melakukan summing stereo ke mono tanpa verifikasi fase terlebih dahulu.

---

### Kasus #04: Reaction Cam PIP Tertutup Tombol UI TikTok/Shorts di Pojok Bawah Kanan
* **Kategori**: Layout Safe Zone 9:16 (1080x1920)
* **Gejala (Symptom)**:
  Pada mode `reaction_cam_position="bottom_right"`, margin awal `m_x=36` dan `m_y_bottom=220` menempatkan sebagian bingkai wajah kreator di area tombol Like/Comment/Share (kanan 164 px) dan deskripsi video (bawah 400-480 px) pada aplikasi TikTok dan YouTube Shorts.
* **Akar Masalah (Root Cause)**:
  Margin awal belum mengacu pada zona aman organik universal 9:16 (`x: 64..916`, `y: 220..1440`).
* **Solusi (Fix Applied)**:
  Kalibrasi margin aman di `video_engine.py` (`m_x_right = 156`, `m_x_left = 56`, `m_y_bottom = 380`, `m_y_top = 220`) dan tambahkan toggle visual **Safe Zone Overlay** di Phone Preview `ClipStudioSection.tsx`.
* **Pelajaran (Takeaway)**:
  Semua elemen penting (wajah reaksi, judul, subtitle, watermark) pada rasio 9:16 wajib memverifikasi kecocokan dengan Safe Box `x: 64..916, y: 220..1440`.

---

### Kasus #05: `moov atom not found` & Hardware Encoder Timeout saat Download/Render
* **Kategori**: Network Resilience & Hardware Encoder Fallback
* **Gejala (Symptom)**:
  Unduhan segmen `yt-dlp` yang terputus di tengah jalan menghasilkan file MP4 parsial tanpa atom `moov`, atau encoder GPU (`h264_amf`/`h264_nvenc`) mengalami timeout pada filtergraph kompleks.
* **Akar Masalah (Root Cause)**:
  Segmen parsial lolos ke FFmpeg jika tidak divalidasi dengan `ffprobe`, dan kegagalan GPU langsung mematikan batch job tanpa fallback CPU.
* **Solusi (Fix Applied)**:
  Validasi wajib `is_valid_mp4()` setelah download, timeout dinamis berdasarkan durasi klip, dan fallback otomatis ke universal `libx264` CPU di `render_clip_to_mp4()`.
* **Pelajaran (Takeaway)**:
  Selalu validasi integritas biner MP4 sebelum dan sesudah proses FFmpeg serta sediakan jalur fallback CPU.

---

### Kasus #06: TypeScript Build Fail akibat Ketidakselarasan Kunci i18n (`id.ts` vs `en.ts` vs TSX)
* **Kategori**: Frontend TypeScript & Lokalisasi
* **Gejala (Symptom)**:
  Penambahan kartu UI baru di `ClipStudioSection.tsx` gagal pada `tsc -b` karena perbedaan nama properti antara `t.studio.*` yang dipanggil di TSX dan kunci yang didefinisikan di `locales/id.ts` serta `locales/en.ts`.
* **Akar Masalah (Root Cause)**:
  Kunci lokalisasi ditambahkan terpisah tanpa verifikasi `npm run build --prefix apps/web` segera setelah edit.
* **Solusi (Fix Applied)**:
  Sinkronkan seluruh kunci di `id.ts` dan `en.ts`, hapus state yang tidak terpakai, dan wajib jalankan `npm run build --prefix apps/web` sebagai gate wajib sebelum selesai.
* **Pelajaran (Takeaway)**:
  Selalu edit `types.ts`, `id.ts`, `en.ts`, dan komponen TSX dalam satu sinkronisasi lalu kunci dengan `tsc -b`.


---

### Kasus #07: `UnboundLocalError` saat Audio Reaction Cam Diaktifkan (`reaction_cam_mute_audio=False`)
* **Kategori**: FFmpeg Audio Filtergraph / Python Ordering
* **Gejala (Symptom)**:
  Ketika pengguna mengaktifkan Reaction Cam PIP dengan `reaction_cam_mute_audio=False`, `render_clip_to_mp4()` melempar `UnboundLocalError` karena mencoba melakukan `audio_inputs_to_mix.append(...)` sebelum daftar `audio_inputs_to_mix = []` diinisialisasi di blok audio.
* **Akar Masalah (Root Cause)**:
  Blok overlay video Reaction Cam berada di atas blok mixing audio sehingga merujuk variabel lokal yang baru dideklarasikan beberapa puluh baris kemudian.
* **Solusi (Fix Applied)**:
  Simpan indeks input audio Reaction Cam sementara pada variabel `rc_audio_idx_to_mix` (dilindungi `check_has_audio(reaction_cam_file_path)`), lalu masukkan ke `audio_inputs_to_mix` setelah inisialisasi blok audio.
* **Pelajaran (Takeaway)**:
  Jaga pemisahan tegas antara tahap deklarasi input/video filtergraph dan tahap audio mixing, serta selalu uji jalur unmuted pada `qa-kernel.py`.

---

### Kasus #08: `NameError: name 'cv2' is not defined` pada Fungsi Helper Baru di `video_engine.py`
* **Kategori**: Python Lazy Import Discipline
* **Gejala (Symptom)**:
  `extract_cover_thumbnail()` di `apps/api/backend/video_engine.py` gagal secara diam-diam saat diuji E2E di `qa-kernel.py` dengan log `Cover thumbnail extraction failed: name 'cv2' is not defined`.
* **Akar Masalah (Root Cause)**:
  `video_engine.py` sengaja tidak mengimpor `cv2` dan `numpy` di top-level agar startup FastAPI cepat; fungsi helper baru lupa menambahkan `import cv2` dan `import numpy as np` secara lokal di dalam fungsi.
* **Solusi (Fix Applied)**:
  Tambahkan `import cv2` dan `import numpy as np` di dalam blok `try:` pada `extract_cover_thumbnail()` lalu verifikasi ulang melalui `qa-kernel.py` Check #5 hingga file `cover_*.jpg` terbangun valid (> 5 KB).
* **Pelajaran (Takeaway)**:
  `python -m compileall` tidak mendeteksi `NameError` runtime akibat lazy import; selalu jalankan fungsi baru secara nyata melalui `.agents/scripts/qa-kernel.py`.
