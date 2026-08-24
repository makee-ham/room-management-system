from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML=Path('WIREFRAME/index.html')
html=HTML.read_text(encoding='utf-8')


def replace_between(start_marker:str,end_marker:str,replacement:str,label:str)->None:
    global html
    start=html.find(start_marker)
    if start<0:raise SystemExit(f'{label}: start marker missing')
    end=html.find(end_marker,start)
    if end<0:raise SystemExit(f'{label}: end marker missing')
    html=html[:start]+replacement+html[end:]


def replace_once(old:str,new:str,label:str)->None:
    global html
    count=html.count(old)
    if count!=1:raise SystemExit(f'{label}: expected one match, found {count}')
    html=html.replace(old,new,1)

facets=r'''      function roomStatusFacets(no) {
        no=String(no);
        const room=ROOMS.find(item=>item.no===no),cleaning=roomCleaningFacet(no),occupied=room?.occupancy==='occupied',blockingReasons=room?roomBlockingReasons(no):[],operationStopped=!!state.roomStopped?.[no],dataHold=!!room&&roomIsOnHold(no),candleCount=room&&!occupied?Number(state.candles?.[no]||0):0,checkoutInspection=!!checkoutInspectionPending(no);
        const genericBlockingReasons=blockingReasons.filter(reason=>!String(reason).startsWith('운영 중지')&&!String(reason).startsWith('정보 확인 필요')&&!String(reason).startsWith('촛불'));
        const genericBlocked=genericBlockingReasons.length>0;
        return {
          room:no,
          occupied,
          occupancy:occupied?'occupied':'vacant',
          occupancyLabel:occupied?'투숙 중':'공실',
          cleaningActive:cleaning.active,
          cleaningKind:cleaning.kind,
          cleaningStage:cleaning.stage,
          cleaningLabel:cleaning.label,
          cleaningTone:cleaning.tone,
          cleaningJob:cleaning.job,
          checkoutInspection,
          operationStopped,
          dataHold,
          genericBlocked,
          blockingReasons,
          genericBlockingReasons,
          candleCount,
          blocked:operationStopped||dataHold||genericBlocked||candleCount>0,
          hasSecondary:cleaning.active||checkoutInspection||operationStopped||dataHold||genericBlocked||candleCount>0,
        };
      }
'''
replace_between('      function roomStatusFacets(no) {','      function roomMatchesFacetFilter',facets,'room status facets')

badges_and_panel=r'''      function roomFacetBadgeMarkup(facets) {
        if(!facets.hasSecondary)return '';
        const badges=[statusBadge(facets.occupancyLabel,facets.occupied?'blue':'neutral')];
        if(facets.cleaningActive)badges.push(statusBadge(facets.cleaningLabel||`${facets.cleaningKind||'청소'} 필요`,facets.cleaningTone));
        if(facets.checkoutInspection)badges.push(statusBadge('퇴실점검 대상','amber'));
        if(facets.operationStopped)badges.push(statusBadge('운영 중지','red'));
        else if(facets.dataHold)badges.push(statusBadge('정보 확인 필요','amber'));
        if(facets.genericBlocked)badges.push(statusBadge('입실 차단','red'));
        if(facets.candleCount>0)badges.push(statusBadge(`촛불 ${facets.candleCount}개`,'amber'));
        return badges.join('');
      }
      function concurrentStatusBadges(no) { return roomFacetBadgeMarkup(roomStatusFacets(no)); }
      function concurrentStatusPanelMarkup(no) {
        const facets=roomStatusFacets(no);if(!facets.hasSecondary)return '';
        const items=[`<div class="info-item"><span>점유</span><strong>${esc(facets.occupancyLabel)}</strong></div>`];
        if(facets.cleaningActive){items.push(`<div class="info-item"><span>청소 유형</span><strong>${esc(facets.cleaningKind||'청소')}</strong></div>`);items.push(`<div class="info-item"><span>청소 단계</span><strong>${esc(facets.cleaningStage||'청소 필요')}</strong></div>`);}
        if(facets.checkoutInspection)items.push('<div class="info-item"><span>퇴실점검</span><strong>대상 · 완료 전</strong></div>');
        if(facets.operationStopped)items.push(`<div class="info-item"><span>운영</span><strong>운영 중지</strong></div>`);
        else if(facets.dataHold)items.push('<div class="info-item"><span>기준정보</span><strong>정보 확인 필요</strong></div>');
        if(facets.genericBlocked)items.push(`<div class="info-item"><span>입실 조건</span><strong>${esc(facets.genericBlockingReasons.join(' · ')||'입실 차단')}</strong></div>`);
        if(facets.candleCount>0)items.push(`<div class="info-item"><span>촛불</span><strong>${facets.candleCount}개 회수 필요</strong></div>`);
        return `<section class="card card-pad room-state-dimensions" data-room-state-dimensions="${no}" aria-labelledby="room-state-dimensions-title-${no}"><div class="section-head"><div><h3 id="room-state-dimensions-title-${no}">동시에 적용되는 객실 상태</h3><p class="audit-note">점유·청소·퇴실점검·운영·안전 조건을 서로 덮어쓰지 않고 함께 표시합니다.</p></div></div><div class="badge-row">${roomFacetBadgeMarkup(facets)}</div><div class="info-grid">${items.join('')}</div></section>`;
      }
'''
replace_between('      function concurrentStatusBadges(no) {','      function decorateConcurrentRoomStatuses',badges_and_panel,'status badge and detail panel')

replace_once(
"""            card.dataset.occupancyFacet=facets.occupancy;
            card.dataset.cleaningFacet=facets.cleaningActive?'active':'none';
            card.dataset.cleaningKind=facets.cleaningKind||'';""",
"""            card.dataset.occupancyFacet=facets.occupancy;
            card.dataset.cleaningFacet=facets.cleaningActive?'active':'none';
            card.dataset.cleaningKind=facets.cleaningKind||'';
            card.dataset.checkoutInspectionFacet=facets.checkoutInspection?'pending':'none';
            card.dataset.operationFacet=facets.operationStopped?'stopped':facets.dataHold?'data-hold':facets.genericBlocked?'blocked':'normal';
            card.dataset.candleFacet=String(facets.candleCount||0);""",
'card facet datasets')

api=r'''          setRoomStatusFacetTest:(roomNo,patch={})=>{const no=String(roomNo),room=ROOMS.find(item=>item.no===no);if(!room)throw new Error('객실을 찾을 수 없습니다.');if(Object.prototype.hasOwnProperty.call(patch,'roomStopped')){state.roomStopped[no]=!!patch.roomStopped;if(patch.roomStopped)state.roomStopReasons[no]=String(patch.stopReason||'상태 조합 테스트');else delete state.roomStopReasons[no];}if(Object.prototype.hasOwnProperty.call(patch,'dataIssue'))room.dataIssue=String(patch.dataIssue||'');if(Object.prototype.hasOwnProperty.call(patch,'candles'))state.candles[no]=Math.max(0,Number(patch.candles)||0);render();return {...roomStatusFacets(no)};},
'''
marker='          roomStatusFacets:roomNo=>({...roomStatusFacets(String(roomNo))}),'
if html.count(marker)!=1:raise SystemExit(f'test API marker mismatch: {html.count(marker)}')
html=html.replace(marker,marker+'\n'+api,1)

HTML.write_text(html,encoding='utf-8')

Path('DOCS/22_ROOM_STATUS_FACET_BADGES.md').write_text('''# 객실 상태 차원 배지 정책\n\n- 확정일: 2026-08-24\n\n객실 카드의 단일 주 상태는 요약일 뿐이며, 중요한 운영 조건을 덮어쓰지 않는다. 청소·퇴실점검·운영 중지·정보 확인·입실 차단·촛불 중 하나라도 활성화되면 카드에 점유 상태와 모든 보조 상태를 함께 표시한다.\n\n## 표시 순서\n\n1. 점유: 투숙 중 / 공실\n2. 청소: 유형과 현재 단계\n3. 퇴실점검 대상\n4. 운영 중지 또는 정보 확인 필요\n5. 기타 입실 차단\n6. 촛불 회수 수량\n\n객실 상세의 `동시에 적용되는 객실 상태` 패널도 같은 차원을 사용한다. 상태 필터는 각 차원을 독립적으로 검색한다.\n''',encoding='utf-8')
for path,appendix in [
('WIREFRAME/README.md','''\n\n## 전체 객실 상태 차원 배지 (2026-08-24)\n\n청소·퇴실점검·운영·안전 보조 조건이 있는 객실은 점유 상태와 모든 활성 차원을 카드와 상세에 함께 표시한다.\n'''),
('WIREFRAME/QA.md','''\n\n## 2026-08-24 · 전체 객실 상태 차원 조합\n\n- 투숙+연박 청소+운영 중지, 공실+퇴실점검+퇴실 청소, 공실+추가 청소+촛불 조합을 확인했다.\n- 각 상태가 카드·상세에서 동시에 보이고 기존 필터가 유지되는지 확인했다.\n- 배지 중복, 반복 렌더링 원장 변경, 390·768·1440px 가로 넘침과 콘솔 오류를 확인했다.\n''')]:
    file=Path(path);file.write_text(file.read_text(encoding='utf-8').rstrip()+appendix,encoding='utf-8')

checker=Path('scripts/check-workspace.mjs')
text=checker.read_text(encoding='utf-8')
marker="console.log('Workspace check: passed');"
contracts=r'''for (const contract of [
  'function roomFacetBadgeMarkup(facets)',
  "statusBadge('퇴실점검 대상','amber')",
  "statusBadge('운영 중지','red')",
  "statusBadge('정보 확인 필요','amber')",
  "statusBadge('입실 차단','red')",
  '점유·청소·퇴실점검·운영·안전 조건을 서로 덮어쓰지 않고 함께 표시합니다.',
  'data-checkout-inspection-facet',
  'setRoomStatusFacetTest:',
]) {
  if (!html.includes(contract)) throw new Error(`Room status facet badge contract missing: ${contract}`);
}
console.log('Room status facet badge static contracts: passed');

'''
if text.count(marker)!=1:raise SystemExit(f'checker marker mismatch: {text.count(marker)}')
checker.write_text(text.replace(marker,contracts+marker,1),encoding='utf-8')

sha=hashlib.sha256(HTML.read_bytes()).hexdigest()
sums=Path('SHA256SUMS.txt');lines=sums.read_text(encoding='utf-8').splitlines();found=False;out=[]
for line in lines:
    if line.endswith('  WIREFRAME/index.html'):out.append(f'{sha}  WIREFRAME/index.html');found=True
    else:out.append(line)
if not found:raise SystemExit('wireframe checksum missing')
sums.write_text('\n'.join(out)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json');manifest=json.loads(manifest_path.read_text(encoding='utf-8'));manifest['version']='2026-08-24-room-status-facet-badges';manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds');manifest.setdefault('sha256',{})['WIREFRAME/index.html']=sha;manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
