import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const route='#scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function waitForWindow(page,first,last){
  await page.waitForFunction(({first,last})=>{
    const headers=[...document.querySelectorAll('#quick-grid-scroller .quick-day-header')];
    return headers.length===29&&headers[0]?.dataset.quickDate===first&&headers.at(-1)?.dataset.quickDate===last;
  },{first,last});
}

const desktop=await browser.newPage({viewport:{width:1440,height:900}});
observe(desktop,'desktop');
await desktop.goto(`${base}${route}`,{waitUntil:'networkidle'});
await waitForWindow(desktop,'2026-08-08','2026-09-05');

const desktopWindow=await desktop.evaluate(()=>({
  dates:[...document.querySelectorAll('#quick-grid-scroller .quick-day-header')].map(header=>header.dataset.quickDate),
  label:document.querySelector('.quick-month-label')?.textContent.replace(/\s+/g,' ').trim(),
  scrollLeft:document.getElementById('quick-grid-scroller')?.scrollLeft,
  anchorGap:(()=>{const anchor=document.querySelector('#quick-grid-scroller [data-quick-date="2026-08-15"]'),room=document.querySelector('#quick-grid-scroller .quick-room-header');if(!anchor||!room)return null;return Math.round(anchor.getBoundingClientRect().left-room.getBoundingClientRect().right);})(),
}));
assert.equal(desktopWindow.dates.length,29);
assert.equal(desktopWindow.dates[7],'2026-08-15');
assert.match(desktopWindow.label,/8\.8–9\.5/);
assert.ok(desktopWindow.scrollLeft>0,'today column was not auto-aligned');
assert.ok(Math.abs(desktopWindow.anchorGap??999)<=3,`today column gap is ${desktopWindow.anchorGap}px`);

const septemberFirst=desktop.locator('#quick-grid-scroller [data-quick-date="2026-09-01"]');
assert.equal(await septemberFirst.getAttribute('class').then(value=>value?.includes('is-month-start')),true);
assert.match((await septemberFirst.textContent())||'',/9\/1/);

const pastCell=desktop.locator('[data-quick-row="516"] [data-date="2026-08-08"]');
assert.equal(await pastCell.getAttribute('aria-disabled'),'true');
assert.equal(await pastCell.getAttribute('data-bookable'),null);
assert.match((await pastCell.getAttribute('title'))||'',/지난 날짜/);

const crossMonth=desktop.locator('[data-id="reservation-demo-cross-month-516"]');
assert.equal(await crossMonth.count(),3);
assert.equal(await crossMonth.filter({has:desktop.locator('[data-date="impossible"]')}).count(),0);
for(const date of ['2026-08-31','2026-09-01','2026-09-02']){
  assert.equal(await desktop.locator(`[data-id="reservation-demo-cross-month-516"][data-date="${date}"]`).count(),1,`cross-month cell missing: ${date}`);
}
assert.match((await desktop.locator('[data-id="reservation-demo-cross-month-516"][data-date="2026-08-31"]').getAttribute('class'))||'',/is-start/);
assert.match((await desktop.locator('[data-id="reservation-demo-cross-month-516"][data-date="2026-09-01"]').getAttribute('class'))||'',/is-month-start/);
assert.match((await desktop.locator('[data-id="reservation-demo-cross-month-516"][data-date="2026-09-02"]').getAttribute('class'))||'',/is-end/);
const oneNight=desktop.locator('[data-id="reservation-demo-cross-month-623"][data-date="2026-08-31"]');
assert.equal(await oneNight.count(),1);
assert.match((await oneNight.getAttribute('class'))||'',/is-single/);

await desktop.locator('[data-action="quick-month-shift"][data-offset="7"]').click();
await waitForWindow(desktop,'2026-08-15','2026-09-12');
assert.match(await desktop.evaluate(()=>location.hash),/bookingAnchor=2026-08-22/);
await desktop.locator('[data-action="quick-month-today"]').click();
await waitForWindow(desktop,'2026-08-08','2026-09-05');
assert.doesNotMatch(await desktop.evaluate(()=>location.hash),/bookingAnchor=/);
await desktop.waitForTimeout(80);
const restoredGap=await desktop.evaluate(()=>{const anchor=document.querySelector('#quick-grid-scroller [data-quick-date="2026-08-15"]'),room=document.querySelector('#quick-grid-scroller .quick-room-header');return anchor&&room?Math.round(anchor.getBoundingClientRect().left-room.getBoundingClientRect().right):999;});
assert.ok(Math.abs(restoredGap)<=3,`today restore gap is ${restoredGap}px`);

const legacy=await browser.newPage({viewport:{width:768,height:900}});
observe(legacy,'legacy');
await legacy.goto(`${base}#scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=&bookingMonth=2026-09`,{waitUntil:'networkidle'});
await waitForWindow(legacy,'2026-09-08','2026-10-06');

const mobile=await browser.newPage({viewport:{width:390,height:844}});
observe(mobile,'mobile');
await mobile.goto(`${base}${route}`,{waitUntil:'networkidle'});
await waitForWindow(mobile,'2026-08-08','2026-09-05');
await mobile.locator('#quick-grid-mobile-header').waitFor();
await mobile.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';const shell=document.querySelector('.quick-grid-shell');window.scrollTo(0,shell.getBoundingClientRect().top+window.scrollY+1500);});
await mobile.waitForTimeout(100);
const sticky=await mobile.evaluate(()=>{const header=document.getElementById('quick-grid-mobile-header'),topbar=document.querySelector('.topbar');return {headerTop:Math.round(header.getBoundingClientRect().top),topbarBottom:Math.round(topbar.getBoundingClientRect().bottom),visible:header.getBoundingClientRect().bottom>0&&header.getBoundingClientRect().top<innerHeight};});
assert.equal(sticky.visible,true);
assert.ok(Math.abs(sticky.headerTop-sticky.topbarBottom)<=3,`sticky header offset mismatch: ${JSON.stringify(sticky)}`);

await mobile.evaluate(()=>{const scroller=document.getElementById('quick-grid-scroller');scroller.scrollLeft=520;scroller.dispatchEvent(new Event('scroll',{bubbles:true}));});
await mobile.waitForTimeout(80);
let sync=await mobile.evaluate(()=>({body:document.getElementById('quick-grid-scroller').scrollLeft,header:document.getElementById('quick-grid-mobile-header').scrollLeft}));
assert.ok(Math.abs(sync.body-sync.header)<=2,`body to header sync failed: ${JSON.stringify(sync)}`);
await mobile.evaluate(()=>{const header=document.getElementById('quick-grid-mobile-header');header.scrollLeft=280;header.dispatchEvent(new Event('scroll',{bubbles:true}));});
await mobile.waitForTimeout(80);
sync=await mobile.evaluate(()=>({body:document.getElementById('quick-grid-scroller').scrollLeft,header:document.getElementById('quick-grid-mobile-header').scrollLeft}));
assert.ok(Math.abs(sync.body-sync.header)<=2,`header to body sync failed: ${JSON.stringify(sync)}`);

const mobileScroller=mobile.locator('#quick-grid-scroller');
const box=await mobileScroller.boundingBox();
assert.ok(box,'mobile quick grid has no box');
const beforeWheel=await mobile.evaluate(()=>({pageY:scrollY,gridTop:document.getElementById('quick-grid-scroller').scrollTop}));
await mobile.mouse.move(box.x+Math.min(150,box.width/2),Math.min(760,Math.max(100,box.y+200)));
await mobile.mouse.wheel(0,650);
await mobile.waitForTimeout(120);
const afterWheel=await mobile.evaluate(()=>({pageY:scrollY,gridTop:document.getElementById('quick-grid-scroller').scrollTop}));
assert.ok(afterWheel.pageY>beforeWheel.pageY,`document did not scroll over grid: ${JSON.stringify({beforeWheel,afterWheel})}`);
assert.equal(afterWheel.gridTop,0);

await mobile.evaluate(()=>{document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,document.documentElement.scrollHeight);});
await mobile.waitForTimeout(100);
const lastRow=await mobile.evaluate(()=>{const last=document.querySelector('.quick-grid-data-row:last-child'),nav=document.querySelector('.bottom-nav');const lastRect=last.getBoundingClientRect(),navRect=nav.getBoundingClientRect();return {lastBottom:lastRect.bottom,navTop:navRect.top};});
assert.ok(lastRow.lastBottom<=lastRow.navTop+2,`last room is hidden: ${JSON.stringify(lastRow)}`);

for(const width of [360,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  observe(page,`overflow-${width}`);
  await page.goto(`${base}${route}`,{waitUntil:'domcontentloaded'});
  await page.locator('#quick-grid-scroller').waitFor();
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal document overflow: ${overflow}`);
  await page.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Quick reservation 29-day rendered QA: passed');
