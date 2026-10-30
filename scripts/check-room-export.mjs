#!/usr/bin/env node
// Browser plugin not available. Synthetic API only; no operational credentials or room data.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4177',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const date='2026-10-31',now=date+'T10:00:00+09:00',output=process.env.RMS_QA_OUTPUT||'/tmp/rms-room-export-qa',before=process.env.RMS_QA_BASE_REF;
const source=before?execFileSync('git',['show',before+':WIREFRAME/index.html'],{encoding:'utf8',maxBuffer:8*1024*1024}):await readFile('WIREFRAME/index.html','utf8');
const boot='      void bootApplication();';assert.equal(source.split(boot).length,2);
const base={serviceDate:date,projectionMode:'LIVE',evaluatedAt:now,serverTime:now,reservationPhase:'current',occupied:true,roomTypeCode:'standard',roomTypeName:'스탠다드',elevatorZone:'A',dataStatus:'verified',stateVersion:1,cleaningRequired:false,candleCount:0,pinSyncStatus:'unconfigured',primaryDisplayStatus:'OCCUPIED',allocationBlocked:false,readinessReasonCodes:[],nextReservationId:null,nextCheckInAt:null,allocationReady:false,displayGuestCount:3,displayBaseOccupancy:2,displayCheckInAt:'2026-10-30T16:00:00+09:00',displayCheckOutAt:'2026-11-02T11:00:00+09:00',detailConditionCodes:['EXTRA_GUESTS'],guestName:'DO_NOT_EXPORT_CUSTOMER',pin:'DO_NOT_EXPORT_PIN'};
const fixtures=[{roomNumber:'001'},{roomNumber:'350',roomTypeCode:'premium',roomTypeName:'프리미어',primaryDisplayStatus:'BLOCKED',allocationBlocked:true,readinessReasonCodes:['OPERATION_BLOCKED'],detailConditionCodes:['LATE_CHECK_OUT']},{roomNumber:'629',roomTypeCode:'oceanFamily',roomTypeName:'패밀리 투룸',displayBaseOccupancy:4,displayGuestCount:6,elevatorZone:'=1+1'}].map((r,i)=>({...base,id:'room-'+r.roomNumber,displayReservationId:'reservation-'+i,...r}));
const hook=`window.__exportQA={setup:(rooms,date='${date}')=>{
 LIVE_RUNTIME.authGeneration++;rawCloseModal();LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',featureFlags:{optionalCleaningWorkflow:true,roomPinExport:true}});
 state.remote=initialRemoteState();state.role='admin';state.liveView='rooms';state.detail=null;liveRoomDetail=null;state.remote.operationalDate=date;state.selectedDate=date;
 state.remote.auth={...state.remote.auth,status:'authenticated',user:{id:'qa-admin',profileId:'qa-admin',role:'admin',displayName:'데모 QA 관리자',status:'active',mustChangePassword:false},session:{accessToken:'qa-only',expiresAt:Date.now()+3600000}};
 for(const key of ['rooms','accounts','roomTypes','reservations','notifications','availability','complaints','payroll','cleaningHistory'])Object.assign(state.remote[key],{status:'ready',lastSuccessAt:new Date().toISOString()});
 state.remote.rooms.items=rooms;state.remote.roomProjection={date,status:'ready',items:rooms,lastSuccessAt:new Date().toISOString()};cleaningState().status='ready';syncAuthState(state);render();
 },age:(rooms,projection)=>{state.remote.rooms.lastSuccessAt=new Date(Date.now()-rooms).toISOString();state.remote.roomProjection.lastSuccessAt=new Date(Date.now()-projection).toISOString();},
 filters:(query='',type='all',filter='all')=>{Object.assign(state.remote.rooms,{query,typeFilter:type,filter});render();},
 date:date=>{state.remote.operationalDate=date;state.selectedDate=date;render();},
 end:kind=>{if(kind==='logout'){LIVE_RUNTIME.authGeneration++;clearLiveAuthSurface();state.remote.auth.status='anonymous';state.remote.auth.user=null;}else state.remote.auth.user.role=kind;syncAuthState(state);render();},
 duplicate:()=>Promise.all([downloadLiveRoomExport('csv'),downloadLiveRoomExport('xlsx')]),
 download:downloadLiveRoomExport,
 snapshot:()=>({date:state.remote.roomProjection.date,status:state.remote.roomProjection.status,rooms:state.remote.roomProjection.items.map(r=>r.roomNumber),query:state.remote.rooms.query,type:state.remote.rooms.typeFilter,filter:state.remote.rooms.filter}),
 swapCache:()=>{state.remote.rooms.items=[{...state.remote.rooms.items[0],roomNumber:'999'}];}
 };`;
const browser=await chromium.launch({headless:true}),context=await browser.newContext({viewport:{width:390,height:900},timezoneId:'America/New_York',serviceWorkers:'block',reducedMotion:'reduce',acceptDownloads:true}),page=await context.newPage();
const errors=[],unexpected=[],calls=[],downloads=[];let roomDelay=0,pinDelay=0,roomMode='ok',pinMode='ok',serverRooms=fixtures;
page.setDefaultTimeout(7000);await page.clock.setFixedTime(new Date(now));
page.on('pageerror',e=>errors.push(e.message));page.on('download',d=>downloads.push(d));page.on('console',m=>{if(['warning','error'].includes(m.type())&&!/Service Worker registration blocked|Failed to load resource.*(?:503|403)/.test(m.text()))errors.push(m.text());});
await page.route('**/*',async route=>{
 const req=route.request(),url=new URL(req.url());
 if(url.origin===origin){if(url.pathname.endsWith('/index.html'))return route.fulfill({contentType:'text/html',body:source.replace(boot,hook)});if(url.pathname==='/runtime-config.json')return route.fulfill({json:{mode:'demo'}});return route.continue();}
 const path=url.pathname.replace('/functions/v1/api','');calls.push({path,date:url.searchParams.get('serviceDate'),method:req.method()});
 const wait=ms=>new Promise(r=>setTimeout(r,ms));
 if(req.method()==='GET'&&path==='/v1/room-pin-sheet-sync/status'){
  const mode=pinMode;await wait(pinDelay);return mode==='error'?route.fulfill({status:503,json:{error:{code:'STORAGE_PROVIDER_UNAVAILABLE'}}}):route.fulfill({json:{sync:{version:1,pending:0,failed:0,operatorBlocked:mode==='blocked',lastSuccessAt:now}}});
 }
 if(req.method()==='GET'&&path==='/v1/rooms'){
  const mode=roomMode,day=url.searchParams.get('serviceDate'),rooms=structuredClone(serverRooms);await wait(roomDelay);
  if(mode==='error')return route.fulfill({status:503,json:{error:{code:'UPSTREAM_UNAVAILABLE',message:'DO_NOT_DISPLAY_PROVIDER_SECRET'}}});
  if(mode==='denied')return route.fulfill({status:403,json:{error:{code:'ADMIN_REQUIRED'}}});
  return route.fulfill({json:{rooms:mode==='empty'?[]:rooms.map(r=>({...r,serviceDate:mode==='wrong-date'?'2000-01-01':day,projectionMode:day<date?'HISTORICAL':day>date?'PLANNED':'LIVE'}))}});
 }
 if(req.method()==='GET'&&path==='/v1/assignments/commit-impact')return route.fulfill({json:{impact:{serviceDate:url.searchParams.get('serviceDate'),committableDrafts:[],blockedDrafts:[],remainingUnassignedTargets:[]}}});
 if(req.method()==='GET'&&['/v1/assignments','/v1/assignment-change-requests','/v1/inspections'].includes(path))return route.fulfill({json:{assignments:[],requests:[],submissions:[],nextCursor:null}});
 // Existing room card destinations remain read-only in this fixture.
 if(req.method()==='GET'&&path==='/v1/reservations')return route.fulfill({json:{reservations:[],nextCursor:null}});
 const match=path.match(/^\/v1\/rooms\/(room-[\d]+)(?:\/(events|operation-blocks|issues|reports|candle-events|pin-sync))?$/);
 if(req.method()==='GET'&&match){const room=fixtures.find(r=>r.id===match[1]);return route.fulfill({json:!match[2]?{room}:match[2]==='pin-sync'?{pinSync:{status:'unconfigured',version:1}}:match[2]==='candle-events'?{events:[]}:{roomId:room.id,roomStateVersion:1,items:[],nextCursor:null}});}
 unexpected.push(req.method()+' '+path);return route.abort();
});
const action=name=>page.locator(`[data-action="${name}"]:visible`).first();
const setup=async(day=date)=>{roomMode='ok';pinMode='ok';roomDelay=0;pinDelay=0;serverRooms=fixtures;await page.evaluate(([rooms,day])=>__exportQA.setup(rooms,day),[fixtures,day]);};
const open=async()=>{await action('live-room-export').click();await page.getByRole('dialog').waitFor();};
const status=()=>page.locator('[data-room-export-status]');
const screenshot=async name=>{await page.screenshot({path:`WIREFRAME/QA/screenshots/room-export-${name}.png`});};
const roomCalls=()=>calls.filter(c=>c.path==='/v1/rooms');
async function download(format,{filtered=false,alreadyOpen=false}={}){
 if(!alreadyOpen)await open();if(filtered)await page.locator('#export-filtered').check();
 const wait=page.waitForEvent('download');await action('live-export-'+format).click();const file=await wait;
 const path=`${output}/${downloads.length}.${format}`;await file.saveAs(path);await page.getByRole('dialog').waitFor({state:'hidden'});await page.waitForTimeout(60);
 return {file,path};
}
const inspect=path=>JSON.parse(execFileSync('python3',['-c',String.raw`import csv,json,sys,zipfile,xml.etree.ElementTree as E
p=sys.argv[1]
if p.endswith('.csv'):
 with open(p,encoding='utf-8-sig',newline='') as f: print(json.dumps({'rows':list(csv.reader(f))},ensure_ascii=False))
else:
 with zipfile.ZipFile(p) as z:
  for name in z.namelist():
   if name.endswith('.xml') or name.endswith('.rels'):E.fromstring(z.read(name))
  root=E.fromstring(z.read('xl/worksheets/sheet1.xml'));n={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  rows=[[(''.join(c.itertext()) if c.attrib.get('t')=='inlineStr' else c.findtext('s:v',default='',namespaces=n)) for c in row] for row in root.findall('s:sheetData/s:row',n)]
  print(json.dumps({'rows':rows,'formulas':len(root.findall('.//s:f',n)),'roomTypes':[row[1].get('t') for row in root.findall('s:sheetData/s:row',n)],'pane':root.find('s:sheetViews/s:sheetView/s:pane',n).attrib,'filter':root.find('s:autoFilter',n).get('ref')},ensure_ascii=False))
`,path],{encoding:'utf8'}));
try{
 await mkdir(output,{recursive:true});await mkdir('WIREFRAME/QA/screenshots',{recursive:true});await page.goto(origin+'/index.html');await setup();
 console.log('Browser plugin not available; Playwright Chromium '+browser.version());
 for(const width of [390,1440]){await page.setViewportSize({width,height:900});await open();await page.getByText('대기 0건 · 실패 0건',{exact:false}).waitFor();await screenshot((before?'before':'after')+'-'+width);await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});}
 if(before){
  await page.evaluate(()=>__exportQA.age(31000,31000));await open();const count=downloads.length,reads=roomCalls().length;await action('live-export-csv').click();await page.waitForTimeout(200);assert.equal(downloads.length,count);assert.equal(roomCalls().length,reads);assert.match(await page.locator('#toast-region').innerText(),/최신 객실 현황/);console.log('[reproduced] 31초 뒤 CSV 거부·객실 GET 0회');
 }else{
  for(const day of [date,'2026-10-29','2026-11-02']){
   await setup(day);await page.evaluate(()=>__exportQA.age(31000,31000));
   const csv=inspect((await download('csv')).path),xlsxResult=await download('xlsx'),xlsx=inspect(xlsxResult.path);assert.deepEqual(csv.rows,xlsx.rows.map(row=>row.map(value=>/^[=+@-]/.test(value)?"'"+value:value)));assert.equal(csv.rows.length,4);assert(csv.rows.slice(1).every(r=>r[0]===day));assert.equal(csv.rows[1][1],'001');assert.equal(xlsx.roomTypes[1],'inlineStr');assert.equal(xlsx.formulas,0);assert.equal(xlsx.pane.state,'frozen');assert(xlsx.filter.startsWith('A1:'));assert.equal(csv.rows[3][3],"'=1+1");assert(!JSON.stringify(csv.rows).includes('DO_NOT_EXPORT'));assert(xlsxResult.file.suggestedFilename().includes(day));assert.deepEqual((await page.evaluate(()=>__exportQA.snapshot())).rooms,['001','350','629']);assert.equal(roomCalls().at(-1).date,day);
  }
  console.log('[ok] 31초 경과 · 오늘/과거/미래 GET · 실제 CSV/XLSX 전체 셀 일치 · 선행0/수식 방어/개인정보 제외');
  for(const [r,p]of [[31000,0],[0,600000]]){await setup();await page.evaluate(([r,p])=>{__exportQA.age(r,p);__exportQA.swapCache();},[r,p]);serverRooms=fixtures.map(r=>({...r,candleCount:9}));const reads=roomCalls().length;const data=inspect((await download('csv')).path);assert.equal(data.rows[1][1],'001');assert.equal(data.rows[1][6],'9');assert.equal(roomCalls().length,reads+1);}
  await setup();await page.evaluate(()=>__exportQA.filters('00','standard','extra-guests'));let data=inspect((await download('csv',{filtered:true})).path);assert.equal(data.rows.length,2);assert.equal(data.rows[1][1],'001');assert.deepEqual(await page.evaluate(()=>__exportQA.snapshot()),{date,status:'ready',rooms:['001','350','629'],query:'00',type:'standard',filter:'extra-guests'});
  data=inspect((await download('xlsx')).path);assert.equal(data.rows.length,4);
  for(const [filter,expected]of [['blocked',['350']],['late',['350']],['extra-guests',['001','629']]]){await page.evaluate(f=>__exportQA.filters('','all',f),filter);assert.deepEqual(inspect((await download('csv',{filtered:true})).path).rows.slice(1).map(r=>r[1]),expected);}
  console.log('[ok] projection/rooms 캐시 불일치 · 검색/유형/주 상태/상세 조건 · 필터 선택/해제');
  await setup();await page.setViewportSize({width:390,height:900});await open();await page.locator('#export-filtered').check();serverRooms=fixtures.slice(0,1);const reads=roomCalls().length;await action('live-room-export-refresh').click();await page.getByText(date+' · 최신 객실 1개 확인',{exact:true}).waitFor();assert.equal(roomCalls().length,reads+1);assert(await page.locator('#export-filtered').isChecked());assert.equal(await page.locator('[data-live-room]').count(),1);
  for(const mode of ['error','denied','wrong-date','empty']){roomMode=mode;const n=downloads.length;await action('live-export-csv').click();await page.waitForFunction(()=>!document.querySelector('[data-action="live-export-csv"]').disabled);assert.equal(downloads.length,n);const message=await status().innerText();assert(mode==='empty'?message.includes('내보낼 객실이 없습니다'):message.includes('다시 시도'));assert(!message.includes('DO_NOT_DISPLAY'));if(mode==='error')await screenshot('error-390');}
  roomMode='ok';await download('xlsx',{alreadyOpen:true});
  await setup();await page.evaluate(()=>__exportQA.filters('no-match'));await open();await page.locator('#export-filtered').check();await action('live-export-csv').click();await page.getByText('현재 검색·필터 결과에 내보낼 객실이 없습니다. 전체 객실은 선택을 해제해 내려받으세요.',{exact:true}).waitFor();await page.locator('#export-filtered').uncheck();await download('csv',{alreadyOpen:true});
  for(const mode of ['error','blocked']){await setup();pinMode=mode;await download('csv');}
  await setup();pinDelay=700;const start=Date.now();await download('xlsx');assert(Date.now()-start<650,'PIN status must not hold downloads');await page.waitForTimeout(750);
  console.log('[ok] 상태 새로고침 대상/선택 유지 · 실패/403/잘못된 날짜/0건 구분·재시도 · PIN 실패/차단/지연 독립');
  await setup();roomDelay=250;await open();const n=downloads.length,readsBefore=roomCalls().length;await page.evaluate(()=>__exportQA.duplicate());await page.waitForTimeout(150);assert.equal(downloads.length,n+1);assert.equal(roomCalls().length,readsBefore+1);
  for(const change of ['close','back','date','filter','filter-return','logout','maid','developer','replace']){
   await setup();roomDelay=250;await open();const n=downloads.length,readCount=roomCalls().length;await action('live-export-csv').click();await page.waitForFunction(()=>document.querySelector('[data-action="live-export-csv"]').disabled);assert.equal(await page.locator('#export-filtered').isDisabled(),true);
   if(change==='close')await page.keyboard.press('Escape');else if(change==='back')await page.goBack();else if(change==='date')await page.evaluate(()=>__exportQA.date('2026-11-01'));else if(change.startsWith('filter'))await page.evaluate(c=>{__exportQA.filters('changed');if(c==='filter-return')__exportQA.filters();},change);else if(change==='replace'){await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await open();}else await page.evaluate(c=>__exportQA.end(c),change);
   await page.waitForTimeout(400);assert.equal(downloads.length,n,'no download after '+change);assert.equal(roomCalls().length,readCount+1);
  }
  await setup();await page.evaluate(()=>__exportQA.end('maid'));const readCount=roomCalls().length;await page.evaluate(()=>__exportQA.download('csv'));assert.equal(roomCalls().length,readCount);
  console.log('[ok] 중복 요청 1회 · 닫기/Back/재진입/날짜/필터·복귀/로그아웃/역할 전환 지연 응답 차단');
  await setup();
  for(const width of [360,390,768,1440]){
   await page.setViewportSize({width,height:900});await action('live-room-export').focus();await page.keyboard.press('Enter');await page.getByRole('dialog').waitFor();await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(e=>e.contains(document.activeElement)));assert.equal(await page.title(),'객실 현황 · CASTLE THE ART');assert(await page.locator('#main-content').innerText());assert.equal(await page.locator('vite-error-overlay,nextjs-portal').count(),0);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);assert(await page.getByRole('dialog').locator('button').evaluateAll(es=>es.every(e=>{const r=e.getBoundingClientRect();return r.width>=44&&r.height>=44&&r.left>=0&&r.right<=innerWidth&&(e.getAttribute('aria-label')||e.textContent.trim());})));
   await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});await page.waitForFunction(()=>document.activeElement?.dataset.action==='live-room-export');
  }
  await setup();await action('open-live-room-reservation-status').click();await page.getByRole('dialog').waitFor();await page.getByRole('heading',{name:/예약 현황/}).waitFor();await page.keyboard.press('Escape');await page.getByRole('dialog').waitFor({state:'hidden'});
  await action('open-live-room-detail').click();await page.getByRole('heading',{name:/001/}).first().waitFor();await page.goBack();await page.locator('[data-live-room]').first().waitFor();
  assert.deepEqual(unexpected,[]);assert.deepEqual(errors,[]);console.log('[ok] 4개 폭 · 페이지/내용/overlay/44px/접근성 이름/가로 넘침 · 키보드/포커스/Back/카드 목적지 · 앱 콘솔/예외0');
 }
}finally{await browser.close();}
