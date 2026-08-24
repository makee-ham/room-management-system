import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});
function observe(page,label){page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});}
async function api(page,method,...args){return page.evaluate(({method,args})=>{const fn=window.__CASTLE_TEST__?.[method];if(typeof fn!=='function')throw new Error(`test API missing: ${method}`);return fn(...args);},{method,args});}
async function waitForFacetCard(page,room){await page.waitForFunction(room=>Array.from(document.querySelectorAll('.room-card-v2,.room-card')).some(card=>Array.from(card.querySelectorAll('[data-id]')).some(node=>node.dataset.id===room)&&card.querySelector('.room-concurrent-statuses')),room);}

const page=await browser.newPage({viewport:{width:1440,height:1000}});observe(page,'desktop');await page.goto(base,{waitUntil:'networkidle'});await api(page,'resetScenario',0);
const durableStart=await api(page,'fingerprint');

// Occupied + stayover cleaning + operation stopped.
let candidates=await api(page,'manualCleaningCandidates');
const occupied=String(candidates.find(item=>item.occupancy==='occupied')?.room||'');
assert.ok(occupied,'occupied test candidate missing');
await api(page,'setManualCleaning',occupied,true);
let facets=await api(page,'setRoomStatusFacetTest',occupied,{roomStopped:true,stopReason:'시설 안전 확인'});
assert.equal(facets.occupied,true);assert.equal(facets.cleaningActive,true);assert.equal(facets.operationStopped,true);
await api(page,'setRoomFilter','cleaning');await waitForFacetCard(page,occupied);
let dom=await api(page,'concurrentStatusDom',occupied);
assert.match(dom.cardText,/투숙 중/);assert.match(dom.cardText,/연박 청소/);assert.match(dom.cardText,/운영 중지/);
await api(page,'showRoom',occupied);await page.waitForFunction(room=>!!document.querySelector(`[data-room-state-dimensions="${room}"]`),occupied);
dom=await api(page,'concurrentStatusDom',occupied);assert.match(dom.panelText,/투숙 중/);assert.match(dom.panelText,/연박 청소/);assert.match(dom.panelText,/운영 중지/);

// Checked-out + checkout inspection + checkout cleaning.
await api(page,'resetScenario',0);await api(page,'setOperationalMoment','2026-08-15','13:05');
const momentCandidates=await api(page,'concurrentStatusCandidates');
const checkoutCase=momentCandidates.find(item=>item.checkoutInspection);
assert.ok(checkoutCase,'checkout-inspection test candidate missing at 13:05');
const checkoutRoom=String(checkoutCase.room);
assert.equal(checkoutCase.occupied,false);assert.equal(checkoutCase.cleaningActive,true,'checkout inspection room should retain checkout cleaning flow');
const checkoutFilter=await api(page,'setRoomFilter','checkout-inspection');assert.ok(checkoutFilter.includes(checkoutRoom));await waitForFacetCard(page,checkoutRoom);
dom=await api(page,'concurrentStatusDom',checkoutRoom);
assert.match(dom.cardText,/공실/);assert.match(dom.cardText,/퇴실점검 대상/);assert.match(dom.cardText,/퇴실 청소|청소/);
await api(page,'showRoom',checkoutRoom);await page.waitForFunction(room=>!!document.querySelector(`[data-room-state-dimensions="${room}"]`),checkoutRoom);
dom=await api(page,'concurrentStatusDom',checkoutRoom);assert.match(dom.panelText,/퇴실점검/);assert.match(dom.panelText,/청소/);

// Vacant + additional cleaning + candles.
await api(page,'resetScenario',0);candidates=await api(page,'manualCleaningCandidates');
const vacant=String(candidates.find(item=>item.occupancy!=='occupied')?.room||'');assert.ok(vacant,'vacant test candidate missing');
await api(page,'setManualCleaning',vacant,true);facets=await api(page,'setRoomStatusFacetTest',vacant,{candles:2});
assert.equal(facets.occupied,false);assert.equal(facets.cleaningActive,true);assert.equal(facets.candleCount,2);
await api(page,'setRoomFilter','cleaning');await waitForFacetCard(page,vacant);dom=await api(page,'concurrentStatusDom',vacant);
assert.match(dom.cardText,/공실/);assert.match(dom.cardText,/추가 청소/);assert.match(dom.cardText,/촛불 2개/);

// Data hold is a separate facet and does not erase occupancy.
await api(page,'resetScenario',0);candidates=await api(page,'manualCleaningCandidates');
const dataRoom=String(candidates.find(item=>item.occupancy==='occupied')?.room||'');assert.ok(dataRoom);
facets=await api(page,'setRoomStatusFacetTest',dataRoom,{dataIssue:'객실 기준정보 확인 필요'});
assert.equal(facets.occupied,true);assert.equal(facets.dataHold,true);
await api(page,'setRoomFilter','occupied');await waitForFacetCard(page,dataRoom);dom=await api(page,'concurrentStatusDom',dataRoom);assert.match(dom.cardText,/투숙 중/);assert.match(dom.cardText,/정보 확인 필요/);
await api(page,'setRoomStatusFacetTest',dataRoom,{dataIssue:''});

const repeat=await api(page,'repeatRender',10);assert.equal(repeat.equal,true,'re-rendering changed durable ledgers');await api(page,'assertUnique');
const duplicateRows=await page.evaluate(()=>Array.from(document.querySelectorAll('.room-card-v2,.room-card')).filter(card=>card.querySelectorAll(':scope > .room-concurrent-statuses').length>1).length);assert.equal(duplicateRows,0,'duplicate facet rows were inserted');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:1000}});observe(responsive,`responsive-${width}`);await responsive.goto(base,{waitUntil:'domcontentloaded'});const list=await api(responsive,'manualCleaningCandidates');const room=String(list.find(item=>item.occupancy==='occupied')?.room||'');assert.ok(room);await api(responsive,'setManualCleaning',room,true);await api(responsive,'setRoomStatusFacetTest',room,{roomStopped:true,stopReason:'반응형 테스트'});await api(responsive,'setRoomFilter','cleaning');await waitForFacetCard(responsive,room);const text=await api(responsive,'concurrentStatusDom',room);assert.match(text.cardText,/투숙 중/);assert.match(text.cardText,/연박 청소/);assert.match(text.cardText,/운영 중지/);const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);await responsive.close();
}

const durableEnd=await api(page,'fingerprint');assert.ok(durableStart&&durableEnd);await page.close();await browser.close();assert.deepEqual(errors,[],errors.join('\n'));console.log('Rendered room status facet combinations and responsive QA: passed');
