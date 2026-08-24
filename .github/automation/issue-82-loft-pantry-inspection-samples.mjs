import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});
const expectedTypeCounts={standard:22,premium:51,oceanPremium:13,oceanFamily:35};
const expectedSlotCounts={standard:13,premium:14,oceanPremium:14,oceanFamily:18};
const universalIds=['loft-stairs','loft-wide','pantry'];

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
const durableBefore=await api(page,'fingerprint');

const audit=await api(page,'universalCheckoutTemplateAudit');
assert.equal(audit.length,121,'current checkout template audit must cover all rooms');
for(const [typeId,count] of Object.entries(expectedTypeCounts)){
  const rooms=audit.filter(item=>item.typeId===typeId);
  assert.equal(rooms.length,count,`${typeId} room count mismatch`);
  assert.equal(new Set(rooms.map(item=>item.signature)).size,1,`${typeId} has more than one current slot contract`);
  assert.ok(rooms.every(item=>item.count===expectedSlotCounts[typeId]),`${typeId} slot count mismatch`);
  for(const id of universalIds)assert.ok(rooms.every(item=>item.universal[id]===1),`${typeId} ${id} is not exactly once in every room`);
}

const catalog=await api(page,'inspectionSampleCatalog');
assert.equal(catalog.length,121,'inspection sample catalog must contain 121 rooms');
for(const sample of catalog){
  assert.equal(sample.count,expectedSlotCounts[sample.typeId],`${sample.room} sample slot count mismatch`);
  for(const id of universalIds)assert.equal(sample.universal[id],1,`${sample.room} sample ${id} count mismatch`);
}

const list=await api(page,'showInspectionSampleList');
assert.equal(list.count,121);
await page.locator('[data-action="inspection-sample-open"]').first().waitFor();
assert.equal(await page.locator('[data-action="inspection-sample-open"]').count(),121,'sample list does not expose every room');
const listText=await page.locator('#main-content').innerText();
assert.match(listText,/객실별 관리자 검수 샘플/);
assert.match(listText,/복층 계단 필수/);
assert.match(listText,/복층 필수/);
assert.match(listText,/팬트리 필수/);

const representatives={
  standard:audit.find(item=>item.typeId==='standard').room,
  premium:audit.find(item=>item.typeId==='premium').room,
  oceanPremium:audit.find(item=>item.typeId==='oceanPremium').room,
  oceanFamily:audit.find(item=>item.typeId==='oceanFamily').room,
};
for(const [typeId,room] of Object.entries(representatives)){
  const contract=await api(page,'showInspectionSample',room);
  assert.equal(contract.same,true,`${room} sample inspection differs from maid template contract`);
  assert.equal(contract.expected.length,expectedSlotCounts[typeId]);
  for(const id of universalIds)assert.equal(contract.universal[id],1,`${room} ${id} sample count mismatch`);
  const sampleRoot=page.locator(`[data-inspection-sample-room="${room}"]`);
  await sampleRoot.waitFor();
  assert.equal(await sampleRoot.getAttribute('data-inspection-sample-readonly'),'true');
  const review=sampleRoot.locator('.inspection-template-review');
  await review.waitFor();
  assert.equal(await review.getAttribute('data-template-contract-match'),'true');
  assert.equal(Number(await review.getAttribute('data-template-photo-count')),expectedSlotCounts[typeId]);
  for(const id of universalIds)assert.equal(await sampleRoot.locator(`[data-template-photo="${id}"]`).count(),1,`${room} rendered ${id} count mismatch`);
  assert.equal(await sampleRoot.locator('[data-action="approve-inspection-v2"], [data-action="reject-inspection-v2"]').count(),0,'read-only sample exposes approval actions');
}

const familyRoom=representatives.oceanFamily;
await api(page,'showInspectionSample',familyRoom);
const samplePhoto=page.locator('[data-template-photo="loft-stairs"] button').first();
await samplePhoto.click();
await page.locator('#modal-root .modal').waitFor();
const modalText=await page.locator('#modal-root .modal').innerText();
assert.match(modalText,/복층 계단/);
assert.match(modalText,/읽기 전용 관리자 검수 샘플/);
await page.locator('#modal-root [data-action="close-modal"]').first().click();
await page.waitForFunction(()=>!document.querySelector('#modal-root .modal'));

const durableAfterSamples=await api(page,'fingerprint');
assert.equal(durableAfterSamples,durableBefore,'opening inspection samples changed durable ledgers');
const repeat=await api(page,'repeatRender',8);
assert.equal(repeat.equal,true,'re-rendering an inspection sample changed durable ledgers');
await api(page,'assertUnique');

// A newly prepared maid submission and the real admin inspection must use the same current universal slots.
await api(page,'resetScenario',0);
const prepared=await api(page,'prepareSubmission','528');
assert.equal(prepared.requiredDone,true,'528 current required photos were not prepared');
const maidParity=await api(page,'maidTemplateParity','528');
assert.equal(maidParity.same,true,'maid task differs from its current template snapshot');
for(const id of universalIds)assert.equal(maidParity.expected.filter(item=>item.id===id).length,1,`maid 528 missing ${id}`);
await api(page,'submitCleaning','528');
await api(page,'showInspection','528');
await page.locator('.inspection-template-review').waitFor();
const realInspection=await api(page,'inspectionTemplateParity','528');
assert.equal(realInspection.same,true,'real admin inspection differs from submitted maid snapshot');
for(const id of universalIds)assert.equal(realInspection.expected.filter(item=>item.id===id).length,1,`real inspection 528 missing ${id}`);
for(const id of universalIds)assert.equal(await page.locator(`.inspection-template-review [data-template-photo="${id}"]`).count(),1,`real inspection rendered ${id} count mismatch`);
assert.equal(await page.locator('[data-action="inspection-sample-open"][data-id="528"]').count(),1,'real inspection does not link to the current template sample');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:1000}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(base,{waitUntil:'domcontentloaded'});
  const responsiveAudit=await api(responsive,'universalCheckoutTemplateAudit');
  const room=responsiveAudit.find(item=>item.typeId==='oceanFamily').room;
  const contract=await api(responsive,'showInspectionSample',room);
  assert.equal(contract.same,true,`${width}px inspection sample contract mismatch`);
  await responsive.locator(`[data-inspection-sample-room="${room}"]`).waitFor();
  assert.equal(await responsive.locator('[data-template-photo="loft-stairs"]').count(),1);
  assert.equal(await responsive.locator('[data-template-photo="loft-wide"]').count(),1);
  assert.equal(await responsive.locator('[data-template-photo="pantry"]').count(),1);
  const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await responsive.close();
}

await page.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered universal loft/pantry templates and 121-room inspection samples QA: passed');
