import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}
async function api(page,method,...args){
  return page.evaluate(({method,args})=>{
    const fn=window.__CASTLE_TEST__?.[method];
    if(typeof fn!=='function')throw new Error(`test API missing: ${method}`);
    return fn(...args);
  },{method,args});
}
async function showAll(page){ await api(page,'setRoomFilter','all'); }

const desktop=await browser.newPage({viewport:{width:1440,height:1000}});
observe(desktop,'desktop');
await desktop.goto(base,{waitUntil:'networkidle'});
assert.match(await desktop.title(),/CASTLE THE ART/);
await api(desktop,'resetScenario',0);
let candidates=await api(desktop,'facetCandidates');
assert.ok(candidates.occupiedCleanable.length,'occupied cleanable candidate missing');
assert.ok(candidates.vacantCleanable.length,'vacant cleanable candidate missing');

// 투숙 중 + 연박 청소: 점유와 청소 축을 동시에 보존한다.
const occupiedRoom=candidates.occupiedCleanable[0];
let result=await api(desktop,'setManualCleaning',occupiedRoom,true);
assert.equal(result.created,true,'occupied manual cleaning request was not created');
let facets=await api(desktop,'roomStateFacets',occupiedRoom);
assert.equal(facets.occupied,true);
assert.equal(facets.cleaningNeeded,true);
assert.equal(facets.cleaningKind,'연박 청소');
const occupiedFilter=await api(desktop,'roomsForState','occupied');
const cleaningFilter=await api(desktop,'roomsForState','cleaning');
assert.ok(occupiedFilter.includes(occupiedRoom),'occupied+cleaning room disappeared from occupied filter');
assert.ok(cleaningFilter.includes(occupiedRoom),'occupied+cleaning room disappeared from cleaning filter');
await showAll(desktop);
let card=desktop.locator(`[data-room="${occupiedRoom}"]`);
await card.waitFor();
assert.equal(await card.getAttribute('data-occupancy'),'occupied');
assert.equal(await card.getAttribute('data-cleaning-needed'),'true');
let cardText=await card.innerText();
assert.match(cardText,/투숙 중/);
assert.match(cardText,/연박 청소/);
assert.match(cardText,/청소/);

// 렌더링은 원장을 바꾸지 않는다.
let rerender=await api(desktop,'repeatRender',12);
assert.equal(rerender.equal,true,'re-rendering changed durable records during occupied cleaning');

// 연박 청소 완료 뒤 점유만 남고 청소 축만 해제된다.
await api(desktop,'completeManualCleaning',occupiedRoom);
facets=await api(desktop,'roomStateFacets',occupiedRoom);
assert.equal(facets.occupied,true,'cleaning completion incorrectly cleared occupancy');
assert.equal(facets.cleaningNeeded,false,'cleaning axis remained after manual cleaning completion');

// 공실 + 추가 청소도 공실과 청소를 함께 보존한다.
await api(desktop,'resetScenario',0);
candidates=await api(desktop,'facetCandidates');
const vacantRoom=candidates.vacantCleanable[0];
result=await api(desktop,'setManualCleaning',vacantRoom,true);
assert.equal(result.created,true,'vacant extra-cleaning request was not created');
facets=await api(desktop,'roomStateFacets',vacantRoom);
assert.equal(facets.occupied,false);
assert.equal(facets.cleaningNeeded,true);
assert.equal(facets.cleaningKind,'추가 청소');
assert.ok((await api(desktop,'roomsForState','vacant')).includes(vacantRoom));
assert.ok((await api(desktop,'roomsForState','cleaning')).includes(vacantRoom));
await showAll(desktop);
card=desktop.locator(`[data-room="${vacantRoom}"]`);
cardText=await card.innerText();
assert.match(cardText,/공실/);
assert.match(cardText,/추가 청소/);

// 투숙 중 + 운영 중지: 투숙 사실과 차단을 모두 표시한다.
await api(desktop,'resetScenario',0);
candidates=await api(desktop,'facetCandidates');
const blockedOccupied=candidates.occupiedCleanable[0];
facets=await api(desktop,'setRoomStoppedForTest',blockedOccupied,true);
assert.equal(facets.occupied,true);
assert.equal(facets.blocked,true);
assert.ok((await api(desktop,'roomsForState','occupied')).includes(blockedOccupied));
assert.ok((await api(desktop,'roomsForState','blocked')).includes(blockedOccupied));
await showAll(desktop);
card=desktop.locator(`[data-room="${blockedOccupied}"]`);
cardText=await card.innerText();
assert.match(cardText,/투숙 중/);
assert.match(cardText,/차단|운영 중지/);

// 체크아웃 이후에는 퇴실점검과 퇴실 청소가 각각 독립적으로 필터된다.
await api(desktop,'resetScenario',0);
await api(desktop,'setOperationalMoment','2026-08-15','13:05');
candidates=await api(desktop,'facetCandidates');
assert.ok(candidates.inspection.length,'checkout inspection candidate missing at 13:05');
const inspectionRoom=candidates.inspection[0];
facets=await api(desktop,'roomStateFacets',inspectionRoom);
assert.equal(facets.checkoutInspectionPending,true);
assert.ok((await api(desktop,'roomsForState','checkout-inspection')).includes(inspectionRoom));
if(facets.cleaningNeeded)assert.ok((await api(desktop,'roomsForState','cleaning')).includes(inspectionRoom),'inspection+cleaning room missing from cleaning filter');
await showAll(desktop);
card=desktop.locator(`[data-room="${inspectionRoom}"]`);
cardText=await card.innerText();
assert.match(cardText,/공실/);
assert.match(cardText,/퇴실점검 대상/);

// 기존 데이터에 이전 퇴실청소와 새 투숙이 겹친 경우가 있으면 충돌 경고를 검증한다.
const conflictRooms=(await api(desktop,'facetCandidates')).conflicts;
if(conflictRooms.length){
  const conflictRoom=conflictRooms[0];
  const conflictFacets=await api(desktop,'roomStateFacets',conflictRoom);
  assert.equal(conflictFacets.occupied,true);
  assert.equal(conflictFacets.cleaningNeeded,true);
  assert.equal(conflictFacets.conflict,true);
  await showAll(desktop);
  const conflictText=await desktop.locator(`[data-room="${conflictRoom}"]`).innerText();
  assert.match(conflictText,/투숙 중/);
  assert.match(conflictText,/충돌/);
}

// 상세 화면에서도 같은 축 배지가 유지된다.
await api(desktop,'showRoom',inspectionRoom);
const detailText=await desktop.locator('#main-content').innerText();
assert.match(detailText,/공실/);
assert.match(detailText,/퇴실점검 대상/);

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  observe(page,`responsive-${width}`);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await api(page,'resetScenario',0);
  const responsiveCandidates=await api(page,'facetCandidates');
  const room=responsiveCandidates.occupiedCleanable[0];
  assert.ok(room,`${width}px occupied candidate missing`);
  await api(page,'setManualCleaning',room,true);
  await api(page,'setRoomFilter','all');
  const roomCard=page.locator(`[data-room="${room}"]`);
  await roomCard.waitFor();
  const text=await roomCard.innerText();
  assert.match(text,/투숙 중/);
  assert.match(text,/연박 청소/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await page.close();
}

await desktop.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered independent room-state facets and transition QA: passed');
