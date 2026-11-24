# Workflow Discipline & Rule #29 (Docs-First Retrieval & Self-Enrichment)

## 1. Siklus Kerja OODA
1. **Observe (Docs-First)**: Baca dokumen fitur terkait di `.agents/feature-docs/`, cek `.agents/knowledge/cross-feature-disambiguation.md`, dan cek `.agents/knowledge/bug-cases.md` sebelum membaca file besar atau menulis kode.
2. **Orient**: Identifikasi seluruh titik kontrak terdampak (Backend Router/Schema/Service/Engine + Frontend Types/Locales/Studio UI/App).
3. **Decide**: Tentukan desain perubahan yang backward-compatible, punya fallback aman, dan tidak merusak preset/fitur eksisting.
4. **Act & Verify**: Terapkan perubahan secara modular, jalankan verifikasi wajib Tier 1 (`qa-kernel.py` + `npm run build`), lalu lakukan *Self-Enrichment* pada `.agents/`.

## 2. Rule #29: Protokol Docs-First Retrieval & Self-Enrichment
* **Sebelum Koding**:
  * Selalu cek `.agents/feature-docs/README.md` untuk menemukan dokumen fitur target.
  * Selalu cek `.agents/knowledge/cross-feature-disambiguation.md` agar tidak tertukar antara jalur `single` vs `merged` vs `clientRenderer.ts` (WASM), atau `pip_corner` vs `reactionCamEnabled`.
* **Setelah Selesai Koding (Wajib Sebelum Selesai Sesi)**:
  * Perbarui berkas fitur terdampak di `.agents/feature-docs/` (minimal bagian Kontrak Parameter, Alur, dan Changelog).
  * Jika menyelesaikan bug baru, catat di `.agents/knowledge/bug-cases.md` dengan format 5 blok (Kategori, Gejala, Akar Masalah, Solusi, Pelajaran).
  * Perbarui `.agents/02-session-state/active-session.json` dengan milestone terbaru (`VERIFIED_PASS`).
  * Jika pengguna menggunakan portal dokumentasi eksternal, dokumentasi siap disinkronkan via `node .agents/scripts/sync-docs.js`.

## 3. Kebersihan Kode & Workspace
* Hapus seluruh berkas eksperimen sementara di root atau folder scratch test begitu verifikasi selesai.
* Tulis komentar kode secara ringkas dan fungsional (1-2 baris), fokus pada alasan teknis ("why"), tanpa banner dekoratif atau kutipan nomor dokumen internal AI.
* Jangan meninggalkan dead code, unused imports, atau state React yang tidak terpakai (terverifikasi otomatis lewat `tsc -b`).
