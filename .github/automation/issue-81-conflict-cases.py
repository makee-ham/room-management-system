from pathlib import Path
import hashlib
import json

index_path=Path('WIREFRAME/index.html')
text=index_path.read_text(encoding='utf-8')
old="""        const blockers=roomBlockingReasons(no),cleaningNeeded=roomNeedsCleaningNow(no),cleaningKind=cleaningNeeded?cleaningKindForRoom(no):'',cleaningStage=cleaningNeeded?(roomCleaningStageLabel(job)||'청소 필요'):'',inspectionPending=checkoutInspectionPending(no),blocked=blockers.length>0,available=!occupied&&!cleaningNeeded&&!inspectionPending&&!blocked;
        const conflict=occupied&&cleaningNeeded&&['퇴실 청소','재청소'].includes(cleaningKind),conflictReason=conflict?'현재 고객이 투숙 중인데 이전 퇴실·재청소 작업이 남아 있습니다. 출입과 작업 대상을 확인하세요.':'';
        return {room:no,occupancy,occupancyLabel,occupancyReason,occupied,vacant:!occupied,arrival:!occupied&&!!next,currentReservationId:current?.id||null,nextReservationId:next?.id||null,cleaningNeeded,cleaningKind,cleaningStage,checkoutInspectionPending:inspectionPending,blocked,blockers,available,conflict,conflictReason,job};"""
new="""        const baseBlockers=roomBlockingReasons(no),cleaningNeeded=roomNeedsCleaningNow(no),cleaningKind=cleaningNeeded?cleaningKindForRoom(no):'',cleaningStage=cleaningNeeded?(roomCleaningStageLabel(job)||'청소 필요'):'',inspectionPending=checkoutInspectionPending(no),conflictReasons=[];
        if(occupied&&cleaningNeeded&&cleaningKind!=='연박 청소')conflictReasons.push(`현재 고객이 투숙 중인데 ${cleaningKind} 작업이 남아 있습니다. 출입과 작업 대상을 확인하세요.`);
        if(!occupied&&cleaningNeeded&&cleaningKind==='연박 청소')conflictReasons.push('현재 공실인데 연박 청소 작업이 남아 있습니다. 고객 퇴실 여부와 작업 종류를 확인하세요.');
        if(occupied&&inspectionPending)conflictReasons.push('현재 고객이 투숙 중인데 이전 고객의 퇴실점검이 남아 있습니다. 다음 입실 전 점검 이력을 확인하세요.');
        const conflict=conflictReasons.length>0,conflictReason=conflictReasons.join(' · '),blockers=[...new Set([...baseBlockers,...conflictReasons])],blocked=blockers.length>0,available=!occupied&&!cleaningNeeded&&!inspectionPending&&!blocked;
        return {room:no,occupancy,occupancyLabel,occupancyReason,occupied,vacant:!occupied,arrival:!occupied&&!!next,currentReservationId:current?.id||null,nextReservationId:next?.id||null,cleaningNeeded,cleaningKind,cleaningStage,checkoutInspectionPending:inspectionPending,blocked,blockers,available,conflict,conflictReason,job};"""
if text.count(old)!=1:
    raise SystemExit(f'room-state conflict source mismatch: {text.count(old)}')
text=text.replace(old,new,1)
old="if(facets.conflict)items.push(statusBadge('이전 청소 충돌','red'));"
new="if(facets.conflict)items.push(statusBadge('상태 충돌','red'));"
if text.count(old)!=1:
    raise SystemExit(f'conflict badge source mismatch: {text.count(old)}')
text=text.replace(old,new,1)
old="if(facets.conflict)items.push(`<span class=\"room-status-sub is-conflict\">${icon('alert','icon-sm')}이전 퇴실 청소 충돌</span>`);"
new="if(facets.conflict)items.push(`<span class=\"room-status-sub is-conflict\">${icon('alert','icon-sm')}상태 충돌 · ${esc(facets.conflictReason)}</span>`);"
if text.count(old)!=1:
    raise SystemExit(f'conflict sub-badge source mismatch: {text.count(old)}')
text=text.replace(old,new,1)
old="const detailBadges=[checkoutInspectionPending(no)?'<span class=\"room-detail-badge\">퇴실점검 대상</span>':'',roomIsOnHold(no)?'<span class=\"room-detail-badge\">정보 확인 필요</span>':'',state.roomStopped[no]?'<span class=\"room-detail-badge\">운영 중지</span>':'',no==='332'&&state.conflict==='active'?'<span class=\"room-detail-badge\">출입·PIN 충돌</span>':'',candle?`<span class=\"room-detail-badge\">${icon('candle','icon-sm')}촛불 ${candle}개</span>`:'',issueCount?`<span class=\"room-detail-badge\">특이사항 ${issueCount}건</span>`:''].filter(Boolean).join('');"
new="const detailBadges=[candle?`<span class=\"room-detail-badge\">${icon('candle','icon-sm')}촛불 ${candle}개</span>`:'',issueCount?`<span class=\"room-detail-badge\">특이사항 ${issueCount}건</span>`:''].filter(Boolean).join('');"
if text.count(old)!=1:
    raise SystemExit(f'duplicate room-state badge source mismatch: {text.count(old)}')
text=text.replace(old,new,1)
index_path.write_text(text,encoding='utf-8')

policy_path=Path('DOCS/20_ROOM_STATE_FACET_POLICY.md')
policy=policy_path.read_text(encoding='utf-8')
old="""- 투숙 중 + 이전 퇴실 청소: 충돌 경고를 추가해 작업 대상을 확인

## 전이 규칙"""
new="""- 투숙 중 + 이전 퇴실·추가·재청소: 충돌 경고를 추가해 출입과 작업 대상을 확인
- 공실 + 연박 청소: 고객이 먼저 퇴실한 불일치로 보고 작업 종류 확인 경고
- 투숙 중 + 이전 고객 퇴실점검: 새 고객 입실 전 점검 이력이 남은 충돌로 표시

정상 조합은 `투숙 중 + 연박 청소`, `공실 + 퇴실·추가·재청소`다. 반대 조합은 임의로 청소 종류를 바꾸지 않고 운영·안전 차단에 포함해 사람이 확인한다.

## 전이 규칙"""
if policy.count(old)!=1:
    raise SystemExit(f'room-state policy conflict section mismatch: {policy.count(old)}')
policy_path.write_text(policy.replace(old,new,1),encoding='utf-8')

qa_path=Path('.github/automation/issue-81-room-facets.mjs')
qa=qa_path.read_text(encoding='utf-8')
marker="""// 공실 + 추가 청소도 공실과 청소를 함께 보존한다.
await api(desktop,'resetScenario',0);"""
insert="""// 투숙 중 연박 청소가 고객 퇴실 뒤까지 남으면 공실+연박의 불일치로 차단한다.
await api(desktop,'resetScenario',0);
candidates=await api(desktop,'facetCandidates');
const staleStayoverRoom=candidates.occupiedCleanable[0];
await api(desktop,'setManualCleaning',staleStayoverRoom,true);
await api(desktop,'setOperationalMoment','2026-09-30','12:00');
const staleStayover=await api(desktop,'roomStateFacets',staleStayoverRoom);
assert.equal(staleStayover.occupied,false);
assert.equal(staleStayover.cleaningNeeded,true);
assert.equal(staleStayover.cleaningKind,'연박 청소');
assert.equal(staleStayover.conflict,true,'vacant room retained a stale stayover job without a conflict');
assert.equal(staleStayover.blocked,true,'stale stayover conflict must be included in operational blockers');
assert.ok((await api(desktop,'roomsForState','blocked')).includes(staleStayoverRoom));

// 공실 + 추가 청소도 공실과 청소를 함께 보존한다.
await api(desktop,'resetScenario',0);"""
if qa.count(marker)!=1:
    raise SystemExit(f'stale stayover QA marker mismatch: {qa.count(marker)}')
qa=qa.replace(marker,insert,1)
old="""assert.match(cardText,/공실/);
assert.match(cardText,/퇴실점검 대상/);

// 기존 데이터에 이전 퇴실청소와 새 투숙이 겹친 경우가 있으면 충돌 경고를 검증한다."""
new="""assert.match(cardText,/공실/);
assert.match(cardText,/퇴실점검 대상/);
await api(desktop,'showRoom',inspectionRoom);
let detailText=await desktop.locator('#main-content').innerText();
assert.match(detailText,/공실/);
assert.match(detailText,/퇴실점검 대상/);
const cleaningBeforeInspectionComplete=facets.cleaningNeeded;
await api(desktop,'completeCheckoutInspection',inspectionRoom,'manual');
const inspectionCompleted=await api(desktop,'roomStateFacets',inspectionRoom);
assert.equal(inspectionCompleted.checkoutInspectionPending,false,'manual inspection completion did not clear inspection only');
assert.equal(inspectionCompleted.cleaningNeeded,cleaningBeforeInspectionComplete,'inspection completion incorrectly changed cleaning axis');
assert.ok(!(await api(desktop,'roomsForState','checkout-inspection')).includes(inspectionRoom));
if(cleaningBeforeInspectionComplete)assert.ok((await api(desktop,'roomsForState','cleaning')).includes(inspectionRoom));
await showAll(desktop);

// 기존 데이터에 이전 퇴실청소와 새 투숙이 겹친 경우가 있으면 충돌 경고를 검증한다."""
if qa.count(old)!=1:
    raise SystemExit(f'inspection-axis QA source mismatch: {qa.count(old)}')
qa=qa.replace(old,new,1)
old="""// 상세 화면에서도 같은 축 배지가 유지된다.
await api(desktop,'showRoom',inspectionRoom);
const detailText=await desktop.locator('#main-content').innerText();
assert.match(detailText,/공실/);
assert.match(detailText,/퇴실점검 대상/);

"""
if qa.count(old)!=1:
    raise SystemExit(f'legacy detail QA block mismatch: {qa.count(old)}')
qa=qa.replace(old,'',1)
qa_path.write_text(qa,encoding='utf-8')

checker_path=Path('scripts/check-workspace.mjs')
checker=checker_path.read_text(encoding='utf-8')
marker="console.log('Room state facet static contracts: passed');"
addition="""for (const contract of [
  "if(occupied&&cleaningNeeded&&cleaningKind!=='연박 청소')",
  "if(!occupied&&cleaningNeeded&&cleaningKind==='연박 청소')",
  'if(occupied&&inspectionPending)',
  'blockers=[...new Set([...baseBlockers,...conflictReasons])]',
]) {
  if (!html.includes(contract)) throw new Error(`Room-state conflict matrix contract missing: ${contract}`);
}
console.log('Room-state conflict matrix static contracts: passed');
"""+marker
if checker.count(marker)!=1:
    raise SystemExit(f'room-state checker marker mismatch: {checker.count(marker)}')
checker_path.write_text(checker.replace(marker,addition,1),encoding='utf-8')

digest=hashlib.sha256(index_path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
lines=sums_path.read_text(encoding='utf-8').splitlines()
found=False
for i,line in enumerate(lines):
    if line.endswith('  WIREFRAME/index.html'):
        lines[i]=f'{digest}  WIREFRAME/index.html';found=True
if not found:raise SystemExit('WIREFRAME checksum line missing')
sums_path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
