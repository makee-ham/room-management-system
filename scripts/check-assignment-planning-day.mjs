import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const html=readFileSync('WIREFRAME/index.html','utf8');
const source=html.slice(html.indexOf('      function liveAssignmentInPlanningDay('),html.indexOf('      function liveAssignmentScheduleBadges('));
const today='2026-11-06',tomorrow='2026-11-07';
let slice;
const api=vm.runInNewContext(source+';({includes:liveAssignmentInPlanningDay,rows:liveAssignmentRows})',{
  liveKstIsoDate:()=>today,addIsoDays:()=>tomorrow,cleaningState:()=>slice,
});
for(const status of ['field_completed','upload_pending','submitted']){
  assert.equal(api.includes({serviceDate:'2026-11-05',attemptStatus:status},tomorrow),false);
  assert.equal(api.includes({serviceDate:today,attemptStatus:status},tomorrow),false);
  assert.equal(api.includes({serviceDate:tomorrow,attemptStatus:status},tomorrow),true);
  assert.equal(api.includes({serviceDate:'2026-11-05',attemptStatus:status},today),true);
  assert.equal(api.includes({attemptStatus:status},tomorrow),true,'missing date is not inferred');
}
for(const status of ['scheduled','in_progress','interrupted','rejected','approved','superseded',null,undefined]){
  assert.equal(api.includes({serviceDate:today,attemptStatus:status},tomorrow),true,'only physical completion workflow states are excluded');
}
const old={cleaningTargetId:'old',serviceDate:today,attemptStatus:'submitted',isCurrent:true,roomNumber:'142',maidProfileId:'a',feeSnapshot:30000};
slice={serviceDate:tomorrow,assignments:[old],manualEdits:new Map(),draftSaveResults:new Map(),preview:{proposedAssignments:[{cleaningTargetId:'new-a',roomNumber:'117',maidProfileId:'a',feeSnapshot:50000},{cleaningTargetId:'new-b',roomNumber:'623',maidProfileId:'b',feeSnapshot:48000}]}};
const rows=api.rows();assert.equal(rows.length,2);assert.equal(Math.abs(rows[0].feeSnapshot-rows[1].feeSnapshot),2000);assert.equal(slice.assignments[0],old,'source history is untouched');
slice.serviceDate=today;assert.equal(api.rows().length,3,'today retains unresolved workflow');
console.log('PASS: tomorrow physical-completion scope, unknown-status/date conservatism, actual fee totals and immutable history');
