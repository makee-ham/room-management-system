#!/usr/bin/env node
// Synthetic API only: no production accounts, tasks or notifications are changed.
import assert from 'node:assert/strict';
import {readFile,mkdir} from 'node:fs/promises';
import {createRequire} from 'node:module';
import {resolve} from 'node:path';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4187',api='https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api';
const source=await readFile(process.env.RMS_QA_HTML||resolve('WIREFRAME/index.html'),'utf8');
const date=new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Seoul',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const uuid=n=>`10000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
const admin=uuid(3),maid=uuid(1),otherMaid=uuid(2),targets=[uuid(10),uuid(11),uuid(12)],accounts=[{profileId:maid,displayName:'메이드 A · 데모',role:'maid',status:'active'},{profileId:otherMaid,displayName:'메이드 B · 데모',role:'maid',status:'active'}];
const room=(n,index)=>({id:uuid(30+index),roomNumber:n,roomTypeCode:'premium',roomTypeName:'프리미어 더블 로프트',elevatorZone:'A',dataStatus:'verified',stateVersion:1,occupied:false,cleaningRequired:true,candleCount:0,pinSyncStatus:'verified',allocationBlocked:false,allocationReady:false,reasonCodes:['CLEANING_REQUIRED']});
const rooms=['117','135','142'].map(room);
const target=index=>({cleaningTargetId:targets[index],roomId:rooms[index].id,roomNumber:rooms[index].roomNumber,roomTypeCode:'premium',roomTypeName:'프리미어 더블 로프트',elevatorZone:'A',feeSnapshot:20000,cleaningKind:'checkout',sourceKind:'scheduled_checkout',serviceDate:date,effectiveServiceDate:date,availableFrom:`${date}T11:00:00+09:00`,dueAt:null,targetAssignmentVersion:1,rolloverCount:0,instructionMemo:null});
let omitMemo=false,sequence=100,role='admin',assignments=[],unassigned=[],requests=[],receipts=new Map(),force=null,lose=false;
function reset(){assignments=[{...target(0),assignmentId:uuid(sequence++),maidProfileId:maid,maidDisplayName:accounts[0].displayName,revision:1,sequenceNumber:1,isCurrent:true,targetStatus:'notified',attemptStatus:'scheduled',notifiedAt:`${date}T09:00:00+09:00`,instructionMemo:'기존 요청 · 데모'}];unassigned=[target(1),target(2)];requests=[];receipts.clear();force=null;lose=false;}
function attempt(a){return {attemptId:uuid(60+targets.indexOf(a.cleaningTargetId)),assignmentId:a.assignmentId,assignmentRevision:a.revision,cleaningTargetId:a.cleaningTargetId,maidProfileId:a.maidProfileId,executionVersion:1,status:a.attemptStatus||'scheduled',instructionMemo:a.instructionMemo};}
const injected=`window.__memoQA={setup:async (role,enabled=true)=>{LIVE_RUNTIME.mode='live';LIVE_RUNTIME.status='ready';LIVE_RUNTIME.config=normalizeRuntimeConfig({apiBaseUrl:'${api}',supabaseUrl:'https://aodikrxcczbogjpsjwjt.supabase.co',supabasePublishableKey:'sb_publishable_abcdefghijklmnopqrstuvwxyz1234',sessionPersistence:'session',featureFlags:{assignmentInstructionMemo:enabled,assignmentPlanningDate:true,optionalCleaningWorkflow:true}});state.remote=initialRemoteState();state.remote.auth={...state.remote.auth,status:'authenticated',user:{profileId:role==='admin'?'${admin}':'${maid}',displayName:'QA 계정 · 데모',role,mustChangePassword:false},session:{accessToken:'qa-memo-token',refreshToken:'qa-refresh',expiresAt:Date.now()+3600000}};state.remote.accounts={...state.remote.accounts,status:'ready',items:${JSON.stringify(accounts)},lastSuccessAt:new Date().toISOString()};state.remote.rooms={...state.remote.rooms,status:'ready',items:${JSON.stringify(rooms)}};state.role=role;state.liveView=role==='admin'?'cleaning':'my';state.cleaningTab='assignment-today';syncAuthState(state);await loadLiveCleaning();render();},refresh:async()=>{await loadLiveCleaning();render();},save:typeof saveLiveInstruction==='function'?saveLiveInstruction:null,rebase:typeof rebaseLiveInstruction==='function'?rebaseLiveInstruction:null,edit:typeof captureLiveInstruction==='function'?captureLiveInstruction:null,identity:liveAssignmentDraftIdentity,patch:typeof liveInstructionPatch==='function'?liveInstructionPatch:null,rows:liveAssignmentRows,resetDate:resetLiveCleaningDate,get:()=>({busy:cleaningState().busy,status:cleaningState().status,edits:(cleaningState().instructionEdits?.size||0),error:cleaningState().error?.code,uncertain:!!uncertainLiveMutation}),rerender:()=>render()};`;
const html=source.replace('\n      void bootApplication();',injected);
const browser=await chromium.launch({headless:true,...(process.env.RMS_QA_BROWSER_CHANNEL?{channel:process.env.RMS_QA_BROWSER_CHANNEL}:{})});
const context=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),page=await context.newPage();page.setDefaultTimeout(10000);
const errors=[],consoleProblems=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(['error','warning'].includes(m.type())&&!m.text().startsWith('Failed to load resource:')&&!m.text().includes('net::ERR_FAILED'))consoleProblems.push(m.text());});
const json=(route,data,status=200,headers={})=>route.fulfill({status,contentType:'application/json',headers:{'cache-control':'no-store',...headers},body:JSON.stringify(data)});
await page.route('**/favicon.ico',r=>r.fulfill({status:204}));
await page.route('**/index.html*',r=>r.fulfill({contentType:'text/html',body:html}));
await page.route(api+'/**',async r=>{
 const req=r.request(),url=new URL(req.url()),path=url.pathname.replace('/functions/v1/api',''),method=req.method(),body=req.postDataJSON(),key=req.headers()['idempotency-key'];
 requests.push({path,method,body,key});
 if(method==='POST'){
  assert(key,'mutation needs idempotency key');
  if(receipts.has(key)){const saved=receipts.get(key);assert.equal(saved.path,path);assert.deepEqual(saved.body,body);return json(r,saved.data,200,{'idempotency-replayed':'true'});}
  if(force){const failure=force;force=null;if(failure===409){const current=assignments.find(a=>a.isCurrent);current.instructionMemo='다른 관리자 최신 메모';current.targetAssignmentVersion++;}return json(r,{error:{code:typeof failure==='string'?failure:failure===409?'ASSIGNMENT_VERSION_CONFLICT':'ASSIGNMENT_INSTRUCTION_INVALID',message:'SAFE ERROR'}},typeof failure==='string'?409:failure);}
  let data;
  if(path==='/v1/assignments/drafts'||path.endsWith('/change')){
   const id=body.cleaningTargetId||path.split('/')[3],old=assignments.find(a=>a.isCurrent&&a.cleaningTargetId===id),base=old||unassigned.find(a=>a.cleaningTargetId===id);
   assert(base);assert.equal(body.expectedAssignmentVersion,base.targetAssignmentVersion);if(old&&path.endsWith('/change'))assert.equal(body.expectedCurrentAssignmentId,old.assignmentId);
   const next={...base,assignmentId:uuid(sequence++),maidProfileId:body.maidProfileId,maidDisplayName:accounts.find(a=>a.profileId===body.maidProfileId).displayName,sequenceNumber:body.sequenceNumber,revision:(old?.revision||0)+1,targetAssignmentVersion:base.targetAssignmentVersion+1,isCurrent:true,targetStatus:old?.notifiedAt?'notified':'draft_assigned',attemptStatus:old?.attemptStatus??null,notifiedAt:old?.notifiedAt||null,instructionMemo:Object.hasOwn(body,'instructionMemo')?body.instructionMemo:base.instructionMemo??null};
   if(old)old.isCurrent=false;assignments.push(next);unassigned=unassigned.filter(t=>t.cleaningTargetId!==id);data=path.endsWith('/drafts')?{assignment:next}:next;
  }else if(path==='/v1/assignments/commit'){for(const item of body.items){const a=assignments.find(a=>a.isCurrent&&a.cleaningTargetId===item.cleaningTargetId);assert.equal(a.targetAssignmentVersion,item.expectedAssignmentVersion);a.notifiedAt=`${date}T09:00:00+09:00`;a.targetStatus='notified';}data={assignments:assignments.filter(a=>a.isCurrent)};}
  else throw new Error('Unexpected mutation '+path);
  receipts.set(key,{path,body,data:structuredClone(data)});if(lose){lose=false;return r.abort('failed');}if(omitMemo){omitMemo=false;data=structuredClone(data);delete (data.assignment||data).instructionMemo;}return json(r,data);
 }
 if(path==='/v1/assignments')return json(r,{assignments:role==='maid'?assignments.filter(a=>a.isCurrent&&a.notifiedAt&&a.maidProfileId===maid):assignments.map(a=>({...a,planningDate:url.searchParams.get('serviceDate')}))});
 if(path==='/v1/assignments/commit-impact')return json(r,{impact:{serviceDate:date,impactFingerprint:'a'.repeat(64),committableDrafts:assignments.filter(a=>a.isCurrent&&!a.notifiedAt).map(a=>({...a,expectedAvailabilityVersion:1})),blockedDrafts:[],remainingUnassignedTargets:unassigned}});
 if(path.endsWith('/history'))return json(r,{assignments:assignments.filter(a=>a.cleaningTargetId===path.split('/')[3])});
 if(path==='/v1/accounts')return json(r,{accounts});
 if(path==='/v1/availability/candidates')return json(r,{candidates:accounts.map(a=>({maidProfileId:a.profileId,displayName:a.displayName,workDate:url.searchParams.get('workDate'),availabilityVersion:1}))});
 if(path==='/v1/availability')return json(r,{availability:accounts.map(a=>({maidProfileId:a.profileId,weekStart:url.searchParams.get('weekStart'),current:true,status:'submitted',days:[]}))});
 if(path==='/v1/assignment-change-requests')return json(r,{requests:[],nextCursor:null});
 if(path==='/v1/inspections')return json(r,{submissions:[],nextCursor:null});
 if(path==='/v1/notifications')return json(r,{notifications:[],nextCursor:null});
 if(path==='/v1/checkout-incidents')return json(r,{items:[],nextCursor:null});
 if(path==='/v1/attempts/lifecycle-impact'||path==='/v1/attempts/current'){
  const a=assignments.find(a=>a.assignmentId===url.searchParams.get('assignmentId')&&a.isCurrent&&a.notifiedAt),adminRead=path.endsWith('/lifecycle-impact');
  assert.equal(role,adminRead?'admin':'maid','attempt endpoint must match actor role');
  if(!a||(!adminRead&&a.maidProfileId!==maid)||(adminRead&&a.attemptStatus===null))return json(r,{error:{code:'ATTEMPT_ACCESS_REQUIRED',message:'SAFE ERROR'}},403);
  return json(r,{attempt:a.attemptStatus===null?null:attempt(a)});
 }
 if(path.endsWith('/photo-slots')){const a=assignments.find(a=>a.isCurrent&&attempt(a).attemptId===path.split('/')[3]);return json(r,{attemptId:attempt(a).attemptId,assignmentId:a.assignmentId,assignmentRevision:a.revision,slots:[]});}
 if(path.endsWith('/submissions'))return json(r,{submissions:[]});
 if(path==='/v1/rooms/candles')return json(r,{items:[],nextCursor:null});
 if(path.endsWith('/reports'))return json(r,{items:[],nextCursor:null});
 if(path==='/v1/rooms')return json(r,{rooms});
 if(path==='/v1/reservations')return json(r,{reservations:[]});
 if(path==='/v1/room-types')return json(r,{items:[]});
 if(path==='/v1/cleaning-history')return json(r,{items:[],nextCursor:null});
 if(path==='/v1/availability/me')return json(r,{availability:null});
 throw new Error('Unexpected read '+path);
});
const row=i=>page.locator(`[data-assignment-target="${targets[i]}"]`),field=i=>row(i).getByRole('textbox'),save=i=>row(i).locator('[data-action="cleaning-instruction-save"]');
async function setup(nextRole='admin',enabled=true){role=nextRole;await page.goto(origin+'/index.html');await page.evaluate(([role,enabled])=>__memoQA.setup(role,enabled),[role,enabled]);await page.waitForFunction(()=>__memoQA.get().status==='ready');}
async function settled(){await page.waitForFunction(()=>!__memoQA.get().busy);}
const evidence=resolve(process.env.RMS_QA_EVIDENCE||'WIREFRAME/QA/screenshots');await mkdir(evidence,{recursive:true});
async function positionRow(){await row(0).evaluate(el=>window.scrollTo(0,el.getBoundingClientRect().top+scrollY-220));await page.evaluate(()=>new Promise(requestAnimationFrame));}
try{
 if(process.env.RMS_QA_COMPARE){
  reset();await setup();for(const width of [390,1440]){await page.setViewportSize({width,height:1000});await positionRow();await page.screenshot({path:resolve(evidence,`assignment-memo-compare-admin-${process.env.RMS_QA_COMPARE}-${width}.png`)});}
  await setup('maid');for(const width of [390,1440]){await page.setViewportSize({width,height:900});await page.screenshot({path:resolve(evidence,`assignment-memo-compare-maid-${process.env.RMS_QA_COMPARE}-${width}.png`)});}
  assert.deepEqual(errors,[]);console.log('PASS: comparable admin/maid screenshots');await browser.close();process.exit(0);
 }
 reset();await setup('admin',false);assert(await field(0).isDisabled());await page.evaluate(id=>__memoQA.save(id),targets[0]);assert.equal(requests.filter(r=>r.method==='POST').length,0);assert((await page.locator('body').innerText()).includes('API 미제공'));
 await page.setViewportSize({width:390,height:900});await row(0).scrollIntoViewIfNeeded();await page.screenshot({path:resolve(evidence,'assignment-memo-unavailable-390.png')});
 // A notified assignment can have no attempt until the maid starts it. Tomorrow's
 // backlog preserves an older service date; it must still accept an admin memo.
 reset();assignments[0].attemptStatus=null;
 assignments[0].serviceDate='2026-10-08';assignments[0].originalServiceDate='2026-10-08';
 await setup();await page.locator('[data-action="cleaning-tab"][data-tab="assignment-tomorrow"]').click();await settled();
 await field(0).fill('장기 · 데모');const beforeSave=requests.length;await save(0).click();await settled();
 await positionRow();await page.screenshot({path:resolve(evidence,'assignment-memo-no-attempt-'+(process.env.RMS_QA_PHASE||'after')+'-390.png')});
 assert.equal(assignments.find(a=>a.isCurrent).instructionMemo,'장기 · 데모','notified assignment without attempt must save');
 assert.equal(requests.slice(beforeSave).filter(r=>r.path==='/v1/attempts/lifecycle-impact').length,0);
 assert.equal(requests.slice(beforeSave).filter(r=>r.method==='POST').length,1);
 assert((await row(0).innerText()).includes('담당자에게 전달됨'));
 for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
 await positionRow();await page.screenshot({path:resolve(evidence,'assignment-memo-no-attempt-after-1440.png')});
 await setup('maid');assert((await page.locator('body').innerText()).includes('장기 · 데모'));assert.equal(await page.locator('[data-action="cleaning-instruction-save"]').count(),0);
 await setup();await page.locator('[data-action="cleaning-tab"][data-tab="assignment-tomorrow"]').click();await settled();
 // If execution starts after this card was read, the command's server guard wins.
 await field(0).fill('경합 중 입력 유지 · 데모');force='ASSIGNMENT_ALREADY_STARTED';await save(0).click();await settled();
 assert.equal(await page.evaluate(()=>__memoQA.get().error),'ASSIGNMENT_ALREADY_STARTED');
 assert.equal(await field(0).inputValue(),'경합 중 입력 유지 · 데모');assert.equal(assignments.find(a=>a.isCurrent).instructionMemo,'장기 · 데모');
 // A real lifecycle permission denial must never be treated as an absent attempt.
 reset();await setup();assignments[0].attemptStatus=null;await field(0).fill('권한 오류 입력 유지 · 데모');
 const deniedAt=requests.length;await save(0).click();await settled();assert.equal(await page.evaluate(()=>__memoQA.get().error),'ATTEMPT_ACCESS_REQUIRED');
 assert.equal(requests.slice(deniedAt).filter(r=>r.method==='POST').length,0);assert.equal(await field(0).inputValue(),'권한 오류 입력 유지 · 데모');
 reset();await page.setViewportSize({width:390,height:900});
 await setup();assert.match(await page.title(),/CASTLE THE ART/);assert.equal(await field(0).inputValue(),'기존 요청 · 데모');assert(await save(0).isDisabled());
 const memo='쓰레기만 치워주세요\n수건 5. 물 캡슐 2.';
 await field(0).fill(memo);assert.equal(await field(0).evaluate(e=>document.activeElement===e),true);assert.equal(await row(0).locator('[data-memo-count]').innerText(),String(memo.length));await page.locator('[data-action="cleaning-save-notify"]').click();await settled();assert.equal(assignments.find(a=>a.isCurrent).instructionMemo,memo);assert(await save(0).isDisabled());assert((await row(0).innerText()).includes('담당자에게 전달됨'));
 await field(0).fill('');await save(0).click();await settled();assert.equal(requests.filter(r=>r.method==='POST').at(-1).body.instructionMemo,null);
 // Untouched assignment change must omit the optional field, preserving the stored memo.
 await row(0).locator('[data-control="live-assignment-maid"]').selectOption(otherMaid);await page.locator('[data-action="cleaning-save-notify"]').click();await settled();assert(!Object.hasOwn(requests.filter(r=>r.method==='POST').at(-1).body,'instructionMemo'));
 await row(0).locator('[data-control="live-assignment-maid"]').selectOption(maid);await page.locator('[data-action="cleaning-save-notify"]').click();await settled();
 // Independent unsaved memos survive assignee selection and are saved with their own targets.
 await field(1).fill('135호 요청 · 데모');assert(await save(1).isDisabled());await row(1).locator('select').selectOption(maid);await field(2).fill('142호 요청 · 데모');await row(2).locator('select').selectOption(otherMaid);
 await save(1).click();await settled();assert.equal(assignments.find(a=>a.isCurrent&&a.cleaningTargetId===targets[1]).instructionMemo,'135호 요청 · 데모');assert.equal(await field(2).inputValue(),'142호 요청 · 데모');assert((await row(1).innerText()).includes('통보 전'));
 await page.locator('[data-action="cleaning-save-notify"]').click();await settled();assert(assignments.filter(a=>a.isCurrent).every(a=>a.notifiedAt));
 // 400 retains input; 409 keeps draft and requires an explicit review before rebasing.
 await field(0).fill('다시 작성한 메모');force=400;await save(0).click();await settled();assert.equal(await field(0).inputValue(),'다시 작성한 메모');force=409;await save(0).click();await settled();assert.equal(await field(0).inputValue(),'다시 작성한 메모');assert((await save(0).innerText()).includes('최신 메모 확인'));
 const count=requests.filter(r=>r.method==='POST').length;await save(0).click();await page.getByRole('dialog').waitFor();assert.equal(requests.filter(r=>r.method==='POST').length,count);assert((await page.getByRole('dialog').innerText()).includes('다른 관리자 최신 메모'));
 assert.equal(await page.evaluate(()=>JSON.stringify(history.state).includes('다시 작성한 메모')),false);
 for(let i=0;i<8;i++){await page.keyboard.press('Tab');assert(await page.getByRole('dialog').evaluate(e=>e.contains(document.activeElement)));}await page.keyboard.press('Escape');assert.equal(await page.getByRole('dialog').count(),0);
 await save(0).click();await page.locator('[data-action="cleaning-instruction-rebase"]').click();await save(0).click();await settled();assert.equal(assignments.find(a=>a.isCurrent&&a.cleaningTargetId===targets[0]).instructionMemo,'다시 작성한 메모');
 // Ambiguous response retries the same body/key and clears a successful pending draft.
 await field(0).fill('응답 유실 확인');lose=true;await save(0).click();await settled();await page.locator('[data-action="confirm-uncertain-live-mutation"]').waitFor();const lost=requests.filter(r=>r.method==='POST').at(-1);await page.locator('[data-action="confirm-uncertain-live-mutation"]').click();await page.waitForFunction(()=>!__memoQA.get().uncertain);const replay=requests.filter(r=>r.method==='POST').at(-1);assert.equal(replay.key,lost.key);assert.deepEqual(replay.body,lost.body);assert.equal(await page.evaluate(()=>__memoQA.get().edits),0);
 // UTF-16 limits and safe text rendering; injection never becomes markup.
 await field(0).fill('😀'.repeat(250));assert.equal((await field(0).inputValue()).length,500);await save(0).click();await settled();await page.evaluate(id=>__memoQA.edit(id,'가'.repeat(501)),targets[0]);const before=requests.filter(r=>r.method==='POST').length;await page.evaluate(id=>__memoQA.save(id),targets[0]);assert.equal(requests.filter(r=>r.method==='POST').length,before);
 await field(0).fill('<img src=x onerror=alert(1)>\n수건 5 · 데모');await save(0).click();await settled();assert.equal(await page.locator('img[src="x"]').count(),0);await field(0).fill(memo);await save(0).click();await settled();
 // Same role/date/scenario viewports; a baseline run uses RMS_QA_HTML.
 for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:900});await row(0).scrollIntoViewIfNeeded();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false,`overflow ${width}`);assert((await save(0).boundingBox()).height>=44);if(width<=800){const alignment=await row(0).evaluate(tr=>[...tr.querySelectorAll('td')].map(td=>{const label=getComputedStyle(td,'::before'),style=getComputedStyle(td),child=td.querySelector('select,.assignment-room-number-link,strong,.badge'),box=child.getBoundingClientRect();return {label:td.dataset.label,start:style.alignItems,delta:Math.abs(td.getBoundingClientRect().top+parseFloat(style.paddingTop)+parseFloat(label.paddingTop)+9-(box.top+box.height/2))};}));assert(alignment.every(a=>a.start==='start'&&a.delta<9),JSON.stringify(alignment));}assert(await field(0).getAttribute('aria-label'));await field(0).focus();await page.keyboard.press('Tab');assert(await page.evaluate(()=>document.activeElement!==document.body));if([390,1440].includes(width)){await positionRow();await page.screenshot({path:resolve(evidence,`assignment-memo-admin-${width}.png`)});}}
 await page.evaluate(()=>__memoQA.rerender());
 await page.locator('[data-action="cleaning-history"][data-id="'+targets[0]+'"]').first().click();await page.getByRole('dialog').waitFor();assert((await page.getByRole('dialog').innerText()).includes('기존 요청 · 데모'),(await page.getByRole('dialog').innerText())+' HISTORY '+JSON.stringify(assignments.filter(a=>a.cleaningTargetId===targets[0]).map(a=>a.instructionMemo)));await page.goBack();await page.waitForFunction(()=>!document.querySelector('[role="dialog"]'));
 const saved=assignments.find(a=>a.isCurrent&&a.cleaningTargetId===targets[0]);saved.instructionMemo=memo;
 await setup('maid');assert.equal(await page.locator('[data-control="assignment-instruction"]').count(),0);assert((await page.locator('body').innerText()).includes(memo));assert(!(await page.locator('body').innerText()).includes('142호 요청 · 데모'));
 const mutations=requests.filter(r=>r.method==='POST').length;await page.evaluate(id=>__memoQA.save(id),targets[0]);assert.equal(requests.filter(r=>r.method==='POST').length,mutations);
 await page.locator('[data-action="cleaning-maid-room-toggle"][data-id="'+saved.assignmentId+'"]').click();await page.locator('[data-cleaning-assignment="'+saved.assignmentId+'"]').waitFor();assert((await page.locator('[data-cleaning-assignment="'+saved.assignmentId+'"]').innerText()).includes(memo));
 for(const width of [360,390,768,1440]){await page.setViewportSize({width,height:900});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);if([390,1440].includes(width))await page.screenshot({path:resolve(evidence,`assignment-memo-maid-${width}.png`)});}
 const leaks=await page.evaluate(memo=>[location.href,JSON.stringify(history.state),...Object.values(localStorage),...Object.values(sessionStorage)].some(v=>String(v).includes(memo)),memo);assert.equal(leaks,false);
 await setup();await field(0).fill('응답 누락 확인');omitMemo=true;await save(0).click();await settled();assert.equal(await page.evaluate(()=>__memoQA.get().error),'ASSIGNMENT_INSTRUCTION_UNCONFIRMED');assert.equal(await field(0).inputValue(),'응답 누락 확인');assert((await save(0).innerText()).includes('최신 메모 확인'));
 await page.evaluate(()=>__memoQA.resetDate('2099-01-01'));assert.equal(await page.evaluate(()=>__memoQA.get().edits),0);
 assignments.find(a=>a.isCurrent&&a.cleaningTargetId===targets[0]).attemptStatus='in_progress';await setup();assert(await field(0).isDisabled());assert(await save(0).isDisabled());
 // Exercise the standalone demo with real login, assignment and save controls.
 const demoContext=await browser.newContext({viewport:{width:390,height:900},serviceWorkers:'block'}),demo=await demoContext.newPage();demo.setDefaultTimeout(10000);
 demo.on('pageerror',e=>errors.push(e.message));
 const demoSource=source.replace('      void bootApplication();',`window.__memoDemo={get:id=>structuredClone(state.assignments[id]),maid:()=>MAIDS[0].id};
      void bootApplication();`);
 await demo.route('**/*',r=>{const u=new URL(r.request().url());if(u.origin!==origin)return r.abort();if(u.pathname==='/runtime-config.json')return json(r,{mode:'demo'});if(u.pathname==='/index.html')return r.fulfill({contentType:'text/html',body:demoSource});return r.continue();});
 await demo.goto(origin+'/index.html?scenario=0&role=admin&view=today&date=2026-08-15');
 await demo.locator('#login-id').fill('admin');await demo.locator('#login-password').fill('admin1234');await demo.locator('#login-form').press('Enter');await demo.locator('[data-action="logout"]:visible').first().waitFor();
 await demo.locator('[data-action="nav"][data-view="cleaning"]:visible').first().click();await demo.locator('[data-action="cleaning-tab"][data-tab="assignment-tomorrow"]').click();
 const demoField=demo.locator('[data-control="demo-assignment-instruction"]:enabled').first(),demoId=await demoField.getAttribute('data-target'),demoMaid=await demo.evaluate(()=>__memoDemo.maid());
 await demo.locator('[data-control="assignment-maid"][data-location="table"][data-target="'+demoId+'"]').selectOption(demoMaid);
 const df=demo.locator('[data-control="demo-assignment-instruction"][data-target="'+demoId+'"]'),ds=demo.locator('[data-action="demo-instruction-save"][data-id="'+demoId+'"]');
 await df.fill('수건 5개 · 데모');await ds.click();await demo.locator('[data-action="save-assignments"]').click();assert.equal((await demo.evaluate(id=>__memoDemo.get(id),demoId)).committedInstructionMemo,'수건 5개 · 데모');
 await df.fill('물 2개 · 데모');await ds.click();assert.equal((await demo.evaluate(id=>__memoDemo.get(id),demoId)).committedInstructionMemo,'물 2개 · 데모',JSON.stringify(await demo.evaluate(id=>__memoDemo.get(id),demoId))+' '+await demo.locator('#toast-region').innerText());
 await df.fill('');await ds.click();assert.equal((await demo.evaluate(id=>__memoDemo.get(id),demoId)).committedInstructionMemo,null);
 await df.fill('메이드 전달 확인 · 데모');await ds.click();
 for(const width of [360,390,768,1440]){await demo.setViewportSize({width,height:900});assert.equal(await demo.evaluate(()=>document.documentElement.scrollWidth>innerWidth),false);}
 await demo.locator('[data-action="logout"]:visible').first().click();await demo.locator('#login-id').fill('maid1');await demo.locator('#login-password').fill('maid1234');await demo.locator('#login-form').press('Enter');await demo.locator('[data-action="logout"]:visible').first().waitFor();assert((await demo.locator('body').innerText()).includes('메이드 전달 확인 · 데모'));assert.equal(await demo.locator('[data-action="demo-instruction-save"]').count(),0);
 await demoContext.close();assert.deepEqual(errors,[]);assert.deepEqual(consoleProblems,[]);
 console.log('PASS: notified/no-attempt tomorrow backlog, start race refusal, permission denial, role-specific endpoints, per-target memo, omit/clear, draft/notify, 400/409, ambiguous replay, 500 UTF-16, safe rendering, history/Back, roles, started lock, 4 widths, keyboard/focus, missing-field refusal, demo save/read, no persistence or console errors');
}finally{await browser.close();}
