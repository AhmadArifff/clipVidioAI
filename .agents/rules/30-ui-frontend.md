# Standar UI/UX Frontend Studio & WYSIWYG Preview (`ClipVidio AI`)

Berlaku untuk seluruh komponen React/TypeScript di `apps/web/src/`:

## 1. Paritas WYSIWYG Preview (320px vs 1080x1920)
* Segala posisi judul, subtitle, watermark, foreground scale, dan Reaction Cam PIP di Phone Preview (`ClipStudioSection.tsx`) harus mencerminkan proporsi persentase aktual pada kanvas `1080x1920` (atau `1920x1080` pada `16:9_landscape`).
* Phone Preview wajib menyediakan tombol toggle **Safe Zone Overlay (TikTok / Shorts / Reels)** yang memvisualisasikan area UI platform (`top: 11.5%`, `bottom: 25%`, `right: 15%`, `left: 6%`) sehingga pengguna langsung tahu apakah teks atau wajah reaksi aman sebelum render.

## 2. Kontrak Lokalisasi (Dual-Language i18n)
* Setiap label UI baru **WAJIB** ditambahkan serentak di kedua berkas:
  * `apps/web/src/locales/id.ts` (Bahasa Indonesia baku, ramah, bebas jargon teknis internal)
  * `apps/web/src/locales/en.ts` (English)
* Dilarang keras memakai karakter em dash di string lokalisasi maupun komponen TSX (Rule R-02).

## 3. Persistensi & Reset Defaults
* Setiap preferensi studio baru yang bersifat persisten wajib ditambahkan ke:
  1. `DEFAULT_STUDIO_PREFS` di `ClipStudioSection.tsx`
  2. `useEffect` penyimpan `localStorage` (`STUDIO_PREFS_KEY`)
  3. `handleResetToDefaults()`
  4. `handleLaunch()` -> `onStartRender(...)`

## 4. Build Verification Gate
* Sebelum menganggap perubahan Frontend selesai, wajib lulus kompilasi penuh `npm run build --prefix apps/web` (`tsc -b && vite build`) dengan 0 error dan 0 unused variable warning.
