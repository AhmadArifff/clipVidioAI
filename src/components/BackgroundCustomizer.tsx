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
  onAspectRatioChange,
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
    <div className="bg-zinc-900/90 border border-zinc-800 rounded-xl p-5 shadow-xl text-zinc-100 space-y-5">
      {/* Header & Aspect Ratio Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-800/80 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <Palette className="w-5 h-5 text-indigo-400" />
            <h3 className="font-semibold text-base text-zinc-100">Kustomisasi Latar Belakang & Rasio</h3>
          </div>
          <p className="text-xs text-zinc-400 mt-1">
            Pilih rasio kanvas, video latar, gradasi sinematik, atau unggah media kustom Anda sendiri.
          </p>
        </div>

        {/* Aspect Ratio Pills */}
        <div className="flex items-center gap-1.5 bg-zinc-950/80 p-1.5 rounded-lg border border-zinc-800">
          {(
            [
              { id: '9:16', label: '9:16 Shorts' },
              { id: '1:1', label: '1:1 Square' },
              { id: '4:3', label: '4:3 Classic' },
              { id: '16:9', label: '16:9 Wide' }
            ] as const
          ).map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onAspectRatioChange(item.id)}
              className={`px-3 py-1.5 rounded text-xs font-medium transition-all ${
                aspectRatio === item.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60'
              }`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Mode Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-zinc-800/60 pb-3">
        <button
          type="button"
          onClick={() => setActiveTab('presets')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'presets'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <Film className="w-4 h-4" />
          <span>Preset Gameplay & Motion</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('colors')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'colors'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <Palette className="w-4 h-4" />
          <span>Solid & Gradasi</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('upload')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'upload'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <UploadCloud className="w-4 h-4" />
          <span>Unggah Media Kustom</span>
          {uploads.length > 0 && (
            <span className="ml-1 px-1.5 py-0.2 bg-zinc-800 text-[10px] rounded-full text-zinc-300">
              {uploads.length}
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveTab('layout')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'layout'
              ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
              : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/50'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Layout Foreground</span>
        </button>
      </div>

      {/* Tab 1: Presets Catalog */}
      {activeTab === 'presets' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-zinc-400">
            <span className="font-medium text-zinc-300">Pilih Animasi Loop Latar:</span>
            <div className="flex items-center gap-1">
              {['all', 'motion', 'ambient'].map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setCategoryFilter(cat)}
                  className={`px-2.5 py-1 rounded text-[11px] capitalize ${
                    categoryFilter === cat
                      ? 'bg-zinc-800 text-zinc-100 font-semibold'
                      : 'text-zinc-500 hover:text-zinc-300'
                  }`}
                >
                  {cat === 'all' ? 'Semua' : cat}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 max-h-72 overflow-y-auto pr-1">
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
                  className={`relative p-3 rounded-lg border text-left cursor-pointer transition-all flex flex-col justify-between ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-950/30 ring-1 ring-indigo-500'
                      : 'border-zinc-800 bg-zinc-950/40 hover:border-zinc-700 hover:bg-zinc-900/60'
                  }`}
                >
                  <div
                    className="w-full h-14 rounded-md mb-2 flex items-center justify-center relative overflow-hidden shadow-inner"
                    style={{ background: preset.preview_color }}
                  >
                    {isSelected && (
                      <div className="absolute top-1 right-1 bg-indigo-600 rounded-full p-0.5 text-white shadow">
                        <Check className="w-3 h-3" />
                      </div>
                    )}
                    {preset.type === 'blur' ? (
                      <Eye className="w-5 h-5 text-zinc-300/80 drop-shadow" />
                    ) : (
                      <Film className="w-5 h-5 text-white/70 drop-shadow" />
                    )}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-zinc-200 truncate">{preset.name}</div>
                    <div className="text-[10px] text-zinc-400 line-clamp-1 mt-0.5">{preset.description}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: Solid Colors & Gradients */}
      {activeTab === 'colors' && (
        <div className="space-y-4">
          <div className="text-xs text-zinc-300 font-medium">Pilihan Gradasi & Warna Dasar Studio:</div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
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
                    className={`p-3 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'border-indigo-500 bg-indigo-950/30 ring-1 ring-indigo-500'
                        : 'border-zinc-800 bg-zinc-950/40 hover:border-zinc-700'
                    }`}
                  >
                    <div
                      className="w-full h-12 rounded-md mb-2 flex items-center justify-center relative shadow-inner"
                      style={{ background: item.preview_color }}
                    >
                      {isSelected && (
                        <div className="absolute top-1 right-1 bg-indigo-600 rounded-full p-0.5 text-white shadow">
                          <Check className="w-3 h-3" />
                        </div>
                      )}
                    </div>
                    <div className="text-xs font-semibold text-zinc-200">{item.name}</div>
                    <div className="text-[10px] text-zinc-400 truncate">{item.description}</div>
                  </div>
                );
              })}
          </div>
        </div>
      )}

      {/* Tab 3: Custom Uploads */}
      {activeTab === 'upload' && (
        <div className="space-y-4">
          {/* Dropzone Upload */}
          <div
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-zinc-700 hover:border-indigo-500 bg-zinc-950/50 hover:bg-zinc-900/40 p-6 rounded-xl text-center cursor-pointer transition-all"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/webm,video/quicktime,image/png,image/jpeg,image/webp"
              onChange={handleFileUpload}
              className="hidden"
            />
            <UploadCloud className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
            <div className="text-sm font-semibold text-zinc-200">
              Klik atau Seret Media Latar Belakang ke Sini
            </div>
            <div className="text-xs text-zinc-400 mt-1">
              Mendukung video MP4, WEBM, MOV (maks 500MB) atau gambar PNG, JPG, WEBP (maks 30MB)
            </div>

            {isUploading && (
              <div className="mt-4 max-w-xs mx-auto">
                <div className="flex justify-between text-xs text-indigo-400 mb-1">
                  <span>Mengunggah...</span>
                  <span>{uploadProgress}%</span>
                </div>
                <div className="w-full bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}

            {uploadError && (
              <div className="mt-3 flex items-center justify-center gap-1.5 text-xs text-rose-400">
                <AlertCircle className="w-4 h-4" />
                <span>{uploadError}</span>
              </div>
            )}
          </div>

          {/* List Media Unggahan */}
          {uploads.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-semibold text-zinc-300">Media Unggahan Anda ({uploads.length}):</div>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-56 overflow-y-auto pr-1">
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
                      className={`relative p-2.5 rounded-lg border text-left cursor-pointer transition-all flex flex-col justify-between ${
                        isSelected
                          ? 'border-indigo-500 bg-indigo-950/30 ring-1 ring-indigo-500'
                          : 'border-zinc-800 bg-zinc-950/40 hover:border-zinc-700'
                      }`}
                    >
                      <div className="w-full h-16 rounded bg-zinc-900 mb-2 flex items-center justify-center relative overflow-hidden">
                        {up.media_type === 'video' ? (
                          <Film className="w-6 h-6 text-indigo-400" />
                        ) : (
                          <ImageIcon className="w-6 h-6 text-emerald-400" />
                        )}
                        {isSelected && (
                          <div className="absolute top-1 right-1 bg-indigo-600 rounded-full p-0.5 text-white shadow">
                            <Check className="w-3 h-3" />
                          </div>
                        )}
                        <button
                          type="button"
                          onClick={(e) => handleDeleteUpload(up.file_name, e)}
                          title="Hapus media ini"
                          className="absolute bottom-1 right-1 p-1 bg-rose-950/80 hover:bg-rose-800 text-rose-300 rounded text-[10px]"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                      <div className="text-xs font-medium text-zinc-200 truncate">{up.file_name}</div>
                      <div className="text-[10px] text-zinc-500 uppercase mt-0.5">
                        {up.media_type} • {(up.file_size_bytes / (1024 * 1024)).toFixed(1)} MB
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-2">
          {/* Scale Slider */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-zinc-300 font-medium">Skala Video Foreground</span>
              <span className="text-indigo-400 font-semibold">{foregroundScale}%</span>
            </div>
            <input
              type="range"
              min="40"
              max="100"
              step="1"
              value={foregroundScale}
              onChange={(e) => onForegroundScaleChange(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500">
              <span>Kecil (40%)</span>
              <span>Standar (100% Penuh)</span>
            </div>
          </div>

          {/* Vertical Position Y */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-zinc-300 font-medium">Posisi Vertikal (Pusat Y)</span>
              <span className="text-indigo-400 font-semibold">{foregroundPositionY}%</span>
            </div>
            <input
              type="range"
              min="10"
              max="90"
              step="1"
              value={foregroundPositionY}
              onChange={(e) => onForegroundPositionYChange(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500">
              <span>Atas (10%)</span>
              <span>Tengah (50%)</span>
              <span>Bawah (90%)</span>
            </div>
          </div>

          {/* Border Radius */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <span className="text-zinc-300 font-medium">Sudut Melengkung (Corner Radius)</span>
              <span className="text-indigo-400 font-semibold">{foregroundBorderRadius} px</span>
            </div>
            <input
              type="range"
              min="0"
              max="36"
              step="2"
              value={foregroundBorderRadius}
              onChange={(e) => onForegroundBorderRadiusChange(Number(e.target.value))}
              className="w-full accent-indigo-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-zinc-500">
              <span>Tegak (0px)</span>
              <span>Melengkung Halus (36px)</span>
            </div>
          </div>

          {/* Drop Shadow Switch */}
          <div className="flex items-center justify-between p-3 rounded-lg border border-zinc-800 bg-zinc-950/40">
            <div>
              <div className="text-xs font-semibold text-zinc-200">Efek Bayangan (Drop Shadow)</div>
              <div className="text-[10px] text-zinc-400">Menambah kedalaman visual di atas background</div>
            </div>
            <input
              type="checkbox"
              checked={foregroundShadow}
              onChange={(e) => onForegroundShadowChange(e.target.checked)}
              className="w-4 h-4 accent-indigo-500 rounded cursor-pointer"
            />
          </div>
        </div>
      )}

      {/* Summary Indicator Bar */}
      <div className="flex items-center justify-between text-xs bg-zinc-950/60 p-2.5 rounded-lg border border-zinc-800/80 text-zinc-400">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-indigo-400" />
          <span>
            Latar Aktif:{' '}
            <strong className="text-zinc-200 capitalize">
              {backgroundType === 'custom_upload'
                ? 'Unggahan Kustom'
                : backgroundType === 'blur'
                ? 'Ambient Blur'
                : backgroundValue}
            </strong>
          </span>
        </div>
        <div className="text-[11px] text-zinc-500">
          Kanvas: <span className="text-zinc-300 font-medium">{aspectRatio}</span> • Foreground:{' '}
          <span className="text-zinc-300 font-medium">{foregroundScale}%</span>
        </div>
      </div>
    </div>
  );
};
