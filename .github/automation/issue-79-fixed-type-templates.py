from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')
    html = html.replace(old, new, 1)


def regex_once(pattern: str, replacement: str, label: str, flags: int = 0) -> None:
    global html
    html, count = re.subn(pattern, replacement, html, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{label}: expected one match, found {count}')


# PR #78에서 임시로 넣었던 객실별 레이아웃 안내 제거.
html = html.replace("        root.querySelectorAll('.cleaning-section-body > .notice-warning').forEach(notice=>{if(/레이아웃 확인 보류|객실 프로필/.test(notice.textContent))notice.remove();});\n", '')
html = html.replace("        root.querySelectorAll('.photo-template-banner .badge').forEach(badge=>{if(/타입 템플릿|레이아웃 확인 보류|사진 표본 확인/.test(badge.textContent))badge.remove();});\n", '')

layout_contract = r'''      const TYPE_LAYOUT_PROFILES=Object.freeze({
        standard:Object.freeze({composition:'원룸형 메인 공간 1 · 주방 1 · 욕실 1',bedrooms:1,bathrooms:1,drains:1,pantry:false,source:'객실 타입 고정 구성'}),
        premium:Object.freeze({composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1',bedrooms:1,bathrooms:1,drains:1,pantry:false,source:'객실 타입 고정 구성'}),
        oceanPremium:Object.freeze({composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1',bedrooms:1,bathrooms:1,drains:1,pantry:true,source:'객실 타입 고정 구성'}),
        oceanFamily:Object.freeze({composition:'주방 1 · 거실 1 · 침실 2 · 욕실 2',bedrooms:2,bathrooms:2,drains:2,pantry:false,source:'객실 타입 고정 구성'})
      });
      function layoutProfileFor(roomNo,typeId=ROOMS.find(room=>room.no===roomNo)?.type||'standard') {
        const room=ROOMS.find(item=>item.no===String(roomNo)),resolvedType=room?.type||typeId||'standard',profile=TYPE_LAYOUT_PROFILES[resolvedType]||TYPE_LAYOUT_PROFILES.standard;
        return Object.freeze({...profile,typeId:resolvedType,fixedByType:true,status:'객실 타입 고정'});
      }
      function expandPhotoRules(roomNo,typeId,rules) {
        const profile=layoutProfileFor(roomNo,typeId);
        return rules.flatMap(rule=>{
          if(rule.conditionalBy&&!profile[rule.conditionalBy])return [];
          const count=rule.repeatBy?Math.max(1,Number(profile[rule.repeatBy])||1):1;
          return Array.from({length:count},(_,index)=>({...rule,id:count>1?`${rule.id}-${index+1}`:rule.id,label:count>1?`${rule.label} ${index+1}`:rule.label,instance:index+1,instanceCount:count}));
        });
      }
      const TYPE_PHOTO_GROUPS='''
regex_once(
    r"      const DEFAULT_LAYOUT_PROFILES=\{.*?      const TYPE_PHOTO_GROUPS=",
    layout_contract,
    'replace room-specific layouts with fixed type layouts',
    re.S,
)

helpers = r'''      function templateRooms(template) {
        return template?ROOMS.filter(room=>room.type===template.typeId):[];
      }
      function templateRepresentativeRoom(template) {
        return templateRooms(template)[0]?.no||null;
      }
      function templateFixedSnapshot(template) {
        const roomNo=templateRepresentativeRoom(template);
        return template&&roomNo?templateSnapshotFor(roomNo,template.name):null;
      }
      function photoSlotContract(items=[]) {
        return items.map((item,index)=>({order:index,id:String(item.id),zone:item.zone||'사진',label:item.label||String(item.id),description:item.description||'청소 완료 상태를 촬영합니다.',required:item.required!==false,multiple:!!item.multiple,repeatable:!!item.repeatable,instance:Number(item.instance)||1,instanceCount:Number(item.instanceCount)||1}));
      }
      function photoSlotContractSignature(items=[]) { return JSON.stringify(photoSlotContract(items)); }
      function templateSlotStats(template) {
        const snapshot=templateFixedSnapshot(template),photos=snapshot?.photos||template?.photos||[],required=photos.filter(item=>item.required).length,baseRequired=template?.photos?.filter(item=>item.required).length||0,baseTotal=template?.photos?.length||0;
        return {baseTotal,baseRequired,total:photos.length,required,optional:photos.length-required,roomCount:templateRooms(template).length};
      }
      function templateParityData(templateId,roomNo=null) {
        const template=templateById(String(templateId));if(!template)return null;
        const rooms=templateRooms(template),requested=roomNo==null?null:String(roomNo),selected=requested&&rooms.some(room=>room.no===requested)?requested:templateRepresentativeRoom(template),snapshot=selected?templateSnapshotFor(selected,template.name):templateFixedSnapshot(template),contract=photoSlotContract(snapshot?.photos||[]),profile=TYPE_LAYOUT_PROFILES[template.typeId]||TYPE_LAYOUT_PROFILES.standard;
        return {templateId:template.id,typeId:template.typeId,kindId:template.kindId,version:template.version,room:selected,roomCount:rooms.length,fixedByType:true,composition:profile.composition,baseRuleCount:template.photos.length,actualSlotCount:contract.length,requiredSlotCount:contract.filter(item=>item.required).length,optionalSlotCount:contract.filter(item=>!item.required).length,layoutProfile:{...profile},contract,signature:JSON.stringify(contract),stats:templateSlotStats(template)};
      }
      function typeTemplateParity(typeId,kind='퇴실 청소') {
        const rooms=ROOMS.filter(room=>room.type===String(typeId)),contracts=rooms.map(room=>({room:room.no,contract:photoSlotContract(templateSnapshotFor(room.no,kind)?.photos||[])})),signatures=[...new Set(contracts.map(item=>JSON.stringify(item.contract)))],profile=TYPE_LAYOUT_PROFILES[typeId]||null;
        return {typeId:String(typeId),kind,roomCount:rooms.length,composition:profile?.composition||'',slotCount:contracts[0]?.contract.length||0,signatures,allSame:signatures.length===1,rooms:contracts.map(item=>item.room)};
      }
'''
regex_once(
    r"      function templateRooms\(template\) \{.*?      function templateSnapshotFor",
    helpers + "      function templateSnapshotFor",
    'replace variable preview helpers with fixed type helpers',
    re.S,
)

list_function = r'''      function renderTemplateList() {
        const catalog=templateCatalog();
        const groups=Object.entries(ROOM_TYPES).map(([typeId,type])=>{
          const profile=TYPE_LAYOUT_PROFILES[typeId],rooms=ROOMS.filter(room=>room.type===typeId);
          const rows=TEMPLATE_KIND_ORDER.map(kindId=>{
            const template=catalog[`${typeId}:${kindId}`],stats=templateSlotStats(template);
            return `<button class="template-row" type="button" data-action="template-detail" data-id="${esc(template.id)}" data-template-id="${esc(template.id)}" aria-label="${esc(type.name)} ${esc(template.name)} 사진 템플릿 상세 보기"><span class="template-row-title"><strong>${esc(template.name)}</strong><span>청소요금 ${money(type.rate)} · 예상 ${template.minutes}분(데모)</span></span><span class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${kindId==='checkout'?statusBadge('타입 고정 슬롯','blue'):statusBadge('공통 사진 슬롯','neutral')}</span><span class="template-row-meta"><strong>메이드 고정 ${stats.total}개 슬롯</strong><span>필수 ${stats.required}개 · 선택 ${stats.optional}개 · 기본 규칙 ${stats.baseTotal}개</span></span>${icon('chevronRight','icon-sm')}</button>`;
          }).join('');
          return `<section class="card template-group"><div class="template-group-head"><div><h2>${esc(type.name)}</h2><p>${esc(profile.composition)} · 적용 ${rooms.length}실 · ${money(type.rate)}</p></div>${statusBadge('3개 활성','green')}</div>${rows}</section>`;
        }).join('');
        return renderCoach()+renderNetworkNotice()+detailHeader('청소 사진 템플릿','객실번호 → 타입 → 타입별 고정 구성 → 고정 사진 슬롯')+`<div class="template-page"><section class="card template-hero"><div class="template-hero-copy"><h2>같은 타입은 하나의 고정 템플릿을 사용합니다</h2><p>객실번호는 현재 객실 마스터에서 타입을 찾는 키이며, 같은 타입의 모든 객실은 동일한 공간 구성과 사진 슬롯을 사용합니다.</p></div><div class="template-hero-stat"><span>객실</span><strong>121실</strong></div><div class="template-hero-stat"><span>객실 타입</span><strong>4종</strong></div><div class="template-hero-stat"><span>활성 조합</span><strong>12개</strong></div></section><div class="notice notice-info"><div><strong>객실별 보정이나 슬롯 범위는 사용하지 않습니다.</strong><br>객실번호를 타입에 매칭한 뒤 해당 타입의 고정 공간 구성과 고정 슬롯 계약을 작업 스냅샷으로 저장합니다.</div></div>${groups}</div>`;
      }
'''
regex_once(
    r"      function renderTemplateList\(\) \{.*?\n      \}\n      function renderTemplateTimeline",
    list_function + "      function renderTemplateTimeline",
    'fixed type template list',
    re.S,
)

detail_function = r'''      function renderTemplateDetail(id,mode='view') {
        const template=templateById(id);
        if(!template)return renderTemplateList();
        const type=ROOM_TYPES[template.typeId],profile=TYPE_LAYOUT_PROFILES[template.typeId],rooms=templateRooms(template),snapshot=templateFixedSnapshot(template),fixedPhotos=snapshot?.photos||template.photos,required=fixedPhotos.filter(item=>item.required).length,optional=fixedPhotos.length-required,stats=templateSlotStats(template),evidence=PHOTO_TEMPLATE_EVIDENCE[template.typeId];
        if(mode==='edit')return renderCoach()+templateDetailHead(template,'edit')+`<form id="template-edit-form" class="card template-section template-edit-form"><div class="template-section-head"><div><h3>템플릿 수정</h3><p>${esc(type.name)} · ${esc(template.name)} · 현재 ${esc(template.version)} · 데모</p></div>${statusBadge('새 작업부터 적용','blue')}</div><div class="template-edit-time"><div class="field"><label for="template-minutes">예상시간 · 데모</label><input id="template-minutes" class="input-control" type="number" min="10" max="180" step="5" value="${template.minutes}" inputmode="numeric" required><small>10~180분, 5분 단위로 입력합니다.</small></div><div class="template-summary-item"><span>타입 고정 사진 슬롯</span><strong>${fixedPhotos.length}개 · 적용 객실 ${rooms.length}실</strong></div></div><div class="notice notice-warning"><div><strong>이 화면에서는 예상시간만 수정합니다.</strong><br>공간 구성과 사진 슬롯은 객실 타입별로 고정되어 있으며, 저장한 예상시간은 새 작업부터 적용됩니다. 기존 작업·제출은 당시 스냅샷을 유지합니다.</div></div><div class="template-actions">${button('수정 취소','template-cancel-edit','outline',`data-id="${esc(template.id)}"`)}${button('변경 내용 확인','template-review','primary',`data-id="${esc(template.id)}"`)}</div></form>`;
        const slotCards=fixedPhotos.map((item,index)=>`<article class="template-photo-item" data-template-fixed-slot="${esc(item.id)}" data-template-fixed-order="${index}" data-template-fixed-zone="${esc(item.zone||'사진')}" data-template-fixed-label="${esc(item.label)}" data-template-fixed-description="${esc(item.description||'청소 완료 상태를 촬영합니다.')}" data-template-fixed-required="${item.required?'true':'false'}"><span class="photo-slot-zone">${esc(item.zone||'사진')}</span><strong>${esc(item.label)}</strong><span>${esc(item.description||'청소 완료 상태를 촬영합니다.')}</span><span class="photo-slot-guide">${item.required?'필수 · 완료 전 제출 불가':'선택 · 추가 증빙'} · 한 슬롯 1장${item.instanceCount>1?` · ${item.instance}/${item.instanceCount}`:''}</span></article>`).join('');
        const sourceNote=template.kindId==='checkout'?`참고 사진 ${evidence.rooms.join('·')}호 ${evidence.photoCount}장은 촬영 항목을 정리하는 근거로만 사용했으며 객실별 다른 구조를 뜻하지 않습니다.`:`${template.name}는 현재 타입별 공통 데모 규칙이며 같은 타입의 모든 객실에 동일하게 적용됩니다.`;
        return renderCoach()+renderNetworkNotice()+templateDetailHead(template)+`<div class="template-page"><section class="card template-section"><div class="template-section-head"><div><h3>활성 버전</h3><p>${esc(type.name)} × ${esc(template.name)} · 청소요금 ${money(type.rate)} (8월 시트)</p></div><div class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${statusBadge('타입 고정 구성','blue')}</div></div><div class="template-summary"><div class="template-summary-item"><span>예상시간 · 데모</span><strong>${template.minutes}분</strong></div><div class="template-summary-item"><span>적용 객실</span><strong>${rooms.length}실</strong></div><div class="template-summary-item"><span>고정 사진 슬롯</span><strong>${fixedPhotos.length}개</strong></div><div class="template-summary-item"><span>필수 / 선택 슬롯</span><strong>${required} / ${optional}</strong></div></div></section><section class="card template-section"><div class="template-section-head"><div><h3>메이드 고정 촬영 슬롯</h3><p>같은 타입의 모든 객실과 관리자 검수가 동일한 슬롯 계약을 사용합니다.</p></div><div class="badge-row">${statusBadge('타입 내 동일','green')}${statusBadge('슬롯 구조 일치','green')}</div></div><div class="template-summary"><div class="template-summary-item"><span>객실 타입 고정 구성</span><strong>${esc(profile.composition)}</strong></div><div class="template-summary-item"><span>객실번호 역할</span><strong>타입 매칭 키</strong></div><div class="template-summary-item"><span>기본 규칙</span><strong>${stats.baseTotal}개</strong></div><div class="template-summary-item"><span>적용 결과</span><strong>${stats.total}개 고정 슬롯</strong></div></div><div class="notice notice-success" style="margin-top:14px"><div><strong>같은 타입이면 객실번호가 달라도 구성이 같습니다.</strong><br>객실별 선택기·레이아웃 보정·확인 보류 없이 이 고정 구성을 새 작업 스냅샷에 저장합니다.</div></div><div class="template-photo-grid" data-template-fixed-grid data-template-id="${esc(template.id)}" data-template-type="${esc(template.typeId)}" data-template-photo-count="${fixedPhotos.length}" style="margin-top:14px">${slotCards}</div><div class="template-evidence"><div class="template-evidence-row"><strong>타입 매칭</strong><span>현재 객실 마스터에서 ${rooms.length}실이 ${esc(type.name)}으로 연결됩니다.</span></div><div class="template-evidence-row"><strong>근거 범위</strong><span>${esc(sourceNote)}</span></div></div></section><div class="notice notice-warning"><div><strong>한 슬롯에는 현재 사진 1장만 유지됩니다.</strong><br>재촬영하면 기존 사진을 교체하고, 삭제하면 다시 미완료가 됩니다. TV 슬롯이 있으면 계정·QR·알림 없는 중립 화면의 전원·출력을 촬영합니다.</div></div>${renderTemplateTimeline(template)}<div class="template-actions">${button('예상시간 수정','template-edit','primary',`data-id="${esc(template.id)}"`)}</div></div>`;
      }
'''
regex_once(
    r"      function renderTemplateDetail\(id,mode='view'\) \{.*?\n      \}\n      function readTemplateChange",
    detail_function + "      function readTemplateChange",
    'fixed type template detail',
    re.S,
)

replace_once(
    "'role','maid-account','scenario','template-preview-room','room-filter'",
    "'role','maid-account','scenario','room-filter'",
    'remove template preview control registration',
)
regex_once(
    r"\n        if\(c==='template-preview-room'\)\{.*?return;\}",
    '',
    'remove template preview room change handler',
)

old_show_template = "          showTemplate:(templateId,roomNo=null)=>{const template=templateById(String(templateId));if(!template)throw new Error('템플릿을 찾을 수 없습니다.');if(roomNo){const no=String(roomNo);if(!templateRooms(template).some(room=>room.no===no))throw new Error('템플릿 타입과 객실이 일치하지 않습니다.');state.templatePreviewRooms={...(state.templatePreviewRooms||{}),[template.id]:no};}state.role='admin';state.detail={type:'template',id:template.id,mode:'view'};render();return templateParityData(template.id,roomNo);},\n          templateParityData:(templateId,roomNo=null)=>templateParityData(String(templateId),roomNo),"
new_show_template = "          showTemplate:(templateId,roomNo=null)=>{const template=templateById(String(templateId));if(!template)throw new Error('템플릿을 찾을 수 없습니다.');if(roomNo&&!templateRooms(template).some(room=>room.no===String(roomNo)))throw new Error('템플릿 타입과 객실이 일치하지 않습니다.');state.role='admin';state.detail={type:'template',id:template.id,mode:'view'};render();return templateParityData(template.id,roomNo);},\n          templateParityData:(templateId,roomNo=null)=>templateParityData(String(templateId),roomNo),\n          typeTemplateParity:(typeId,kind='퇴실 청소')=>typeTemplateParity(String(typeId),kind),"
replace_once(old_show_template, new_show_template, 'update fixed type template test API')

for forbidden in ['ROOM_LAYOUT_PROFILES','DEFAULT_LAYOUT_PROFILES','templatePreviewRoom','templatePreviewSnapshot','templateSlotRange','template-preview-room']:
    if forbidden in html:
        raise SystemExit(f'obsolete variable-layout contract remains in HTML: {forbidden}')

html_path.write_text(html, encoding='utf-8')

policy = '''# 객실 타입별 청소 사진 템플릿 정책

- 최초 확정일: 2026-08-16
- 사진 전용·TV 작동 증빙 확정일: 2026-08-18
- 타입 고정 구성 정정일: 2026-08-24
- 근거: 사용자 확정 운영 규칙, 2026년 8월 객실 마스터, 사용자 제공 `clean-template/` 참고 사진 123장
- 상태: 객실번호·타입·청소 사진 템플릿의 구현 정본

## 1. 최우선 결정

같은 객실 타입은 객실번호와 관계없이 공간 구성이 같다. 객실번호는 별도 레이아웃을 고르는 값이 아니라 현재 객실 마스터에서 객실 타입을 찾는 식별값이다. 새 청소 작업의 템플릿은 다음 순서로 결정한다.

`객실번호 → 객실 타입 → 타입별 고정 공간 구성 → 청소 유형별 고정 사진 슬롯 → 작업 스냅샷`

따라서 객실별 `ROOM_LAYOUT_PROFILES`, 사진 표본 객실과 미확인 객실의 구분, 최소 공통 슬롯, 레이아웃 확인 보류, 관리자 객실 선택기는 사용하지 않는다.

현재 메이드 수행·현장 완료·전체 제출은 체크리스트 없이 구역별 사진 슬롯만 사용한다. 이 범위에서는 `DOCS/FINAL_UX_AUDIT.md`와 `DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`의 오래된 체크리스트 또는 객실별 보정 요구보다 이 문서가 우선한다.

## 2. 객실번호와 타입 매칭

객실번호별 타입은 `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`와 와이어프레임의 121실 객실 마스터를 정본으로 사용한다.

| 코드 | 화면 타입 | 객실 수 | 정본 기본 청소요금 |
|---|---|---:|---:|
| `standard` | 스탠다드 | 22실 | 16,000원 |
| `premium` | 프리미어 | 51실 | 20,000원 |
| `oceanPremium` | 파셜 오션뷰 | 13실 | 20,000원 |
| `oceanFamily` | 패밀리 투룸 | 35실 | 30,000원 |
| 합계 | 4개 타입 | 121실 | — |

관리자가 객실 타입을 수정하면 이후 새 작업은 새 타입의 고정 구성·단가·사진 슬롯을 사용한다. 이미 생성·배정·수행·제출된 작업은 당시 타입과 템플릿 스냅샷을 유지한다.

## 3. 타입별 고정 공간 구성

| 타입 | 고정 공간 구성 | 퇴실 청소 고정 슬롯 | 필수 / 선택 |
|---|---|---:|---:|
| 스탠다드 | 원룸형 메인 공간 1 · 주방 1 · 욕실 1 | 10개 | 9 / 1 |
| 프리미어 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 | 11개 | 10 / 1 |
| 파셜 오션뷰 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1 | 13개 | 12 / 1 |
| 패밀리 투룸 | 주방 1 · 거실 1 · 침실 2 · 욕실 2 | 15개 | 14 / 1 |

패밀리 투룸의 침실·침실 수납·욕실·욕실 배수구 규칙은 각각 두 개의 슬롯으로 고정된다. 예를 들어 645호와 542호는 모두 패밀리 투룸이므로 같은 15개 슬롯 ID·순서·표시명·설명·필수 여부를 사용한다.

파셜 오션뷰의 계단과 팬트리는 기존 타입 템플릿의 공간 항목을 객실별 조건이 아니라 타입 고정 구성으로 정리한 것이다. 객실 마스터의 타입 정의 자체가 바뀌는 경우에만 타입 구성과 새 버전을 함께 수정한다.

## 4. 참고 사진 123장의 역할

참고 사진은 촬영해야 할 공간과 마감 항목을 정리하는 근거다. 객실마다 업로드된 사진 장수가 달랐다는 사실을 침실·욕실·배수구 수의 차이로 해석하지 않는다.

| 타입 | 참고 객실 | 참고 사진 수 |
|---|---|---:|
| 스탠다드 | 750호 | 11장 |
| 프리미어 | 651·540·455호 | 42장 |
| 파셜 오션뷰 | 639·641·536호 | 42장 |
| 패밀리 투룸 | 645·542호 | 28장 |
| 합계 | 9실 | 123장 |

참고 원본 파일·썸네일·파일명·로컬 경로·EXIF·해시는 앱과 저장소에 반입하지 않는다. 사진 수 차이는 촬영 누락, 추가 증빙, 촬영 각도 등 여러 이유로 생길 수 있으므로 타입 내부 구조 차이의 근거가 아니다.

## 5. 고정 사진 슬롯 계약

관리자 템플릿 상세, 메이드 작업, 관리자 검수는 다음 값을 같은 순서로 사용한다.

1. 슬롯 ID
2. 순서
3. 구역
4. 항목명
5. 촬영 설명
6. 필수·선택 여부
7. 반복 인스턴스 번호와 전체 수

한 슬롯에는 현재 사진 한 장만 유지한다. 재촬영은 기존 사진을 교체하고 삭제하면 슬롯이 다시 미완료가 된다. `multiple` 메타데이터가 남아 있더라도 한 슬롯에 여러 파일을 동시에 보존한다고 안내하지 않는다.

필수 슬롯이 비어 있거나 사진이 처리 중·실패 상태면 현장 완료와 전체 제출을 막는다. 선택 슬롯은 비어 있어도 제출할 수 있다.

## 6. TV 작동 증빙

네 타입의 새 퇴실 청소 `v7` 이상에는 `tv-on` 필수 슬롯을 정확히 하나 둔다. 표시 이름은 `TV 켜짐·화면 출력 확인`이다.

TV 전체와 켜진 화면이 한 장에 보여야 한다. 계정·프로필·QR·페어링 코드·알림·Wi-Fi 기기명·캐스트 화면·방송·영화·사람이 보이면 입력 선택·설정·음량·신호 없음 등 TV 자체의 중립 화면으로 바꾼다.

TV 안내는 버전 문자열이 아니라 제출 스냅샷에 `tv-on` 슬롯이 실제로 있는지로 결정한다. 과거 퇴실 청소 `v6`에는 TV 슬롯을 소급 추가하지 않는다.

## 7. 버전과 스냅샷

작업 생성 시 다음을 하나의 읽기 전용 스냅샷으로 고정한다.

- 객실번호와 당시 객실 타입
- 타입별 기본 청소요금
- 청소 유형과 활성 템플릿 버전
- 예상시간
- 타입별 고정 공간 구성
- 사진 슬롯 ID·순서·설명·필수 여부

관리자 검수는 현재 활성 템플릿을 다시 계산하지 않고 제출 당시 `templateSnapshot`을 사용한다. 이후 객실 타입이나 템플릿이 변경되어도 기존 작업·제출·검수 이력을 덮어쓰지 않는다.

## 8. 역할별 화면 계약

### 관리자

- `더보기 → 청소 템플릿`에서 4개 타입 × 퇴실·연박·재청소 12개 조합을 본다.
- 목록에서 객실 타입의 고정 공간 구성, 적용 객실 수, 고정 슬롯 수, 필수·선택 수를 본다.
- 상세에는 객실 선택기나 슬롯 범위를 두지 않고 타입의 고정 슬롯 전체를 표시한다.
- 검수에서는 메이드 제출 기준 슬롯 수와 관리자 검수 슬롯 수, 구조 일치 여부를 확인한다.
- 예상시간 변경은 새 버전과 새 작업에만 적용한다.

### 메이드

- 본인에게 통보된 작업의 읽기 전용 템플릿 스냅샷만 본다.
- 같은 타입이면 객실번호가 달라도 같은 슬롯 순서로 촬영한다.
- 별도 체크리스트 없이 필수·선택 사진 슬롯과 현재 업로드 상태를 본다.
- 참고 원본과 다른 객실의 제출 사진은 볼 수 없다.

## 9. 현재 구현의 한계

- 템플릿 편집 데모는 예상시간만 수정한다. 타입 공간 구성·사진 슬롯 추가·삭제·순서 변경·게시 승인 서버는 구현하지 않았다.
- 사진 선택은 현재 탭 메모리의 `blob:` 미리보기이며 실제 서버 전송·악성 파일 검사·오프라인 재전송·장기 보존·동시 편집·서버 권한 검사는 없다.
- 연박·재청소 규칙과 예상시간은 현재 데모 fixture다. 타입별 기본 청소요금은 운영 정본이다.
- 지원 모바일에서 `capture="environment"`가 실제 후면 카메라를 여는지는 실기기에서 별도 확인해야 한다.

## 10. 수용 기준

- 네 타입 각각에 고정 공간 구성과 고정 퇴실 청소 슬롯 계약이 하나씩 존재한다.
- 같은 타입의 모든 객실은 새 작업 생성 시 완전히 같은 슬롯 서명을 사용한다.
- 패밀리 투룸 35실은 모두 `주방 1 · 거실 1 · 침실 2 · 욕실 2`와 15개 슬롯을 사용한다.
- 관리자 목록과 상세에 객실별 슬롯 범위·객실 선택기·레이아웃 확인 보류가 없다.
- 메이드 작업 슬롯은 작업 스냅샷과, 관리자 검수 슬롯은 제출 스냅샷과 일치한다.
- 현재 퇴실 청소에는 TV 슬롯이 있고 과거 v6에는 소급되지 않는다.
- 390·768·1440px에서 가로 넘침과 콘솔·런타임 오류가 없다.
'''
Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md').write_text(policy, encoding='utf-8')

audit = '''# 객실 타입 고정 청소 템플릿 정정 감사 보고서

- 정정일: 2026-08-24
- 관련 작업: Issue #79
- 기준: 사용자 확정 운영 규칙, `DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md`, `WIREFRAME/index.html`
- 범위: 객실번호·타입 매칭, 관리자 템플릿, 메이드 작업, 관리자 검수

## 결론

PR #78은 참고 객실별 사진 수 차이를 실제 공간 구성 차이로 잘못 해석했다. 같은 타입 안에서도 침실·욕실·배수구·팬트리 수가 달라질 수 있다고 가정하여 객실별 레이아웃 프로필, 슬롯 범위, 관리자 객실 선택기, 확인 보류 112실을 만들었다.

운영 정본은 반대다. 같은 타입은 공간 구성이 모두 같으며 객실번호는 타입을 찾는 키다. 따라서 새 작업은 `객실번호 → 타입 → 타입별 고정 구성 → 고정 슬롯 → 스냅샷`으로 생성해야 한다.

## 잘못된 전제와 정정

| 기존 전제 | 판정 | 정정 |
|---|---|---|
| 645호는 15개, 542호는 11개 슬롯 | 오류 | 두 객실 모두 패밀리 투룸이므로 같은 15개 슬롯 |
| 참고 사진 9실만 구조 확인 완료 | 오류 | 사진은 촬영 항목 참고 자료이며 타입 구성은 운영 규칙으로 고정 |
| 나머지 112실은 최소 공통 슬롯 | 오류 | 121실 모두 객실번호에 매칭된 타입의 고정 슬롯 사용 |
| 관리자에서 같은 타입의 객실을 선택해 미리보기 | 불필요 | 타입당 고정 템플릿 하나만 표시 |
| 목록에 `11~15개` 슬롯 범위 표시 | 오류 | 패밀리 투룸은 고정 15개처럼 정확한 수 표시 |
| 팬트리는 일부 파셜 오션뷰 객실에만 조건부 적용 | 오류 | 기존 타입 구성 항목을 파셜 오션뷰 타입 전체의 고정 슬롯으로 적용 |

## 타입별 정본

| 타입 | 고정 구성 | 퇴실 청소 슬롯 | 적용 객실 |
|---|---|---:|---:|
| 스탠다드 | 원룸형 메인 공간 1 · 주방 1 · 욕실 1 | 10개 | 22실 |
| 프리미어 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 | 11개 | 51실 |
| 파셜 오션뷰 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1 | 13개 | 13실 |
| 패밀리 투룸 | 주방 1 · 거실 1 · 침실 2 · 욕실 2 | 15개 | 35실 |

## 유지한 올바른 계약

- 메이드 작업은 작업 생성 당시 `templateSnapshot`을 사용한다.
- 관리자 검수는 제출 당시 스냅샷을 사용하며 현재 템플릿으로 과거 제출을 덮지 않는다.
- 슬롯 ID·순서·구역·항목명·설명·필수 여부·반복 번호를 비교한다.
- 한 슬롯에는 현재 사진 한 장만 유지한다.
- 현재 퇴실 청소의 TV 필수 슬롯은 유지하고 과거 v6에는 소급하지 않는다.

## 제거한 화면·상태

- `ROOM_LAYOUT_PROFILES`
- 객실별 최소 공통 레이아웃
- `레이아웃 확인 완료 / 확인 보류`
- 관리자 템플릿의 객실 선택기
- 같은 타입 안의 실제 슬롯 최소~최대 범위
- 사진 장수로 공간 수를 추정하는 설명

## 검증 기준

- 네 타입에 속한 모든 객실을 순회해 타입별 슬롯 서명이 하나뿐인지 확인한다.
- 패밀리 투룸 645호와 542호가 모두 15개이며 완전히 같은 서명인지 확인한다.
- 관리자 목록·상세, 메이드 작업, 관리자 검수의 슬롯 수와 계약을 비교한다.
- 현재 TV 슬롯과 과거 v6 비소급을 확인한다.
- 반복 렌더링 내구 원장 불변과 390·768·1440px 반응형·콘솔 오류를 확인한다.

## 남은 한계

관리자는 아직 예상시간만 수정할 수 있다. 타입 구성이나 슬롯 자체를 운영 화면에서 편집하는 기능, 실제 서버 사진 업로드·권한·보존·동시 편집은 별도 구현 대상이다.
'''
Path('DOCS/19_TEMPLATE_PARITY_AUDIT.md').write_text(audit, encoding='utf-8')

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8')
readme_section = '''## 타입별 청소 사진 템플릿

객실번호는 현재 121실 객실 마스터에서 타입을 찾는 키입니다. 같은 타입이면 객실번호와 관계없이 공간 구성과 청소 사진 슬롯이 모두 같습니다. 새 작업은 `객실번호 → 타입 → 타입별 고정 구성 → 고정 사진 슬롯 → 작업 스냅샷` 순서로 생성합니다.

사용자 제공 `clean-template/`의 9객실·123장 참고 사진은 촬영 항목 문구를 정리하는 자료로만 사용합니다. 객실별 사진 장수 차이를 공간 구성 차이로 해석하지 않으며, 원본 파일·썸네일·경로·파일명은 앱과 저장소에 반입하지 않았습니다.

| 타입 | 고정 공간 구성 | 적용 객실 | 정본 기본 청소요금 | 퇴실 청소 고정 슬롯 |
|---|---|---:|---:|---:|
| 스탠다드 | 원룸형 메인 공간 1 · 주방 1 · 욕실 1 | 22실 | 16,000원 | 필수 9 + 선택 1 = 10 |
| 프리미어 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 | 51실 | 20,000원 | 필수 10 + 선택 1 = 11 |
| 파셜 오션뷰 | 침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1 | 13실 | 20,000원 | 필수 12 + 선택 1 = 13 |
| 패밀리 투룸 | 주방 1 · 거실 1 · 침실 2 · 욕실 2 | 35실 | 30,000원 | 필수 14 + 선택 1 = 15 |

패밀리 투룸 645호와 542호를 포함한 35실은 모두 같은 15개 슬롯을 사용합니다. 관리자 템플릿에는 객실 선택기나 슬롯 범위를 두지 않고 타입별 고정 구성·적용 객실 수·고정 슬롯 전체를 표시합니다.

네 타입의 새 퇴실 청소 `v7` 이상에는 `TV 켜짐·화면 출력 확인` 필수 슬롯이 하나씩 있습니다. TV 전체와 켜진 중립 화면을 촬영하고 계정·QR·알림·고객 정보가 보이지 않게 합니다. 과거 `v6` 작업·제출에는 TV 슬롯을 소급하지 않습니다.

메이드 작업은 작업 생성 당시 스냅샷, 관리자 검수는 제출 당시 스냅샷을 사용합니다. 각 슬롯에는 현재 사진 한 장만 유지하며 재촬영하면 교체되고 삭제하면 다시 미완료가 됩니다. 카메라·갤러리 이미지는 현재 탭 메모리의 `blob:` 미리보기 데모이고 실제 서버 업로드·보존은 연결하지 않았습니다.

'''
readme, count = re.subn(r"## 타입별 청소 사진 템플릿\n.*?\n## 청소 운영 흐름", readme_section + '## 청소 운영 흐름', readme, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'README template section: expected one match, found {count}')
readme = re.sub(
    r"- 타입별 사진 템플릿은 사진 확인 9객실에서.*",
    "- 타입별 사진 템플릿은 같은 타입의 모든 객실에 같은 고정 공간 구성과 슬롯 계약을 적용합니다. 객실번호는 타입 매칭에만 사용하며, 실제 이미지 서버 전송·자동분류·서버 버전 게시·영속 보존은 구현하지 않았습니다.",
    readme,
)
readme_path.write_text(readme, encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8')
qa = re.sub(r"\| 레이아웃 프로필 \|.*", "| 타입별 고정 구성 | 정적 확인 | `TYPE_LAYOUT_PROFILES`에 스탠다드 10, 프리미어 11, 파셜 오션뷰 13, 패밀리 투룸 15개 퇴실 청소 슬롯을 만드는 고정 공간 수 정의 확인 |", qa)
qa = re.sub(r"\| 미확인 객실 \|.*", "| 동일 타입 고정 계약 | 통과 | 같은 타입의 모든 객실이 같은 슬롯 서명을 사용하며 객실별 선택·최소 공통값·확인 보류 상태가 없음 |", qa)
qa = re.sub(r"현재 참고 표본은 객실 마스터 121실 중 9실이고,.*", "참고 표본 9실·123장은 촬영 항목의 근거일 뿐 객실별 구조 차이의 근거가 아니다. 공간 구성은 객실 타입별 운영 정본으로 고정하며 121실 모두 객실번호에 매칭된 타입 템플릿을 사용한다.", qa)
qa = re.sub(r"\| 타입별 최소 공통 수 \|.*", "| 타입별 고정 슬롯 수 | 통과 | 관리자 템플릿 목록에서 스탠다드 10, 프리미어 11, 파셜 오션뷰 13, 패밀리 투룸 15개 고정 슬롯 확인 |", qa)
qa = qa.replace('메이드 528호 프리미어 퇴실 청소 v5·레이아웃 확인 보류·최소 공통 촬영 슬롯을 체크와 분리해 보여 준 이전 화면 참고', '메이드 528호 프리미어 퇴실 청소 v5의 이전 촬영 화면 참고')
qa = re.sub(
    r"- 타입별 사진 템플릿은 9객실·123장 참고 표본에서.*",
    "- 타입별 사진 템플릿은 객실번호를 타입에 매칭한 뒤 같은 타입 전체에 동일한 고정 슬롯을 사용한다. 참고 9실·123장은 촬영 항목 문구의 근거이고 공간 수 차이의 근거가 아니다. 새 퇴실 청소 `v7`은 중립 화면의 `TV 켜짐·화면 출력 확인` 슬롯을 별도 필수 사진으로 사용하고 기존 `v6`에는 소급하지 않는다. 슬롯당 현재 사진은 한 장이며 실제 서버 전송·영속 보존은 아직 없다.",
    qa,
)
qa = qa.replace('- 관리자 템플릿 목록의 기본 규칙 수와 객실별 실제 슬롯 범위 분리 확인', '- 관리자 템플릿 목록에 타입별 고정 구성·적용 객실 수·정확한 고정 슬롯 수 표시 확인')
qa = qa.replace('- 패밀리 투룸 645호의 기본 11개 규칙이 메이드 실제 15개 슬롯으로 확장되고 관리자 미리보기와 완전 일치하는지 확인', '- 패밀리 투룸 645호와 542호가 모두 고정 15개 슬롯이며 슬롯 서명이 완전히 같은지 확인')
qa = qa.replace('- 542호 선택 시 11개 슬롯으로 다시 계산되고 선택 상태가 유지되는지 확인', '- 네 타입의 121실을 순회해 타입별 슬롯 서명이 각각 하나뿐인지 확인')
qa = qa.replace('- 390·768·1440px 가로 넘침과 콘솔·런타임 오류 확인', '- 관리자 고정 템플릿 상세와 검수 화면의 390·768·1440px 가로 넘침 및 콘솔·런타임 오류 확인')
qa_path.write_text(qa, encoding='utf-8')

# 오래된 인계서에 객실별 보정 문장이 남아 있으면 정정문으로 대체한다.
handoff_path = Path('DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md')
handoff = handoff_path.read_text(encoding='utf-8')
correction = '> 2026-08-24 타입 구성 정정: 객실번호는 타입 매칭에만 사용하며 같은 타입의 모든 객실은 동일한 공간 구성과 고정 사진 슬롯을 사용한다. 객실별 레이아웃 프로필·최소 공통 슬롯·확인 보류는 사용하지 않는다. 상세 정본은 `DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md`를 따른다.\n'
if correction not in handoff:
    marker = '> 2026-08-18 추가 운영 결정:'
    pos = handoff.find(marker)
    if pos >= 0:
        line_end = handoff.find('\n', pos)
        handoff = handoff[:line_end + 1] + '\n' + correction + handoff[line_end + 1:]
    else:
        handoff = correction + '\n' + handoff
filtered=[]
for line in handoff.splitlines():
    if any(token in line for token in ['ROOM_LAYOUT_PROFILES','레이아웃 확인 보류','나머지 112실','타입 기본 + 객실 레이아웃 보정']):
        if line.strip() == correction.strip():
            filtered.append(line)
        continue
    filtered.append(line)
handoff_path.write_text('\n'.join(filtered).rstrip()+'\n', encoding='utf-8')

checks_path = Path('scripts/check-workspace.mjs')
checks = checks_path.read_text(encoding='utf-8')
new_checks = r'''for (const contract of [
  'const TYPE_LAYOUT_PROFILES=Object.freeze({',
  "composition:'원룸형 메인 공간 1 · 주방 1 · 욕실 1'",
  "composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1'",
  "composition:'침실 1 · 거실 1 · 주방 1 · 욕실 1 · 복층 계단 1 · 팬트리 1'",
  "composition:'주방 1 · 거실 1 · 침실 2 · 욕실 2'",
  'function templateRepresentativeRoom(template)',
  'function templateFixedSnapshot(template)',
  'function photoSlotContract(items=[])',
  'function templateSlotStats(template)',
  'function typeTemplateParity(typeId,kind=\'퇴실 청소\')',
  'data-template-fixed-slot="${esc(item.id)}"',
  'data-template-fixed-grid',
  '메이드 고정 촬영 슬롯',
  '객실번호 → 타입 → 타입별 고정 구성 → 고정 사진 슬롯',
  '메이드 제출 기준 ${expectedItems.length}개 슬롯 · 관리자 검수 ${items.length}개 슬롯',
  'data-template-contract-match="${structureMatches?\'true\':\'false\'}"',
  "snapshot?.photos?.some(item=>item.id==='tv-on'||String(item.id).startsWith('tv-on-'))",
  '한 슬롯에는 현재 사진 1장만 유지됩니다.',
  'typeTemplateParity:(typeId,kind=\'퇴실 청소\')=>',
  'templateVersionAudit:roomNo=>',
]) {
  if (!html.includes(contract)) throw new Error(`Fixed type template contract missing: ${contract}`);
}
const templateDetailStart=html.indexOf("function renderTemplateDetail(id,mode='view')");
const templateDetailEnd=html.indexOf('function readTemplateChange',templateDetailStart);
const templateDetailSource=html.slice(templateDetailStart,templateDetailEnd);
if(templateDetailStart<0||templateDetailEnd<=templateDetailStart)throw new Error('Template detail source block not found.');
if(!templateDetailSource.includes('fixedPhotos.map((item,index)=>'))throw new Error('Admin template detail does not render fixed type slots.');
if(templateDetailSource.includes('roomSelector')||templateDetailSource.includes('previewRoomNo'))throw new Error('Admin template detail still contains room-specific preview logic.');
const inspectionReviewStart=html.indexOf('function renderInspectionTemplateReview');
const inspectionReviewEnd=html.indexOf('function openInspectionPhoto',inspectionReviewStart);
const inspectionReviewSource=html.slice(inspectionReviewStart,inspectionReviewEnd);
if(!inspectionReviewSource.includes('photoSlotContractSignature(expectedItems)===photoSlotContractSignature(items)'))throw new Error('Admin inspection does not verify the submitted slot contract.');
for(const removed of ['ROOM_LAYOUT_PROFILES','DEFAULT_LAYOUT_PROFILES','template-preview-room','templateSlotRange','레이아웃 확인 보류','최소 공통 슬롯','필수 촬영 구역 ${requiredUploads.length}개','여러 장 허용',"snapshot?.version==='v7'"]){
  if(html.includes(removed))throw new Error(`Obsolete or contradictory template contract remains: ${removed}`);
}
if(!html.includes("version:'v6'")||!html.includes("filter(item=>item.id!=='tv-on')"))throw new Error('Historical v6 snapshot preservation contract is missing.');
for(const [path,text] of [['DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md',typePhotoPolicy],['DOCS/19_TEMPLATE_PARITY_AUDIT.md',templateParityAudit],['WIREFRAME/README.md',wireframeReadme]]){
  for(const removed of ['ROOM_LAYOUT_PROFILES','레이아웃 확인 보류','나머지 112실','11~15개']){
    if(text.includes(removed))throw new Error(`${path} still contains obsolete variable-layout copy: ${removed}`);
  }
}
console.log('Fixed type template static contracts: passed');
'''
checks, count = re.subn(
    r"for \(const contract of \[\n  'function templateRooms\(template\)'.*?console\.log\('Maid/admin template parity static contracts: passed'\);\n",
    new_checks,
    checks,
    count=1,
    flags=re.S,
)
if count != 1:
    raise SystemExit(f'workspace parity checks: expected one match, found {count}')
checks_path.write_text(checks, encoding='utf-8')

# 현재 정본 문서에서 잘못된 객실별 보정 용어가 남지 않았는지 확인한다.
for path in [html_path, Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md'), Path('DOCS/19_TEMPLATE_PARITY_AUDIT.md'), readme_path]:
    text=path.read_text(encoding='utf-8')
    for token in ['ROOM_LAYOUT_PROFILES','레이아웃 확인 보류','나머지 112실','11~15개']:
        if token in text:
            raise SystemExit(f'{path}: obsolete term remains: {token}')

# 해시·manifest 갱신.
final_audit_path=Path('DOCS/FINAL_UX_AUDIT.md')
def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
final_hash=sha256(final_audit_path)
wireframe_hash=sha256(html_path)
Path('SHA256SUMS.txt').write_text(f'{final_hash}  DOCS/FINAL_UX_AUDIT.md\n{wireframe_hash}  WIREFRAME/index.html\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version']='2026-08-24-fixed-type-templates'
manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest['sha256']['DOCS/FINAL_UX_AUDIT.md']=final_hash
manifest['sha256']['WIREFRAME/index.html']=wireframe_hash
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

print('Applied fixed room-type template contracts.')
