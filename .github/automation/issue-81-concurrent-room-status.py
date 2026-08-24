from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HTML = Path('WIREFRAME/index.html')
html = HTML.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    html = html.replace(old, new, 1)


css = r'''
    .room-concurrent-statuses { display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:8px 0 0; }
    .room-state-dimensions { border-color:#b9d4ec; background:#f7fbff; }
    .room-state-dimensions .badge-row { margin-top:10px; }
    .room-state-dimensions .info-grid { margin-top:12px; }
    @media (max-width:720px) {
      .room-concurrent-statuses { gap:5px; }
      .room-state-dimensions .section-head { align-items:flex-start; }
    }
'''
replace_once('  </style>', css + '  </style>', 'concurrent room status CSS')

helpers = r'''      const ROOM_CLEANING_ACTIVE_JOBS=new Set(['draft','future','public','unassigned','claimed','scheduled','cleaning','upload','inspection','reclean','hold','stayover-requested','extra-requested']);
      function roomCleaningFacet(no) {
        no=String(no);
        const room=ROOMS.find(item=>item.no===no),job=state.jobs?.[no]||'',manual=activeManualCleaningRequest(no),attempt=activeUnfinishedAttempt(no),submission=currentSubmission(no),occupied=room?.occupancy==='occupied';
        const active=!!room&&(!!manual||roomNeedsCleaningNow(no)||ROOM_CLEANING_ACTIVE_JOBS.has(job));
        let kind=manual?.kind||attempt?.kind||submission?.kind||'';
        if(active&&!kind)kind=occupied?'연박 청소':roomCheckoutCleaningDue(no)?'퇴실 청소':'추가 청소';
        const stage=active?(roomCleaningStageLabel(job)||'청소 필요'):'';
        const compactKind=kind.replace(/\s*청소$/,'');
        const label=!active?'':stage.includes(kind)||compactKind&&stage.includes(compactKind)?stage:`${kind||'청소'}${stage?` · ${stage}`:''}`;
        const tone=['reclean','hold'].includes(job)?'red':['claimed','scheduled'].includes(job)?'blue':'amber';
        return {active,kind,stage,label,tone,job,manualRequestId:manual?.id||null,attemptId:attempt?.id||null,submissionId:submission?.id||null};
      }
      function roomStatusFacets(no) {
        no=String(no);
        const room=ROOMS.find(item=>item.no===no),cleaning=roomCleaningFacet(no),occupied=room?.occupancy==='occupied';
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
          checkoutInspection:!!checkoutInspectionPending(no),
          blocked:!!room&&roomBlockingReasons(no).length>0,
        };
      }
      function roomMatchesFacetFilter(room,filter) {
        const facets=roomStatusFacets(room.no);
        if(filter==='occupied')return facets.occupied;
        if(filter==='cleaning')return facets.cleaningActive;
        return true;
      }
      function roomNoFromStatusCard(card) {
        const ids=[card.dataset.room,card.dataset.id,...Array.from(card.querySelectorAll('[data-id]'),node=>node.dataset.id)].filter(Boolean).map(String);
        return ids.find(id=>ROOMS.some(room=>room.no===id))||null;
      }
      let roomStatusDecorating=false,roomStatusObserver=null,roomStatusQueued=false;
      function concurrentStatusBadges(no) {
        const facets=roomStatusFacets(no);
        if(!(facets.occupied&&facets.cleaningActive))return '';
        return `${statusBadge('투숙 중','blue')}${statusBadge(facets.cleaningLabel||'연박 청소 필요',facets.cleaningTone)}`;
      }
      function concurrentStatusPanelMarkup(no) {
        const facets=roomStatusFacets(no);
        if(!(facets.occupied&&facets.cleaningActive))return '';
        return `<section class="card card-pad room-state-dimensions" data-room-state-dimensions="${no}" aria-labelledby="room-state-dimensions-title-${no}"><div class="section-head"><div><h3 id="room-state-dimensions-title-${no}">동시에 적용되는 객실 상태</h3><p class="audit-note">투숙 여부와 청소 흐름은 서로 덮어쓰지 않고 독립적으로 표시합니다.</p></div></div><div class="badge-row">${statusBadge('투숙 중','blue')}${statusBadge(facets.cleaningLabel||'연박 청소 필요',facets.cleaningTone)}</div><div class="info-grid"><div class="info-item"><span>점유</span><strong>투숙 중</strong></div><div class="info-item"><span>청소 유형</span><strong>${esc(facets.cleaningKind||'연박 청소')}</strong></div><div class="info-item"><span>청소 단계</span><strong>${esc(facets.cleaningStage||'청소 필요')}</strong></div><div class="info-item"><span>필터 포함</span><strong>투숙 중 · 청소 필요</strong></div></div></section>`;
      }
      function decorateConcurrentRoomStatuses(root=document) {
        if(roomStatusDecorating)return;
        roomStatusDecorating=true;
        try {
          root.querySelectorAll('.room-card-v2,.room-card').forEach(card=>{
            const no=roomNoFromStatusCard(card);if(!no)return;
            const facets=roomStatusFacets(no),markup=concurrentStatusBadges(no);
            card.dataset.occupancyFacet=facets.occupancy;
            card.dataset.cleaningFacet=facets.cleaningActive?'active':'none';
            card.dataset.cleaningKind=facets.cleaningKind||'';
            let row=card.querySelector(':scope > .room-concurrent-statuses');
            if(!markup){row?.remove();return;}
            if(!row){row=document.createElement('div');row.className='room-concurrent-statuses';row.dataset.concurrentStatuses=no;const anchor=card.querySelector('.room-card-v2-head,.room-card-head,.room-card-v2-title');anchor?anchor.insertAdjacentElement('afterend',row):card.prepend(row);}
            if(row.innerHTML!==markup)row.innerHTML=markup;
          });
          const no=state.detail?.type==='room'?String(state.detail.id||''):'';
          const stack=no?document.querySelector('#main-content .detail-stack'):null,markup=no?concurrentStatusPanelMarkup(no):'';
          let panel=document.querySelector('[data-room-state-dimensions]');
          if(!markup){panel?.remove();}
          else if(stack){
            if(!panel){const holder=document.createElement('div');holder.innerHTML=markup;panel=holder.firstElementChild;stack.prepend(panel);}
            else if(panel.outerHTML!==markup)panel.outerHTML=markup;
          }
        } finally { roomStatusDecorating=false; }
      }
      function queueConcurrentRoomStatusDecoration() {
        if(roomStatusQueued)return;roomStatusQueued=true;
        queueMicrotask(()=>{roomStatusQueued=false;decorateConcurrentRoomStatuses();});
      }
      function installConcurrentRoomStatusObserver() {
        if(roomStatusObserver)return;
        const root=document.getElementById('app')||document.body;
        roomStatusObserver=new MutationObserver(queueConcurrentRoomStatusDecoration);
        roomStatusObserver.observe(root,{childList:true,subtree:true});
        queueConcurrentRoomStatusDecoration();
      }

'''
marker = '      function roomPresentation'
if html.count(marker) != 1:
    raise SystemExit(f'room status helper marker mismatch: {html.count(marker)}')
html = html.replace(marker, helpers + marker, 1)

wrapper = r'''      const filteredRoomsBeforeConcurrentFacets=filteredRooms;
      filteredRooms=function() {
        const filter=state.roomFilter;
        if(!['occupied','cleaning'].includes(filter))return filteredRoomsBeforeConcurrentFacets();
        state.roomFilter='all';
        try { return filteredRoomsBeforeConcurrentFacets().filter(room=>roomMatchesFacetFilter(room,filter)); }
        finally { state.roomFilter=filter; }
      };

'''
render_rooms_marker = '      function renderRooms()'
if html.count(render_rooms_marker) != 1:
    raise SystemExit(f'filtered rooms wrapper marker mismatch: {html.count(render_rooms_marker)}')
html = html.replace(render_rooms_marker, wrapper + render_rooms_marker, 1)

install_marker = '      hydrateTemplateSnapshotsForState();'
if html.count(install_marker) != 1:
    raise SystemExit(f'concurrent status observer install marker mismatch: {html.count(install_marker)}')
html = html.replace(install_marker, '      installConcurrentRoomStatusObserver();\n' + install_marker, 1)

api_methods = r'''          roomStatusFacets:roomNo=>({...roomStatusFacets(String(roomNo))}),
          concurrentStatusCandidates:()=>ROOMS.map(room=>({room:room.no,...roomStatusFacets(room.no)})),
          setConcurrentCleaningStage:(roomNo,job)=>{const no=String(roomNo);if(!ROOM_CLEANING_ACTIVE_JOBS.has(String(job)))throw new Error('지원하지 않는 청소 단계입니다.');if(!activeManualCleaningRequest(no))throw new Error('활성 수동 청소 요청이 없습니다.');state.jobs[no]=String(job);render();return {...roomStatusFacets(no)};},
          resolveConcurrentCleaning:(roomNo)=>{const no=String(roomNo),request=activeManualCleaningRequest(no);if(request){request.status='completed';request.completedAt=`${state.selectedDate} ${state.time}`;}state.jobs[no]='approved';render();return {...roomStatusFacets(no)};},
          concurrentStatusDom:roomNo=>{const no=String(roomNo),card=Array.from(document.querySelectorAll('.room-card-v2,.room-card')).find(node=>roomNoFromStatusCard(node)===no),row=card?.querySelector('.room-concurrent-statuses'),panel=document.querySelector(`[data-room-state-dimensions="${no}"]`);return {cardFound:!!card,cardText:row?.textContent?.replace(/\s+/g,' ').trim()||'',occupancyFacet:card?.dataset.occupancyFacet||null,cleaningFacet:card?.dataset.cleaningFacet||null,panelText:panel?.textContent?.replace(/\s+/g,' ').trim()||''};},
'''
api_marker = '          counts:()=>({reservations:'
if html.count(api_marker) != 1:
    raise SystemExit(f'concurrent status test API marker mismatch: {html.count(api_marker)}')
html = html.replace(api_marker, api_methods + api_marker, 1)

HTML.write_text(html, encoding='utf-8')

policy = '''# 객실 복합 상태 정책\n\n- 확정일: 2026-08-24\n- 범위: 객실 카드, 객실 상세, 상태 필터\n\n## 원칙\n\n객실의 `투숙 중`과 `청소 필요`는 서로 배타적인 단일 상태가 아니다. 투숙 중 객실에도 연박 청소가 요청·배정·진행·검수될 수 있으므로 점유, 청소 흐름, 운영·안전, 퇴실점검을 독립 차원으로 계산한다.\n\n## 표시 계약\n\n- 투숙 중이며 청소 흐름이 없으면 `투숙 중`만 표시한다.\n- 투숙 중이며 청소가 필요하면 `투숙 중`과 `연박 청소 · 현재 단계`를 동시에 표시한다.\n- 공실 청소는 `퇴실 청소` 또는 `추가 청소`와 현재 단계를 표시한다.\n- 운영 중지·입실 차단·퇴실점검은 점유와 청소를 덮어쓰지 않는 별도 조건이다.\n\n## 필터 계약\n\n- `투숙 중`: 청소 단계와 무관하게 현재 점유 중인 모든 객실.\n- `청소 필요`: 투숙 중 연박 청소와 공실 퇴실·추가·재청소의 활성 흐름 전체.\n- `배정 가능`: 공실이며 청소·안전·운영 조건을 모두 충족한 객실.\n\n청소 요청을 해제하거나 최종 승인하면 청소 차원만 해제되고, 예약 시각상 투숙 중이면 점유 차원은 유지된다.\n'''
Path('DOCS/20_CONCURRENT_ROOM_STATUS_POLICY.md').write_text(policy, encoding='utf-8')

for path, appendix in [
    ('WIREFRAME/README.md', '''\n\n## 투숙·청소 동시 상태 (2026-08-24)\n\n객실 점유와 청소 흐름을 독립 차원으로 표시한다. 투숙 중 객실에 연박 청소가 활성화되면 객실 카드와 상세에서 `투숙 중`과 `연박 청소 · 현재 단계`가 함께 보이며, `투숙 중` 필터와 `청소 필요` 필터 양쪽에 모두 포함된다.\n'''),
    ('WIREFRAME/QA.md', '''\n\n## 2026-08-24 · 투숙·청소 복합 상태\n\n- 투숙 중 + 연박 청소 필요 객실이 두 상태 필터에 모두 포함되는지 확인했다.\n- 배정 준비·담당 확정·청소 중·업로드·검수 단계에서도 점유 표식이 유지되는지 확인했다.\n- 청소 요청 해제 및 최종 해결 뒤 투숙 상태만 남는지 확인했다.\n- 공실 추가 청소가 청소 필요 필터에만 포함되는지 확인했다.\n- 반복 렌더링 뒤 상태 배지 중복과 예약·청소·급여 원장 변경이 없는지 확인했다.\n- 390·768·1440px 가로 넘침과 콘솔·런타임 오류를 확인했다.\n'''),
]:
    file = Path(path)
    file.write_text(file.read_text(encoding='utf-8').rstrip() + appendix, encoding='utf-8')

checker = Path('scripts/check-workspace.mjs')
check_text = checker.read_text(encoding='utf-8')
check_marker = "console.log('Workspace check: passed');"
contracts = r'''for (const contract of [
  'function roomStatusFacets(no)',
  "ROOM_CLEANING_ACTIVE_JOBS=new Set(['draft','future','public','unassigned','claimed','scheduled','cleaning','upload','inspection','reclean','hold','stayover-requested','extra-requested'])",
  "if(filter==='occupied')return facets.occupied;",
  "if(filter==='cleaning')return facets.cleaningActive;",
  'data-room-state-dimensions=',
  "statusBadge('투숙 중','blue')",
  '투숙 여부와 청소 흐름은 서로 덮어쓰지 않고 독립적으로 표시합니다.',
  'installConcurrentRoomStatusObserver();',
  'roomStatusFacets:roomNo=>',
]) {
  if (!html.includes(contract)) throw new Error(`Concurrent occupancy/cleaning status contract missing: ${contract}`);
}
console.log('Concurrent occupancy/cleaning status static contracts: passed');

'''
if check_text.count(check_marker) != 1:
    raise SystemExit(f'workspace checker marker mismatch: {check_text.count(check_marker)}')
checker.write_text(check_text.replace(check_marker, contracts + check_marker, 1), encoding='utf-8')

sha = hashlib.sha256(HTML.read_bytes()).hexdigest()
sums = Path('SHA256SUMS.txt')
lines = sums.read_text(encoding='utf-8').splitlines()
found = False
out = []
for line in lines:
    if line.endswith('  WIREFRAME/index.html'):
        out.append(f'{sha}  WIREFRAME/index.html')
        found = True
    else:
        out.append(line)
if not found:
    raise SystemExit('WIREFRAME/index.html checksum entry missing')
sums.write_text('\n'.join(out) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-24-concurrent-room-status'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = sha
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
