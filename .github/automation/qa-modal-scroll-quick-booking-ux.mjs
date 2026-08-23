import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const expectedCounts={standard:22,premium:51,oceanPremium:13,oceanFamily:35};
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function modalDiagnostics(page,label){
  const state=await page.evaluate(()=>({
    label:document.querySelector('#modal-title')?.textContent||'',
    windowScrollY:window.scrollY,
    bodyTop:document.body.style.top,
    bodyPosition:document.body.style.position,
    historyLayer:history.state?.layer||null,
    routeScrollY:history.state?.route?.scrollY??null,
    historyIndex:history.state?.index??null,
    activeTag:document.activeElement?.tagName||null,
  }));
  console.log(`${label} ${JSON.stringify(state)}`);
  return state;
}

async function closeModalAndMeasure(page,before){
  await page.locator('#modal-root [data-action="close-modal"]').first().click();
  await page.waitForFunction(()=>!document.querySelector('#modal-root .modal'));
  await page.waitForTimeout(180);
  const after=await page.evaluate(()=>window.scrollY);
  assert.ok(Math.abs(after-before)<=4,`modal close scroll changed from ${before} to ${after}`);
}

const desktop=await browser.newPage({viewport:{width:1440,height:900}});
observe(desktop,'desktop');
await desktop.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'networkidle'});
await desktop.locator('[data-action="filter-room-type"]').first().waitFor();
assert.match(await desktop.title(),/CASTLE THE ART/);
for(const [type,count] of Object.entries(expectedCounts)){
  await desktop.locator(`[data-action="filter-room-type"][data-type="${type}"]`).click();
  await desktop.waitForFunction(({type,count})=>document.querySelector('[data-control="room-type-filter"]')?.value===type&&document.querySelectorAll('.room-card-v2').length===count,{type,count});
  assert.equal(await desktop.locator(`[data-action="filter-room-type"][data-type="${type}"]`).getAttribute('aria-pressed'),'true');
}
await desktop.locator('[data-action="filter-room-type"][data-type="premium"]').click();
await desktop.screenshot({path:'WIREFRAME/QA/screenshots/admin-room-type-filter-1440.png',fullPage:false});

const roomCard=desktop.locator('.room-card-v2').nth(24);
await roomCard.scrollIntoViewIfNeeded();
const roomBefore=await desktop.evaluate(()=>window.scrollY);
console.log(`ROOM_BEFORE ${roomBefore}`);
await roomCard.locator('[data-action="reservation-edit"], [data-action="quick-reservation-edit"]').first().click();
await desktop.locator('#modal-root .modal').waitFor();
await modalDiagnostics(desktop,'ROOM_MODAL_OPEN');
await closeModalAndMeasure(desktop,roomBefore);

await desktop.goto(`${base}#scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'networkidle'});
await desktop.locator('#quick-grid-scroller').waitFor();
const existingReservation=desktop.locator('#quick-grid-scroller [data-action="quick-reservation-edit"]').first();
await existingReservation.scrollIntoViewIfNeeded();
await desktop.evaluate(()=>window.scrollBy(0,180));
const quickBefore=await desktop.evaluate(()=>({pageY:window.scrollY,left:document.getElementById('quick-grid-scroller').scrollLeft,top:document.getElementById('quick-grid-scroller').scrollTop}));
await existingReservation.click();
await desktop.locator('#modal-root .modal').waitFor();
await modalDiagnostics(desktop,'QUICK_MODAL_OPEN');
await closeModalAndMeasure(desktop,quickBefore.pageY);
const quickAfter=await desktop.evaluate(()=>({left:document.getElementById('quick-grid-scroller').scrollLeft,top:document.getElementById('quick-grid-scroller').scrollTop}));
assert.ok(Math.abs(quickAfter.left-quickBefore.left)<=2,'quick grid horizontal position changed after modal close');
assert.ok(Math.abs(quickAfter.top-quickBefore.top)<=2,'quick grid vertical position changed after modal close');

const mobile=await browser.newPage({viewport:{width:390,height:844}});
observe(mobile,'mobile');
await mobile.goto(`${base}#scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'networkidle'});
await mobile.locator('#quick-grid-scroller').waitFor();
const mobileStyle=await mobile.evaluate(()=>{const el=document.getElementById('quick-grid-scroller'),style=getComputedStyle(el);return {overflowY:style.overflowY,maxHeight:style.maxHeight,minHeight:style.minHeight};});
assert.equal(mobileStyle.overflowY,'hidden');
await mobile.evaluate(()=>{const shell=document.querySelector('.quick-grid-shell');window.scrollTo(0,Math.max(0,shell.getBoundingClientRect().top+window.scrollY-100));});
const box=await mobile.locator('#quick-grid-scroller').boundingBox();
assert.ok(box,'mobile quick grid has no bounding box');
const mobileBefore=await mobile.evaluate(()=>({pageY:window.scrollY,top:document.getElementById('quick-grid-scroller').scrollTop}));
await mobile.mouse.move(box.x+Math.min(120,box.width/2),box.y+Math.min(220,box.height/2));
await mobile.mouse.wheel(0,700);
await mobile.waitForTimeout(180);
const mobileAfter=await mobile.evaluate(()=>({pageY:window.scrollY,top:document.getElementById('quick-grid-scroller').scrollTop}));
assert.ok(mobileAfter.pageY>mobileBefore.pageY+80,`page did not continue scrolling over grid: ${mobileBefore.pageY} -> ${mobileAfter.pageY}`);
assert.equal(mobileAfter.top,0);
await mobile.evaluate(()=>window.scrollTo(0,document.documentElement.scrollHeight));
await mobile.waitForTimeout(120);
const lastVisibility=await mobile.evaluate(()=>{const last=document.querySelector('.quick-grid-data-row:last-child'),nav=document.querySelector('.bottom-nav');const lastRect=last.getBoundingClientRect(),navRect=nav.getBoundingClientRect();return {lastBottom:lastRect.bottom,navTop:navRect.top};});
assert.ok(lastVisibility.lastBottom<=lastVisibility.navTop+2,`last row is hidden behind bottom nav: ${JSON.stringify(lastVisibility)}`);
await mobile.screenshot({path:'WIREFRAME/QA/screenshots/admin-quick-booking-mobile-scroll-390.png',fullPage:false});

for(const width of [360,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  observe(page,`overflow-${width}`);
  await page.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'domcontentloaded'});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await page.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered modal, mobile quick-booking, and room-type filter QA: passed');
