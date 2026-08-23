import { chromium } from 'playwright';

const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:900}});
const base='http://127.0.0.1:4173/index.html';
await page.goto(`${base}#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=`,{waitUntil:'networkidle'});
await page.locator('[data-action="filter-room-type"][data-type="premium"]').click();
await page.waitForFunction(()=>document.querySelectorAll('.room-card-v2').length===51);
const card=page.locator('.room-card-v2').nth(24);
await card.scrollIntoViewIfNeeded();
const before=await page.evaluate(()=>window.scrollY);
await card.locator('[data-action="reservation-edit"], [data-action="quick-reservation-edit"]').first().click();
await page.locator('#modal-root .modal').waitFor();
const open=await page.evaluate(()=>({scrollY:window.scrollY,bodyTop:document.body.style.top,bodyPosition:document.body.style.position,route:history.state?.route,layer:history.state?.layer,href:location.href}));
await page.locator('#modal-root [data-action="close-modal"]').first().click();
await page.waitForFunction(()=>!document.querySelector('#modal-root .modal'));
await page.waitForTimeout(220);
const after=await page.evaluate(()=>({
  scrollY:window.scrollY,
  scrollHeight:document.documentElement.scrollHeight,
  clientHeight:document.documentElement.clientHeight,
  bodyTop:document.body.style.top,
  bodyPosition:document.body.style.position,
  roomCards:document.querySelectorAll('.room-card-v2').length,
  roomType:document.querySelector('[data-control="room-type-filter"]')?.value,
  roomFilter:document.querySelector('[data-control="room-filter"]')?.value,
  title:document.querySelector('h1')?.textContent,
  route:history.state?.route,
  layer:history.state?.layer,
  historyLength:history.length,
  href:location.href,
  activeAction:document.activeElement?.dataset?.action||null,
  activeId:document.activeElement?.dataset?.id||null,
  mainTop:document.querySelector('#main-content')?.getBoundingClientRect().top,
}));
console.log(`MODAL_SCROLL_DIAGNOSTIC ${JSON.stringify({before,open,after})}`);
await browser.close();
