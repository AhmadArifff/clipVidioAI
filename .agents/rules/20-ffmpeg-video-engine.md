# Standar FFmpeg Video Engine, Subtitle & Audio Mastering (`ClipVidio AI`)

Dokumen ini mengunci standar teknis pada [video_engine.py](../../apps/api/backend/video_engine.py), [silence_cutter_service.py](../../apps/api/backend/services/silence_cutter_service.py), dan [video_qa_service.py](../../apps/api/backend/services/video_qa_service.py) (mengadopsi standar `herk-edit-kit`, `showtime`, `reelmimic`, `motlab`, dan `motionmaxxing`).

## 1. Hukum Filtergraph FFmpeg
1. **Single-Consumption Pad Rule**: Setiap pad output `[label]` hanya boleh masuk ke 1 filter berikutnya. Jika audio vokal dibutuhkan oleh `sidechaincompress` DAN `amix`, wajib gunakan `asplit=2[v_voice_mix][v_voice_sidechain]`.
2. **Urutan Komposisi Video Wajib**:
   `[Background Canvas]` -> `[Foreground Crop/Scale/Face-Tracking]` -> `[Overlay Foreground ke Canvas]` -> `[Subtitles ASS]` -> `[Title PNG Emoji]` -> `[Watermark]` -> `[Reaction Cam PIP]` -> `[Hook Punch-in Zoom 0-2.5s]` -> `[Comedy FX]` -> `[Visual Polish unsharp/eq]` -> `[Micro Speed Ramp setpts]`.
3. **Master Encoding Spec**:
   * Video: H.264, `yuv420p`, BT.709 tagged (`-colorspace bt709 -color_primaries bt709 -color_trc bt709`), `-movflags +faststart`.
   * Audio: AAC-LC **48 kHz stereo** (`-c:a aac -ar 48000 -ac 2 -b:a 192k`).
   * Encoder fallback: Utamakan hardware (`nvenc` / `amf` / `qsv`), otomatis fallback ke `libx264 -preset veryfast -crf 22` jika timeout atau gagal.

## 2. Standar Audio & Anti-Phase-Cancel
1. **Phase-Safe Mono Check** (dari `reelmimic`): Sebelum menerapkan `center_vocal_extract` (`0.5*L + 0.5*R`), ukur volume RMS kanal L, kanal R, dan jumlah L+R. Jika `L+R` lebih rendah > 6 dB dibanding kanal terkuat (indikasi rekaman *inverted phase*), otomatis ekstrak kanal tunggal terkuat saja (`c0=c0|c1=c0` atau `c0=c1|c1=c1`) agar suara tidak hilang.
2. **Phone Speaker Clarity** (dari `showtime`): Terapkan `highpass=f=120` pada BGM bed saat bercampur dengan dialog vokal agar sub-bass tidak menelan suara pembicara di speaker smartphone.
3. **Broadcast Loudness**: Target `-14 LUFS`, `LRA=7`, `TP=-1.5 dBTP` via `loudnorm`.

## 3. Standar Safe Zone 9:16 (1080x1920)
Mengacu pada `showtime/references/platforms.md`:
* **Universal Organic Safe Box**: `x = 64..916` (sisi kanan 164 px tertutup tombol Like/Comment/Share), `y = 220..1440` (bawah 480 px tertutup caption & profil channel, atas 220 px tertutup bar pencarian).
* **Reaction Cam PIP**: Pada posisi bawah (`bottom_right`/`bottom_left`), margin vertikal aman minimal `380 px` dari bawah dan margin kanan aman minimal `150 px` pada `bottom_right` (atau `56 px` di kiri) agar wajah kreator tidak terpotong UI TikTok/Shorts.

## 4. Standar Subtitle ASS & Sidecar SRT
* Minimum durasi tampil satu chunk subtitle: **`>= 0.40s`** (mencegah `caption_flash` yang terlalu cepat dibaca mata), kecuali terbatasi langsung oleh awal chunk berikutnya.
* Selalu sertakan preset **High-Contrast Box** (`high_contrast_box`, latar gelap semi-transparan `BorderStyle=3` agar terbaca jelas di atas rekaman terang maupun gelap).
* Setiap render klip menghasilkan sidecar `.srt` di dalam paket ZIP ekspor untuk SEO indexing YouTube Shorts / LinkedIn.

## 5. Standar Smart Silence Jumpcut
* Menggunakan 1-pass FFmpeg `trim`/`atrim` + **5 ms micro-audio-fade** (`afade` masuk/keluar) di tiap sambungan agar bebas bunyi klik/pop.
* Jeda antar kata dipangkas dengan mempertahankan **nafas natural adaptif** (`0.14s` biasa, `0.20s` akhir kalimat `.!?`, `0.24s` jeda >= 2s), dan langsung menggeser (*re-time*) seluruh timestamp kata agar subtitle ASS tetap 100% sinkron dengan gerak bibir.
