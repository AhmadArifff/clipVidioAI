# Standar Keamanan API Keys, Cookies YouTube & Upload Media

1. **Isolasi Secrets**:
   * Kunci API (`GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `SUPADATA_API_KEY`) dan URL proxy hanya disimpan di `apps/api/backend/.env` (yang di-ignore Git) atau dikirim lewat request header/body dari LocalStorage browser user tanpa dicetak ke log server.
   * Format contoh di `.env.template` tidak boleh menyerupai token rahasia valid agar bebas dari *GitHub Secret Scanning false-positive*.
2. **Cookies YouTube**:
   * Cookies yang dikirim dari UI dinormalisasi ke format Netscape via `normalize_to_netscape()` dan ditulis sementara menggunakan `ephemeral_cookies_file` yang otomatis dihapus pada blok `finally`.
3. **Keamanan File Upload**:
   * Semua endpoint upload di `routers/media.py`, `routers/audio.py`, dan `routers/backgrounds.py` wajib:
     * Memeriksa ekstensi file pada daftar izin (*allowlist*).
     * Membatasi ukuran file maksimal (misal 500 MB untuk video reaksi, 50 MB untuk gambar/audio).
     * Men-sanitasi nama file untuk endpoint `GET` (`os.path.basename` / `Path(file_name).name`) dan memastikan path final tetap berada di dalam direktori target.
4. **Prompt Injection Hygiene**:
   * Teks transkrip YouTube dari internet diperlakukan murni sebagai data input bagi AI analyzer (`analyze.py`), bukan instruksi sistem.
