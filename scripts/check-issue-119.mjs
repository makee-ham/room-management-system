#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
const html=readFileSync(resolve('WIREFRAME/index.html'),'utf8');
const required=[
  "const AUTH_SESSION_KEY='roomManagementAuthSessionV1'",
  "{id:'admin',password:'admin1234',role:'admin'",
  "password:'maid1234',role:'maid'",
  "const LONG_STAY_OPEN_END_AT='9999-12-31T23:59'",
  'function reservationHasKnownEnd(reservation)',
  'reservationLongStayEndLabel(reservation)',
  '종료일을 알면 입력하고, 모르면 비워 둔 채',
  'data-res-checkout-label',
  "isLongStay&&!enteredCheckoutAt?LONG_STAY_OPEN_END_AT",
  "reservationIsLongStay(reservation)&&!reservationHasKnownEnd(reservation)",
  'function cleaningTargetVisible(item,targetState=state)',
  '.filter(item=>cleaningTargetVisible(item,targetState))',
  'assignment-availability-disclosure',
  "const openAttr=phase==='open'?' open':''",
  'data-action="focus-assignment-room"',
  'id="assignment-room-${item.room}"',
  'assignment-room-type-link',
  "const maid={my:'내 업무',schedule:'다음 주 근무 가능일',pay:'내 주급',more:'더보기'}",
  'data-action="logout" aria-label="로그아웃"',
];
for(const contract of required){if(!html.includes(contract))throw new Error(`Issue #119 contract missing: ${contract}`);}
for(const removed of ["{id:'alerts',label:'알림',icon:'bell'}","if (state.maidView==='alerts') return renderMaidAlerts();","data-action=\"switch-role\" aria-label=\"${state.role==='admin'?'메이드 보기':'관리자 보기'}\""]){if(html.includes(removed))throw new Error(`Removed issue #119 contract remains: ${removed}`);}

const maidScheduleIndex=html.lastIndexOf('function renderMaidSchedule()');
const publicJobIndex=html.lastIndexOf('function publicJobCard(no)');
const maidOpenIndex=html.lastIndexOf('function renderMaidOpen()');
const myJobIndex=html.lastIndexOf('function myJobCard(no)');
const maidMyIndex=html.lastIndexOf('function renderMaidMy()');
const maidAlertsIndex=html.lastIndexOf('function renderMaidAlerts()');
if(!(maidScheduleIndex>=0&&maidScheduleIndex<publicJobIndex&&publicJobIndex<maidOpenIndex&&maidOpenIndex<myJobIndex&&myJobIndex<maidMyIndex&&maidMyIndex<maidAlertsIndex)){
  throw new Error('Latest maid schedule rewrite must retain the maid work dashboard functions before the alerts helper.');
}
if(!html.includes("if(roomHasOpenEndedLongStay(room.no))return '장기 투숙 · 종료일 미정 · 예약 불가';")){
  throw new Error('Only open-ended long stays may block all future reservation dates.');
}

const inlineScripts=[...html.matchAll(/<script\b(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)].map(match=>match[1]);
if(!inlineScripts.length)throw new Error('No inline application script found.');
for(const script of inlineScripts)new Function(script);
console.log('Issue #119 source contracts and JavaScript syntax verified.');
