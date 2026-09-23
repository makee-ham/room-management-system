#!/usr/bin/env node

import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { resolve } from 'node:path';

const require=createRequire(import.meta.url),{chromium}=require('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4175';
const screenshotDir=resolve('WIREFRAME/QA/screenshots');
await mkdir(screenshotDir,{recursive:true});

const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();
page.setDefaultTimeout(8000);
const pageErrors=[],consoleProblems=[],passed=[];
page.on('pageerror',error=>pageErrors.push(error.message));
page.on('console',message=>{const value=message.text();if(['warning','error'].includes(message.type())&&!/^Failed to load resource:/.test(value)&&value!=='Service Worker registration blocked by Playwright')consoleProblems.push(value);});

try {
  await page.goto(`${origin}/index.html?scenario=0&role=admin&view=rooms&date=2026-08-15`,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.__CASTLE_TEST__);
  await page.locator('#login-id').fill('admin');await page.locator('#login-password').fill('admin1234');await page.locator('#login-form').press('Enter');await page.locator('[data-action="nav"][data-view="rooms"]:visible').waitFor();

  const lifecycle=await page.evaluate(()=>{
    __CASTLE_TEST__.setOperationalMoment('2026-08-14','10:00');const dayBefore=__CASTLE_TEST__.reservationLifecycle('623');
    __CASTLE_TEST__.setOperationalMoment('2026-08-15','10:00');const arrival=__CASTLE_TEST__.reservationLifecycle('623');
    __CASTLE_TEST__.setOperationalMoment('2026-08-15','16:00');const occupied=__CASTLE_TEST__.reservationLifecycle('623');
    __CASTLE_TEST__.setOperationalMoment('2026-08-15','10:00');const future=__CASTLE_TEST__.reservationLifecycle('516');
    return {dayBefore,arrival,occupied,future};
  });
  assert.equal(lifecycle.dayBefore.key,'reserved');assert.equal(lifecycle.arrival.key,'arrival');assert.equal(lifecycle.occupied.key,'occupied');assert.equal(lifecycle.future.key,'future');
  passed.push('D-1 예약 있음 → D-day 시각 전 입실 예정 → 시각 도달 투숙 중, D+2 미래 예약은 현재 상태 비점유');

  await page.evaluate(()=>{__CASTLE_TEST__.resetScenario(0);__CASTLE_TEST__.setOperationalMoment('2026-08-15','10:32');__CASTLE_TEST__.setRoomFilter('all');});
  for(const width of [360,390,768,1440]){
    await page.setViewportSize({width,height:1000});
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`room list horizontal overflow at ${width}`);
    assert(await page.locator('.room-list-actions .btn:visible').evaluateAll(buttons=>buttons.every(button=>button.getBoundingClientRect().width>=44&&button.getBoundingClientRect().height>=44)),`room controls smaller than 44px at ${width}`);
  }
  assert(await page.getByText('입실 예정',{exact:true}).count()>0);assert(await page.getByText('예약 있음',{exact:true}).count()>0);
  await page.evaluate(()=>document.querySelector('#toast-region')?.replaceChildren());
  await page.setViewportSize({width:390,height:900});await page.locator('article[data-room="623"]').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(screenshotDir,'admin-room-arrival-status-390.png')});
  await page.setViewportSize({width:1440,height:1000});await page.locator('article[data-room="350"]').scrollIntoViewIfNeeded();await page.screenshot({path:resolve(screenshotDir,'admin-room-arrival-status-1440.png')});
  passed.push('객실 상태 목록·필터·큰 상태와 보조 배지, 360/390/768/1440 반응형');

  const precheck=await page.evaluate(()=>{
    __CASTLE_TEST__.resetScenario(0);__CASTLE_TEST__.setOperationalMoment('2026-08-15','10:32');
    const candidates=__CASTLE_TEST__.reservationMoveCandidates('reservation-demo-211'),target=candidates.includes('352')?'352':candidates[0];
    if(!target)throw new Error('예약 전 객실 변경 후보가 없습니다.');
    const result=__CASTLE_TEST__.moveReservation('reservation-demo-211',target),record=__CASTLE_TEST__.snapshot().reservations.find(item=>item.id==='reservation-demo-211');
    return {target,result:{mode:result.mode,fromRoom:result.fromRoom,toRoom:result.toRoom},record};
  });
  assert.equal(precheck.result.mode,'before-checkin');assert.equal(precheck.result.fromRoom,'211');assert.equal(precheck.result.toRoom,precheck.target);assert.equal(precheck.record.id,'reservation-demo-211');assert.equal(precheck.record.room,precheck.target);
  passed.push('체크인 전 객실 변경: 예약 ID 유지 · 전체 기간 충돌 재검증 · 객실 연결 변경');

  const activeMove=await page.evaluate(()=>{
    __CASTLE_TEST__.resetScenario(0);__CASTLE_TEST__.setOperationalMoment('2026-08-15','10:32');
    const created=__CASTLE_TEST__.upsertReservation({roomNo:'352',checkInAt:'2026-08-15T18:00',checkOutAt:'2026-08-16T11:00',guestCount:2,source:'test'}).reservation;
    __CASTLE_TEST__.setOperationalMoment('2026-08-15','18:30');
    const candidates=__CASTLE_TEST__.reservationMoveCandidates(created.id),target=candidates[0];
    if(!target)throw new Error('투숙 중 방 이동 후보가 없습니다.');
    const result=__CASTLE_TEST__.moveReservation(created.id,target);if(result.error)throw new Error(result.error);
    const snapshot=__CASTLE_TEST__.snapshot(),source=snapshot.reservations.find(item=>item.id===created.id),continuation=snapshot.reservations.find(item=>item.id===result.reservation.id),sourceState=__CASTLE_TEST__.occupancyState('352'),targetState=__CASTLE_TEST__.occupancyState(target);
    return {target,result:{mode:result.mode,fromRoom:result.fromRoom,toRoom:result.toRoom},source,continuation,sourceState,targetState,moves:snapshot.reservationRoomMoves};
  });
  assert.equal(activeMove.result.mode,'during-stay');assert.equal(activeMove.result.fromRoom,'352');assert.equal(activeMove.source.checkOutAt,'2026-08-15T18:30');assert.equal(activeMove.continuation.checkInAt,'2026-08-15T18:30');assert.equal(activeMove.continuation.room,activeMove.target);assert.equal(activeMove.sourceState.occupancy,'vacant');assert.equal(activeMove.sourceState.presentation.cleaning,true);assert.equal(activeMove.targetState.occupancy,'occupied');assert.equal(activeMove.moves.length,1);
  passed.push('투숙 중 방 이동: 원 객실 구간 보존 · 새 구간 생성 · 원 객실 청소 필요 · 새 객실 투숙 중');

  await page.evaluate(()=>{__CASTLE_TEST__.resetScenario(0);__CASTLE_TEST__.setOperationalMoment('2026-08-15','10:32');__CASTLE_TEST__.setRoomFilter('all');});
  await page.setViewportSize({width:390,height:900});
  await page.locator('[data-room="211"] [data-action="room-reservation-status"]').click();await page.getByText('211호 예약 상세·변경',{exact:true}).waitFor();
  const moveButton=page.getByRole('button',{name:'예약 객실 변경',exact:true});assert(await moveButton.isEnabled());await moveButton.click();await page.getByText('211호 예약 객실 변경',{exact:true}).waitFor();
  assert(/예약 (ID )?유지/.test(await page.locator('#modal-root').innerText()));assert(await page.locator('#reservation-room-move-target option').count()>0);
  await page.evaluate(()=>document.querySelector('#toast-region')?.replaceChildren());
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);await page.screenshot({path:resolve(screenshotDir,'admin-reservation-room-move-390.png')});
  await page.keyboard.press('Escape');await page.waitForFunction(()=>!document.body.classList.contains('modal-open'));
  passed.push('예약 상세 → 예약 객실 변경 확인 모달 · 키보드 Escape 닫기');

  assert.deepEqual(pageErrors,[]);assert.deepEqual(consoleProblems,[]);passed.push('페이지 예외와 console warning/error 없음');
  passed.forEach(item=>console.log(`[ok] ${item}`));
  console.log(`Environment: Chromium ${await browser.version()} via Playwright; Browser plugin unavailable.`);
} catch(error) {
  console.error('page errors',pageErrors);console.error('console problems',consoleProblems);await page.screenshot({path:'/tmp/reservation-arrival-room-move-failure.png',fullPage:true});throw error;
} finally {
  await browser.close();
}
