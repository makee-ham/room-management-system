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

const page=await browser.newPage({viewport:{width:1440,height:1000}});
observe(page,'desktop');
await page.goto(base,{waitUntil:'networkidle'});
assert.match(await page.title(),/CASTLE THE ART/);
await api(page,'resetScenario',0);
const durableBefore=await api(page,'snapshot');
const candidates=await api(page,'manualCleaningCandidates');
const occupiedCandidate=candidates.find(item=>item.occupancy==='occupied');
const vacantCandidate=candidates.find(item=>item.occupancy!=='occupied');
assert.ok(occupiedCandidate,'occupied room without an existing cleaning flow was not found');
assert.ok(vacantCandidate,'vacant room without an existing cleaning flow was not found');
const occupiedRoom=String(occupiedCandidate.room),vacantRoom=String(vacantCandidate.room);

let facets=await api(page,'roomStatusFacets',occupiedRoom);
assert.equal(facets.occupied,true);
assert.equal(facets.cleaningActive,false);
let occupiedFilter=await api(page,'setRoomFilter','occupied');
let cleaningFilter=await api(page,'setRoomFilter','cleaning');
assert.ok(occupiedFilter.includes(occupiedRoom),'plain occupied room is missing from occupied filter');
assert.ok(!cleaningFilter.includes(occupiedRoom),'plain occupied room incorrectly appears in cleaning filter');

const created=await api(page,'setManualCleaning',occupiedRoom,true);
assert.ok(!created?.error,created?.error||'occupied manual cleaning was not created');
facets=await api(page,'roomStatusFacets',occupiedRoom);
assert.equal(facets.occupied,true);
assert.equal(facets.cleaningActive,true);
assert.equal(facets.cleaningKind,'연박 청소');
occupiedFilter=await api(page,'setRoomFilter','occupied');
cleaningFilter=await api(page,'setRoomFilter','cleaning');
assert.ok(occupiedFilter.includes(occupiedRoom),'occupied+cleaning room is missing from occupied filter');
assert.ok(cleaningFilter.includes(occupiedRoom),'occupied+cleaning room is missing from cleaning filter');
await page.waitForFunction(room=>Array.from(document.querySelectorAll('.room-card-v2,.room-card')).some(card=>card.dataset.occupancyFacet==='occupied'&&card.dataset.cleaningFacet==='active'&&Array.from(card.querySelectorAll('[data-id]')).some(node=>node.dataset.id===room)),occupiedRoom);
let dom=await api(page,'concurrentStatusDom',occupiedRoom);
assert.equal(dom.occupancyFacet,'occupied');
assert.equal(dom.cleaningFacet,'active');
assert.match(dom.cardText,/투숙 중/);
assert.match(dom.cardText,/연박 청소/);

const cancelled=await api(page,'setManualCleaning',occupiedRoom,false);
assert.ok(!cancelled?.error,cancelled?.error||'occupied manual cleaning was not cancelled');
facets=await api(page,'roomStatusFacets',occupiedRoom);
assert.equal(facets.occupied,true);
assert.equal(facets.cleaningActive,false);

await api(page,'setManualCleaning',occupiedRoom,true);
for(const stage of ['draft','claimed','cleaning','upload','inspection']){
  facets=await api(page,'setConcurrentCleaningStage',occupiedRoom,stage);
  assert.equal(facets.occupied,true,`${stage}: occupied facet disappeared`);
  assert.equal(facets.cleaningActive,true,`${stage}: cleaning facet disappeared`);
  assert.equal(facets.cleaningJob,stage);
  occupiedFilter=await api(page,'setRoomFilter','occupied');
  cleaningFilter=await api(page,'setRoomFilter','cleaning');
  assert.ok(occupiedFilter.includes(occupiedRoom),`${stage}: occupied filter lost room`);
  assert.ok(cleaningFilter.includes(occupiedRoom),`${stage}: cleaning filter lost room`);
}
await api(page,'showRoom',occupiedRoom);
await page.waitForFunction(room=>!!document.querySelector(`[data-room-state-dimensions="${room}"]`),occupiedRoom);
dom=await api(page,'concurrentStatusDom',occupiedRoom);
assert.match(dom.panelText,/투숙 중/);
assert.match(dom.panelText,/연박 청소/);
assert.match(dom.panelText,/투숙 중 · 청소 필요/);

facets=await api(page,'resolveConcurrentCleaning',occupiedRoom);
assert.equal(facets.occupied,true,'resolving cleaning changed occupancy');
assert.equal(facets.cleaningActive,false,'resolved cleaning remains active');
occupiedFilter=await api(page,'setRoomFilter','occupied');
cleaningFilter=await api(page,'setRoomFilter','cleaning');
assert.ok(occupiedFilter.includes(occupiedRoom),'resolved occupied room left occupied filter');
assert.ok(!cleaningFilter.includes(occupiedRoom),'resolved occupied room remains in cleaning filter');

await api(page,'resetScenario',0);
const vacantCreated=await api(page,'setManualCleaning',vacantRoom,true);
assert.ok(!vacantCreated?.error,vacantCreated?.error||'vacant manual cleaning was not created');
const vacantFacets=await api(page,'roomStatusFacets',vacantRoom);
assert.equal(vacantFacets.occupied,false);
assert.equal(vacantFacets.cleaningActive,true);
assert.equal(vacantFacets.cleaningKind,'추가 청소');
occupiedFilter=await api(page,'setRoomFilter','occupied');
cleaningFilter=await api(page,'setRoomFilter','cleaning');
assert.ok(!occupiedFilter.includes(vacantRoom),'vacant cleaning room appears in occupied filter');
assert.ok(cleaningFilter.includes(vacantRoom),'vacant cleaning room is missing from cleaning filter');

const repeat=await api(page,'repeatRender',10);
assert.equal(repeat.equal,true,'re-rendering changed durable ledgers');
await api(page,'assertUnique');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:1000}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(base,{waitUntil:'domcontentloaded'});
  const responsiveCandidates=await api(responsive,'manualCleaningCandidates');
  const candidate=responsiveCandidates.find(item=>item.occupancy==='occupied');
  assert.ok(candidate,`${width}px occupied candidate missing`);
  await api(responsive,'setManualCleaning',String(candidate.room),true);
  await api(responsive,'setRoomFilter','cleaning');
  await responsive.waitForFunction(room=>Array.from(document.querySelectorAll('.room-card-v2,.room-card')).some(card=>card.dataset.occupancyFacet==='occupied'&&card.dataset.cleaningFacet==='active'&&Array.from(card.querySelectorAll('[data-id]')).some(node=>node.dataset.id===room)),String(candidate.room));
  const text=await api(responsive,'concurrentStatusDom',String(candidate.room));
  assert.match(text.cardText,/투숙 중/);
  assert.match(text.cardText,/연박 청소/);
  const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await responsive.close();
}

const durableAfter=await api(page,'snapshot');
assert.ok(durableBefore&&durableAfter,'durable snapshots are unavailable');
await page.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered concurrent occupancy/cleaning status and responsive QA: passed');
