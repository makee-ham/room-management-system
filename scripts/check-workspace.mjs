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
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-1440.png',
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-390.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-390.png',
  'WIREFRAME/QA/screenshots/admin-available-room-edit-390.png',
  'WIREFRAME/QA/screenshots/admin-room-info-edit-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-info-edit-390.png',
  'WIREFRAME/QA/screenshots/admin-manual-checkout-390.png',
  'WIREFRAME/QA/screenshots/admin-quick-booking-1440.png',
  'WIREFRAME/QA/screenshots/admin-quick-booking-390.png',
  'WIREFRAME/QA/screenshots/admin-assignment-elevator-1440.png',
  'WIREFRAME/QA/screenshots/admin-random-assignment-1440.png',
  'WIREFRAME/QA/screenshots/admin-random-assignment-390.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-report-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-inspection-390.png',
  'WIREFRAME/QA/screenshots/admin-bomb-room-payroll-1440.png',
  'WIREFRAME/QA/screenshots/admin-payroll-cleaning-ledger-1440.png',
  'WIREFRAME/QA/screenshots/admin-payroll-cleaning-ledger-390.png',
  'WIREFRAME/QA/screenshots/admin-payroll-per-maid-toggle-1440.png',
  'WIREFRAME/QA/screenshots/admin-payroll-per-maid-toggle-390.png',
  'WIREFRAME/QA/screenshots/maid-bomb-room-pay-history-390.png',
  'WIREFRAME/QA/screenshots/admin-type-photo-template-1440.png',
  'WIREFRAME/QA/screenshots/maid-type-photo-template-390.png',
  'WIREFRAME/QA/screenshots/maid-zone-camera-1440.png',
  'WIREFRAME/QA/screenshots/maid-zone-camera-390.png',
  'WIREFRAME/reference/redesign-concepts/admin-inspection.png',
  'WIREFRAME/reference/redesign-concepts/admin-next-day-assignment.png',
  'WIREFRAME/reference/redesign-concepts/maid-weekly-availability.png',
  'WIREFRAME/reference/redesign-concepts/admin-quick-booking-1440.png',
  'WIREFRAME/reference/redesign-concepts/admin-quick-booking-390.png',
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
const maidSource = html.match(/const MAIDS\s*=\s*\[([\s\S]*?)\n\s*\];/)?.[1];
const maidIds = [...(maidSource || '').matchAll(/id:'(m\d+)'/g)].map((match) => match[1]);
if (maidIds.length !== 9 || new Set(maidIds).size !== 9) {
  throw new Error(`Large-team maid fixture mismatch: ${maidIds.length} rows / ${new Set(maidIds).size} unique IDs.`);
}
for (const contract of [
  'random-assignments',
  'undo-random-assignment',
  '총 청소요금 균형 우선',
  '같은 엘리베이터·가까운 호수',
  '메이드별 배정 객실·청소 순서',
  'maxAssigned=Math.max(...results.map(result=>result.assigned))',
  'results.filter(result=>result.assigned===maxAssigned).sort((left,right)=>left.payGap-right.payGap||left.payDeviation-right.payDeviation||left.zoneRankTotal-right.zoneRankTotal||left.roomDistanceTotal-right.roomDistanceTotal',
  'assignmentTargetRate(item)',
  'assignmentPricingSnapshot(item)',
  'rateSnapshot:snapshot.rate',
  'minutesSnapshot:snapshot.minutes',
  'elevatorSnapshot:snapshot.elevator',
  'randomAssignmentStateMatches',
  'data-location="board"',
]) {
  if (!html.includes(contract)) throw new Error(`Random assignment contract missing: ${contract}`);
}
for (const removed of ['메이드별 작업량·동선 비교', 'renderAssignmentWorkloadOverview', 'toggle-assignment-route']) {
  if (html.includes(removed)) throw new Error(`Removed assignment comparison contract remains: ${removed}`);
}
for (const contract of [
  '구역별 청소·촬영',
  'taskZoneGroups',
  'capture-task-photo',
  'choose-task-photo',
  'remove-task-photo',
  'task-photo-file',
  'accept="image/*" capture="environment"',
  'URL.createObjectURL(file)',
  'releaseRoomIssuePhoto(upload.image)',
  'task.uploads?.forEach(upload=>collect(upload.image))',
  'submission.uploads?.forEach(upload=>collect(upload.image))',
  'urls.forEach(url=>URL.revokeObjectURL(url))',
]) {
  if (!html.includes(contract)) throw new Error(`Maid zone camera contract missing: ${contract}`);
}
for (const removed of ['add-task-photo', 'add-task-photos', "'add-photo'", "'add-photos'", '파일 전송 없이 슬롯 상태만']) {
  if (html.includes(removed)) throw new Error(`Removed simulated photo completion contract remains: ${removed}`);
}
for (const contract of ['paymentRecords:{}', 'paymentAttemptHistory:[]', 'paymentRecordKey(weekStart,maidId)', 'data-action="toggle-payment" data-week=', 'data-maid=', 'taskFingerprint', "['OPEN','PAYING','CHECK']", 'confirm-finish-payment', 'mark-payment-check', 'confirm-payment-open-v2', 'resolutionReason']) {
  if (!html.includes(contract)) throw new Error(`Per-maid payment contract missing: ${contract}`);
}
if (/cfg\.start==='2026-08-03'&&index===0/.test(html) || /state\.payment\s*=/.test(html)) {
  throw new Error('A first-card-only or global payment state regression remains in WIREFRAME/index.html.');
}

const sourceIds = (source, label) => {
  if (!source) throw new Error(`${label} source block not found.`);
  return [...source.matchAll(/'(\d+)'\s*:/g)].map((match) => match[1]);
};
const expectedInitialOccupiedRooms = ['139', '358', '359', '449', '458', '461', '553', '558', '559', '628', '629'];
const initialOccupiedIds = sourceIds(
  html.match(/const INITIAL_OCCUPIED_ROOMS\s*=\s*Object\.freeze\(\{([\s\S]*?)\}\);/)?.[1],
  'INITIAL_OCCUPIED_ROOMS',
).sort();
const dataIssueIds = sourceIds(
  html.match(/const ROOM_STATUS_HOLDS\s*=\s*\{([\s\S]*?)\};/)?.[1],
  'ROOM_STATUS_HOLDS',
).sort();
const catalogSource = html.match(/const ROOM_CATALOG\s*=\s*\[([\s\S]*?)\n\s*\];/)?.[1];
if (!catalogSource) throw new Error('ROOM_CATALOG source block not found.');
const catalogIds = [...catalogSource.matchAll(/\['(\d+)'\s*,/g)].map((match) => match[1]);
const uniqueCatalogIds = new Set(catalogIds);
const sameIds = (actual, expected) => actual.length === expected.length && actual.every((id, index) => id === expected[index]);
if (!sameIds(initialOccupiedIds, expectedInitialOccupiedRooms)) {
  throw new Error(`Initial occupied room seed mismatch: ${initialOccupiedIds.join(', ')}`);
}
if (!sameIds(dataIssueIds, ['762'])) {
  throw new Error(`Room data issue contract mismatch: ${dataIssueIds.join(', ')}`);
}
if (catalogIds.length !== 121 || uniqueCatalogIds.size !== 121) {
  throw new Error(`Room catalog contract mismatch: ${catalogIds.length} rows / ${uniqueCatalogIds.size} unique rooms.`);
}
if (!/dataIssue:hold\|\|null/.test(html) || !html.includes("'762':'엘리베이터·현재 투숙 상태 확인 필요'")) {
  throw new Error('Room 762 must remain a dataIssue until elevator and occupancy are confirmed.');
}
if (!/occupancy:occupiedSeed\?'occupied':'vacant'/.test(html) || !/catalogStatus:hold\?'hold':'available'/.test(html)) {
  throw new Error('Room master must separate initial occupancy from customer assignability.');
}
if (/LONG_STAY_(?:ROOMS|ENDED_ROOMS)|long-?stay|장기투숙/i.test(html)) {
  throw new Error('Legacy long-stay UI or state contracts remain in WIREFRAME/index.html.');
}

for (const contract of [
  "if(a==='edit-room-info')",
  "if(a==='save-room-info')",
  'id="room-info-number"',
  'readonly aria-readonly="true"',
  'id="room-info-type"',
  'id="room-info-elevator"',
  'roomMasterFingerprint(room)',
  'adminCanMutate()',
  'appendEvent(`${id}호 객실 정보 수정`',
  '이후 새 작업부터 적용',
]) {
  if (!html.includes(contract)) throw new Error(`Admin room master edit contract missing: ${contract}`);
}
for (const contract of [
  "if(a==='manual-checkout')",
  "if(a==='confirm-manual-checkout')",
  "room.occupancy!=='occupied'",
  'activeUnfinishedAttempt(id)',
  'recordManualCheckoutScheduleChange(id,unstartedAttempt,previousWorkDate,previousAccessStart)',
  'attemptId:currentAttemptId(no)||null',
  "draft.kind==='퇴실 청소'",
  "activeReservation.status='checked-out'",
  'existingDraft.reservationId=activeReservation.id',
  'projectReservationState(state,id)',
  "room.occupancy='vacant'",
  'room.actualCheckoutAt=actualCheckoutAt',
  'delete room.actualCheckoutAt',
  '예정 ${plannedCheckout} 보존',
  '퇴실 청소 초안 1건',
  'appendEvent(`${id}호 지금 체크아웃`',
]) {
  if (!html.includes(contract)) throw new Error(`Manual checkout contract missing: ${contract}`);
}

for (const contract of [
  'const INITIAL_RESERVATIONS',
  "{id:'quickReservation',label:'간편 예약'",
  "if (state.adminView==='quickReservation') return renderQuickReservation()",
  'reservationOverlaps(roomNo,checkInAt,checkOutAt,ignoreId',
  'initialReservationDrafts()',
  "activeReservationsFor(state).filter(reservation=>reservation.checkOutAt.slice(0,10)===state.assignmentDate)",
  'cleaningAssignmentForReservation(reservation)',
  'data-action="quick-reservation-edit"',
  "'quick-reservation-undo'",
  'quickTouchArmTimer=setTimeout',
  'Math.abs(dy)>8&&Math.abs(dy)>Math.abs(dx)',
  'quickSuppressClickUntil=Date.now()+500',
]) {
  if (!html.includes(contract)) throw new Error(`Quick reservation contract missing: ${contract}`);
}
const reservationCheckinLabel = '<label for="res-checkin">1. 체크인 일시</label>';
const reservationCheckoutLabel = '<label for="res-checkout">2. 체크아웃 일시</label>';
if (html.indexOf(reservationCheckinLabel) < 0 || html.indexOf(reservationCheckoutLabel) <= html.indexOf(reservationCheckinLabel)) {
  throw new Error('Single-reservation form must render check-in before check-out.');
}
for (const contract of [
  '한 고객의 체크인부터 체크아웃까지를 한 예약 ID로 저장',
  'reservationOverlaps(room.no,checkInAt,checkOutAt,id)',
  'quickReservationConflict(room.no,firstNight,lastNight,id,checkInAt,checkOutAt)',
  'reservationFingerprint(existing)',
  "historyReservationId=isNew?'__new__'",
  'syncAdjacentReservationCleaningSchedules',
  'syncReservationAssignmentScheduleState',
  "['checkout','checkin','deadline','nextReservationId'].some",
  'underlyingManualCheckoutTarget',
  'reservationWorkScheduleFingerprint',
  '이 예약은 이미 변경되었거나 취소되었습니다.',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation interval contract missing: ${contract}`);
}
const reservationModalStart = html.indexOf('function reservationModalConfig');
const reservationModalSource = html.slice(reservationModalStart, html.indexOf('function openReservation', reservationModalStart));
if (reservationModalSource.includes('퇴실 고객 체크아웃') || reservationModalSource.includes('다음 고객 체크인')) {
  throw new Error('Turnover labels must not be used as fields in a single-customer reservation form.');
}

const qa = readFileSync(resolve(root, 'WIREFRAME/QA.md'), 'utf8');
if (/고객 배정 가능 기준 109개|장기투숙 중 11개|현재 장기투숙 11개/.test(qa)) {
  throw new Error('Stale 109/11/1 room status contract remains in WIREFRAME/QA.md.');
}
for (const contract of ['초기 투숙 seed 11개', '762호 dataIssue', '객실 정보 수정', '수동 체크아웃', '랜덤 배정', 'admin-room-info-edit-1440.png', 'admin-manual-checkout-390.png', 'admin-random-assignment-1440.png', 'admin-random-assignment-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Room master QA contract missing: ${contract}`);
}
for (const contract of ['간편 예약 원장과 터치 오입력 방지', '세로 터치 스크롤', '길게 누른 뒤 가로 선택', 'admin-quick-booking-1440.png', 'admin-quick-booking-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Quick reservation QA contract missing: ${contract}`);
}
for (const contract of ['체크인 → 체크아웃 입력 순서', '같은 예약 ID', '실제 시각 겹침', '직전 퇴실 청소 재통보']) {
  if (!qa.includes(contract)) throw new Error(`Reservation interval QA contract missing: ${contract}`);
}
for (const contract of ['추가 검증 · 메이드 구역별 체크·즉시 카메라', 'maid-zone-camera-1440.png', 'maid-zone-camera-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Maid zone camera QA documentation missing: ${contract}`);
}
if (!/(?:실물|실기기)[^\n]{0,80}(?:후면 )?카메라[^\n]{0,120}(?:미검증|검증하지 못|확인하지 못)/.test(qa)) {
  throw new Error('Maid zone camera QA must distinguish static/browser checks from unverified physical-device camera behavior.');
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
console.log(`Large-team assignment fixture: ${maidIds.length} maids`);
console.log('Per-maid weekly payment static contracts: passed');
console.log('Portable path scan: passed');
console.log(`Room master contract: ${catalogIds.length} rooms / ${initialOccupiedIds.length} initially occupied / ${dataIssueIds.length} data issue`);
console.log(`Final UX audit SHA-256: ${auditHash}`);
console.log(`Wireframe SHA-256: ${indexHash}`);
console.log('Manifest hashes: passed');
console.log('Workspace check: passed');
