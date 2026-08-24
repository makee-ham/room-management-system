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

await api(page,'setOperationalMoment','2026-08-15','12:59');
let inspection=await api(page,'checkoutInspectionState','117');
assert.equal(inspection.pending,false,'room entered checkout inspection before checkout time');

await api(page,'setOperationalMoment','2026-08-15','13:00');
inspection=await api(page,'checkoutInspectionState','117');
assert.equal(inspection.pending,true,'room did not enter checkout inspection at checkout time');
assert.equal(inspection.reservation.id,'reservation-demo-117');
assert.equal(inspection.presentation.key,'cleaning');

const filtered=await api(page,'setRoomFilter','checkout-inspection');
assert.ok(filtered.includes('117'),'checkout inspection room is missing from status filter');
await api(page,'showRoom','117');
const panel=page.locator('[data-checkout-inspection-room="117"]');
await panel.waitFor();
assert.equal(await panel.getAttribute('data-checkout-inspection-pending'),'true');
assert.equal(await page.locator('[data-action="complete-checkout-inspection"][data-id="117"]').count(),1);

const beforeManual=await api(page,'counts');
const manual=await api(page,'completeCheckoutInspection','117','manual');
assert.equal(manual.created,true);
assert.equal(manual.record.method,'manual');
inspection=await api(page,'checkoutInspectionState','117');
assert.equal(inspection.pending,false);
assert.equal(inspection.record.method,'manual');
assert.equal(inspection.presentation.key,'cleaning','manual checkout inspection completion incorrectly cleared cleaning need');
const duplicateManual=await api(page,'completeCheckoutInspection','117','manual');
assert.equal(duplicateManual.created,false);
assert.equal(duplicateManual.duplicate,true);
const afterManual=await api(page,'counts');
assert.equal(afterManual.events,beforeManual.events+1,'manual inspection completion created duplicate events');

await api(page,'resetScenario',0);
await api(page,'setOperationalMoment','2026-08-15','13:00');
inspection=await api(page,'checkoutInspectionState','117');
assert.equal(inspection.pending,true);
const cleaning=await api(page,'completeCheckoutInspectionByCleaning','117');
assert.equal(cleaning.created,true);
assert.equal(cleaning.record.method,'cleaning');
inspection=await api(page,'checkoutInspectionState','117');
assert.equal(inspection.pending,false,'field completion did not clear checkout inspection');
assert.equal(inspection.record.method,'cleaning');
const duplicateCleaning=await api(page,'completeCheckoutInspectionByCleaning','117');
assert.equal(duplicateCleaning.created,false);
assert.equal(duplicateCleaning.duplicate,true);

await api(page,'resetScenario',0);
await api(page,'setOperationalMoment','2026-08-15','13:00');
const candidate=(await api(page,'manualCleaningCandidates')).find(item=>item.room!=='117');
assert.ok(candidate,'no additional-cleaning candidate for checkout inspection isolation test');
await api(page,'setManualCleaning',candidate.room,true);
const candidateInspection=await api(page,'checkoutInspectionState',candidate.room);
assert.equal(candidateInspection.pending,false,'additional or stayover cleaning created checkout inspection without checkout reservation');
await api(page,'setManualCleaning',candidate.room,false);

assert.equal(await api(page,'assertUnique'),true);
const rerender=await api(page,'repeatRender',12);
assert.equal(rerender.equal,true,'re-render changed checkout inspection durable ledger');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:950}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'domcontentloaded'});
  await api(responsive,'setOperationalMoment','2026-08-15','13:00');
  await api(responsive,'showRoom','117');
  await responsive.locator('[data-checkout-inspection-room="117"]').waitFor();
  const overflow=await responsive.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await responsive.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Checkout inspection rendered QA: passed');
