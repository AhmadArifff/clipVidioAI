/**
 * sync-docs.js
 *
 * Skrip otomatisasi mirroring dokumentasi fitur dari .agents/feature-docs/
 * dan 4 dokumen fondasi global ClipVidio AI ke portal dokumentasi SaaS Nuxt 3
 * (C:\Users\ASUS\Documents\Web Dev\improving\documentasi-projects\content\projects\Clipper-Vidio-YT).
 *
 * Dijalankan dengan: node .agents/scripts/sync-docs.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const SOURCE_DIR = path.resolve(__dirname, '../feature-docs');
const TARGET_PROJECT_DIR = 'C:\\Users\\ASUS\\Documents\\Web Dev\\improving\\documentasi-projects\\content\\projects\\Clipper-Vidio-YT';
const MANIFEST_PATH = path.join(TARGET_PROJECT_DIR, 'manifest.json');

console.log('====================================================');
console.log('Memulai Sinkronisasi Dokumentasi Fitur ClipVidio AI');
console.log('====================================================');
console.log(`Sumber : ${SOURCE_DIR}`);
console.log(`Tujuan : ${TARGET_PROJECT_DIR}\n`);

if (!fs.existsSync(SOURCE_DIR)) {
  console.error(`Direktori sumber tidak ditemukan: ${SOURCE_DIR}`);
  process.exit(1);
}

if (!fs.existsSync(TARGET_PROJECT_DIR)) {
  console.log(`Direktori tujuan belum ada, membuat folder: ${TARGET_PROJECT_DIR}`);
  fs.mkdirSync(TARGET_PROJECT_DIR, { recursive: true });
}

function getMarkdownFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      results = results.concat(getMarkdownFiles(filePath));
    } else if (file.endsWith('.md')) {
      if (file !== 'TEMPLATE-FEATURE-DOC.md' && file !== 'README.md') {
        results.push(filePath);
      }
    }
  });
  return results;
}

function parseFrontmatter(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const yamlBlock = match[1];
  const meta = {};

  yamlBlock.split(/\r?\n/).forEach(line => {
    const colonIndex = line.indexOf(':');
    if (colonIndex > -1) {
      const key = line.slice(0, colonIndex).trim();
      let val = line.slice(colonIndex + 1).trim();
      if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
        val = val.slice(1, -1);
      }
      meta[key] = val;
    }
  });
  return meta;
}

const mdFiles = getMarkdownFiles(SOURCE_DIR);
console.log(`Ditemukan ${mdFiles.length} berkas dokumentasi fitur untuk disinkronkan:\n`);

const syncedFeatures = [];

mdFiles.forEach(srcPath => {
  const content = fs.readFileSync(srcPath, 'utf8');
  const meta = parseFrontmatter(content);
  const fileBasename = path.basename(srcPath);

  const targetFileName = meta.id ? `${meta.id}.md` : fileBasename;
  const destPath = path.join(TARGET_PROJECT_DIR, targetFileName);

  fs.writeFileSync(destPath, content, 'utf8');
  console.log(`  [MIRROR] ${path.relative(SOURCE_DIR, srcPath)} -> ${targetFileName}`);

  syncedFeatures.push({
    id: meta.id || path.basename(srcPath, '.md'),
    title: meta.title || meta.id || 'Fitur Tanpa Judul',
    category: meta.category || 'Umum',
    route: meta.route || '',
    lead_developer: meta.lead_developer || 'ClipVidio AI Team',
    status: meta.status || 'Done',
    last_updated: meta.last_updated || new Date().toISOString().split('T')[0]
  });
});

console.log('\nMenyinkronkan 4 Berkas Pengetahuan Fondasi Global ClipVidio AI:');

const GLOBAL_FOUNDATION_FILES = [
  {
    src: path.resolve(__dirname, '../rules/10-architecture.md'),
    destName: 'system-architecture.md',
    id: 'system-architecture',
    title: 'Standar Arsitektur Backend FastAPI & Monorepo ClipVidio AI',
    category: '00-arsitektur-dan-knowledge'
  },
  {
    src: path.resolve(__dirname, '../rules/20-ffmpeg-video-engine.md'),
    destName: 'ffmpeg-video-engine.md',
    id: 'ffmpeg-video-engine',
    title: 'Standar FFmpeg Filtergraph, Audio DSP & Safe Zone 9:16',
    category: '00-arsitektur-dan-knowledge'
  },
  {
    src: path.resolve(__dirname, '../knowledge/bug-cases.md'),
    destName: 'production-bug-cases.md',
    id: 'production-bug-cases',
    title: 'Daftar Kasus Bug & Solusi Terverifikasi ClipVidio AI',
    category: '00-arsitektur-dan-knowledge'
  },
  {
    src: path.resolve(__dirname, '../knowledge/cross-feature-disambiguation.md'),
    destName: 'cross-feature-disambiguation.md',
    id: 'cross-feature-disambiguation',
    title: 'Kamus Disambiguasi Fitur Kembar & Jalur Paralel (Anti-Halusinasi)',
    category: '00-arsitektur-dan-knowledge'
  }
];

const syncedKnowledge = [];

GLOBAL_FOUNDATION_FILES.forEach(item => {
  if (fs.existsSync(item.src)) {
    let content = fs.readFileSync(item.src, 'utf8');
    if (!content.startsWith('---')) {
      const frontmatter = `---\nid: "${item.id}"\ntitle: "${item.title}"\ncategory: "${item.category}"\nroute: "N/A"\nlead_developer: "ClipVidio AI Team"\nlast_updated: "${new Date().toISOString().split('T')[0]}"\n---\n\n`;
      content = frontmatter + content;
    }
    const destPath = path.join(TARGET_PROJECT_DIR, item.destName);
    fs.writeFileSync(destPath, content, 'utf8');
    console.log(`  [FOUNDATION] ${path.basename(item.src)} -> ${item.destName}`);

    syncedKnowledge.push({
      id: item.id,
      title: item.title,
      category: item.category,
      filename: item.destName,
      last_updated: new Date().toISOString().split('T')[0]
    });
  } else {
    console.warn(`  Berkas sumber fondasi tidak ditemukan: ${item.src}`);
  }
});

const manifest = fs.existsSync(MANIFEST_PATH)
  ? JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'))
  : { project: 'Clipper-Vidio-YT', display_name: 'ClipVidio AI Studio', version: '3.9.0' };

manifest.menus = syncedFeatures;
manifest.system_knowledge = syncedKnowledge;
manifest.last_synced_at = new Date().toISOString();
fs.writeFileSync(MANIFEST_PATH, JSON.stringify(manifest, null, 2), 'utf8');

console.log(`\n[MANIFEST] Indeks fitur (${syncedFeatures.length}) & fondasi (${syncedKnowledge.length}) diperbarui di manifest.json.`);
console.log('Selesai! Dokumentasi ClipVidio AI berhasil dicerminkan.\n');
