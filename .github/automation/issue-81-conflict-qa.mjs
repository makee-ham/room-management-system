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

const desktop=await browser.newPage({viewport:{width:1440,height:1000}});
observe(desktop,'desktop');
await desktop.goto(base,{waitUntil:'networkidle'});
await api(desktop,'resetScenario',0);
let candidates=await api(desktop,'facetCandidates');
const occupiedRoom=candidates.occupiedCleanable[0];
assert.ok(occupiedRoom,'occupied cleanable room missing');
await api(desktop,'setManualCleaning',occupiedRoom,true);
let facets=await api(desktop,'roomStateFacets',occupiedRoom);
assert.equal(facets.occupied,true);
assert.equal(facets.cleaningKind,'연박 청소');
assert.equal(facets.conflict,false,'valid occupied+stayover combination was marked as conflict');
assert.ok((await api(desktop,'roomsForState','occupied')).includes(occupiedRoom));
assert.ok((await api(desktop,'roomsForState','cleaning')).includes(occupiedRoom));

await api(desktop,'setOperationalMoment','2026-09-30','12:00');
facets=await api(desktop,'roomStateFacets',occupiedRoom);
assert.equal(facets.occupied,false);
assert.equal(facets.cleaningNeeded,true);
assert.equal(facets.cleaningKind,'연박 청소');
assert.equal(facets.conflict,true,'vacant+stayover stale job was not marked as conflict');
assert.equal(facets.blocked,true,'stale stayover conflict was not included in operational blockers');
assert.match(facets.conflictReason,/공실.*연박 청소/);
assert.ok((await api(desktop,'roomsForState','blocked')).includes(occupiedRoom));
await api(desktop,'setRoomFilter','all');
let card=desktop.locator(`article.room-card-v2[data-room="${occupiedRoom}"]`);
await card.waitFor();
let cardText=await card.innerText();
assert.match(cardText,/공실/);
assert.match(cardText,/연박 청소/);
assert.match(cardText,/상태 충돌/);

await api(desktop,'resetScenario',0);
await api(desktop,'setOperationalMoment','2026-08-15','13:05');
candidates=await api(desktop,'facetCandidates');
const inspectionRoom=candidates.inspection[0];
assert.ok(inspectionRoom,'checkout inspection candidate missing');
const before=await api(desktop,'roomStateFacets',inspectionRoom);
assert.equal(before.checkoutInspectionPending,true);
await api(desktop,'completeCheckoutInspection',inspectionRoom,'manual');
const after=await api(desktop,'roomStateFacets',inspectionRoom);
assert.equal(after.checkoutInspectionPending,false,'inspection completion did not clear inspection axis');
assert.equal(after.cleaningNeeded,before.cleaningNeeded,'inspection completion changed cleaning axis');
assert.ok(!(await api(desktop,'roomsForState','checkout-inspection')).includes(inspectionRoom));
if(before.cleaningNeeded)assert.ok((await api(desktop,'roomsForState','cleaning')).includes(inspectionRoom));

const rerender=await api(desktop,'repeatRender',10);
assert.equal(rerender.equal,true,'re-rendering changed durable records after state-axis transitions');

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:1000}});
  observe(page,`responsive-${width}`);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  await api(page,'resetScenario',0);
  const room=(await api(page,'facetCandidates')).occupiedCleanable[0];
  await api(page,'setManualCleaning',room,true);
  await api(page,'setRoomFilter','all');
  const roomCard=page.locator(`article.room-card-v2[data-room="${room}"]`);
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
console.log('Rendered room-state conflict matrix and independent completion QA: passed');
