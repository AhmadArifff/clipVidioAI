#!/usr/bin/env node
/**
 * Session State Manager CLI for clipVidioAI
 * 
 * Inspects, displays, or updates active session state to prevent context drift.
 * Usage:
 *   node .agents/02-session-state/session-manager.js
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sessionFile = path.join(__dirname, 'active-session.json');

if (!fs.existsSync(sessionFile)) {
  console.error('[SessionManager] Error: active-session.json not found!');
  process.exit(1);
}

const session = JSON.parse(fs.readFileSync(sessionFile, 'utf-8'));

console.log('========================================================');
console.log('       SESSION STATE TRACKER - CLIPVIDIO AI             ');
console.log('========================================================');
console.log(`Session ID   : ${session.session_id}`);
console.log(`Project      : ${session.project} (v${session.version})`);
console.log(`Active Goal  : ${session.active_goal}`);
console.log(`Status       : ${session.status}`);
console.log(`Last Updated : ${session.last_updated}`);
console.log('--------------------------------------------------------');
console.log('\n[Completed Milestones]:');
session.completed_milestones.forEach((m, idx) => {
  console.log(`  ${idx + 1}. [${m.status}] ${m.title} (${m.prd_sections.join(', ')})`);
});

console.log('\n[In Progress / Upcoming Milestones]:');
session.in_progress_milestones.forEach((m, idx) => {
  console.log(`  - [${m.status}] ${m.title} [Owner: ${m.owner_role}]`);
});

console.log('\n[Established Constraints (LOCKED)]:');
session.established_constraints.forEach((c, idx) => {
  console.log(`  ${idx + 1}. ${c}`);
});

console.log('\n========================================================\n');
