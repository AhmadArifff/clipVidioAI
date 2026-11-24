# Basis Pengetahuan & Memori Teknis ClipVidio AI (`.agents/knowledge/`)

Direktori ini adalah pusat pengetahuan teknis (**Single Source of Truth**) untuk proyek **ClipVidio AI** (`Clipper-Vidio-YT`). Seluruh AI Agent wajib merujuk berkas-berkas di sini sebelum memodifikasi alur render, FFmpeg filtergraph, AI analyzer, maupun komponen Studio UI.

---

## Indeks Dokumen Pengetahuan

1. **[cross-feature-disambiguation.md](./cross-feature-disambiguation.md)**: **[CRITICAL]** Kamus Anti-Halusinasi pemisah 6 keluarga fitur kembar (Single vs Merged vs Client WASM, PIP Sumber vs Reaction Cam, ASS Title vs PNG Emoji Title, `ClipStudioSection` vs `ClipStudioModal`, dll.).
2. **[bug-cases.md](./bug-cases.md)**: Riwayat kasus bug produksi nyata di ClipVidio AI beserta akar masalah dan pola pencegahannya.
3. **[domain-reference/README.md](./domain-reference/README.md)**: 4 dokumen arsitektur mendalam (Ingestion & AI Pipeline, FFmpeg Filtergraph, WYSIWYG Preview Sync, dan 5-Point RenderSettings Contract).
4. **[hub-and-spoke-sync.md](./hub-and-spoke-sync.md)**: Protokol sinkronisasi Master Hub (`agentic AI`) dengan proyek spoke.

---

## Standar Penambahan Kasus Bug Baru
Setiap kali menyelesaikan bug produksi di `bug-cases.md`, gunakan struktur 5 blok:
1. **Kasus #**: Judul deskriptif bug.
2. **Kategori**: Backend / FFmpeg Filtergraph / Audio DSP / AI Router / Frontend Studio / Media Upload.
3. **Gejala (Symptom)**: Error atau anomali visual/audio yang muncul.
4. **Akar Masalah (Root Cause)**: Penyebab teknis persis di kode.
5. **Solusi & Pelajaran (Fix & Takeaway)**: Berkas yang diubah dan aturan pencegahan permanen.
