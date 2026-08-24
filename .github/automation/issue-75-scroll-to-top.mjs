import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base='http://127.0.0.1:4173/index.html#scenario=0&role=admin&view=rooms&date=2026-08-15&filter=all&type=all&q=';
const errors=[];
const browser=await chromium.launch({headless:true});

function observe(page,label){
  page.on('pageerror',error=>errors.push(`${label} pageerror: ${error.message}`));
  page.on('console',message=>{if(message.type()==='error')errors.push(`${label} console: ${message.text()}`);});
}

async function jumpTo(page,y){
  await page.evaluate(value=>{
    const root=document.documentElement,previous=root.style.scrollBehavior;
    root.style.scrollBehavior='auto';window.scrollTo(0,value);root.style.scrollBehavior=previous;
  },y);
  await page.waitForTimeout(100);
}

const desktop=await browser.newPage({viewport:{width:1440,height:900}});
observe(desktop,'desktop');
await desktop.goto(base,{waitUntil:'networkidle'});
assert.match(await desktop.title(),/CASTLE THE ART/);
assert.ok((await desktop.locator('body').innerText()).includes('객실'),'meaningful app content is missing');
assert.equal(await desktop.locator('.nextjs-container-errors-header, vite-error-overlay, #webpack-dev-server-client-overlay').count(),0,'framework error overlay is visible');
const desktopButton=desktop.locator('#scroll-to-top');
await desktopButton.waitFor({state:'attached'});
assert.equal(await desktopButton.isVisible(),false,'scroll-to-top button must be hidden at the top');
await jumpTo(desktop,1200);
await desktop.waitForFunction(()=>{const button=document.getElementById('scroll-to-top');return button&&!button.hidden&&getComputedStyle(button).display!=='none';});
assert.ok(await desktop.evaluate(()=>window.scrollY>=600),'desktop did not reach the visibility threshold');
await desktop.screenshot({path:'/tmp/scroll-to-top-desktop.png',fullPage:false});
await desktopButton.click();
await desktop.waitForFunction(()=>window.scrollY<=4);
assert.equal(await desktop.evaluate(()=>document.activeElement?.id),'main-content','focus did not move to the main content after returning to top');
assert.equal(await desktopButton.isVisible(),false,'scroll-to-top button must hide after reaching the top');

await jumpTo(desktop,1200);
await desktop.waitForFunction(()=>!document.getElementById('scroll-to-top').hidden);
const beforeModal=await desktop.evaluate(()=>window.scrollY);
await desktop.locator('[data-action="alerts"]').click();
await desktop.locator('#modal-root .modal').waitFor();
assert.equal(await desktopButton.isVisible(),false,'scroll-to-top button must hide while a modal is open');
await desktop.locator('#modal-root [data-action="close-modal"]').first().click();
await desktop.waitForFunction(()=>!document.querySelector('#modal-root .modal'));
await desktop.waitForFunction(()=>!document.getElementById('scroll-to-top').hidden);
const afterModal=await desktop.evaluate(()=>window.scrollY);
assert.ok(Math.abs(afterModal-beforeModal)<=4,`modal changed the document position: ${beforeModal} -> ${afterModal}`);

const mobile=await browser.newPage({viewport:{width:390,height:844}});
observe(mobile,'mobile');
await mobile.emulateMedia({reducedMotion:'reduce'});
await mobile.goto(base,{waitUntil:'networkidle'});
const mobileButton=mobile.locator('#scroll-to-top');
assert.equal(await mobileButton.isVisible(),false,'mobile button must be hidden at the top');
await jumpTo(mobile,1400);
await mobile.waitForFunction(()=>!document.getElementById('scroll-to-top').hidden);
const buttonBox=await mobileButton.boundingBox();
const navBox=await mobile.locator('.bottom-nav').boundingBox();
assert.ok(buttonBox&&navBox,'mobile button or bottom navigation has no layout box');
assert.ok(buttonBox.bottom<=navBox.y-8,`mobile button overlaps bottom navigation: button bottom ${buttonBox.bottom}, nav top ${navBox.y}`);
assert.ok(buttonBox.width>=44&&buttonBox.height>=44,`mobile touch target is too small: ${buttonBox.width}×${buttonBox.height}`);
await mobile.screenshot({path:'/tmp/scroll-to-top-mobile.png',fullPage:false});
await mobileButton.click();
await mobile.waitForTimeout(80);
assert.ok(await mobile.evaluate(()=>window.scrollY<=2),'reduced-motion click did not return immediately to the top');
assert.equal(await mobileButton.isVisible(),false,'mobile button must hide at the top');

for(const width of [360,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900}});
  observe(page,`overflow-${width}`);
  await page.goto(base,{waitUntil:'domcontentloaded'});
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-window.innerWidth);
  assert.ok(overflow<=1,`${width}px horizontal overflow: ${overflow}`);
  await page.close();
}

await desktop.close();
await mobile.close();
await browser.close();
assert.deepEqual(errors,[],errors.join('\n'));
console.log('Rendered scroll-to-top interaction and responsive QA: passed');
