# Case 2: Resolusi Parsing Sintaks Karakter Khusus Ampersand dan Asterisk pada start.bat

- **ID Kasus**: `case-20261010-batch-launcher-special-characters-crash`
- **Kategori**: DevOps / Windows Native Shell
- **Keparahan**: High (Launcher crash seketika saat double-click)
- **Status**: VERIFIED
- **Reviewer**: `qa-engineer` & `tech-critic`

---

## 1. Gejala & Masalah
Ketika pengguna mengklik dua kali file `start.bat` di File Explorer, jendela terminal Windows langsung muncul dan tertutup sendiri seketika (*auto-close*).
Ketika dijalankan via command prompt:
```
'Launch' is not recognized as an internal or external command
* was unexpected at this time.
```

---

## 2. Akar Masalah
1. Karakter ampersand `&` di baris `echo Pre-flight Check & Launch` dan `Node.js & NPM` diartikan oleh parser batch Windows (`cmd.exe`) sebagai operator pemisah perintah (*command chaining*).
2. Karakter bintang/wildcard `*` dan tanda kurung buka/tutup `()` pada baris `echo *(Pastikan mencentang "Add Python to PATH")*` yang berada di dalam blok `if (...)` merusak parser nested block sehingga memicu `* was unexpected at this time`.
3. Pemanggilan `npm run dev` tanpa keyword `call` menyebabkan proses langsung keluar tanpa melewati instruksi `pause`.

---

## 3. Solusi Tervalidasi
1. Mengganti semua karakter `&` menjadi kata `dan` atau meng-escape dengan caret `^&`.
2. Membersihkan seluruh karakter wildcard `*` dan tanda kurung dari baris `echo` di dalam blok `if (...)`.
3. Mengubah pemanggilan menjadi `call npm run dev` dan menambahkan `pause` di akhir file.

---

## 4. Hasil Verifikasi
- Pengujian via `cmd.exe /c start.bat` sukses lolos seluruh 5 tahapan pre-flight check.
- Server Vite (5173) dan FastAPI (8000) menyala serentak dengan stabil.
