import React, { useState, useEffect, useRef } from 'react';
import {
  UploadCloud,
  Layers,
  Palette,
  Check,
  Film,
  Image as ImageIcon,
  Trash2,
  AlertCircle,
  SlidersHorizontal,
  Eye
} from 'lucide-react';
import type {
  AspectRatioOption,
  BackgroundType,
  BackgroundPresetItem,
  CustomBackgroundFileItem
} from '../types';

interface BackgroundCustomizerProps {
  aspectRatio: AspectRatioOption;
  onAspectRatioChange: (ratio: AspectRatioOption) => void;
  backgroundType: BackgroundType;
  onBackgroundTypeChange: (type: BackgroundType) => void;
  backgroundValue: string;
  onBackgroundValueChange: (value: string) => void;
  backgroundFilePath?: string;
  onBackgroundFilePathChange: (path?: string) => void;
  foregroundScale: number;
  onForegroundScaleChange: (scale: number) => void;
  foregroundPositionY: number;
  onForegroundPositionYChange: (pos: number) => void;
  foregroundBorderRadius: number;
  onForegroundBorderRadiusChange: (radius: number) => void;
  foregroundShadow: boolean;
  onForegroundShadowChange: (shadow: boolean) => void;
}

const DEFAULT_PRESETS: BackgroundPresetItem[] = [
  {
    id: 'blur_ambient',
    name: 'Ambient Blur',
    category: 'ambient',
    type: 'blur',
    description: 'Video latar di-blur dinamis dan tersaturasi',
    preview_color: 'linear-gradient(135deg, #1e293b, #0f172a)',
    value: 'blurred'
  },
  {
    id: 'obsidian_black',
    name: 'Obsidian Black',
    category: 'color',
    type: 'color',
    description: 'Hitam pekat minimalis netral',
    preview_color: '#09090b',
    value: '#09090b'
  },
  {
    id: 'deep_slate',
    name: 'Deep Slate',
    category: 'color',
    type: 'color',
    description: 'Warna zinc slate studio modern',
    preview_color: '#18181b',
    value: '#18181b'
  },
  {
    id: 'navy_midnight',
    name: 'Midnight Navy',
    category: 'color',
    type: 'color',
    description: 'Biru malam gelap sinematik',
    preview_color: '#0f172a',
    value: '#0f172a'
  },
  {
    id: 'gradient_neon_indigo',
    name: 'Neon Indigo',
    category: 'gradient',
    type: 'gradient',
    description: 'Gradasi indigo violet elektrik',
    preview_color: 'linear-gradient(180deg, #1e1b4b 0%, #0f172a 100%)',
    value: 'indigo_dark',
    c0: '#1e1b4b',
    c1: '#0f172a'
  },
  {
    id: 'gradient_cyber_emerald',
    name: 'Cyber Emerald',
    category: 'gradient',
    type: 'gradient',
    description: 'Gradasi hijau zamrud teknologi tinggi',
    preview_color: 'linear-gradient(180deg, #064e3b 0%, #022c22 100%)',
    value: 'cyber_emerald',
    c0: '#064e3b',
    c1: '#022c22'
  },
  {
    id: 'gradient_sunset_ember',
    name: 'Sunset Ember',
    category: 'gradient',
    type: 'gradient',
    description: 'Gradasi senja tembaga hangat',
    preview_color: 'linear-gradient(180deg, #7c2d12 0%, #451a03 100%)',
    value: 'sunset_ember',
    c0: '#7c2d12',
    c1: '#451a03'
  },
  {
    id: 'minecraft_parkour',
    name: 'Minecraft Parkour',
    category: 'motion',
    type: 'preset',
    description: 'Gameplay parkour balok vertikal viral',
    preview_color: 'linear-gradient(135deg, #15803d, #166534)',
    value: 'minecraft_parkour',
    media_file: 'minecraft_parkour.mp4'
  },
  {
    id: 'subway_surfers',
    name: 'Subway Runner',
    category: 'motion',
    type: 'preset',
    description: 'Gameplay subway runner loop kecepatan tinggi',
    preview_color: 'linear-gradient(135deg, #eab308, #ca8a04)',
    value: 'subway_surfers',
    media_file: 'subway_surfers.mp4'
  },
  {
    id: 'gta_mega_ramp',
    name: 'GTA Mega Ramp',
    category: 'motion',
    type: 'preset',
    description: 'Aksi stunt mobil ramp GTA 5 sinematik',
    preview_color: 'linear-gradient(135deg, #0284c7, #0369a1)',
    value: 'gta_mega_ramp',
    media_file: 'gta_mega_ramp.mp4'
  },
  {
    id: 'synthwave_neon_grid',
    name: 'Synthwave Grid',
    category: 'motion',
    type: 'preset',
    description: 'Loop wireframe jalan neon 80s retro wave',
    preview_color: 'linear-gradient(135deg, #d946ef, #6366f1)',
    value: 'synthwave_grid',
    media_file: 'synthwave_grid.mp4'
  },
  {
    id: 'lofi_aesthetic_rain',
    name: 'Lo-Fi Rainy Window',
    category: 'motion',
    type: 'preset',
    description: 'Suasana jendela hujan tenang estetis',
    preview_color: 'linear-gradient(135deg, #475569, #1e293b)',
    value: 'lofi_rain',
    media_file: 'lofi_rain.mp4'
  }
];

export const BackgroundCustomizer: React.FC<BackgroundCustomizerProps> = ({
  aspectRatio,
  onAspectRatioChange: _onAspectRatioChange,
  backgroundType,
  onBackgroundTypeChange,
  backgroundValue,
  onBackgroundValueChange,
  backgroundFilePath,
  onBackgroundFilePathChange,
  foregroundScale,
  onForegroundScaleChange,
  foregroundPositionY,
  onForegroundPositionYChange,
  foregroundBorderRadius,
  onForegroundBorderRadiusChange,
  foregroundShadow,
  onForegroundShadowChange
}) => {
  const [activeTab, setActiveTab] = useState<'presets' | 'colors' | 'upload' | 'layout'>('presets');
  const [presets, setPresets] = useState<BackgroundPresetItem[]>(DEFAULT_PRESETS);
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [uploads, setUploads] = useState<CustomBackgroundFileItem[]>([]);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Ambil preset dari backend saat render
  useEffect(() => {
    let isMounted = true;
    fetch('/api/backgrounds/presets')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (isMounted && data && Array.isArray(data.presets) && data.presets.length > 0) {
          setPresets(data.presets);
        }
      })
      .catch(() => {
        // Gunakan fallback default presets jika server belum aktif
      });

    fetchUploadsList();

    return () => {
      isMounted = false;
    };
  }, []);

  const fetchUploadsList = () => {
    fetch('/api/backgrounds/uploads')
      .then((res) => (res.ok ? res.json() : null))
      .then((data) => {
        if (data && Array.isArray(data.uploads)) {
          setUploads(data.uploads);
        }
      })
      .catch(() => {});
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadProgress(10);
    setUploadError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadProgress(40);
      const res = await fetch('/api/backgrounds/upload', {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Gagal mengunggah file background');
      }

      setUploadProgress(90);
      const data = await res.json();
      setUploadProgress(100);

      // Otomatis aktifkan custom upload ini
      onBackgroundTypeChange('custom_upload');
      onBackgroundValueChange(data.file_path);
      onBackgroundFilePathChange(data.file_path);

      fetchUploadsList();
    } catch (err: any) {
      setUploadError(err.message || 'Gagal mengunggah media');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const handleDeleteUpload = async (fileName: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const res = await fetch(`/api/backgrounds/uploads/${fileName}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        if (backgroundFilePath?.includes(fileName)) {
          onBackgroundTypeChange('blur');
          onBackgroundValueChange('blurred');
          onBackgroundFilePathChange(undefined);
        }
        fetchUploadsList();
      }
    } catch {
      // Ignored
    }
  };

  const filteredPresets = presets.filter((p) => {
    if (categoryFilter === 'all') return true;
    return p.category === categoryFilter;
  });

  return (
    <div className="bg-customizer-card">
      {/* Header */}
      <div className="bg-customizer-header">
        <div className="bg-customizer-title-wrap">
          <div className="bg-customizer-title">
            <Palette size={18} />
            <span>Kustomisasi Latar Belakang & Tata Letak</span>
          </div>
          <p className="bg-customizer-desc">
            Pilih video animasi latar, gradasi warna sinematik, efek ambient blur, atau unggah media kustom Anda sendiri.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
          <span className="badge" style={{ fontSize: '0.72rem', padding: '0.2rem 0.55rem' }}>
            Kanvas: {aspectRatio}
          </span>
        </div>
      </div>

      {/* Main Mode Tabs */}
      <div className="bg-customizer-tabs">
        <button
          type="button"
          onClick={() => setActiveTab('presets')}
          className={`bg-customizer-tab-btn ${activeTab === 'presets' ? 'active' : ''}`}
        >
          <Film size={15} />
          <span>Preset Gameplay & Motion</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('colors')}
          className={`bg-customizer-tab-btn ${activeTab === 'colors' ? 'active' : ''}`}
        >
          <Palette size={15} />
          <span>Solid & Gradasi</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`bg-customizer-tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
        >
          <UploadCloud size={15} />
          <span>Unggah Media Kustom</span>
          {uploads.length > 0 && (
            <span className="bg-customizer-badge">{uploads.length}</span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('layout')}
          className={`bg-customizer-tab-btn ${activeTab === 'layout' ? 'active' : ''}`}
        >
          <SlidersHorizontal size={15} />
          <span>Layout Foreground</span>
        </button>
      </div>

      {/* Tab 1: Presets Catalog */}
      {activeTab === 'presets' && (
        <div>
          <div className="bg-customizer-subfilter">
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Pilih Animasi Loop Latar:</span>
            <div className="bg-customizer-pills">
              {['all', 'motion', 'ambient'].map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategoryFilter(cat)}
                  className={`bg-customizer-pill-btn ${categoryFilter === cat ? 'active' : ''}`}
                >
                  {cat === 'all' ? 'Semua' : cat}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-customizer-grid">
            {filteredPresets.map((preset) => {
              const isSelected =
                (backgroundType === preset.type || (preset.type === 'preset' && backgroundType === 'preset')) &&
                backgroundValue === preset.value;

              return (
                <div
                  key={preset.id}
                  onClick={() => {
                    onBackgroundTypeChange(preset.type as BackgroundType);
                    onBackgroundValueChange(preset.value);
                    onBackgroundFilePathChange(preset.media_file);
                  }}
                  className={`bg-customizer-card-item ${isSelected ? 'active' : ''}`}
                >
                  <div
                    className="bg-customizer-thumb-box"
                    style={{ background: preset.preview_color }}
                  >
                    {isSelected && (
                      <div className="bg-customizer-check-badge">
                        <Check size={11} strokeWidth={3} />
                      </div>
                    )}
                    {preset.type === 'blur' ? (
                      <Eye size={20} color="rgba(255,255,255,0.85)" />
                    ) : (
                      <Film size={20} color="rgba(255,255,255,0.85)" />
                    )}
                  </div>
                  <div className="bg-customizer-card-meta">
                    <div className="bg-customizer-card-name" title={preset.name}>{preset.name}</div>
                    <div className="bg-customizer-card-desc" title={preset.description}>{preset.description}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Solid Colors & Gradients */}
      {activeTab === 'colors' && (
        <div>
          <div className="bg-customizer-subfilter">
            <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Pilihan Gradasi & Warna Dasar Studio:</span>
          </div>
          <div className="bg-customizer-grid">
            {presets
              .filter((p) => p.type === 'color' || p.type === 'gradient')
              .map((item) => {
                const isSelected = backgroundValue === item.value;
                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onBackgroundTypeChange(item.type as BackgroundType);
                      onBackgroundValueChange(item.value);
                      onBackgroundFilePathChange(undefined);
                    }}
                    className={`bg-customizer-card-item ${isSelected ? 'active' : ''}`}
                  >
                    <div
                      className="bg-customizer-thumb-box"
                      style={{ background: item.preview_color }}
                    >
                      {isSelected && (
                        <div className="bg-customizer-check-badge">
                          <Check size={11} strokeWidth={3} />
                        </div>
                      )}
                    </div>
                    <div className="bg-customizer-card-meta">
                      <div className="bg-customizer-card-name" title={item.name}>{item.name}</div>
                      <div className="bg-customizer-card-desc" title={item.description}>{item.description}</div>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Tab 3: Custom Uploads */}
      {activeTab === 'upload' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          {/* Dropzone Upload */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="bg-customizer-dropzone"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/webm,video/quicktime,image/png,image/jpeg,image/webp"
              onChange={handleFileUpload}
              style={{ display: 'none' }}
            />
            <UploadCloud size={30} color="var(--primary, #a855f7)" />
            <div className="bg-customizer-dropzone-title">
              Klik atau Seret Media Latar Belakang ke Sini
            </div>
            <div className="bg-customizer-dropzone-subtitle">
              Mendukung video MP4, WEBM, MOV (maks 500MB) atau gambar PNG, JPG, WEBP (maks 30MB)
            </div>

            {isUploading && (
              <div className="bg-customizer-progress-wrap">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#c084fc' }}>
                  <span>Mengunggah...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="bg-customizer-progress-bar">
                  <div
                    className="bg-customizer-progress-fill"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {uploadError && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: '#f87171', fontSize: '0.74rem', marginTop: '0.4rem' }}>
                <AlertCircle size={15} />
                <span>{uploadError}</span>
              </div>
            )}
          </div>

          {/* List Media Unggahan */}
          {uploads.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                Media Unggahan Anda ({uploads.length}):
              </div>
              <div className="bg-customizer-grid">
                {uploads.map((up) => {
                  const isSelected =
                    backgroundType === 'custom_upload' &&
                    (backgroundValue === up.file_path || backgroundFilePath === up.file_path);

                  return (
                    <div
                      key={up.file_name}
                      onClick={() => {
                        onBackgroundTypeChange('custom_upload');
                        onBackgroundValueChange(up.file_path);
                        onBackgroundFilePathChange(up.file_path);
                      }}
                      className={`bg-customizer-card-item ${isSelected ? 'active' : ''}`}
                    >
                      <div
                        className="bg-customizer-thumb-box"
                        style={{ background: 'rgba(255,255,255,0.05)' }}
                      >
                        {up.media_type === 'video' ? (
                          <Film size={22} color="var(--primary, #a855f7)" />
                        ) : (
                          <ImageIcon size={22} color="#10b981" />
                        )}
                        {isSelected && (
                          <div className="bg-customizer-check-badge">
                            <Check size={11} strokeWidth={3} />
                          </div>
                        )}
                        <button
                          type="button"
                          onClick={(e) => handleDeleteUpload(up.file_name, e)}
                          title="Hapus media ini"
                          style={{
                            position: 'absolute',
                            bottom: '3px',
                            right: '3px',
                            background: 'rgba(239, 68, 68, 0.3)',
                            border: '1px solid rgba(239, 68, 68, 0.4)',
                            color: '#fca5a5',
                            borderRadius: '4px',
                            padding: '2px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                          }}
                        >
                          <Trash2 size={12} />
                        </button>
                      </div>
                      <div className="bg-customizer-card-meta">
                        <div className="bg-customizer-card-name" title={up.file_name}>{up.file_name}</div>
                        <div className="bg-customizer-card-desc">
                          {up.media_type.toUpperCase()} • {(up.file_size_bytes / (1024 * 1024)).toFixed(1)} MB
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Foreground Position & Scale Controls */}
      {activeTab === 'layout' && (
        <div className="bg-customizer-layout-grid">
          {/* Scale Slider */}
          <div className="bg-customizer-slider-group">
            <div className="bg-customizer-slider-label-row">
              <span>Skala Video Foreground</span>
              <span className="bg-customizer-slider-val">{foregroundScale}%</span>
            </div>
            <input
              type="range"
              min="40"
              max="100"
              step="1"
              value={foregroundScale}
              onChange={(e) => onForegroundScaleChange(Number(e.target.value))}
              className="studio-slider"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              <span>Kecil (40%)</span>
              <span>Standar (100% Penuh)</span>
            </div>
          </div>

          {/* Vertical Position Y */}
          <div className="bg-customizer-slider-group">
            <div className="bg-customizer-slider-label-row">
              <span>Posisi Vertikal (Pusat Y)</span>
              <span className="bg-customizer-slider-val">{foregroundPositionY}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              step="1"
              value={foregroundPositionY}
              onChange={(e) => onForegroundPositionYChange(Number(e.target.value))}
              className="studio-slider"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              <span>Atas (10%)</span>
              <span>Tengah (50%)</span>
              <span>Bawah (90%)</span>
            </div>
          </div>

          {/* Border Radius */}
          <div className="bg-customizer-slider-group">
            <div className="bg-customizer-slider-label-row">
              <span>Sudut Melengkung (Corner Radius)</span>
              <span className="bg-customizer-slider-val">{foregroundBorderRadius} px</span>
            </div>
            <input
              type="range"
              min="0"
              max="36"
              step="2"
              value={foregroundBorderRadius}
              onChange={(e) => onForegroundBorderRadiusChange(Number(e.target.value))}
              className="studio-slider"
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: 'var(--text-muted)' }}>
              <span>Tegak (0px)</span>
              <span>Melengkung Halus (36px)</span>
            </div>
          </div>

          {/* Drop Shadow Switch */}
          <div className="bg-customizer-switch-card">
            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--text-primary)' }}>Efek Bayangan (Drop Shadow)</div>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '2px' }}>Menambah kedalaman visual di atas background</div>
            </div>
            <input
              type="checkbox"
              checked={foregroundShadow}
              onChange={(e) => onForegroundShadowChange(e.target.checked)}
              style={{ width: '16px', height: '16px', accentColor: 'var(--primary, #a855f7)', cursor: 'pointer' }}
            />
          </div>
        </div>
      )}

      {/* Summary Indicator Bar */}
      <div className="bg-customizer-footer">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.45rem' }}>
          <Layers size={14} color="var(--primary, #a855f7)" />
          <span>
            Latar Aktif:{' '}
            <strong style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>
              {backgroundType === 'custom_upload'
                ? 'Unggahan Kustom'
                : backgroundType === 'blur'
                ? 'Ambient Blur'
                : backgroundValue}
            </strong>
          </span>
        </div>
        <div>
          Kanvas: <strong style={{ color: 'var(--text-primary)' }}>{aspectRatio}</strong> • Foreground:{' '}
          <strong style={{ color: 'var(--text-primary)' }}>{foregroundScale}%</strong>
        </div>
      </div>
    </div>
  );
};
