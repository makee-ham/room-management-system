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
  'DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md',
  'DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md',
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
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-1440.png',
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-390.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-390.png',
  'WIREFRAME/QA/screenshots/admin-room-status-available-long-stay-1440.png',
  'WIREFRAME/QA/screenshots/admin-available-room-edit-390.png',
  'WIREFRAME/QA/screenshots/admin-assignment-elevator-1440.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-report-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-inspection-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-payroll-1440.png',
  'WIREFRAME/QA/screenshots/admin-payroll-cleaning-ledger-1440.png',
  'WIREFRAME/QA/screenshots/admin-payroll-cleaning-ledger-390.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-pay-history-390.png',
  'WIREFRAME/QA/screenshots/admin-type-photo-template-1440.png',
  'WIREFRAME/QA/screenshots/maid-type-photo-template-390.png',
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
  'DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md',
  'DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md',
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

const sourceIds = (source, label) => {
  if (!source) throw new Error(`${label} source block not found.`);
  return [...source.matchAll(/'(\d+)'\s*:/g)].map((match) => match[1]);
};
const expectedLongStayRooms = ['139', '358', '359', '449', '458', '461', '553', '558', '559', '628', '629'];
const longStayIds = sourceIds(
  html.match(/const LONG_STAY_ROOMS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\);/)?.[1],
  'LONG_STAY_ROOMS',
).sort();
const endedLongStayIds = sourceIds(
  html.match(/const LONG_STAY_ENDED_ROOMS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\);/)?.[1],
  'LONG_STAY_ENDED_ROOMS',
).sort();
const holdIds = sourceIds(
  html.match(/const ROOM_STATUS_HOLDS\s*=\s*\{([\s\S]*?)\};/)?.[1],
  'ROOM_STATUS_HOLDS',
).sort();
const catalogSource = html.match(/const ROOM_CATALOG\s*=\s*\[([\s\S]*?)\n\s*\];/)?.[1];
if (!catalogSource) throw new Error('ROOM_CATALOG source block not found.');
const catalogIds = [...catalogSource.matchAll(/\['(\d+)'\s*,/g)].map((match) => match[1]);
const uniqueCatalogIds = new Set(catalogIds);
const sameIds = (actual, expected) => actual.length === expected.length && actual.every((id, index) => id === expected[index]);
if (!sameIds(longStayIds, expectedLongStayRooms)) {
  throw new Error(`Active long-stay room contract mismatch: ${longStayIds.join(', ')}`);
}
if (!sameIds(endedLongStayIds, ['527'])) {
  throw new Error(`Ended long-stay room contract mismatch: ${endedLongStayIds.join(', ')}`);
}
if (!sameIds(holdIds, ['762'])) {
  throw new Error(`Room hold contract mismatch: ${holdIds.join(', ')}`);
}
if (catalogIds.length !== 121 || uniqueCatalogIds.size !== 121) {
  throw new Error(`Room catalog contract mismatch: ${catalogIds.length} rows / ${uniqueCatalogIds.size} unique rooms.`);
}
const availableRoomCount = catalogIds.filter((id) => !longStayIds.includes(id) && !holdIds.includes(id)).length;
if (availableRoomCount !== 109) {
  throw new Error(`Customer-assignable room contract mismatch: ${availableRoomCount} rooms.`);
}
if (!/catalogStatus:hold\?'hold':longStay\?'longstay':'available'/.test(html) || /디폴트/.test(html)) {
  throw new Error('General rooms must use the existing customer-assignable status without a neutral default UI state.');
}

const qa = readFileSync(resolve(root, 'WIREFRAME/QA.md'), 'utf8');
if (/운영 상태 미입력|상태 미연결 111개|기준정보만 연결된 112개|디폴트/.test(qa)) {
  throw new Error('Stale neutral/default room status wording remains in WIREFRAME/QA.md.');
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
console.log(`Room master contract: ${availableRoomCount} customer-assignable / ${longStayIds.length} long-stay / ${holdIds.length} hold`);
console.log(`Final UX audit SHA-256: ${auditHash}`);
console.log(`Wireframe SHA-256: ${indexHash}`);
console.log('Manifest hashes: passed');
console.log('Workspace check: passed');
