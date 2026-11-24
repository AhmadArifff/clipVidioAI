# Domain 02: FFmpeg Filtergraph, Silence Cutter & Post-Render QA

## 1. Pra-Pemrosesan Opsional: Smart Silence Jumpcut (`silence_cutter_service.py`)
Jika `silence_cut_mode` aktif (`natural` gap >= 0.55s, `snappy` gap >= 0.35s):
1. Membaca word timestamps hasil `transcribe_clip_words()` (atau fallback FFmpeg `silencedetect` jika transkrip kosong).
2. Memangkas dead air awal (`head_pad=0.12s`), dead air akhir (`tail_pad=0.28s`), dan jeda panjang antar-kata dengan mempertahankan nafas kontekstual (`0.14s` biasa, `0.20s` akhir kalimat `.!?`, `0.24s` jeda >= 2s).
3. Menjalankan 1-pass FFmpeg `trim`/`atrim` + `afade` 5 ms di tiap sambungan + `concat` sehingga video dan audio bebas klik serta 100% sinkron.
4. Melakukan **re-timing otomatis** seluruh `words` ke timeline baru sebelum diserahkan ke `generate_ass_file()` dan `generate_srt_file()`.

## 2. Rantai Filtergraph Inti (`video_engine.py::render_clip_to_mp4`)
* **Video Chain**:
  `Background Canvas` -> `Foreground Crop/Scale/Tracking` -> `Overlay` -> `Subtitles (.ass)` -> `Emoji Title (.png)` -> `Watermark` -> `Reaction Cam PIP` (safe margins) -> `Hook Zoom (0-2.5s)` -> `Comedy FX` -> `Visual Polish` -> `Speed Ramp (setpts)`.
* **Audio Chain**:
  1. `detect_safe_mono_pan()` sebelum `center_vocal_extract` (mencegah inverted phase cancellation).
  2. Volume boost + `atempo` (bila speed ramp aktif).
  3. Bila BGM + Smart Ducking aktif: **`asplit=2[v_voice_mix][v_voice_sidechain]`**.
  4. BGM memakai `highpass=f=120` (clarity speaker HP) + `sidechaincompress` dipicu `[v_voice_sidechain]`.
  5. `amix` + `loudnorm=I=-14:LRA=7:TP=-1.5`.
  6. Output terkunci: `-c:a aac -ar 48000 -ac 2 -b:a 192k`, `-pix_fmt yuv420p`, BT.709 color tags, `-movflags +faststart`.

## 3. Post-Render QA (`video_qa_service.py`)
Menjalankan audit cepat pada MP4 final (non-blocking thread):
* `stream_integrity`: cek resolusi genap, H.264, `yuv420p`, audio 48 kHz, durasi A/V delta <= 0.15s.
* `first_frame`: cek frame 0 (t=0.05s) bukan layar hitam/kosong (luma mean >= 12).
* `audio_loudness`: cek Integrated LUFS (target -14 +/- 2.5 LU), True Peak (<= -0.5 dBTP), dan tidak silent.
* `leading_silence`: cek jeda hening di awal klip (< 0.5s).
* `frozen_video`: cek `freezedetect` >= 2.5s.
* Mengembalikan status `PASS` / `WARN` / `FAIL` + daftar ringkas untuk ditampilkan sebagai QA Badge di modal render.
