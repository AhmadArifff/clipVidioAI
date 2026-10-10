# Case Study: YouTube Segment Download Latency, Progress Telemetry Streaming, & Smart Caching Strategy

## 1. Identifikasi Kasus
* **ID Kasus**: `CASE-20261010-RENDER-TELEMETRY-CACHING`
* **Komponen Terdampak**: `apps/api/backend/services/render_service.py`, `video_engine.py`, `apps/web/src/components/ClipStudioSection.tsx`
* **Tanggal Analisis**: 10 Oktober 2026
* **Status**: ARCHITECTURAL_BLUEPRINT_PLANNED

---

## 2. Deskripsi Masalah & Analisis
Saat pengguna memulai proses render batch klip video (misalnya klip video YouTube), progres render pada klip pertama tampak tertahan (*stuck*) di status:
```
#1 The True Story That Inspired Moby Dick ⚡ Memotong (15%)
```
Kondisi ini berlangsung selama 15 hingga 40 detik sebelum akhirnya melompat langsung ke 40% (transkripsi) dan 70% (rendering FFmpeg).

### Akar Masalah Teknis:
1. **Bukan Render Eksternal / AI**: Proses pemotongan dan rendering video dijalankan 100% lokal di komputer pengguna menggunakan library `yt-dlp` dan `FFmpeg`.
2. **Blocking Subprocess Execution**: Fungsi `download_clip_segment` mengeksekusi `subprocess.run([yt-dlp, ...])` secara sinkron/blocking di dalam thread executor.
3. **Static Progress Feedback**: Karena tidak ada parsing stdout real-time selama `subprocess.run()` berjalan, backend mengunci nilai `clip_status["progress_percent"] = 15`.
4. **Label UI Ambigu**: Label *"⚡ Memotong (15%)"* menimbulkan persepsi bahwa sistem sedang melakukan cropping lokal yang macet, padahal di latar belakang sistem sedang melakukan transfer data unduhan video 1080p + audio dari CDN YouTube via koneksi internet.
5. **Redundant Re-download**: Jika pengguna merender ulang klip yang sama dengan penyesuaian font/watermark, file segmen mentah yang sama diunduh kembali dari awal tanpa memanfaatkan cache lokal.

---

## 3. Strategi Perbaikan & Solusi Arsitektural

### A. Real-Time Download Progress Parser
* Membaca stream stdout dari `yt-dlp` menggunakan format `--progress-template "%(progress._percent_str)s;%(progress._speed_str)s;%(progress._eta_str)s"`.
* Meneruskan data progres unduhan byte riil ke Server-Sent Events (SSE) `/api/render-progress/{batch_id}`.
* UI menampilkan detail dinamis:
  `"⬇️ Mengunduh Segmen HD (32% · 4.8 MB/s · ETA: 5s)"`.

### B. Smart Video Segment Caching
* Menyimpan segmen mentah di `temp_downloads/` dengan kunci hash:
  `cache_{video_id}_{start_time}_{end_time}.mp4`.
* Jika klip dirender ulang atau rentang waktu yang sama diminta kembali dalam rentang TTL (1 jam), proses lewati unduhan (0 detik) dan langsung mengeksekusi compositing.

### C. Single-Pass Master Stream Slicing
* Pada pemrosesan batch $\ge$ 3 klip dari video yang sama, unduh master stream satu kali.
* Lakukan ekstraksi klip-klip turunan secara lokal menggunakan `ffmpeg -ss ... -to ... -c copy` yang berkecepatan tinggi (~1 detik per klip).

### D. Hardware Acceleration Priority
* Memastikan encoder perangkat keras `h264_amf` (AMD) atau `h264_nvenc` (NVIDIA) selalu diprioritaskan otomatis untuk mengurangi waktu compositing filter FFmpeg hingga 3x-5x.

---

## 4. Verifikasi & Approval Gate
* **PRD Mapping**: Fase 7 (High-Speed Render Engine & Telemetry Streaming)
* **Status**: APPROVED for Future Roadmap
