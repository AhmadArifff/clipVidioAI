# Case 20261011: Dual-Subtitle Collision & Cross-Language Dubbing Latency

## 1. Metadata
- **ID Kasus**: CASE-20261011-SUBTITLE-SYNC-LANG
- **Tanggal**: 2026-10-11
- **Domain**: Media Processing, Subtitle Pipeline, ASS Generator, Audio-Text Synchronization
- **Tingkat Keparahan**: Medium (UX / Visual Clutter)
- **Status**: Documented & Architecture Approved (PRD v2.6.0)

---

## 2. Gejala & Temuan Lapangan
Pengguna melaporkan dua kejanggalan visual pada klip hasil proses dan Studio Preview:
1. **Terdapat 2 Lapisan Subtitle Bertumpuk**:
   - Subtitle 1 (Putih kecil di atas bar hitam tipis): Berbahasa Indonesia (*"paus itu menabrak kapal dengan kekuatan besar"*).
   - Subtitle 2 (Besar tebal dengan styling warna viral pink/putih): Berbahasa Inggris (*"RAMMED THE WITH"*).
2. **Bahasa Tidak Sesuai Keinginan Pengguna**:
   - Pengguna mengharapkan subtitle berbahasa Indonesia, namun sistem menghasilkan subtitle karaoke berbahasa Inggris.
3. **Sensasi Delay antara Suara Dubbing dan Teks**:
   - Teks subtitle styling muncul sedikit terlambat (*lag/delay*) dibandingkan pelafalan narator dubbing.

---

## 3. Investigasi Akar Masalah (Root Cause Analysis)

### Akar Masalah A: Asal-Usul Subtitle Pertama (Hardsub Bawaan Video)
Berdasarkan inspeksi `ffprobe` terhadap file mentah `batch_..._raw.mp4`, kontainer hanya memiliki 2 stream:
- `Stream #0:0`: Video H.264
- `Stream #0:1`: Audio AAC
Tidak ada stream subtitle terpisah (`subtitles`/`mov_text`). Artinya, teks putih kecil berbahasa Indonesia tersebut **merupakan teks hardsub yang sudah tertempel pada piksel video asli di YouTube oleh kreator aslinya**.

### Akar Masalah B: Konflik Bahasa & Ketiadaan Selektor Bahasa
Di YouTube, video tersebut memiliki transkrip asli bahasa Inggris (`en`) dan subtitle terjemahan otomatis. Fungsi backend `prioritize_transcripts()` sebelumnya memprioritaskan bahasa lisan asli ASR YouTube (`native_asr_lang`), sehingga secara otomatis menarik track bahasa Inggris (`en`) tanpa memberi opsi kepada pengguna untuk memilih Bahasa Indonesia (`id`).

### Akar Masalah C: Penyebab Delay Antara Dubbing dan Subtitle
1. **Perbedaan Gramatika & Durasi Pelafalan**: Audio narasi menggunakan bahasa Indonesia yang memiliki jumlah suku kata dan ritme bicara berbeda dengan transkrip teks bahasa Inggris.
2. **Granularitas Timestamp YouTube ASR**: YouTube kerap memberikan timestamp per frasa panjang (3-5 detik) alih-alih per kata presisi, sehingga interpolasi kata buatan FFmpeg/ASS mengalami pergeseran waktu (200ms - 500ms).

---

## 4. Solusi Terstruktur & Blueprint Arsitektur

### Solusi 1: Pemilih Bahasa Subtitle Terfokus (Indonesian & English)
- Menambahkan parameter `subtitle_language` pada request analisis dan render:
  - Nilai: `"id"` (Bahasa Indonesia) atau `"en"` (English).
- Pada `youtube_service.py`:
  - Jika pengguna memilih `"id"`, sistem mencari track `id` / `id-ID` terlebih dahulu (baik manual maupun auto-translated YouTube).
  - Jika pengguna memilih `"en"`, sistem mengambil track bahasa Inggris asli.

### Solusi 2: Kalibrasi Offset Timing Subtitle (Audio-Subtitle Shift)
- Menambahkan slider pengaturan `subtitle_offset_ms` di Studio (rentang `-1000ms` hingga `+1000ms`, default `0ms`).
- Nilai offset ditambahkan ke setiap event dialog ASS:
  `Start = max(0.0, event.start + offset)` dan `End = event.end + offset`.
- Memungkinkan pengguna menyelaraskan subtitle dengan suara dubbing secara instan.

### Solusi 3: Mode "Tanpa Subtitle" (Anti-Clutter jika Video Sudah Ada Teks)
- Jika video YouTube yang dipotong sudah memiliki hardsub bawaan dari pembuat aslinya, pengguna cukup memilih opsi `Gaya Subtitle: None` di Studio agar FFmpeg tidak menambahkan subtitle kedua di atas video.

---

## 5. Kepatuhan Governance & Verification Gate
- Bebas dari em dash (R-02).
- Telah disinkronkan ke dalam `PRD.md` dan `.agents/session-state.json`.
