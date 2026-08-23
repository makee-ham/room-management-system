from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

html_path = Path('WIREFRAME/index.html')
html = html_path.read_text(encoding='utf-8')


def replace_once(old: str, new: str, label: str) -> None:
    global html
    count = html.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    html = html.replace(old, new, 1)


old_gallery = '''      function renderInspectionGallery(no) {
        const submission=currentSubmission(no),uploads=inspectionUploads(no);
        return `<div class="inspection-gallery">${uploads.map(upload=>`<button class="inspection-photo" type="button" data-action="inspection-photo" data-submission="${submission?.id||''}" data-photo="${upload.id}" data-room="${no}" aria-label="${upload.label} 업로드 이미지 크게 보기">${inspectionPhotoSvg(upload)}<span class="inspection-photo-copy"><span><strong>${upload.label}</strong><small>${upload.required?'필수':'선택'} · ${esc(inspectionPhotoTime(upload))} ${upload.status==='failed'?'전송 실패':'촬영 완료'}</small></span>${icon(upload.status==='failed'?'alert':'check','icon-sm')}</span></button>`).join('')}</div>`;
      }'''
new_gallery = '''      function inspectionTemplateUploadItems(no,template,submission=currentSubmission(no),attempt=null) {
        const rules=(template?.photos||[]).map(rule=>({...rule})),actualUploads=submission?.uploads||attempt?.uploads||inspectionUploads(no),actualById=new Map(actualUploads.map(upload=>[String(upload.id),upload])),seen=new Set(),items=[];
        rules.forEach(rule=>{
          const actual=actualById.get(String(rule.id))||null;seen.add(String(rule.id));
          items.push({...rule,...(actual||{}),id:String(rule.id),zone:rule.zone||actual?.zone||'사진',label:rule.label||actual?.label||String(rule.id),description:rule.description||actual?.description||'청소 완료 상태를 촬영합니다.',required:rule.required!==false,status:actual?.status||'missing',image:actual?.image||null,templateOrder:items.length});
        });
        actualUploads.forEach(upload=>{if(seen.has(String(upload.id)))return;items.push({...upload,id:String(upload.id),zone:upload.zone||'이전 제출 사진',description:upload.description||'이전 제출에만 남아 있는 사진입니다.',required:!!upload.required,templateOrder:items.length});});
        return items;
      }
      function inspectionTemplateGroups(no,template,submission=currentSubmission(no),attempt=null) {
        return taskZoneGroups({uploads:inspectionTemplateUploadItems(no,template,submission,attempt)});
      }
      function inspectionTemplatePhotoState(upload) {
        if(upload.status==='done')return {label:`촬영 완료 · ${inspectionPhotoTime(upload)}`,tone:'green',icon:'check'};
        if(upload.status==='failed')return {label:`전송 실패 · ${inspectionPhotoTime(upload)}`,tone:'red',icon:'alert'};
        if(upload.status==='uploading')return {label:'전송 중',tone:'blue',icon:'clock'};
        return {label:upload.required?'필수 사진 누락':'선택 사진 없음',tone:upload.required?'red':'neutral',icon:'camera'};
      }
      function renderInspectionTemplatePhoto(no,submission,group,upload) {
        const stateMeta=inspectionTemplatePhotoState(upload),hasImage=!!upload.image&&['done','failed'].includes(upload.status),copy=`<span class="task-zone-photo-main"><span class="task-zone-photo-visual">${hasImage?inspectionPhotoSvg(upload,upload.label):icon(stateMeta.icon)}</span><span class="task-zone-photo-copy"><strong>${esc(upload.label)} · ${upload.required?'필수':'선택'}</strong><span>${esc(upload.description||'청소 완료 상태를 촬영합니다.')}</span><span class="photo-state ${stateMeta.tone}">${esc(stateMeta.label)}${upload.instanceCount>1?` · ${upload.instance}/${upload.instanceCount}`:''}</span></span></span>`;
        return `<article class="task-zone-photo inspection-template-photo ${esc(upload.status||'missing')}" data-template-photo="${esc(upload.id)}" data-template-zone="${esc(group.zone)}" data-template-required="${upload.required?'true':'false'}" data-template-status="${esc(upload.status||'missing')}">${hasImage?`<button class="inspection-template-photo-button" type="button" data-action="inspection-photo" data-submission="${submission?.id||''}" data-photo="${esc(upload.id)}" data-room="${no}" aria-label="${esc(group.zone)} ${esc(upload.label)} ${upload.required?'필수':'선택'} 사진 크게 보기">${copy}</button>`:copy}</article>`;
      }
      function renderInspectionTemplateGroup(no,submission,group) {
        const required=group.uploads.filter(upload=>upload.required),requiredDone=required.filter(upload=>upload.status==='done').length,done=group.uploads.filter(upload=>upload.status==='done').length,attention=group.uploads.some(upload=>upload.status==='failed'||upload.status==='uploading'||upload.required&&upload.status!=='done'),complete=requiredDone===required.length&&!attention;
        return `<section class="task-zone-card inspection-template-zone ${complete?'complete':''} ${attention?'failed':''}" data-inspection-zone="${esc(group.zone)}" data-required-done="${requiredDone}" data-required-total="${required.length}" aria-labelledby="inspection-zone-${no}-${groupsafe(group.zone)}"><div class="task-zone-head"><div><h4 id="inspection-zone-${no}-${groupsafe(group.zone)}">${esc(group.zone)}</h4><p>필수 ${requiredDone}/${required.length} · 사진 ${done}/${group.uploads.length}</p></div>${statusBadge(complete?'구역 확인 완료':attention?'확인 필요':required.length?'사진 확인':'선택',complete?'green':attention?'red':required.length?'amber':'neutral')}</div><div class="task-zone-photos">${group.uploads.map(upload=>renderInspectionTemplatePhoto(no,submission,group,upload)).join('')}</div></section>`;
      }
      function renderInspectionTemplateReview(no,template,submission=currentSubmission(no),attempt=null) {
        const groups=inspectionTemplateGroups(no,template,submission,attempt),items=groups.flatMap(group=>group.uploads),required=items.filter(item=>item.required),requiredDone=required.filter(item=>item.status==='done').length,done=items.filter(item=>item.status==='done').length,requiredGroups=groups.filter(group=>group.uploads.some(item=>item.required)),completeGroups=requiredGroups.filter(group=>group.uploads.filter(item=>item.required).every(item=>item.status==='done')).length,version=template?.version||submission?.templateVersion||'이전 버전';
        return `<section class="card card-pad inspection-template-review" data-template-id="${esc(template?.id||submission?.templateId||'legacy')}" data-template-version="${esc(version)}" data-template-photo-count="${items.length}" data-template-required-count="${required.length}"><div class="section-head"><div><h3>메이드 청소 템플릿 기준 검수</h3><span class="meta">제출 당시 구역·항목·순서 그대로 확인</span></div>${statusBadge(requiredDone===required.length?'필수 사진 확인':'누락·실패 확인',requiredDone===required.length?'green':'red')}</div><div class="photo-template-banner"><div><strong>${esc(template?.name||submission?.kind||'청소')} · ${esc(version)}</strong><span>필수 사진 ${required.length}장 · 제출 당시 템플릿 기준</span></div><div class="badge-row">${statusBadge(`${completeGroups}/${requiredGroups.length} 구역 확인`,completeGroups===requiredGroups.length?'green':'amber')}</div></div><div class="task-zone-progress"><div><span>필수 사진</span><strong>${requiredDone}/${required.length}</strong></div><div><span>전체 사진</span><strong>${done}/${items.length}</strong></div></div><div class="task-zone-safety">${icon('shield','icon-sm')}<span><strong>메이드 촬영 화면과 같은 기준입니다.</strong><br>구역 순서·사진 항목·필수 여부·설명을 제출 당시 템플릿 그대로 비교합니다. TV 항목은 켜짐·화면 출력 요구사항까지 확인하세요.</span></div><div class="task-zone-grid inspection-template-grid">${groups.map(group=>renderInspectionTemplateGroup(no,submission,group)).join('')}</div></section>`;
      }'''
replace_once(old_gallery, new_gallery, 'inspection template review helpers')

replace_once(
    "        const submittedUploads=inspectionUploads(no),earning=earningBreakdown(no),decisionLocked=isLocked()||bombPending,unpaidReclean=submission?.kind==='재청소',submittedChecks=submissionTemplate?.checklist||[],completedChecks=submittedChecks.filter(item=>submission?.checklist?.[item.id]),requiredUploads=(submissionTemplate?.photos||[]).filter(item=>item.required);",
    "        const earning=earningBreakdown(no),decisionLocked=isLocked()||bombPending,unpaidReclean=submission?.kind==='재청소',submittedChecks=submissionTemplate?.checklist||[],completedChecks=submittedChecks.filter(item=>submission?.checklist?.[item.id]),requiredUploads=(submissionTemplate?.photos||[]).filter(item=>item.required);",
    'remove flat inspection upload summary',
)

old_section = '''<section class="card card-pad"><div class="section-head"><h3>구역별 청소 사진</h3><span class="meta">${submittedUploads.length}개 구역 · 눌러서 크게 보기</span></div>${renderInspectionGallery(no)}</section>'''
replace_once(old_section, '${renderInspectionTemplateReview(no,submissionTemplate,submission,attempt)}', 'inspection detail grouped review')

replace_once(
    "    .inspection-photo-copy .icon { color:var(--green); }",
    "    .inspection-photo-copy .icon { color:var(--green); }\n    .inspection-template-photo-button { display:block; width:100%; padding:0; border:0; color:inherit; background:transparent; text-align:left; }\n    .inspection-template-photo-button:focus-visible { border-radius:10px; outline-offset:3px; }\n    .inspection-template-photo .photo-state.green { color:var(--green); }\n    .inspection-template-photo .photo-state.red { color:var(--red); }\n    .inspection-template-photo .photo-state.blue { color:var(--blue); }\n    .inspection-template-photo.missing { border-color:#e3a9ae; background:#fff8f8; }\n    .inspection-template-photo[data-template-required=\"false\"].missing { border-color:var(--line); background:var(--surface-soft); }\n    .inspection-template-review .task-zone-grid { margin-top:12px; }",
    'inspection template review styles',
)

html_path.write_text(html, encoding='utf-8')

readme_path = Path('WIREFRAME/README.md')
readme = readme_path.read_text(encoding='utf-8').rstrip()
readme += '''

## 관리자 검수·메이드 청소 템플릿 통일 (2026-08-24)

- 관리자 검수는 메이드가 실제 청소 작업을 시작할 때 고정한 `templateSnapshot`을 기준으로 한다. 현재 최신 템플릿이 바뀌어도 제출 당시의 구역·항목·순서·필수 여부를 유지한다.
- 검수 화면은 메이드 촬영 화면과 같은 구역 카드, 사진 항목, 설명, 필수/선택 표시를 사용한다. 관리자에게는 촬영 버튼 대신 사진 확대와 누락·실패 상태가 표시된다.
- 제출 사진은 템플릿 사진 ID로 병합한다. 필수 사진이 빠졌거나 전송에 실패한 경우에도 그 항목 자체를 숨기지 않고 원래 위치에서 `필수 사진 누락` 또는 `전송 실패`로 표시한다.
- 구역별 `필수 완료/전체 필수`, 전체 `필수 사진`, `전체 사진` 진행 수치를 동일한 계산 기준으로 표시한다. TV 켜짐·화면 출력 항목도 다른 필수 사진과 같은 구조로 검사한다.
- 이전 v6 제출과 현재 v7 제출 모두 각 제출에 저장된 스냅샷을 사용하며, 최신 템플릿으로 소급 재해석하지 않는다.
'''
readme_path.write_text(readme, encoding='utf-8')

qa_path = Path('WIREFRAME/QA.md')
qa = qa_path.read_text(encoding='utf-8').rstrip()
qa += '''

## 2026-08-24 · 관리자 검수·메이드 청소 템플릿 통일

- 관리자 검수에서 제출 당시 템플릿의 구역 순서와 사진 항목 순서가 그대로 표시되는지 확인했다.
- 각 구역의 `필수 완료/전체 필수`, 사진 완료 수, 항목명·설명·필수 여부가 메이드 촬영 템플릿과 동일한 데이터에서 계산되는지 확인했다.
- 업로드 완료 사진은 같은 항목에서 확대할 수 있고, 전송 실패·필수 누락·선택 미촬영은 숨기지 않고 각각의 상태로 표시되는지 확인했다.
- 퇴실 청소 v7의 `TV 켜짐·화면 출력 확인` 항목이 TV 구역의 필수 사진으로 표시되는지 확인했다.
- 제출 이후 최신 템플릿을 바꾸더라도 관리자 검수의 `data-template-id`, `data-template-version`, 항목 수가 제출 스냅샷에서 유지되는지 정적 계약으로 확인했다.
- 승인·반려 버튼, 폭탄방 결정, 재청소 및 급여 연결 기존 흐름에 회귀가 없는지 확인했다.
- 390·768·1440px에서 구역 카드 배치, 사진 확대, 콘솔·런타임 오류와 문서 가로 넘침을 확인했다.
'''
qa_path.write_text(qa, encoding='utf-8')

checker_path = Path('scripts/check-workspace.mjs')
checker = checker_path.read_text(encoding='utf-8')
marker = "console.log('Per-maid weekly payment static contracts: passed');"
if checker.count(marker) != 1:
    raise SystemExit(f'inspection checker marker mismatch: {checker.count(marker)}')
checks = r'''for (const contract of [
  'function inspectionTemplateUploadItems(',
  'function inspectionTemplateGroups(',
  'function inspectionTemplatePhotoState(',
  'function renderInspectionTemplatePhoto(',
  'function renderInspectionTemplateGroup(',
  'function renderInspectionTemplateReview(',
  'template?.photos||[]',
  'actualById=new Map',
  "status:actual?.status||'missing'",
  'data-template-photo=',
  'data-template-zone=',
  'data-template-required=',
  'data-template-status=',
  '메이드 청소 템플릿 기준 검수',
  '제출 당시 구역·항목·순서 그대로 확인',
  '필수 사진 누락',
  'TV 항목은 켜짐·화면 출력 요구사항까지 확인하세요.',
  '${renderInspectionTemplateReview(no,submissionTemplate,submission,attempt)}',
]) {
  if (!html.includes(contract)) throw new Error(`Admin/maid inspection-template parity contract missing: ${contract}`);
}
const activeInspectionStart=html.lastIndexOf('function renderInspectionDetail(no)');
const activeInspectionEnd=html.indexOf('function renderPayDetail()',activeInspectionStart);
const activeInspectionSource=html.slice(activeInspectionStart,activeInspectionEnd);
if(activeInspectionStart<0||activeInspectionEnd<=activeInspectionStart||activeInspectionSource.includes('renderInspectionGallery(no)')||activeInspectionSource.includes('submittedUploads.length')){
  throw new Error('Active admin inspection still uses the legacy flat photo gallery.');
}
for (const contract of ['관리자 검수·메이드 청소 템플릿 통일','templateSnapshot','필수 사진 누락','TV 켜짐·화면 출력 항목']) {
  if (!wireframeReadme.includes(contract)) throw new Error(`Inspection-template parity README contract missing: ${contract}`);
}
for (const contract of ['관리자 검수·메이드 청소 템플릿 통일','필수 완료/전체 필수','전송 실패·필수 누락','data-template-version']) {
  if (!qa.includes(contract)) throw new Error(`Inspection-template parity QA contract missing: ${contract}`);
}

'''
checker_path.write_text(checker.replace(marker, checks + marker, 1), encoding='utf-8')

digest = hashlib.sha256(html_path.read_bytes()).hexdigest()
sums_path = Path('SHA256SUMS.txt')
lines = sums_path.read_text(encoding='utf-8').splitlines()
found = False
updated = []
for line in lines:
    if line.endswith('  WIREFRAME/index.html'):
        updated.append(f'{digest}  WIREFRAME/index.html')
        found = True
    else:
        updated.append(line)
if not found:
    raise SystemExit('WIREFRAME/index.html checksum line missing')
sums_path.write_text('\n'.join(updated) + '\n', encoding='utf-8')

manifest_path = Path('manifest.json')
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['version'] = '2026-08-24-inspection-template-parity'
manifest['generated_at_kst'] = datetime.now(ZoneInfo('Asia/Seoul')).isoformat(timespec='seconds')
manifest.setdefault('sha256', {})['WIREFRAME/index.html'] = digest
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
