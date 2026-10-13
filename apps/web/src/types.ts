export interface HeatmapPoint {
  start_time: number;
  end_time: number;
  value: number;
}

export interface TranscriptLine {
  start: number;
  end: number;
  text: string;
  engagement?: number;
}

export interface SocialCopyDeck {
  hook_titles: {
    curiosity: string;
    contrarian: string;
    action: string;
  };
  captions: {
    tiktok_reels: string;
    youtube_shorts: string;
  };
  hashtags: string[];
  hashtags_formatted: string;
}

export interface ViralClip {
  title: string;
  start_time: number;
  end_time: number;
  hook_time?: number;
  virality_score: number;
  key_quotes: string[];
  transcript: string;
  title_suggestion?: string;
  caption_suggestion?: string;
  hashtag_suggestion?: string;
  // v3.4.0 AI Social Copywriting Pack
  copy_deck?: SocialCopyDeck;
  // v3.5.0 AI Smart Clip Settings Recommendation
  recommendation?: ClipSettingsRecommendation;
  custom_title?: string;
  spoken_text?: string;
  clip_index?: number;
}

export type ViralArchetypeKey = 'beast_hype' | 'hormozi_finance' | 'rogan_podcast' | 'vox_documentary' | 'daily_vlog';

export interface ViralArchetypeProfile {
  id: ViralArchetypeKey;
  name: string;
  icon: string;
  badge: string;
  description: string;
  settings: {
    caption_style: CaptionStyle;
    caption_font: string;
    font_size: FontSizeOption;
    text_case: TextCaseOption;
    keyword_accent_mode: KeywordAccentMode;
    bgm_preset: string;
    bgm_volume: number;
    auto_ducking: boolean;
    hook_zoom_enabled: boolean;
    streamer_preset: StreamerPreset;
    podcast_layout_mode: PodcastLayoutMode;
    podcast_divider_style: PodcastDividerStyle;
    title_position: TitlePosition;
    title_duration: TitleDurationOption;
  };
}

export interface ClipSettingsRecommendation {
  archetype_id: ViralArchetypeKey;
  archetype_name: string;
  archetype_icon: string;
  reasoning: string;
  growth_tip: string;
  viral_scores: {
    hook_power: number;
    audio_balance: number;
    visual_retention: number;
    overall_score: number;
  };
  settings: {
    caption_style: CaptionStyle;
    caption_font: string;
    font_size: FontSizeOption;
    text_case: TextCaseOption;
    keyword_accent_mode: KeywordAccentMode;
    bgm_preset: string;
    bgm_volume: number;
    auto_ducking: boolean;
    hook_zoom_enabled: boolean;
    streamer_preset: StreamerPreset;
    podcast_layout_mode: PodcastLayoutMode;
    podcast_divider_style: PodcastDividerStyle;
    title_position: TitlePosition;
    title_duration: TitleDurationOption;
  };
}

export interface AnalyzeResponse {
  video_id: string;
  title: string;
  duration: number;
  heatmap: HeatmapPoint[];
  summary: string;
  clips: ViralClip[];
  transcript?: TranscriptLine[];
  model?: string;
  video_url?: string;
  source_type?: 'youtube' | 'upload' | 'gdrive';
  subtitle_language?: string;
  token_optimized?: boolean;
  original_cues?: number;
  compact_cues?: number;
}

export type AspectRatioOption = '9:16' | '1:1' | '4:3' | '16:9' | '16:9_landscape';
export type BackgroundStyle = 'black' | 'blurred';
export type CaptionStyle = 
  | 'viral_pop' 
  | 'beast_punch' 
  | 'cyber_violet' 
  | 'fire_red' 
  | 'electric_cyan' 
  | 'golden_aura' 
  | 'clean_minimal' 
  | 'none';
export type CaptionFont = 
  | 'Outfit' 
  | 'Montserrat' 
  | 'Inter' 
  | 'Impact' 
  | 'Bebas Neue' 
  | 'Anton' 
  | 'Poppins' 
  | 'Arial Black'
  | (string & {});
export type TitlePosition = 'auto' | 'safe_zone' | 'middle' | 'none';
export type TitleDurationOption = 'entire' | '5s' | '10s';
export type SubtitlePositionMode = 'bottom' | 'center';
export type StreamerPreset = 'none' | 'split_top_cam' | 'pip_corner' | 'podcast_split';
export type PodcastLayoutMode = 'stacked_split' | 'left_focus' | 'right_focus';
export type PodcastDividerStyle = 'clean_white' | 'glow_cyan' | 'glow_gold' | 'dark_line' | 'none';
export type FacecamPosition = 'auto' | 'bottom_right' | 'top_right' | 'bottom_left' | 'top_left' | 'center' | 'left' | 'right';
export type FontSizeOption = 'small' | 'medium' | 'big' | 'custom';
export type TextCaseOption = 'uppercase' | 'capitalize' | 'lowercase';
export type HardwareAccelOption = 'auto' | 'nvenc' | 'amf' | 'qsv' | 'cpu' | 'browser_wasm';
export type KeywordAccentMode = 'off' | 'accent_only' | 'accent_and_emoji';
export type CameraTrackingMode = 'off' | 'fit_balanced' | 'fit_close_up' | 'dynamic_pan_only' | 'static_center';
export type ComedyEffectPreset = 'none' | 'pwk_snap_zoom' | 'pwk_red_blush' | 'pwk_funny_fisheye';
export type VocalIsolationMode = 'off' | 'center_vocal_extract' | 'voice_clarity_bandpass';

export interface FontItem {
  name: string;
  is_custom: boolean;
  filename?: string | null;
  url?: string | null;
}

export interface HardwareAccelInfo {
  status: string;
  active_default: string;
  recommended: string;
  support: {
    nvenc: boolean;
    amf: boolean;
    qsv: boolean;
    cpu: boolean;
    recommended: string;
  };
  options: Array<{
    id: HardwareAccelOption;
    label: string;
    sub: string;
    available: boolean;
  }>;
}

export type BackgroundType = 'blur' | 'black' | 'color' | 'gradient' | 'preset' | 'custom_upload';

export interface BackgroundPresetItem {
  id: string;
  name: string;
  category: 'ambient' | 'color' | 'gradient' | 'motion' | 'gaming' | 'aesthetic';
  type: 'blur' | 'color' | 'gradient' | 'preset';
  description: string;
  preview_color: string;
  value: string;
  media_file?: string;
  c0?: string;
  c1?: string;
}

export interface CustomBackgroundFileItem {
  file_name: string;
  file_path: string;
  url: string;
  media_type: 'image' | 'video';
  file_size_bytes: number;
}

export interface AudioPresetItem {
  id: string;
  name: string;
  category: string;
  description: string;
  file?: string;
  duration?: number;
  url?: string;
  size_bytes?: number;
  created_at?: number;
}

export interface RenderSettings {
  renderEngine?: 'server' | 'client';
  aspectRatio: AspectRatioOption;
  backgroundStyle: BackgroundStyle;
  backgroundType?: BackgroundType;
  backgroundValue?: string;
  backgroundFilePath?: string;
  foregroundScale?: number; // 40 to 100%
  foregroundPositionY?: number; // 0 to 100%
  foregroundBorderRadius?: number; // 0 to 48px
  foregroundShadow?: boolean;
  enableFaceTracking: boolean;
  streamerPreset: StreamerPreset;
  facecamPosition?: FacecamPosition;
  titleText?: string;
  titlePrefix?: string;
  titleSuffix?: string;
  fileNamePrefix?: string;
  fileNameSuffix?: string;
  titlePosition: TitlePosition;
  titleDuration?: TitleDurationOption;
  titleFont?: CaptionFont;
  titleFontSize?: FontSizeOption;
  titleFontSizePx?: number;
  titleTextCase?: TextCaseOption;
  subtitlesEnabled?: boolean;
  captionStyle: CaptionStyle;
  captionFont: CaptionFont;
  fontSize: FontSizeOption;
  fontSizePx?: number;
  textCase: TextCaseOption;
  titleYPercent?: number;
  subtitleYPercent?: number;
  subtitlePositionMode?: SubtitlePositionMode;
  subtitleCenterYPercent?: number;
  selectedClips: ViralClip[];
  // Background Music
  bgmEnabled?: boolean;
  bgmPreset?: string;
  bgmFilePath?: string;
  bgmFileName?: string;
  bgmVolume?: number; // 0 to 100%
  bgmStartOffset?: number; // seconds from start of audio track
  // Hook SFX
  hookSfxEnabled?: boolean;
  hookSfxFilePath?: string;
  hookSfxFileName?: string;
  hookSfxVolume?: number; // 0 to 150%
  // Raw Audio / Voice Boost
  originalAudioVolume?: number; // 0 to 200%
  // Watermark
  watermarkEnabled?: boolean;
  watermarkType?: 'image' | 'text';
  watermarkFilePath?: string;
  watermarkUrl?: string;
  watermarkText?: string;
  watermarkSize?: number; // 5 to 50%
  watermarkOpacity?: number; // 10 to 100%
  watermarkX?: number; // 0 to 100%
  watermarkY?: number; // 0 to 100%
  // Hardware Acceleration / Video Encoder
  hardwareAccel?: HardwareAccelOption;
  // Subtitle Audio Calibration & Language
  subtitleOffsetMs?: number; // -1000 to +1000 ms
  subtitleLanguage?: 'id' | 'en';
  // Multi-Segment Merged Highlight Video
  renderMode?: 'separate' | 'merged';
  compilationTitle?: string;
  // v3.0 Ultra-Quality Render Engine
  videoPolishEnabled?: boolean;
  audioMasteringEnabled?: boolean;
  smartDuckingEnabled?: boolean;
  hookZoomEnabled?: boolean;
  // v3.1 Subtitle Keyword Emoji Accent & Viral Styling Engine
  keywordAccentMode?: KeywordAccentMode;
  // v3.3 Podcast Multi-Speaker Split Engine
  podcastLayoutMode?: PodcastLayoutMode;
  podcastDividerStyle?: PodcastDividerStyle;
  podcastHostCx?: number;
  podcastGuestCx?: number;
  // v3.6 Smart Camera Tracking (CapCut Style) & Fit to Canvas
  cameraTrackingMode?: CameraTrackingMode;
  trackingSmoothness?: number; // 1 to 10
  // v3.6 Comedy Expression FX (PWK Style)
  comedyEffectPreset?: ComedyEffectPreset;
  comedyEffectStartTime?: number; // seconds
  comedyEffectDuration?: number; // default 1.5s
  comedySfxEnabled?: boolean;
  // v3.7 Anti-Content ID Shield & Viral Algorithm Booster
  speedRampRatio?: number; // 1.00 to 1.08
  vocalIsolationMode?: VocalIsolationMode;
}

export interface RenderClipStatus {
  clip_index: number;
  title: string;
  base_title?: string;
  status: 'pending' | 'downloading' | 'transcribing' | 'tracking' | 'rendering' | 'completed' | 'error';
  progress_percent: number;
  download_url?: string;
  error_message?: string;
  error?: string;
  download_speed?: string;
  download_eta?: string;
  download_pct?: number;
}

export interface BatchRenderProgress {
  batch_id: string;
  total_clips: number;
  current_clip_index: number;
  overall_status: 'running' | 'completed' | 'error';
  zip_url?: string;
  error_message?: string;
  warning_message?: string;
  clips: RenderClipStatus[];
}
