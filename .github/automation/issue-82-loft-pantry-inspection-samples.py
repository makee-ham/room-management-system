from __future__ import annotations

import hashlib
import json
import re
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


def balanced_end(source: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    quote = None
    escaped = False
    for index in range(start, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index + 1
    raise SystemExit(f'unbalanced {opening}{closing} block')


# Every current checkout template gets exactly one standardized loft-stairs, loft and pantry slot.
groups_marker = '      const TYPE_PHOTO_GROUPS='
groups_start = html.find(groups_marker)
if groups_start < 0:
    raise SystemExit('TYPE_PHOTO_GROUPS marker missing')
object_start = html.find('{', groups_start)
object_end = balanced_end(html, object_start, '{', '}')
groups_block = html[object_start:object_end]

universal_rules = """
          {id:'loft-stairs',zone:'복층 계단',label:'복층 계단·난간·계단 하부',description:'계단 전체와 난간, 모서리, 계단 하부까지 한 화면에 확인되도록 촬영합니다.',required:true,fixture:'floor'},
          {id:'loft-wide',zone:'복층',label:'복층 전체·바닥·난간',description:'복층 전체와 바닥, 벽면, 난간 끝단의 청소 상태가 보이게 촬영합니다.',required:true,fixture:'bed'},
          {id:'pantry',zone:'팬트리',label:'팬트리·수납 내부',description:'팬트리 문과 선반을 열어 내부, 바닥, 모서리의 정리·청소 상태를 촬영합니다.',required:true,fixture:'supply'},"""

for type_id in ['standard','premium','oceanPremium','oceanFamily']:
    match = re.search(rf'\b{re.escape(type_id)}\s*:\s*\[', groups_block)
    if not match:
        raise SystemExit(f'{type_id} photo group missing')
    array_start = groups_block.find('[', match.start())
    array_end = balanced_end(groups_block, array_start, '[', ']')
    array = groups_block[array_start:array_end]
    array = re.sub(r"\s*\{id:'(?:stairs|loft-stairs|loft-wide|pantry)'[^{}]*\},?", '', array)
    tv = re.search(r"\{id:'tv-on'[^{}]*\},?", array)
    if not tv:
        raise SystemExit(f'{type_id} tv-on insertion anchor missing')
    prefix = array[:tv.end()]
    if not prefix.rstrip().endswith(','):
        prefix += ','
    array = prefix + universal_rules + array[tv.end():]
    array = re.sub(r',\s*,', ',', array)
    for slot_id in ['loft-stairs','loft-wide','pantry']:
        count = len(re.findall(rf"id:'{re.escape(slot_id)}'", array))
        if count != 1:
            raise SystemExit(f'{type_id} {slot_id} expected once, found {count}')
    groups_block = groups_block[:array_start] + array + groups_block[array_end:]

html = html[:object_start] + groups_block + html[object_end:]

css = r'''
    .inspection-sample-entry { margin-top:16px; border-color:#b9d4ec; background:#f7fbff; }
    .inspection-sample-groups { display:grid; gap:16px; }
    .inspection-sample-room-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(108px,1fr)); gap:8px; margin-top:12px; }
    .inspection-sample-room-grid .btn { justify-content:center; min-height:44px; }
    .inspection-sample-readonly { border-color:#9fc7a9; background:#f6fff8; }
    .inspection-sample-readonly .badge-row { margin-top:10px; }
    .inspection-sample-photo-view { display:grid; gap:12px; }
    .inspection-sample-photo-view svg { width:100%; height:auto; max-height:52vh; border-radius:12px; background:#eef3f7; }
    @media (max-width:720px) {
      .inspection-sample-room-grid { grid-template-columns:repeat(3,minmax(0,1fr)); }
    }
'''
replace_once('  </style>', css + '  </style>', 'inspection sample CSS')

structure_labels = r'''      const UNIVERSAL_TEMPLATE_STRUCTURE_LABELS=Object.freeze({
        standard:'원룸형 메인 공간 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1',
        premium:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1',
        oceanPremium:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1',
        oceanFamily:'침실 2 · 거실 1 · 주방 1 · 욕실 2 · 복층 계단 1 · 복층 1 · 팬트리 1'
      });
      const UNIVERSAL_TEMPLATE_SLOT_IDS=Object.freeze(['loft-stairs','loft-wide','pantry']);

'''
insert_after_groups = object_start + len(groups_block)
html = html[:insert_after_groups] + '\n' + structure_labels + html[insert_after_groups:]

sample_helpers = r'''      function inspectionSampleForRoom(no) {
        no=String(no);
        const room=ROOMS.find(item=>item.no===no);if(!room)return null;
        const template=templateSnapshotFor(no,'퇴실 청소');if(!template)return null;
        const uploads=(template.photos||[]).map((slot,index)=>({...slot,id:String(slot.id),status:'done',image:{fixture:slot.fixture||'supply',version:'관리자 검수 샘플',uploadedAt:`샘플 ${String(index+1).padStart(2,'0')}`}}));
        const submission={id:`inspection-sample-${no}`,room:no,sample:true,readOnly:true,kind:'퇴실 청소',templateId:template.id,templateVersion:template.version,templateSnapshot:template,uploads,performerId:'sample',performerName:'검수 샘플',completedAt:'읽기 전용 샘플',note:'현재 타입 템플릿으로 자동 생성한 관리자 검수 샘플입니다.',candle:0};
        const attempt={id:`inspection-sample-attempt-${no}`,room:no,sample:true,kind:'퇴실 청소',templateSnapshot:template,uploads,performerId:'sample',performerName:'검수 샘플',startedAt:'읽기 전용 샘플',completedAt:'읽기 전용 샘플'};
        return {room,template,submission,attempt};
      }
      function inspectionSampleCatalog() { return ROOMS.map(room=>inspectionSampleForRoom(room.no)).filter(Boolean); }
      function inspectionSampleContract(no) {
        const sample=inspectionSampleForRoom(no);if(!sample)return null;
        const expected=photoSlotContract(sample.template.photos||[]),actual=photoSlotContract(inspectionTemplateUploadItems(String(no),sample.template,sample.submission,sample.attempt));
        return {room:String(no),typeId:sample.room.type,version:sample.template.version,expected,actual,same:JSON.stringify(expected)===JSON.stringify(actual),universal:Object.fromEntries(UNIVERSAL_TEMPLATE_SLOT_IDS.map(id=>[id,expected.filter(item=>item.id===id).length]))};
      }
      function universalCheckoutTemplateAudit() {
        return ROOMS.map(room=>{const snapshot=templateSnapshotFor(room.no,'퇴실 청소'),contract=photoSlotContract(snapshot?.photos||[]);return {room:room.no,typeId:room.type,count:contract.length,required:contract.filter(item=>item.required).length,signature:JSON.stringify(contract),universal:Object.fromEntries(UNIVERSAL_TEMPLATE_SLOT_IDS.map(id=>[id,contract.filter(item=>item.id===id).length]))};});
      }
      function renderInspectionSampleList() {
        const groups=Object.entries(ROOM_TYPES).map(([typeId,type])=>{const rooms=ROOMS.filter(room=>room.type===typeId),snapshot=templateSnapshotFor(rooms[0]?.no,'퇴실 청소'),required=(snapshot?.photos||[]).filter(item=>item.required).length,total=snapshot?.photos?.length||0;return `<section class="card card-pad"><div class="section-head"><div><h3>${esc(type.name)} · ${rooms.length}실</h3><p class="audit-note">${esc(UNIVERSAL_TEMPLATE_STRUCTURE_LABELS[typeId])}</p></div><div class="badge-row">${statusBadge(`고정 ${total}개 슬롯`,'blue')}${statusBadge(`필수 ${required}개`,'green')}</div></div><div class="inspection-sample-room-grid">${rooms.map(room=>button(`${room.no}호`,'inspection-sample-open','outline',`data-id="${room.no}" aria-label="${room.no}호 현재 템플릿 관리자 검수 샘플 보기"`)).join('')}</div></section>`;}).join('');
        return renderCoach()+renderNetworkNotice()+detailHeader('객실별 관리자 검수 샘플',`현재 퇴실 청소 템플릿 · ${ROOMS.length}개 객실 · 읽기 전용`)+`<div class="template-page"><section class="card card-pad inspection-sample-readonly"><div class="section-head"><div><h3>실제 운영 원장과 분리된 검수 샘플입니다</h3><p class="audit-note">각 객실번호를 타입에 매칭해 현재 고정 템플릿으로 생성합니다. 승인·반려·급여·청소 상태·이벤트는 만들지 않습니다.</p></div>${statusBadge(`${ROOMS.length}개 샘플`,'green')}</div><div class="badge-row">${statusBadge('복층 계단 필수','blue')}${statusBadge('복층 필수','blue')}${statusBadge('팬트리 필수','blue')}</div></section><div class="inspection-sample-groups">${groups}</div><div class="template-actions">${button('청소 템플릿으로 돌아가기','inspection-sample-list-back','outline')}</div></div>`;
      }
      function renderInspectionSample(no) {
        const sample=inspectionSampleForRoom(no);if(!sample)return renderInspectionSampleList();
        const {room,template,submission,attempt}=sample,type=ROOM_TYPES[room.type],required=template.photos.filter(item=>item.required).length;
        return renderCoach()+renderNetworkNotice()+detailHeader(`${room.no}호 관리자 검수 샘플`,`${esc(type.name)} · 현재 ${esc(template.version)} · 읽기 전용`)+`<div class="detail-grid" data-inspection-sample-room="${room.no}" data-inspection-sample-readonly="true"><div class="detail-stack"><section class="card card-pad inspection-sample-readonly"><div class="section-head"><div><h3>현재 타입 템플릿 검수 샘플</h3><p class="audit-note">메이드가 현재 템플릿으로 제출했을 때 관리자가 확인하는 요소·순서·형식입니다.</p></div>${statusBadge('읽기 전용 · 원장 미연결','green')}</div><div class="info-grid"><div class="info-item"><span>객실·타입</span><strong>${room.no}호 · ${esc(type.name)}</strong></div><div class="info-item"><span>타입 고정 구성</span><strong>${esc(UNIVERSAL_TEMPLATE_STRUCTURE_LABELS[room.type])}</strong></div><div class="info-item"><span>전체 사진 슬롯</span><strong>${template.photos.length}개</strong></div><div class="info-item"><span>필수 / 선택</span><strong>${required} / ${template.photos.length-required}</strong></div></div><div class="badge-row">${statusBadge('복층 계단','blue')}${statusBadge('복층','blue')}${statusBadge('팬트리','blue')}</div></section>${renderInspectionTemplateReview(room.no,template,submission,attempt)}</div><aside class="detail-stack"><section class="card card-pad"><h3>샘플의 효력</h3><p class="audit-note">실제 제출·승인·반려·폭탄방 판단·급여 적립·청소 완료를 발생시키지 않습니다. 현재 템플릿 UI와 검수 형식만 확인합니다.</p></section><section class="card card-pad"><h3>버전 원칙</h3><p class="audit-note">실제 과거 제출은 당시 스냅샷을 유지합니다. 이 샘플은 현재 새 작업에 적용될 템플릿만 보여줍니다.</p></section></aside></div><div class="template-actions">${button('이전 화면','inspection-sample-back','outline',`data-id="${room.no}"`)}</div>`;
      }

'''
snapshot_marker = "      function templateSnapshotFor(roomNo,kind='퇴실 청소')"
if html.count(snapshot_marker) != 1:
    raise SystemExit(f'inspection sample helper marker mismatch: {html.count(snapshot_marker)}')
html = html.replace(snapshot_marker, sample_helpers + snapshot_marker, 1)

# Make the current template area explicitly show the universal spaces and a 121-room sample entry point.
timeline_marker = '      function renderTemplateTimeline'
if html.count(timeline_marker) != 1:
    raise SystemExit(f'template list wrapper marker mismatch: {html.count(timeline_marker)}')
list_wrapper = r'''      const renderTemplateListBeforeInspectionSamples=renderTemplateList;
      renderTemplateList=function() {
        const output=renderTemplateListBeforeInspectionSamples();
        return output+`<section class="card card-pad inspection-sample-entry"><div class="section-head"><div><h3>객실별 관리자 검수 샘플</h3><p class="audit-note">121개 객실을 현재 타입 템플릿으로 생성한 읽기 전용 검수 화면에서 확인합니다.</p></div>${statusBadge(`${ROOMS.length}개`,'green')}</div><div class="badge-row">${statusBadge('모든 객실 · 복층 계단','blue')}${statusBadge('모든 객실 · 복층','blue')}${statusBadge('모든 객실 · 팬트리','blue')}</div><div class="template-actions">${button('객실별 검수 샘플 보기','inspection-sample-list','primary')}</div></section>`;
      };

'''
html = html.replace(timeline_marker, list_wrapper + timeline_marker, 1)

read_change_marker = '      function readTemplateChange'
if html.count(read_change_marker) != 1:
    raise SystemExit(f'template detail wrapper marker mismatch: {html.count(read_change_marker)}')
detail_wrapper = r'''      const renderTemplateDetailBeforeUniversalSpaces=renderTemplateDetail;
      renderTemplateDetail=function(id,mode='view') {
        const output=renderTemplateDetailBeforeUniversalSpaces(id,mode),template=templateById(id);
        if(mode!=='view'||!template)return output;
        const notice=`<section class="card template-section"><div class="template-section-head"><div><h3>모든 객실 공통 필수 공간</h3><p>객실번호와 관계없이 현재 퇴실 청소 템플릿에 고정 적용합니다.</p></div><div class="badge-row">${statusBadge('복층 계단','blue')}${statusBadge('복층','blue')}${statusBadge('팬트리','blue')}</div></div><p class="audit-note">${esc(UNIVERSAL_TEMPLATE_STRUCTURE_LABELS[template.typeId])}</p></section>`;
        return output.replace('<div class="template-page">','<div class="template-page">'+notice);
      };

'''
html = html.replace(read_change_marker, detail_wrapper + read_change_marker, 1)

# Sample photo clicks use the same visual card without requiring a real stored submission.
photo_marker = '      function openInspectionPhoto(no,submissionId,id,trigger=document.activeElement) {'
if html.count(photo_marker) != 1:
    raise SystemExit(f'inspection sample photo marker mismatch: {html.count(photo_marker)}')
photo_branch = r'''      function openInspectionPhoto(no,submissionId,id,trigger=document.activeElement) {
        if(String(submissionId)===`inspection-sample-${no}`){
          const sample=inspectionSampleForRoom(no),upload=sample?.submission?.uploads?.find(item=>String(item.id)===String(id));
          if(!upload){toast('검수 샘플 사진 슬롯을 찾을 수 없습니다.','error');return;}
          showModal({title:`${no}호 · ${upload.label}`,subtitle:'현재 템플릿 · 읽기 전용 관리자 검수 샘플',body:`<div class="inspection-sample-photo-view">${inspectionPhotoSvg(upload,upload.label)}<div><strong>${esc(upload.zone||'사진')} · ${upload.required?'필수':'선택'}</strong><p class="audit-note">${esc(upload.description||'청소 완료 상태를 촬영합니다.')}</p></div></div>`,confirmLabel:'닫기',confirmAction:'close-modal',confirmVariant:'primary',trigger});return;
        }
'''
html = html.replace(photo_marker, photo_branch, 1)

# Route the new sample list and detail pages.
detail_route_marker = "        if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');"
if html.count(detail_route_marker) != 1:
    raise SystemExit(f'inspection sample detail route marker mismatch: {html.count(detail_route_marker)}')
html = html.replace(detail_route_marker, "        if (state.detail.type==='inspectionSamples') return renderInspectionSampleList();\n        if (state.detail.type==='inspectionSample') return renderInspectionSample(state.detail.id);\n" + detail_route_marker, 1)

old_title = "templates:'청소 템플릿 설정',template:'청소 템플릿 상세'"
if html.count(old_title) != 1:
    raise SystemExit(f'inspection sample title map marker mismatch: {html.count(old_title)}')
html = html.replace(old_title, "templates:'청소 템플릿 설정',template:'청소 템플릿 상세',inspectionSamples:'객실별 관리자 검수 샘플',inspectionSample:'관리자 검수 샘플'", 1)

click_marker = "        if(a==='template'){"
if html.count(click_marker) != 1:
    raise SystemExit(f'inspection sample click route marker mismatch: {html.count(click_marker)}')
click_actions = r'''        if(a==='inspection-sample-list'){if(state.role!=='admin')return;state.inspectionSampleReturn=state.detail?{...state.detail}:null;pushPageTransition(()=>{state.detail={type:'inspectionSamples',id:'all'};});return;}
        if(a==='inspection-sample-list-back'){if(state.role!=='admin')return;backPageTransition(()=>{state.detail={type:'templates',id:'all'};},{action:'inspection-sample-list'});return;}
        if(a==='inspection-sample-open'){if(state.role!=='admin')return;const roomNo=String(id||el.dataset.room||'');if(!ROOMS.some(room=>room.no===roomNo))return;state.inspectionSampleReturn=state.detail?{...state.detail}:null;pushPageTransition(()=>{state.detail={type:'inspectionSample',id:roomNo};});return;}
        if(a==='inspection-sample-back'){if(state.role!=='admin')return;const target=state.inspectionSampleReturn;backPageTransition(()=>{state.detail=target||{type:'inspectionSamples',id:'all'};state.inspectionSampleReturn=null;},{action:target?.type==='cleaning'?'inspection-sample-open':'inspection-sample-open',id});return;}
'''
html = html.replace(click_marker, click_actions + click_marker, 1)

# Add a current-template sample link to every actual admin inspection result without altering the submitted snapshot.
pay_marker = '      function renderPayDetail()'
if html.count(pay_marker) != 1:
    raise SystemExit(f'actual inspection sample link marker mismatch: {html.count(pay_marker)}')
inspection_wrapper = r'''      const renderInspectionDetailBeforeCurrentTemplateSample=renderInspectionDetail;
      renderInspectionDetail=function(no) {
        const output=renderInspectionDetailBeforeCurrentTemplateSample(no);
        if(state.role!=='admin')return output;
        return output+`<section class="card card-pad inspection-sample-entry"><div class="section-head"><div><h3>현재 템플릿 검수 샘플</h3><p class="audit-note">위 실제 제출은 제출 당시 스냅샷을 유지합니다. 현재 새 작업에 적용되는 전체 슬롯은 별도 읽기 전용 샘플에서 확인하세요.</p></div></div><div class="template-actions">${button(`${no}호 현재 검수 샘플 보기`,'inspection-sample-open','outline',`data-id="${no}"`)}</div></section>`;
      };

'''
html = html.replace(pay_marker, inspection_wrapper + pay_marker, 1)

api_methods = r'''          universalCheckoutTemplateAudit:()=>universalCheckoutTemplateAudit(),
          inspectionSampleCatalog:()=>inspectionSampleCatalog().map(sample=>({room:sample.room.no,typeId:sample.room.type,version:sample.template.version,count:sample.template.photos.length,required:sample.template.photos.filter(item=>item.required).length,universal:Object.fromEntries(UNIVERSAL_TEMPLATE_SLOT_IDS.map(id=>[id,sample.template.photos.filter(item=>item.id===id).length]))})),
          inspectionSampleContract:roomNo=>inspectionSampleContract(String(roomNo)),
          showInspectionSampleList:()=>{state.role='admin';state.detail={type:'inspectionSamples',id:'all'};render();return {count:inspectionSampleCatalog().length};},
          showInspectionSample:roomNo=>{const no=String(roomNo);if(!inspectionSampleForRoom(no))throw new Error('검수 샘플 객실을 찾을 수 없습니다.');state.role='admin';state.detail={type:'inspectionSample',id:no};render();return inspectionSampleContract(no);},
'''
api_marker = '          counts:()=>({reservations:'
if html.count(api_marker) != 1:
    raise SystemExit(f'inspection sample test API marker mismatch: {html.count(api_marker)}')
html = html.replace(api_marker, api_methods + api_marker, 1)

HTML.write_text(html, encoding='utf-8')

# Replace the policy's two structure sections and acceptance section so no per-room exception remains.
policy_path = Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md')
policy = policy_path.read_text(encoding='utf-8')
section5 = '''## 5. 타입별 고정 퇴실 청소 사진 슬롯\n\n모든 객실에는 복층 계단·복층·팬트리가 있으며, 세 공간은 네 객실 타입의 현재 퇴실 청소 템플릿에 각각 하나의 필수 사진 슬롯으로 고정한다. 같은 타입의 객실은 객실번호와 관계없이 완전히 같은 슬롯 ID·순서·구역·항목명·설명·필수 여부를 사용한다.\n\n| 타입 | 적용 객실 | 고정 공간 구성 | 전체 슬롯 | 필수 / 선택 |\n|---|---:|---|---:|---:|\n| 스탠다드 | 22실 | 원룸형 메인 공간 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1 | 13개 | 12 / 1 |\n| 프리미어 | 51실 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1 | 14개 | 13 / 1 |\n| 파셜 오션뷰 | 13실 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 복층 1 · 팬트리 1 | 14개 | 13 / 1 |\n| 패밀리 투룸 | 35실 | 침실 2 · 거실 1 · 주방 1 · 욕실 2 · 복층 계단 1 · 복층 1 · 팬트리 1 | 18개 | 17 / 1 |\n\n공통 필수 슬롯 ID는 `loft-stairs`, `loft-wide`, `pantry`다. 기존 파셜 오션뷰의 계단·팬트리 규칙은 이 표준 슬롯으로 통합하며 중복 생성하지 않는다. TV 켜짐 확인도 현재 퇴실 청소의 별도 필수 슬롯으로 유지한다.\n\n'''
section6 = '''## 6. 객실번호·타입·스냅샷 계약\n\n1. 객실번호로 현재 객실 마스터의 타입을 찾는다.\n2. 해당 타입의 고정 퇴실·연박·재청소 템플릿을 선택한다.\n3. 퇴실 청소라면 모든 타입에 복층 계단·복층·팬트리 필수 슬롯을 포함한다.\n4. 작업 생성 시 타입·단가·예상시간·슬롯 ID·순서·설명·필수 여부를 `templateSnapshot`으로 고정한다.\n5. 메이드는 작업 스냅샷으로 촬영하고 관리자는 제출 스냅샷으로 검수한다.\n6. 이후 템플릿이 변경되어도 이미 생성·수행·제출된 작업에는 소급하지 않는다.\n\n객실별 예외 레이아웃, 최소 공통 슬롯, 확인 완료·보류 상태는 사용하지 않는다. 같은 타입이면 모든 객실이 동일한 고정 구성을 사용한다.\n\n'''
section9 = '''## 9. 수용 기준\n\n- 객실 마스터 121실이 스탠다드 22·프리미어 51·파셜 오션뷰 13·패밀리 투룸 35실로 매칭된다.\n- 같은 타입의 모든 객실은 동일한 퇴실 청소 사진 슬롯 서명을 가진다.\n- 모든 객실의 현재 퇴실 청소 스냅샷에 `loft-stairs`, `loft-wide`, `pantry`가 각각 정확히 하나 있고 모두 필수다.\n- 타입별 현재 슬롯 수는 스탠다드 13·프리미어 14·파셜 오션뷰 14·패밀리 투룸 18개다.\n- 관리자 템플릿 목록·상세, 메이드 작업, 관리자 제출 검수는 같은 슬롯 계약을 사용한다.\n- 관리자에게 121개 객실별 현재 템플릿 검수 샘플을 제공하되 실제 제출·승인·급여·청소 상태·이벤트 원장을 변경하지 않는다.\n- 실제 과거 제출은 당시 `templateSnapshot`을 보존하고 새 복층·팬트리·TV 슬롯을 소급 추가하지 않는다.\n- 390·768·1440px에서 항목 누락·가로 넘침·콘솔·런타임 오류가 없다.\n'''
for number, replacement, next_number in [(5,section5,6),(6,section6,7)]:
    pattern = rf'## {number}\..*?(?=\n## {next_number}\.)'
    policy, count = re.subn(pattern, replacement.rstrip(), policy, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'policy section {number} replacement mismatch: {count}')
policy, count = re.subn(r'## 9\..*\Z', section9.rstrip() + '\n', policy, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'policy section 9 replacement mismatch: {count}')
policy_path.write_text(policy, encoding='utf-8')

new_policy = '''# 공통 복층·팬트리 템플릿과 관리자 검수 샘플 정책\n\n- 확정일: 2026-08-24\n- 적용 대상: 121개 객실의 현재 퇴실 청소 템플릿\n\n## 공통 공간\n\n모든 객실에 `복층 계단`, `복층`, `팬트리`가 있다. 세 공간은 객실 타입과 무관하게 현재 퇴실 청소의 필수 사진 슬롯으로 하나씩 생성한다.\n\n## 관리자 검수 샘플\n\n관리자는 `더보기 → 청소 템플릿 → 객실별 관리자 검수 샘플`에서 121개 객실을 각각 열 수 있다. 샘플은 객실번호를 타입에 매칭한 뒤 현재 템플릿으로 즉시 생성하며, 메이드 제출과 동일한 슬롯 ID·순서·구역·항목명·설명·필수 여부를 관리자 검수 형식으로 표시한다.\n\n샘플은 읽기 전용이며 실제 청소 상태, 제출, 승인·반려, 폭탄방 판단, 급여, 이벤트 원장을 만들거나 변경하지 않는다. 실제 검수 화면은 과거 제출 당시 스냅샷을 유지하고, 별도 버튼을 통해 현재 템플릿 샘플로 이동한다.\n\n## 이력 원칙\n\n현재 새 작업에는 복층 계단·복층·팬트리가 포함된다. 과거 제출에는 당시 존재하지 않던 슬롯을 소급 추가하지 않는다.\n'''
Path('DOCS/21_UNIVERSAL_LOFT_INSPECTION_SAMPLE_POLICY.md').write_text(new_policy, encoding='utf-8')

for path, appendix in [
    ('DOCS/19_TEMPLATE_PARITY_AUDIT.md', '''\n\n## 2026-08-24 추가 정정 · 모든 객실 공통 공간\n\n모든 객실에 복층 계단·복층·팬트리가 있다는 운영 확인을 반영했다. 세 공간은 네 타입의 현재 퇴실 청소 템플릿에 각각 하나의 필수 슬롯으로 고정하며 객실별 예외는 두지 않는다. 관리자에는 실제 원장과 분리된 121개 객실별 검수 샘플을 제공한다.\n'''),
    ('WIREFRAME/README.md', '''\n\n## 공통 복층·팬트리와 객실별 검수 샘플 (2026-08-24)\n\n모든 객실의 현재 퇴실 청소에 복층 계단·복층·팬트리 필수 슬롯을 하나씩 적용한다. 관리자는 청소 템플릿에서 121개 객실별 읽기 전용 검수 샘플을 열어 메이드 제출과 동일한 슬롯 형식을 확인할 수 있다.\n'''),
    ('WIREFRAME/QA.md', '''\n\n## 2026-08-24 · 공통 복층·팬트리와 관리자 검수 샘플\n\n- 121개 객실의 현재 퇴실 청소 스냅샷에 복층 계단·복층·팬트리가 각각 정확히 하나 있는지 전수 검사했다.\n- 타입별 고정 슬롯 수와 같은 타입 전체의 단일 서명을 확인했다.\n- 객실별 관리자 검수 샘플 121개가 읽기 전용으로 생성되는지 확인했다.\n- 샘플과 메이드 템플릿 슬롯 계약이 일치하고 승인·급여·이벤트 원장을 변경하지 않는지 확인했다.\n- 실제 관리자 검수에서 현재 템플릿 샘플로 이동할 수 있는지 확인했다.\n- 390·768·1440px와 콘솔·런타임 오류를 확인했다.\n'''),
]:
    file = Path(path)
    file.write_text(file.read_text(encoding='utf-8').rstrip() + appendix, encoding='utf-8')

checker = Path('scripts/check-workspace.mjs')
check_text = checker.read_text(encoding='utf-8')
check_marker = "console.log('Workspace check: passed');"
contracts = r'''for (const contract of [
  "UNIVERSAL_TEMPLATE_SLOT_IDS=Object.freeze(['loft-stairs','loft-wide','pantry'])",
  "id:'loft-stairs',zone:'복층 계단'",
  "id:'loft-wide',zone:'복층'",
  "id:'pantry',zone:'팬트리'",
  'function inspectionSampleForRoom(no)',
  'function inspectionSampleCatalog()',
  'function renderInspectionSampleList()',
  'function renderInspectionSample(no)',
  'data-inspection-sample-readonly="true"',
  "if(a==='inspection-sample-list')",
  "if(a==='inspection-sample-open')",
  '현재 타입 템플릿 검수 샘플',
  'inspectionSampleCatalog:()=>',
]) {
  if (!html.includes(contract)) throw new Error(`Universal loft/pantry inspection sample contract missing: ${contract}`);
}
for (const typeId of ['standard','premium','oceanPremium','oceanFamily']) {
  const start=html.indexOf(`${typeId}:[`,html.indexOf('const TYPE_PHOTO_GROUPS='));
  if(start<0)throw new Error(`Template group missing: ${typeId}`);
  const nextCandidates=['standard:[','premium:[','oceanPremium:[','oceanFamily:[','      };'].map(marker=>html.indexOf(marker,start+1)).filter(index=>index>start);
  const end=Math.min(...nextCandidates);
  const block=html.slice(start,end);
  for(const id of ['loft-stairs','loft-wide','pantry']){
    const count=(block.match(new RegExp(`id:'${id}'`,'g'))||[]).length;
    if(count!==1)throw new Error(`${typeId} ${id} expected once, found ${count}`);
  }
}
console.log('Universal loft/pantry inspection sample static contracts: passed');

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
manifest['version'] = '2026-08-24-universal-loft-inspection-samples'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = sha
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
