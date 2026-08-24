import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}
async function api(page,method,...args){
  return page.evaluate(({method,args})=>{
    const target=window.__CASTLE_TEST__?.[method];
    if(typeof target!=='function')throw new Error(`test API missing: ${method}`);
    return target(...args);
  },{method,args});
}

const page=await browser.newPage({viewport:{width:1440,height:1000}});
observe(page,'main');
await page.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'networkidle'});
await page.locator('.room-card-v2').first().waitFor();
await api(page,'resetScenario',0);

await api(page,'setOperationalMoment','2026-08-15','15:59');
let state=await api(page,'occupancyState','623');
assert.equal(state.occupancy,'vacant');
assert.equal(state.currentReservationId,null);

await api(page,'setOperationalMoment','2026-08-15','16:00');
state=await api(page,'occupancyState','623');
assert.equal(state.occupancy,'occupied');
assert.equal(state.currentReservationId,'reservation-demo-623');
assert.equal(state.actualCheckinAt,'2026-08-15T16:00');
assert.equal(state.plannedCheckoutAt,'2026-08-16T11:00');
assert.equal(state.presentation.key,'occupied');

await api(page,'setOperationalMoment','2026-08-16','10:59');
state=await api(page,'occupancyState','623');
assert.equal(state.occupancy,'occupied');
assert.equal(state.currentReservationId,'reservation-demo-623');

await api(page,'setOperationalMoment','2026-08-16','11:00');
state=await api(page,'occupancyState','623');
assert.equal(state.occupancy,'vacant');
assert.equal(state.currentReservationId,null);
assert.equal(state.actualCheckoutAt,'2026-08-16T11:00');
assert.equal(state.checkoutCleaningDue,true);
assert.equal(state.presentation.key,'cleaning');

await api(page,'resetScenario',0);
await api(page,'setOperationalMoment','2026-08-17','13:59');
state=await api(page,'occupancyState','552');
assert.equal(state.occupancy,'vacant');
await api(page,'setOperationalMoment','2026-08-17','14:00');
state=await api(page,'occupancyState','552');
assert.equal(state.occupancy,'occupied','early check-in did not use stored reservation time');
assert.equal(state.currentReservationId,'reservation-demo-552-attention');

await api(page,'setReservationTimes','reservation-demo-552-attention','2026-08-17T15:00','2026-08-19T12:00');
await api(page,'setOperationalMoment','2026-08-17','14:30');
state=await api(page,'occupancyState','552');
assert.equal(state.occupancy,'vacant','edited check-in time was not projected');
await api(page,'setOperationalMoment','2026-08-17','15:00');
state=await api(page,'occupancyState','552');
assert.equal(state.occupancy,'occupied');
assert.equal(state.plannedCheckoutAt,'2026-08-19T12:00');

await api(page,'showRoom','552');
assert.equal(await page.locator('[data-action="manual-checkin"]').count(),0);
assert.equal(await page.locator('[data-action="manual-checkout"]').count(),0);
assert.equal((await page.getByText('투숙 시작',{exact:true}).count()),0);
assert.equal((await page.getByText('지금 체크아웃',{exact:true}).count()),0);
assert.match((await page.locator('#main-content').textContent())||'',/입실·퇴실은 예약 시각에 자동 반영/);

assert.equal(await api(page,'assertUnique'),true);
const rerender=await api(page,'repeatRender',12);
assert.equal(rerender.equal,true,'automatic occupancy render changed durable ledgers');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:950}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'domcontentloaded'});
  await api(responsive,'setOperationalMoment','2026-08-15','16:00');
  await api(responsive,'showRoom','623');
  await responsive.getByText('현재 투숙 상태',{exact:true}).waitFor();
  assert.equal(await responsive.locator('[data-action="manual-checkin"],[data-action="manual-checkout"]').count(),0);
  const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await responsive.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Automatic reservation occupancy rendered QA: passed');
