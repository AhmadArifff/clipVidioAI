# Case 3: Dual-Engine AI Router: Dynamic Multi-Key Gemini Rotation dan OpenRouter Quota Fallback

- **ID Kasus**: `case-20261009-multi-provider-ai-router-quota-fallback`
- **Kategori**: AI Architecture / Resilience
- **Keparahan**: High (Layanan analisis video gagal jika kuota Gemini habis)
- **Status**: VERIFIED
- **Reviewer**: `backend-engineer` & `tech-critic`

---

## 1. Gejala & Masalah
Analisis transkrip dan deteksi klip viral bergantung pada satu API key Google Gemini. Ketika batas kuota gratis tercapai (*ResourceExhausted 429*), seluruh fungsi AI lumpuh.

---

## 2. Akar Masalah
Tidak adanya failover otomatis ke model alternatif atau rotasi multi-kunci dinamis.

---

## 3. Solusi Tervalidasi
1. Mengembangkan kelas `AIRouter` di `backend/services/ai_service.py`.
2. Mendukung `GEMINI_API_KEYS` (daftar kunci terpisah koma) dengan rotasi dinamis saat mendeteksi error kuota.
3. Mendukung integrasi OpenRouter (`OPENROUTER_API_KEY`) dengan model berbiaya sangat rendah / gratis (DeepSeek V3/R1, LLaMA 3.3, Claude 3.5 Sonnet).
4. Menyediakan endpoint API `GET /api/ai/models` dan `GET /api/ai/provider-status` untuk inspeksi reaktif di antarmuka web.

---

## 4. Hasil Verifikasi
- Pengujian unit `scratch/test_ai_router.py` berhasil memvalidasi rotasi kunci dan fallback provider tanpa interupsi pengguna.
