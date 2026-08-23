import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const baseRoute='#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function api(page,method,...args){
  return page.evaluate(({method,args})=>{
    const target=window.__CASTLE_TEST__;
    if(!target||typeof target[method]!=='function')throw new Error(`Missing test API method: ${method}`);
    return target[method](...args);
  },{method,args});
}

const page=await browser.newPage({viewport:{width:1440,height:1000}});
observe(page,'idempotency');
await page.goto(`${base}${baseRoute}`,{waitUntil:'networkidle'});
await page.waitForFunction(()=>!!window.__CASTLE_TEST__);

const renderResult=await api(page,'repeatRender',12);
assert.equal(renderResult.equal,true,'repeated render mutated a durable ledger');
assert.equal(renderResult.before,renderResult.after);
assert.equal(await api(page,'assertUnique'),true);

await api(page,'resetScenario',0);
const reservationBefore=await api(page,'counts');
const created=await api(page,'createReservationTest',35);
assert.equal(created.result.error,undefined,created.result.error||'reservation test create failed');
assert.equal(created.result.duplicate,undefined);
const afterReservationCreate=await api(page,'counts');
assert.equal(afterReservationCreate.reservations,reservationBefore.reservations+1);
assert.ok(afterReservationCreate.drafts>=reservationBefore.drafts,'reservation create unexpectedly removed a cleaning draft');
assert.equal(afterReservationCreate.events,reservationBefore.events+1);

const duplicate=await api(page,'upsertReservation',created.input);
assert.equal(duplicate.duplicate,true);
assert.equal(duplicate.unchanged,true);
assert.equal(duplicate.reservation.id,created.result.reservation.id);
const afterReservationDuplicate=await api(page,'counts');
assert.deepEqual(afterReservationDuplicate,afterReservationCreate,'duplicate reservation changed durable counts or totals');

const unchangedInput={...created.input,id:created.result.reservation.id};
const unchanged=await api(page,'upsertReservation',unchangedInput);
assert.equal(unchanged.duplicate,true);
assert.equal(unchanged.unchanged,true);
const afterUnchangedUpdate=await api(page,'counts');
assert.deepEqual(afterUnchangedUpdate,afterReservationCreate,'unchanged reservation update changed durable counts or totals');

const distinct=await api(page,'createReservationTest',70);
assert.equal(distinct.result.error,undefined,distinct.result.error||'distinct reservation test create failed');
assert.notEqual(distinct.result.reservation.id,created.result.reservation.id);
const afterDistinct=await api(page,'counts');
assert.equal(afterDistinct.reservations,afterReservationCreate.reservations+1,'a distinct valid reservation did not create a separate record');
assert.equal(afterDistinct.events,afterReservationCreate.events+1,'a distinct valid reservation did not create its own audit event');
assert.equal(await api(page,'assertUnique'),true);
const reservationRerender=await api(page,'repeatRender',6);
assert.equal(reservationRerender.equal,true,'render after reservation mutations changed durable records');

await api(page,'resetScenario',3);
const prepared=await api(page,'prepareSubmission','528');
assert.equal(prepared.requiredDone,true,'submission test fixture did not complete required photos');
const submissionBefore=await api(page,'counts');
const firstSubmission=await api(page,'submitCleaning','528');
assert.equal(firstSubmission.error,undefined,firstSubmission.error||'first cleaning submission failed');
assert.equal(firstSubmission.created,true);
assert.match(firstSubmission.submission.id,new RegExp(`^submission-${prepared.attemptId.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')}$`));
const afterFirstSubmission=await api(page,'counts');
assert.equal(afterFirstSubmission.submissions,submissionBefore.submissions+1);
assert.equal(afterFirstSubmission.events,submissionBefore.events+1);
const secondSubmission=await api(page,'submitCleaning','528');
assert.equal(secondSubmission.created,false);
assert.equal(secondSubmission.duplicate,true);
assert.equal(secondSubmission.submission.id,firstSubmission.submission.id);
const afterSecondSubmission=await api(page,'counts');
assert.deepEqual(afterSecondSubmission,afterFirstSubmission,'same cleaning attempt created a duplicate submission or event');
assert.equal(await api(page,'assertUnique'),true);

await api(page,'resetScenario',4);
const earningBefore=await api(page,'counts');
const firstEarning=await api(page,'confirmEarning','350');
assert.equal(firstEarning.invalid,undefined,'first earning was invalid');
assert.equal(firstEarning.created,true);
assert.ok(firstEarning.record?.total>0,'first earning has no amount');
const afterFirstEarning=await api(page,'counts');
assert.equal(afterFirstEarning.earnings,earningBefore.earnings+1);
assert.equal(afterFirstEarning.earningTotal,earningBefore.earningTotal+firstEarning.record.total);
const secondEarning=await api(page,'confirmEarning','350');
assert.equal(secondEarning.created,false);
assert.equal(secondEarning.record.id,firstEarning.record.id);
const afterSecondEarning=await api(page,'counts');
assert.deepEqual(afterSecondEarning,afterFirstEarning,'same submission credited payroll twice');
assert.equal(await api(page,'assertUnique'),true);
const earningRerender=await api(page,'repeatRender',8);
assert.equal(earningRerender.equal,true,'render duplicated or changed payroll credit');

await api(page,'resetScenario',10);
const paymentContext=await api(page,'paymentTestContext');
assert.ok(paymentContext,'no open payment context with confirmed earnings was found');
const paymentBefore=await api(page,'counts');
const payingFirst=await api(page,'setPaymentStatus',paymentContext.weekStart,paymentContext.maidId,'PAYING');
assert.equal(payingFirst.record.status,'PAYING');
assert.ok(payingFirst.record.amountSnapshot>0,'PAYING did not snapshot an amount');
assert.equal(new Set(payingFirst.record.taskIds).size,payingFirst.record.taskIds.length,'PAYING snapshot contains duplicate earning IDs');
const afterPayingFirst=await api(page,'counts');
assert.equal(afterPayingFirst.payments,paymentBefore.payments+1);
const payingSecond=await api(page,'setPaymentStatus',paymentContext.weekStart,paymentContext.maidId,'PAYING');
assert.deepEqual(payingSecond.record,payingFirst.record,'repeated PAYING changed the locked payment record');
const afterPayingSecond=await api(page,'counts');
assert.deepEqual(afterPayingSecond,afterPayingFirst,'repeated PAYING created a duplicate payment record');

const paidFirst=await api(page,'setPaymentStatus',paymentContext.weekStart,paymentContext.maidId,'PAID');
assert.equal(paidFirst.record.status,'PAID');
const afterPaidFirst=await api(page,'counts');
const paidSecond=await api(page,'setPaymentStatus',paymentContext.weekStart,paymentContext.maidId,'PAID');
assert.deepEqual(paidSecond.record,paidFirst.record,'repeated PAID rewrote the completed payment record');
const afterPaidSecond=await api(page,'counts');
assert.deepEqual(afterPaidSecond,afterPaidFirst,'repeated PAID created a duplicate payment record or amount');
assert.equal(await api(page,'assertUnique'),true);
const paymentRerender=await api(page,'repeatRender',12);
assert.equal(paymentRerender.equal,true,'render changed payment or payroll records');

for(const width of [390,768,1440]){
  const responsive=await browser.newPage({viewport:{width,height:1000}});
  observe(responsive,`responsive-${width}`);
  await responsive.goto(`${base}${baseRoute}`,{waitUntil:'domcontentloaded'});
  await responsive.waitForFunction(()=>!!window.__CASTLE_TEST__);
  const result=await responsive.evaluate(()=>({
    overflow:document.documentElement.scrollWidth-window.innerWidth,
    renderStable:window.__CASTLE_TEST__.repeatRender(3).equal,
    unique:window.__CASTLE_TEST__.assertUnique(),
  }));
  assert.ok(result.overflow<=1,`${width}px horizontal overflow: ${result.overflow}`);
  assert.equal(result.renderStable,true,`${width}px repeated render changed durable state`);
  assert.equal(result.unique,true,`${width}px duplicate durable records were detected`);
  await responsive.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Reservation, cleaning, payroll, and payment idempotency QA: passed');
