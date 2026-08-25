import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true});
const errors=[];

async function installClock(page,initialIso='2026-08-25T03:00:00.000Z'){
  await page.addInitScript(({initialIso})=>{
    const NativeDate=Date;
    let mockedNow=NativeDate.parse(initialIso);
    class MockDate extends NativeDate{
      constructor(...args){super(...(args.length?args:[mockedNow]));}
      static now(){return mockedNow;}
      static parse(value){return NativeDate.parse(value);}
      static UTC(...args){return NativeDate.UTC(...args);}
    }
    Object.setPrototypeOf(MockDate,NativeDate);
    window.__setCastleMockNow=value=>{mockedNow=NativeDate.parse(value);};
    window.Date=MockDate;
  },{initialIso});
}

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function openQuick(page,{date='2026-08-15',extra=''}={}){
  const suffix=extra?`&${extra}`:'';
  await page.goto(`${base}#scenario=0&role=admin&view=quickReservation&date=${date}&filter=all&type=all&q=${suffix}`,{waitUntil:'networkidle'});
  await page.locator('#quick-grid-scroller').waitFor();
}

async function visibleDates(page){
  return page.evaluate(()=>{
    const root=document.getElementById('quick-grid-scroller');
    if(!root)return [];
    const values=[...root.querySelectorAll('[data-date]')]
      .map(node=>node.getAttribute('data-date'))
      .filter(value=>/^\d{4}-\d{2}-\d{2}$/.test(value||''));
    return [...new Set(values)].sort();
  });
}

async function expectRange(page,{start,end,mode}){
  await page.waitForFunction(({start,end,mode})=>{
    const root=document.getElementById('quick-grid-scroller');
    if(!root)return false;
    const dates=[...new Set([...root.querySelectorAll('[data-date]')]
      .map(node=>node.getAttribute('data-date'))
      .filter(value=>/^\d{4}-\d{2}-\d{2}$/.test(value||'')))].sort();
    const label=document.querySelector('.quick-month-label')?.textContent||'';
    return dates.length===29&&dates[0]===start&&dates.at(-1)===end&&label.includes(mode);
  },{start,end,mode});
  const dates=await visibleDates(page);
  assert.equal(dates.length,29);
  assert.equal(dates[0],start);
  assert.equal(dates.at(-1),end);
  assert.match((await page.locator('.quick-month-label').innerText()).replace(/\s+/g,' '),new RegExp(mode));
  return dates;
}

async function assertHealthy(page,width){
  const main=page.locator('#main-content');
  await main.waitFor();
  assert.ok((await main.innerText()).trim().length>100,`${width}px app must not be blank`);
  const body=await page.locator('body').innerText();
  assert.doesNotMatch(body,/Application error|Internal Server Error|Unhandled Runtime Error|Vite Error|Webpack Error|ReferenceError/);
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px document horizontal overflow: ${overflow}`);
}

const desktop=await browser.newPage({viewport:{width:1440,height:900}});
await installClock(desktop);
observe(desktop,'desktop');
await openQuick(desktop);
await expectRange(desktop,{start:'2026-08-18',end:'2026-09-15',mode:'오늘 기준 29일'});
assert.ok(!desktop.url().includes('bookingAnchor='),'today-following URL must not freeze a booking anchor');
assert.equal(await desktop.locator('.quick-day-header.today[data-quick-date="2026-08-25"]').count(),1,'real KST today must be highlighted');
assert.ok(await desktop.locator('.quick-date-cell.is-past[data-date="2026-08-24"]').count()>0,'the day before real KST today must be read-only');
await assertHealthy(desktop,1440);
await desktop.screenshot({path:'WIREFRAME/QA/screenshots/admin-quick-booking-kst-today-1440.png',fullPage:false});

// A tab that still follows Today moves one day at Korean midnight.
await desktop.evaluate(()=>window.__setCastleMockNow('2026-08-26T03:00:00.000Z'));
await desktop.evaluate(()=>window.dispatchEvent(new Event('focus')));
await expectRange(desktop,{start:'2026-08-19',end:'2026-09-16',mode:'오늘 기준 29일'});
assert.ok(!desktop.url().includes('bookingAnchor='),'daily rollover must remain in today-following URL mode');
assert.equal(await desktop.locator('.quick-day-header.today[data-quick-date="2026-08-26"]').count(),1);

// Seven-day browsing becomes an explicit custom range and survives the next date rollover.
await desktop.locator('[data-action="quick-month-shift"][data-offset="7"]').click();
await expectRange(desktop,{start:'2026-08-26',end:'2026-09-23',mode:'이동한 29일'});
await desktop.waitForFunction(()=>location.hash.includes('bookingAnchor=2026-09-02'));
await desktop.evaluate(()=>window.__setCastleMockNow('2026-08-27T03:00:00.000Z'));
await desktop.evaluate(()=>window.dispatchEvent(new Event('focus')));
await desktop.waitForTimeout(100);
await expectRange(desktop,{start:'2026-08-26',end:'2026-09-23',mode:'이동한 29일'});

// Today returns to the new real KST day and removes the explicit anchor.
await desktop.locator('[data-action="quick-month-today"]').click();
await expectRange(desktop,{start:'2026-08-20',end:'2026-09-17',mode:'오늘 기준 29일'});
await desktop.waitForFunction(()=>!location.hash.includes('bookingAnchor='));
assert.equal(await desktop.locator('.quick-day-header.today[data-quick-date="2026-08-27"]').count(),1);

// The selected demo operating date is independent from the real-day quick window.
const demoDatePage=await browser.newPage({viewport:{width:768,height:900}});
await installClock(demoDatePage);
observe(demoDatePage,'demo-date');
await openQuick(demoDatePage,{date:'2026-07-01'});
await expectRange(demoDatePage,{start:'2026-08-18',end:'2026-09-15',mode:'오늘 기준 29일'});
await assertHealthy(demoDatePage,768);

// Existing explicit bookingAnchor and legacy bookingMonth links remain custom ranges.
const explicitPage=await browser.newPage({viewport:{width:768,height:900}});
await installClock(explicitPage);
observe(explicitPage,'explicit');
await openQuick(explicitPage,{extra:'bookingAnchor=2026-09-10'});
await expectRange(explicitPage,{start:'2026-09-03',end:'2026-10-01',mode:'이동한 29일'});
assert.ok(explicitPage.url().includes('bookingAnchor=2026-09-10'));
await openQuick(explicitPage,{extra:'bookingMonth=2026-10'});
await expectRange(explicitPage,{start:'2026-10-08',end:'2026-11-05',mode:'이동한 29일'});

for(const width of [390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  await installClock(page);
  observe(page,`responsive-${width}`);
  await openQuick(page);
  await expectRange(page,{start:'2026-08-18',end:'2026-09-15',mode:'오늘 기준 29일'});
  await assertHealthy(page,width);
  if(width===390)await page.screenshot({path:'WIREFRAME/QA/screenshots/admin-quick-booking-kst-today-390.png',fullPage:false});
  await page.close();
}

await desktop.close();
await demoDatePage.close();
await explicitPage.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('PR #94 rebased KST daily quick-window QA: passed');
