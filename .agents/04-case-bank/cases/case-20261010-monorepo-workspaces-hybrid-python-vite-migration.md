# Case: Arsitektur Monorepo Hybrid Node.js Workspaces dan FastAPI Python

**ID**: `case-20261010-monorepo-workspaces-hybrid-python-vite-migration`  
**Proyek**: clipVidioAI  
**Kategori**: architecture / devops  
**Tingkat Keparahan**: High  
**Status**: VERIFIED  
**Reviewers**: `backend-engineer`, `qa-engineer`, `tech-critic`  
**Tanggal**: 2026-10-10  

---

## 1. Konteks & Deskripsi Masalah

Pada arsitektur awal, proyek ClipVidio AI menggabungkan kode frontend Vite (`src/`) dan backend Python (`backend/`) dalam satu direktori root yang padat. Seiring penambahan fitur custom background, preset rendering, dan pustaka komponen ikon `lucide-react`, tim membutuhkan modularitas Monorepo terstandar:
- Pemisahan independen antara antarmuka web (`apps/web`), API server (`apps/api`), dan kontrak tipe data bersama (`packages/shared`).
- **Tantangan Utama**:
  1. Migrasi ke monorepo sering mematahkan launcher native Windows (`start.bat` dan `update.bat`) yang biasa digunakan pengguna non-developer dengan 1-klik.
  2. Python `import backend...` rentan mengalami `ModuleNotFoundError` jika `PYTHONPATH` dan current working directory bergeser saat dipindah ke `apps/api/backend`.
  3. Pada TypeScript 6.0+, opsi `baseUrl: "."` telah di-deprecate saat menggunakan bundler resolution mode (`moduleResolution: "bundler"`).
  4. Server FastAPI pada mode produksi perlu menemukan bundle build `dist/index.html` yang kini dihasilkan di `apps/web/dist/`.

---

## 2. Analisis Akar Masalah (Root Cause)

1. **Python Path Resolution**: Modul FastAPI menggunakan konvensi absolut `from backend.config import logger`. Saat folder `backend/` dipindahkan ke dalam `apps/api/backend`, Python yang dijalankan dari root direktori tidak secara otomatis menyertakan `apps/api` dalam `sys.path`.
2. **TypeScript Deprecation Warning (TS5101)**: Penambahan path mapping untuk `@clipvidio/shared` dengan `baseUrl: "."` memicu kegagalan build `error TS5101: Option 'baseUrl' is deprecated`.
3. **SPA Static Files Mount**: `backend/main.py` melakukan hardcode path `dist_dir = Path(__file__).resolve().parent.parent / "dist"`, yang gagal jika frontend di-build di dalam `apps/web/dist/`.

---

## 3. Solusi & Pola Implementasi (Verified Architecture Pattern)

### 3.1 Struktur Direktori Monorepo
```
Clipper-Vidio-YT/
├── apps/
│   ├── web/                     # Frontend Vite + React 19 + TypeScript (@clipvidio/web)
│   └── api/                     # Backend FastAPI Python (@clipvidio/api)
├── packages/
│   └── shared/                  # Shared TypeScript types & konstanta (@clipvidio/shared)
├── .agents/                     # Tata kelola session-state & Case-Bank
├── scripts/
│   └── start-backend.js         # Intelligent multi-path Python launcher
├── start.bat                    # One-click Windows runner (root proxy)
└── package.json                 # Root npm workspaces ("apps/*", "packages/*")
```

### 3.2 Root NPM Workspaces & Script Proxy
Root `package.json` mendelegasikan tugas ke masing-masing workspace secara transparan:
```json
{
  "name": "clipvidio-ai-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "concurrently --prefix \"[{name}]\" --names \"frontend,backend\" -c \"cyan,magenta\" \"npm run dev-frontend\" \"npm run dev-backend\"",
    "dev-frontend": "npm run dev -w @clipvidio/web",
    "dev-backend": "node scripts/start-backend.js",
    "build": "npm run build -w @clipvidio/web"
  }
}
```

### 3.3 Dynamic PYTHONPATH & Reload-Dir Harmonizer (`scripts/start-backend.js`)
Menyediakan path kandidat yang otomatis mendeteksi apakah backend berada di root atau `apps/api`:
```javascript
const rootDir = path.resolve(__dirname, '..');
const apiDir = path.join(rootDir, 'apps', 'api');
const apiBackendDir = path.join(apiDir, 'backend');
const backendDir = fs.existsSync(apiBackendDir) ? apiBackendDir : path.join(rootDir, 'backend');

const pyPathList = [rootDir, apiDir, backendDir].filter((p) => fs.existsSync(p));
const backendEnv = {
  ...process.env,
  PYTHONPATH: pyPathList.join(path.delimiter)
};
```

### 3.4 Multi-Candidate SPA Static Files Mount (`apps/api/backend/main.py`)
Mendukung penemuan bundle `dist` dari lokasi monorepo maupun legacy root:
```python
_dist_candidates = [
    Path(__file__).resolve().parent.parent.parent / "web" / "dist",
    Path(__file__).resolve().parent.parent.parent.parent / "apps" / "web" / "dist",
    Path(__file__).resolve().parent.parent / "dist",
    Path(__file__).resolve().parent.parent.parent / "dist"
]
dist_dir = next((d for d in _dist_candidates if d.exists() and (d / "index.html").exists()), None)
```

---

## 4. Hasil Verifikasi & Pengujian

- **Kompilasi TypeScript (`npm run build`)**: Lulus 100% (749ms) menghasilkan bundle produksi `apps/web/dist`.
- **Kompilasi Python (`python -m compileall apps/api/backend`)**: Lulus 100% tanpa syntax/import error.
- **Uji Runtime Backend**: Uvicorn berhasil boot pada `http://127.0.0.1:8000`, mendeteksi reload-dir `apps/api/backend`, dan sukses me-mount SPA frontend.
- **Backward-Compatibility**: Pengguna tetap dapat menjalankan aplikasi dengan perintah `start.bat` atau `npm run dev` di root folder tanpa perlu mempelajari perintah monorepo baru.
