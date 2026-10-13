# Case 20261013: Speech Cadence Clamping & Reverse Chronological Subtitle Sync

## 1. Metadata
- **ID Kasus**: CASE-20261013-SPEECH-CADENCE-SUBTITLE-SYNC
- **Tanggal**: 2026-10-13
- **Domain**: Media Processing, Subtitle Pipeline, High-Tempo Speech, Word-Level Sync, Studio Live Preview
- **Tingkat Keparahan**: High (Core UX Feature Failure during Fast Dialogue / Podcasts)
- **Status**: Resolved & Architecture Codified (v3.5.1)

---

## 2. Gejala & Bukti Visual (Visual Artifacts)
Pengguna mendapati anomali desinkronisasi pada klip dialog bertempo cepat (contoh: podcast Fajar Sadboy):
1. **Subtitle Asli Video Berjalan Normal**:
   - Teks bawaan video yang tidak di-styling sudah berpindah ke kalimat baru: *"beda lagi sekarang. Enggak tahu"*.
2. **Subtitle dengan Styling Tertahan (Lag/Delay)**:
   - Subtitle dengan visual punch / karaoke masih terkunci pada kata terakhir dari baris sebelumnya: *"SEKARANG."*.
3. **Pertanyaan Inti Pengguna**:
   - *"Kenapa text yang tidak delay tanpa styling mengikuti dengan baik sementara text subtitle yang dengan styling tidak karena kecepetan seperti itu? Jadi gimana metode logic yang cocok supaya tidak delay?"*

---

## 3. Investigasi Akar Masalah (Root Cause Analysis)

### Akar Masalah A: YouTube Auto-Caption Overlap Inflation
YouTube ASR membuat format subtitle bertipe rolling 2-line box di mana durasi setiap segmen sengaja dibuat panjang (3.0 detik hingga 5.0 detik per cue) agar baris teks tetap terbaca di layar pemutar YouTube bawaan.
- Cue 1: start = 12.0s, end = 16.5s (*"beda lagi sekarang."*)
- Cue 2: start = 14.1s, end = 18.0s (*"Enggak tahu"*)
Pada pemutar YouTube bawaan, kedua baris ditampilkan bersamaan bertumpuk dua tingkat sehingga penonton melihat keduanya.

### Akar Masalah B: Forward Search Starvation pada Single-Line Punch Captions
Gaya subtitle viral punch (seperti Beast Punch atau Pop Word) hanya menampilkan 1 kata atau 1 baris pendek pada satu waktu.
Pada implementasi lama:
```typescript
fullTranscript.find(item => item.start <= effectiveTime && effectiveTime <= item.end)
```
Pencarian array dilakukan maju dari indeks 0 (`Array.prototype.find()`).
Ketika audio berada di detik 14.5s:
- Cue 1 masih valid karena `effectiveTime <= 16.5s`.
- Cue 2 juga valid karena `14.1s <= effectiveTime <= 18.0s`.
Namun karena `find()` berhenti pada kecocokan pertama, sistem **selalu mengembalikan Cue 1** hingga detik 16.5s. Akibatnya, kata terakhir Cue 1 (*"SEKARANG."*) tetap terpajang di layar selama lebih dari 2 detik setelah pembicara melafalkan kata berikutnya (*"Enggak tahu"*).

### Akar Masalah C: Pembagian Durasi Kata Rata (Uniform Division)
Ketika transkrip tidak memiliki Word-Level Timestamps bawaan, sistem lama membagi durasi cue secara seragam (`duration / wordCount`). Pada ucapan cepat, kata pendek (seperti "dan", "lagi", "ini") mendapat alokasi durasi yang sama besarnya dengan kata panjang, sehingga kata-kata terakhir menumpuk di akhir rentang waktu.

---

## 4. Solusi Rekayasa Logic & Standar Arsitektur

### Solusi 1: Speech Cadence Clamping Pipeline
Sebelum transkrip diproses untuk penentuan kata aktif, setiap cue dinormalisasi secara deterministik:
1. **Next-Cue Boundary Clamping**:
   `clampedEnd = min(cur.end, next.start)` (Cue tidak boleh melewati waktu mulai cue berikutnya).
2. **Max Spoken Cadence Cap**:
   Kapasitas pelafalan manusia rata-rata adalah 150-200 kata per menit (sekitar 0.3-0.4 detik per kata).
   `maxSpokenDuration = max(0.6, wordCount * 0.40)` detik.
3. **Real End Determination**:
   `realEnd = min(clampedEnd, cur.start + maxSpokenDuration)`.
Dengan formula ini, cue pendek berisi 2 kata tidak akan pernah menggantung lebih dari 0.8 detik di layar.

### Solusi 2: Reverse-Chronological Cue Selection
Di fungsi `liveSubtitleInfo` (`ClipStudioSection.tsx`):
Alih-alih mencari dari depan, sistem memindai transkrip secara terbalik dari indeks paling akhir ke indeks awal:
```typescript
for (let i = syncedTranscript.length - 1; i >= 0; i--) {
  const cue = syncedTranscript[i];
  if (effectiveTime >= cue.start && effectiveTime <= cue.end + 0.15) {
    activeCue = cue;
    break;
  }
}
```
Ketika pembicara mulai mengucapkan kata pada Cue 2, pemindai terbalik langsung mengunci Cue 2 seketika tanpa terhalang durasi usang dari Cue 1.

### Solusi 3: Character / Syllable-Weighted Word Timing
Waktu setiap kata dihitung proporsional terhadap panjang karakternya:
```typescript
const weight = Math.max(1, word.length);
const wordDuration = (weight / totalWeight) * cueDuration;
```
Kata pendek lekas berganti dan kata panjang mendapatkan durasi yang natural sesuai ritme fonetik lisan.

### Solusi 4: Paritas Backend Rendering di `video_engine.py`
Logika Speech Cadence Clamping dan character-weighted timing diterapkan secara identik pada fungsi Python `generate_word_level_subtitles_from_transcript` di backend:
```python
max_spoken_dur = max(0.6, words_cnt * 0.40)
effective_end = min(clamped_end, max(effective_start + 0.5, effective_start + max_spoken_dur))
```
Hal ini menjamin hasil render file video akhir sama persis dengan apa yang dilihat pengguna di Studio Live Preview.

### Solusi 5: Clock Extrapolation 25ms & Preset Dubbing Cepat
- Ekstrapolasi waktu frame menggunakan `performance.now()` dengan polling 25ms untuk transisi visual 60fps tanpa jeda antar timeupdate browser.
- Lead-in offset kompensasi otomatis 280ms untuk mengatasi latensi decoding audio HTML5.
- Tombol shortcut 1-klik `⚡ Dubbing Cepat (-200 ms)` di antarmuka Studio untuk menyelaraskan audio bertempo sangat cepat.

---

## 5. Kepatuhan Governance & Verification Gate
- **Hard Gate R-02**: Bebas dari em dash.
- **Kompilasi TypeScript**: Lulus 100% via `tsc -b && vite build` (0 warning, 0 error).
- **Kompilasi Python Backend**: Lulus 100% via `py_compile`.
- **Reviewer Dual-Approval**: Disetujui oleh `qa-engineer` dan `tech-critic`.
