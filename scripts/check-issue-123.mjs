#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const html=readFileSync(resolve('WIREFRAME/index.html'),'utf8');

for(const removed of [
  '아이디에 따라 화면이 분리됩니다.',
  '관리자는 관리자 화면만, 메이드는 본인 업무 화면만 이용합니다.',
  '역할 간 직접 전환 없음',
  '다른 역할은 로그아웃한 뒤 해당 아이디로 다시 로그인합니다.',
  '.auth-role-card {',
]){
  if(html.includes(removed))throw new Error(`Issue #123 removed login copy remains: ${removed}`);
}

for(const required of [
  'id="login-form"',
  '와이어프레임: 관리자 admin / admin1234 · 메이드 maid1~maid9 / maid1234',
  'function reservationCanEditCurrentStay(reservation,room=',
  'latestStarted?.id===reservation.id',
  'if(reservationCanEditCurrentStay(reservation,room))return false',
  "requestedCurrentStay=!!requested&&reservationCanEditCurrentStay(requested,room)",
  'editableCurrentStay=!!existing&&reservationCanEditCurrentStay(existing,room)',
  'readOnly=weekPast&&!currentEntry&&!editableCurrentStay',
  "const readOnly=(nextRegistration.weekPast||reservationRecordIsPast(reservation))&&!reservationCanEditCurrentStay(reservation,room)",
  "linkedCurrentStay=!!before&&reservationCanEditCurrentStay(before,room)",
  "if((reservationWeekIsPast()||reservationRecordIsPast(existing))&&!currentStay&&!editableCurrentStay)",
  "checkInAt<=now&&(openEndedLongStay||checkOutAt>now)",
  '투숙 중 예약은 수정 가능 · 종료된 기록은 조회만 가능',
]){
  if(!html.includes(required))throw new Error(`Issue #123 contract missing: ${required}`);
}

const inlineScripts=[...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(match=>match[1]);
if(!inlineScripts.length)throw new Error('No inline application script found.');
for(const script of inlineScripts)new Function(script);
console.log('Issue #123 login and current-stay extension contracts verified.');
