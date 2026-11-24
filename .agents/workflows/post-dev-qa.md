# SOP: Post-Development QA (`ClipVidio AI` - Hemat Token)

Dokumen ini mengatur pelaksanaan **Quality Assurance (QA) terstruktur pasca-development** di proyek **ClipVidio AI** menggunakan pola 2-Tier seperti `adminShuttleV3`, diadaptasi 100% ke stack Python FastAPI + FFmpeg + React Vite.

---

## 1. Pemisahan Peran (Zero-Overlap)
* **Tier 1 (Wajib Tiap Selesai Coding, ~5-12 Detik, Tanpa Browser)**:
  * Jalankan runner CLI reusable:
    ```powershell
    .\.venv\Scripts\python.exe .agents\scripts\qa-kernel.py
    ```
  * Plus build frontend TypeScript:
    ```powershell
    npm run build --prefix apps/web
    ```
* **Tier 2 (Browser Visual QA Playwright - On-Demand Only)**:
  * Hanya dijalankan jika pengguna secara eksplisit meminta pengujian browser / inspeksi screenshot UI, mengikuti [playwright-testing.md](./playwright-testing.md).

---

## 2. Cakupan Verifikasi Tier 1 (`qa-kernel.py`)
Satu perintah `qa-kernel.py` otomatis memverifikasi:
1. **Python Syntax & Import Check**: Kompilasi seluruh modul di `apps/api/backend/` (`routers/`, `services/`, `schemas/`, `video_engine.py`).
2. **Pydantic Contract & 5-Point Sync Check**: Memvalidasi default dan skema `RenderSettingsModel` + `ViralClip`.
3. **Synthetic FFmpeg Pipeline E2E Tests**:
   * **Test A (Standard + Phase-Safe Audio + BGM Smart Ducking + High-Contrast Box Subtitle + Reaction Cam PIP)**: Membuktikan bebas error pad ganda, audio 48 kHz stereo, frame 0 valid, dan ukuran file valid.
   * **Test B (Inverted Stereo Phase Protection)**: Membuat audio stereo fase terbalik (`R = -L`) dan memastikan `detect_safe_mono_pan` menyelamatkan suara agar tidak hening!
   * **Test C (Smart Silence Jumpcut + Subtitle Re-Timing)**: Membuat video dengan jeda hening panjang di awal dan tengah, memastikan durasi terpangkas, 5 ms micro-fade aktif, dan `words` tergeser presisi.
   * **Test D (Post-Render QA Service + Sidecar SRT + Cover JPG)**: Menjalankan `video_qa_service.audit_rendered_video()`, cek output `.srt`, dan ekstraksi `cover.jpg`.
4. **Anti-Slop Guard (Rule R-02)**: Memastikan tidak ada em dash bocor di file yang diubah.

---

## 3. Format Laporan QA ke Pengguna

| Lapisan Uji | Skenario | Status | Catatan Singkat |
| :--- | :--- | :---: | :--- |
| Tier 1 (Python/Schema) | Syntax & Pydantic Contracts | PASS | 0 error import/schema |
| Tier 1 (FFmpeg Core) | Render + Ducking + Reaction Cam + High-Contrast Box | PASS | MP4 valid, 48 kHz, BT.709 |
| Tier 1 (Audio Phase) | Inverted Phase Stereo Recovery | PASS | Terdeteksi & diselamatkan |
| Tier 1 (Jumpcut) | Silence Cutter + Subtitle Re-Time | PASS | Dead air terpangkas, sinkron |
| Tier 1 (Video QA) | `video_qa_service` + SRT + Cover | PASS | LUFS, Frame 0, SRT & JPG valid |
| Tier 1 (Frontend) | `tsc -b && vite build` | PASS | 0 TypeScript error |
| Tier 2 (Browser) | Playwright UI *(On-Demand)* | SKIP / PASS | Jalankan hanya bila diminta |
