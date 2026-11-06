#!/usr/bin/env node
// Browser plugin not available. Synthetic push events, real browser IndexedDB; no provider sends.
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createRequire} from 'node:module';
const {chromium}=createRequire(import.meta.url)('playwright');
const origin=process.env.RMS_QA_ORIGIN||'http://127.0.0.1:4178';
const source=await readFile('WIREFRAME/sw.js','utf8');
const browser=await chromium.launch({headless:true});
try {
 const page=await browser.newPage();
 await page.goto(origin+'/privacy.html');
 const result=await page.evaluate(async source=>{
  const listeners=new Map(),shown=[],opened=[],messages=[];
  let failDisplay=false,windows=[];
  const worker={location:new URL(location.origin+'/sw.js'),addEventListener:(name,fn)=>listeners.set(name,fn),
   clients:{matchAll:async()=>windows,openWindow:async url=>opened.push(url)},registration:{
    showNotification:async(title,options)=>{if(failDisplay)throw Error('synthetic display failure');shown.push({title,options});},getNotifications:async()=>[]}};
  const api=new Function('self',source+'\nreturn {readPushPayload,safeNotificationUrl,claimPushReceipt,openPushReceiptStore};')(worker);
  const id=n=>`22000000-0000-4000-8000-${String(n).padStart(12,'0')}`;
  const push=(n,kind='availabilityRequest',extra={})=>({payloadVersion:1,notificationId:id(n),title:'민감 원문',body:'원문을 표시하지 않음',deepLink:{kind,entityId:id(9000)},...extra});
  const dispatch=async(name,event)=>{let done;listeners.get(name)({...event,waitUntil:p=>done=p});await done;};
  const send=data=>dispatch('push',{data:{json:()=>data}});
  await Promise.all(Array.from({length:8},()=>send(push(1))));
  const concurrentCount=shown.length;
  const first=shown[0];
  for(const [n,kind]of ['cleaningTarget','assignmentRequest','submission','complaintCase','payrollCycle','payrollProfile','availabilityRequest'].entries())await send(push(n+2,kind));
  failDisplay=true;try{await send(push(10));}catch{}failDisplay=false;await send(push(10));
  const retryCount=shown.filter(n=>n.options.tag===id(10)).length;
  // Seed expired and over-cap receipts, then claim once through the actual transaction.
  const db=await api.openPushReceiptStore();
  await new Promise((resolve,reject)=>{const tx=db.transaction('receipts','readwrite'),store=tx.objectStore('receipts');store.clear();for(let n=100;n<1110;n++)store.put({id:id(n),receivedAt:Date.now()-n});store.put({id:id(1),receivedAt:Date.now()-25*3600000});tx.oncomplete=resolve;tx.onerror=reject;});db.close();
  await send(push(1));
  const db2=await api.openPushReceiptStore();const receipts=await new Promise((resolve,reject)=>{const tx=db2.transaction('receipts'),req=tx.objectStore('receipts').getAll();req.onsuccess=()=>resolve(req.result);req.onerror=reject;});db2.close();
  let navigations=0,focused=0;
  windows=[{url:location.origin+'/index.html?view=rooms',postMessage:m=>messages.push(m),navigate:async()=>navigations++,focus:async()=>focused++}];
  await dispatch('notificationclick',{notification:{data:first.options.data,close(){}}});
  windows=[];await dispatch('notificationclick',{notification:{data:first.options.data,close(){}}});
  await dispatch('notificationclick',{notification:{data:{url:'https://attacker.test/?token=secret'},close(){}}});
  const malformed=api.readPushPayload({json:()=>push(30,'https://attacker.test/')});
  const injected=api.safeNotificationUrl(location.origin+'/index.html?view=more&notice='+id(1)+'&token=secret');
  return {concurrentCount,first,retryCount,count:receipts.length,receiptFields:Object.keys(receipts[0]).sort(),messages,navigations,focused,opened,malformed,injected,uniqueTags:shown.slice(0,8).map(n=>n.options.tag)};
 },source);
 assert.equal(result.concurrentCount,1,'concurrent identical delivery displays once');
 assert.equal(result.retryCount,1,'display failure releases receipt for retry');
 assert.equal(result.count,1000,'24-hour receipt store remains bounded');
 assert.deepEqual(result.receiptFields,['id','receivedAt']);
 assert.equal(new Set(result.uniqueTags).size,8,'each notification uses its own ID tag');
 assert.equal(result.first.options.renotify,false);
 assert.equal(result.first.title,'확인할 운영 알림이 있습니다');
 assert(!result.first.options.body.includes('원문'));
 assert.equal(result.navigations,0,'click must not reload a running form');
 assert.equal(result.focused,1);
 assert.equal(result.messages.at(-1).type,'PUSH_NOTIFICATION_OPEN');
 assert.equal(result.opened[0],origin+'/index.html?view=more&notice=22000000-0000-4000-8000-000000000001');
 assert.equal(result.opened[1],origin+'/index.html?view=more');
 assert.equal(result.injected,origin+'/index.html?view=more');
 assert.equal(result.malformed.notificationId,undefined);
 console.log('Device push: all 7 typed links, concurrent dedupe, failed display retry, TTL/cap/privacy, safe cold/open-window clicks PASS. Synthetic only; actual device delivery NOT RUN.');
}finally{await browser.close();}
