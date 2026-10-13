# Case Study: Visual Config Diff & 3-Second Live Preview Spotlight (v3.8.0)

- **ID Kasus**: `CASE-20261014-DIFF-INSPECTOR-SPOTLIGHT`
- **Tanggal**: 2026-10-14
- **Komponen Terdampak**: 
  - `apps/api/backend/schemas/recommendation.py`
  - `apps/api/backend/services/recommendation_service.py`
  - `apps/web/src/types.ts`
  - `apps/web/src/locales/index.ts`
  - `apps/web/src/components/ClipStudioSection.tsx`
  - `apps/web/src/index.css`
- **Reviewer Status**: VERIFIED PASS (QA Engineer & Tech Critic Dual Approval)
- **Kepatuhan Guardrails**: Rule R-02 (Zero Em Dash Mutlak), WCAG AA Contrast, No Slop, Content-Driven UI.

---

## 1. Problem Statement
Sebelumnya, saat sistem merekomendasikan profil setelan AI (seperti MrBeast, Alex Hormozi, Vox Documentary), pengguna tidak dapat membandingkan nilai konfigurasi saat ini dengan nilai yang direkomendasikan secara transparan. Pengguna juga tidak mendapatkan penjelasan terukur mengenai dampak retensi dari setiap parameter, dan tidak dapat melihat efek visual spesifik pada video preview sebelum memutuskan untuk menerapkan setelan.

## 2. Solusi Rekayasa yang Diterapkan
1. **Side-by-side Configuration Comparison Table**:
   - Menampilkan komparasi 6 pilar konfigurasi: Gaya Subtitle & Font, Aksen Kata Kunci & Emoji, Hook Punch-In Zoom, BGM & Auto-Ducking, Anti-Content ID Shield & Micro Pacing, serta Framing Kamera 9:16.
   - Kolom Dampak Algoritma Terukur menyajikan penjelasan dampak retensi dan keterbacaan (misal: +24% keterbacaan instan di layar ponsel saat scroll cepat).
2. **Interactive 3-Second Spotlight with Auto-Dismiss**:
   - Tombol "Highlight (3s)" pada setiap baris konfigurasi memicu spotlight visual pada elemen bersangkutan di live phone preview player.
   - Banner spotlight menampilkan nama parameter, deskripsi dampak, dan bilah hitung mundur 3 detik yang menyusut secara linear.
   - Elemen video (kotak takarir, judul, frame video, audio soundwave) berkedip dengan animasi neon pulsing dan otomatis kembali normal (auto-fade) tepat setelah 3 detik.
3. **Portal-based Responsive Viewport Integration**:
   - Modal diff dirender melalui `createPortal(..., document.body)` untuk melepaskan diri dari batasan stacking context dan transform induk.
   - Pada layar desktop (lebar >= 1200px), saat spotlight aktif, backdrop modal menjadi transparan dan kartu bergeser mulus ke sisi kiri sehingga live phone preview di sisi kanan terlihat 100% tanpa halangan.
4. **Confirmation Gate (Apply vs Regenerate)**:
   - Tombol "Setujui & Terapkan Settingan Rekomendasi" (hijau emerald) untuk menerapkan seluruh paket konfigurasi dengan 1 klik.
   - Tombol "Belum Puas? Regenerasi AI" (oranye amber) untuk memicu kalkulasi ulang variasi profil viral lainnya.

## 3. Hasil Pengujian & Verifikasi
- **Unit Test Backend**: `scratch/test_recommendation_diff.py` lulus 100% memverifikasi parameter `speed_ramp_ratio`, `vocal_isolation_mode`, `camera_tracking_mode`, dan kamus `param_impacts`.
- **E2E Browser Automation**: Pengujian Playwright memverifikasi pembukaan modal, rendering tabel 6 baris, pemicuan spotlight 3 detik, auto-dismiss, penutupan modal saat konfirmasi, dan penerapan profil.
- **Kompilasi Monorepo**: `npm run build` lulus (exit code 0, 1.46 detik) dan `py_compile` lulus (exit code 0).
