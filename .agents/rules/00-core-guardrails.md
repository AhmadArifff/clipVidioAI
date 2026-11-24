# Core Guardrails ClipVidio AI (Aturan Mutlak)

Seluruh agen pengembang **WAJIB** mematuhi batasan teknis berikut tanpa pengecualian pada proyek **ClipVidio AI**:

1. **Zero Secret & Credential Leak**:
   * Dilarang menaruh kunci API (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `SUPADATA_API_KEY`), kredensial proxy, atau isi `cookies.txt` YouTube di kode sumber, fixture test, maupun dokumentasi.
   * File cookies sementara untuk `yt-dlp` wajib memakai context manager `ephemeral_cookies_file` agar langsung dihapus usai dipakai.
2. **FFmpeg Filtergraph Integrity**:
   * Dilarang mengonsumsi satu stream pad output FFmpeg lebih dari satu kali dalam `filter_complex`. Jika stream dipakai oleh 2 cabang (contoh: audio untuk `sidechaincompress` dan `amix`), wajib gunakan `asplit=2` atau `split=2`.
   * Dilarang mengandalkan 1 hardware encoder saja tanpa fallback universal ke `libx264` CPU.
   * Dilarang melakukan penjumlahan stereo-to-mono mentah (`0.5*L + 0.5*R`) tanpa pengecekan *inverted phase* terlebih dahulu.
3. **5-Point RenderSettings Contract Sync**:
   * Setiap fitur render baru yang menambah parameter wajib disinkronkan di 5 titik:
     1. `apps/web/src/types.ts` (`RenderSettings`)
     2. `apps/web/src/components/ClipStudioSection.tsx` (state, `STUDIO_PREFS`, `handleResetToDefaults`, `handleLaunch`)
     3. `apps/web/src/App.tsx` (`handleStartBatchRender` payload snake_case)
     4. `apps/api/backend/schemas/render.py` (`RenderSettingsModel`)
     5. `apps/api/backend/services/render_service.py` (kedua jalur: `render_single_batch_clip` dan `render_merged_batch_clips`) -> `apps/api/backend/video_engine.py`
4. **Sanitasi Upload Media**:
   * Semua file upload (video sumber, custom background, BGM, SFX, watermark, reaction cam) wajib memvalidasi ekstensi file, batas ukuran, dan membersihkan nama file (`Path(name).name`) untuk mencegah *path traversal*.
5. **Anti-Slop & Clean Copywriting (R-02)**:
   * Dilarang menggunakan karakter em dash di kode, komentar, lokalisasi UI (`id.ts`, `en.ts`), maupun laporan ke pengguna.
   * Label antarmuka wajib human-friendly tanpa jargon teknis internal.
6. **Batas Eksekusi Browser Otomatis**:
   * Pengujian browser Playwright (Tier 2) hanya dijalankan secara *on-demand* atau saat memverifikasi tampilan UI yang diminta pengguna; utamakan Tier 1 CLI (`qa-kernel.py` + `npm run build`) agar cepat dan hemat token.
