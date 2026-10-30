#!/usr/bin/env node
// Responsive UI journeys with demo data only. All non-local requests are blocked.
import assert from 'node:assert/strict';
import {mkdir, readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=(process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177').replace(/\/$/,'');
const widths=[360,390,768,1024,1280,1440];
const source=await readFile('WIREFRAME/index.html','utf8');
const boot='      void bootApplication();\n    })();';
assert.equal(source.split(boot).length,2,'unique application boot hook');
const browser=await chromium.launch({headless:true});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',reducedMotion:'reduce',locale:'ko-KR'});
const page=await context.newPage(),errors=[],external=[],checked=[];
page.setDefaultTimeout(10000);
page.on('pageerror',e=>errors.push(e.message));
page.on('console',m=>{if(['warning','error'].includes(m.type())&&m.text()!=='Service Worker registration blocked by Playwright')errors.push(m.text());});
await page.route('**/*',async route=>{
  const url=new URL(route.request().url());
  if(url.origin!==origin){external.push(url.origin);return route.abort();}
  if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});
  if(url.pathname==='/'||url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,'      window.__responsiveModal = showModal;\n'+boot)});
  return route.continue();
});
const action=(name,extra='')=>page.locator(`[data-action="${name}"]${extra}:visible`).first();
async function nav(view){await action('nav',`[data-view="${view}"]`).click();await page.waitForFunction(view=>document.querySelector(`[data-action="nav"][data-view="${view}"][aria-current="page"]`),view);}
async function login(role){await page.locator('#login-id').fill(role==='admin'?'admin':'maid1');await page.locator('#login-password').fill(role==='admin'?'admin1234':'maid1234');await page.locator('#login-form').press('Enter');await action('logout').waitFor();}
async function close(){await page.keyboard.press('Escape');await page.locator('[role=dialog]').waitFor({state:'hidden'});}
async function check(name,{evidence=false}={}){
  for(const width of widths){
    await page.setViewportSize({width,height:900});
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    // Let the existing 160–200ms control transitions finish after a breakpoint change.
    await page.waitForTimeout(220);
    const result=await page.evaluate(()=>{
      const root=document.querySelector('[role=dialog]')||document.querySelector('#main-content'),issues=[];
      const visible=e=>e.checkVisibility()&&e.getBoundingClientRect().width>0;
      for(const e of root.querySelectorAll('button,input:not([type=hidden]),select,textarea')){
        if(!visible(e))continue;
        const rect=e.getBoundingClientRect(),name=(e.getAttribute('aria-label')||e.textContent||e.id).trim().slice(0,65);
        let inScrollable=false;
        for(let p=e.parentElement;p&&p!==root;p=p.parentElement){if(p.scrollWidth>p.clientWidth+2&&['auto','scroll'].includes(getComputedStyle(p).overflowX)){inScrollable=true;break;}}
        if(!inScrollable&&(rect.left< -1||rect.right>innerWidth+1))issues.push(`outside viewport: ${name}`);
        if(e.matches('.btn,.icon-btn,.select-control,.input-control')&&(rect.height<43.5||rect.width<43.5))issues.push(`target below 44px: ${name}`);
        if(e.matches('.btn')&&e.scrollWidth>e.clientWidth+2)issues.push(`clipped button: ${name}`);
        if(e.matches('button')&&!e.getAttribute('aria-label')&&!e.textContent.trim()&&!e.getAttribute('aria-labelledby'))issues.push('button without accessible name');
      }
      const dialog=document.querySelector('[role=dialog]'),foot=dialog?.querySelector('.modal-foot');
      if(foot){
        const buttons=[...foot.querySelectorAll('button')].filter(visible);
        for(const b of buttons){const r=b.getBoundingClientRect();if(r.bottom>innerHeight+1||r.top<0)issues.push('modal footer outside viewport');}
        const trailing=[...foot.children].filter(e=>e.matches('button'));
        if(trailing.length===2){const [cancel,confirm]=trailing.map(e=>e.getBoundingClientRect());if(confirm.left<cancel.right-1||Math.abs(confirm.top-cancel.top)>1)issues.push('confirmation is not right of cancel');}
        if(trailing.length===1){const r=trailing[0].getBoundingClientRect(),f=foot.getBoundingClientRect(),right=f.right-parseFloat(getComputedStyle(foot).paddingRight);if(Math.abs(r.right-right)>2)issues.push('single footer button is not aligned to right edge');}
      }
      return {issues,overflow:document.documentElement.scrollWidth>innerWidth,content:root.textContent.trim().length};
    });
    assert(result.content>0,`${name}/${width}: blank content`);
    assert(!result.overflow,`${name}/${width}: page overflow`);
    assert.deepEqual(result.issues,[],`${name}/${width}`);
    if(evidence&&[390,1024,1440].includes(width))await page.screenshot({path:`WIREFRAME/QA/screenshots/responsive-${name}-${width}.png`});
  }
  checked.push(name);
}
async function modal(name,open,{evidence=false,keyboard=false}={}){
  await open();await page.locator('[role=dialog]').waitFor();await check(name,{evidence});
  if(keyboard){
    await page.setViewportSize({width:390,height:900});
    const focusables=page.locator('[role=dialog]').locator('button:visible:not(:disabled),input:visible:not(:disabled),select:visible:not(:disabled),textarea:visible:not(:disabled),[tabindex="0"]:visible');
    await focusables.last().focus();await page.keyboard.press('Tab');assert(await page.evaluate(()=>!!document.activeElement.closest('[role=dialog]')),'Tab escaped dialog');
    await focusables.first().focus();await page.keyboard.press('Shift+Tab');assert(await page.evaluate(()=>!!document.activeElement.closest('[role=dialog]')),'Shift+Tab escaped dialog');
  }
  if(['pin','reservation'].includes(name)){
    for(const viewport of [{width:360,height:480},{width:768,height:390}]){
      await page.setViewportSize(viewport);
      assert(await page.locator('.modal-foot button').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)?.closest('button')===e;})),name+' short viewport footer');
      const body=page.locator('.modal-body,.pin-sheet-body');await body.evaluate(e=>{e.scrollTop=e.scrollHeight;});
      assert(await body.evaluate(e=>e.clientHeight>0&&e.scrollTop+e.clientHeight>=e.scrollHeight-1),name+' scrollable body');
    }
  }
  await close();
}

try{
  await mkdir('WIREFRAME/QA/screenshots',{recursive:true});
  await page.goto(origin+'/index.html?scenario=0&role=admin&view=today&date=2026-08-15');
  await page.locator('#login-form').waitFor();await check('login');
  assert((await page.title()).includes('CASTLE THE ART'));assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);
  await login('admin');await page.waitForTimeout(3500);
  await check('admin-today');await page.locator('[data-action=toggle-section]:visible').filter({hasText:'청소 검수'}).first().click();await action('go-inspection').click();await page.waitForFunction(()=>document.querySelector('[data-action=cleaning-tab][data-tab=inspection]')?.getAttribute('aria-selected')==='true');
  await nav('rooms');await check('rooms',{evidence:true});
  await page.locator('#room-search').fill('99999');await page.locator('#room-search').press('Enter');await check('room-empty');await page.locator('#room-search').fill('');await page.locator('#room-search').press('Enter');
  await modal('calendar',()=>action('open-calendar').click(),{keyboard:true});
  await modal('export',()=>action('open-room-export').click());
  await modal('operation-demo',()=>action('operation-status').click());
  await modal('pin',()=>action('pin-edit').click(),{keyboard:true});
  await modal('reservation',()=>action('room-reservation-status').click(),{keyboard:true,evidence:true});
  await action('room-detail').click();await check('room-detail');
  await modal('room-metadata',()=>action('edit-room-info').click());
  await action('back').click();await action('room-detail').waitFor();
  await nav('quickReservation');await check('quick-reservation');
  await action('quick-reservation-enter-fullscreen').click();await check('calendar-fullscreen');await page.keyboard.press('Escape');
  await nav('cleaning');await action('cleaning-tab','[data-tab="assignment-today"]').click();await check('assignment-today');
  await modal('new-cleaning',()=>action('new-cleaning').click());
  for(const tab of ['assignment-tomorrow','progress','inspection','done']){await action('cleaning-tab',`[data-tab="${tab}"]`).click();await check('cleaning-'+tab);}
  await action('cleaning-tab','[data-tab="inspection"]').click();
  await action('cleaning-detail').click();await check('inspection-detail');await action('back').click();
  await nav('maids');
  for(const tab of ['workforce','history','pay','complaints']){await action('admin-maid-tab',`[data-tab="${tab}"]`).click();await check('maids-'+tab);}
  await action('admin-maid-tab','[data-tab="workforce"]').click();await action('maid-detail').click();await check('maid-detail');
  await nav('more');await check('admin-more');
  for(const name of ['audit-log','rates','account-status'])await modal(name,()=>action(name).click(),{keyboard:name==='account-status'});
  await modal('notifications',()=>action('alerts').click(),{keyboard:true});
  await action('account-status').click();await page.locator('[role=dialog]').waitFor();await page.goBack();await page.locator('[role=dialog]').waitFor({state:'hidden'});await page.waitForFunction(()=>document.activeElement.dataset.action==='account-status');
  await action('logout').click();await login('maid');
  for(const view of ['my','schedule','done','pay','more']){await nav(view);await check('maid-'+view);}
  await nav('my');await action('cleaning-detail','[data-id="332"]').click();await check('maid-cleaning',{evidence:true});
  await page.setViewportSize({width:1024,height:900});await action('capture-task-photo').scrollIntoViewIfNeeded();
  await page.screenshot({path:'WIREFRAME/QA/screenshots/responsive-maid-photo-1024.png'});await action('back').click();
  await nav('pay');await modal('pay-calendar',()=>action('open-pay-calendar').click(),{keyboard:true});await action('toggle-maid-pay-week').click();await check('maid-pay-expanded');
  await nav('more');await modal('notification-settings',()=>action('notification-permission').click());
  for(const leading of [false,true]){
    await modal('single-footer-'+leading,()=>page.evaluate(leading=>window.__responsiveModal({title:'확인 · 합성 UI 검증',body:'<p>보조 행동이 있는 결과 화면의 닫기 정렬</p>',closeLabel:'확인',...(leading?{secondaryLabel:'다시 확인',secondaryAction:'close-modal'}:{})}),leading),{evidence:leading,keyboard:true});
  }
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(`[ok] ${checked.length} screens/dialogs × ${widths.join('/')}px: meaningful content, viewport bounds, 44px controls, button names and unclipped labels`);
  console.log('[ok] modal confirm/cancel alignment, keyboard containment, Escape, browser Back and trigger focus');
  console.log('[ok] admin/maid navigation, tabs, room actions, reservation/calendar, inspection, work/payroll/history, notification/settings destinations');
  console.log('[ok] page exceptions, console warning/error and external business requests: 0');
  console.log(`Environment: Playwright Chromium ${await browser.version()}; Browser plugin not available. Synthetic demo only.`);
}finally{await browser.close();}
