#!/usr/bin/env node
// Browser plugin not available: isolated Playwright fixtures; no operational writes.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api',date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul'}).format(new Date());
const types=['standard','premium','oceanPremium','oceanFamily'],names=['스탠다드','프리미어','파셜 오션뷰 프리미어','패밀리 투룸'];
const rooms=[{id:'room-629',roomNumber:'629',roomTypeCode:'oceanFamily',roomTypeName:names[3]},...Array.from({length:24},(_,i)=>({id:'room-'+(117+i*10),roomNumber:String(117+i*10),roomTypeCode:types[i%4],roomTypeName:names[i%4]}))].reverse().map(r=>({...r,stateVersion:1,occupied:false}));
const assignments=types.map((type,i)=>({assignmentId:'assignment-'+i,cleaningTargetId:'target-'+i,roomId:rooms[i].id,roomNumber:rooms[i].roomNumber,roomTypeCode:type,roomTypeName:names[i],roomTypeSnapshot:{code:type,name:names[i]},cleaningKind:['checkout','stayover','additional','reclean'][i],maidProfileId:'qa-maid',maidDisplayName:'QA 메이드',serviceDate:date,revision:1,isCurrent:true,notifiedAt:date+'T01:00:00Z',availableFrom:date+'T02:00:00Z'}));
assignments.push({...assignments[0],assignmentId:'snapshot',roomNumber:'553',roomTypeCode:'standard',roomTypeSnapshot:{code:'oceanFamily',name:'패밀리 투룸'},cleaningKind:'stayover'}, {...assignments[0],assignmentId:'unknown',roomNumber:'999',roomTypeCode:null,roomTypeSnapshot:null,cleaningKind:null});
const attempt=a=>({attemptId:'attempt-'+a.assignmentId,assignmentId:a.assignmentId,assignmentRevision:1,executionVersion:1,status:'scheduled'});
const source=await readFile('WIREFRAME/index.html','utf8'),boot='      void bootApplication();\n    })();';assert.equal(source.split(boot).length,2);
const hook=`window.__contextQA={setup:(role,rooms)=>{
 LIVE_RUNTIME.authGeneration++;LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true}});
 state.remote=initialRemoteState();state.role=role;state.liveView=role==='maid'?'my':'cleaning';state.cleaningTab='assignment-today';state.detail=null;liveRoomDetail=null;
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{id:'qa-maid',profileId:'qa-maid',role,displayName:'QA 메이드',status:'active'},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});state.remote.rooms.items=rooms;
 Object.assign(cleaningState(),{status:'ready',serviceDate:'${date}',maidAssignmentsInitialized:true,commitImpactStatus:'ready',commitImpact:{committableDrafts:[],blockedDrafts:[]},planningAvailability:{status:'ready',items:[],candidates:[]}});syncAuthState(state);rawCloseModal();render();
 },load:()=>loadLiveMaidCleaning(),draft:()=>({room:document.getElementById('cleaning-add-room')?.value}),render:()=>render()};\n`;
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block',reducedMotion:'reduce'}),page=await context.newPage(),errors=[],requests=[];
page.setDefaultTimeout(10000);page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['warning','error'].includes(m.type())&&m.text()!=='Service Worker registration blocked by Playwright')errors.push(m.text());});
await page.route('**/*',async route=>{const req=route.request(),url=new URL(req.url());
 if(url.origin===origin){if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook+boot)});return route.continue();}
 requests.push(req.method()+' '+url.pathname);assert.equal(url.origin,new URL(api).origin);url.pathname=url.pathname.replace('/functions/v1/api','');assert.equal(req.method(),'GET','no writes during UI QA');
 if(url.pathname==='/v1/assignments')return route.fulfill({json:{assignments}});
 if(url.pathname==='/v1/assignment-change-requests')return route.fulfill({json:{requests:[],nextCursor:null}});
 if(url.pathname==='/v1/attempts/current')return route.fulfill({json:{attempt:attempt(assignments.find(a=>a.assignmentId===url.searchParams.get('assignmentId')))}});
 const a=assignments.find(a=>url.pathname.includes('attempt-'+a.assignmentId+'/'));
 if(a&&url.pathname.endsWith('/photo-slots'))return route.fulfill({json:{attemptId:attempt(a).attemptId,assignmentId:a.assignmentId,assignmentRevision:1,slots:[]}});
 if(a&&url.pathname.endsWith('/submissions'))return route.fulfill({json:{submissions:[]}});
 throw new Error('unexpected request '+url.pathname);
});
const setup=role=>page.evaluate(({role,rooms})=>__contextQA.setup(role,rooms),{role,rooms});
const action=name=>page.locator(`[data-action="${name}"]:visible`).first();
const shot=async name=>page.screenshot({path:`WIREFRAME/QA/screenshots/cleaning-context-${name}.png`});
async function layout(width){await page.setViewportSize({width,height:900});await page.waitForTimeout(240);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);assert(await page.locator('#main-content').innerText());}
try{
 await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await page.goto(origin+'/index.html');await setup('maid');await page.evaluate(()=>__contextQA.load());
 assert.equal(await page.title(),'내 업무 · CASTLE THE ART');assert.equal(await page.locator('[data-maid-room-task]').count(),6);
 for(const [i,kind] of ['퇴실 청소','연박 청소','추가 청소','재청소'].entries())assert.match(await page.locator(`[data-maid-room-task="assignment-${i}"]`).innerText(),new RegExp(`${kind} · 베딩 수 ${i===3?2:1}개`));
 assert.match(await page.locator('[data-maid-room-task=snapshot]').innerText(),/베딩 수 2개/);assert.match(await page.locator('[data-maid-room-task=unknown]').innerText(),/종류 API 미제공 · 베딩 수 유형 확인 필요/);
 for(const width of [360,390,768,1440]){await layout(width);if([390,1440].includes(width))await shot('maid-'+width);}
 await page.setViewportSize({width:390,height:900});const toggle=page.locator('[data-maid-room-task="assignment-1"] button').first();await toggle.click();await page.locator('[data-cleaning-assignment="assignment-1"]').waitFor();const detail=page.locator('[data-cleaning-assignment="assignment-1"]');assert.match(await detail.innerText(),/청소 유형\s*연박 청소/);assert.match(await detail.innerText(),/베딩 수\s*1개/);await shot('maid-detail-390');await toggle.click();assert.equal(await toggle.getAttribute('aria-expanded'),'false');
 console.log('[ok] 실제 AssignmentCard 조회 → 네 청소 종류·베딩 1/2개 · 스냅샷 우선 · 누락값 · 펼침/접힘 · 4개 폭');
 await setup('admin');await action('cleaning-add-review').click();const dialog=page.getByRole('dialog'),search=page.getByRole('searchbox',{name:'객실번호·유형 검색'});
 assert.deepEqual(await dialog.locator('h4').allTextContents(),names);
 for(const group of await dialog.locator('[data-room-picker-group]').all()){const nums=await group.locator('[data-room-picker-choice]').evaluateAll(es=>es.map(e=>Number(e.dataset.label.split('호')[0])));assert.deepEqual(nums,[...nums].sort((a,b)=>a-b));assert(await group.locator('h4').evaluate(e=>Number(getComputedStyle(e).fontWeight)>=700));}
 for(const width of [360,390,768,1440]){await layout(width);assert(await dialog.locator('.cleaning-room-choice').evaluateAll(es=>es.every(e=>e.getBoundingClientRect().height>=44)));assert(await dialog.locator('.modal-foot button').evaluateAll(es=>es.every(e=>e.getBoundingClientRect().bottom<=innerHeight)));if([390,1440].includes(width))await shot('picker-'+width);}
 await search.fill('파셜오션뷰 프리미어');assert.equal(await dialog.locator('[data-room-picker-group]:visible').count(),1);assert(await dialog.getByRole('heading',{name:names[2]}).isVisible());
 await search.fill('99999');assert(await dialog.getByText('검색 결과가 없습니다. 객실번호나 유형을 다시 입력하세요.').isVisible());assert(await action('cleaning-add-room').isDisabled());assert.equal(await page.locator('#cleaning-add-room').inputValue(),'');
 await search.fill('패밀리');assert.equal(await dialog.locator('[data-room-picker-group]:visible').count(),1);const radios=dialog.getByRole('radio');await radios.first().focus();await page.keyboard.press('Space');await page.keyboard.press('ArrowRight');assert.equal(await radios.nth(1).isChecked(),true);assert.equal(await action('cleaning-add-room').isEnabled(),true);
 await page.setViewportSize({width:390,height:900});await search.fill('629');await dialog.getByRole('radio',{name:'패밀리 투룸 629호'}).check();assert.equal(await page.locator('#cleaning-add-room').inputValue(),'room-629');await shot('picker-search-390');
 await action('cleaning-add-room').click();await page.getByRole('heading',{name:'629호 청소 요청',exact:true}).waitFor();assert.equal(await page.locator('#live-cleaning-kind').inputValue(),'additional');await page.keyboard.press('Escape');await dialog.waitFor({state:'hidden'});
 await action('cleaning-add-review').click();await action('cleaning-add-room').focus();await page.keyboard.press('Tab');assert(await page.evaluate(()=>!!document.activeElement.closest('[role=dialog]')));await page.keyboard.press('Escape');await dialog.waitFor({state:'hidden'});assert.equal(await page.evaluate(()=>document.activeElement?.dataset.action),'cleaning-add-review');
 await action('cleaning-add-review').click();await page.goBack();await dialog.waitFor({state:'hidden'});
 await page.evaluate(()=>__contextQA.setup('admin',[]));await action('cleaning-add-review').click();assert(await action('cleaning-add-room').isDisabled());assert(await dialog.getByText('선택할 수 있는 객실이 없습니다.').isVisible());await page.keyboard.press('Escape');
 console.log('[ok] 유형 제목·호수 오름차순 · 유형/호수/공백 검색 · 빈 결과 · 라디오 키보드 · 원래 객실 요청 연결 · 포커스/ESC/Back');
 assert.deepEqual(errors,[]);assert(requests.every(r=>r.startsWith('GET ')));console.log('[ok] 페이지 식별·내용·콘솔 warning/error·넘침·오류 overlay 이상 없음 · 운영 쓰기 0');
}finally{await browser.close();}
