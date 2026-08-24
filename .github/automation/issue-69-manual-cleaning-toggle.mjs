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

const candidates=await api(page,'manualCleaningCandidates');
assert.ok(candidates.length>0,'no room can be used for manual cleaning test');
const vacant=candidates.find(item=>item.occupancy!=='occupied')||candidates[0];
const occupied=candidates.find(item=>item.occupancy==='occupied')||null;

const baseline=await api(page,'counts');
const first=await api(page,'setManualCleaning',vacant.room,true);
assert.equal(first.created,true,'first manual cleaning request was not created');
assert.equal(first.request.kind,vacant.occupancy==='occupied'?'연박 청소':'추가 청소');
const afterFirst=await api(page,'manualCleaningState',vacant.room);
assert.equal(afterFirst.request.status,'active');
assert.equal(afterFirst.manualTargetCount,1);
assert.equal(afterFirst.presentation.key,'cleaning');
assert.match(afterFirst.presentation.reason,/추가 청소|연박 청소/);

const duplicate=await api(page,'setManualCleaning',vacant.room,true);
assert.equal(duplicate.created,false);
assert.equal(duplicate.duplicate,true);
const afterDuplicate=await api(page,'manualCleaningState',vacant.room);
assert.equal(afterDuplicate.request.id,afterFirst.request.id);
assert.equal(afterDuplicate.manualTargetCount,1,'repeat ON duplicated assignment target');

await api(page,'showRoom',vacant.room);
const toggle=page.locator(`[data-action="toggle-room-cleaning"][data-id="${vacant.room}"]`);
await toggle.waitFor();
assert.equal(await toggle.getAttribute('aria-checked'),'true');
assert.match((await page.locator('#main-content').textContent())||'',/청소 필요 ON/);

const cleaningRooms=await api(page,'setRoomFilter','cleaning');
assert.ok(cleaningRooms.includes(vacant.room),'manual cleaning room is missing from cleaning filter');

const cancelled=await api(page,'setManualCleaning',vacant.room,false);
assert.equal(cancelled.cancelled,true);
const afterCancel=await api(page,'manualCleaningState',vacant.room);
assert.equal(afterCancel.request,null);
assert.equal(afterCancel.manualTargetCount,0);
assert.notEqual(afterCancel.presentation.key,'cleaning','OFF left room in cleaning status');
const afterCancelCounts=await api(page,'counts');
assert.equal(afterCancelCounts.submissions,baseline.submissions);
assert.equal(afterCancelCounts.earnings,baseline.earnings);

if(occupied){
  const stayover=await api(page,'setManualCleaning',occupied.room,true);
  assert.equal(stayover.created,true);
  assert.equal(stayover.request.kind,'연박 청소');
  const occupiedState=await api(page,'manualCleaningState',occupied.room);
  assert.equal(occupiedState.presentation.key,'cleaning');
  assert.match(occupiedState.presentation.reason,/연박 청소/);
  await api(page,'setManualCleaning',occupied.room,false);
}

const completedRequest=await api(page,'setManualCleaning',vacant.room,true);
assert.equal(completedRequest.created,true);
const completed=await api(page,'completeManualCleaning',vacant.room);
assert.equal(completed.status,'completed');
const completedState=await api(page,'manualCleaningState',vacant.room);
assert.equal(completedState.request,null,'field completion left manual request active');
const snapshot=await api(page,'snapshot');
const storedRequest=snapshot.manualCleaningRequests.find(([,item])=>item.id===completed.id)?.[1];
assert.equal(storedRequest?.status,'completed');
assert.equal(await api(page,'assertUnique'),true);
const rerender=await api(page,'repeatRender',10);
assert.equal(rerender.equal,true,'re-render changed manual cleaning durable ledger');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:950}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'domcontentloaded'});
  const candidate=(await api(responsive,'manualCleaningCandidates'))[0];
  assert.ok(candidate,`${width}px has no manual cleaning candidate`);
  await api(responsive,'setManualCleaning',candidate.room,true);
  await api(responsive,'showRoom',candidate.room);
  await responsive.locator(`[data-action="toggle-room-cleaning"][data-id="${candidate.room}"]`).waitFor();
  const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await responsive.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Manual room-cleaning toggle rendered QA: passed');
