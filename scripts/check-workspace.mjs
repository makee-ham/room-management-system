#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const required = [
  'AGENTS.md',
  'manifest.json',
  'DOCS/FINAL_UX_AUDIT.md',
  'DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md',
  'DOCS/15_TWO_PASS_AUDIT_RESULT.md',
  'DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md',
  'DOCS/WIREFRAME_TASK_PROMPT.md',
  'WIREFRAME/index.html',
  'WIREFRAME/README.md',
  'WIREFRAME/QA.md',
  'WIREFRAME/screenshots/admin-desktop-1440.png',
  'WIREFRAME/screenshots/admin-mobile-390.png',
  'WIREFRAME/screenshots/maid-mobile-390.png',
  'WIREFRAME/QA/screenshots/admin-mobile-rooms-unified.png',
  'WIREFRAME/QA/screenshots/admin-mobile-inspection-gallery.png',
  'WIREFRAME/QA/screenshots/admin-mobile-inspection-photo.png',
  'WIREFRAME/QA/screenshots/admin-mobile-pay-calendar.png',
  'WIREFRAME/QA/screenshots/admin-auto-early-late-1440.png',
  'WIREFRAME/QA/screenshots/admin-auto-early-late-390.png',
  'WIREFRAME/QA/screenshots/maid-weekly-availability-390.png',
  'WIREFRAME/QA/screenshots/maid-room-issue-multi-photo-390.png',
  'WIREFRAME/QA/screenshots/admin-room-issue-gallery-1440.png',
  'WIREFRAME/QA/screenshots/admin-assignment-type-filter-1440.png',
  'WIREFRAME/QA/screenshots/admin-maid-order-board-390.png',
  'WIREFRAME/QA/screenshots/admin-partial-assignment-390.png',
  'WIREFRAME/QA/screenshots/admin-weekly-worktable-symbols-390.png',
  'WIREFRAME/QA/screenshots/admin-maid-type-distribution-1440.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-report-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-inspection-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-payroll-1440.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-pay-history-390.png',
  'WIREFRAME/reference/redesign-concepts/admin-inspection.png',
  'WIREFRAME/reference/redesign-concepts/admin-next-day-assignment.png',
  'WIREFRAME/reference/redesign-concepts/maid-weekly-availability.png',
];

const missing = required.filter((file) => !existsSync(resolve(root, file)));
if (missing.length) {
  throw new Error(`Required files missing:\n${missing.join('\n')}`);
}

const portableDocs = [
  'README.md',
  'AGENTS.md',
  'DOCS/00_START_HERE.md',
  'DOCS/CODEX_PROMPT.md',
  'DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md',
  'DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md',
  'DOCS/WIREFRAME_TASK_PROMPT.md',
  'WIREFRAME/README.md',
  'WIREFRAME/QA.md',
];
const windowsPath = /(?:^|[\s(`])(?:[A-Za-z]:[\\/])/m;
const nonPortable = portableDocs.filter((file) => windowsPath.test(readFileSync(resolve(root, file), 'utf8')));
if (nonPortable.length) {
  throw new Error(`Windows absolute paths remain in portable docs:\n${nonPortable.join('\n')}`);
}

const html = readFileSync(resolve(root, 'WIREFRAME/index.html'), 'utf8');
const inlineScripts = [...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map((match) => match[1]);
if (!inlineScripts.length) throw new Error('No inline application script found.');
for (const script of inlineScripts) new Function(script);
if (/<(?:script|link)\b[^>]*(?:src|href)=["']https?:\/\//i.test(html)) {
  throw new Error('External script or stylesheet dependency found in WIREFRAME/index.html.');
}

const audit = readFileSync(resolve(root, 'DOCS/FINAL_UX_AUDIT.md'));
const auditHash = createHash('sha256').update(audit).digest('hex');
const indexHash = createHash('sha256').update(readFileSync(resolve(root, 'WIREFRAME/index.html'))).digest('hex');
const manifest = JSON.parse(readFileSync(resolve(root, 'manifest.json'), 'utf8'));
const expectedAuditHash = manifest.sha256?.['DOCS/FINAL_UX_AUDIT.md'];
const expectedIndexHash = manifest.sha256?.['WIREFRAME/index.html'];
if (auditHash !== expectedAuditHash || indexHash !== expectedIndexHash) {
  throw new Error([
    'Canonical file hash mismatch.',
    `Audit: ${auditHash} (expected ${expectedAuditHash})`,
    `Index: ${indexHash} (expected ${expectedIndexHash})`,
  ].join('\n'));
}

console.log(`Required files: ${required.length}/${required.length}`);
console.log(`Inline scripts parsed: ${inlineScripts.length}`);
console.log('Portable path scan: passed');
console.log(`Final UX audit SHA-256: ${auditHash}`);
console.log(`Wireframe SHA-256: ${indexHash}`);
console.log('Manifest hashes: passed');
console.log('Workspace check: passed');
