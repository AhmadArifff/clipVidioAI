# 🎬 ClipVidio AI

> **AI Powered Auto Clipper — Turn long YouTube, Google Drive, and uploaded videos into viral TikToks, Shorts, and Reels with animated subtitles, face centering, and music in minutes.**

---

## ⚡ Cara Menjalankan Project (How to Run)

ClipVidio AI menyediakan 3 cara menjalankan aplikasi, mulai dari yang paling praktis hingga manual:

### 🚀 Cara 1: Menggunakan Launcher Otomatis (Direkomendasikan untuk Windows)
Cukup jalankan file [`start.bat`](./start.bat) dengan double-click atau lewat terminal:
```cmd
start.bat
```
* **Fitur Cerdas `start.bat` Baru:**
  * ✅ Otomatis memeriksa instalasi **Node.js** & **NPM**.
  * ✅ Otomatis mendeteksi jika folder `node_modules` belum ada dan menjalankan `npm install` secara otomatis.
  * ✅ Otomatis memeriksa instalasi **Python** (versi 3.10+).
  * ✅ Otomatis membuatkan virtual environment (`venv`) jika belum tersedia.
  * ✅ Otomatis menginstall dependensi backend dari `requirements.txt` jika library belum lengkap.
  * ✅ Memeriksa ketersediaan **FFmpeg** & **yt-dlp** di PATH dan memberikan petunjuk instalasi instan jika belum terpasang.
  * ✅ Menahan jendela terminal (`pause`) saat terjadi error agar log kesalahan tidak langsung tertutup.

---

### 🛠️ Cara 2: Menjalankan Secara Manual (Terminal / CLI)

#### 1. Persyaratan Sistem (Prerequisites)
Pastikan telah terpasang:
* **[Node.js](https://nodejs.org/)** (v18 atau lebih baru)
* **[Python](https://www.python.org/)** (v3.10 atau lebih baru)
* **FFmpeg & yt-dlp**:
  * **Windows (PowerShell):**
    ```powershell
    winget install Gyan.FFmpeg
    winget install yt-dlp.yt-dlp
    ```
  * **macOS:**
    ```bash
    brew install ffmpeg-full yt-dlp
    ```
  * **Linux:**
    ```bash
    sudo apt update && sudo apt install ffmpeg
    pip install yt-dlp
    ```

#### 2. Install Dependensi Frontend
```bash
npm install
```

#### 3. Setup Virtual Environment & Install Dependensi Backend
* **Windows (PowerShell/CMD):**
  ```powershell
  python -m venv venv
  venv\Scripts\activate
  pip install -r backend/requirements.txt
  ```
* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -r backend/requirements.txt
  ```

#### 4. Jalankan Aplikasi
Jalankan frontend dan backend sekaligus menggunakan perintah:
```bash
npm run dev
```
* **Web App (Frontend):** `http://localhost:5173`
* **API Server (Backend):** `http://localhost:8000`
* **Dokumentasi Interaktif API:** `http://localhost:8000/docs`

---

### 🐳 Cara 3: Menjalankan dengan Docker
Jika Anda menggunakan Docker dan Docker Compose:
```bash
docker-compose up --build
```
Aplikasi akan langsung online di port `8000`.

---

## 🔑 Konfigurasi API Key (Gemini & Multi-Provider AI)

1. **Google Gemini API Key (Gratis 1 Menit):**
   * Buat key di **[Google AI Studio](https://aistudio.google.com/)**.
   * Salin key dan tempelkan ke kolom **Gemini API Key** di antarmuka web, atau letakkan di `backend/.env` sebagai `GEMINI_API_KEY=AIzaSy...`.
2. **Mode Pengujian (Mock Mode):**
   * Masukkan kata `mock` pada kolom API Key untuk menguji seluruh fungsi studio tanpa kuota API!

---

## 🏗️ Analisis Implementasi OOP (Object-Oriented Programming)

Saat ini, codebase ClipVidio AI mengombinasikan **Data Modeling OOP** dengan **Functional Pipeline**:
* **Bagian yang Sudah Menerapkan OOP:**
  * Validasi payload dan tipe data menggunakan Pydantic Class Models ([`backend/schemas/analyze.py`](./backend/schemas/analyze.py), [`backend/schemas/render.py`](./backend/schemas/render.py)), seperti `ViralClip`, `HeatmapPoint`, dan `AnalyzeResponse`.
  * Objek manipulasi gambar menggunakan library Pillow (`ImageDraw.Draw`, `ImageFont.truetype`).
* **Bagian yang Masih Prosedural / Functional:**
  * Modul downloader ([`youtube_service.py`](./backend/services/youtube_service.py)) dan rendering engine ([`video_engine.py`](./backend/video_engine.py)) masih didominasi fungsi prosedural lepas (`def render_clip`, `def detect_faces`, dll).
* **Rekomendasi Refactoring ke OOP Murni (Design Patterns):**
  1. **Strategy Pattern untuk Video Downloader:**
     * `BaseVideoSource` (Interface abstrak) $\rightarrow$ `YouTubeSource`, `GoogleDriveSource`, `LocalUploadSource`.
  2. **Adapter & Factory Pattern untuk Video Encoder:**
     * `BaseVideoEncoder` $\rightarrow$ `NvidiaEncoder`, `AmdEncoder`, `IntelEncoder`, `CpuSoftwareEncoder`.
  3. **Service Class Berbasis Dependency Injection:**
     * Mengelompokkan logika bisnis ke dalam `class VideoAnalysisService`, `class FaceTrackingService`, dan `class SubtitleRenderingService` sesuai arsitektur 4-layer di [`.agents/rules/10-architecture.md`](./.agents/rules/10-architecture.md).

---

## 🌐 Analisis Fitur Multi-AI Router (OpenRouter & Gemini Multi-Key Rotation)

Untuk meningkatkan keandalan transkrip dan analisis video tanpa terbentur limit kuota (HTTP 429), arsitektur dapat ditingkatkan dengan sistem **AI Router Gateway**:

### 1. Konsep AI Router Multi-Provider (OpenRouter / Multi-Gateway)
Alih-alih hanya bergantung pada satu API key Gemini, sistem dapat menggunakan antarmuka router terpadu:
* **Integrasi OpenRouter API:** Menggunakan satu endpoint OpenAI-compatible (`https://openrouter.ai/api/v1`) untuk merouting instruksi AI ke puluhan model unggulan (Claude 3.5 Sonnet, DeepSeek V3/R1, Llama 3.3 70B, GPT-4o mini).
* **Arsitektur 9-Router Failover Matrix:**
  1. `Google Gemini 2.5 Flash` (Default: Gratis & Cepat)
  2. `Google Gemini 2.0 Flash` (Fallback tier 1)
  3. `Groq Llama-3.3-70B` (Inference super cepat < 1 detik)
  4. `OpenRouter Gateway` (Multi-model aggregator)
  5. `DeepSeek API` (Ekonomis & penalaran tajam)
  6. `OpenAI GPT-4o mini`
  7. `Anthropic Claude 3.5 Haiku`
  8. `Mistral AI / Together AI`
  9. `Local Ollama / Faster-Whisper` (100% Offline & Tanpa Kuota)

### 2. Mekanisme Multi-Key Dynamic Rotation
Seperti yang sudah diterapkan pada Supadata di [`youtube_service.py`](./backend/services/youtube_service.py), API Key Gemini dan OpenRouter dapat dikonfigurasi sebagai array atau dipisah dengan koma:
```env
GEMINI_API_KEYS=key1,key2,key3,key4
OPENROUTER_API_KEY=sk-or-v1-...
```
Jika key aktif mengalami *Quota Exceeded (HTTP 429)*, sistem secara otomatis mengalihkan request ke key berikutnya dalam putaran tanpa membuat proses analisis pengguna gagal.

---

## 🚀 Peluang Optimasi Performa Lebih Lanjut

1. **Frontend Code-Splitting & Modular Refactoring:**
   * Memecah file raksasa `src/App.tsx` (221 KB) dan `ClipStudioSection.tsx` (223 KB) menjadi komponen-komponen kecil dengan `React.lazy()` untuk memangkas waktu *First Contentful Paint (FCP)*.
2. **Optimasi Computer Vision (Frame Skipping Face Detection):**
   * Saat ini deteksi wajah memindai setiap frame video. Mengubahnya dengan memindai 1 frame setiap 3–5 frame lalu melakukan interpolasi linier bounding box akan **mempercepat render hingga 300%** dengan akurasi yang tetap mulus.
3. **Local Offline Transcription (Faster-Whisper):**
   * Menambahkan modul `faster-whisper` di backend sehingga video lokal tanpa subtitle YouTube dapat langsung ditranskrip secara offline tanpa perlu dependensi layanan cloud pihak ketiga.
4. **Asynchronous Background Task Queue:**
   * Menerapkan queue worker untuk render batch agar pemrosesan video berdurasi panjang tidak mengunci event loop server.

---

## 📄 License & Author

* **Author:** [Ahmad Arif](https://github.com/AhmadArifff)
* Distributed under the **MIT License**. Free for personal and commercial use!
