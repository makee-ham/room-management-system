import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html';
const browser=await chromium.launch({headless:true});
const errors=[];

function installFixedDate(page,iso){
  return page.addInitScript(({iso})=>{
    const NativeDate=Date;
    const fixed=NativeDate.parse(`${iso}T00:05:00+09:00`);
    class FixedDate extends NativeDate{
      constructor(...args){super(...(args.length?args:[window.__castleFixedNow??fixed]));}
      static now(){return window.__castleFixedNow??fixed;}
      static parse(value){return NativeDate.parse(value);}
      static UTC(...args){return NativeDate.UTC(...args);}
    }
    Object.setPrototypeOf(FixedDate,NativeDate);
    window.__castleFixedNow=fixed;
    window.Date=FixedDate;
  },{iso});
}

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function quickDates(page){
  return page.evaluate(()=>{
    const root=document.getElementById('quick-grid-scroller');
    if(!root)return [];
    const values=[...root.querySelectorAll('[data-date]')]
      .map(node=>node.getAttribute('data-date'))
      .filter(value=>/^\d{4}-\d{2}-\d{2}$/.test(value||''));
    return [...new Set(values)].sort();
  });
}

async function waitForRange(page,first,last){
  await page.waitForFunction(({first,last})=>{
    const root=document.getElementById('quick-grid-scroller');
    if(!root)return false;
    const dates=[...new Set([...root.querySelectorAll('[data-date]')]
      .map(node=>node.getAttribute('data-date'))
      .filter(value=>/^\d{4}-\d{2}-\d{2}$/.test(value||'')))].sort();
    return dates.length===29&&dates[0]===first&&dates.at(-1)===last;
  },{first,last});
}

async function openAt(iso,{hash='scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=',width=1440}={}){
  const context=await browser.newContext({viewport:{width,height:900},timezoneId:'Asia/Seoul'});
  const page=await context.newPage();
  observe(page,`${iso}-${width}`);
  await installFixedDate(page,iso);
  await page.goto(`${base}#${hash}`,{waitUntil:'networkidle'});
  await page.locator('#quick-grid-scroller').waitFor();
  return {context,page};
}

{
  const {context,page}=await openAt('2026-08-25');
  await waitForRange(page,'2026-08-18','2026-09-15');
  assert.deepEqual(await quickDates(page),Array.from({length:29},(_,index)=>{
    const date=new Date(Date.UTC(2026,7,18+index));
    return date.toISOString().slice(0,10);
  }));
  const text=await page.locator('body').innerText();
  assert.match(text,/8\.18\s*[–~-]\s*9\.15/);
  assert.match(text,/29일/);

  const nextButton=page.locator('[data-offset="7"]').first();
  await nextButton.click();
  await waitForRange(page,'2026-08-25','2026-09-22');
  await page.locator('[data-action="quick-month-today"]').first().click();
  await waitForRange(page,'2026-08-18','2026-09-15');

  // While following Today, a KST date rollover updates the rolling window.
  await page.evaluate(()=>{window.__castleFixedNow=Date.parse('2026-08-26T00:05:00+09:00');window.dispatchEvent(new Event('focus'));});
  await waitForRange(page,'2026-08-19','2026-09-16');

  // Manual browsing is not pulled back to Today on the next rollover.
  await nextButton.click();
  await waitForRange(page,'2026-08-26','2026-09-23');
  await page.evaluate(()=>{window.__castleFixedNow=Date.parse('2026-08-27T00:05:00+09:00');window.dispatchEvent(new Event('focus'));});
  await page.waitForTimeout(100);
  await waitForRange(page,'2026-08-26','2026-09-23');
  await context.close();
}

{
  const {context,page}=await openAt('2026-08-26');
  await waitForRange(page,'2026-08-19','2026-09-16');
  await context.close();
}

{
  const explicit='scenario=0&role=admin&view=quickReservation&date=2026-08-15&filter=all&type=all&q=&bookingAnchor=2026-09-10';
  const {context,page}=await openAt('2026-08-25',{hash:explicit});
  await waitForRange(page,'2026-09-03','2026-10-01');
  await context.close();
}

for(const width of [390,768,1440]){
  const {context,page}=await openAt('2026-08-25',{width});
  await waitForRange(page,'2026-08-18','2026-09-15');
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await context.close();
}

await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered KST-today rolling 29-day quick reservation QA: passed');
