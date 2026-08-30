#!/usr/bin/env node

import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const required = [
  'AGENTS.md',
  'manifest.json',
  'SHA256SUMS.txt',
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
  'WIREFRAME/QA/screenshots/admin-maid-order-total-1440.png',
  'WIREFRAME/QA/screenshots/admin-partial-assignment-390.png',
  'WIREFRAME/QA/screenshots/admin-weekly-worktable-symbols-390.png',
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-1440.png',
  'WIREFRAME/QA/screenshots/admin-weekly-work-history-calendar-390.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-catalog-390.png',
  'WIREFRAME/QA/screenshots/admin-room-four-states-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-card-priority-390.png',
  'WIREFRAME/QA/screenshots/admin-room-stay-progress-390.png',
  'WIREFRAME/QA/screenshots/admin-assignment-early-late-1440.png',
  'WIREFRAME/QA/screenshots/admin-assignment-early-late-390.png',
  'WIREFRAME/QA/screenshots/admin-available-room-edit-390.png',
  'WIREFRAME/QA/screenshots/admin-room-info-edit-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-info-edit-390.png',
  'WIREFRAME/QA/screenshots/admin-manual-checkout-390.png',
  'WIREFRAME/QA/screenshots/admin-quick-booking-1440.png',
  'WIREFRAME/QA/screenshots/admin-quick-booking-390.png',
  'WIREFRAME/QA/screenshots/admin-quick-booking-sticky-header-390.png',
  'WIREFRAME/QA/screenshots/admin-room-total-filter-1440.png',
  'WIREFRAME/QA/screenshots/admin-calendar-standard-1440.png',
  'WIREFRAME/QA/screenshots/admin-calendar-standard-390.png',
  'WIREFRAME/QA/screenshots/admin-reservation-cancel-1440.png',
  'WIREFRAME/QA/screenshots/admin-reservation-cancel-390.png',
  'WIREFRAME/QA/screenshots/admin-reservation-guests-1440.png',
  'WIREFRAME/QA/screenshots/admin-reservation-guests-390.png',
  'WIREFRAME/QA/screenshots/maid-reservation-guests-390.png',
  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',
  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-390.png',
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
  'WIREFRAME/QA/screenshots/maid-tv-on-required-390.png',
  'WIREFRAME/QA/screenshots/admin-tv-on-inspection-1440.png',
  'WIREFRAME/QA/screenshots/admin-copy-cleanup-1440.png',
  'WIREFRAME/QA/screenshots/admin-info-tooltip-390.png',
  'WIREFRAME/QA/screenshots/maid-copy-cleanup-390.png',
  'WIREFRAME/QA/screenshots/maid-info-tooltip-390.png',
  'WIREFRAME/QA/screenshots/admin-cleaning-rollover-1440.png',
  'WIREFRAME/QA/screenshots/admin-cleaning-rollover-390.png',
  'WIREFRAME/QA/screenshots/maid-cleaning-rollover-390.png',
  'WIREFRAME/QA/screenshots/admin-occupied-reservation-1440.png',
  'WIREFRAME/QA/screenshots/admin-occupied-reservation-390.png',
  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',
  'WIREFRAME/QA/screenshots/admin-same-day-adjustment-390.png',
  'WIREFRAME/QA/screenshots/maid-same-day-change-notice-390.png',
  'WIREFRAME/QA/screenshots/maid-other-up-to-10-320.png',
  'WIREFRAME/QA/screenshots/admin-inspection-other-up-to-10-390.png',
  'WIREFRAME/QA/screenshots/quick-reservation-today-row-320.png',
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

const requiredPngEvidence = [
  'WIREFRAME/QA/screenshots/admin-reservation-cancel-1440.png',
  'WIREFRAME/QA/screenshots/admin-reservation-cancel-390.png',
  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-card-guest-count-390.png',
  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-1440.png',
  'WIREFRAME/QA/screenshots/admin-room-extra-guests-filter-390.png',
  'WIREFRAME/QA/screenshots/admin-cleaning-day-tabs-1440.png',
  'WIREFRAME/QA/screenshots/admin-same-day-adjustment-390.png',
  'WIREFRAME/QA/screenshots/maid-same-day-change-notice-390.png',
  'WIREFRAME/QA/screenshots/maid-other-up-to-10-320.png',
  'WIREFRAME/QA/screenshots/admin-inspection-other-up-to-10-390.png',
  'WIREFRAME/QA/screenshots/quick-reservation-today-row-320.png',
];
const pngSignature = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const invalidPngEvidence = requiredPngEvidence.filter((file) => {
  const bytes = readFileSync(resolve(root, file));
  return bytes.length < pngSignature.length || !bytes.subarray(0, pngSignature.length).equals(pngSignature);
});
if (invalidPngEvidence.length) {
  throw new Error(`Required PNG evidence has an invalid file signature:\n${invalidPngEvidence.join('\n')}`);
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
for (const contract of [
  'function infoTip(id,label,text',
  'data-info-tip aria-label=',
  'aria-expanded="false"',
  'aria-controls="${panelId}"',
  '<span class="info-tip-mark" aria-hidden="true">ⓘ</span>',
  'role="tooltip" hidden',
  'function closeInfoTips(',
  'function toggleInfoTip(trigger)',
  'function applyAdminCopyPolicy(root)',
  'function applyMaidCopyPolicy(root)',
  "if(state.role==='maid'){applyMaidCopyPolicy(root);return;}",
  "'maid-schedule','근무 가능일'",
  "'maid-pay','주급 내역'",
  "'촬영 방법','구역별 인증 사진을 촬영하세요.",
  '.help-title { display:flex; align-items:center; gap:7px;',
  '.info-tip-trigger { display:grid; place-items:center; width:44px; height:44px',
  '.info-tip-mark { display:grid; place-items:center; width:22px; height:22px; border:0; font-size:19px;',
]) {
  if (!html.includes(contract)) throw new Error(`Admin copy/help contract missing: ${contract}`);
}
if (html.includes('<span class="info-tip-mark" aria-hidden="true">!</span>')) {
  throw new Error('Legacy exclamation help glyph remains; use the ⓘ symbol.');
}
const availabilityPhaseStart = html.indexOf('function availabilitySubmissionPhase()');
const availabilityPhaseSource = html.slice(availabilityPhaseStart, html.indexOf('function availabilityCell', availabilityPhaseStart));
if (availabilityPhaseStart < 0) throw new Error('Maid availability submission phase source could not be resolved.');
for (const contract of [
  "AVAILABILITY_OPEN_TIME='12:00'",
  "AVAILABILITY_CLOSE_TIME='23:59'",
  'minutes<=closingMinutes',
  '일요일 ${AVAILABILITY_OPEN_TIME}부터 ${AVAILABILITY_CLOSE_TIME}까지',
  '일요일 23:59 마감 후',
]) {
  if (!html.includes(contract)) throw new Error(`Maid availability submission window contract missing: ${contract}`);
}
if (availabilityPhaseSource.includes("timeMinutes('22:00')") || /일요일[^\n]{0,40}22:00/.test(html)) {
  throw new Error('Legacy Sunday 22:00 maid availability deadline remains.');
}
const availabilityEditStart = html.indexOf("if(a==='edit-week-availability')");
const availabilityEditSource = html.slice(availabilityEditStart, html.indexOf("if(a==='request-availability-change')", availabilityEditStart));
if (availabilityEditStart < 0) throw new Error('Maid availability edit handler source could not be resolved.');
for (const contract of ['state.availabilityEditing=true', "state.availabilityDraft=[...(record?.days||[])]"]) {
  if (!availabilityEditSource.includes(contract)) throw new Error(`Maid availability edit-draft contract missing: ${contract}`);
}
if (/availabilitySubmitted\s*=\s*false|\.status\s*=\s*['"]draft['"]/.test(availabilityEditSource)) {
  throw new Error('Editing maid availability must not invalidate the last submitted record before resubmission.');
}
for (const contract of ['state.availabilitySubmitted&&!state.availabilityEditing', 'state.availabilityEditing=false;state.availabilityChangeRequested=false']) {
  if (!html.includes(contract)) throw new Error(`Maid availability committed-draft separation missing: ${contract}`);
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
  '메이드별 청소 순서 수정',
  'maxAssigned=Math.max(...results.map(result=>result.assigned))',
  'results.filter(result=>result.assigned===maxAssigned).sort((left,right)=>left.payGap-right.payGap||left.payDeviation-right.payDeviation||left.zoneRankTotal-right.zoneRankTotal||left.roomDistanceTotal-right.roomDistanceTotal',
  'assignmentTargetRate(item)',
  'assignmentPricingSnapshot(item)',
  'rateSnapshot:snapshot.rate',
  'minutesSnapshot:snapshot.minutes',
  'elevatorSnapshot:snapshot.elevator',
  'randomAssignmentStateMatches',
  'data-location="board"',
  'maid-order-schedule-badges',
  'scheduleBadges=assignmentSchedulePriorityBadges(item)',
  'class="maid-order-lane-total"',
  'data-maid-id="${maid.id}" data-maid-total="${total}"',
  '총 청소요금 · ${ordered.length}건',
  'ordered.reduce((sum,item)=>sum+assignmentTargetRate(item),0)',
  "isEditingBalance=targets.some(item=>assignmentFor(item).status==='draft')",
  "eligibleAssignmentMaids().map(maid=>maid.id)",
  '배정된 객실이 없습니다.',
  '얼리 체크인·레이트 체크아웃의 조정된 예정 시각을 먼저 확인하고',
  '랜덤 배정 기준 설명',
  'assignment-rule-tooltip',
  'aria-describedby="assignment-random-tooltip"',
  'id="assignment-random-tooltip" role="tooltip"',
  'assignment-rule-help.is-dismissed',
  "e.target.closest?.('.assignment-rule-help')",
  "document.addEventListener('pointerover'",
]) {
  if (!html.includes(contract)) throw new Error(`Random assignment contract missing: ${contract}`);
}
for (const removed of ['메이드별 작업량·동선 비교', 'renderAssignmentWorkloadOverview', 'toggle-assignment-route', 'class="random-rule"']) {
  if (html.includes(removed)) throw new Error(`Removed assignment comparison contract remains: ${removed}`);
}
for (const contract of [
  "requirementsMode:'photo-only-v1'",
  '구역별 사진 촬영',
  '인증 사진 ${requiredUploads.length}장 · 각 항목에 사진을 한 장 이상 등록하세요.',
  '남은 인증 사진 ${photosLeft}장',
  'taskZoneGroups',
  'capture-task-photo',
  'choose-task-photo',
  'remove-task-photo',
  'task-photo-file',
  'accept="image/*" capture="environment"',
  'URL.createObjectURL(file)',
  'remove-task-photo-item',
  'uploadPhotoEntries(upload).forEach(item=>releaseRoomIssuePhoto(item.image))',
  'task.uploads?.forEach(upload=>uploadPhotoEntries(upload).forEach(item=>collect(item.image)))',
  'submission.uploads?.forEach(upload=>uploadPhotoEntries(upload).forEach(item=>collect(item.image)))',
  'multiple data-control="task-photo-file" data-source="gallery"',
  'urls.forEach(url=>URL.revokeObjectURL(url))',
]) {
  if (!html.includes(contract)) throw new Error(`Maid photo-only workflow contract missing: ${contract}`);
}
const taskRequirementsStart = html.indexOf('function taskRequirements');
const taskRequirementsSource = html.slice(taskRequirementsStart, html.indexOf('function taskUploadByIdentity', taskRequirementsStart));
const taskZonesStart = html.indexOf('function taskZoneGroups');
const taskZonesSource = html.slice(taskZonesStart, html.indexOf('function groupsafe', taskZonesStart));
const taskSectionsStart = html.indexOf('function renderTaskInputSections');
const taskSectionsSource = html.slice(taskSectionsStart, html.indexOf('function cleaningPrimary', taskSectionsStart));
if ([taskRequirementsStart, taskZonesStart, taskSectionsStart].some(index => index < 0)) {
  throw new Error('Maid photo-only source ranges could not be resolved.');
}
const cleaningSectionHelperStart = html.indexOf('function renderCleaningInputSection');
const cleaningSectionHelperSource = html.slice(cleaningSectionHelperStart, taskSectionsStart);
if (cleaningSectionHelperStart < 0 || !cleaningSectionHelperSource.includes('class="cleaning-section"') || !cleaningSectionHelperSource.includes('data-cleaning-section-meta')) {
  throw new Error('Always-open maid cleaning section markup is missing.');
}
if (/<details\b|<summary\b/.test(taskSectionsSource) || html.includes('.cleaning-sections details') || html.includes('.cleaning-sections summary')) {
  throw new Error('Maid cleaning inputs must stay visible without collapsible details/summary controls.');
}
for (const sectionKey of ["'photos'", "'bomb-room'", "'room-issues'", "'candles'"]) {
  if (!taskSectionsSource.includes(`renderCleaningInputSection(no,${sectionKey}`)) throw new Error(`Always-open maid section missing: ${sectionKey}`);
}
const activeTemplateStart = html.indexOf('const TEMPLATE_KIND_DEMO');
const activeTemplateSource = html.slice(activeTemplateStart, html.indexOf('const LEGACY_TEMPLATE_CHECKLISTS', activeTemplateStart));
const templateUiStart = html.indexOf('function templateDetailHead');
const templateUiSource = html.slice(templateUiStart, html.indexOf('function titleForView', templateUiStart));
if ([activeTemplateStart, templateUiStart].some(index => index < 0) || activeTemplateSource.includes('checklist:') || /필수 체크|체크리스트|data-template-check|template\.checklist/.test(templateUiSource)) {
  throw new Error('The active cleaning template catalog or admin template UI still exposes checklist requirements.');
}
for (const removed of ['requiredChecks', 'req.checked', 'group.checks', 'data-control="task-check"', '필수 체크', '청소 확인', '체크리스트']) {
  if (`${taskRequirementsSource}${taskZonesSource}${taskSectionsSource}`.includes(removed)) {
    throw new Error(`Checklist dependency remains in active maid photo-only flow: ${removed}`);
  }
}
const fieldCompleteSource = html.slice(html.indexOf("if(a==='field-complete-v2')"), html.indexOf("if(a==='approve-inspection-v2')"));
const delegatedSubmissionStart = html.indexOf('function createCleaningSubmissionRecord');
const delegatedSubmissionEnd = html.indexOf('function activeBombRoomReport', delegatedSubmissionStart);
const delegatedSubmissionSource = delegatedSubmissionStart >= 0 && delegatedSubmissionEnd > delegatedSubmissionStart ? html.slice(delegatedSubmissionStart, delegatedSubmissionEnd) : '';
const submissionStoresEmptyChecklist = fieldCompleteSource.includes('checklist:{}') || fieldCompleteSource.includes('createCleaningSubmissionRecord(id)') && delegatedSubmissionSource.includes('checklist:{}');
if (fieldCompleteSource.includes('req.checked') || !fieldCompleteSource.includes('!req.requiredDone||req.failed') || !submissionStoresEmptyChecklist) {
  throw new Error('Maid completion/submission is not exclusively gated by required photo status.');
}
if (!delegatedSubmissionSource.includes('bindSubmissionEvidenceSnapshots(submission,attempt)')) throw new Error('Atomic cleaning submission evidence binding is missing.');
for (const contract of ['bombRoomReportSnapshot', 'roomIssuesSnapshot', 'candleCountSnapshot']) {
  if (!html.includes(contract)) throw new Error(`Atomic cleaning submission evidence contract missing: ${contract}`);
}
for (const contract of ['evidencePhotoSignature', 'issueLineageOk', 'snapshotIssueIds', 'liveIssuesById', 'evidenceDamageAudit:']) {
  if (!html.includes(contract)) throw new Error(`Damaged submission evidence guard missing: ${contract}`);
}
const rawBombEvidenceStart = html.indexOf('function rawBombRoomReportForSubmission');
const rawBombEvidenceEnd = html.indexOf('function bombRoomReportForSubmission', rawBombEvidenceStart);
const rawBombEvidenceSource = html.slice(rawBombEvidenceStart, rawBombEvidenceEnd);
if (rawBombEvidenceStart < 0 || rawBombEvidenceEnd <= rawBombEvidenceStart || !rawBombEvidenceSource.includes('if(snapshotValid)') || !rawBombEvidenceSource.includes('const preserved=bombRoomReportSnapshot(snapshot)')) {
  throw new Error('Submitted bomb-room snapshot is not the authoritative evidence fallback.');
}
const evidenceViewerStart = html.indexOf('function photoViewerConfig');
const evidenceViewerEnd = html.indexOf('function photoViewerModalMarkup', evidenceViewerStart);
const evidenceViewerSource = html.slice(evidenceViewerStart, evidenceViewerEnd);
for (const contract of ['validatedSubmission(rawSubmission)||rawSubmission', 'linkedSubmission?rawBombRoomReportForSubmission(linkedSubmission)', 'snapshotRecord||roomIssueRecords(no)']) {
  if (!evidenceViewerSource.includes(contract)) throw new Error(`Read-only submitted evidence viewer fallback missing: ${contract}`);
}
const taskInputMigrationStart = html.indexOf('function createTaskInputsFromSnapshot');
const taskInputMigrationSource = html.slice(taskInputMigrationStart, html.indexOf('function taskState', taskInputMigrationStart));
if (taskInputMigrationStart < 0 || taskInputMigrationSource.includes('sameFixture') || taskInputMigrationSource.includes('image?.fixture===')) {
  throw new Error('Cleaning photos must migrate only by exact versioned slot ID, never by a generic image fixture.');
}

const typePhotoGroupsStart = html.indexOf('const TYPE_PHOTO_GROUPS=');
const typePhotoGroupsEnd = html.indexOf('const TEMPLATE_KIND_DEMO=', typePhotoGroupsStart);
const typePhotoGroupsSource = html.slice(typePhotoGroupsStart, typePhotoGroupsEnd);
const typePhotoObjectStart = typePhotoGroupsSource.indexOf('{');
const typePhotoObjectEnd = typePhotoGroupsSource.lastIndexOf('};');
if ([typePhotoGroupsStart, typePhotoGroupsEnd, typePhotoObjectStart, typePhotoObjectEnd].some(index => index < 0)) {
  throw new Error('TV-required checkout photo template source could not be resolved.');
}
const typePhotoGroups = Function(`"use strict";return (${typePhotoGroupsSource.slice(typePhotoObjectStart, typePhotoObjectEnd + 1)});`)();
const expectedCheckoutPhotoCounts = {
  standard:{total:9,required:8},
  premium:{total:10,required:9},
  oceanPremium:{total:12,required:11},
  oceanFamily:{total:10,required:9},
};
for (const [typeId, expected] of Object.entries(expectedCheckoutPhotoCounts)) {
  const rules = typePhotoGroups[typeId] || [];
  const tvRules = rules.filter(rule => rule.id === 'tv-on');
  if (rules.length !== expected.total || rules.filter(rule => rule.required).length !== expected.required) {
    throw new Error(`${typeId} checkout photo counts do not match the simplified entrance-free template.`);
  }
  if (tvRules.length !== 1 || tvRules[0].zone !== 'TV' || tvRules[0].label !== 'TV 켜짐·화면 출력 확인' || tvRules[0].required !== true || tvRules[0].fixture !== 'tv') {
    throw new Error(`${typeId} must have exactly one distinct required TV-on photo rule.`);
  }

  if (rules.some(rule => rule.id === 'entry-number' || rule.label === '객실번호·현관')) {
    throw new Error(`${typeId} still contains the redundant room-number entrance slot.`);
  }
  if (rules.some(rule => rule.zone !== '기타' && rule.required !== true)) {
    throw new Error(`${typeId} has a non-기타 slot that is not required.`);
  }
  if (rules.some(rule => rule.zone === '기타' && (rule.required !== false || rule.maxPhotos !== 10))) {
    throw new Error(`${typeId} 기타 slot must be optional with maxPhotos 10.`);
  }
}
for (const contract of [
  "checkout:{name:'퇴실 청소',version:'v7'",
  'function legacyCheckoutTemplateSnapshotFor',
  "version:'v6',photos:Object.freeze(current.photos.filter(item=>item.id!=='tv-on')",
  "if(exact)return {status:exact.status||'empty',upload:exact};",
  "draft.kind==='퇴실 청소'?legacyCheckoutTemplateSnapshotFor(draft.room)",
  "templateVersionSeed:'v7'",
  "attempt.templateVersionSeed!=='v7'?legacyCheckoutTemplateSnapshotFor(attempt.room)",
  "snapshot.version==='v6'&&state.jobs[attempt.room]==='upload'&&!prior.templateId",
  'TV 켜짐·화면 출력 확인',
  'TV는 켜고 계정·QR·알림 없는 기본 화면',
]) {
  if (!html.includes(contract)) throw new Error(`TV-on photo version/safety contract missing: ${contract}`);
}
for (const removed of ['TV 화면은 끕니다', 'TV는 끄고', '켜진 TV 화면은 촬영하지 않습니다', '켜진 TV 화면은 사진에서 제외']) {
  if (html.includes(removed)) throw new Error(`Stale TV-off photo instruction remains: ${removed}`);
}

const rolloverAttemptStart = html.indexOf('function attemptForCleaningTarget');
const rolloverAttemptEnd = html.indexOf('\n      function ', rolloverAttemptStart + 20);
const rolloverAttemptSource = html.slice(rolloverAttemptStart, rolloverAttemptEnd < 0 ? rolloverAttemptStart + 2500 : rolloverAttemptEnd);
if (rolloverAttemptStart < 0 || !rolloverAttemptSource.includes('currentAttemptByRoom') || !rolloverAttemptSource.includes("attempt.status!=='superseded'") || !rolloverAttemptSource.includes('.reverse().find(')) {
  throw new Error('Repeated rollover must resolve the current/latest non-superseded attempt for the same cleaning target.');
}

const rolloverFunctionMatches = [...html.matchAll(/(?:function\s+[\w$]*(?:rollover|carryover)[\w$]*\s*\(|const\s+[\w$]*(?:rollover|carryover)[\w$]*\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)/gi)];
const rolloverCandidates = rolloverFunctionMatches.map((match) => {
  const start = match.index;
  const nextFunction = html.slice(start + match[0].length).search(/\n\s*(?:function\s+|const\s+[\w$]+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>)/);
  const end = nextFunction < 0 ? Math.min(html.length, start + 16000) : start + match[0].length + nextFunction;
  return html.slice(start, end);
});
const rolloverSource = rolloverCandidates.find((source) => ['unassigned', 'not-started', 'started-unfinished']
  .every((reason) => new RegExp(`carryReason\\s*[:=]\\s*['\"]${reason}['\"]`).test(source)));
if (!rolloverSource) throw new Error('Cleaning rollover source with all three unresolved classifications could not be resolved.');
for (const contract of ['planDate', 'effectiveDate', 'carriedFromDate', 'rolloverCount', 'lastRolloverDate']) {
  if (!html.includes(contract)) throw new Error(`Cleaning planned/effective rollover field missing: ${contract}`);
}
for (const reason of ['unassigned', 'not-started', 'started-unfinished']) {
  if (!new RegExp(`carryReason\\s*[:=]\\s*['\"]${reason}['\"]`).test(rolloverSource)) {
    throw new Error(`Cleaning rollover classification missing: ${reason}`);
  }
}
if (!/!\s*attempt(?:\s|\)|&&|\|\||\{)/.test(rolloverSource)) {
  throw new Error('Cleaning rollover must explicitly classify a target that had no prior maid attempt.');
}
if (!/!\s*attempt(?:\?\.)?\.startedAt/.test(rolloverSource) || !/attempt(?:\?\.)?\.startedAt\s*&&\s*!\s*attempt(?:\?\.)?\.completedAt/.test(rolloverSource)) {
  throw new Error('Cleaning rollover must distinguish assigned-not-started from started-unfinished work.');
}
if (!/maidId\s*[:=]\s*['\"]{2}/.test(rolloverSource) || !/order\s*[:=]\s*null/.test(rolloverSource)) {
  throw new Error('Assigned-but-unstarted carryover must reopen without a current maid or order.');
}
if (!rolloverSource.includes("assignment.status==='notified'?assignment.maidId:assignment.previousMaidId||null") || !rolloverSource.includes("carryReason=notifiedMaidId?'not-started':'unassigned'")) {
  throw new Error('Unsaved assignment drafts must not be recorded as previously notified maids during rollover.');
}
if (!/\[\s*['\"]upload['\"]\s*,\s*['\"]inspection['\"]\s*\]\.includes\(/.test(rolloverSource) || !/completedAt/.test(rolloverSource)) {
  throw new Error('Upload, inspection, and field-completed work must not re-enter next-day assignment carryover.');
}
if (!/(?:target|item|record|entry)\.id/.test(rolloverSource) || /(?:Date\.now\(|Math\.random\(|randomUUID\(|crypto\.randomUUID\()/.test(rolloverSource)) {
  throw new Error('Cleaning rollover must keep the original target ID instead of generating a replacement target.');
}
const rolloverCountIncrements = /rolloverCount\s*[:=][^;\n]{0,120}\+\s*1/.test(rolloverSource)
  || /nextCount\s*=\s*[^;\n]{0,160}rolloverCount[^;\n]{0,80}\+\s*1/.test(rolloverSource) && /rolloverCount\s*[:=]\s*nextCount/.test(rolloverSource);
if (!rolloverCountIncrements || !/lastRolloverDate/.test(rolloverSource)) {
  throw new Error('Repeated cleaning rollover must be counted once per destination date.');
}

const assignmentTargetsStart = html.indexOf('function assignmentTargets');
const assignmentTargetsEnd = html.indexOf('\n      function ', assignmentTargetsStart + 20);
const assignmentTargetsSource = html.slice(assignmentTargetsStart, assignmentTargetsEnd < 0 ? assignmentTargetsStart + 5000 : assignmentTargetsEnd);
if (assignmentTargetsStart < 0 || !/(?:targetEffectiveDate|assignmentTargetDate|effectiveDate)/.test(assignmentTargetsSource) || !assignmentTargetsSource.includes('state.assignmentDate')) {
  throw new Error('Assignment board must project unresolved targets by effective date, not only their original plan date.');
}
const assignmentOptionsStart = html.indexOf('function assignmentOptions');
const assignmentOptionsEnd = html.indexOf('\n      function ', assignmentOptionsStart + 20);
const assignmentOptionsSource = html.slice(assignmentOptionsStart, assignmentOptionsEnd < 0 ? assignmentOptionsStart + 3000 : assignmentOptionsEnd);
if (assignmentOptionsStart < 0 || !assignmentOptionsSource.includes('availabilityForWorkDate') || !/(?:targetEffectiveDate|assignmentTargetDate|effectiveDate)/.test(assignmentOptionsSource)) {
  throw new Error('Carryover reassignment must revalidate maid availability on the effective work date.');
}
const attemptAccessStart = html.indexOf('function attemptAccessStatus');
const attemptAccessEnd = html.indexOf('\n      function ', attemptAccessStart + 20);
const attemptAccessSource = html.slice(attemptAccessStart, attemptAccessEnd < 0 ? attemptAccessStart + 3000 : attemptAccessEnd);
if (attemptAccessStart < 0 || !/(?:attemptEffectiveDate|targetEffectiveDate|effectiveDate)/.test(attemptAccessSource) || /sameDate\s*=\s*state\.selectedDate\s*===\s*workDate/.test(attemptAccessSource)) {
  throw new Error('A carried started attempt must be accessible on its effective date while preserving its original plan date.');
}
for (const contract of ['전일 이월 · 미배정', '전일 이월 · 미완료', '원 계획', '이월']) {
  if (!html.includes(contract)) throw new Error(`Compact cleaning rollover label missing: ${contract}`);
}

const confirmStartStart = html.indexOf("if(a==='confirm-start')");
const confirmStartEnd = html.indexOf("if(a==='capture-task-photo')", confirmStartStart);
const confirmStartSource = html.slice(confirmStartStart, confirmStartEnd);
if (confirmStartStart < 0 || !confirmStartSource.includes('`${state.selectedDate} ${state.time}`')) {
  throw new Error('A cleaning attempt must record its actual start date instead of backdating to the original plan date.');
}
if (!fieldCompleteSource.includes('`${state.selectedDate} ${state.time}`')) {
  throw new Error('Field completion must use the actual selected date and time.');
}
const submitCleaningStart = html.indexOf("if(a==='submit-cleaning-v2')");
const submitCleaningEnd = html.indexOf("if(a==='approve-inspection-v2')", submitCleaningStart);
const submitCleaningSource = html.slice(submitCleaningStart, submitCleaningEnd);
const submissionCompletionSource = `${submitCleaningSource}${delegatedSubmissionSource}`;
if (submitCleaningStart < 0 || !submissionCompletionSource.includes('`${state.selectedDate} ${state.time}`') || !/weekStartIso\([^)]*completedAt/.test(submissionCompletionSource)) {
  throw new Error('Cleaning submission time and payroll week must derive from actual completion, not the original plan date.');
}
const validatedSubmissionStart = html.indexOf('function validatedSubmission');
const validatedSubmissionEnd = html.indexOf('\n      function ', validatedSubmissionStart + 20);
const validatedSubmissionSource = html.slice(validatedSubmissionStart, validatedSubmissionEnd < 0 ? validatedSubmissionStart + 5000 : validatedSubmissionEnd);
if (validatedSubmissionStart < 0 || !/weekStartIso\(completedDate\)\s*!==\s*submission\.weekStart/.test(validatedSubmissionSource)) {
  throw new Error('Validated cleaning submissions must derive their payroll week from actual completion date.');
}
if (/attempt\.workDate\s*&&\s*attempt\.workDate\s*!==\s*completedDate/.test(validatedSubmissionSource)) {
  throw new Error('A carried cleaning submission must not require actual completion date to equal original plan date.');
}
if (html.includes('if(!submission.templateSnapshot&&!submission.templateId)return submission;') || !html.includes('submission.templateSnapshot=legacySnapshot;submission.templateId=legacySnapshot.id;submission.templateVersion=legacySnapshot.version;')) {
  throw new Error('Legacy cleaning submissions can bypass their immutable template/photo validation.');
}
if (!html.includes("snapshot.version==='v6'&&state.jobs[attempt.room]==='upload'&&!prior.templateId") || !html.includes("upload.required&&upload.status==='empty'")) {
  throw new Error('Legacy upload-stage fixtures can become permanently blocked after photo-only template migration.');
}
for (const contract of ['currentAttemptId(no)!==attemptId', 'currentAttemptId(id)!==attemptId', 'latestTask?.attemptId!==attemptId']) {
  if (!html.includes(contract)) throw new Error(`Photo retry attempt guard missing: ${contract}`);
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
const catalogRows = [...catalogSource.matchAll(/\['(\d+)'\s*,\s*'([^']+)'\s*,\s*(null|'([ABC])')\]/g)].map((match) => ({
  no: match[1],
  type: match[2],
  elevator: match[4] || null,
}));
const catalogIds = catalogRows.map((room) => room.no);
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
const expectedElevatorForRoom = (no) => {
  const suffix = Number(no.slice(-2));
  if (suffix >= 6 && suffix <= 27) return 'A';
  if ((suffix >= 1 && suffix <= 5) || (suffix >= 28 && suffix <= 33) || (suffix >= 57 && suffix <= 62)) return 'B';
  if (suffix >= 34 && suffix <= 56) return 'C';
  return null;
};
const elevatorMismatches = catalogRows.filter((room) => room.elevator !== expectedElevatorForRoom(room.no));
if (elevatorMismatches.length) {
  throw new Error(`Building-map elevator mismatch: ${elevatorMismatches.map((room) => `${room.no}:${room.elevator || 'missing'}`).join(', ')}`);
}
const elevatorCounts = catalogRows.reduce((counts, room) => ({...counts, [room.elevator]: (counts[room.elevator] || 0) + 1}), {});
if (elevatorCounts.A !== 33 || elevatorCounts.B !== 29 || elevatorCounts.C !== 59 || catalogRows.some((room) => !room.elevator)) {
  throw new Error(`Elevator totals mismatch: A ${elevatorCounts.A || 0} / B ${elevatorCounts.B || 0} / C ${elevatorCounts.C || 0} / missing ${catalogRows.filter((room) => !room.elevator).length}`);
}
const mappedFormerMissingRooms = {139:'C',358:'B',359:'B',449:'C',458:'B',461:'B',553:'C',559:'B',628:'B',629:'B',762:'B'};
for (const [no, elevator] of Object.entries(mappedFormerMissingRooms)) {
  if (catalogRows.find((room) => room.no === no)?.elevator !== elevator) {
    throw new Error(`Former missing elevator mapping mismatch: ${no} must use ${elevator}.`);
  }
}
if (!html.includes("const ROOM_ELEVATOR_SOURCE = '2026-08-18 사용자 제공 건물 지도';")) {
  throw new Error('Building-map elevator source is missing.');
}
if (!/dataIssue:hold\|\|null/.test(html) || !html.includes("'762':'현재 투숙 상태 확인 필요'")) {
  throw new Error('Room 762 must remain a dataIssue until occupancy is confirmed.');
}
if (!/occupancy:occupiedSeed\?'occupied':'vacant'/.test(html) || !/catalogStatus:hold\?'hold':'available'/.test(html)) {
  throw new Error('Room master must separate initial occupancy from customer assignability.');
}
if (/LONG_STAY_(?:ROOMS|ENDED_ROOMS)/.test(html)) {
  throw new Error('Deprecated fixed long-stay room lists remain in WIREFRAME/index.html.');
}
for (const contract of [
  "const LONG_STAY_OPEN_END_AT='9999-12-31T23:59'",
  'function reservationIsLongStay(reservation)',
  'function reservationHasKnownEnd(reservation)',
  'function reservationLongStayEndLabel(reservation)',
  'data-control="reservation-long-stay"',
  '종료일 미정',
]) {
  if (!html.includes(contract)) throw new Error(`Long-stay contract missing: ${contract}`);
}
for (const contract of [
  "key:'blocked',tone:'red',status:'배정 불가'",
  "key:'cleaning',tone:'amber',status:'청소 필요'",
  "key:'occupied',tone:'neutral',status:'투숙 중'",
  "key:'available',tone:'green',status:'배정 가능'",
  'roomCleaningStageLabel(job)',
  'cardReservationStatus(no)',
  "{id:'reservation-demo-142'",
  'label:`연박 ${day}/${total}일차`',
]) {
  if (!html.includes(contract)) throw new Error(`Four-state room card contract missing: ${contract}`);
}
const roomPresentationSource = html.slice(html.indexOf('function roomPresentation(no)'), html.indexOf('function renderPinRow', html.indexOf('function roomPresentation(no)')));
const roomPresentationOrder = ["if(blockers.length)return", "if(room.occupancy==='occupied')return", "if(cleaning)return", "key:'available'"]
  .map((marker) => roomPresentationSource.indexOf(marker));
if (roomPresentationOrder.some((index) => index < 0) || roomPresentationOrder.some((index, position) => position && index <= roomPresentationOrder[position - 1])) {
  throw new Error(`Room card priority must remain blocked > occupied (with subordinate cleaning) > cleaning > available: ${roomPresentationOrder.join(', ')}`);
}
for (const contract of [
  'function roomCleaningControl(no)',
  "label:'청소 요청'",
  "label:'청소 취소'",
  "confirmLabel:request?'청소 취소':'청소 대기열에 넣기'",
  "if(state.roomFilter==='occupied')return r.occupancy==='occupied'",
  "if(state.roomFilter==='cleaning')return roomNeedsCleaningNow(r.no)",
  'data-room-cleaning-control=\"${no}\"',
  "청소 필요 · ${p.cleaningKind||'청소'}",
]) {
  if (!html.includes(contract)) throw new Error(`Room cleaning request contract missing: ${contract}`);
}
for (const forbidden of ['ON으로 변경', 'OFF로 변경', '청소 필요 ON', '청소 필요 OFF']) {
  if (html.includes(forbidden)) throw new Error(`Legacy cleaning switch copy remains: ${forbidden}`);
}
const roomListRowStart = html.indexOf('function roomListRow(no)');
const roomListRowEnd = html.indexOf('function cleaningLabel', roomListRowStart);
if (roomListRowStart < 0 || roomListRowEnd <= roomListRowStart) throw new Error('Room list row source block not found.');
const roomListRowSource = html.slice(roomListRowStart, roomListRowEnd);
const renderRoomsStart = html.lastIndexOf('function renderRooms()');
const renderRoomsEnd = html.indexOf('const QUICK_RESERVATION_PAST_DAYS', renderRoomsStart);
if (renderRoomsStart < 0 || renderRoomsEnd <= renderRoomsStart) throw new Error('Room list rendering block not found.');
const renderRoomsSource = html.slice(renderRoomsStart, renderRoomsEnd);
for (const contract of [
  'function renderRoomListPinManager(no)',
  'class="room-list-item',
  'class="room-list-actions"',
  '<span>PIN 관리</span>',
  '.room-list-actions { display:grid; grid-template-columns:repeat(4,minmax(0,1fr));',
  '.room-list-actions { grid-template-columns:repeat(2,minmax(0,1fr));',
  "roomViewState:()=>({view:'list',cardCount:0",
]) {
  if (!html.includes(contract)) throw new Error(`List-only room view contract missing: ${contract}`);
}
for (const forbidden of [
  'roomViewMode',
  'data-action="set-room-view"',
  'room-view-switcher',
  '카드 보기',
  '리스트 보기',
]) {
  if (html.includes(forbidden)) throw new Error(`Removed room-view toggle returned: ${forbidden}`);
}
if (!renderRoomsSource.includes('class="room-list-table"') || renderRoomsSource.includes('roomCard(') || renderRoomsSource.includes('room-list-v2')) {
  throw new Error('Room screen must render the list-only layout.');
}
if (roomListRowSource.includes('<span>관리</span>')) throw new Error('Ambiguous room-list 관리 header returned; use PIN 관리.');
for (const action of ['quick-reservation-edit','reservation-edit','operation-status','room-detail']) {
  if (!roomListRowSource.includes(action)) throw new Error(`Room list action contract missing: ${action}`);
}
for (const contract of [
  '.assignment-table td { min-width:0; overflow:hidden; }',
  '.assignment-source { display:inline-flex; align-items:flex-start; flex-wrap:wrap;',
  'white-space:normal; overflow-wrap:anywhere; word-break:keep-all;',
  '.assignment-schedule-badges { display:flex; flex-wrap:wrap; gap:5px; min-width:0; max-width:100%; overflow:hidden; }',
  '.assignment-table .schedule-priority-badge { max-width:100%; min-width:0;',
]) {
  if (!html.includes(contract)) throw new Error(`Cleaning assignment badge containment contract missing: ${contract}`);
}
console.log('List-only room view and cleaning assignment badge containment contracts: passed');

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
  "activeReservationsFor(targetState).filter(reservation=>reservation.checkOutAt.slice(0,10)===assignmentDate)",
  'cleaningAssignmentForReservation(reservation)',
  'data-action="quick-reservation-edit"',
  "'quick-reservation-undo'",
  'quickTouchArmTimer=setTimeout',
  'Math.abs(dy)>8&&Math.abs(dy)>Math.abs(dx)',
  'quickSuppressClickUntil=Date.now()+500',
  'quickGridScrollLeft:null',
  'state.quickGridScrollLeft=null',
  '--quick-room-col:112px',
  'class="quick-room-link"',
  'tabindex="${rowIndex===0?',
  '${room.no}호 객실 상세 열기',
  "if(state.adminView==='quickReservation'&&!state.detail)rememberQuickGridViewport()",
  '검색어 또는 객실 유형 필터를 바꿔 주세요.',
  'rowIndex===0&&iso===focusDate',
  "['ArrowUp','ArrowDown','Home','End'].includes(event.key)",
]) {
  if (!html.includes(contract)) throw new Error(`Quick reservation contract missing: ${contract}`);
}
for (const removedContract of [
  'quickReservationElevator',
  'quick-reservation-elevator',
  'bookingElevator',
  'quickRoomCleaner',
  'quick-room-cleaner',
]) {
  if (html.includes(removedContract)) throw new Error(`Removed quick reservation filter or cleaner contract returned: ${removedContract}`);
}
const quickGridStart = html.indexOf('function quickCellMarkup');
const quickGridEnd = html.indexOf('function rememberQuickGridViewport', quickGridStart);
if (quickGridStart < 0 || quickGridEnd <= quickGridStart) throw new Error('Quick reservation grid scope is missing.');
const quickGridScope = html.slice(quickGridStart, quickGridEnd);
for (const removedCopy of ['퇴실 청소 담당','청소 미배정','assignedCount=monthReservations','유형·엘리베이터 필터']) {
  if (quickGridScope.includes(removedCopy)) throw new Error(`Removed quick reservation grid copy returned: ${removedCopy}`);
}
for (const contract of [
  "const CALENDAR_WEEKDAYS=Object.freeze(['일','월','화','수','목','금','토'])",
  'const KR_HOLIDAY_FIXTURE=Object.freeze({',
  "jurisdiction:'KR',mode:'demo-static',coverage:['2026-01-01','2026-12-31']",
  "'2026-01-01':{name:'신정'",
  "'2026-05-01':{name:'노동절'",
  "'2026-06-03':{name:'제9회 전국동시지방선거'",
  "'2026-07-17':{name:'제헌절'",
  "'2026-08-15':{name:'광복절'",
  "'2026-08-17':{name:'광복절 대체공휴일'",
  "'2026-09-25':{name:'추석'",
  "'2026-12-25':{name:'기독탄신일'",
  'function calendarDayMeta(iso)',
  "tone:holiday?'holiday':isSunday?'sunday':isSaturday?'saturday':'weekday'",
  'function calendarWeekdayHeaderMarkup()',
  'function calendarDateAriaLabel(iso',
  'offset=first.getDay(),start=',
  'Array.from({length:42}',
  'calendarWeekdayHeaderMarkup()',
  'calendarDayMeta(iso)',
  'calendar-holiday-mark',
  '.calendar-day.is-saturday:not(.is-holiday)',
  '.quick-day-header.is-saturday:not(.is-holiday)',
]) {
  if (!html.includes(contract)) throw new Error(`Sunday-first Korean calendar contract missing: ${contract}`);
}
const calendarStart = html.indexOf('function calendarMarkup');
const calendarEnd = html.indexOf('function openCalendar', calendarStart);
if (calendarStart < 0 || calendarEnd <= calendarStart) throw new Error('Shared calendar scope is missing.');
const calendarScope = html.slice(calendarStart, calendarEnd);
for (const removedCalendarContract of [
  "weekMode?['월','화','수','목','금','토','일']",
  '(first.getDay()+6)%7',
]) {
  if (calendarScope.includes(removedCalendarContract)) throw new Error(`Monday-first calendar layout returned: ${removedCalendarContract}`);
}
for (const removedQuickCalendarContract of ['.quick-day-header.weekend','weekend=[0,6]']) {
  if (html.includes(removedQuickCalendarContract)) throw new Error(`Combined red weekend styling returned: ${removedQuickCalendarContract}`);
}
for (const businessWeekContract of [
  'offset=(d.getDay()+6)%7',
  'mondayOffset=-((date.getUTCDay()+6)%7)',
  '날짜를 누르면 그 날짜가 포함된 월요일–일요일 주차를 선택합니다.',
]) {
  if (!html.includes(businessWeekContract)) throw new Error(`Monday-to-Sunday business-week meaning changed: ${businessWeekContract}`);
}
const reservationCheckinLabel = '<label for="res-checkin">1. 체크인 일시</label>';
const reservationCheckoutLabel = '<label for="res-checkout" data-res-checkout-label>';
if (html.indexOf(reservationCheckinLabel) < 0 || html.indexOf(reservationCheckoutLabel) <= html.indexOf(reservationCheckinLabel)) {
  throw new Error('Single-reservation form must render check-in before check-out.');
}
const roomTypesStart = html.indexOf('const ROOM_TYPES = {');
const roomTypesEnd = html.indexOf('};', roomTypesStart);
if (roomTypesStart < 0 || roomTypesEnd <= roomTypesStart) throw new Error('ROOM_TYPES guest policy source could not be resolved.');
const roomTypesSource = html.slice(roomTypesStart, roomTypesEnd);
const expectedReservationGuestPolicies = {
  standard: [2, 2],
  premium: [2, 3],
  oceanPremium: [2, 4],
  oceanFamily: [4, 6],
};
for (const [typeId, expected] of Object.entries(expectedReservationGuestPolicies)) {
  const match = roomTypesSource.match(new RegExp(`${typeId}:\\s*\\{[^}]*defaultGuestCount:(\\d+)\\s*,\\s*maxGuestCount:(\\d+)`));
  const actual = match ? [Number(match[1]), Number(match[2])] : [];
  if (actual.length !== 2 || actual.some((value, index) => value !== expected[index])) {
    throw new Error(`Reservation guest policy mismatch for ${typeId}: ${actual.join('/') || 'missing'} (expected ${expected.join('/')}).`);
  }
}
for (const contract of [
  'function guestPolicyForRoom(roomNo)',
  'function reservationGuestCount(reservation)',
  "Object.hasOwn(reservation,'guestCount')",
  'guestCount:guestPolicyForRoom(reservation.room).defaultGuestCount',
  "reservationGuestCount(reservation),reservationIsLongStay(reservation)?'long':'dated',reservation.status",
  'Number.isInteger(value)&&value>=1?value:policy.defaultGuestCount',
  "return Number.isInteger(Number(value))&&Number(value)>=1?`${Number(value)}명`:'인원 미기록'",
]) {
  if (!html.includes(contract)) throw new Error(`Reservation guest data contract missing: ${contract}`);
}
const guestUpsertStart = html.indexOf('function upsertReservationRecord');
const guestUpsertEnd = html.indexOf('function clearOrphanedReservationDraftJob', guestUpsertStart);
if (guestUpsertStart < 0 || guestUpsertEnd <= guestUpsertStart) throw new Error('Reservation guest upsert source could not be resolved.');
const guestUpsertSource = html.slice(guestUpsertStart, guestUpsertEnd);
for (const contract of [
  'policy.defaultGuestCount):Number(guestCount)',
  '!Number.isInteger(resolvedGuestCount)||resolvedGuestCount<1||resolvedGuestCount>policy.maxGuestCount',
  'guestError:true',
  'guestCountChanged=!!before&&reservationGuestCount(before)!==resolvedGuestCount',
  'cleaningChanges=reservationCleaningChanges(beforeReservations,prospectiveReservations)',
  'roomCleaningChanged=cleaningChanges.length>0',
  'reservationCleaningChangeTouchesPublic(cleaningChanges,room.no)',
  'reservationCleaningChangeTouchesRandom(cleaningChanges)',
  'guestCount:resolvedGuestCount',
  'syncReservationCleaningDraft(reservation,before)',
]) {
  if (!guestUpsertSource.includes(contract)) throw new Error(`Reservation guest upsert contract missing: ${contract}`);
}
for (const contract of [
  "upsertReservationRecord({roomNo,checkInAt:range.checkInAt,checkOutAt:range.checkOutAt,source:'grid'})",
  'reservationGuestCount(result.reservation)}명 예약 접수',
  "upsertReservationRecord({id:reservationId,roomNo:no,checkInAt:checkinAt,checkOutAt:isLongStay&&!enteredCheckoutAt?'':checkoutAt,guestCount,source:isLongStay?'long-stay':'card',currentStay,isLongStay})",
  "document.getElementById(result.guestError?'reservation-guest-stepper'",
]) {
  if (!html.includes(contract)) throw new Error(`Reservation guest entry contract missing: ${contract}`);
}
const guestModalStart = html.indexOf('function reservationModalConfig');
const guestModalEnd = html.indexOf('function openReservation', guestModalStart);
if (guestModalStart < 0 || guestModalEnd <= guestModalStart) throw new Error('Reservation guest modal source could not be resolved.');
const guestModalSource = html.slice(guestModalStart, guestModalEnd);
const guestRoomFieldIndex = guestModalSource.indexOf('id="res-room"');
const guestStepperIndex = guestModalSource.indexOf('id="res-guests"');
if (guestRoomFieldIndex < 0 || guestStepperIndex <= guestRoomFieldIndex) {
  throw new Error('Reservation guest stepper must render immediately after the room field in the primary row.');
}
for (const contract of [
  'class="reservation-primary-row field-full"',
  '<span class="label" id="res-guests-label">인원수</span>',
  'id="res-guests" type="hidden"',
  'id="reservation-guest-stepper" role="group" tabindex="-1"',
  'data-action="reservation-guest-change" data-delta="-1"',
  'data-action="reservation-guest-change" data-delta="1"',
  'id="res-guests-value" aria-live="polite"',
  '기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명',
]) {
  if (!guestModalSource.includes(contract)) throw new Error(`Reservation guest stepper contract missing: ${contract}`);
}
for (const contract of [
  '.reservation-guest-stepper { display:grid; grid-template-columns:44px minmax(44px,1fr) 44px;',
  '.reservation-guest-stepper button { display:grid; place-items:center; width:44px; min-width:44px; min-height:44px;',
  'function updateReservationGuestControls(resetToDefault=false)',
  'resetToDefault?policy.defaultGuestCount:Number(input.value)',
  "if(c==='reservation-room'){updateReservationGuestControls(true);return;}",
  "if(a==='reservation-guest-change')",
  'if(next<1||next>policy.maxGuestCount)return',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation guest control contract missing: ${contract}`);
}
for (const contract of [
  '.schedule-priority-badge.guests { background:#17314a;',
  'function reservationHasExtraGuests(reservation)',
  'reservationGuestCount(reservation)>guestPolicyForRoom(reservation.room).defaultGuestCount',
  'function roomHasExtraGuests(no)',
  'const reservation=activeReservationsFor(state,String(no)).find(item=>!reservationRecordIsPast(item))||null;',
  'const cardGuestCount=closestReservation&&reservationHasExtraGuests(closestReservation)?reservationGuestCount(closestReservation):null;',
  "if(state.roomFilter==='extra-guests')return roomHasExtraGuests(r.no);",
  "'occupied','extra-guests','candle'",
  'value="extra-guests"',
  '>인원 추가</option>',
  'class="schedule-priority-badge guests" aria-label="숙박 인원 ${cardGuestCount}명"',
  "${icon('user','icon-sm')}${cardGuestCount}명",
]) {
  if (!html.includes(contract)) throw new Error(`Room-card extra-guest/filter contract missing: ${contract}`);
}
const roomCardPolicy = readFileSync(resolve(root, 'DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md'), 'utf8');
for (const contract of [
  '기준인원보다 많을 때만',
  '`+N명`처럼 초과분만 표시하지 않으며',
  '객실 상태 필터의 `인원 추가`는 이 동일한 조건',
]) {
  if (!roomCardPolicy.includes(contract)) throw new Error(`Room-card extra-guest/filter policy missing: ${contract}`);
}
for (const contract of [
  '체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',
  'reservationOverlaps(room.no,checkInAt,checkOutAt,id)',
  'quickReservationConflict(room.no,firstNight,lastNight,id,checkInAt,checkOutAt,registeringCurrentStay)',
  'reservationFingerprint(existing)',
  "historyReservationId=currentEntry?'__current__':isNew?'__new__'",
  'syncAdjacentReservationCleaningSchedules',
  'syncReservationAssignmentScheduleState',
  "['checkout','checkin','deadline','nextReservationId'].some",
  'underlyingManualCheckoutTarget',
  'reservationWorkScheduleFingerprint',
  '이 예약은 이미 변경되었거나 취소되었습니다.',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation interval contract missing: ${contract}`);
}
for (const contract of [
  "{id:'reservation-demo-117'",
  'function reservationHardBlockReason(room)',
  'function currentOccupiedReservation(room)',
  'linked=room.currentStayReservationId?reservations.find(reservation=>reservation.id===room.currentStayReservationId):null',
  'function occupiedReservationEnd(room)',
  'function occupiedStayNeedsCheckoutUpdate(room)',
  'function suggestedReservationStartDate(roomNo)',
  "requestedCurrent=reservationId==='__current__'",
  "needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room)",
  "auxiliaryAction:nextRegistration.canAdd?'reservation-add':''",
  '현재 예약 수정 가능 · 예약 취소 불가',
  'registeringCurrentStay',
  'linkedCurrentStay',
  'room.currentStayReservationId=reservation.id',
  'function reservationCanEditCurrentStay(reservation,room=',
  'requestedCurrentStay=!!requested&&reservationCanEditCurrentStay(requested,room)',
  'readOnly=weekPast&&!currentEntry&&!editableCurrentStay',
  'delete room.currentStayReservationId',
  'function syncUnstartedReservationCleaningAttempt(reservation,linkedAttempt=null)',
  'attempt.startedAt||roomPinWasViewed(reservation.room,attempt.id)||attempt.accessReviewRequired',
  "checkoutSnapshot:target.checkout||''",
  'guestCountSnapshot:assignmentGuestCount(target)',
  'function reservationCleaningChanges(beforeReservations,afterReservations)',
  'function ensureQuickDateCellVisible(cell)',
  '예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',
]) {
  if (!html.includes(contract)) throw new Error(`Occupied-room reservation contract missing: ${contract}`);
}
const reservationHardBlockStart = html.indexOf('function reservationHardBlockReason(room)');
const reservationHardBlockEnd = html.indexOf('function quickRoomBlockReason', reservationHardBlockStart);
const reservationHardBlockSource = html.slice(reservationHardBlockStart, reservationHardBlockEnd);
if (reservationHardBlockStart < 0 || reservationHardBlockEnd <= reservationHardBlockStart || reservationHardBlockSource.includes('room.occupancy')) {
  throw new Error('Occupied state must not return as a reservation hard-block reason.');
}
for (const contract of [
  'guestCount:reservationGuestCount(reservation),nextReservationId:schedule.nextReservationId',
  'reservationId:reservation?.id||null,guestCount:reservation?reservationGuestCount(reservation):null',
  'guestCountChanged=!committed||(item.guestCount??null)!==(committed.guestCount??null)',
  'record.targetChanged=changed',
  'assignment.guestCountChanged===true||assignment.reservationChanged===true',
  'return {item:record.committedTarget,assignment}',
  'item.guestCount??\'\'',
  'assignment.committedTarget={...item,type:snapshot.typeId,rateSnapshot:snapshot.rate,minutesSnapshot:snapshot.minutes,elevatorSnapshot:snapshot.elevator}',
  'assignment.guestCountChanged=false;assignment.reservationChanged=false;assignment.targetChanged=false',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation guest assignment snapshot contract missing: ${contract}`);
}
const randomGuestWeightStart = html.indexOf('function randomAssignmentTrial');
const randomGuestWeightEnd = html.indexOf('function createRandomAssignment', randomGuestWeightStart);
const assignmentPricingStart = html.indexOf('function assignmentPricingSnapshot');
const assignmentPricingEnd = html.indexOf('function assignmentTargetMinutes', assignmentPricingStart);
if (randomGuestWeightStart < 0 || randomGuestWeightEnd <= randomGuestWeightStart || assignmentPricingStart < 0 || assignmentPricingEnd <= assignmentPricingStart) {
  throw new Error('Random assignment or pricing source could not be resolved for guest-count isolation.');
}
if (/guestCount|assignmentGuest/i.test(html.slice(randomGuestWeightStart, randomGuestWeightEnd)) || /guestCount|assignmentGuest/i.test(html.slice(assignmentPricingStart, assignmentPricingEnd))) {
  throw new Error('Reservation guest count must invalidate stale assignment drafts but must not change pricing or random-assignment weighting.');
}
const cleaningAttemptStart = html.indexOf('function beginCleaningAttempt');
const cleaningAttemptEnd = html.indexOf('function validatedSubmission', cleaningAttemptStart);
if (cleaningAttemptStart < 0 || cleaningAttemptEnd <= cleaningAttemptStart) throw new Error('Cleaning attempt guest snapshot source could not be resolved.');
const cleaningAttemptSource = html.slice(cleaningAttemptStart, cleaningAttemptEnd);
for (const contract of [
  'reservationIdSnapshot=undefined,guestCountSnapshot=undefined',
  'committedTarget=state.assignments?.[resolvedWorkTargetId]?.committedTarget||null',
  'resolvedReservationId=reservationIdSnapshot===undefined?(committedTarget?.reservationId??null):reservationIdSnapshot',
  'lineageMatches=!resolvedReservationId||committedTarget?.reservationId===resolvedReservationId',
  'committedGuestCount=lineageMatches?committedTarget?.guestCount:null',
  'resolvedGuestCount=guestCountSnapshot===undefined?committedGuestCount:guestCountSnapshot',
  'guestCountSnapshot:Number.isInteger(Number(resolvedGuestCount))',
]) {
  if (!cleaningAttemptSource.includes(contract)) throw new Error(`Cleaning attempt guest snapshot contract missing: ${contract}`);
}
for (const contract of [
  'committedReservationId=state.assignments?.[attempt.workTargetId]?.committedTarget?.reservationId||null',
  'attemptReservationId=attempt.reservationIdSnapshot||committedReservationId',
  'reservationMatches=attemptReservationId===reservation.id',
  'previousAttempt?.guestCountSnapshot??assignmentGuestCount(target)',
  'guestCountSnapshot:previousAttempt.guestCountSnapshot',
  'guestCountSnapshot:submission.guestCountSnapshot',
  '(attempt.guestCountSnapshot??null)===(submission.guestCountSnapshot??null)',
  'guestCountSnapshot:guestCountForAttempt(attempt)',
  'const guestCount=assignmentGuestCount(item)',
  '<span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong>',
  "<span>숙박 인원</span><strong>${activeGuestCount?guestCountLabel(activeGuestCount):'미기록'}</strong>",
  'parts.push(`숙박 인원 ${guestCountLabel(assignmentGuestCount(item))}`)',
  'unstartedAttempt.reservationIdSnapshot===activeReservation.id&&!guestCountForAttempt(unstartedAttempt)',
  'committedReservationId===attempt.reservationIdSnapshot?guestCountForAttempt(attempt):null',
  'reopenCancelledAssignmentForNewReservation(state,{...freshTarget,id},{allowSameReservation:reopenSameReservation})',
]) {
  if (!html.includes(contract)) throw new Error(`Maid reservation guest snapshot contract missing: ${contract}`);
}
for (const contract of [
  'const overCapacity=activeReservationsFor(state,id).find',
  '!reservationRecordIsPast(reservation)&&reservationGuestCount(reservation)>ROOM_TYPES[type].maxGuestCount',
  'reservationGuestCount(reservation)>ROOM_TYPES[type].maxGuestCount',
  '예약이 ${reservationGuestCount(overCapacity)}명이라 최대 ${ROOM_TYPES[type].maxGuestCount}명',
]) {
  if (!html.includes(contract)) throw new Error(`Room-type guest capacity guard missing: ${contract}`);
}
const reservationCopyStart = html.indexOf('function reservationModalConfig');
const reservationCopyEnd = html.indexOf('function openReservationCancellationReview', reservationCopyStart);
if (reservationCopyStart < 0 || reservationCopyEnd <= reservationCopyStart) {
  throw new Error('Admin reservation copy scope is missing.');
}
const reservationCopy = html.slice(reservationCopyStart, reservationCopyEnd);
for (const contract of [
  'reservationWeekScheduleMarkup',
  'reservationWeekIsPast',
  'reservationRecordIsPast',
  'data-action="reservation-week-shift"',
  'data-action="open-reservation-week-calendar"',
  "state.calendarContext==='reservation-week'",
  '지난 예약 기록 · 조회만 가능',
  'reservation.checkInAt<window.endAt&&reservation.checkOutAt>window.startAt',
  'checkOutAt<=reservationCurrentMoment()',
  'weekStart:state.reservationWeekStart',
  'entry.modalPayload?.weekStart',
  'historyOnly=roomRecords.length>0&&roomRecords.every(reservationRecordIsPast)',
  'reservationWeekHistoryOverride',
]) {
  if (!html.includes(contract)) throw new Error(`Weekly reservation history contract missing: ${contract}`);
}
for (const unwantedCopy of [
  '저장 즉시 양방향 반영',
  '카드와 간편 예약표에 동시에 반영됩니다.',
  '카드·예약표 공통 원장',
  '같은 예약 ID',
  '예약 식별',
  '다중 예약 원장',
  '내부 수동 예약 원장',
  '현재 탭의 객실 카드·청소 초안과 즉시 연동',
  '객실 카드와 간편 예약표에 바로 반영',
  '객실 카드·예약표·청소 상태를 함께 갱신',
  '예약 후 청소 자동 연결',
  '수동 예약 복제본',
  '상태 이력 보존',
  '통보 스냅샷',
  '신규 예약 입력으로 바꾸거나 다른 예약을 덮어쓰지 않았습니다.',
]) {
  if (reservationCopy.includes(unwantedCopy)) throw new Error(`Admin reservation copy exposes implementation detail: ${unwantedCopy}`);
}
for (const contract of [
  'const RESERVATION_CANCEL_REASONS',
  "other:'기타 운영 사유'",
  'reservationCancelReasonError(reasonCode)',
  'Object.hasOwn(RESERVATION_CANCEL_REASONS,code)',
  "if(c==='reservation-cancel-reason')",
  'confirm.disabled=!!reservationCancelReasonError(e.target.value)',
  '고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.',
  'reservationCancellationImpact(reservation)',
  'reservationCancellationImpactFingerprint(reservation',
  'reservationAutomaticCleaningAttempt',
  'privateDrafts',
  'publishedDrafts',
  'publicCleaningLinked',
  'randomAssignmentActive',
  'actualStayStarted',
  'cancelReservationAssignmentRecord(record',
  'cancelReservationRecord({reservationId',
  'clearOrphanedReservationDraftJob',
  "reservation.status='cancelled'",
  'state.selectedDrafts=state.selectedDrafts.filter',
  'cancelledTarget:targetSnapshot',
  "cancelledBy:'관리자 · 데모'",
  'targetSnapshot:targetSnapshot?{...targetSnapshot}:null',
  'previousMaidId:null,previousOrder:null,committedTarget:null',
  'historyStack:true',
  "'reservation-cancel-review'",
  "'confirm-reservation-cancel'",
  '예약정보 수정 저장',
  '예약 취소 확정',
  '외부 예약은 취소되지 않습니다.',
  '체크인이 시작된 예약은 취소하지 않고',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation cancellation contract missing: ${contract}`);
}
if (html.includes('id="reservation-cancel-other"') || html.includes('normalizedReservationCancelOther') || html.includes('reasonDetail')) {
  throw new Error('Reservation cancellation must not expose or persist a free-form reason field.');
}
const reservationAssignmentCancelStart = html.indexOf('function cancelReservationAssignmentRecord');
const reservationAssignmentCancelSource = html.slice(reservationAssignmentCancelStart, html.indexOf('function syncAdjacentReservationCleaningSchedules', reservationAssignmentCancelStart));
for (const contract of [
  "if(record.status==='cancelled')return",
  'alreadyCancelled:true',
  'state.cleaningTargets[targetId]',
  'closed:true',
  'closedAt:cancelledAt',
  "closedBy:'관리자 · 데모'",
  "closeReasonCode:'reservation'",
  "closeStatus:'cancelled'",
]) {
  if (!reservationAssignmentCancelSource.includes(contract)) throw new Error(`Reservation cancellation cleaning-ledger tombstone contract missing: ${contract}`);
}
if (!html.includes("if(cancelled.alreadyCancelled)cleaningEffect='퇴실 청소 대상 이미 취소됨 · 기존 취소 이력 보존'")) {
  throw new Error('Reservation cancellation must distinguish an already-cancelled cleaning target from a newly released assignee.');
}
const reservationModalStart = html.indexOf('function reservationModalConfig');
const reservationModalSource = html.slice(reservationModalStart, html.indexOf('function openReservation', reservationModalStart));
if (reservationModalSource.includes('퇴실 고객 체크아웃') || reservationModalSource.includes('다음 고객 체크인')) {
  throw new Error('Turnover labels must not be used as fields in a single-customer reservation form.');
}

const assignmentDashboardStart = html.indexOf('function renderAssignmentDashboard');
const assignmentDashboardSource = html.slice(assignmentDashboardStart, html.indexOf('function cleaningTabButton', assignmentDashboardStart));
const assignmentFlowContracts = ['메이드 주간 근무표', 'renderRandomAssignmentCard()', '객실별 담당 수정', 'renderMaidOrderBoardContent()'];
let assignmentFlowIndex = -1;
for (const contract of assignmentFlowContracts) {
  const nextIndex = assignmentDashboardSource.indexOf(contract);
  if (nextIndex <= assignmentFlowIndex) throw new Error(`Cleaning assignment flow order is invalid at: ${contract}`);
  assignmentFlowIndex = nextIndex;
}
if (assignmentDashboardSource.includes('assignment-grid')) {
  throw new Error('Cleaning assignment flow must stay one-column: worktable, random draft, assignee edit, then order edit.');
}
const maidOrderItemStart = html.indexOf('function maidOrderItemMarkup');
const maidOrderItemSource = html.slice(maidOrderItemStart, html.indexOf('function renderRandomAssignmentCard', maidOrderItemStart));
if (!maidOrderItemSource.includes('assignmentSchedulePriorityBadges(item)') || !maidOrderItemSource.includes('maid-order-schedule-badges')) {
  throw new Error('Maid order items must repeat early/late schedule priority badges with their adjusted times.');
}
for (const contract of ['previous=ordered[index-1]', 'next=ordered[index+1]', '!cleaningTargetCanAdjust(previous)', '!cleaningTargetCanAdjust(next)']) {
  if (!maidOrderItemSource.includes(contract)) throw new Error(`Maid order controls must not cross a locked adjacent target: ${contract}`);
}

const cleaningHubStart = html.indexOf('function renderCleaningHub');
const cleaningHubSource = html.slice(cleaningHubStart, html.indexOf('function taskRow', cleaningHubStart));
const cleaningDayTabContracts = [
  "cleaningTabButton('assignment-today','오늘 배정'",
  "cleaningTabButton('assignment-tomorrow','내일 배정'",
  "cleaningTabButton('progress','진행 중'",
  "cleaningTabButton('inspection','검수 대상 목록'",
  "cleaningTabButton('done','완료'",
  'assignmentCountsForDate(todayDate).total',
  'assignmentCountsForDate(tomorrowDate).total',
];
let cleaningDayTabIndex = -1;
for (const contract of cleaningDayTabContracts.slice(0, 5)) {
  const nextIndex = cleaningHubSource.indexOf(contract);
  if (nextIndex <= cleaningDayTabIndex) throw new Error(`Today/tomorrow cleaning tab order is invalid at: ${contract}`);
  cleaningDayTabIndex = nextIndex;
}
for (const contract of cleaningDayTabContracts.slice(5)) {
  if (!cleaningHubSource.includes(contract)) throw new Error(`Cleaning day tab count contract missing: ${contract}`);
}
for (const removed of ['전날 배정에서 보기', '전날 배정에서 확인', '전날 관리자 배정으로 이동']) {
  if (html.includes(removed)) throw new Error(`Legacy single-day cleaning assignment label remains: ${removed}`);
}
for (const contract of [
  "function assignmentDateForCleaningTab(targetState=state,tab=targetState.cleaningTab)",
  "tab==='assignment-tomorrow'||tab==='assignment'?addIsoDays(targetState.selectedDate,1):targetState.selectedDate",
  "params.set('cleaningDay','today')",
  "params.set('cleaningDay','tomorrow')",
  "if(tab===state.cleaningTab){el.focus();return;}",
  'rememberCurrentHistoryRoute();state.cleaningTab=tab',
  'pushHistoryOnNextRender();render()',
]) {
  if (!html.includes(contract)) throw new Error(`Today/tomorrow route contract missing: ${contract}`);
}
for (const contract of [
  "find(item=>!item.cancelled&&item.room===roomNo&&item.kind==='퇴실 청소'",
  'manual=(targetState.manualAssignmentTargets||[]).filter(item=>!item.cancelled&&targetEffectiveDate(item,assignmentDate)===assignmentDate)',
  'independentTarget=(state.manualAssignmentTargets||[]).some(target=>!target.cancelled&&target.room===roomNo)',
]) {
  if (!html.includes(contract)) throw new Error(`Cancelled manual cleaning targets must stay out of active assignment lookup: ${contract}`);
}

const activationStart = html.indexOf('function activateNotifiedAssignmentsForDate');
const activationSource = html.slice(activationStart, html.indexOf('function assignmentFor', activationStart));
for (const contract of [
  "assignment?.status!=='notified'",
  'attemptForCleaningTarget(item)',
  'activeUnfinishedAttempt(item.room)',
  'roomAttemptBlocksActivation=!!roomAttempt',
  'assignment.activationBlockedBy',
  "appendEvent('내 청소 시작 보류 안내'",
  '{maidIds:[assignment.maidId]}',
  "appendEvent('내 청소 시작 가능 안내'",
  "reason:'사전 통보 청소 당일 활성화'",
  'beginCleaningAttempt(item.room',
  "state.jobs[item.room]=item.kind==='재청소'?'reclean':'scheduled'",
]) {
  if (!activationSource.includes(contract)) throw new Error(`Future assignment activation contract missing: ${contract}`);
}
if (!html.includes('if(targetState===state&&toDate>=previousDate)activateNotifiedAssignmentsForDate(toDate)')) {
  throw new Error('Operational date advancement must activate previously notified cleaning assignments.');
}
for (const routeFunction of ['function applyHistoryRoute', 'function applyHashParameters']) {
  const routeStart = html.indexOf(routeFunction);
  const routeEnd = html.indexOf('\n      function ', routeStart + routeFunction.length);
  const routeSource = html.slice(routeStart, routeEnd > routeStart ? routeEnd : undefined);
  if (!routeSource.includes("if(state.cleaningTab==='assignment-today')activateNotifiedAssignmentsForDate(state.selectedDate)")) {
    throw new Error(`${routeFunction} must reconcile today assignments after all route fields are restored.`);
  }
}
if (!html.includes('closeModal();activateNotifiedAssignmentsForDate(state.selectedDate);render();toast(')) {
  throw new Error('Inspection completion must reconcile same-day assignments that were explicitly held for an earlier room task.');
}

const adjustmentBlockStart = html.indexOf('function cleaningTargetAdjustmentBlock');
const adjustmentBlockSource = html.slice(adjustmentBlockStart, html.indexOf('function cleaningTargetCanAdjust', adjustmentBlockStart));
for (const contract of ['roomAttempt.workTargetId!==target.id', "roomAttempt.status==='submitted'", 'attempt.startedAt', 'attempt.completedAt', "!['active','scheduled'].includes(attempt.status)"]) {
  if (!adjustmentBlockSource.includes(contract)) throw new Error(`Cleaning adjustment stage lock contract missing: ${contract}`);
}

const sameDayAddStart = html.indexOf("if(a==='new-cleaning')");
const sameDayAddSource = html.slice(sameDayAddStart, html.indexOf("if(a==='cancel-cleaning-target')", sameDayAddStart));
for (const contract of [
  'state.assignmentDate!==state.selectedDate||!activeUnfinishedAttempt(r.no)',
  'state.assignmentDate===state.selectedDate&&activeUnfinishedAttempt(no)',
  "state.assignments[key]={maidId:'',order:null,status:'unassigned'",
  "reopenReason:'관리자 직접 다시 추가'",
  'cancellationHistory:[...(cancelledAssignment.cancellationHistory||[]),cancellationRevision]',
  'closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]',
  'priorJobState:state.jobs[no]??null',
]) {
  if (!sameDayAddSource.includes(contract)) throw new Error(`Same-day cleaning add/reopen contract missing: ${contract}`);
}

const cancelledReservationReopenStart = html.indexOf('function reopenCancelledAssignmentForNewReservation');
const cancelledReservationReopenSource = html.slice(cancelledReservationReopenStart, html.indexOf('function initializeCleaningTargetLedger', cancelledReservationReopenStart));
for (const contract of [
  'cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]',
  'record.cancelledNotifiedAt||record.notifiedAt||null',
  'record.cancelledNotificationRevision??record.notificationRevision??null',
  'record.cancelledTarget||record.committedTarget||null',
  'cancelledStatus:record.cancelledStatus||null',
  'closeStatus:ledger.closeStatus||null',
  'cleaningTargetOperationalSnapshot(ledger',
  'closeHistory:[...(ledger?.closeHistory||[])',
  "reopenReason:'새 예약 청소 의무'",
]) {
  if (!cancelledReservationReopenSource.includes(contract)) throw new Error(`New-reservation cleaning reopen history contract missing: ${contract}`);
}
for (const contract of [
  'reopenCancelledAssignmentForNewReservation(targetState,item)===record',
  'reopenCancelledAssignmentForNewReservation(state,item)',
  'reopenCancelledAssignmentForNewReservation(state,{...freshTarget,id},{allowSameReservation:reopenSameReservation})',
]) {
  if (!html.includes(contract)) throw new Error(`Cancelled target reopen must use the shared history-preserving helper: ${contract}`);
}
for (const contract of [
  "if(record.status==='cancelled')return",
  'syncReservationAssignmentScheduleState(reservation,checkoutDate,{reopenSameReservation:true})',
  "['closed','closedAt','closedBy','closeReasonCode','closeReason','closeStatus','closeHistory','reopenedAt','reopenReason']",
]) {
  if (!html.includes(contract)) throw new Error(`Cancelled reservation date-revert guard missing: ${contract}`);
}
const cancelledManualReopenStart = html.indexOf('function reopenCancelledManualCleaningTarget');
const cancelledManualReopenSource = html.slice(cancelledManualReopenStart, html.indexOf('function initializeCleaningTargetLedger', cancelledManualReopenStart));
for (const contract of [
  "record.status!=='cancelled'",
  'delete manual.cancelled',
  'cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]',
  'record.cancelledNotifiedAt||record.notifiedAt||null',
  'record.cancelledNotificationRevision??record.notificationRevision??null',
  'cleaningTargetOperationalSnapshot(closedTarget',
  'closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]',
  'reopenReason',
]) {
  if (!cancelledManualReopenSource.includes(contract)) throw new Error(`Cancelled manual cleaning target reopen contract missing: ${contract}`);
}
if (!html.includes("reopened=reopenCancelledManualCleaningTarget(manualTarget,'실제 체크아웃으로 퇴실 청소 다시 생성')") || !html.includes('if(!reopened){if(existingTarget)Object.assign(existingTarget,manualTarget)')) {
  throw new Error('Repeated same-day manual checkout must reopen its cancelled cleaning target before replacing the ledger snapshot.');
}
for (const contract of [
  'filter(reservation=>reservation.id!==activeReservation?.id).find(reservation=>reservation.checkInAt>=actualCheckoutAt)',
  'nextCheckinSnapshot=sameDayNext?nextReservation.checkInAt.slice(11,16):DEFAULT_CHECKIN_TIME',
  'checkin:nextCheckinSnapshot,deadline:nextDeadlineSnapshot',
  'checkinSnapshot:nextCheckinSnapshot,deadlineSnapshot:nextDeadlineSnapshot',
]) {
  if (!html.includes(contract)) throw new Error(`Manual checkout must derive cleaning deadlines from the actual next reservation: ${contract}`);
}
if (html.includes("checkin:room.nextCheckinAt?.slice(11,16)||room.checkin")) {
  throw new Error('Manual checkout must not reuse the departing stay check-in time as the next reservation deadline.');
}
const reservationDraftSyncStart = html.indexOf('function syncReservationCleaningDraft');
const reservationDraftSyncSource = html.slice(reservationDraftSyncStart, html.indexOf('function reservationWorkScheduleFingerprint', reservationDraftSyncStart));
for (const contract of [
  'targetRecord=reservationAssignmentEntryForDate(reservation,date).record',
  "targetRecord?.status==='cancelled'",
  '(targetRecord.cancelledReservationId||null)===reservation.id',
  'oldDate===date',
  'state.drafts=state.drafts.filter(draft=>draft.id!==draftId)',
  'state.selectedDrafts=state.selectedDrafts.filter(id=>id!==draftId)',
]) {
  if (!reservationDraftSyncSource.includes(contract)) throw new Error(`Cancelled same-date reservation draft guard missing: ${contract}`);
}

const sameDayCancelStart = html.indexOf("if(a==='confirm-cancel-cleaning-target')");
const sameDayCancelSource = html.slice(sameDayCancelStart, html.indexOf("if(a==='toggle-week-day')", sameDayCancelStart));
for (const contract of [
  'cleaningCancelReasonError(reasonCode)',
  'cleaningCancelReasonLabel(reasonCode)',
  'cancelReasonCode:reasonCode',
  "status:'cancelled'",
  "cancelledBy:'관리자 · 데모'",
  'cancelledMaidId:selectedMaidId',
  'cancelledNotifiedMaidId:notifiedMaidId',
  'cancelledOrder:assignment.order??null',
  'cancelledPreviousOrder:notifiedOrder??null',
  "cancelledStatus:assignment.status||'unassigned'",
  'cancelledNotifiedAt:assignment.notifiedAt||null',
  'cancelledNotificationRevision:assignment.notificationRevision||null',
  'cancelledReservationId:item.reservationId||null',
  'cancelledObligationKey:cleaningTargetObligationKey(item)',
  'draft.reservationId===item.reservationId',
  "draft.visibility!=='public'",
  'state.selectedDrafts=state.selectedDrafts.filter',
  'commitRemainingNotifiedOrdersAfterCancellation',
  "appendEvent('내 청소 취소 통보'",
  '${reason} · ${routeText}',
  '{maidIds:[notifiedMaidId]}',
  'item.priorJobState',
]) {
  if (!sameDayCancelSource.includes(contract)) throw new Error(`Same-day cleaning cancellation contract missing: ${contract}`);
}
for (const contract of [
  'cancelledNotifiedMaidId:cancelledAssignment.cancelledNotifiedMaidId||null',
  'cancelledPreviousOrder:cancelledAssignment.cancelledPreviousOrder??null',
  'cancelledStatus:cancelledAssignment.cancelledStatus||null',
  'cancelledAssignment.cancelledNotifiedAt||cancelledAssignment.notifiedAt||null',
  'cancelledAssignment.cancelledNotificationRevision??cancelledAssignment.notificationRevision??null',
]) {
  if (!sameDayAddSource.includes(contract)) throw new Error(`Reopened manual cleaning target must retain the full cancellation revision: ${contract}`);
}
if (!html.includes('const CLEANING_CANCEL_REASONS=Object.freeze') || !html.includes('Object.entries(CLEANING_CANCEL_REASONS)') || !html.includes('<select id="cleaning-cancel-reason"')) {
  throw new Error('Same-day cleaning cancellation must use controlled reason choices.');
}
const manualCheckoutStayoverStart = html.indexOf('function cancelPendingStayoverTargetsAfterCheckout');
const manualCheckoutStayoverSource = html.slice(manualCheckoutStayoverStart, html.indexOf('function assignmentTypeId', manualCheckoutStayoverStart));
for (const contract of [
  "item.kind!=='연박 청소'",
  "targetEffectiveDate(item,'')<state.selectedDate",
  'Object.values(state.cleaningTargets||{}).forEach(addCandidate)',
  'Object.values(state.assignments||{}).forEach(record=>addCandidate(record?.committedTarget))',
  'Object.values(state.cleaningAttempts||{}).forEach',
  'closed:true',
  "closeStatus:'cancelled'",
  "attempt.status='superseded'",
  "status:'cancelled'",
  'cancelledNotifiedAt:assignment.notifiedAt||null',
  'commitRemainingNotifiedOrdersAfterCancellation',
  "appendEvent('내 투숙 중 청소 요청 취소'",
]) {
  if (!manualCheckoutStayoverSource.includes(contract)) throw new Error(`Manual checkout must close every future unstarted stayover target: ${contract}`);
}
for (const contract of [
  'cancelPendingStayoverTargetsAfterCheckout(id)',
  'cancelledStayoverDraftIds',
  'state.selectedDrafts=state.selectedDrafts.filter',
]) {
  if (!html.includes(contract)) throw new Error(`Manual checkout stayover cancellation contract missing: ${contract}`);
}
if (html.includes('<textarea id="cleaning-cancel-reason"') || html.includes('<input id="cleaning-cancel-reason"')) {
  throw new Error('Same-day cleaning cancellation must not persist free-form reasons that can contain personal data.');
}
if (sameDayCancelSource.includes('delete state.assignments') || sameDayCancelSource.includes('delete state.cleaningTargets')) {
  throw new Error('Same-day cleaning cancellation must preserve assignment and target history as tombstones.');
}
if (sameDayCancelSource.includes('manualAssignmentTargets=') || sameDayCancelSource.includes('manualAssignmentTargets.splice')) {
  throw new Error('Same-day cleaning cancellation must not delete the manual target tombstone.');
}
const maidCancelNoticeStart = sameDayCancelSource.indexOf("if(notifiedMaidId)");
const maidCancelNoticeSource = sameDayCancelSource.slice(maidCancelNoticeStart, sameDayCancelSource.indexOf('historyReturnFocus', maidCancelNoticeStart));
if (!sameDayCancelSource.includes('reason=cleaningCancelReasonLabel(reasonCode)') || !maidCancelNoticeSource.includes('${reason}')) {
  throw new Error('Maid cancellation notifications must use the selected controlled reason label.');
}

const assignmentSaveStart = html.indexOf("if(a==='save-assignments')");
const assignmentSaveSource = html.slice(assignmentSaveStart, html.indexOf("if(a==='set-availability')", assignmentSaveStart));
const assignmentOrderMoveStart = html.indexOf("if(a==='move-assignment-order')");
const assignmentOrderMoveSource = html.slice(assignmentOrderMoveStart, assignmentSaveStart);
for (const contract of ['needsAttemptBridge', 'beginCleaningAttempt(item.room', 'sameDay&&existingAttempt&&!existingAttempt.startedAt', 'assignment.notifiedAt=', 'assignment.notificationRevision=']) {
  if (!assignmentSaveSource.includes(contract)) throw new Error(`Same-day assignment execution bridge contract missing: ${contract}`);
}
for (const contract of ['affectedMaidIds.forEach', 'if(assignment.maidId!==maidId)return', '{maidIds:[maidId]}', '미배정 객실 정보 제외']) {
  if (!assignmentSaveSource.includes(contract)) throw new Error(`Old/new maid notification audience contract missing: ${contract}`);
}
if (!assignmentOrderMoveSource.includes('if(!cleaningTargetCanAdjust(other))')) {
  throw new Error('Maid order swaps must recheck the adjacent target before changing either order.');
}

const notifiedEntriesStart = html.indexOf('function notifiedAssignmentEntriesForMaid');
const notifiedEntriesSource = html.slice(notifiedEntriesStart, html.indexOf('function assignmentGuestCount', notifiedEntriesStart));
for (const contract of ['ledger?.closed', 'workDate<state.selectedDate', 'workDate>addIsoDays(state.selectedDate,1)', 'attempt?.completedAt', "['submitted','approved','rejected','superseded']", 'activationBlockedBy:record.activationBlockedBy']) {
  if (!notifiedEntriesSource.includes(contract)) throw new Error(`Current maid schedule boundary contract missing: ${contract}`);
}

const maidAlertsStart = html.indexOf('function renderMaidAlerts');
const maidAlertsSource = html.slice(maidAlertsStart, html.indexOf('function renderMaidPay', maidAlertsStart));
for (const contract of [
  "notificationAudienceKey('maid',signedInMaidId())",
  'renderNotificationListMarkup({key',
  'notificationUnreadCount(key)',
  '배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.',
]) {
  if (!maidAlertsSource.includes(contract)) throw new Error(`Maid event notification contract missing: ${contract}`);
}
const directAssignStart = html.indexOf('function openDirectAssign');
const directAssignSource = html.slice(directAssignStart, html.indexOf('function reservationPreviewMarkup', directAssignStart));
if (!directAssignSource.includes('if(roomTarget){pushPageTransition') || !directAssignSource.includes("state.cleaningTab=targetEffectiveDate(roomTarget)===state.selectedDate?'assignment-today':'assignment-tomorrow'")) {
  throw new Error('Ledger-backed cleaning targets must be adjusted through the today/tomorrow assignment board.');
}

const qa = readFileSync(resolve(root, 'WIREFRAME/QA.md'), 'utf8');
const wireframeReadme = readFileSync(resolve(root, 'WIREFRAME/README.md'), 'utf8');
const taskPrompt = readFileSync(resolve(root, 'DOCS/WIREFRAME_TASK_PROMPT.md'), 'utf8');
if (!wireframeReadme.includes('객실 목록은 빠른 비교를 위한 리스트형만 사용한다.')) {
  throw new Error('List-only room view README policy is missing.');
}
for (const qaContract of ['객실 목록 리스트형 단일화와 청소 배지 넘침 방지','PIN 관리','계산 너비 차이가 1px 이하','인접 열을 침범하지 않게 한다']) {
  if (!qa.includes(qaContract)) throw new Error(`List-only room view QA record missing: ${qaContract}`);
}
for (const contract of [
  '추가 검증 · 오늘·내일 배정과 당일 추가·취소·변경 알림',
  '숫자는 미배정 수가 아니라 날짜별 전체 청소대상 수',
  '같은 대상 한 건',
  '정확히 한 번',
  '이전 담당 알림에는 새 메이드 이름이 없었고',
  '남은 순서 1.352호',
  '활성화 보류 / 관리자 확인 대기 · 시작 불가',
  '검수 대기 2→1',
  '이전 취소 이력은 남았다',
  '실제 체크아웃의 미래 연박 취소',
  '남은 순서 1.350호',
  '같은 날 재투숙·재체크아웃',
  '준비 마감 14:30',
  '통보 시각·revision 스냅샷',
  '자유입력 사유 없이 선택형 라벨',
  '취소한 예약의 퇴실 청소는 전일 이월로 다시 나타나지 않았다',
  '실제 푸시·SMS·전화 발송이 아니다',
  'admin-cleaning-day-tabs-1440.png',
  'admin-same-day-adjustment-390.png',
  'maid-same-day-change-notice-390.png',
]) {
  if (!qa.includes(contract)) throw new Error(`Today/tomorrow cleaning QA documentation missing: ${contract}`);
}
for (const contract of ['캘린더 공통 표시 규칙', '일 · 월 · 화 · 수 · 목 · 금 · 토', '공휴일이 겹치면 공휴일 빨간색이 우선', '이후 추가하는 달력도', '우주항공청 2026년 월력요항', '국가법령정보센터 현행 공휴일 규정']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Future calendar README contract missing: ${contract}`);
}
for (const contract of [
  '데모값이 아니라 사용자가 확정한 운영값',
  '스탠다드 `2 / 2명`',
  '프리미어 `2 / 3명`',
  '파셜 오션뷰 프리미어 `2 / 4명`',
  '패밀리 `4 / 6명`',
  '연결 예약과 숙박 인원을 통보 스냅샷으로 고정',
  '메이드의 `근무 일정 / 내 업무 / 알림`에 표시',
  '그 시점의 인원을 수행 회차 스냅샷으로 다시 고정',
  '예약과 연결되지 않은 현장 청소는 `인원 미기록`',
]) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Reservation guest README contract missing: ${contract}`);
}
for (const contract of ['모든 월간 캘린더', '일 · 월 · 화 · 수 · 목 · 금 · 토', '공휴일이 토요일과 겹치면 공휴일 색을 우선', '월요일–일요일 운영 주차 계산은 바꾸지 않고']) {
  if (!taskPrompt.includes(contract)) throw new Error(`Future calendar task contract missing: ${contract}`);
}
if (/고객 배정 가능 기준 109개|장기투숙 중 11개|현재 장기투숙 11개/.test(qa)) {
  throw new Error('Stale 109/11/1 room status contract remains in WIREFRAME/QA.md.');
}
for (const contract of ['초기 투숙 seed 11개', '762호 dataIssue', '객실 정보 수정', '수동 체크아웃', '랜덤 배정', 'admin-room-info-edit-1440.png', 'admin-manual-checkout-390.png', 'admin-random-assignment-1440.png', 'admin-random-assignment-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Room master QA contract missing: ${contract}`);
}
for (const contract of ['간편 예약 원장과 터치 오입력 방지', '청소 담당 표시 제거', '엘리베이터 필터 제거', '객실 상세 연결·뒤로가기', '세로 터치 스크롤', '길게 누른 뒤 가로 선택', 'admin-quick-booking-1440.png', 'admin-quick-booking-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Quick reservation QA contract missing: ${contract}`);
}
for (const contract of ['체크인 → 체크아웃 입력 순서', '다른 고객 일정 비병합', '실제 시각 겹침', '직전 퇴실 청소 재통보']) {
  if (!qa.includes(contract)) throw new Error(`Reservation interval QA contract missing: ${contract}`);
}
for (const contract of ['추가 검증 · 메이드 체크리스트 제거·구역별 사진 전용', 'maid-zone-camera-1440.png', 'maid-zone-camera-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Maid photo-only QA documentation missing: ${contract}`);
}
for (const contract of ['추가 검증 · 켜진 TV 화면 필수 촬영', 'TV 켜짐·화면 출력 확인', '기존 `v6` 작업·제출·검수', '새 작업만 `v7`', 'maid-tv-on-required-390.png', 'admin-tv-on-inspection-1440.png']) {
  if (!qa.includes(contract)) throw new Error(`Required TV-on photo QA documentation missing: ${contract}`);
}
for (const contract of ['추가 검증 · 관리자 설명 간소화와 도움말', 'ⓘ', 'admin-copy-cleanup-1440.png', 'admin-info-tooltip-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Admin copy/help QA documentation missing: ${contract}`);
}
for (const contract of ['추가 검증 · 메이드 설명 간소화와 도움말', '시나리오 코치 0개', 'maid-copy-cleanup-390.png', 'maid-info-tooltip-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Maid copy/help QA documentation missing: ${contract}`);
}
for (const contract of ['추가 검증 · 메이드 근무 가능일 제출 시간', '일요일 12:00부터 23:59까지 제출 가능', '일요일 11:59', '12:00', '22:15', '23:59', '수정 중 마감', '관리자 집계도 9/9', 'maid-weekly-availability-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Maid availability submission window QA contract missing: ${contract}`);
}
for (const contract of [
  '추가 검증 · 전일 미배정·미완료 청소 이월',
  '전일 미배정',
  '배정 후 미시작',
  '진행 중인 같은 수행 회차',
  '현장 완료·업로드',
  '실제 완료일 기준 주급',
  'admin-cleaning-rollover-1440.png',
  'admin-cleaning-rollover-390.png',
  'maid-cleaning-rollover-390.png',
]) {
  if (!qa.includes(contract)) throw new Error(`Cleaning rollover QA documentation missing: ${contract}`);
}
if (!/(?:실물|실기기)[^\n]{0,80}(?:후면 )?카메라[^\n]{0,120}(?:미검증|검증하지 못|확인하지 못)/.test(qa)) {
  throw new Error('Maid zone camera QA must distinguish static/browser checks from unverified physical-device camera behavior.');
}
for (const contract of ['예약정보 수정·예약 취소', '카드·예약표 공통 설정', '취소 사유 선택', '같은 날짜 재예약 격리', '다중 예약 중 한 건', '독립 현장 청소 요청', '비공개 초안·현재 카드 정리', '예정 시각 경과·실제 투숙 경계', '공개·수행·랜덤 초안 경계', '최신 상태 재검사', 'admin-reservation-cancel-1440.png', 'admin-reservation-cancel-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Reservation cancellation QA contract missing: ${contract}`);
}
for (const contract of ['객실 카드 4개 주 상태·일정 우선 배지', '연박 진행 배지', '별도 주의 패널 없이', 'admin-room-four-states-1440.png', 'admin-room-stay-progress-390.png', 'admin-assignment-early-late-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Four-state room card QA contract missing: ${contract}`);
}
for (const contract of ['객실 카드 예약 요약 행 제거', '중복 행 제거', '별도 예약 버튼 유지', '일정 우선 정보 유지', 'admin-room-card-priority-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Compact room-card reservation QA contract missing: ${contract}`);
}
for (const contract of ['근무표 다음 동선 고려 랜덤 배정 흐름', '객실별 담당 수정', '메이드별 청소 순서 수정', '순서 보드 일정 강조', '메이드 카드 총 청소요금', 'admin-maid-order-board-390.png', 'admin-maid-order-total-1440.png']) {
  if (!qa.includes(contract)) throw new Error(`Cleaning assignment flow QA contract missing: ${contract}`);
}
if (html.includes('내일 청소·일정 주의 한눈에') || html.includes('assignmentAttentionItems()')) {
  throw new Error('Redundant assignment attention panel must stay removed.');
}
for (const contract of ['객실별 주간 예약 탐색과 과거 기록', '이전·다음 주 이동', '주차 선택 달력', '과거 예약 기록 읽기 전용', 'admin-reservation-week-1440.png', 'admin-reservation-week-390.png', 'admin-reservation-week-calendar-1440.png', 'admin-reservation-week-calendar-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Weekly reservation QA contract missing: ${contract}`);
}
for (const contract of ['추가 검증 · 예약 숙박 인원과 메이드 표시', '객실 유형별 기본·최대 인원', '간편 예약 기본 인원', '최대 인원 초과 차단', '인원수만 수정·최신본 보호', '재통보 전 기존 인원 유지', '재통보 후 메이드 반영', '메이드 내 업무·청소 상세', '과거 예약 읽기 전용', 'admin-reservation-guests-1440.png', 'admin-reservation-guests-390.png', 'maid-reservation-guests-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Reservation guest QA contract missing: ${contract}`);
}
for (const contract of ['추가 검증 · 투숙 중 현재 예약 수정과 다음 예약 등록', '현재 예약 수정·취소 분리', '다음 예약 별도 등록', '실제 반개구간 겹침', '예정 체크아웃 경과·실제 점유', '체크아웃 미입력 투숙', '청소 출입·업무일 보호', 'admin-occupied-reservation-1440.png', 'admin-occupied-reservation-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Occupied-room reservation QA contract missing: ${contract}`);
}
for (const contract of ['투숙 중`이어도 현재 예약의 일정과 숙박 인원은 수정', '다음 예약은 별도 예약 ID', '예정 체크아웃이 지났는데 실제 점유가 계속되면', '새 예약은 체크아웃을 미래로 갱신하거나 `지금 체크아웃`을 처리할 때까지 잠급니다']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Occupied-room reservation README contract missing: ${contract}`);
}
for (const contract of ['전체 캘린더 일요일–토요일 고정 열', '8/15 광복절', '8/17 대체공휴일 빨간색', '일반 토요일 파란색', '선택 주차 두 행 강조', '공휴일 접근성 이름', 'admin-calendar-standard-1440.png', 'admin-calendar-standard-390.png']) {
  if (!qa.includes(contract)) throw new Error(`Korean calendar QA contract missing: ${contract}`);
}
for (const contract of ['메이드 입력 영역 상시 펼침·제출 자료 수신 정합성', '접기 컨트롤이 0개', '정확한 슬롯 ID', '유형 사진 `12/12장`', '폭탄방 증빙 `2장`', '객실 특이사항 `1건 · 2장`', '읽기 전용으로 표시', 'maid-cleaning-sections-open-390.png', 'maid-evidence-sections-open-390.png', 'admin-inspection-template-parity-1440.png', 'admin-bomb-room-evidence-1440.png']) {
  if (!qa.includes(contract)) throw new Error(`Always-open cleaning submission QA contract missing: ${contract}`);
}
for (const contract of ['메이드 청소 입력 상시 표시와 제출 자료 묶음', '작업 진입 즉시 모든 입력 본문', '일반적인 이미지 종류가 비슷하다는 이유로 다른 슬롯에 사진을 자동 배정하지 않는다', '하나의 제출 자료 묶음', '받은 자료를 숨기지 않고 읽기 전용', '해당 수행 회차에 묶인 특이사항 스냅샷만 표시']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Always-open cleaning submission README contract missing: ${contract}`);
}

const audit = readFileSync(resolve(root, 'DOCS/FINAL_UX_AUDIT.md'));
const auditHash = createHash('sha256').update(audit).digest('hex');
const indexHash = createHash('sha256').update(readFileSync(resolve(root, 'WIREFRAME/index.html'))).digest('hex');
const manifest = JSON.parse(readFileSync(resolve(root, 'manifest.json'), 'utf8'));
const expectedAuditHash = manifest.sha256?.['DOCS/FINAL_UX_AUDIT.md'];
const expectedIndexHash = manifest.sha256?.['WIREFRAME/index.html'];
const checksumLines = readFileSync(resolve(root, 'SHA256SUMS.txt'), 'utf8').trim().split(/\r?\n/);
const checksums = Object.fromEntries(checksumLines.map((line) => {
  const match = line.match(/^([a-f0-9]{64})\s+\*?(.+)$/);
  if (!match) throw new Error(`Invalid SHA256SUMS entry: ${line}`);
  return [match[2], match[1]];
}));
if (auditHash !== expectedAuditHash || indexHash !== expectedIndexHash || checksums['DOCS/FINAL_UX_AUDIT.md'] !== auditHash || checksums['WIREFRAME/index.html'] !== indexHash) {
  throw new Error([
    'Canonical file hash mismatch.',
    `Audit: ${auditHash} (expected ${expectedAuditHash})`,
    `Index: ${indexHash} (expected ${expectedIndexHash})`,
    `SHA256SUMS audit: ${checksums['DOCS/FINAL_UX_AUDIT.md'] || 'missing'}`,
    `SHA256SUMS index: ${checksums['WIREFRAME/index.html'] || 'missing'}`,
  ].join('\n'));
}


const roomCardCopyStart = html.lastIndexOf('      function roomCard(no) {');
const roomCardCopyEnd = html.indexOf('\n      function cleaningLabel(', roomCardCopyStart);
if (roomCardCopyStart < 0 || roomCardCopyEnd < 0) {
  throw new Error('Active roomCard source could not be resolved for copy cleanup checks.');
}
const roomCardCopySource = html.slice(roomCardCopyStart, roomCardCopyEnd);
if (!html.includes('<strong>총 ${ROOMS.length}개 객실</strong>')) {
  throw new Error('Room catalog total-only heading is missing.');
}
if (html.includes('총 ${ROOMS.length}개 객실 · 상태 중복 집계')) {
  throw new Error('Legacy duplicate-count wording remains in the room catalog heading.');
}
for (const forbidden of ['<span>${esc(p.reason)}</span>', '${subBadges}', 'const cleaningSubLabel=']) {
  if (roomCardCopySource.includes(forbidden)) {
    throw new Error(`Visible room-card secondary status remains: ${forbidden}`);
  }
}
for (const requiredContract of [
  '<div class="concept-status-copy"><strong>${esc(p.status)}</strong></div>',
  '${scheduleBadges}${detailBadges}',
  'class="badge-row room-schedule-badges"',
]) {
  if (!roomCardCopySource.includes(requiredContract)) {
    throw new Error(`Room-card primary-status or upper-badge contract missing: ${requiredContract}`);
  }
}

console.log(`Required files: ${required.length}/${required.length}`);
console.log(`Inline scripts parsed: ${inlineScripts.length}`);
console.log(`Large-team assignment fixture: ${maidIds.length} maids`);
for (const contract of [
  "if('scrollRestoration' in history)history.scrollRestoration='manual';",
  'let modalPageScrollY=null,modalScrollRestoreFrame=0,modalHistoryReturnScrollY=null,modalScrollRestoreTimer=0;',
  "root.style.scrollBehavior='auto';window.scrollTo(0,y);root.style.scrollBehavior=previous;",
  'modalScrollRestoreTimer=setTimeout(()=>{restore();modalScrollRestoreTimer=0;},90);',
  'scheduleWindowScrollRestore(Math.max(0,Number(route.scrollY)||0))',
  "if(isWireframeHistory(current)&&current.layer==='page')history.replaceState({...current,route},'',historyRouteUrl(route));",
  "else if(a==='close-modal'||a==='backdrop-close')dismissModal();",
  'modalHistoryReturnScrollY=modalPageScrollY;',
  'route=modalHistoryReturnScrollY==null?baseRoute:{...baseRoute,scrollY:modalHistoryReturnScrollY}',
  'function lockModalViewport(scrollY=window.scrollY)',
  'function restoreModalViewport({restore=true}={})',
  'function historyRouteSnapshot(scrollY=modalPageScrollY??window.scrollY)',
  'rawCloseModal({restoreFocus=false,restoreScroll=true}={})',
  "trigger?.focus?.({preventScroll:true})",
  "function quickGridUsesInternalVerticalScroll() { return !window.matchMedia('(max-width: 720px)').matches; }",
  'overflow-x:auto; overflow-y:hidden; overscroll-behavior-x:contain; overscroll-behavior-y:auto;',
  'data-action="filter-room-type"',
  "if(a==='filter-room-type')",
  "state.roomTypeFilter=typeId;state.roomFilter='all';state.roomSearch='';",
  '.catalog-summary { display:grid; grid-template-columns:minmax(0,1.5fr) repeat(5,minmax(88px,.5fr));',
  '.catalog-summary-stat[data-type="all"] { grid-column:1/-1; }',
  "{id:'all',name:'전체 객실',count:ROOMS.length}",
  'data-type="${item.id}" aria-pressed="${state.roomTypeFilter===item.id}"',
  "typeId==='all'||ROOM_TYPES[typeId]",
  'id="quick-grid-mobile-header"',
  '.quick-grid-mobile-header { position:sticky; top:var(--topbar);',
  '.quick-grid-scroller .quick-grid-header { display:none; }',
  'function syncQuickGridHorizontalScroll(source)',
  "['quick-grid-scroller','quick-grid-mobile-header'].includes(target?.id)",
]) {
  if (!html.includes(contract)) throw new Error(`Modal/quick-booking/type-filter UX contract missing: ${contract}`);
}

for (const contract of [
  '모바일 고정 날짜 머리글·전체 객실 필터',
  '날짜 머리글 상단이 앱 바 하단과 2px 이내',
  'admin-quick-booking-sticky-header-390.png',
  'admin-room-total-filter-1440.png',
]) {
  if (!qa.includes(contract)) throw new Error(`Sticky date/total-room QA documentation missing: ${contract}`);
}
for (const contract of [
  '모바일 고정 날짜 머리글·전체 객실 필터',
  '고정 날짜 머리글과 객실 예약 본문의 가로 위치는 양방향으로 동기화',
  '`전체 객실`이다',
  '121개 객실 전체',
]) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Sticky date/total-room README documentation missing: ${contract}`);
}

for (const contract of [
  'quickReservationAnchorDate',
  'QUICK_RESERVATION_PAST_DAYS=7',
  'QUICK_RESERVATION_FUTURE_DAYS=21',
  'QUICK_RESERVATION_DAY_COUNT=QUICK_RESERVATION_PAST_DAYS+1+QUICK_RESERVATION_FUTURE_DAYS',
  'function quickWindowBounds(',
  'function quickWindowDates(',
  'function reservationInQuickWindow(',
  'data-offset="-7"',
  'data-offset="7"',
  "params.set('bookingAnchor',route.quickAnchor)",
  '지난 날짜 · 조회만 가능',
  'is-month-start',
  'function quickGridAnchorScrollLeft(',
  'reservation-demo-cross-month-516',
  'reservation-demo-cross-month-623',
  '선택한 29일 기준',
]) {
  if (!html.includes(contract)) throw new Error(`Quick reservation 29-day contract missing: ${contract}`);
}
if (html.includes('function quickMonthDates(') || html.includes('function reservationInMonth(')) {
  throw new Error('Legacy month-bounded quick reservation helpers remain.');
}
for (const contract of ['간편 예약 29일 연속 보기', '`-7일 ~ +21일`', 'bookingAnchor=YYYY-MM-DD']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Quick reservation 29-day README contract missing: ${contract}`);
}
for (const contract of ['간편 예약 29일 연속 보기', '2026-08-08~2026-09-05', '8/31~9/3 연박']) {
  if (!qa.includes(contract)) throw new Error(`Quick reservation 29-day QA contract missing: ${contract}`);
}

for (const contract of [
  'function inspectionTemplateUploadItems(',
  'function inspectionTemplateGroups(',
  'function inspectionTemplatePhotoState(',
  'function renderInspectionTemplatePhoto(',
  'function renderInspectionTemplateGroup(',
  'function renderInspectionTemplateReview(',
  'template?.photos||[]',
  'actualById=new Map',
  "status:actual?.status||'missing'",
  'data-template-photo=',
  'data-template-zone=',
  'data-template-required=',
  'data-template-status=',
  '메이드 청소 템플릿 기준 검수',
  '제출 당시 구역·항목·순서 그대로 확인',
  '사진 누락',
  'TV 항목은 켜짐·화면 출력 요구사항까지 확인하세요.',
  '${renderInspectionTemplateReview(no,submissionTemplate,submission,attempt)}',
]) {
  if (!html.includes(contract)) throw new Error(`Admin/maid inspection-template parity contract missing: ${contract}`);
}
const activeInspectionStart=html.lastIndexOf('function renderInspectionDetail(no)');
const activeInspectionEnd=html.indexOf('function renderPayDetail()',activeInspectionStart);
const activeInspectionSource=html.slice(activeInspectionStart,activeInspectionEnd);
if(activeInspectionStart<0||activeInspectionEnd<=activeInspectionStart||activeInspectionSource.includes('renderInspectionGallery(no)')||activeInspectionSource.includes('submittedUploads.length')){
  throw new Error('Active admin inspection still uses the legacy flat photo gallery.');
}
for (const contract of ['관리자 검수·메이드 청소 템플릿 통일','templateSnapshot','사진 누락','TV 켜짐·화면 출력 항목']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Inspection-template parity README contract missing: ${contract}`);
}
for (const contract of ['관리자 검수·메이드 청소 템플릿 통일','필수 완료/전체 필수','전송 실패·필수 누락','data-template-version']) {
  if (!qa.includes(contract)) throw new Error(`Inspection-template parity QA contract missing: ${contract}`);
}

for (const contract of [
  'function durableLedgerSnapshot(',
  'function durableLedgerFingerprint(',
  'function assertNoDuplicateDurableRecords(',
  "throw new Error('렌더링 중 예약·청소 제출·급여·지급 원장이 변경되었습니다.')",
  'function reservationPayloadMatches(',
  'duplicateReservation=!id?',
  'unchangedReservation=!!previous',
  'duplicate:true,unchanged:true',
  'dedupeKey:`reservation:${reservation.id}:${reservationFingerprint(reservation)}`',
  'function submissionForAttempt(',
  'function createCleaningSubmissionRecord(',
  'submissionId=`submission-${attemptId}`',
  'dedupeKey:`submission:${attemptId}`',
  'dedupeKey:`approval:${submission.id}:paid`',
  'if(previous.status===status)return previous.status',
  'mutationActionLocks=new Set()',
  'mutationActions=new Set(',
  'window.__CASTLE_TEST__=Object.freeze',
  'repeatRender:',
  'createReservationTest:',
  'prepareSubmission:',
  'confirmEarning:',
  'setPaymentStatus:',
]) {
  if (!html.includes(contract)) throw new Error(`Reservation/cleaning/payroll idempotency contract missing: ${contract}`);
}
const upsertIdempotencyStart=html.indexOf('function upsertReservationRecord');
const upsertIdempotencyEnd=html.indexOf('function clearOrphanedReservationDraftJob',upsertIdempotencyStart);
const upsertIdempotencySource=html.slice(upsertIdempotencyStart,upsertIdempotencyEnd);
if(!upsertIdempotencySource.includes('duplicateReservation')||!upsertIdempotencySource.includes('unchangedReservation')||upsertIdempotencySource.indexOf('duplicateReservation')>upsertIdempotencySource.indexOf('++state.reservationSequence')){
  throw new Error('Reservation duplicate guard must run before generating a new reservation ID.');
}
const submissionIdempotencyStart=html.indexOf('function createCleaningSubmissionRecord');
const submissionIdempotencyEnd=html.indexOf('function activeBombRoomReport',submissionIdempotencyStart);
const submissionIdempotencySource=html.slice(submissionIdempotencyStart,submissionIdempotencyEnd);
if(!submissionIdempotencySource.includes('submissionForAttempt(attemptId)')||/Date\.now\(|\+\+cleaningSubmissionSequence/.test(submissionIdempotencySource)){
  throw new Error('Cleaning submission identity must be stable per attempt and must not use time/random sequence IDs.');
}
for (const contract of ['예약·청소·급여 멱등성과 중복 방지','DB 유니크 제약','API idempotency key']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Idempotency README contract missing: ${contract}`);
}
for (const contract of ['예약·청소·급여 멱등성·중복 방지 회귀 검사','render()`를 12회','같은 청소 `attemptId`','earningRecords[submissionId]']) {
  if (!qa.includes(contract)) throw new Error(`Idempotency QA contract missing: ${contract}`);
}

console.log('Per-maid weekly payment static contracts: passed');
console.log('Admin copy/help static contracts: passed');
console.log('Maid copy/help static contracts: passed');
console.log('Maid photo-only workflow static contracts: passed');
console.log('Required TV-on checkout photo static contracts: passed');
console.log('Maid availability submission window static contracts: passed');
console.log('Cleaning rollover static contracts: passed');
console.log('Reservation guest-count static contracts: passed');
console.log('Portable path scan: passed');
console.log(`Room master contract: ${catalogIds.length} rooms / ${initialOccupiedIds.length} initially occupied / ${dataIssueIds.length} data issue`);
console.log(`Final UX audit SHA-256: ${auditHash}`);
console.log(`Wireframe SHA-256: ${indexHash}`);
console.log('Manifest hashes: passed');
for (const contract of [
  'manualCleaningSequence:0, manualCleaningRequests:{}',
  'function activeManualCleaningRequest(no,targetState=state)',
  'function createManualCleaningRequest(no)',
  'function cancelManualCleaningRequest(no)',
  'function completeManualCleaningRequestForAttempt(no,attempt)',
  'data-action="toggle-room-cleaning"',
  "if(a==='confirm-room-cleaning-on')",
  "if(a==='confirm-room-cleaning-off')",
  'if(activeManualCleaningRequest(no))return true;',
]) {
  if (!html.includes(contract)) throw new Error(`Manual cleaning toggle contract missing: ${contract}`);
}
const manualCleaningActionSet = html.slice(html.indexOf('const rebuiltActions='), html.indexOf('const deprecatedStateActions='));
if (!manualCleaningActionSet.includes("'toggle-room-cleaning'") || !manualCleaningActionSet.includes("'confirm-room-cleaning-on'") || !manualCleaningActionSet.includes("'confirm-room-cleaning-off'")) {
  throw new Error('Manual cleaning toggle actions are not registered.');
}
console.log('Manual room-cleaning toggle static contracts: passed');

for (const contract of [
  'function operationalMoment(targetState=state)',
  'function reservationAtOperationalMoment(roomNo,targetState=state)',
  'function latestCheckedOutReservationForRoom(roomNo,targetState=state)',
  'function roomCheckoutCleaningDue(no,targetState=state)',
  "reservation.checkInAt<=moment&&moment<reservation.checkOutAt",
  '입실·퇴실은 예약 시각에 자동 반영됩니다.',
]) {
  if (!html.includes(contract)) throw new Error(`Automatic occupancy contract missing: ${contract}`);
}
const occupancyActionsSource=html.slice(html.indexOf('const rebuiltActions='),html.indexOf('const deprecatedStateActions='));
for (const removed of ["'manual-checkout'","'confirm-manual-checkout'","'manual-checkin'","'confirm-manual-checkin'"]) {
  if (occupancyActionsSource.includes(removed)) throw new Error(`Manual occupancy action remains registered: ${removed}`);
}
console.log('Automatic reservation occupancy static contracts: passed');

for (const contract of [
  'checkoutInspections:{}',
  'function checkoutInspectionPending(no,targetState=state)',
  'function completeCheckoutInspection(no,{method=\'manual\',attempt=null}={})',
  'function completeCheckoutInspectionForAttempt(no,attempt)',
  'function renderCheckoutInspectionPanel(no)',
  'data-filter="checkout-inspection"',
  'value="checkout-inspection"',
  "'complete-checkout-inspection'",
  "if(a==='confirm-checkout-inspection')",
]) {
  if (!html.includes(contract)) throw new Error(`Checkout inspection contract missing: ${contract}`);
}
if (!html.includes('completeCheckoutInspectionForAttempt(id,attempt)')) throw new Error('Field completion does not clear checkout inspection.');
console.log('Checkout inspection static contracts: passed');

for (const contract of [
  'id="scroll-to-top"',
  'aria-label="맨 위로 이동"',
  'const SCROLL_TOP_THRESHOLD=600',
  'function scrollTopButtonShouldShow()',
  "window.addEventListener('scroll',scheduleScrollTopButtonSync,{passive:true})",
  "window.matchMedia('(prefers-reduced-motion: reduce)').matches",
  "window.scrollTo({top:0,left:0,behavior:'smooth'})",
  "body.modal-open .scroll-top-button",
  "bottom: calc(var(--bottom-nav) + env(safe-area-inset-bottom) + 14px)",
]) {
  if (!html.includes(contract)) throw new Error(`Scroll-to-top contract missing: ${contract}`);
}
if ((html.match(/id="scroll-to-top"/g)||[]).length!==1) throw new Error('Scroll-to-top button must exist exactly once.');
if ((html.match(/window\.addEventListener\('scroll',scheduleScrollTopButtonSync/g)||[]).length!==1) throw new Error('Scroll-to-top listener must be registered exactly once.');
console.log('Scroll-to-top static contracts: passed');

for (const contract of [
  'const TYPE_LAYOUT_PROFILES=Object.freeze({',
  "composition:'원룸형 메인 공간 1 · 주방 1 · 욕실 1'",
  "composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1'",
  "composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1'",
  "composition:'주방 1 · 거실 1 · 침실 2 · 욕실 2'",
  'function templateRepresentativeRoom(template)',
  'function templateFixedSnapshot(template)',
  'function photoSlotContract(items=[])',
  'function templateSlotStats(template)',
  'function typeTemplateParity(typeId,kind=\'퇴실 청소\')',
  'data-template-fixed-slot="${esc(item.id)}"',
  'data-template-fixed-grid',
  '메이드 고정 촬영 슬롯',
  '객실번호 → 타입 → 타입별 고정 구성 → 고정 사진 슬롯',
  '메이드 제출 기준 ${expectedItems.length}개 슬롯 · 관리자 검수 ${items.length}개 슬롯',
  'data-template-contract-match="${structureMatches?\'true\':\'false\'}"',
  "snapshot?.photos?.some(item=>item.id==='tv-on'||String(item.id).startsWith('tv-on-'))",
  '일반 슬롯은 1장, 기타 슬롯은 최대 10장을 유지합니다.',
  'function enforceCleaningPhotoRequirementRules(items=[])',
  'data-template-max-photos="${photoUploadLimit(item)}"',
  'typeTemplateParity:(typeId,kind=\'퇴실 청소\')=>',
  'templateVersionAudit:roomNo=>',
]) {
  if (!html.includes(contract)) throw new Error(`Fixed type template contract missing: ${contract}`);
}
const templateDetailStart=html.indexOf("function renderTemplateDetail(id,mode='view')");
const templateDetailEnd=html.indexOf('function readTemplateChange',templateDetailStart);
const templateDetailSource=html.slice(templateDetailStart,templateDetailEnd);
if(templateDetailStart<0||templateDetailEnd<=templateDetailStart)throw new Error('Template detail source block not found.');
if(!templateDetailSource.includes('fixedPhotos.map((item,index)=>'))throw new Error('Admin template detail does not render fixed type slots.');
if(templateDetailSource.includes('roomSelector')||templateDetailSource.includes('previewRoomNo'))throw new Error('Admin template detail still contains room-specific preview logic.');
const inspectionReviewStart=html.indexOf('function renderInspectionTemplateReview');
const inspectionReviewEnd=html.indexOf('function openInspectionPhoto',inspectionReviewStart);
const inspectionReviewSource=html.slice(inspectionReviewStart,inspectionReviewEnd);
if(!inspectionReviewSource.includes('photoSlotContractSignature(expectedItems)===photoSlotContractSignature(items)'))throw new Error('Admin inspection does not verify the submitted slot contract.');
for(const stale of ["${esc(upload.label)} · ${upload.required?'필수':'선택'}", "${esc(upload.description||'청소 완료 상태를 촬영합니다.')}"]){
  if(inspectionReviewSource.includes(stale))throw new Error(`Admin inspection still renders redundant slot copy: ${stale}`);
}
const taskZoneCardStart=html.indexOf('function taskPhotoCollectionMarkup');
const taskZoneCardEnd=html.indexOf('function groupsafe',taskZoneCardStart);
const taskZoneCardSource=html.slice(taskZoneCardStart,taskZoneCardEnd);
for(const stale of ["${esc(upload.label)} · ${upload.required?'필수':'선택'}", "${esc(upload.description||'청소 완료 상태를 촬영합니다.')}"]){
  if(taskZoneCardSource.includes(stale))throw new Error(`Maid photo card still renders redundant slot copy: ${stale}`);
}
if(html.includes("{id:'entry-number',zone:'현관',label:'객실번호·현관'"))throw new Error('Current templates still contain the redundant room-number entrance slot.');
if((html.match(/required:false,fixture:'supply',multiple:true,maxPhotos:10/g)||[]).length!==6)throw new Error('All six optional evidence slots must use maxPhotos 10.');
if((html.match(/zone:'기타'/g)||[]).length<6||html.includes("zone:'선택 증빙'"))throw new Error('Optional evidence zone must be named 기타 everywhere.');
for(const contract of [
  'function photoUploadLimit(upload)',
  'function uploadPhotoCollection(upload)',
  'function cloneUploadEvidence(upload)',
  'data-max-photos="${limit}"',
  'data-template-max-photos="${photoUploadLimit(upload)}"',
  'otherPhotoCount:other?uploadPhotoCount(other):0',
  'otherMaxPhotos:other?photoUploadLimit(other):0',
]) if(!html.includes(contract))throw new Error(`Other-photo collection contract missing: ${contract}`);
for(const removed of ['ROOM_LAYOUT_PROFILES','DEFAULT_LAYOUT_PROFILES','template-preview-room','templateSlotRange','레이아웃 확인 보류','최소 공통 슬롯','필수 촬영 구역 ${requiredUploads.length}개','여러 장 허용',"snapshot?.version==='v7'"]){
  if(html.includes(removed))throw new Error(`Obsolete or contradictory template contract remains: ${removed}`);
}
if(!html.includes("version:'v6'")||!html.includes("filter(item=>item.id!=='tv-on')"))throw new Error('Historical v6 snapshot preservation contract is missing.');
console.log('Fixed type template static contracts: passed');

console.log('Workspace check: passed');

const currentAdminTodayStart = html.lastIndexOf('function renderAdminToday()');
const currentAdminTodayEnd = html.indexOf('\n      function maidName(', currentAdminTodayStart);
if (currentAdminTodayStart < 0 || currentAdminTodayEnd < 0) {
  throw new Error('Current admin-today render block could not be isolated.');
}
const currentAdminToday = html.slice(currentAdminTodayStart, currentAdminTodayEnd);
for (const required of [
  "renderAccordion('assignment','오늘 청소 배정'",
  "renderAccordion('inspection','청소 검수'",
]) {
  if (!currentAdminToday.includes(required)) throw new Error(`Admin-home core item missing: ${required}`);
}
for (const forbidden of [
  'class="availability-link"',
  "renderAccordion('schedule','오늘 체크인·체크아웃'",
  '${cancelAccordion}',
  "renderAccordion('drafts','배정 준비 청소 작업'",
  "renderAccordion('inspection','검수 대기'",
  "renderAccordion('pay','지난주 지급'",
]) {
  if (currentAdminToday.includes(forbidden)) throw new Error(`Removed admin-home item still rendered: ${forbidden}`);
}
console.log('Admin-home cleaning-only static contracts: passed');

const notificationContracts = [
  'const NOTIFICATION_SCHEMA_VERSION=1',
  'function notificationPolicyForEvent(',
  'function notificationBundlesForKey(',
  'function notificationUnreadCount(',
  'function markNotificationRead(',
  'function markAllNotificationsRead(',
  'function renderNotificationListMarkup(',
  "data-action=\"notification-open\"",
  "data-action=\"notification-mark-all-read\"",
  "data-action=\"notification-toggle-push\"",
  'NOTIFICATION_BUNDLE_WINDOW_MINUTES=10',
  '서비스 워커',
  "const alertCount=notificationUnreadCount(notificationAudienceKey())",
  "if(actorRole==='maid')",
  "if(/청소 전체 제출|검수 요청|재검수 요청/.test(text))",
  "appendEvent('기기 푸시 설정 변경'",
];
for (const contract of notificationContracts) {
  if (!html.includes(contract)) throw new Error(`Event notification contract missing: ${contract}`);
}
const notificationOpenStart = html.indexOf('function openAlerts()');
const notificationOpenEnd = html.indexOf('function openPublishConfirm()', notificationOpenStart);
const notificationOpenSource = html.slice(notificationOpenStart, notificationOpenEnd);
if (notificationOpenStart < 0 || notificationOpenEnd < 0) throw new Error('Notification center source could not be isolated.');
for (const forbidden of [
  "const items=[['350호 입실 미준비'",
  "title:'알림 현황 · 데모'",
  "'동기화',state.network",
  "검수 대기',`${pendingInspections}건",
]) {
  if (notificationOpenSource.includes(forbidden)) throw new Error(`Legacy static alert summary remains: ${forbidden}`);
}
const actionAlertStart = html.indexOf('function openActionAlerts(');
const actionAlertEnd = html.indexOf('function adminAuditSummary(', actionAlertStart);
const actionAlertSource = html.slice(actionAlertStart, actionAlertEnd);
if (!actionAlertSource.includes('openNotificationCenter(trigger)')) throw new Error('Action alert entry point does not use the unified event center.');
if (actionAlertSource.includes('최신 상태') || actionAlertSource.includes('0건')) throw new Error('Static zero/sync alert rows remain in action alert entry point.');
console.log('Event notification center static contracts: passed');

const maidPayLedgerStart = html.indexOf('function renderMaidPayFromLedger()');
const maidPayRenderStart = html.indexOf('function renderMaidPay()');
if (maidPayLedgerStart < 0 || maidPayRenderStart < 0 || maidPayLedgerStart > maidPayRenderStart) {
  throw new Error('Maid pay ledger renderer was removed while replacing the maid notification screen.');
}
if (html.includes('__CASTLE_NOTIFICATION_QA__')) {
  throw new Error('Notification QA mutation bridge must not be present in the shipped wireframe.');
}
console.log('Maid pay ledger notification regression contracts: passed');

const inspectionWordingContracts = [
  "cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)",
  "button('검수 대상 목록 열기','go-inspection','outline')",
  "inspection:'검수 요청됨'",
  "next:'검수 대상 목록 탭에서 639호 전체 제출을 검수하세요.'",
  '관리자에게 처리해야 할 업무 큐는 `검수 대상 목록`',
  '개별 청소 제출 상태는 `검수 요청됨`',
];
for (const contract of inspectionWordingContracts) {
  if (!html.includes(contract) && !wireframeReadme.includes(contract)) {
    throw new Error(`Inspection target-list wording contract missing: ${contract}`);
  }
}
const inspectionWordingCleaningHubStart = html.lastIndexOf('function renderCleaningHub()');
const inspectionWordingCleaningHubEnd = html.indexOf('function taskRow(', inspectionWordingCleaningHubStart);
const inspectionWordingCleaningHubSource = html.slice(inspectionWordingCleaningHubStart, inspectionWordingCleaningHubEnd);
if (inspectionWordingCleaningHubStart < 0 || inspectionWordingCleaningHubEnd < 0) throw new Error('Current cleaning hub source could not be isolated.');
if (inspectionWordingCleaningHubSource.includes("cleaningTabButton('inspection','검수 대기'")) {
  throw new Error('Legacy admin inspection tab wording remains.');
}
const currentAdminTodayStartForInspectionWording = html.lastIndexOf('function renderAdminToday()');
const currentAdminTodayEndForInspectionWording = html.indexOf('\n      function maidName(', currentAdminTodayStartForInspectionWording);
const currentAdminTodayForInspectionWording = html.slice(currentAdminTodayStartForInspectionWording, currentAdminTodayEndForInspectionWording);
if (currentAdminTodayForInspectionWording.includes("button('검수 대기 열기'")) {
  throw new Error('Legacy admin-home inspection entry wording remains.');
}
console.log('Inspection target-list wording static contracts: passed');

for (const demoQuickWindowContract of [
  "const DEMO_TODAY='2026-08-15'",
  "quickReservationAnchorDate:'2026-08-15', quickReservationFollowsToday:true",
  'function refreshQuickReservationActualToday({rerender=false}={})',
  'const today=DEMO_TODAY;',
  'else{state.quickReservationAnchorDate=DEMO_TODAY;state.quickReservationFollowsToday=true;}',
  'state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;',
  'data-action="quick-month-today">오늘</button>',
  '.quick-month-tools > [data-action="quick-month-today"] { grid-column:1/-1; width:100%; min-height:44px; }',
  '8월 15일 기준 29일',
  '간편 예약 · 8월 15일 기준',
  '.quick-booking-page { display:grid; grid-template-columns:minmax(0,1fr); gap:14px; min-width:0; }',
  '.quick-booking-toolbar { grid-template-columns:minmax(0,1fr); padding:11px; }',
  '.quick-month-tools { grid-column:auto; min-width:0; width:100%; }',
  '.quick-grid-shell { overflow-x:clip; overflow-y:visible; }',
  'box-shadow:inset 0 -1px 0 rgba(20,36,55,.12);',
  "today=iso===actualToday,isPast=iso<actualToday",
]) {
  if (!html.includes(demoQuickWindowContract)) throw new Error(`Demo-date quick-window contract missing: ${demoQuickWindowContract}`);
}
for (const liveDateQuickWindowContract of [
  'const today=kstTodayIso();',
  'state.quickReservationAnchorDate=kstTodayIso()',
  '한국 시간 오늘 기준 29일',
  '매일 실제 오늘의 7일 전부터 21일 뒤까지',
]) {
  if (html.includes(liveDateQuickWindowContract)) throw new Error(`Live-date quick-window coupling remains in the mock: ${liveDateQuickWindowContract}`);
}
if (!wireframeReadme.includes('목업의 고정 기준일 `2026-08-15`')) {
  throw new Error('Demo-date quick-window README policy is missing.');
}
for(const contract of ['`오늘` 버튼을 누르면', '420px 이하에서는 이전·기간·다음 조작 아래의 독립 행']) {
  if(!wireframeReadme.includes(contract))throw new Error(`Mobile today-button README contract missing: ${contract}`);
}
console.log('Demo-date quick-window static contracts: passed');

for (const contract of [
  'function setMaidStatusFor(maidId,status)',
  'function maidDeactivationFor(maidId)',
  'function ensureMaidDeactivationFor(maidId)',
  'function maidDeactivationBlockers(maidId)',
  'function renderMaidAccountManagement(maidId)',
  'data-maid-account-management="${maidId}"',
  'data-maid-id="${maidId}"',
  "openMaidDeactivationV2(maidId,el)",
  "setMaidStatusFor(maidId,'deactivating')",
  "setMaidStatusFor(maidId,'inactive')",
  '모든 메이드에 동일한 계정 관리·이력 보존 규칙 적용',
]) {
  if (!html.includes(contract)) throw new Error(`All-maid deactivation contract missing: ${contract}`);
}
const maidDetailStartForAccountManagement=html.indexOf('function renderMaidDetail(id)');
const maidDetailEndForAccountManagement=html.indexOf('function renderComplaintDetail()',maidDetailStartForAccountManagement);
const maidDetailSourceForAccountManagement=html.slice(maidDetailStartForAccountManagement,maidDetailEndForAccountManagement);
if (maidDetailSourceForAccountManagement.includes("if(m.id!=='m1')")) throw new Error('Non-m1 early return still hides deactivation controls.');
const historyIndexForAccountManagement=maidDetailSourceForAccountManagement.indexOf('data-maid-history="${m.id}"');
const accountManagementIndex=maidDetailSourceForAccountManagement.indexOf('renderMaidAccountManagement(m.id)');
if (historyIndexForAccountManagement<0||accountManagementIndex<historyIndexForAccountManagement) throw new Error('Maid account management is not below the work-history section.');
const accountStatusCardEnd=maidDetailSourceForAccountManagement.indexOf('</section><section class="card card-pad"><div class="section-head"><h3>업무 영향 요약');
if (maidDetailSourceForAccountManagement.slice(0,accountStatusCardEnd).includes('deactivate-maid-v2')) throw new Error('Deactivation button still appears in the upper account-status card.');
const finalWorkforceStart=html.lastIndexOf('function renderWorkforce()');
const finalWorkforceEnd=html.indexOf('function payrollDateLabel(',finalWorkforceStart);
const finalWorkforceSource=html.slice(finalWorkforceStart,finalWorkforceEnd);
if (!finalWorkforceSource.includes('accountStatus=maidStatusFor(maid.id)')) throw new Error('Workforce cards do not show per-maid account status.');
console.log('All-maid lower account-management deactivation contracts: passed');

for (const contract of [
  "function detailHeader(title,subtitle='')",
  "${subtitle?`<p>${subtitle}</p>`:''}",
  '<h2 id="summary-title">오늘 객실 요약</h2></div></div><div class="today-summary">',
  '<span>투숙 중</span><strong>${occupiedCount}</strong></button>',
  '<span>청소 필요</span><strong>${cleaningCount}</strong></button>',
  '<span>배정 가능</span><strong>${availableCount}</strong></button>',
  '<span>배정 불가</span><strong>${blockedCount}</strong></button>',
  "detailHeader(`${active?.maid||'김민지1'} ${active?.type||'컴플레인'}`)",
  '.today-summary .metric-card { min-height:96px;',
]) {
  if (!html.includes(contract)) throw new Error(`Essential-copy contract missing: ${contract}`);
}
for (const forbidden of [
  '현재 점유 · 회색',
  '퇴실·연박 청소 · 주황',
  '공실·준비 완료 · 초록',
  '촛불·차단 특이사항 등 · 빨강',
  '네 가지 주 상태로만 계산 · 데모',
  '주급 자동 차감 없음 · 삭제 이력 보존',
]) {
  if (html.includes(forbidden)) throw new Error(`Redundant UI copy remains: ${forbidden}`);
}
if (!html.includes('<span>주급 영향</span><strong>자동 차감 없음</strong>')) {
  throw new Error('The single operational payroll-impact fact was removed from complaint details.');
}
if (!html.includes('<h3>감사 이력</h3>')) throw new Error('Complaint audit history was removed.');
console.log('Essential-copy-only static contracts: passed');

const adminHomePriorityStart = html.lastIndexOf('function renderAdminToday()');
const adminHomePriorityEnd = html.indexOf('\n      function maidName(', adminHomePriorityStart);
if (adminHomePriorityStart < 0 || adminHomePriorityEnd < 0) throw new Error('Active admin-home source could not be isolated for priority checks.');
const adminHomePrioritySource = html.slice(adminHomePriorityStart, adminHomePriorityEnd);
for (const contract of [
  'data-admin-home-section="room-summary"',
  'data-admin-home-section="cleaning-actions"',
  'data-admin-home-section="cleaning-cost"',
  'data-dashboard-cost-shortcut="today"',
  'class="card cleaning-cost-shortcut"',
  '<strong>청소비 예상 지출</strong>',
  '<small>오늘 ${cleaningCost.count}건 · ${money(cleaningCost.expected)}</small>',
  '<span class="cleaning-cost-shortcut-cta">주급 정산',
  'data-action="go-payroll"',
]) {
  if (!adminHomePrioritySource.includes(contract)) throw new Error(`Admin-home priority/cost shortcut contract missing: ${contract}`);
}
const adminHomeSummaryIndex = adminHomePrioritySource.indexOf('data-admin-home-section="room-summary"');
const adminHomeActionsIndex = adminHomePrioritySource.indexOf('data-admin-home-section="cleaning-actions"');
const adminHomeCostIndex = adminHomePrioritySource.indexOf('data-admin-home-section="cleaning-cost"');
if (!(adminHomeSummaryIndex >= 0 && adminHomeSummaryIndex < adminHomeActionsIndex && adminHomeActionsIndex < adminHomeCostIndex)) {
  throw new Error('Admin-home sections are not ordered summary → cleaning actions → cleaning cost.');
}
for (const forbidden of [
  'class="cleaning-cost-grid"',
  'class="cleaning-cost-foot"',
  '이번 주 예상',
  '검수 통과 시 예상 지출',
  '앱은 실제 송금을 실행하지 않습니다.',
]) {
  if (adminHomePrioritySource.includes(forbidden)) throw new Error(`Verbose cleaning-cost content remains on admin home: ${forbidden}`);
}
if (!html.includes('/* Admin-home compact cleaning-cost shortcut */')) throw new Error('Compact cleaning-cost shortcut styles are missing.');
console.log('Admin-home room-summary priority and compact cost-link contracts: passed');

const upcomingAvailabilityMatch = html.match(/weeklyAvailability:\{\n([\s\S]*?)\n\s*\},\n\s*availabilityHistory:/);
if (!upcomingAvailabilityMatch) throw new Error('Next-week availability fixture could not be isolated.');
const upcomingAvailabilityRows = [...upcomingAvailabilityMatch[1].matchAll(/(m\d+):\{days:\[([^\]]*)\],status:'submitted'/g)].map(match => ({
  maidId: match[1],
  days: match[2].split(',').filter(Boolean).map(Number),
}));
if (upcomingAvailabilityRows.length !== 9 || new Set(upcomingAvailabilityRows.map(row => row.maidId)).size !== 9) {
  throw new Error(`Next-week availability fixture mismatch: ${upcomingAvailabilityRows.length} submitted rows.`);
}
const unavailableOnSimulationMonday = upcomingAvailabilityRows.filter(row => !row.days.includes(0)).map(row => row.maidId);
if (unavailableOnSimulationMonday.length) {
  throw new Error(`Random-assignment simulation Monday is unavailable for: ${unavailableOnSimulationMonday.join(', ')}`);
}
const upcomingHistoryStart = html.indexOf('availabilityHistory:[');
const upcomingHistoryEnd = html.indexOf("assignmentDate:'2026-08-17'", upcomingHistoryStart);
const upcomingHistorySource = html.slice(upcomingHistoryStart, upcomingHistoryEnd);
const upcomingHistoryRows = [...upcomingHistorySource.matchAll(/maidId:'(m\d+)',weekStart:'2026-08-17',days:\[([^\]]*)\]/g)].map(match => ({
  maidId: match[1],
  days: match[2].split(',').filter(Boolean).map(Number),
}));
if (upcomingHistoryRows.length !== 9 || upcomingHistoryRows.some(row => !row.days.includes(0))) {
  throw new Error('Next-week availability history must contain nine Monday-available maid records.');
}
const workHistoryStart = html.indexOf('const WORK_HISTORY_FIXTURES = [');
const workHistoryEnd = html.indexOf('const PAYROLL_CLEANING_FIXTURES = {', workHistoryStart);
const workHistorySource = html.slice(workHistoryStart, workHistoryEnd);
if (workHistoryStart < 0 || workHistoryEnd < 0) throw new Error('Weekly work-history fixture could not be isolated.');
for (const maidId of maidIds) {
  const count = [...workHistorySource.matchAll(new RegExp(`${maidId}:\\{nameSnapshot:`, 'g'))].length;
  if (count !== 3) throw new Error(`Weekly work-history fixture must contain ${maidId} in all three weeks; found ${count}.`);
}
if (html.includes('다음 주 가능일 미제출 2명')) throw new Error('Stale missing-availability notification remains.');
for (const contract of [
  "title:'다음 주 가능일 전원 제출 완료'",
  "detail:'등록된 메이드 9명이 모두 근무 가능일을 제출했습니다.'",
  'return MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,state.assignmentDate)===\'available\');',
  '<strong>${eligible.length}명</strong>',
]) {
  if (!html.includes(contract)) throw new Error(`All-maid random-assignment contract missing: ${contract}`);
}
const workforceMatrixStart = html.indexOf('function renderAvailabilityMatrix()');
if (workforceMatrixStart < 0) throw new Error('Workforce availability matrix source could not be isolated.');
const workforceMatrixSource = html.slice(workforceMatrixStart, workforceMatrixStart + 5000);
if (!workforceMatrixSource.includes('const start=weekStartIso(state.assignmentDate)')) {
  throw new Error('Workforce matrix must use the assignment date week.');
}
if (workforceMatrixSource.includes("const start='2026-08-17'")) {
  throw new Error('Legacy fixed 2026-08-17 workforce week remains.');
}
console.log('All-maid availability and work-history fixture contracts: passed');

const issue114SimulationContracts = [
  'const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY = Object.freeze({',
  "const TOMORROW_ASSIGNMENT_SIMULATION_DATE='2026-08-16'",
  'const TOMORROW_ASSIGNMENT_SIMULATION_TARGETS = Object.freeze([',
  'function applyTomorrowAssignmentSimulation(targetState)',
  "if(Number(id)===0)applyTomorrowAssignmentSimulation(s)",
  "targetState.roomStopped['608']=true",
  "targetState.candles['211']=Math.max(1",
  "targetState.assignments[notified623.id]",
  "workTargetId:startedTarget.id",
  'function assignmentRoomHoldReason(no,targetState=state)',
  "return `촛불 ${candleCount}개 회수 후 배정 가능`",
  "const start=weekStartIso(state.assignmentDate)",
];
for (const contract of issue114SimulationContracts) {
  if (!html.includes(contract)) throw new Error(`Issue #114 assignment fixture contract missing: ${contract}`);
}
const issue114TargetSourceStart = html.indexOf('const TOMORROW_ASSIGNMENT_SIMULATION_TARGETS');
const issue114TargetSourceEnd = html.indexOf('function applyTomorrowAssignmentSimulation', issue114TargetSourceStart);
const issue114TargetSource = html.slice(issue114TargetSourceStart, issue114TargetSourceEnd);
const issue114TargetRooms = [...issue114TargetSource.matchAll(/room:'(\d+)'/g)].map(match=>match[1]);
if (issue114TargetRooms.length !== 35 || new Set(issue114TargetRooms).size !== 35) {
  throw new Error(`Tomorrow simulation target fixture mismatch: ${issue114TargetRooms.length} rows / ${new Set(issue114TargetRooms).size} unique rooms.`);
}
for (const roomNo of ['516','556','541','455','540','762','608','211']) {
  if (!issue114TargetRooms.includes(roomNo)) throw new Error(`Required varied-state fixture missing: ${roomNo}`);
}
const issue114AvailabilityStart = html.indexOf('const CURRENT_WEEK_ASSIGNMENT_AVAILABILITY');
const issue114AvailabilityEnd = html.indexOf('const TOMORROW_ASSIGNMENT_SIMULATION_DATE', issue114AvailabilityStart);
const issue114AvailabilitySource = html.slice(issue114AvailabilityStart, issue114AvailabilityEnd);
for (let maidIndex=1;maidIndex<=9;maidIndex+=1) {
  const match=issue114AvailabilitySource.match(new RegExp(`m${maidIndex}:Object\\.freeze\\(\\[([^\\]]+)\\]\\)`));
  if (!match || !match[1].split(',').map(value=>Number(value.trim())).includes(6)) {
    throw new Error(`Maid m${maidIndex} must be available on simulation Sunday.`);
  }
}
console.log('Issue #114 assignment-week and varied-fixture static contracts: passed');

const reservationListSource=html.slice(html.indexOf('function reservationNextRegistrationState'),html.indexOf('function reservationModalConfig'));
for(const expected of ['reservation-list-head','예약 일정','숙박 · 인원','청소 상태']){
  if(!reservationListSource.includes(expected))throw new Error(`Reservation list view is missing ${expected}.`);
}
if(reservationListSource.includes('reservation-schedule-add'))throw new Error('Next reservation action is still rendered inside the schedule body.');
const standardModalSource=html.slice(html.indexOf('function standardModalMarkup'),html.indexOf('function showModal'));
for(const expected of ['modal-leading-actions','auxiliaryAction','modal-auxiliary']){
  if(!standardModalSource.includes(expected))throw new Error(`Modal footer auxiliary action contract is missing ${expected}.`);
}
const reservationConfigSource=html.slice(html.indexOf("function reservationModalConfig"),html.indexOf("function openReservation(roomNo='211'"));
if(!reservationConfigSource.includes("auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':''"))throw new Error('Next reservation action is not configured in the modal footer.');
const roomConceptStart=html.indexOf('const catalogSummary=');
const roomConceptSource=html.slice(roomConceptStart,html.indexOf('function renderRoomDetail',roomConceptStart));
if(roomConceptSource.includes('data-control="room-type-filter"'))throw new Error('Room type select still duplicates the catalog tabs.');
for(const expected of ['concept-filter-search','data-control="room-search"','optgroup label="상태 조건"']){
  if(!roomConceptSource.includes(expected))throw new Error(`Room status toolbar is missing ${expected}.`);
}
if(roomConceptSource.includes('상태 조건 · 중복 가능'))throw new Error('Room status group still contains the redundant 중복 가능 copy.');
console.log('Reservation list and room-toolbar simplification static contracts: passed');
