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


helpers = r'''      function templateRooms(template) {
        return template?ROOMS.filter(room=>room.type===template.typeId):[];
      }
      function templateDefaultPreviewRoom(template) {
        const rooms=templateRooms(template),evidence=(PHOTO_TEMPLATE_EVIDENCE[template?.typeId]?.rooms||[]).map(String),verified=evidence.filter(no=>rooms.some(room=>room.no===no)),pool=verified.length?verified:rooms.map(room=>room.no);
        return pool.map(no=>({no,count:templateSnapshotFor(no,template.name)?.photos?.length||0})).sort((left,right)=>right.count-left.count||Number(left.no)-Number(right.no))[0]?.no||null;
      }
      function templatePreviewRoom(template) {
        const rooms=templateRooms(template),requested=state.templatePreviewRooms?.[template?.id];
        return rooms.some(room=>room.no===String(requested))?String(requested):templateDefaultPreviewRoom(template);
      }
      function templatePreviewSnapshot(template,roomNo=templatePreviewRoom(template)) {
        return template&&roomNo?templateSnapshotFor(String(roomNo),template.name):null;
      }
      function photoSlotContract(items=[]) {
        return items.map((item,index)=>({order:index,id:String(item.id),zone:item.zone||'사진',label:item.label||String(item.id),description:item.description||'청소 완료 상태를 촬영합니다.',required:item.required!==false,multiple:!!item.multiple,repeatable:!!item.repeatable,instance:Number(item.instance)||1,instanceCount:Number(item.instanceCount)||1}));
      }
      function photoSlotContractSignature(items=[]) { return JSON.stringify(photoSlotContract(items)); }
      function templateSlotStats(template) {
        const rooms=templateRooms(template),targets=template?.kindId==='checkout'?rooms:rooms.slice(0,1),snapshots=targets.map(room=>templatePreviewSnapshot(template,room.no)).filter(Boolean),totals=snapshots.map(snapshot=>snapshot.photos.length),required=snapshots.map(snapshot=>snapshot.photos.filter(item=>item.required).length),baseRequired=template?.photos?.filter(item=>item.required).length||0,baseTotal=template?.photos?.length||0;
        return {baseTotal,baseRequired,minTotal:totals.length?Math.min(...totals):baseTotal,maxTotal:totals.length?Math.max(...totals):baseTotal,minRequired:required.length?Math.min(...required):baseRequired,maxRequired:required.length?Math.max(...required):baseRequired};
      }
      function templateSlotRange(min,max) { return min===max?`${min}개`:`${min}~${max}개`; }
      function templateParityData(templateId,roomNo=null) {
        const template=templateById(String(templateId));if(!template)return null;
        const selected=roomNo&&templateRooms(template).some(room=>room.no===String(roomNo))?String(roomNo):templatePreviewRoom(template),snapshot=templatePreviewSnapshot(template,selected),contract=photoSlotContract(snapshot?.photos||[]),profile=snapshot?.layoutProfile||null,verified=!!ROOM_LAYOUT_PROFILES[selected];
        return {templateId:template.id,typeId:template.typeId,kindId:template.kindId,version:template.version,room:selected,verified,baseRuleCount:template.photos.length,actualSlotCount:contract.length,requiredSlotCount:contract.filter(item=>item.required).length,optionalSlotCount:contract.filter(item=>!item.required).length,layoutProfile:profile?{...profile}:null,contract,signature:JSON.stringify(contract),stats:templateSlotStats(template)};
      }
'''
replace_once(
    "      function templateById(id) { return templateCatalog()[id]||null; }\n",
    "      function templateById(id) { return templateCatalog()[id]||null; }\n" + helpers,
    'template parity helpers',
)

list_function = r'''      function renderTemplateList() {
        const catalog=templateCatalog();
        const groups=Object.entries(ROOM_TYPES).map(([typeId,type])=>{
          const rows=TEMPLATE_KIND_ORDER.map(kindId=>{
            const template=catalog[`${typeId}:${kindId}`],stats=templateSlotStats(template),actualRange=templateSlotRange(stats.minTotal,stats.maxTotal),requiredRange=templateSlotRange(stats.minRequired,stats.maxRequired);
            return `<button class="template-row" type="button" data-action="template-detail" data-id="${esc(template.id)}" data-template-id="${esc(template.id)}" aria-label="${esc(type.name)} ${esc(template.name)} 사진 템플릿 상세 보기"><span class="template-row-title"><strong>${esc(template.name)}</strong><span>청소요금 ${money(type.rate)} · 예상 ${template.minutes}분(데모)</span></span><span class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${kindId==='checkout'?statusBadge('객실별 확장','blue'):statusBadge('공통 사진 슬롯','neutral')}</span><span class="template-row-meta"><strong>메이드 실제 ${actualRange} 슬롯</strong><span>필수 ${requiredRange} · 기본 규칙 ${stats.baseTotal}개</span></span>${icon('chevronRight','icon-sm')}</button>`;
          }).join('');
          return `<section class="card template-group"><div class="template-group-head"><div><h2>${esc(type.name)}</h2><p>${money(type.rate)} · 8월 시트 정본 · 참고 ${PHOTO_TEMPLATE_EVIDENCE[typeId].rooms.join('·')}호 ${PHOTO_TEMPLATE_EVIDENCE[typeId].photoCount}장</p></div>${statusBadge('3개 활성','green')}</div>${rows}</section>`;
        }).join('');
        return renderCoach()+renderNetworkNotice()+detailHeader('청소 사진 템플릿','객실 타입 4종 × 퇴실·연박·재청소')+`<div class="template-page"><section class="card template-hero"><div class="template-hero-copy"><h2>메이드의 실제 사진 슬롯을 확인하세요</h2><p>기본 규칙을 객실 침실·욕실·배수구·팬트리 구조에 맞춰 펼친 결과를 관리자도 동일하게 봅니다.</p></div><div class="template-hero-stat"><span>분석 표본</span><strong>123장</strong></div><div class="template-hero-stat"><span>객실 타입</span><strong>4종</strong></div><div class="template-hero-stat"><span>활성 조합</span><strong>12개</strong></div></section><div class="notice notice-info"><div><strong>기본 규칙 수와 메이드 실제 슬롯 수는 다를 수 있습니다.</strong><br>침실별·욕실별·배수구별 규칙은 객실 레이아웃 수만큼 개별 슬롯으로 펼쳐집니다. 아래 숫자는 기본 규칙이 아니라 메이드 화면에 실제로 나타나는 슬롯 범위입니다.</div></div>${groups}</div>`;
      }
'''
regex_once(r"      function renderTemplateList\(\) \{.*?\n      \}\n      function renderTemplateTimeline", list_function + "      function renderTemplateTimeline", 'template list actual slot ranges', re.S)


detail_function = r'''      function renderTemplateDetail(id,mode='view') {
        const template=templateById(id);
        if(!template)return renderTemplateList();
        const type=ROOM_TYPES[template.typeId],stats=templateSlotStats(template),previewRoomNo=templatePreviewRoom(template),previewSnapshot=templatePreviewSnapshot(template,previewRoomNo),previewPhotos=previewSnapshot?.photos||template.photos,previewRequired=previewPhotos.filter(item=>item.required).length,previewOptional=previewPhotos.length-previewRequired,profile=previewSnapshot?.layoutProfile||{},verified=!!ROOM_LAYOUT_PROFILES[previewRoomNo],rooms=templateRooms(template),evidence=PHOTO_TEMPLATE_EVIDENCE[template.typeId];
        if(mode==='edit')return renderCoach()+templateDetailHead(template,'edit')+`<form id="template-edit-form" class="card template-section template-edit-form"><div class="template-section-head"><div><h3>템플릿 수정</h3><p>${esc(type.name)} · ${esc(template.name)} · 현재 ${esc(template.version)} · 데모</p></div>${statusBadge('새 작업부터 적용','blue')}</div><div class="template-edit-time"><div class="field"><label for="template-minutes">예상시간 · 데모</label><input id="template-minutes" class="input-control" type="number" min="10" max="180" step="5" value="${template.minutes}" inputmode="numeric" required><small>10~180분, 5분 단위로 입력합니다.</small></div><div class="template-summary-item"><span>사진 슬롯 계약</span><strong>기본 규칙 ${stats.baseTotal}개 · ${previewRoomNo}호 실제 ${previewPhotos.length}개</strong></div></div><div class="notice notice-warning"><div><strong>이 화면에서는 예상시간만 수정합니다.</strong><br>사진 항목 추가·삭제·순서와 객실 레이아웃 값은 현재 데모 편집 범위가 아닙니다. 사진 슬롯은 새 작업 생성 시 버전 스냅샷으로 고정됩니다.</div></div><div class="template-actions">${button('수정 취소','template-cancel-edit','outline',`data-id="${esc(template.id)}"`)}${button('변경 내용 확인','template-review','primary',`data-id="${esc(template.id)}"`)}</div></form>`;
        const roomSelector=template.kindId==='checkout'?`<div class="field"><label for="template-preview-room">메이드 실제 화면 미리보기 객실</label><select id="template-preview-room" class="select-control" data-control="template-preview-room" data-template="${esc(template.id)}">${rooms.map(room=>`<option value="${room.no}" ${room.no===previewRoomNo?'selected':''}>${room.no}호 · ${ROOM_LAYOUT_PROFILES[room.no]?'레이아웃 확인 완료':'레이아웃 확인 보류'}</option>`).join('')}</select><small>객실을 바꾸면 같은 기본 규칙을 해당 객실 구조만큼 펼친 실제 슬롯을 봅니다.</small></div>`:`<div class="notice notice-info"><div><strong>공통 사진 슬롯</strong><br>${esc(template.name)}는 현재 객실 레이아웃 반복 규칙을 사용하지 않아 같은 타입의 모든 객실에 동일한 슬롯이 적용됩니다.</div></div>`;
        const layoutLabel=template.kindId==='checkout'?`침실 ${profile.bedrooms||1} · 욕실 ${profile.bathrooms||1} · 배수구 ${profile.drains||1} · 팬트리 ${profile.pantry?'있음':'없음'}`:'객실별 반복 없음';
        const slotCards=previewPhotos.map((item,index)=>`<article class="template-photo-item" data-template-preview-slot="${esc(item.id)}" data-template-preview-order="${index}" data-template-preview-zone="${esc(item.zone||'사진')}" data-template-preview-label="${esc(item.label)}" data-template-preview-description="${esc(item.description||'청소 완료 상태를 촬영합니다.')}" data-template-preview-required="${item.required?'true':'false'}"><span class="photo-slot-zone">${esc(item.zone||'사진')}</span><strong>${esc(item.label)}</strong><span>${esc(item.description||'청소 완료 상태를 촬영합니다.')}</span><span class="photo-slot-guide">${item.required?'필수 · 완료 전 제출 불가':'선택 · 추가 증빙'} · 한 슬롯 1장${item.instanceCount>1?` · ${item.instance}/${item.instanceCount}`:''}</span></article>`).join('');
        return renderCoach()+renderNetworkNotice()+templateDetailHead(template)+`<div class="template-page"><section class="card template-section"><div class="template-section-head"><div><h3>활성 버전</h3><p>${esc(type.name)} × ${esc(template.name)} · 청소요금 ${money(type.rate)} (8월 시트)</p></div><div class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${statusBadge('사진 전용','blue')}</div></div><div class="template-summary"><div class="template-summary-item"><span>예상시간 · 데모</span><strong>${template.minutes}분</strong></div><div class="template-summary-item"><span>기본 규칙</span><strong>${stats.baseTotal}개</strong></div><div class="template-summary-item"><span>메이드 실제 슬롯</span><strong>${previewPhotos.length}개</strong></div><div class="template-summary-item"><span>필수 / 선택 슬롯</span><strong>${previewRequired} / ${previewOptional}</strong></div></div></section><section class="card template-section"><div class="template-section-head"><div><h3>메이드 실제 촬영 슬롯 미리보기</h3><p>관리자와 메이드가 동일한 객실별 확장 결과를 사용합니다.</p></div><div class="badge-row">${statusBadge('슬롯 구조 일치','green')}${template.kindId==='checkout'?statusBadge(verified?'레이아웃 확인 완료':'레이아웃 확인 보류',verified?'green':'amber'):statusBadge('공통 슬롯','neutral')}</div></div>${roomSelector}<div class="template-summary" style="margin-top:14px"><div class="template-summary-item"><span>미리보기 객실</span><strong>${previewRoomNo}호</strong></div><div class="template-summary-item"><span>레이아웃</span><strong>${esc(layoutLabel)}</strong></div><div class="template-summary-item"><span>근거 상태</span><strong>${esc(verified?(profile.source||'사진 확인 완료'):'최소 공통값 · 확인 보류')}</strong></div><div class="template-summary-item"><span>타입 전체 실제 슬롯</span><strong>${templateSlotRange(stats.minTotal,stats.maxTotal)}</strong></div></div><div class="notice ${verified?'notice-success':'notice-warning'}" style="margin-top:14px"><div><strong>${verified?'사진으로 확인한 객실 레이아웃입니다.':'레이아웃 확인 보류 객실입니다.'}</strong><br>${verified?'이 객실의 실제 침실·욕실·배수구 수를 반영했습니다.':'사진으로 확정하지 못해 침실 1·욕실 1·배수구 1의 최소 공통 슬롯을 사용합니다. 실제 서비스 전 확인이 필요합니다.'}</div></div><div class="template-photo-grid" data-template-preview-grid data-template-id="${esc(template.id)}" data-template-room="${previewRoomNo}" data-template-photo-count="${previewPhotos.length}" style="margin-top:14px">${slotCards}</div>${template.kindId==='checkout'?`<div class="template-evidence"><div class="template-evidence-row"><strong>사진 표본</strong><span>${evidence.rooms.join('·')}호 · ${evidence.photoCount}장 · ${esc(evidence.coverage)}</span></div><div class="template-evidence-row"><strong>기본 → 실제</strong><span>기본 규칙 ${stats.baseTotal}개를 ${previewRoomNo}호 레이아웃에 맞춰 ${previewPhotos.length}개 슬롯으로 확장했습니다.</span></div></div>`:''}</section><div class="notice notice-warning"><div><strong>한 슬롯에는 현재 사진 1장만 유지됩니다.</strong><br>재촬영하면 기존 사진을 교체하고, 삭제하면 다시 미완료가 됩니다. 연락처·얼굴·고객 물품·거울 속 사람은 제외하고 TV 슬롯이 있으면 중립 화면의 전원·출력을 촬영합니다.</div></div>${renderTemplateTimeline(template)}<div class="template-actions">${button('예상시간 수정','template-edit','primary',`data-id="${esc(template.id)}"`)}</div></div>`;
      }
'''
regex_once(r"      function renderTemplateDetail\(id,mode='view'\) \{.*?\n      \}\n      function readTemplateChange", detail_function + "      function readTemplateChange", 'template detail expanded preview', re.S)


inspection_function = r'''      function renderInspectionTemplateReview(no,template,submission=currentSubmission(no),attempt=null) {
        const groups=inspectionTemplateGroups(no,template,submission,attempt),items=groups.flatMap(group=>group.uploads),expectedItems=template?.photos||[],required=items.filter(item=>item.required),requiredDone=required.filter(item=>item.status==='done').length,done=items.filter(item=>item.status==='done').length,requiredGroups=groups.filter(group=>group.uploads.some(item=>item.required)),completeGroups=requiredGroups.filter(group=>group.uploads.filter(item=>item.required).every(item=>item.status==='done')).length,version=template?.version||submission?.templateVersion||'이전 버전',structureMatches=photoSlotContractSignature(expectedItems)===photoSlotContractSignature(items),tvRequired=expectedItems.some(item=>item.id==='tv-on'||String(item.id).startsWith('tv-on-'));
        const safety=tvRequired?'TV 슬롯은 켜짐·화면 출력과 계정·QR·알림 없는 중립 화면까지 확인하세요.':'이 제출 버전에는 TV 슬롯이 없을 수 있습니다. 현재 템플릿의 TV 요구사항을 과거 제출에 소급하지 않습니다.';
        return `<section class="card card-pad inspection-template-review" data-template-id="${esc(template?.id||submission?.templateId||'legacy')}" data-template-version="${esc(version)}" data-template-photo-count="${items.length}" data-template-required-count="${required.length}" data-template-contract-match="${structureMatches?'true':'false'}"><div class="section-head"><div><h3>메이드 청소 템플릿 기준 검수</h3><span class="meta">제출 당시 구역·항목·순서 그대로 확인</span></div><div class="badge-row">${statusBadge(structureMatches?'슬롯 구조 일치':'슬롯 구조 확인 필요',structureMatches?'green':'red')}${statusBadge(requiredDone===required.length?'필수 사진 확인':'누락·실패 확인',requiredDone===required.length?'green':'red')}</div></div><div class="photo-template-banner"><div><strong>${esc(template?.name||submission?.kind||'청소')} · ${esc(version)}</strong><span>메이드 제출 기준 ${expectedItems.length}개 슬롯 · 관리자 검수 ${items.length}개 슬롯</span></div><div class="badge-row">${statusBadge(`${completeGroups}/${requiredGroups.length} 구역 확인`,completeGroups===requiredGroups.length?'green':'amber')}</div></div><div class="task-zone-progress"><div><span>필수 사진 슬롯</span><strong>${requiredDone}/${required.length}</strong></div><div><span>전체 사진 슬롯</span><strong>${done}/${items.length}</strong></div></div><div class="task-zone-safety">${icon('shield','icon-sm')}<span><strong>메이드 촬영 화면과 같은 제출 스냅샷입니다.</strong><br>슬롯 ID·순서·구역·항목명·필수 여부·설명을 그대로 비교합니다. ${esc(safety)}</span></div>${structureMatches?'':`<div class="notice notice-danger"><div><strong>제출 스냅샷과 검수 슬롯 구조가 다릅니다.</strong><br>승인 전에 누락·추가 슬롯을 확인해야 합니다.</div></div>`}<div class="task-zone-grid inspection-template-grid">${groups.map(group=>renderInspectionTemplateGroup(no,submission,group)).join('')}</div></section>`;
      }
'''
regex_once(r"      function renderInspectionTemplateReview\(no,template,submission=currentSubmission\(no\),attempt=null\) \{.*?\n      \}\n      function openInspectionPhoto", inspection_function + "      function openInspectionPhoto", 'inspection slot parity', re.S)

replace_once(
    "        const tvSafety=snapshot?.version==='v7'?' TV는 켜고 계정·QR·알림 없는 기본 화면으로 촬영하세요.':'';",
    "        const tvSafety=snapshot?.photos?.some(item=>item.id==='tv-on'||String(item.id).startsWith('tv-on-'))?' TV는 켜고 계정·QR·알림 없는 기본 화면으로 촬영하세요.':'';",
    'TV guidance follows slot instead of version label',
)

for old,new,label in [
    ('필수 촬영 구역 ${requiredUploads.length}개','필수 사진 슬롯 ${requiredUploads.length}개','inspection slot count wording'),
    ('본인 담당 청소 중인 최신 촬영 구역만 열 수 있습니다.','본인 담당 청소 중인 최신 사진 슬롯만 열 수 있습니다.','latest photo slot wording'),
    ('필수 촬영 구역을 모두 완료하고 미전송 사진을 재시도하세요.','필수 사진 슬롯을 모두 완료하고 미전송 사진을 재시도하세요.','required photo slot wording'),
    ('이미지 파일만 촬영 구역에 넣을 수 있습니다.','이미지 파일만 사진 슬롯에 넣을 수 있습니다.','image slot wording'),
    (' 구역에 반영했습니다.',' 사진 슬롯에 반영했습니다.','captured slot wording'),
]:
    if old not in html:
        raise SystemExit(f'{label}: source text not found')
    html=html.replace(old,new)

replace_once(
    "const c=e.target.dataset.control;if(!c||!['role','maid-account','scenario','room-filter','room-type-filter','quick-reservation-type','reservation-room','maid-pay-filter','work-history-maid','task-photo-file','task-candle','room-issue-type','room-issue-files','bomb-room-files','complaint-type','conflict-step-v2','maid-deactivation-gate','assignment-maid','reservation-cancel-reason'].includes(c))return;",
    "const c=e.target.dataset.control;if(!c||!['role','maid-account','scenario','template-preview-room','room-filter','room-type-filter','quick-reservation-type','reservation-room','maid-pay-filter','work-history-maid','task-photo-file','task-candle','room-issue-type','room-issue-files','bomb-room-files','complaint-type','conflict-step-v2','maid-deactivation-gate','assignment-maid','reservation-cancel-reason'].includes(c))return;",
    'template preview room control registration',
)
replace_once(
    "        if(c==='room-filter'){state.roomFilter=e.target.value;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"room-filter\"]')?.focus());return;}",
    "        if(c==='template-preview-room'){const template=templateById(e.target.dataset.template),roomNo=String(e.target.value);if(!template||!templateRooms(template).some(room=>room.no===roomNo))return;state.templatePreviewRooms={...(state.templatePreviewRooms||{}),[template.id]:roomNo};render();requestAnimationFrame(()=>document.querySelector('[data-control=\"template-preview-room\"]')?.focus({preventScroll:true}));return;}\n        if(c==='room-filter'){state.roomFilter=e.target.value;render();requestAnimationFrame(()=>document.querySelector('[data-control=\"room-filter\"]')?.focus());return;}",
    'template preview room change handler',
)

api_insert = r'''          showTemplateList:()=>{state.role='admin';state.detail={type:'templates',id:'all'};render();return Object.values(templateCatalog()).map(template=>({id:template.id,...templateSlotStats(template)}));},
          showTemplate:(templateId,roomNo=null)=>{const template=templateById(String(templateId));if(!template)throw new Error('템플릿을 찾을 수 없습니다.');if(roomNo){const no=String(roomNo);if(!templateRooms(template).some(room=>room.no===no))throw new Error('템플릿 타입과 객실이 일치하지 않습니다.');state.templatePreviewRooms={...(state.templatePreviewRooms||{}),[template.id]:no};}state.role='admin';state.detail={type:'template',id:template.id,mode:'view'};render();return templateParityData(template.id,roomNo);},
          templateParityData:(templateId,roomNo=null)=>templateParityData(String(templateId),roomNo),
          maidTemplateParity:roomNo=>{const no=String(roomNo),task=taskState(no),snapshot=task.templateSnapshot||snapshotForAttempt(no,state.cleaningAttempts?.[task.attemptId]),expected=photoSlotContract(snapshot?.photos||[]),actual=photoSlotContract(task.uploads||[]);return {room:no,version:snapshot?.version||null,expected,actual,same:JSON.stringify(expected)===JSON.stringify(actual)};},
          inspectionTemplateParity:roomNo=>{const no=String(roomNo),submission=currentSubmission(no),attempt=submission?.attemptId?state.cleaningAttempts?.[submission.attemptId]:null,template=templateSnapshotForSubmission(no,submission,attempt),expected=photoSlotContract(template?.photos||[]),actual=photoSlotContract(inspectionTemplateUploadItems(no,template,submission,attempt));return {room:no,submissionId:submission?.id||null,version:template?.version||null,expected,actual,same:JSON.stringify(expected)===JSON.stringify(actual)};},
          showInspection:roomNo=>{const no=String(roomNo);state.role='admin';state.detail={type:'cleaning',id:no};render();return {room:no,job:state.jobs[no],submissionId:currentSubmission(no)?.id||null};},
          templateVersionAudit:roomNo=>{const no=String(roomNo),current=templateSnapshotFor(no,'퇴실 청소'),legacy=legacyCheckoutTemplateSnapshotFor(no);return {current:{version:current?.version||null,count:current?.photos?.length||0,tv:!!current?.photos?.some(item=>item.id==='tv-on')},legacy:{version:legacy?.version||null,count:legacy?.photos?.length||0,tv:!!legacy?.photos?.some(item=>item.id==='tv-on')}};},
'''
replace_once(
    "          setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},\n          counts:",
    "          setRoomFilter:filter=>{state.role='admin';state.adminView='rooms';state.detail=null;state.roomFilter=filter;render();return filteredRooms().map(room=>room.no);},\n" + api_insert + "          counts:",
    'template parity test API',
)

readme_path=Path('WIREFRAME/README.md')
readme=readme_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 메이드·관리자 사진 슬롯 정합성 (2026-08-24)\n\n- 관리자 템플릿 목록은 기본 규칙 수를 실제 사진 수처럼 표시하지 않고, 객실 레이아웃 확장 뒤 메이드 화면에 나타나는 실제 슬롯 범위를 표시한다.\n- 퇴실 청소 템플릿 상세에서 같은 타입의 실제 객실을 선택해 침실·욕실·배수구·팬트리 수가 반영된 슬롯 전체를 미리 본다.\n- 관리자 검수는 현재 템플릿이 아니라 제출 당시 `templateSnapshot`의 슬롯 ID·순서·구역·항목명·필수 여부·설명을 사용한다.\n- 각 슬롯은 현재 사진 1장만 유지하고 재촬영은 교체로 처리한다. `여러 장 허용`처럼 현재 구현과 모순되는 안내는 표시하지 않는다.\n- TV 안내는 버전 문자열이 아니라 실제 `tv-on` 슬롯 존재 여부를 따른다. 따라서 예상시간 수정으로 v8 이상이 되어도 TV 슬롯 안내가 사라지지 않고, 과거 v6에는 소급 표시되지 않는다.\n'''
readme_path.write_text(readme+'\n',encoding='utf-8')

qa_path=Path('WIREFRAME/QA.md')
qa=qa_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 2026-08-24 · 메이드 작업·관리자 템플릿·관리자 검수 사진 슬롯 정합성\n\n- 관리자 템플릿 목록의 기본 규칙 수와 객실별 실제 슬롯 범위 분리 확인\n- 패밀리 투룸 645호의 기본 11개 규칙이 메이드 실제 15개 슬롯으로 확장되고 관리자 미리보기와 완전 일치하는지 확인\n- 542호 선택 시 11개 슬롯으로 다시 계산되고 선택 상태가 유지되는지 확인\n- 슬롯 ID·순서·구역·항목명·필수 여부·설명·반복 인스턴스 계약 비교\n- 메이드 작업 `task.uploads`와 작업 생성 당시 `templateSnapshot.photos` 계약 일치 확인\n- 관리자 검수 슬롯과 제출 당시 메이드 스냅샷 계약 일치 확인\n- 현재 v7에는 TV 슬롯이 있고 과거 v6에는 TV 슬롯이 소급되지 않는지 확인\n- 버전 문자열이 아니라 TV 슬롯 존재 여부로 촬영·검수 안내가 결정되는지 확인\n- `필수 촬영 구역`을 슬롯 개수로 잘못 부르거나 `여러 장 허용`으로 오해시키는 문구 제거 확인\n- 390·768·1440px 가로 넘침과 콘솔·런타임 오류 확인\n'''
qa_path.write_text(qa+'\n',encoding='utf-8')

policy_path=Path('DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md')
policy=policy_path.read_text(encoding='utf-8').rstrip()+'''\n\n## 10. 2026-08-24 관리자·메이드 표시 정합성 보정\n\n- 관리자 템플릿 목록의 숫자는 타입 기본 규칙 수와 객실별 실제 슬롯 수를 구분한다.\n- 관리자 상세는 실제 객실을 선택해 `expandPhotoRules()`와 `templateSnapshotFor()`가 만든 메이드용 확장 슬롯 전체를 그대로 미리 본다.\n- 관리자 검수는 제출 당시 스냅샷과 검수 렌더의 슬롯 계약이 일치하는지 표시한다. 계약은 슬롯 ID·순서·구역·표시명·설명·필수 여부·반복 인스턴스로 구성한다.\n- `필수 촬영 구역 N개`처럼 슬롯 수와 구역 수를 혼용하지 않고 `필수 사진 슬롯 N개`로 표시한다.\n- 현재 구현 계약은 슬롯당 사진 1장이다. `multiple` 메타데이터가 있더라도 화면에서 여러 사진을 동시에 보존할 수 있는 것처럼 안내하지 않으며, 재촬영은 현재 사진을 교체한다.\n- TV 촬영·검수 안내는 `v7`이라는 문자열 비교가 아니라 제출 스냅샷에 `tv-on` 슬롯이 실제로 있는지로 결정한다. 새 버전 번호에서도 TV 슬롯을 유지하고 과거 v6에는 소급하지 않는다.\n'''
policy_path.write_text(policy+'\n',encoding='utf-8')

report_path=Path('DOCS/19_TEMPLATE_PARITY_AUDIT.md')
report_path.write_text('''# 메이드·관리자 청소 사진 템플릿 정합성 감사 보고서\n\n- 감사일: 2026-08-24\n- 기준: `DOCS/18_TYPE_PHOTO_TEMPLATE_POLICY.md`, `WIREFRAME/index.html`\n- 범위: 관리자 템플릿 관리, 메이드 작업 사진 슬롯, 관리자 제출 검수\n\n## 결론\n\n메이드 작업 화면의 항목이 많은 것이 정상이다. 퇴실 청소의 타입 기본 규칙은 객실별 침실·욕실·배수구·팬트리 수에 따라 여러 개의 실제 사진 슬롯으로 확장된다. 기존 관리자 템플릿 관리 화면은 확장 전 기본 규칙만 표시해 메이드 화면보다 항목이 적어 보였으며, 이것이 주된 불일치였다.\n\n관리자 제출 검수는 이미 제출 당시 `templateSnapshot`을 사용하고 있었으나, 화면에서 동일 개수와 계약 일치를 명시하지 않아 사용자가 정합성을 확인하기 어려웠다. 이번 보정으로 관리자 템플릿 미리보기와 검수 모두 메이드 슬롯 계약을 명시적으로 보여준다.\n\n## 발견 사항과 조치\n\n| 구분 | 발견 | 판정 | 조치 |\n|---|---|---|---|\n| 관리자 템플릿 상세 | 확장 전 `template.photos`만 표시 | 결함 | 실제 객실 선택과 객실별 확장 슬롯 전체 미리보기 추가 |\n| 관리자 템플릿 목록 | 기본 규칙 수를 `필수 사진 N장`으로 표시 | 결함 | 기본 규칙과 메이드 실제 슬롯 범위를 분리 표시 |\n| 관리자 검수 | 제출 스냅샷 사용은 정상이나 동일 구조 확인이 어려움 | 확인성 부족 | 메이드 제출 기준 슬롯 수, 관리자 검수 슬롯 수, 구조 일치 배지 추가 |\n| 개수 명칭 | 슬롯 수를 `필수 촬영 구역`으로 표현 | 결함 | `필수 사진 슬롯`으로 통일 |\n| TV 안내 | `version === v7`일 때만 메이드 안내 노출 | 결함 | 실제 `tv-on` 슬롯 존재 여부로 판단 |\n| 과거 v6 | 현재 v7과 달리 TV 슬롯 없음 | 의도된 차이 | 제출 당시 버전·슬롯을 보존하고 소급하지 않음 |\n| 다중 사진 문구 | 한 슬롯 1장 구조인데 `여러 장 허용`으로 안내 | 결함 | 한 슬롯 1장·재촬영 시 교체로 명확화 |\n| 미확인 112실 | 최소 공통 레이아웃만 사용 | 의도된 보류 | 관리자 미리보기에 `레이아웃 확인 보류`와 사유 노출 |\n| 연박·재청소 | 123장 표본 기반 퇴실 청소와 규칙 출처가 다름 | 의도된 차이 | 공통 데모 슬롯으로 구분 표시 |\n\n## 통일한 사진 슬롯 계약\n\n관리자 미리보기, 메이드 작업, 관리자 검수는 다음 값을 같은 순서로 사용한다.\n\n1. 슬롯 ID\n2. 순서\n3. 구역\n4. 항목명\n5. 촬영 설명\n6. 필수·선택 여부\n7. 반복 인스턴스 번호와 총수\n\n관리자 검수는 현재 활성 템플릿을 다시 계산하지 않고 제출 당시 스냅샷을 기준으로 한다. 따라서 템플릿 버전이나 객실 타입이 이후 변경되어도 과거 제출은 바뀌지 않는다.\n\n## 의도적으로 유지한 차이\n\n- 새 퇴실 청소 v7 이상: `TV 켜짐·화면 출력 확인` 필수 슬롯 포함\n- 과거 퇴실 청소 v6: TV 슬롯 미포함, 소급 추가 금지\n- 퇴실 청소: 123장 표본과 객실 레이아웃 보정 기반\n- 연박·재청소: 현재 데모 공통 규칙\n- 사진 확인 9실: 확인된 반복 수 사용\n- 나머지 112실: 침실 1·욕실 1·배수구 1 최소 공통값과 확인 보류 표시\n\n## 남은 한계\n\n- 관리자 편집 화면은 예상시간만 수정하며 사진 슬롯 추가·삭제·순서 변경과 레이아웃 마스터 편집은 지원하지 않는다.\n- 112실의 실제 레이아웃은 운영 전 별도 확인이 필요하다.\n- 사진은 현재 탭 메모리 데모이며 실제 서버 업로드·권한·보존·동시 편집 계약은 구현되지 않았다.\n''',encoding='utf-8')

checker_path=Path('scripts/check-workspace.mjs')
checker=checker_path.read_text(encoding='utf-8')
marker="console.log('Workspace check: passed');"
checks=r'''for (const contract of [
  'function templateRooms(template)',
  'function templatePreviewSnapshot(template,roomNo=templatePreviewRoom(template))',
  'function photoSlotContract(items=[])',
  'function templateSlotStats(template)',
  'data-control="template-preview-room"',
  'data-template-preview-slot="${esc(item.id)}"',
  '메이드 실제 촬영 슬롯 미리보기',
  '기본 규칙 수와 메이드 실제 슬롯 수는 다를 수 있습니다.',
  '메이드 제출 기준 ${expectedItems.length}개 슬롯 · 관리자 검수 ${items.length}개 슬롯',
  'data-template-contract-match="${structureMatches?\'true\':\'false\'}"',
  "snapshot?.photos?.some(item=>item.id==='tv-on'||String(item.id).startsWith('tv-on-'))",
  '한 슬롯에는 현재 사진 1장만 유지됩니다.',
  "if(c==='template-preview-room')",
  'templateVersionAudit:roomNo=>',
]) {
  if (!html.includes(contract)) throw new Error(`Template parity contract missing: ${contract}`);
}
const templateDetailStart=html.indexOf("function renderTemplateDetail(id,mode='view')");
const templateDetailEnd=html.indexOf('function readTemplateChange',templateDetailStart);
const templateDetailSource=html.slice(templateDetailStart,templateDetailEnd);
if(templateDetailStart<0||templateDetailEnd<=templateDetailStart)throw new Error('Template detail source block not found.');
if(!templateDetailSource.includes('previewPhotos.map((item,index)=>'))throw new Error('Admin template detail does not render expanded preview slots.');
if(templateDetailSource.includes('<div class="template-photo-grid">${template.photos.map'))throw new Error('Admin template detail still renders only base rules.');
const inspectionReviewStart=html.indexOf('function renderInspectionTemplateReview');
const inspectionReviewEnd=html.indexOf('function openInspectionPhoto',inspectionReviewStart);
const inspectionReviewSource=html.slice(inspectionReviewStart,inspectionReviewEnd);
if(!inspectionReviewSource.includes('photoSlotContractSignature(expectedItems)===photoSlotContractSignature(items)'))throw new Error('Admin inspection does not verify the submitted slot contract.');
for(const removed of ['필수 촬영 구역 ${requiredUploads.length}개','여러 장 허용',"snapshot?.version==='v7'"]){
  if(html.includes(removed))throw new Error(`Contradictory template copy or logic remains: ${removed}`);
}
if(!html.includes("version:'v6'")||!html.includes("filter(item=>item.id!=='tv-on')"))throw new Error('Historical v6 snapshot preservation contract is missing.');
console.log('Maid/admin template parity static contracts: passed');

'''
if checker.count(marker)!=1:raise SystemExit(f'workspace marker mismatch: {checker.count(marker)}')
checker_path.write_text(checker.replace(marker,checks+marker,1),encoding='utf-8')

html_path.write_text(html,encoding='utf-8')
digest=hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path=Path('SHA256SUMS.txt')
sums=sums_path.read_text(encoding='utf-8').splitlines()
sums_path.write_text('\n'.join(f'{digest}  WIREFRAME/index.html' if line.endswith('  WIREFRAME/index.html') else line for line in sums)+'\n',encoding='utf-8')
manifest_path=Path('manifest.json')
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version']='2026-08-24-template-parity-audit'
manifest['generated_at_kst']=datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256',{})['WIREFRAME/index.html']=digest
manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
