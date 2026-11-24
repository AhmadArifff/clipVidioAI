# Domain 04: Kontrak 5-Titik `RenderSettings`

Setiap parameter render baru **WAJIB** terdaftar konsisten di 5 file berikut:

| Titik | File | Gaya Penamaan | Catatan |
| :---: | :--- | :--- | :--- |
| **1** | `apps/web/src/types.ts` | `camelCase` (`RenderSettings`) | Tipe TypeScript + tipe union opsi baru |
| **2** | `apps/web/src/components/ClipStudioSection.tsx` | `camelCase` (`StudioPreferences`, state, `handleResetToDefaults`, `handleLaunch`) | Simpan ke `localStorage` & kirim ke `onStartRender` |
| **3** | `apps/web/src/App.tsx` | `camelCase` -> `snake_case` (`handleStartBatchRender`) | Mapping payload JSON ke `POST /api/render-batch` |
| **4** | `apps/api/backend/schemas/render.py` | `snake_case` (`RenderSettingsModel`) | Default aman + `ConfigDict(extra="ignore")` |
| **5** | `apps/api/backend/services/render_service.py` + `video_engine.py` | `snake_case` | Wajib diteruskan di **KEDUA** jalur: `render_single_batch_clip` DAN `render_merged_batch_clips`! |

### Contoh Parameter Terbaru (M16 & M17):
* Reaction Cam PIP: `reactionCamEnabled` <-> `reaction_cam_enabled`, `reactionCamFilePath` <-> `reaction_cam_file_path`, `reactionCamPosition` <-> `reaction_cam_position`, `reactionCamSize` <-> `reaction_cam_size`, `reactionCamShape` <-> `reaction_cam_shape`, `reactionCamBorderColor` <-> `reaction_cam_border_color`, `reactionCamMuteAudio` <-> `reaction_cam_mute_audio`.
* Smart Silence Jumpcut (Paket B): `silenceCutMode` <-> `silence_cut_mode` (`"off" | "natural" | "snappy"`).
* High-Contrast Caption Preset (Paket B): `captionStyle = "high_contrast_box"`.
