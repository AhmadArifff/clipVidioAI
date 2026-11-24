# Domain 03: Studio WYSIWYG Preview & Safe Zone Sync

## 1. Skala Koordinat Kanvas
* **Kanvas Render Vertical (9:16)**: `1080 x 1920 px`.
* **Kanvas Preview di `ClipStudioSection.tsx`**: lebar dasar ~`320 px` (`scale = 320 / 1080` untuk vertical, `320 / 1920` untuk `16:9_landscape`).
* Posisi Y judul (`titleYPercent`), subtitle (`subtitleYPercent` / `subtitleCenterYPercent`), watermark (`watermarkX`, `watermarkY`), dan Reaction Cam PIP (`reactionCamSize`, `reactionCamPosition`) dihitung dengan persentase yang identik antara CSS preview dan ekspresi koordinat FFmpeg.

## 2. Universal Platform Safe Box (9:16 = 1080x1920)
Mengacu pada standar TikTok, YouTube Shorts, dan Instagram Reels:
* **Top Unsafe**: `0..220 px` (`0%..11.5%`) -> Search bar, tab Following/For You.
* **Bottom Unsafe**: `1440..1920 px` (`75%..100%`, atau `25%` terbawah) -> Nama akun, caption, audio ticker.
* **Right Unsafe**: `916..1080 px` (`15%` paling kanan) -> Tombol Like, Comment, Bookmark, Share.
* **Left Margin**: `0..64 px` (`6%` paling kiri) -> Tepi aman bezel HP.

Toggle **Safe Zone Overlay** di Phone Preview `ClipStudioSection.tsx` menampilkan panduan visual area ini agar pengguna dapat menempatkan judul, subtitle, watermark, dan Reaction Cam di dalam zona hijau/aman sebelum render.
