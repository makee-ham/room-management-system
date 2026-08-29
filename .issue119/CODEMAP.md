# Issue #119 code map

- source: `WIREFRAME/index.html`
- bytes: 1,167,773
- lines: 7,850
- generated from the issue branch for temporary implementation inspection

## 관리자 청소 화면: `renderHousekeeping`

matches: 0

## 메이드 루트 화면: `function renderMaid`

matches: 18

### occurrence 1 · line 3355

```html
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
  3331 |             ${queueCard('neutral','동기화','동기화·PIN·정산','2건','충돌 또는 확인 필요 사건','alerts','알림 보기')}
  3332 |           </div>
  3333 |           <div class="dashboard-layout">
  3334 |             <div><div class="section-head"><h2>객실 일별 현황</h2><span class="meta">총 7개 · 한국시간</span></div>${renderDateTools()}${renderRoomTable()}</div>
  3335 |             <aside class="rail" aria-label="보조 운영 큐">${renderDraftRail()}${renderInspectionRail()}${renderPayRail()}</aside>
  3336 |           </div>`;
  3337 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  3338 |       }
  3339 | 
  3340 |       function renderScenario13Controls() {
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
  3361 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">
  3362 |           ${settingCard('wallet','주급·지급',`지난주 상태 ${paymentWeekSummaryFor().label} · 메이드별 외부 송금 기록`,button('지급 상세','pay-detail','outline'))}
  3363 |           ${settingCard('settings','객실 타입 청소요금·예상시간','청소요금은 8월 시트 정본 · 예상시간은 데모',button('청소요금 보기','rates','outline'))}
  3364 |           ${settingCard('list','청소 템플릿',`초안·미리보기·게시 버전 · 현재 ${state.template}`,button('템플릿 관리','template','outline'))}
  3365 |           ${settingCard('bell','알림 상태',state.notificationsEnabled?'이 기기 알림 허용 데모':'권한 요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}
  3366 |           ${settingCard('shield','감사 이력','PIN 조회 사실·검수·단가·지급 수행자 기록',button('최근 이력 보기','audit-log','outline'))}
  3367 |           ${settingCard('lock','로그인·보안 상태','최초 변경·5회 실패·15분 잠금 데모',button('로그인 상태 보기','logout','outline'))}
  3368 |         </div>`;
  3369 |       }
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
```

### occurrence 2 · line 3386

```html
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
  3361 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">
  3362 |           ${settingCard('wallet','주급·지급',`지난주 상태 ${paymentWeekSummaryFor().label} · 메이드별 외부 송금 기록`,button('지급 상세','pay-detail','outline'))}
  3363 |           ${settingCard('settings','객실 타입 청소요금·예상시간','청소요금은 8월 시트 정본 · 예상시간은 데모',button('청소요금 보기','rates','outline'))}
  3364 |           ${settingCard('list','청소 템플릿',`초안·미리보기·게시 버전 · 현재 ${state.template}`,button('템플릿 관리','template','outline'))}
  3365 |           ${settingCard('bell','알림 상태',state.notificationsEnabled?'이 기기 알림 허용 데모':'권한 요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}
  3366 |           ${settingCard('shield','감사 이력','PIN 조회 사실·검수·단가·지급 수행자 기록',button('최근 이력 보기','audit-log','outline'))}
  3367 |           ${settingCard('lock','로그인·보안 상태','최초 변경·5회 실패·15분 잠금 데모',button('로그인 상태 보기','logout','outline'))}
  3368 |         </div>`;
  3369 |       }
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
  3421 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section class="card pay-hero"><span>이번 주 · ${weekRangeLabel(current.id)} · 데모 지급 이력</span><strong>${money(current.confirmed)}</strong><div class="pay-hero-grid"><div><span>검수 전 예상 포함</span><b>${money(current.confirmed+current.pending)}</b></div><div><span>검수 대기</span><b>${money(current.pending)}</b></div></div></section><div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong></div></div><div class="pay-week-toolbar"><div><h2>지금까지 주급 내역</h2><p>관리자와 같은 객실별 원장을 월요일–일요일 주차로 표시합니다.</p></div><button class="pay-week-picker" type="button" data-action="open-pay-calendar" data-context="maid-pay" aria-haspopup="dialog">${icon('calendar','icon-sm')}<span>${selectedLabel}</span>${icon('chevronRight','icon-sm')}</button></div><div class="maid-pay-history-head"><div><h2>${selectedWeek?'선택한 주차':'저장된 전체 주차'}</h2><p>${selectedWeek?weekRangeLabel(selectedWeek,true):`데모 ${weeks.length}주 · 최신순`}</p></div>${selectedWeek?button('전체 주차 보기','clear-maid-pay-week','outline'):''}</div><div class="maid-pay-history">${historyBody}</div><p class="maid-pay-footnote">객실 타입·기본 청소요금은 8월 운영 시트 정본이고, 인명·예약·과거 지급 이력은 기능 확인용 데모입니다. 컴플레인·벌점은 주급에서 자동 차감되지 않습니다.</p></div>`;
  3422 |       }
  3423 |       function renderMaidPay() {
  3424 |         return `<div class="settings-grid">${settingCard('wallet','이번 주 예상','승인 확정 52,000원 · 검수 대기 20,000원',button('상세 보기','demo-info','outline'))}${settingCard('check','지난주 지급 예정',paymentStatusFor('2026-08-03',signedInMaidId())==='PAID'?'138,000원 · 지급 완료':'138,000원 · 다음 월요일 외부 지급',button('지급 이력','pay-detail','outline'))}</div><div class="notice notice-warning" style="margin-top:14px">청소요금은 8월 운영 시트 정본입니다. 벌점·컴플레인은 평가 참고 기록이며 주급을 자동 차감하지 않습니다.</div>`;
  3425 |       }
  3426 | 
  3427 |       function renderMaidMore() {
  3428 |         return `<div class="settings-grid">${settingCard('user','내 정보','김민지1 · 데모 · 휴대폰 •••• 4821',button('정보 보기','demo-info','outline'))}${settingCard('bell','알림 권한',state.notificationsEnabled?'허용 · 앱 내부 알림 사용':'요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}${settingCard('lock','로그인 비밀번호','개인 숫자 6자리 이상 · 객실 PIN과 분리',button('변경 데모','demo-info','outline'))}</div>`;
  3429 |       }
  3430 | 
  3431 |       function renderDetail() {
  3432 |         if(!state.detail||!detailAllowedForRole(state.detail.type,state.role)){state.detail=null;return renderMain();}
  3433 |         if (state.detail.type==='templates') return renderTemplateList();
  3434 |         if (state.detail.type==='template') return renderTemplateDetail(state.detail.id,state.detail.mode||'view');
  3435 |         if (state.detail.type==='room') return renderRoomDetail(state.detail.id);
  3436 |         if (state.detail.type==='cleaning') return renderCleaningDetail(state.detail.id);
  3437 |         if (state.detail.type==='maid') return renderMaidDetail(state.detail.id);
  3438 |         if (state.detail.type==='complaint') return renderComplaintDetail();
  3439 |         if (state.detail.type==='pay') return renderPayDetail();
  3440 |         return '';
  3441 |       }
  3442 | 
  3443 |       function detailHeader(title,subtitle='') { return `<div class="detail-head"><button class="btn btn-ghost" type="button" data-action="back">${icon('chevronLeft','icon-sm')}목록</button><div class="detail-title"><h2>${title}</h2>${subtitle?`<p>${subtitle}</p>`:''}</div></div>`; }
  3444 | 
  3445 |       function renderRoomDetailLegacy(no) {
  3446 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room.type], p=roomPresentation(no);
  3447 |         let special='';
  3448 |         if (no==='350') special=`<section class="card card-pad"><div class="section-head"><h3>입실 준비 조건</h3>${statusBadge(p.status,p.tone)}</div><div class="info-grid"><div class="info-item"><span>청소 검수</span><strong>${state.jobs['350']==='approved'?'승인':'미검수'}</strong></div><div class="info-item"><span>촛불 전체 수량</span><strong>${state.candles['350']}개</strong></div><div class="info-item"><span>운영 상태</span><strong>정상</strong></div><div class="info-item"><span>미해결 차단</span><strong>${state.candles['350']>0?'촛불 회수 필요':'없음'}</strong></div></div>${state.candles['350']>0?`<div style="margin-top:12px">${button('촛불 1개 회수','recover-candle','danger',isLocked()?'disabled':'')}</div>`:`<div class="notice notice-success" style="margin:12px 0 0">${timeMinutes(state.time)>=timeMinutes('16:00')?'입실 시각 후 조건이 해소되어 예약상 투숙 중 전이를 한 번 기록했습니다.':'검수 승인·촛불 0·차단 없음으로 입실 준비가 완료됐습니다.'}</div>`}</section>`;
  3449 |         if (no==='332'&&state.conflict==='active') special=`<section class="card card-pad"><div class="section-head"><h3>레이트 체크아웃·청소 출입 충돌</h3>${statusBadge('즉시 조치','red','alert')}</div><p>11:00 자동 체크아웃 뒤 PIN이 조회되고 청소가 시작된 상태에서 체크아웃이 13:00으로 변경됐습니다. 단순 재잠금으로 해결할 수 없습니다.</p><div class="info-grid"><div class="info-item"><span>변경 전 / 후</span><strong>11:00 → 13:00</strong></div><div class="info-item"><span>PIN 조회</span><strong>11:06 · 김민지1</strong></div><div class="info-item"><span>수행 단계</span><strong>청소 중</strong></div><div class="info-item"><span>필요 항목</span><strong>조율 · 재계획 · PIN 교체</strong></div></div><div style="margin-top:12px">${button('영향 확인·충돌 해결','resolve-conflict','danger',isLocked()?'disabled':'')}</div></section>`;
  3450 |         if (no==='142') special=`<section class="card card-pad"><div class="section-head"><h3>현재 예약 · 연박 청소</h3>${statusBadge('예약상 투숙 중','neutral')}</div><p>연박 청소는 투숙객 요청이 있을 때만 만들며 예약 점유를 종료하거나 다음 예약 입실 준비로 사용하지 않습니다.</p>${state.stayoverCreated?`<div class="notice notice-success">연박 청소 배정 준비 작업이 관리자 내일 배정 목록에 추가됐습니다.</div>${button('오늘 운영 보기','go-today','outline')}`:button('연박 청소 생성','create-stayover','primary',isLocked()?'disabled':'')}</section>`;
  3451 |         return renderCoach()+renderNetworkNotice()+detailHeader(`${no}호 · 데모`,type.name)+`<div class="detail-grid"><div class="detail-stack">${special}<section class="card card-pad"><h3>예약·일정</h3><div class="info-grid"><div class="info-item"><span>체크인 일시</span><strong>${room.checkin}</strong></div><div class="info-item"><span>체크아웃 일시</span><strong>${room.checkout}</strong></div><div class="info-item"><span>청소요금 · 8월 시트</span><strong>${money(type.rate)}</strong></div><div class="info-item"><span>예상시간 · 데모</span><strong>${type.minutes}분</strong></div></div>${no==='211'?`<div class="notice notice-info" style="margin:12px 0 0"><strong>고객 이름</strong>&nbsp; 홍길동 (데모) · 관리자 예약 상세에서만 표시</div>`:''}</section></div><aside class="detail-stack"><section class="card card-pad"><h3>객실 사건 타임라인</h3>${renderTimeline(no)}</section><section class="card card-pad"><h3>객실 PIN</h3><p class="cell-sub">목록·알림·영속 저장소에는 원문을 두지 않습니다.</p><div class="pin-box"><span class="pin-value">••••</span>${button('변경 이력','demo-info','outline')}</div></section></aside></div>`;
  3452 |       }
  3453 | 
  3454 |       function renderTimeline(no) {
  3455 |         const base=[{title:`${no}호 상태 조회`,time:state.time,detail:'현재 상태 확인'},{title:'예약 일정 확인',time:'09:10',detail:'외부 예약은 별도 확인'},{title:'청소 일정 확인',time:'09:12',detail:'담당·수행·제출 내용 확인'}];
```

## 메이드 근무 가능 화면: `renderMaidSchedule`

matches: 4

### occurrence 1 · line 3244

```html
  3199 |           if(/활성 PIN lease/.test(label.textContent)){label.textContent='활성 PIN 조회';value.textContent=value.textContent.replace(/^[^·]+/,'1건');}
  3200 |         });
  3201 |         root.querySelectorAll('.choice').forEach(choice=>{
  3202 |           const title=choice.querySelector('strong'),copy=title?.nextElementSibling;if(!title||!copy)return;
  3203 |           if(title.textContent.includes('작업 재계획 완료')){title.textContent='청소 일정 변경 완료';copy.textContent=copy.textContent.replace('기존 수행 회차','진행 중 청소').replace('새 회차','새 청소');}
  3204 |           if(title.textContent.includes('필요 PIN 교체')){title.textContent='도어락 PIN 확인 완료';copy.textContent='기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.';}
  3205 |         });
  3206 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3207 |           if(/새 작업은 시트 청소요금을 스냅샷|기존 확정 이력은 당시 기록|새 담당 구간이 타임라인/.test(notice.textContent))notice.textContent=/담당/.test(notice.textContent)?'저장하면 담당 메이드에게 통보됩니다.':'변경한 청소요금은 새 작업부터 적용됩니다.';
  3208 |           if(/새 타입·엘리베이터는 이후 생성하는 작업/.test(notice.textContent))notice.textContent='변경한 정보는 새 작업부터 적용됩니다.';
  3209 |         });
  3210 |         const catalogCopy=root.querySelector('.catalog-summary-copy');
  3211 |         if(catalogCopy){const occupied=ROOMS.filter(room=>room.occupancy==='occupied').length,vacant=ROOMS.filter(room=>room.occupancy==='vacant'&&!roomIsOnHold(room.no)).length,hold=ROOMS.filter(room=>roomIsOnHold(room.no)).length;catalogCopy.querySelector('span').textContent=`투숙 중 ${occupied}개 · 공실 ${vacant}개 · 확인 필요 ${hold}개`;catalogCopy.insertAdjacentHTML('beforeend',infoTip('room-status','객실 상태','고객 배정 가능은 공실 중 청소·촛불·운영 조건까지 모두 준비된 객실에만 표시됩니다.'));}
  3212 |         const replacements=new Map([
  3213 |           ['객실별 청소 원장 합계','청소 내역 합계'],['객실별 청소 원장','객실별 청소 내역'],['주급 산출 원장','주급 청소 내역'],['현재 원장 예상','승인 시 예상'],['현재 원장','현재 합계'],['공통 원장 산식','청소 내역 합계'],['카드·예약표 공통 원장','예약 일정'],['다중 예약 원장','예약 일정'],['비공개 퇴실 청소 초안','퇴실 청소 미배정'],['잠근 지급 기록액','지급 기록액'],['잠근 지급액','지급 기록액'],['지급 진행 스냅샷','지급 진행 상태'],['원장 변동 · 정정 필요','금액 확인 필요'],['지급 대기(OPEN)','지급 대기'],['지급 진행(PAYING)','지급 진행'],['정산 확인 필요(CHECK)','정산 확인 필요'],['지급 완료(PAID)','지급 완료'],['송금하지 않음 · OPEN 복귀','송금하지 않음 · 지급 대기'],['OPEN 복귀','지급 대기 복귀'],['잠근 수익 ID','청소 내역'],['수익 ID','청소 내역'],['잠근 수익','청소 내역'],['포함 수익','청소 내역'],['미지급 수익','미지급 청소비'],['PIN lease','PIN 조회 기록'],['활성 lease','활성 PIN 조회'],['lease 영향','PIN 조회 영향'],['lease','PIN 조회'],['기존 수행 회차','기존 청소 작업'],['수행 회차','청소 작업'],['기존 회차','기존 청소 작업'],['기존 청소 작업는','기존 청소 작업은'],['새 회차 생성','새 청소 생성'],['중단 이력으로 보존','중단 처리하고'],['상태 재계산','상태 다시 확인'],['재계산 완료','확인 완료'],['재검증','다시 확인'],['충돌 종결','충돌 조치 완료'],['충돌 조치 완료·상태 다시 확인','조치 완료'],['종결 전','조치 완료 전'],['종결 시각','조치 시각'],['기존 사건 삭제 금지','현재 상태 변경 전 확인'],['체크아웃 투숙 상태 복원을 추가합니다.','체크아웃 시각까지 투숙 중으로 표시합니다.'],['투숙 상태 복원와','투숙 상태 복원과'],['점유 재개 보정','투숙 상태 복원'],['점유 보정','투숙 상태'],['점유 재개','투숙 상태 복원'],['보정 대기','변경 대기'],['보정 완료','변경 완료'],['보정 이벤트','변경 기록'],[' · 원문 미표시',''],['브라우저 시뮬레이션','데모 화면'],['정적 파일','데모 화면'],['fixture','데모 기록'],['fingerprint','확인값'],['예약 ID별','예약별'],['예약 ID','예약'],['예약 식별','예약'],['식별값','확인값'],['식별자','확인값'],['스냅샷','기준'],['수익 원장','청소 내역'],['폭탄방 요금 원장','폭탄방 청소비'],['산출 원장','청소 내역'],['원장','내역'],['시트 정본','기본 요금'],[' · 8월 시트',''],['제출 당시 기준','제출 당시 기준'],['제출 버전 고정','제출 내용'],['현재 활성 템플릿 상세','템플릿 상세'],[' · 상태 이력 보존',''],['메이드 지정 · 사유 입력 · 삭제/복구 이력','메이드별 기록 관리'],['PIN 원문을 제외한 예약·업무·지급 감사 이력','예약·업무·지급 변경 내역'],['시트 청소요금·데모 예상시간과 템플릿','청소요금과 사진 템플릿'],['로그인 비밀번호는 객실 PIN과 분리','계정과 로그인 설정'],['OPEN','지급 대기'],['PAYING','지급 진행'],['CHECK','정산 확인 필요'],['PAID','지급 완료']
  3214 |         ]);
  3215 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3216 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\bLEASE-[A-Za-z0-9-]+\b/g,'기존 PIN 조회').replace(/\s*·\s*데모/g,'').replace(/\(데모\)/g,'').replace(/투숙 상태 복원와/g,'투숙 상태 복원과').replace(/중단 처리하고하고/g,'중단 처리하고').replace(/기존 청소 작업는/g,'기존 청소 작업은').replace(/청소 작업를/g,'청소 작업을').replace(/데모 데모 기록/g,'데모 기록');node.nodeValue=value.trim()==='데모'?'':value;});
  3217 |         root.querySelectorAll('.info-item').forEach(item=>{const label=item.querySelector('span'),value=item.querySelector('strong');if(label?.textContent.trim()==='PIN 조회'&&value?.textContent.includes('기존 조회 종료'))label.textContent='PIN 조회 처리';});
  3218 |         root.querySelectorAll('.badge').forEach(badge=>{if(!badge.textContent.trim())badge.remove();});
  3219 |       }
  3220 | 
  3221 |       function renderTopbar() {
  3222 |         return `<header class="topbar">
  3223 |           <div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 2026.08.14 ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div>
  3224 |           <div class="topbar-actions">
  3225 |             <button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기">${icon('bell')}<span class="count-dot">${state.role==='admin'?6:3}</span></button>
  3226 |             <button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button>
  3227 |           </div>
  3228 |         </header>`;
  3229 |       }
  3230 | 
  3231 |       function renderBottomNav(nav) {
  3232 |         return `<nav class="bottom-nav" aria-label="모바일 주요 내비게이션">${nav.map(n=>`<button type="button" data-action="nav" data-view="${n.id}" ${currentView()===n.id&&!state.detail?'aria-current="page"':''}>${icon(n.icon)}<span>${n.mobileLabel||n.label}</span></button>`).join('')}</nav>`;
  3233 |       }
  3234 | 
  3235 |       function renderMain() {
  3236 |         if (!state.loggedIn) return renderLogin();
  3237 |         if (state.detail) return renderDetail();
  3238 |         if (state.role==='admin') {
  3239 |           if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();
  3240 |           if (state.adminView==='rooms') return renderRooms();
  3241 |           if (state.adminView==='maids') return renderMaids();
  3242 |           return renderAdminMore();
  3243 |         }
  3244 |         if (state.maidView==='schedule') return renderMaidSchedule();
  3245 |         if (state.maidView==='my') return renderMaidMy();
  3246 |         if (state.maidView==='done') return renderMaidDone();
  3247 |         if (state.maidView==='pay') return renderMaidPay();
  3248 |         return renderMaidMore();
  3249 |       }
  3250 | 
  3251 |       function renderCoach() {
  3252 |         if (state.role==='admin'||state.scenario===0) return '';
  3253 |         const cfg=SCENARIOS[state.scenario];
  3254 |         return `<aside class="scenario-coach"><span class="step">${state.scenario}</span><div><strong>${esc(cfg.title)}</strong><p>${esc(cfg.next)}</p></div>${button('시나리오 재설정','reset','outline')}</aside>`;
  3255 |       }
  3256 | 
  3257 |       function renderNetworkNotice() {
  3258 |         if (state.network==='online' && state.listMode!=='stale') return '';
  3259 |         return `<div class="notice notice-danger">${icon('sync')}<div><strong>${state.network==='offline'?'오프라인 · 읽기 전용':'오래된 데이터 · 변경할 수 없음'}</strong><br>마지막 연결 09:48. 인터넷에 연결한 뒤 다시 시도하세요.</div>${button('다시 시도','retry-network','outline')}</div>`;
  3260 |       }
  3261 | 
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
```

### occurrence 2 · line 4043

```html
  3998 |         const template=templateById(id);
  3999 |         if(!template)return renderTemplateList();
  4000 |         const type=ROOM_TYPES[template.typeId],profile=TYPE_LAYOUT_PROFILES[template.typeId],rooms=templateRooms(template),snapshot=templateFixedSnapshot(template),fixedPhotos=snapshot?.photos||template.photos,required=fixedPhotos.filter(item=>item.required).length,optional=fixedPhotos.length-required,stats=templateSlotStats(template),evidence=PHOTO_TEMPLATE_EVIDENCE[template.typeId];
  4001 |         if(mode==='edit')return renderCoach()+templateDetailHead(template,'edit')+`<form id="template-edit-form" class="card template-section template-edit-form"><div class="template-section-head"><div><h3>템플릿 수정</h3><p>${esc(type.name)} · ${esc(template.name)} · 현재 ${esc(template.version)} · 데모</p></div>${statusBadge('새 작업부터 적용','blue')}</div><div class="template-edit-time"><div class="field"><label for="template-minutes">예상시간 · 데모</label><input id="template-minutes" class="input-control" type="number" min="10" max="180" step="5" value="${template.minutes}" inputmode="numeric" required><small>10~180분, 5분 단위로 입력합니다.</small></div><div class="template-summary-item"><span>타입 고정 사진 슬롯</span><strong>${fixedPhotos.length}개 · 적용 객실 ${rooms.length}실</strong></div></div><div class="notice notice-warning"><div><strong>이 화면에서는 예상시간만 수정합니다.</strong><br>공간 구성과 사진 슬롯은 객실 타입별로 고정되어 있으며, 저장한 예상시간은 새 작업부터 적용됩니다. 기존 작업·제출은 당시 스냅샷을 유지합니다.</div></div><div class="template-actions">${button('수정 취소','template-cancel-edit','outline',`data-id="${esc(template.id)}"`)}${button('변경 내용 확인','template-review','primary',`data-id="${esc(template.id)}"`)}</div></form>`;
  4002 |         const slotCards=fixedPhotos.map((item,index)=>`<article class="template-photo-item" data-template-fixed-slot="${esc(item.id)}" data-template-fixed-order="${index}" data-template-fixed-zone="${esc(item.zone||'사진')}" data-template-fixed-label="${esc(item.label)}" data-template-fixed-description="${esc(item.description||'청소 완료 상태를 촬영합니다.')}" data-template-fixed-required="${item.required?'true':'false'}" data-template-max-photos="${photoUploadLimit(item)}"><span class="photo-slot-zone">${esc(item.zone||'사진')}</span><strong>${esc(item.label)}</strong><span class="photo-slot-guide">${photoUploadLimit(item)>1?`최대 ${photoUploadLimit(item)}장`:'1장 이상'}${item.instanceCount>1?` · ${item.instance}/${item.instanceCount}`:''}</span></article>`).join('');
  4003 |         const sourceNote=template.kindId==='checkout'?`참고 사진 ${evidence.rooms.join('·')}호 ${evidence.photoCount}장은 촬영 항목을 정리하는 근거로만 사용했으며 객실별 다른 구조를 뜻하지 않습니다.`:`${template.name}는 현재 타입별 공통 데모 규칙이며 같은 타입의 모든 객실에 동일하게 적용됩니다.`;
  4004 |         return renderCoach()+renderNetworkNotice()+templateDetailHead(template)+`<div class="template-page"><section class="card template-section"><div class="template-section-head"><div><h3>활성 버전</h3><p>${esc(type.name)} × ${esc(template.name)} · 청소요금 ${money(type.rate)} (8월 시트)</p></div><div class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${statusBadge('타입 고정 구성','blue')}</div></div><div class="template-summary"><div class="template-summary-item"><span>예상시간 · 데모</span><strong>${template.minutes}분</strong></div><div class="template-summary-item"><span>적용 객실</span><strong>${rooms.length}실</strong></div><div class="template-summary-item"><span>고정 사진 슬롯</span><strong>${fixedPhotos.length}개</strong></div><div class="template-summary-item"><span>인증 / 기타 슬롯</span><strong>${required} / ${optional}</strong></div></div></section><section class="card template-section"><div class="template-section-head"><div><h3>메이드 고정 촬영 슬롯</h3><p>같은 타입의 모든 객실과 관리자 검수가 동일한 슬롯 계약을 사용합니다.</p></div><div class="badge-row">${statusBadge('타입 내 동일','green')}${statusBadge('슬롯 구조 일치','green')}</div></div><div class="template-summary"><div class="template-summary-item"><span>객실 타입 고정 구성</span><strong>${esc(profile.composition)}</strong></div><div class="template-summary-item"><span>객실번호 역할</span><strong>타입 매칭 키</strong></div><div class="template-summary-item"><span>기본 규칙</span><strong>${stats.baseTotal}개</strong></div><div class="template-summary-item"><span>적용 결과</span><strong>${stats.total}개 고정 슬롯</strong></div></div><div class="notice notice-success" style="margin-top:14px"><div><strong>같은 타입이면 객실번호가 달라도 구성이 같습니다.</strong><br>객실별 선택기·레이아웃 보정·확인 보류 없이 이 고정 구성을 새 작업 스냅샷에 저장합니다.</div></div><div class="template-photo-grid" data-template-fixed-grid data-template-id="${esc(template.id)}" data-template-type="${esc(template.typeId)}" data-template-photo-count="${fixedPhotos.length}" style="margin-top:14px">${slotCards}</div><div class="template-evidence"><div class="template-evidence-row"><strong>타입 매칭</strong><span>현재 객실 마스터에서 ${rooms.length}실이 ${esc(type.name)}으로 연결됩니다.</span></div><div class="template-evidence-row"><strong>근거 범위</strong><span>${esc(sourceNote)}</span></div></div></section><div class="notice notice-warning"><div><strong>일반 슬롯은 1장, 기타 슬롯은 최대 10장을 유지합니다.</strong><br>일반 슬롯은 재촬영 시 기존 사진을 교체하고, 기타 슬롯은 각 사진을 따로 추가·삭제합니다. TV 슬롯이 있으면 계정·QR·알림 없는 중립 화면의 전원·출력을 촬영합니다.</div></div>${renderTemplateTimeline(template)}<div class="template-actions">${button('예상시간 수정','template-edit','primary',`data-id="${esc(template.id)}"`)}</div></div>`;
  4005 |       }
  4006 |       function readTemplateChange(id) {
  4007 |         const template=templateById(id),input=document.getElementById('template-minutes');
  4008 |         if(!template||!input) return null;
  4009 |         const minutes=Number(input.value);
  4010 |         if(!Number.isInteger(minutes)||minutes<10||minutes>180){toast('예상시간은 10분부터 180분 사이로 입력하세요.','error');input.focus();return null;}
  4011 |         return {id,minutes};
  4012 |       }
  4013 |       function openTemplateReview(id) {
  4014 |         const template=templateById(id),change=readTemplateChange(id);if(!template||!change)return;
  4015 |         pendingTemplateChange=change;rememberCurrentHistoryRoute();
  4016 |         const nextVersion=`v${Number(template.version.replace(/\D/g,''))+1}`;
  4017 |         showModal({title:'템플릿 변경 내용 확인',subtitle:`${ROOM_TYPES[template.typeId].name} · ${template.name} · 데모`,body:`<div class="template-review-summary"><div class="template-review-row"><span>활성 버전</span><strong>${esc(template.version)} → ${esc(nextVersion)}</strong></div><div class="template-review-row"><span>예상시간 · 데모</span><strong>${template.minutes}분 → ${change.minutes}분</strong></div><div class="template-review-row"><span>촬영 규칙</span><strong>인증 ${template.photos.filter(item=>item.required).length}개 · 기타 ${template.photos.filter(item=>!item.required).length}개</strong></div></div><div class="notice notice-warning" style="margin:12px 0 0">사진 구역은 유지되고 예상시간 변경은 새 작업부터 적용됩니다.</div>`,confirmLabel:'변경 저장·활성',confirmAction:'template-save',confirmVariant:'primary',historyKind:'template-review',historyPayload:change});
  4018 |         document.querySelector('[data-action="template-save"]')?.setAttribute('data-id',id);
  4019 |       }
  4020 | 
  4021 |       function titleForView() {
  4022 |         if (state.detail) {
  4023 |           const map={room:`${state.detail.id}호 객실 상세`,cleaning:`${state.detail.id}호 청소 상세`,maid:`${maidById(state.detail.id)?.name||'메이드'} 상세`,complaint:'컴플레인·벌점 상세',pay:'주급 정산 상세',templates:'청소 템플릿 설정',template:'청소 템플릿 상세'};
  4024 |           return map[state.detail.type]||'상세';
  4025 |         }
  4026 |         const admin={today:'오늘 할 일',rooms:'객실 현황',quickReservation:'간편 예약',cleaning:'청소 관리',maids:'메이드',more:'더보기'};
  4027 |         const maid={my:'내 업무',schedule:'다음 주 근무 가능일',alerts:'알림',pay:'내 주급',more:'더보기'};
  4028 |         return (state.role==='admin'?admin:maid)[currentView()]||'객실관리';
  4029 |       }
  4030 | 
  4031 |       function renderMain() {
  4032 |         if (!state.loggedIn) return renderLogin();
  4033 |         if (state.detail) return renderDetail();
  4034 |         if (state.role==='admin') {
  4035 |           if (state.adminView==='today') return renderAdminToday();
  4036 |           if (state.adminView==='rooms') return renderRooms();
  4037 |           if (state.adminView==='quickReservation') return renderQuickReservation();
  4038 |           if (state.adminView==='cleaning') return renderCleaningHub();
  4039 |           if (state.adminView==='maids') return renderMaids();
  4040 |           return renderAdminMore();
  4041 |         }
  4042 |         if (state.maidView==='my') return renderMaidMy();
  4043 |         if (state.maidView==='schedule') return renderMaidSchedule();
  4044 |         if (state.maidView==='alerts') return renderMaidAlerts();
  4045 |         if (state.maidView==='pay') return renderMaidPay();
  4046 |         return renderMaidMore();
  4047 |       }
  4048 | 
  4049 |       function renderTopbar() {
  4050 |         const alertCount=notificationUnreadCount(notificationAudienceKey()),countMarkup=alertCount?`<span class="count-dot">${alertCount}</span>`:'';
  4051 |         return `<header class="topbar"><div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 ${state.selectedDate.replaceAll('-','.')} ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div><div class="topbar-actions"><button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기 · 안 읽음 ${alertCount}건">${icon('bell')}${countMarkup}</button><button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button></div></header>`;
  4052 |       }
  4053 | 
  4054 |       function dateObject(value=state.selectedDate) {
  4055 |         const [y,m,d]=value.split('-').map(Number);
  4056 |         return new Date(y,m-1,d);
  4057 |       }
  4058 |       function dateIso(date) {
  4059 |         return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
  4060 |       }
  4061 |       function calendarDayMeta(iso) {
  4062 |         const value=dateObject(iso),weekday=value.getDay(),holiday=KR_HOLIDAY_FIXTURE.dates[iso]||null,isSunday=weekday===0,isSaturday=weekday===6;
  4063 |         return {
  4064 |           weekday,weekdayLabel:CALENDAR_WEEKDAYS[weekday],holiday,isSunday,isSaturday,
  4065 |           tone:holiday?'holiday':isSunday?'sunday':isSaturday?'saturday':'weekday',
  4066 |           classes:[isSunday?'is-sunday':'',isSaturday?'is-saturday':'',holiday?'is-holiday':''].filter(Boolean).join(' ')
  4067 |         };
  4068 |       }
  4069 |       function calendarWeekdayHeaderMarkup() {
  4070 |         return CALENDAR_WEEKDAYS.map((label,index)=>`<span class="${index===0?'is-sunday':index===6?'is-saturday':''}">${label}</span>`).join('');
  4071 |       }
  4072 |       function calendarDateAriaLabel(iso,{today=false,weekSelected=false}={}) {
  4073 |         const value=dateObject(iso),meta=calendarDayMeta(iso),parts=[`${value.getFullYear()}년 ${value.getMonth()+1}월 ${value.getDate()}일 ${meta.weekdayLabel}요일`];
  4074 |         if(meta.holiday)parts.push(meta.holiday.name);
  4075 |         if(today)parts.push('오늘');
  4076 |         if(weekSelected)parts.push('선택 주차');
  4077 |         return parts.join(', ');
  4078 |       }
  4079 |       function dateLabel(value=state.selectedDate) {
  4080 |         const d=dateObject(value), day=CALENDAR_WEEKDAYS[d.getDay()];
  4081 |         return `${d.getMonth()+1}월 ${d.getDate()}일 (${day})`;
  4082 |       }
  4083 |       function weekStartIso(value) {
  4084 |         const d=dateObject(value), offset=(d.getDay()+6)%7;
  4085 |         d.setDate(d.getDate()-offset);
  4086 |         return dateIso(d);
  4087 |       }
  4088 |       function normalizePayWeek(value) {
  4089 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4090 |         const date=dateObject(value);
  4091 |         if(dateIso(date)!==value)return null;
  4092 |         const start=weekStartIso(value);
  4093 |         return start<='2026-08-10'?start:null;
  4094 |       }
  4095 |       function normalizeWorkHistoryWeek(value) {
  4096 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4097 |         const date=dateObject(value);
  4098 |         if(dateIso(date)!==value)return null;
  4099 |         const start=weekStartIso(value);
  4100 |         return start<='2026-08-17'?start:null;
  4101 |       }
  4102 |       function workHistoryCalendarAllowed() { return state.loggedIn!==false&&state.role==='admin'&&state.adminView==='maids'&&state.adminMaidTab==='history'; }
  4103 |       function weekRangeLabel(start,withYear=false) {
  4104 |         const from=dateObject(start),to=new Date(from);to.setDate(from.getDate()+6);
  4105 |         const prefix=withYear?`${from.getFullYear()}년 `:'';
  4106 |         const fromText=`${from.getMonth()+1}월 ${from.getDate()}일(월)`;
  4107 |         const toText=from.getMonth()===to.getMonth()?`${to.getDate()}일(일)`:`${to.getMonth()+1}월 ${to.getDate()}일(일)`;
  4108 |         return `${prefix}${fromText}–${toText}`;
  4109 |       }
  4110 |       function renderDateTools(showFilters=false) {
  4111 |         return `<div class="date-tools calendar-anchor">
  4112 |           <button class="icon-btn" type="button" data-action="date-shift" data-offset="-1" aria-label="이전 날짜">${icon('chevronLeft')}</button>
```

## 메이드 네비게이션: `maid-nav`

matches: 0

## 메이드 알림: `알림`

matches: 53

### occurrence 1 · line 2512

```html
  2467 |       let toastTimer = null;
  2468 |       let undoTimer = null;
  2469 |       let pendingPin = null;
  2470 |       let pendingDraftPublish = null;
  2471 |       let historyWriteMode = 'replace';
  2472 |       let restoringHistory = false;
  2473 |       let historyTraversalPending = false;
  2474 |       let historyTraversalOverride = null;
  2475 |       let reservationWeekHistoryOverride = null;
  2476 |       let historyReturnFocus = null;
  2477 |       let historyModalSequence = 0;
  2478 |       let cleaningAttemptSequence = 0;
  2479 |       let cleaningSubmissionSequence = 0;
  2480 |       let quickPointerSession = null;
  2481 |       let quickTouchArmTimer = null;
  2482 |       let quickKeyboardSelection = null;
  2483 |       let quickSearchTimer = null;
  2484 |       let quickSuppressClickUntil = 0;
  2485 |       let activePinModalSessionId = null;
  2486 |       let activePinRevealSecret = null;
  2487 |       const completedModalSessions = [];
  2488 |       const pinModalSessions = new Map();
  2489 |       const pinModalSessionTimers = new Map();
  2490 |       const pinDerivationSeed=crypto.getRandomValues(new Uint32Array(1))[0],protectedPinOverrides=new Map();
  2491 |       function pinDerivationHash(no,salt='fixture') {
  2492 |         let hash=(pinDerivationSeed^0x9e3779b9)>>>0;
  2493 |         for(const char of `${salt}:${no}`)hash=Math.imul(hash^char.charCodeAt(0),16777619)>>>0;
  2494 |         return hash;
  2495 |       }
  2496 |       function pinMemoryMask(no) {
  2497 |         let hash=pinDerivationHash(no,'override');return Array.from({length:4},()=>{hash^=hash<<13;hash^=hash>>>17;hash^=hash<<5;return hash&255;});
  2498 |       }
  2499 |       function deriveDemoPin(no) { return String(pinDerivationHash(no)%10000).padStart(4,'0'); }
  2500 |       function readProtectedPin(no) {
  2501 |         const protectedDigits=protectedPinOverrides.get(String(no));if(!protectedDigits)return deriveDemoPin(no);
  2502 |         const mask=pinMemoryMask(no);return [...protectedDigits].map((value,index)=>String.fromCharCode(value^mask[index])).join('');
  2503 |       }
  2504 |       function writeProtectedPin(no,value) {
  2505 |         const mask=pinMemoryMask(no),digits=String(value);protectedPinOverrides.set(String(no),Uint8Array.from([...digits].map((char,index)=>char.charCodeAt(0)^mask[index])));
  2506 |       }
  2507 | 
  2508 |       const adminNav = [
  2509 |         {id:'today',label:'오늘',icon:'home'}, {id:'rooms',label:'객실',icon:'rooms'}, {id:'quickReservation',label:'간편 예약',mobileLabel:'예약',icon:'calendar'}, {id:'cleaning',label:'청소',icon:'briefcase'}, {id:'maids',label:'메이드',icon:'users'}, {id:'more',label:'더보기',icon:'more'}
  2510 |       ];
  2511 |       const maidNav = [
  2512 |         {id:'my',label:'내 업무',icon:'briefcase'}, {id:'schedule',label:'근무 일정',icon:'calendar'}, {id:'alerts',label:'알림',icon:'bell'}, {id:'pay',label:'주급',icon:'wallet'}, {id:'more',label:'더보기',icon:'more'}
  2513 |       ];
  2514 | 
  2515 |       function currentNav() { return state.role === 'admin' ? adminNav : maidNav; }
  2516 |       function currentView() { return state.role === 'admin' ? state.adminView : state.maidView; }
  2517 |       function detailAllowedForRole(type,role=state.role) {
  2518 |         return role==='admin'?['room','cleaning','maid','complaint','pay','templates','template'].includes(type):['cleaning','complaint'].includes(type);
  2519 |       }
  2520 |       function isLocked() { return state.network !== 'online' || state.listMode === 'stale'; }
  2521 |       function adminCanMutate() { return state.role==='admin'&&!isLocked(); }
  2522 |       function signedInMaidId() { return state.currentMaidId||'m1'; }
  2523 |       function signedInMaid() { return MAIDS.find(maid=>maid.id===signedInMaidId())||MAIDS[0]; }
  2524 |       function signedInMaidName() { return signedInMaid().name; }
  2525 |       function maidStatusFor(maidId) { return maidId==='m1'?state.maidStatus:(state.maidStatusById?.[maidId]||'active'); }
  2526 |       function setMaidStatusFor(maidId,status) {
  2527 |         state.maidStatusById=state.maidStatusById||{};state.maidStatusById[maidId]=status;
  2528 |         if(maidId==='m1')state.maidStatus=status;
  2529 |         return status;
  2530 |       }
  2531 |       function emptyMaidDeactivationFlow(){return {choice:null,activeRoom:null,gates:{assignments:false,round:false,lease:false},startedAt:null,completedAt:null};}
  2532 |       function maidDeactivationFor(maidId) {
  2533 |         const flow=maidId==='m1'?state.maidDeactivation:state.maidDeactivationById?.[maidId];
  2534 |         return flow&&flow.gates?flow:emptyMaidDeactivationFlow();
  2535 |       }
  2536 |       function ensureMaidDeactivationFor(maidId) {
  2537 |         if(maidId==='m1'){
  2538 |           if(!state.maidDeactivation?.gates)state.maidDeactivation=emptyMaidDeactivationFlow();
  2539 |           return state.maidDeactivation;
  2540 |         }
  2541 |         state.maidDeactivationById=state.maidDeactivationById||{};
  2542 |         if(!state.maidDeactivationById[maidId]?.gates)state.maidDeactivationById[maidId]=emptyMaidDeactivationFlow();
  2543 |         return state.maidDeactivationById[maidId];
  2544 |       }
  2545 |       function setMaidDeactivationFor(maidId,flow) {
  2546 |         if(maidId==='m1')state.maidDeactivation=flow;
  2547 |         state.maidDeactivationById=state.maidDeactivationById||{};state.maidDeactivationById[maidId]=flow;
  2548 |         return flow;
  2549 |       }
  2550 |       function signedInMaidIsActive() { return maidStatusFor(signedInMaidId())==='active'; }
  2551 |       function maidCanReceiveNewAssignment(maidId) { return maidStatusFor(maidId)==='active'; }
  2552 |       function pendingInspectionForMaid(maidId) { return validatedSubmissions().find(submission=>submission.performerId===maidId&&submission.status==='pending')||null; }
  2553 |       function maidCanCompleteRequiredReclean(no) {
  2554 |         const maidId=signedInMaidId(),attempt=activeRecleanAttempt(no);
  2555 |         return maidStatusFor(maidId)==='deactivating'&&attempt?.performerId===maidId;
  2556 |       }
  2557 |       function maidCanContinueDeactivation(no) {
  2558 |         const maidId=signedInMaidId(),flow=maidDeactivationFor(maidId),attempt=state.cleaningAttempts?.[currentAttemptId(no)],job=state.jobs[no];
  2559 |         return maidStatusFor(maidId)==='deactivating'&&attempt?.room===no&&attempt.performerId===maidId&&attempt.kind!=='재청소'&&(job==='upload'||flow?.choice==='finish'&&flow.activeRoom===no&&job==='cleaning');
  2560 |       }
  2561 |       function activeUnfinishedAttempt(no) {
  2562 |         const attemptId=state.currentAttemptByRoom?.[no],attempt=attemptId?state.cleaningAttempts?.[attemptId]:null;
  2563 |         if(!attemptId||!attempt||attempt.id!==attemptId||attempt.room!==no)return null;
  2564 |         return !['approved','rejected','superseded'].includes(attempt.status)?attempt:null;
  2565 |       }
  2566 |       function roomPinWasViewed(no,attemptId=currentAttemptId(no)) {
  2567 |         if(state.pinVisibleRoom===no)return true;
  2568 |         if(!attemptId)return false;
  2569 |         const latest=(state.events||[]).find(event=>event.roomId===no&&event.attemptId===attemptId&&[`${no}호 PIN 조회`,`${no}호 PIN lease 종료`].includes(event.title));
  2570 |         return latest?.title===`${no}호 PIN 조회`;
  2571 |       }
  2572 |       function manualCheckoutBlockingAttempt(no) {
  2573 |         const attempt=activeUnfinishedAttempt(no),job=state.jobs[no],room=ROOMS.find(item=>item.no===String(no)),currentReservation=currentOccupiedReservation(room);
  2574 |         if(!attempt)return null;
  2575 |         const unstartedCheckout=attempt.kind==='퇴실 청소'&&!attempt.startedAt&&attempt.status==='active'&&['scheduled','claimed','unassigned'].includes(job);
  2576 |         if(!unstartedCheckout)return attempt;
  2577 |         const lineageIds=new Set([attempt.reservationIdSnapshot,state.assignments?.[attempt.workTargetId]?.committedTarget?.reservationId,state.cleaningTargets?.[attempt.workTargetId]?.reservationId].filter(Boolean));
  2578 |         if(lineageIds.size>1||lineageIds.size===1&&![...lineageIds].includes(currentReservation?.id))return attempt;
  2579 |         if(currentReservation){
  2580 |           const checkoutDate=currentReservation.checkOutAt.slice(0,10),manualTarget=underlyingManualCheckoutTarget(no,checkoutDate),allowedTargetIds=new Set([`checkout-${no}-${checkoutDate}`,manualTarget?.id].filter(Boolean));
  2581 |           const targetLineageMatches=[state.assignments?.[attempt.workTargetId]?.committedTarget?.reservationId,state.cleaningTargets?.[attempt.workTargetId]?.reservationId].some(id=>id===currentReservation.id);
```

### occurrence 2 · line 3108

```html
  3063 |               <div class="demo-field scenario"><label for="demo-scenario">시나리오</label><select id="demo-scenario" data-control="scenario">${Object.entries(SCENARIOS).map(([id,s])=>`<option value="${id}" ${state.scenario===Number(id)?'selected':''}>${id==='0'?'기본':id+'.'} ${esc(s.title)}</option>`).join('')}</select></div>
  3064 |               <button class="btn btn-ghost demo-reset" type="button" data-action="reset">${icon('refresh','icon-sm')}초기 상태로 재설정</button>
  3065 |             </div>
  3066 |           </div>
  3067 |         </section>`;
  3068 |       }
  3069 | 
  3070 |       function renderSidebar(nav) {
  3071 |         const maid=signedInMaid();
  3072 |         return `<aside class="sidebar" aria-label="주요 내비게이션">
  3073 |           <div class="brand"><div class="brand-mark">CA</div><div><div class="brand-name">CASTLE THE ART</div><div class="brand-sub">객실관리</div></div></div>
  3074 |           <div class="identity"><div class="avatar">${state.role==='admin'?'관':esc(maid.name[0])}</div><div><strong>${state.role==='admin'?'관리자':esc(maid.name)}</strong><span>${state.role==='admin'?'최고 관리자':'메이드'}</span></div></div>
  3075 |           <nav class="side-nav">${nav.map(n=>`<button class="nav-btn" type="button" data-action="nav" data-view="${n.id}" ${currentView()===n.id&&!state.detail?'aria-current="page"':''}>${icon(n.icon)}<span>${n.label}</span></button>`).join('')}</nav>
  3076 |           <div class="side-foot">${button('로그인 상태 보기','logout','ghost')}</div>
  3077 |         </aside>`;
  3078 |       }
  3079 | 
  3080 |       function addAdminHelp(root,headingText,id,label,text,{rename=''}={}) {
  3081 |         [...root.querySelectorAll('h2,h3')].filter(heading=>heading.textContent.trim()===headingText).forEach((heading,index)=>{
  3082 |           if(rename)heading.textContent=rename;
  3083 |           if(heading.closest('.help-title'))return;
  3084 |           const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(`${id}-${index}`,label,text));
  3085 |         });
  3086 |       }
  3087 |       function addAdminHelpToElement(heading,id,label,text) {
  3088 |         if(!heading||heading.closest('.help-title'))return;
  3089 |         const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(id,label,text));
  3090 |       }
  3091 |       function applyMaidCopyPolicy(root) {
  3092 |         if(state.role!=='maid')return;
  3093 |         root.querySelectorAll('.scenario-coach,.week-card-head p,.weekly-availability .assignment-notice,.assigned-preview .meta,.assigned-preview > .audit-note,.work-hero p,.mobile-section-title p,.pay-week-toolbar p,.maid-pay-history-head p,.maid-pay-footnote').forEach(element=>element.remove());
  3094 |         root.querySelectorAll('.assignment-notice p').forEach(paragraph=>{const title=paragraph.querySelector('strong');if(title)paragraph.replaceChildren(title);});
  3095 |         root.querySelectorAll('.task-row p').forEach(paragraph=>{
  3096 |           if(paragraph.textContent.includes('해당 객실별 승인 합계'))paragraph.textContent=paragraph.textContent.replace('해당 객실별 승인 합계','승인 금액');
  3097 |           if(paragraph.textContent.includes('판정 확인 또는 이의 메모만 가능합니다'))paragraph.remove();
  3098 |         });
  3099 |         root.querySelectorAll('.pay-hero > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*데모 (?:지급 이력|금액)$/,'');});
  3100 |         root.querySelectorAll('.maid-pay-week-head small').forEach(label=>{label.textContent=label.textContent.includes('지급 기록액')?'지급 기록액':'승인 확정';});
  3101 |         root.querySelectorAll('.maid-pay-week-stats span').forEach(label=>{if(label.textContent.trim()==='현재 원장 예상')label.textContent='예상 금액';});
  3102 |         root.querySelectorAll('.maid-pay-disclosure > span:first-child').forEach(label=>{label.textContent=label.textContent.replace('작업 상세','청소 내역');});
  3103 |         root.querySelectorAll('.maid-pay-task > div:first-child > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*제출\/회차.*$/,'');});
  3104 |         root.querySelectorAll('.maid-pay-week .notice-danger strong').forEach(label=>{label.textContent=label.textContent.replace('현재 원장','현재 합계');});
  3105 |         root.querySelectorAll('.setting-card p').forEach(copy=>{
  3106 |           const text=copy.textContent.trim();
  3107 |           if(text==='담당·시작·완료·제출 이력')copy.textContent='최근 업무 확인';
  3108 |           if(text==='브라우저 알림 권한 전')copy.textContent='알림 권한 확인 필요';
  3109 |           if(text==='판정 확인·이의 메모만 가능')copy.textContent='판정과 답변 확인';
  3110 |         });
  3111 |         root.querySelectorAll('.detail-title p').forEach(subtitle=>{subtitle.textContent=subtitle.textContent.replace(/\s*·\s*v\d+(?:\.\d+)?\s*$/i,'').replace(/\s*·\s*데모\s*$/,'');});
  3112 |         root.querySelectorAll('h3').forEach(heading=>{if(heading.textContent.trim()==='수행·제출 타임라인')heading.textContent='진행 상황';});
  3113 |         root.querySelectorAll('.cleaning-section-body > .audit-note,.room-issue-form > .audit-note,.bomb-room-editor > .audit-note').forEach(note=>{if(/현재 탭|실제 서버|영속|흐름만 검증|지원 기기/.test(note.textContent))note.remove();});
  3114 |         root.querySelectorAll('.photo-template-banner .badge-row').forEach(row=>{if(!row.children.length)row.remove();});
  3115 |         root.querySelectorAll('.timeline li span').forEach(copy=>{copy.textContent=adminAuditSummary(copy.textContent.replace(/\s*·\s*(?:이력 보존|조건 미충족)$/,''));});
  3116 |         root.querySelectorAll('.photo-meta .info-item').forEach(item=>{const label=item.querySelector('span');if(label&&/제출 버전|관리자 결정·회차|보존 상태/.test(label.textContent))item.remove();});
  3117 |         root.querySelectorAll('.photo-viewer-visual + .photo-meta ~ .audit-note').forEach(note=>note.remove());
  3118 |         const modalTitle=root.querySelector('#modal-title'),modalDescription=root.querySelector('#modal-desc');
  3119 |         if(modalTitle?.textContent.includes('내 업무 이력'))modalTitle.textContent='내 업무 이력';
  3120 |         if(modalTitle?.textContent.includes('내 알림'))modalTitle.textContent='내 알림';
  3121 |         if(modalTitle?.textContent.includes('알림 상태'))modalTitle.textContent='알림 상태';
  3122 |         if(modalTitle?.textContent.includes('알림을 켤까요'))modalTitle.textContent='알림을 켤까요?';
  3123 |         if(modalDescription&&/본인 담당·수행·응답 기록|이 브라우저|실제 운영에서는 브라우저 권한/.test(modalDescription.textContent))modalDescription.remove();
  3124 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3125 |           if(/허용 여부와 관계없이 앱 내부 알림/.test(notice.textContent)){notice.textContent='기기 알림을 켜도 앱 안 알림은 그대로 확인할 수 있습니다.';return;}
  3126 |           if(/정적 데모|정적 파일|현재 탭 메모리|브라우저의 화면 상태/.test(notice.textContent))notice.remove();
  3127 |         });
  3128 |         root.querySelectorAll('.rail-row span').forEach(copy=>{copy.textContent=copy.textContent.replace(/\s*·\s*내 담당 작업만 표시/g,'').replace(/\s*·\s*본인 기록만 확인/g,'').replace(/\s*·\s*객실별 합계/g,'');});
  3129 |         addAdminHelp(root,'8월 17일 (월)–8월 23일 (일)','maid-schedule','근무 가능일','일요일 12:00부터 23:59까지 다음 주에 일할 수 있는 요일을 모두 고른 뒤 제출하세요. 객실과 순서는 관리자가 각 근무일 전날 배정합니다.');
  3130 |         addAdminHelp(root,'배정된 내 업무','maid-assigned','배정된 업무','관리자가 통보한 업무만 표시합니다. 담당이나 순서가 바뀌면 알림에서 확인할 수 있습니다.');
  3131 |         root.querySelectorAll('.mobile-section-title h2').forEach((heading,index)=>{if(heading.textContent.trim().startsWith('내 업무 '))addAdminHelpToElement(heading,`maid-my-${index}`,'내 업무','관리자가 통보한 업무만 표시하며 청소는 한 번에 한 객실씩 진행합니다.');});
  3132 |         addAdminHelp(root,'지금까지 주급 내역','maid-pay','주급 내역','월요일부터 일요일까지 관리자 승인을 받은 청소비를 합산합니다. 검수 대기는 예상 금액에만 표시되고, 폭탄방 승인 시 해당 객실 기본요금과 같은 추가요금이 반영됩니다. 컴플레인·벌점은 자동 차감되지 않습니다.');
  3133 |         const cameraBanner=root.querySelector('.cleaning-sections .photo-template-banner');
  3134 |         if(cameraBanner&&!cameraBanner.previousElementSibling?.classList.contains('task-photo-help')){
  3135 |           const help=document.createElement('div');help.className='help-title task-photo-help';help.innerHTML=`<h3>촬영 방법</h3>${infoTip(`maid-camera-${state.detail?.id||'task'}`,'촬영 방법','구역별 인증 사진을 촬영하세요. 바로 촬영은 후면 카메라를 열고 갤러리는 저장된 사진을 선택합니다. 다시 촬영하면 해당 사진을 교체합니다.')}`;cameraBanner.before(help);
  3136 |         }
  3137 |         const notificationCard=[...root.querySelectorAll('.setting-card')].find(card=>card.querySelector('h3')?.textContent.trim()==='알림 설정');
  3138 |         if(notificationCard){const heading=notificationCard.querySelector('h3');addAdminHelpToElement(heading,'maid-notifications','알림 설정','기기 알림을 끄더라도 앱 안의 배정 변경·검수·주급 알림은 계속 확인할 수 있습니다.');}
  3139 |         const replacements=new Map([
  3140 |           ['데모 메모리 이미지','사진'],['현재 원장','현재 합계'],['객실별 원장','객실별 청소 내역'],['수익 원장','청소비 내역'],['새 청소비 내역','추가 청소비'],['스냅샷','기준'],['fixture','데모 기록'],['수행 회차','청소 작업'],['회차 종료','청소 종료'],['제출 버전','제출 내용'],['데모 지급 이력','지급 이력'],['데모 금액','금액'],['브라우저 세션','현재 기록']
  3141 |         ]);
  3142 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3143 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\b(?:ATT|SUB|REPORT|PAY|LEASE|work|target)-[A-Za-z0-9-]+\b/gi,'').replace(/\s*·\s*v\d+(?:\.\d+)?\b/gi,'').replace(/\s*·\s*데모(?:\s+(?:기록|지급 이력|금액))?/g,'').replace(/\(데모\)/g,'').replace(/\s{2,}/g,' ');node.nodeValue=value;});
  3144 |       }
  3145 | 
  3146 |       function applyAdminCopyPolicy(root) {
  3147 |         if(state.role==='maid'){applyMaidCopyPolicy(root);return;}
  3148 |         if(state.role!=='admin')return;
  3149 |         root.querySelectorAll('.work-history-person-head p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.replace(/^당시 이름 스냅샷\s*·\s*/,'').replace(/\s*·\s*제출 버전.*$/,'');});
  3150 |         root.querySelectorAll('.pay-ledger-room p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.split(' · ').slice(0,3).join(' · ');});
  3151 |         root.querySelectorAll('.audit-note,.scenario-coach,.mobile-section-title p,.quick-booking-boundary,.quick-booking-guide-copy,.quick-booking-summary small,.quick-grid-status span:last-child,.assignment-random-copy p,.random-rule,.maid-order-lane-head p,.assignment-panel-head p,.maid-order-unassigned p,.assignment-target-rule,.work-history-unit-note,.work-history-contract,.work-history-hero p,.tab-header p,.pay-week-toolbar p,.pay-ledger-reconcile,.template-page > .notice-info,.template-row-version,.template-hero-stat,.template-hero p,.template-evidence,.template-timeline').forEach(element=>element.remove());
  3152 |         root.querySelectorAll('.cleaning-cost-foot').forEach(foot=>{const range=foot.querySelector('b');foot.replaceChildren(range||document.createTextNode(''));});
  3153 |         const costCard=root.querySelector('.cleaning-cost-card');
  3154 |         if(costCard)costCard.setAttribute('aria-label',`청소비 예상 지출. 오늘과 이번 주 금액을 확인하고 주급 정산으로 이동합니다.`);
  3155 |         const assignmentIntro=root.querySelector('.assignment-intro p');if(assignmentIntro)assignmentIntro.textContent=assignmentIntro.textContent.split(' · ')[0];
  3156 |         root.querySelectorAll('.assignment-normal,.assignment-table .cell-sub').forEach(element=>element.remove());
  3157 |         root.querySelectorAll('.assignment-route-reference').forEach(element=>{if(element.textContent.includes('담당 선택 후'))element.remove();});
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
  3164 |           button.textContent=button.textContent.replace('산출 보기','상세 보기');
  3165 |           button.setAttribute('aria-label',(button.getAttribute('aria-label')||'').replace(/현재 원장/g,'현재 합계').replace(/산출 근거 보기/g,'청소 내역 보기'));
  3166 |         });
  3167 |         root.querySelectorAll('.toggle-row span').forEach(span=>{if(['외부 송금을 시작하기 전입니다.','확정 지급액이 생기면 이 자리에서 기록합니다.'].includes(span.textContent.trim()))span.remove();});
  3168 |         const quickCopy=root.querySelector('.quick-booking-hero-copy');
  3169 |         if(quickCopy)quickCopy.innerHTML=`<span class="quick-booking-kicker">빠른 예약 등록</span><div class="help-title"><h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking','간편 예약','빈 날짜를 클릭하거나 같은 객실 행에서 가로로 드래그하세요. 터치는 0.35초 길게 누른 뒤 드래그합니다. 한 번 선택한 범위는 예약 한 건으로 저장됩니다.')}</div>`;
  3170 |         root.querySelectorAll('p').forEach(paragraph=>{if(!paragraph.closest('.notice')&&/서버 영속|fixture|스냅샷|불변 사용자 ID|PIN lease|식별값|이력 연결키|원장 비연결|예약 가능과 현재 입실 가능을 별도로 판단|사진 원본은 앱에 저장하지 않음/.test(paragraph.textContent))paragraph.remove();});
  3171 |         root.querySelectorAll('.meta').forEach(meta=>{if(/데모|스냅샷|정본/.test(meta.textContent))meta.remove();});
  3172 |         addAdminHelp(root,'총 청소요금을 먼저 맞추고 가까운 객실로 배정','random-assignment','랜덤 배정','근무 가능한 메이드의 총 청소요금이 비슷해지도록 먼저 나누고, 같은 엘리베이터와 가까운 호수를 다음 기준으로 사용합니다. 결과는 저장 전에 담당과 순서를 바꿀 수 있습니다.',{rename:'랜덤 배정'});
  3173 |         addAdminHelp(root,'메이드별 청소 순서 수정','assignment-result','청소 순서 수정','얼리 체크인·레이트 체크아웃의 예정 시각을 먼저 확인하고, 객실별 담당 메이드를 바꾸거나 위·아래 버튼으로 1번부터 순서를 정하세요. 담당과 순서가 정해진 객실만 저장·통보됩니다.');
  3174 |         addAdminHelp(root,'내일 청소 배정','next-day-assignment','내일 청소 배정','근무 가능일을 제출한 메이드에게만 배정할 수 있습니다. 랜덤 배정 뒤에도 객실별 담당과 메이드별 청소 순서를 직접 바꾼 다음 저장·통보하세요.');
  3175 |         addAdminHelp(root,'주간 근무 기록','work-history','주간 근무 기록','명은 해당 기록이 있는 메이드 수이고, 일은 메이드별 기록 날짜를 합한 값입니다. 가능 제출·담당 통보·실근무 완료를 서로 다른 표시로 확인합니다.');
  3176 |         addAdminHelp(root,'주별 지급 이력','weekly-pay','주별 지급 이력','월요일부터 일요일까지의 승인 청소를 합산합니다. 검수 대기는 예상액에만, 전체 반려와 본인 재청소는 0원으로 표시됩니다.');
  3177 |         addAdminHelp(root,'객실 기본정보','room-basics','객실 기본정보','관리자는 객실 타입과 엘리베이터를 수정할 수 있습니다. 변경값은 새로 만드는 작업부터 적용되고 객실번호는 이 화면에서 바꿀 수 없습니다.');
```

### occurrence 3 · line 3120

```html
  3075 |           <nav class="side-nav">${nav.map(n=>`<button class="nav-btn" type="button" data-action="nav" data-view="${n.id}" ${currentView()===n.id&&!state.detail?'aria-current="page"':''}>${icon(n.icon)}<span>${n.label}</span></button>`).join('')}</nav>
  3076 |           <div class="side-foot">${button('로그인 상태 보기','logout','ghost')}</div>
  3077 |         </aside>`;
  3078 |       }
  3079 | 
  3080 |       function addAdminHelp(root,headingText,id,label,text,{rename=''}={}) {
  3081 |         [...root.querySelectorAll('h2,h3')].filter(heading=>heading.textContent.trim()===headingText).forEach((heading,index)=>{
  3082 |           if(rename)heading.textContent=rename;
  3083 |           if(heading.closest('.help-title'))return;
  3084 |           const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(`${id}-${index}`,label,text));
  3085 |         });
  3086 |       }
  3087 |       function addAdminHelpToElement(heading,id,label,text) {
  3088 |         if(!heading||heading.closest('.help-title'))return;
  3089 |         const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(id,label,text));
  3090 |       }
  3091 |       function applyMaidCopyPolicy(root) {
  3092 |         if(state.role!=='maid')return;
  3093 |         root.querySelectorAll('.scenario-coach,.week-card-head p,.weekly-availability .assignment-notice,.assigned-preview .meta,.assigned-preview > .audit-note,.work-hero p,.mobile-section-title p,.pay-week-toolbar p,.maid-pay-history-head p,.maid-pay-footnote').forEach(element=>element.remove());
  3094 |         root.querySelectorAll('.assignment-notice p').forEach(paragraph=>{const title=paragraph.querySelector('strong');if(title)paragraph.replaceChildren(title);});
  3095 |         root.querySelectorAll('.task-row p').forEach(paragraph=>{
  3096 |           if(paragraph.textContent.includes('해당 객실별 승인 합계'))paragraph.textContent=paragraph.textContent.replace('해당 객실별 승인 합계','승인 금액');
  3097 |           if(paragraph.textContent.includes('판정 확인 또는 이의 메모만 가능합니다'))paragraph.remove();
  3098 |         });
  3099 |         root.querySelectorAll('.pay-hero > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*데모 (?:지급 이력|금액)$/,'');});
  3100 |         root.querySelectorAll('.maid-pay-week-head small').forEach(label=>{label.textContent=label.textContent.includes('지급 기록액')?'지급 기록액':'승인 확정';});
  3101 |         root.querySelectorAll('.maid-pay-week-stats span').forEach(label=>{if(label.textContent.trim()==='현재 원장 예상')label.textContent='예상 금액';});
  3102 |         root.querySelectorAll('.maid-pay-disclosure > span:first-child').forEach(label=>{label.textContent=label.textContent.replace('작업 상세','청소 내역');});
  3103 |         root.querySelectorAll('.maid-pay-task > div:first-child > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*제출\/회차.*$/,'');});
  3104 |         root.querySelectorAll('.maid-pay-week .notice-danger strong').forEach(label=>{label.textContent=label.textContent.replace('현재 원장','현재 합계');});
  3105 |         root.querySelectorAll('.setting-card p').forEach(copy=>{
  3106 |           const text=copy.textContent.trim();
  3107 |           if(text==='담당·시작·완료·제출 이력')copy.textContent='최근 업무 확인';
  3108 |           if(text==='브라우저 알림 권한 전')copy.textContent='알림 권한 확인 필요';
  3109 |           if(text==='판정 확인·이의 메모만 가능')copy.textContent='판정과 답변 확인';
  3110 |         });
  3111 |         root.querySelectorAll('.detail-title p').forEach(subtitle=>{subtitle.textContent=subtitle.textContent.replace(/\s*·\s*v\d+(?:\.\d+)?\s*$/i,'').replace(/\s*·\s*데모\s*$/,'');});
  3112 |         root.querySelectorAll('h3').forEach(heading=>{if(heading.textContent.trim()==='수행·제출 타임라인')heading.textContent='진행 상황';});
  3113 |         root.querySelectorAll('.cleaning-section-body > .audit-note,.room-issue-form > .audit-note,.bomb-room-editor > .audit-note').forEach(note=>{if(/현재 탭|실제 서버|영속|흐름만 검증|지원 기기/.test(note.textContent))note.remove();});
  3114 |         root.querySelectorAll('.photo-template-banner .badge-row').forEach(row=>{if(!row.children.length)row.remove();});
  3115 |         root.querySelectorAll('.timeline li span').forEach(copy=>{copy.textContent=adminAuditSummary(copy.textContent.replace(/\s*·\s*(?:이력 보존|조건 미충족)$/,''));});
  3116 |         root.querySelectorAll('.photo-meta .info-item').forEach(item=>{const label=item.querySelector('span');if(label&&/제출 버전|관리자 결정·회차|보존 상태/.test(label.textContent))item.remove();});
  3117 |         root.querySelectorAll('.photo-viewer-visual + .photo-meta ~ .audit-note').forEach(note=>note.remove());
  3118 |         const modalTitle=root.querySelector('#modal-title'),modalDescription=root.querySelector('#modal-desc');
  3119 |         if(modalTitle?.textContent.includes('내 업무 이력'))modalTitle.textContent='내 업무 이력';
  3120 |         if(modalTitle?.textContent.includes('내 알림'))modalTitle.textContent='내 알림';
  3121 |         if(modalTitle?.textContent.includes('알림 상태'))modalTitle.textContent='알림 상태';
  3122 |         if(modalTitle?.textContent.includes('알림을 켤까요'))modalTitle.textContent='알림을 켤까요?';
  3123 |         if(modalDescription&&/본인 담당·수행·응답 기록|이 브라우저|실제 운영에서는 브라우저 권한/.test(modalDescription.textContent))modalDescription.remove();
  3124 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3125 |           if(/허용 여부와 관계없이 앱 내부 알림/.test(notice.textContent)){notice.textContent='기기 알림을 켜도 앱 안 알림은 그대로 확인할 수 있습니다.';return;}
  3126 |           if(/정적 데모|정적 파일|현재 탭 메모리|브라우저의 화면 상태/.test(notice.textContent))notice.remove();
  3127 |         });
  3128 |         root.querySelectorAll('.rail-row span').forEach(copy=>{copy.textContent=copy.textContent.replace(/\s*·\s*내 담당 작업만 표시/g,'').replace(/\s*·\s*본인 기록만 확인/g,'').replace(/\s*·\s*객실별 합계/g,'');});
  3129 |         addAdminHelp(root,'8월 17일 (월)–8월 23일 (일)','maid-schedule','근무 가능일','일요일 12:00부터 23:59까지 다음 주에 일할 수 있는 요일을 모두 고른 뒤 제출하세요. 객실과 순서는 관리자가 각 근무일 전날 배정합니다.');
  3130 |         addAdminHelp(root,'배정된 내 업무','maid-assigned','배정된 업무','관리자가 통보한 업무만 표시합니다. 담당이나 순서가 바뀌면 알림에서 확인할 수 있습니다.');
  3131 |         root.querySelectorAll('.mobile-section-title h2').forEach((heading,index)=>{if(heading.textContent.trim().startsWith('내 업무 '))addAdminHelpToElement(heading,`maid-my-${index}`,'내 업무','관리자가 통보한 업무만 표시하며 청소는 한 번에 한 객실씩 진행합니다.');});
  3132 |         addAdminHelp(root,'지금까지 주급 내역','maid-pay','주급 내역','월요일부터 일요일까지 관리자 승인을 받은 청소비를 합산합니다. 검수 대기는 예상 금액에만 표시되고, 폭탄방 승인 시 해당 객실 기본요금과 같은 추가요금이 반영됩니다. 컴플레인·벌점은 자동 차감되지 않습니다.');
  3133 |         const cameraBanner=root.querySelector('.cleaning-sections .photo-template-banner');
  3134 |         if(cameraBanner&&!cameraBanner.previousElementSibling?.classList.contains('task-photo-help')){
  3135 |           const help=document.createElement('div');help.className='help-title task-photo-help';help.innerHTML=`<h3>촬영 방법</h3>${infoTip(`maid-camera-${state.detail?.id||'task'}`,'촬영 방법','구역별 인증 사진을 촬영하세요. 바로 촬영은 후면 카메라를 열고 갤러리는 저장된 사진을 선택합니다. 다시 촬영하면 해당 사진을 교체합니다.')}`;cameraBanner.before(help);
  3136 |         }
  3137 |         const notificationCard=[...root.querySelectorAll('.setting-card')].find(card=>card.querySelector('h3')?.textContent.trim()==='알림 설정');
  3138 |         if(notificationCard){const heading=notificationCard.querySelector('h3');addAdminHelpToElement(heading,'maid-notifications','알림 설정','기기 알림을 끄더라도 앱 안의 배정 변경·검수·주급 알림은 계속 확인할 수 있습니다.');}
  3139 |         const replacements=new Map([
  3140 |           ['데모 메모리 이미지','사진'],['현재 원장','현재 합계'],['객실별 원장','객실별 청소 내역'],['수익 원장','청소비 내역'],['새 청소비 내역','추가 청소비'],['스냅샷','기준'],['fixture','데모 기록'],['수행 회차','청소 작업'],['회차 종료','청소 종료'],['제출 버전','제출 내용'],['데모 지급 이력','지급 이력'],['데모 금액','금액'],['브라우저 세션','현재 기록']
  3141 |         ]);
  3142 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3143 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\b(?:ATT|SUB|REPORT|PAY|LEASE|work|target)-[A-Za-z0-9-]+\b/gi,'').replace(/\s*·\s*v\d+(?:\.\d+)?\b/gi,'').replace(/\s*·\s*데모(?:\s+(?:기록|지급 이력|금액))?/g,'').replace(/\(데모\)/g,'').replace(/\s{2,}/g,' ');node.nodeValue=value;});
  3144 |       }
  3145 | 
  3146 |       function applyAdminCopyPolicy(root) {
  3147 |         if(state.role==='maid'){applyMaidCopyPolicy(root);return;}
  3148 |         if(state.role!=='admin')return;
  3149 |         root.querySelectorAll('.work-history-person-head p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.replace(/^당시 이름 스냅샷\s*·\s*/,'').replace(/\s*·\s*제출 버전.*$/,'');});
  3150 |         root.querySelectorAll('.pay-ledger-room p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.split(' · ').slice(0,3).join(' · ');});
  3151 |         root.querySelectorAll('.audit-note,.scenario-coach,.mobile-section-title p,.quick-booking-boundary,.quick-booking-guide-copy,.quick-booking-summary small,.quick-grid-status span:last-child,.assignment-random-copy p,.random-rule,.maid-order-lane-head p,.assignment-panel-head p,.maid-order-unassigned p,.assignment-target-rule,.work-history-unit-note,.work-history-contract,.work-history-hero p,.tab-header p,.pay-week-toolbar p,.pay-ledger-reconcile,.template-page > .notice-info,.template-row-version,.template-hero-stat,.template-hero p,.template-evidence,.template-timeline').forEach(element=>element.remove());
  3152 |         root.querySelectorAll('.cleaning-cost-foot').forEach(foot=>{const range=foot.querySelector('b');foot.replaceChildren(range||document.createTextNode(''));});
  3153 |         const costCard=root.querySelector('.cleaning-cost-card');
  3154 |         if(costCard)costCard.setAttribute('aria-label',`청소비 예상 지출. 오늘과 이번 주 금액을 확인하고 주급 정산으로 이동합니다.`);
  3155 |         const assignmentIntro=root.querySelector('.assignment-intro p');if(assignmentIntro)assignmentIntro.textContent=assignmentIntro.textContent.split(' · ')[0];
  3156 |         root.querySelectorAll('.assignment-normal,.assignment-table .cell-sub').forEach(element=>element.remove());
  3157 |         root.querySelectorAll('.assignment-route-reference').forEach(element=>{if(element.textContent.includes('담당 선택 후'))element.remove();});
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
  3164 |           button.textContent=button.textContent.replace('산출 보기','상세 보기');
  3165 |           button.setAttribute('aria-label',(button.getAttribute('aria-label')||'').replace(/현재 원장/g,'현재 합계').replace(/산출 근거 보기/g,'청소 내역 보기'));
  3166 |         });
  3167 |         root.querySelectorAll('.toggle-row span').forEach(span=>{if(['외부 송금을 시작하기 전입니다.','확정 지급액이 생기면 이 자리에서 기록합니다.'].includes(span.textContent.trim()))span.remove();});
  3168 |         const quickCopy=root.querySelector('.quick-booking-hero-copy');
  3169 |         if(quickCopy)quickCopy.innerHTML=`<span class="quick-booking-kicker">빠른 예약 등록</span><div class="help-title"><h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking','간편 예약','빈 날짜를 클릭하거나 같은 객실 행에서 가로로 드래그하세요. 터치는 0.35초 길게 누른 뒤 드래그합니다. 한 번 선택한 범위는 예약 한 건으로 저장됩니다.')}</div>`;
  3170 |         root.querySelectorAll('p').forEach(paragraph=>{if(!paragraph.closest('.notice')&&/서버 영속|fixture|스냅샷|불변 사용자 ID|PIN lease|식별값|이력 연결키|원장 비연결|예약 가능과 현재 입실 가능을 별도로 판단|사진 원본은 앱에 저장하지 않음/.test(paragraph.textContent))paragraph.remove();});
  3171 |         root.querySelectorAll('.meta').forEach(meta=>{if(/데모|스냅샷|정본/.test(meta.textContent))meta.remove();});
  3172 |         addAdminHelp(root,'총 청소요금을 먼저 맞추고 가까운 객실로 배정','random-assignment','랜덤 배정','근무 가능한 메이드의 총 청소요금이 비슷해지도록 먼저 나누고, 같은 엘리베이터와 가까운 호수를 다음 기준으로 사용합니다. 결과는 저장 전에 담당과 순서를 바꿀 수 있습니다.',{rename:'랜덤 배정'});
  3173 |         addAdminHelp(root,'메이드별 청소 순서 수정','assignment-result','청소 순서 수정','얼리 체크인·레이트 체크아웃의 예정 시각을 먼저 확인하고, 객실별 담당 메이드를 바꾸거나 위·아래 버튼으로 1번부터 순서를 정하세요. 담당과 순서가 정해진 객실만 저장·통보됩니다.');
  3174 |         addAdminHelp(root,'내일 청소 배정','next-day-assignment','내일 청소 배정','근무 가능일을 제출한 메이드에게만 배정할 수 있습니다. 랜덤 배정 뒤에도 객실별 담당과 메이드별 청소 순서를 직접 바꾼 다음 저장·통보하세요.');
  3175 |         addAdminHelp(root,'주간 근무 기록','work-history','주간 근무 기록','명은 해당 기록이 있는 메이드 수이고, 일은 메이드별 기록 날짜를 합한 값입니다. 가능 제출·담당 통보·실근무 완료를 서로 다른 표시로 확인합니다.');
  3176 |         addAdminHelp(root,'주별 지급 이력','weekly-pay','주별 지급 이력','월요일부터 일요일까지의 승인 청소를 합산합니다. 검수 대기는 예상액에만, 전체 반려와 본인 재청소는 0원으로 표시됩니다.');
  3177 |         addAdminHelp(root,'객실 기본정보','room-basics','객실 기본정보','관리자는 객실 타입과 엘리베이터를 수정할 수 있습니다. 변경값은 새로 만드는 작업부터 적용되고 객실번호는 이 화면에서 바꿀 수 없습니다.');
  3178 |         addAdminHelp(root,'현재 투숙 상태','occupancy','현재 투숙 상태','투숙 중에는 지금 체크아웃하거나 투숙 중 청소를 요청할 수 있습니다. 지금 체크아웃하면 공실·청소 필요 상태로 바뀝니다.');
  3179 |         addAdminHelp(root,'예약·입퇴실','reservation-times','예약·입퇴실','한 고객의 체크인부터 체크아웃 순서로 입력합니다. 체크인 16:00보다 빠르거나 체크아웃 11:00보다 늦으면 자동으로 표시되고, 체크아웃 날짜에 퇴실 청소가 추가됩니다.');
  3180 |         addAdminHelp(root,'타입별 촬영 구역을 확인하세요','templates','청소 템플릿','객실 타입과 실제 침실·욕실 수에 맞춰 촬영 구역을 정합니다. 수정한 내용은 새 작업부터 적용됩니다. 연락처·얼굴·고객 물품은 제외하고, TV는 켠 뒤 계정·QR·알림 없는 기본 화면을 촬영합니다.',{rename:'타입별 청소 템플릿'});
  3181 |         root.querySelectorAll('h3').forEach((heading,index)=>{if(/^왜 .+인가요\?$/.test(heading.textContent.trim()))addAdminHelpToElement(heading,`pay-detail-${index}`,'주급 계산','확정된 객실별 청소요금을 합산합니다. 폭탄방은 해당 객실만 기본요금을 한 번 더하고, 검수 대기 금액은 확정 주급에 포함하지 않습니다.');});
  3182 |         root.querySelectorAll('h3').forEach(heading=>{
  3183 |           const text=heading.textContent.trim();
  3184 |           if(text==='계산 규칙'||text==='객실 사건 타임라인')heading.closest('.card')?.remove();
  3185 |           if(text==='폭탄방 요금 원장')heading.textContent='폭탄방 청소비';
  3186 |           if(text==='저장된 전체 과거 주차')heading.textContent='과거 주차';
  3187 |         });
  3188 |         root.querySelectorAll('th').forEach(heading=>{if(heading.textContent.trim()==='청소 정보·등록 근거')heading.textContent='청소 유형';});
  3189 |         root.querySelectorAll('#modal-desc').forEach(description=>{
```

### occurrence 4 · line 3121

```html
  3076 |           <div class="side-foot">${button('로그인 상태 보기','logout','ghost')}</div>
  3077 |         </aside>`;
  3078 |       }
  3079 | 
  3080 |       function addAdminHelp(root,headingText,id,label,text,{rename=''}={}) {
  3081 |         [...root.querySelectorAll('h2,h3')].filter(heading=>heading.textContent.trim()===headingText).forEach((heading,index)=>{
  3082 |           if(rename)heading.textContent=rename;
  3083 |           if(heading.closest('.help-title'))return;
  3084 |           const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(`${id}-${index}`,label,text));
  3085 |         });
  3086 |       }
  3087 |       function addAdminHelpToElement(heading,id,label,text) {
  3088 |         if(!heading||heading.closest('.help-title'))return;
  3089 |         const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(id,label,text));
  3090 |       }
  3091 |       function applyMaidCopyPolicy(root) {
  3092 |         if(state.role!=='maid')return;
  3093 |         root.querySelectorAll('.scenario-coach,.week-card-head p,.weekly-availability .assignment-notice,.assigned-preview .meta,.assigned-preview > .audit-note,.work-hero p,.mobile-section-title p,.pay-week-toolbar p,.maid-pay-history-head p,.maid-pay-footnote').forEach(element=>element.remove());
  3094 |         root.querySelectorAll('.assignment-notice p').forEach(paragraph=>{const title=paragraph.querySelector('strong');if(title)paragraph.replaceChildren(title);});
  3095 |         root.querySelectorAll('.task-row p').forEach(paragraph=>{
  3096 |           if(paragraph.textContent.includes('해당 객실별 승인 합계'))paragraph.textContent=paragraph.textContent.replace('해당 객실별 승인 합계','승인 금액');
  3097 |           if(paragraph.textContent.includes('판정 확인 또는 이의 메모만 가능합니다'))paragraph.remove();
  3098 |         });
  3099 |         root.querySelectorAll('.pay-hero > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*데모 (?:지급 이력|금액)$/,'');});
  3100 |         root.querySelectorAll('.maid-pay-week-head small').forEach(label=>{label.textContent=label.textContent.includes('지급 기록액')?'지급 기록액':'승인 확정';});
  3101 |         root.querySelectorAll('.maid-pay-week-stats span').forEach(label=>{if(label.textContent.trim()==='현재 원장 예상')label.textContent='예상 금액';});
  3102 |         root.querySelectorAll('.maid-pay-disclosure > span:first-child').forEach(label=>{label.textContent=label.textContent.replace('작업 상세','청소 내역');});
  3103 |         root.querySelectorAll('.maid-pay-task > div:first-child > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*제출\/회차.*$/,'');});
  3104 |         root.querySelectorAll('.maid-pay-week .notice-danger strong').forEach(label=>{label.textContent=label.textContent.replace('현재 원장','현재 합계');});
  3105 |         root.querySelectorAll('.setting-card p').forEach(copy=>{
  3106 |           const text=copy.textContent.trim();
  3107 |           if(text==='담당·시작·완료·제출 이력')copy.textContent='최근 업무 확인';
  3108 |           if(text==='브라우저 알림 권한 전')copy.textContent='알림 권한 확인 필요';
  3109 |           if(text==='판정 확인·이의 메모만 가능')copy.textContent='판정과 답변 확인';
  3110 |         });
  3111 |         root.querySelectorAll('.detail-title p').forEach(subtitle=>{subtitle.textContent=subtitle.textContent.replace(/\s*·\s*v\d+(?:\.\d+)?\s*$/i,'').replace(/\s*·\s*데모\s*$/,'');});
  3112 |         root.querySelectorAll('h3').forEach(heading=>{if(heading.textContent.trim()==='수행·제출 타임라인')heading.textContent='진행 상황';});
  3113 |         root.querySelectorAll('.cleaning-section-body > .audit-note,.room-issue-form > .audit-note,.bomb-room-editor > .audit-note').forEach(note=>{if(/현재 탭|실제 서버|영속|흐름만 검증|지원 기기/.test(note.textContent))note.remove();});
  3114 |         root.querySelectorAll('.photo-template-banner .badge-row').forEach(row=>{if(!row.children.length)row.remove();});
  3115 |         root.querySelectorAll('.timeline li span').forEach(copy=>{copy.textContent=adminAuditSummary(copy.textContent.replace(/\s*·\s*(?:이력 보존|조건 미충족)$/,''));});
  3116 |         root.querySelectorAll('.photo-meta .info-item').forEach(item=>{const label=item.querySelector('span');if(label&&/제출 버전|관리자 결정·회차|보존 상태/.test(label.textContent))item.remove();});
  3117 |         root.querySelectorAll('.photo-viewer-visual + .photo-meta ~ .audit-note').forEach(note=>note.remove());
  3118 |         const modalTitle=root.querySelector('#modal-title'),modalDescription=root.querySelector('#modal-desc');
  3119 |         if(modalTitle?.textContent.includes('내 업무 이력'))modalTitle.textContent='내 업무 이력';
  3120 |         if(modalTitle?.textContent.includes('내 알림'))modalTitle.textContent='내 알림';
  3121 |         if(modalTitle?.textContent.includes('알림 상태'))modalTitle.textContent='알림 상태';
  3122 |         if(modalTitle?.textContent.includes('알림을 켤까요'))modalTitle.textContent='알림을 켤까요?';
  3123 |         if(modalDescription&&/본인 담당·수행·응답 기록|이 브라우저|실제 운영에서는 브라우저 권한/.test(modalDescription.textContent))modalDescription.remove();
  3124 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3125 |           if(/허용 여부와 관계없이 앱 내부 알림/.test(notice.textContent)){notice.textContent='기기 알림을 켜도 앱 안 알림은 그대로 확인할 수 있습니다.';return;}
  3126 |           if(/정적 데모|정적 파일|현재 탭 메모리|브라우저의 화면 상태/.test(notice.textContent))notice.remove();
  3127 |         });
  3128 |         root.querySelectorAll('.rail-row span').forEach(copy=>{copy.textContent=copy.textContent.replace(/\s*·\s*내 담당 작업만 표시/g,'').replace(/\s*·\s*본인 기록만 확인/g,'').replace(/\s*·\s*객실별 합계/g,'');});
  3129 |         addAdminHelp(root,'8월 17일 (월)–8월 23일 (일)','maid-schedule','근무 가능일','일요일 12:00부터 23:59까지 다음 주에 일할 수 있는 요일을 모두 고른 뒤 제출하세요. 객실과 순서는 관리자가 각 근무일 전날 배정합니다.');
  3130 |         addAdminHelp(root,'배정된 내 업무','maid-assigned','배정된 업무','관리자가 통보한 업무만 표시합니다. 담당이나 순서가 바뀌면 알림에서 확인할 수 있습니다.');
  3131 |         root.querySelectorAll('.mobile-section-title h2').forEach((heading,index)=>{if(heading.textContent.trim().startsWith('내 업무 '))addAdminHelpToElement(heading,`maid-my-${index}`,'내 업무','관리자가 통보한 업무만 표시하며 청소는 한 번에 한 객실씩 진행합니다.');});
  3132 |         addAdminHelp(root,'지금까지 주급 내역','maid-pay','주급 내역','월요일부터 일요일까지 관리자 승인을 받은 청소비를 합산합니다. 검수 대기는 예상 금액에만 표시되고, 폭탄방 승인 시 해당 객실 기본요금과 같은 추가요금이 반영됩니다. 컴플레인·벌점은 자동 차감되지 않습니다.');
  3133 |         const cameraBanner=root.querySelector('.cleaning-sections .photo-template-banner');
  3134 |         if(cameraBanner&&!cameraBanner.previousElementSibling?.classList.contains('task-photo-help')){
  3135 |           const help=document.createElement('div');help.className='help-title task-photo-help';help.innerHTML=`<h3>촬영 방법</h3>${infoTip(`maid-camera-${state.detail?.id||'task'}`,'촬영 방법','구역별 인증 사진을 촬영하세요. 바로 촬영은 후면 카메라를 열고 갤러리는 저장된 사진을 선택합니다. 다시 촬영하면 해당 사진을 교체합니다.')}`;cameraBanner.before(help);
  3136 |         }
  3137 |         const notificationCard=[...root.querySelectorAll('.setting-card')].find(card=>card.querySelector('h3')?.textContent.trim()==='알림 설정');
  3138 |         if(notificationCard){const heading=notificationCard.querySelector('h3');addAdminHelpToElement(heading,'maid-notifications','알림 설정','기기 알림을 끄더라도 앱 안의 배정 변경·검수·주급 알림은 계속 확인할 수 있습니다.');}
  3139 |         const replacements=new Map([
  3140 |           ['데모 메모리 이미지','사진'],['현재 원장','현재 합계'],['객실별 원장','객실별 청소 내역'],['수익 원장','청소비 내역'],['새 청소비 내역','추가 청소비'],['스냅샷','기준'],['fixture','데모 기록'],['수행 회차','청소 작업'],['회차 종료','청소 종료'],['제출 버전','제출 내용'],['데모 지급 이력','지급 이력'],['데모 금액','금액'],['브라우저 세션','현재 기록']
  3141 |         ]);
  3142 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3143 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\b(?:ATT|SUB|REPORT|PAY|LEASE|work|target)-[A-Za-z0-9-]+\b/gi,'').replace(/\s*·\s*v\d+(?:\.\d+)?\b/gi,'').replace(/\s*·\s*데모(?:\s+(?:기록|지급 이력|금액))?/g,'').replace(/\(데모\)/g,'').replace(/\s{2,}/g,' ');node.nodeValue=value;});
  3144 |       }
  3145 | 
  3146 |       function applyAdminCopyPolicy(root) {
  3147 |         if(state.role==='maid'){applyMaidCopyPolicy(root);return;}
  3148 |         if(state.role!=='admin')return;
  3149 |         root.querySelectorAll('.work-history-person-head p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.replace(/^당시 이름 스냅샷\s*·\s*/,'').replace(/\s*·\s*제출 버전.*$/,'');});
  3150 |         root.querySelectorAll('.pay-ledger-room p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.split(' · ').slice(0,3).join(' · ');});
  3151 |         root.querySelectorAll('.audit-note,.scenario-coach,.mobile-section-title p,.quick-booking-boundary,.quick-booking-guide-copy,.quick-booking-summary small,.quick-grid-status span:last-child,.assignment-random-copy p,.random-rule,.maid-order-lane-head p,.assignment-panel-head p,.maid-order-unassigned p,.assignment-target-rule,.work-history-unit-note,.work-history-contract,.work-history-hero p,.tab-header p,.pay-week-toolbar p,.pay-ledger-reconcile,.template-page > .notice-info,.template-row-version,.template-hero-stat,.template-hero p,.template-evidence,.template-timeline').forEach(element=>element.remove());
  3152 |         root.querySelectorAll('.cleaning-cost-foot').forEach(foot=>{const range=foot.querySelector('b');foot.replaceChildren(range||document.createTextNode(''));});
  3153 |         const costCard=root.querySelector('.cleaning-cost-card');
  3154 |         if(costCard)costCard.setAttribute('aria-label',`청소비 예상 지출. 오늘과 이번 주 금액을 확인하고 주급 정산으로 이동합니다.`);
  3155 |         const assignmentIntro=root.querySelector('.assignment-intro p');if(assignmentIntro)assignmentIntro.textContent=assignmentIntro.textContent.split(' · ')[0];
  3156 |         root.querySelectorAll('.assignment-normal,.assignment-table .cell-sub').forEach(element=>element.remove());
  3157 |         root.querySelectorAll('.assignment-route-reference').forEach(element=>{if(element.textContent.includes('담당 선택 후'))element.remove();});
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
  3164 |           button.textContent=button.textContent.replace('산출 보기','상세 보기');
  3165 |           button.setAttribute('aria-label',(button.getAttribute('aria-label')||'').replace(/현재 원장/g,'현재 합계').replace(/산출 근거 보기/g,'청소 내역 보기'));
  3166 |         });
  3167 |         root.querySelectorAll('.toggle-row span').forEach(span=>{if(['외부 송금을 시작하기 전입니다.','확정 지급액이 생기면 이 자리에서 기록합니다.'].includes(span.textContent.trim()))span.remove();});
  3168 |         const quickCopy=root.querySelector('.quick-booking-hero-copy');
  3169 |         if(quickCopy)quickCopy.innerHTML=`<span class="quick-booking-kicker">빠른 예약 등록</span><div class="help-title"><h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking','간편 예약','빈 날짜를 클릭하거나 같은 객실 행에서 가로로 드래그하세요. 터치는 0.35초 길게 누른 뒤 드래그합니다. 한 번 선택한 범위는 예약 한 건으로 저장됩니다.')}</div>`;
  3170 |         root.querySelectorAll('p').forEach(paragraph=>{if(!paragraph.closest('.notice')&&/서버 영속|fixture|스냅샷|불변 사용자 ID|PIN lease|식별값|이력 연결키|원장 비연결|예약 가능과 현재 입실 가능을 별도로 판단|사진 원본은 앱에 저장하지 않음/.test(paragraph.textContent))paragraph.remove();});
  3171 |         root.querySelectorAll('.meta').forEach(meta=>{if(/데모|스냅샷|정본/.test(meta.textContent))meta.remove();});
  3172 |         addAdminHelp(root,'총 청소요금을 먼저 맞추고 가까운 객실로 배정','random-assignment','랜덤 배정','근무 가능한 메이드의 총 청소요금이 비슷해지도록 먼저 나누고, 같은 엘리베이터와 가까운 호수를 다음 기준으로 사용합니다. 결과는 저장 전에 담당과 순서를 바꿀 수 있습니다.',{rename:'랜덤 배정'});
  3173 |         addAdminHelp(root,'메이드별 청소 순서 수정','assignment-result','청소 순서 수정','얼리 체크인·레이트 체크아웃의 예정 시각을 먼저 확인하고, 객실별 담당 메이드를 바꾸거나 위·아래 버튼으로 1번부터 순서를 정하세요. 담당과 순서가 정해진 객실만 저장·통보됩니다.');
  3174 |         addAdminHelp(root,'내일 청소 배정','next-day-assignment','내일 청소 배정','근무 가능일을 제출한 메이드에게만 배정할 수 있습니다. 랜덤 배정 뒤에도 객실별 담당과 메이드별 청소 순서를 직접 바꾼 다음 저장·통보하세요.');
  3175 |         addAdminHelp(root,'주간 근무 기록','work-history','주간 근무 기록','명은 해당 기록이 있는 메이드 수이고, 일은 메이드별 기록 날짜를 합한 값입니다. 가능 제출·담당 통보·실근무 완료를 서로 다른 표시로 확인합니다.');
  3176 |         addAdminHelp(root,'주별 지급 이력','weekly-pay','주별 지급 이력','월요일부터 일요일까지의 승인 청소를 합산합니다. 검수 대기는 예상액에만, 전체 반려와 본인 재청소는 0원으로 표시됩니다.');
  3177 |         addAdminHelp(root,'객실 기본정보','room-basics','객실 기본정보','관리자는 객실 타입과 엘리베이터를 수정할 수 있습니다. 변경값은 새로 만드는 작업부터 적용되고 객실번호는 이 화면에서 바꿀 수 없습니다.');
  3178 |         addAdminHelp(root,'현재 투숙 상태','occupancy','현재 투숙 상태','투숙 중에는 지금 체크아웃하거나 투숙 중 청소를 요청할 수 있습니다. 지금 체크아웃하면 공실·청소 필요 상태로 바뀝니다.');
  3179 |         addAdminHelp(root,'예약·입퇴실','reservation-times','예약·입퇴실','한 고객의 체크인부터 체크아웃 순서로 입력합니다. 체크인 16:00보다 빠르거나 체크아웃 11:00보다 늦으면 자동으로 표시되고, 체크아웃 날짜에 퇴실 청소가 추가됩니다.');
  3180 |         addAdminHelp(root,'타입별 촬영 구역을 확인하세요','templates','청소 템플릿','객실 타입과 실제 침실·욕실 수에 맞춰 촬영 구역을 정합니다. 수정한 내용은 새 작업부터 적용됩니다. 연락처·얼굴·고객 물품은 제외하고, TV는 켠 뒤 계정·QR·알림 없는 기본 화면을 촬영합니다.',{rename:'타입별 청소 템플릿'});
  3181 |         root.querySelectorAll('h3').forEach((heading,index)=>{if(/^왜 .+인가요\?$/.test(heading.textContent.trim()))addAdminHelpToElement(heading,`pay-detail-${index}`,'주급 계산','확정된 객실별 청소요금을 합산합니다. 폭탄방은 해당 객실만 기본요금을 한 번 더하고, 검수 대기 금액은 확정 주급에 포함하지 않습니다.');});
  3182 |         root.querySelectorAll('h3').forEach(heading=>{
  3183 |           const text=heading.textContent.trim();
  3184 |           if(text==='계산 규칙'||text==='객실 사건 타임라인')heading.closest('.card')?.remove();
  3185 |           if(text==='폭탄방 요금 원장')heading.textContent='폭탄방 청소비';
  3186 |           if(text==='저장된 전체 과거 주차')heading.textContent='과거 주차';
  3187 |         });
  3188 |         root.querySelectorAll('th').forEach(heading=>{if(heading.textContent.trim()==='청소 정보·등록 근거')heading.textContent='청소 유형';});
  3189 |         root.querySelectorAll('#modal-desc').forEach(description=>{
  3190 |           if(/이력 연결키|식별값/.test(description.textContent))description.textContent='객실 타입과 엘리베이터를 수정합니다.';
```

### occurrence 5 · line 3122

```html
  3077 |         </aside>`;
  3078 |       }
  3079 | 
  3080 |       function addAdminHelp(root,headingText,id,label,text,{rename=''}={}) {
  3081 |         [...root.querySelectorAll('h2,h3')].filter(heading=>heading.textContent.trim()===headingText).forEach((heading,index)=>{
  3082 |           if(rename)heading.textContent=rename;
  3083 |           if(heading.closest('.help-title'))return;
  3084 |           const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(`${id}-${index}`,label,text));
  3085 |         });
  3086 |       }
  3087 |       function addAdminHelpToElement(heading,id,label,text) {
  3088 |         if(!heading||heading.closest('.help-title'))return;
  3089 |         const wrapper=document.createElement('div');wrapper.className='help-title';heading.before(wrapper);wrapper.append(heading);wrapper.insertAdjacentHTML('beforeend',infoTip(id,label,text));
  3090 |       }
  3091 |       function applyMaidCopyPolicy(root) {
  3092 |         if(state.role!=='maid')return;
  3093 |         root.querySelectorAll('.scenario-coach,.week-card-head p,.weekly-availability .assignment-notice,.assigned-preview .meta,.assigned-preview > .audit-note,.work-hero p,.mobile-section-title p,.pay-week-toolbar p,.maid-pay-history-head p,.maid-pay-footnote').forEach(element=>element.remove());
  3094 |         root.querySelectorAll('.assignment-notice p').forEach(paragraph=>{const title=paragraph.querySelector('strong');if(title)paragraph.replaceChildren(title);});
  3095 |         root.querySelectorAll('.task-row p').forEach(paragraph=>{
  3096 |           if(paragraph.textContent.includes('해당 객실별 승인 합계'))paragraph.textContent=paragraph.textContent.replace('해당 객실별 승인 합계','승인 금액');
  3097 |           if(paragraph.textContent.includes('판정 확인 또는 이의 메모만 가능합니다'))paragraph.remove();
  3098 |         });
  3099 |         root.querySelectorAll('.pay-hero > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*데모 (?:지급 이력|금액)$/,'');});
  3100 |         root.querySelectorAll('.maid-pay-week-head small').forEach(label=>{label.textContent=label.textContent.includes('지급 기록액')?'지급 기록액':'승인 확정';});
  3101 |         root.querySelectorAll('.maid-pay-week-stats span').forEach(label=>{if(label.textContent.trim()==='현재 원장 예상')label.textContent='예상 금액';});
  3102 |         root.querySelectorAll('.maid-pay-disclosure > span:first-child').forEach(label=>{label.textContent=label.textContent.replace('작업 상세','청소 내역');});
  3103 |         root.querySelectorAll('.maid-pay-task > div:first-child > span').forEach(label=>{label.textContent=label.textContent.replace(/\s*·\s*제출\/회차.*$/,'');});
  3104 |         root.querySelectorAll('.maid-pay-week .notice-danger strong').forEach(label=>{label.textContent=label.textContent.replace('현재 원장','현재 합계');});
  3105 |         root.querySelectorAll('.setting-card p').forEach(copy=>{
  3106 |           const text=copy.textContent.trim();
  3107 |           if(text==='담당·시작·완료·제출 이력')copy.textContent='최근 업무 확인';
  3108 |           if(text==='브라우저 알림 권한 전')copy.textContent='알림 권한 확인 필요';
  3109 |           if(text==='판정 확인·이의 메모만 가능')copy.textContent='판정과 답변 확인';
  3110 |         });
  3111 |         root.querySelectorAll('.detail-title p').forEach(subtitle=>{subtitle.textContent=subtitle.textContent.replace(/\s*·\s*v\d+(?:\.\d+)?\s*$/i,'').replace(/\s*·\s*데모\s*$/,'');});
  3112 |         root.querySelectorAll('h3').forEach(heading=>{if(heading.textContent.trim()==='수행·제출 타임라인')heading.textContent='진행 상황';});
  3113 |         root.querySelectorAll('.cleaning-section-body > .audit-note,.room-issue-form > .audit-note,.bomb-room-editor > .audit-note').forEach(note=>{if(/현재 탭|실제 서버|영속|흐름만 검증|지원 기기/.test(note.textContent))note.remove();});
  3114 |         root.querySelectorAll('.photo-template-banner .badge-row').forEach(row=>{if(!row.children.length)row.remove();});
  3115 |         root.querySelectorAll('.timeline li span').forEach(copy=>{copy.textContent=adminAuditSummary(copy.textContent.replace(/\s*·\s*(?:이력 보존|조건 미충족)$/,''));});
  3116 |         root.querySelectorAll('.photo-meta .info-item').forEach(item=>{const label=item.querySelector('span');if(label&&/제출 버전|관리자 결정·회차|보존 상태/.test(label.textContent))item.remove();});
  3117 |         root.querySelectorAll('.photo-viewer-visual + .photo-meta ~ .audit-note').forEach(note=>note.remove());
  3118 |         const modalTitle=root.querySelector('#modal-title'),modalDescription=root.querySelector('#modal-desc');
  3119 |         if(modalTitle?.textContent.includes('내 업무 이력'))modalTitle.textContent='내 업무 이력';
  3120 |         if(modalTitle?.textContent.includes('내 알림'))modalTitle.textContent='내 알림';
  3121 |         if(modalTitle?.textContent.includes('알림 상태'))modalTitle.textContent='알림 상태';
  3122 |         if(modalTitle?.textContent.includes('알림을 켤까요'))modalTitle.textContent='알림을 켤까요?';
  3123 |         if(modalDescription&&/본인 담당·수행·응답 기록|이 브라우저|실제 운영에서는 브라우저 권한/.test(modalDescription.textContent))modalDescription.remove();
  3124 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3125 |           if(/허용 여부와 관계없이 앱 내부 알림/.test(notice.textContent)){notice.textContent='기기 알림을 켜도 앱 안 알림은 그대로 확인할 수 있습니다.';return;}
  3126 |           if(/정적 데모|정적 파일|현재 탭 메모리|브라우저의 화면 상태/.test(notice.textContent))notice.remove();
  3127 |         });
  3128 |         root.querySelectorAll('.rail-row span').forEach(copy=>{copy.textContent=copy.textContent.replace(/\s*·\s*내 담당 작업만 표시/g,'').replace(/\s*·\s*본인 기록만 확인/g,'').replace(/\s*·\s*객실별 합계/g,'');});
  3129 |         addAdminHelp(root,'8월 17일 (월)–8월 23일 (일)','maid-schedule','근무 가능일','일요일 12:00부터 23:59까지 다음 주에 일할 수 있는 요일을 모두 고른 뒤 제출하세요. 객실과 순서는 관리자가 각 근무일 전날 배정합니다.');
  3130 |         addAdminHelp(root,'배정된 내 업무','maid-assigned','배정된 업무','관리자가 통보한 업무만 표시합니다. 담당이나 순서가 바뀌면 알림에서 확인할 수 있습니다.');
  3131 |         root.querySelectorAll('.mobile-section-title h2').forEach((heading,index)=>{if(heading.textContent.trim().startsWith('내 업무 '))addAdminHelpToElement(heading,`maid-my-${index}`,'내 업무','관리자가 통보한 업무만 표시하며 청소는 한 번에 한 객실씩 진행합니다.');});
  3132 |         addAdminHelp(root,'지금까지 주급 내역','maid-pay','주급 내역','월요일부터 일요일까지 관리자 승인을 받은 청소비를 합산합니다. 검수 대기는 예상 금액에만 표시되고, 폭탄방 승인 시 해당 객실 기본요금과 같은 추가요금이 반영됩니다. 컴플레인·벌점은 자동 차감되지 않습니다.');
  3133 |         const cameraBanner=root.querySelector('.cleaning-sections .photo-template-banner');
  3134 |         if(cameraBanner&&!cameraBanner.previousElementSibling?.classList.contains('task-photo-help')){
  3135 |           const help=document.createElement('div');help.className='help-title task-photo-help';help.innerHTML=`<h3>촬영 방법</h3>${infoTip(`maid-camera-${state.detail?.id||'task'}`,'촬영 방법','구역별 인증 사진을 촬영하세요. 바로 촬영은 후면 카메라를 열고 갤러리는 저장된 사진을 선택합니다. 다시 촬영하면 해당 사진을 교체합니다.')}`;cameraBanner.before(help);
  3136 |         }
  3137 |         const notificationCard=[...root.querySelectorAll('.setting-card')].find(card=>card.querySelector('h3')?.textContent.trim()==='알림 설정');
  3138 |         if(notificationCard){const heading=notificationCard.querySelector('h3');addAdminHelpToElement(heading,'maid-notifications','알림 설정','기기 알림을 끄더라도 앱 안의 배정 변경·검수·주급 알림은 계속 확인할 수 있습니다.');}
  3139 |         const replacements=new Map([
  3140 |           ['데모 메모리 이미지','사진'],['현재 원장','현재 합계'],['객실별 원장','객실별 청소 내역'],['수익 원장','청소비 내역'],['새 청소비 내역','추가 청소비'],['스냅샷','기준'],['fixture','데모 기록'],['수행 회차','청소 작업'],['회차 종료','청소 종료'],['제출 버전','제출 내용'],['데모 지급 이력','지급 이력'],['데모 금액','금액'],['브라우저 세션','현재 기록']
  3141 |         ]);
  3142 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3143 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\b(?:ATT|SUB|REPORT|PAY|LEASE|work|target)-[A-Za-z0-9-]+\b/gi,'').replace(/\s*·\s*v\d+(?:\.\d+)?\b/gi,'').replace(/\s*·\s*데모(?:\s+(?:기록|지급 이력|금액))?/g,'').replace(/\(데모\)/g,'').replace(/\s{2,}/g,' ');node.nodeValue=value;});
  3144 |       }
  3145 | 
  3146 |       function applyAdminCopyPolicy(root) {
  3147 |         if(state.role==='maid'){applyMaidCopyPolicy(root);return;}
  3148 |         if(state.role!=='admin')return;
  3149 |         root.querySelectorAll('.work-history-person-head p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.replace(/^당시 이름 스냅샷\s*·\s*/,'').replace(/\s*·\s*제출 버전.*$/,'');});
  3150 |         root.querySelectorAll('.pay-ledger-room p').forEach(paragraph=>{paragraph.textContent=paragraph.textContent.split(' · ').slice(0,3).join(' · ');});
  3151 |         root.querySelectorAll('.audit-note,.scenario-coach,.mobile-section-title p,.quick-booking-boundary,.quick-booking-guide-copy,.quick-booking-summary small,.quick-grid-status span:last-child,.assignment-random-copy p,.random-rule,.maid-order-lane-head p,.assignment-panel-head p,.maid-order-unassigned p,.assignment-target-rule,.work-history-unit-note,.work-history-contract,.work-history-hero p,.tab-header p,.pay-week-toolbar p,.pay-ledger-reconcile,.template-page > .notice-info,.template-row-version,.template-hero-stat,.template-hero p,.template-evidence,.template-timeline').forEach(element=>element.remove());
  3152 |         root.querySelectorAll('.cleaning-cost-foot').forEach(foot=>{const range=foot.querySelector('b');foot.replaceChildren(range||document.createTextNode(''));});
  3153 |         const costCard=root.querySelector('.cleaning-cost-card');
  3154 |         if(costCard)costCard.setAttribute('aria-label',`청소비 예상 지출. 오늘과 이번 주 금액을 확인하고 주급 정산으로 이동합니다.`);
  3155 |         const assignmentIntro=root.querySelector('.assignment-intro p');if(assignmentIntro)assignmentIntro.textContent=assignmentIntro.textContent.split(' · ')[0];
  3156 |         root.querySelectorAll('.assignment-normal,.assignment-table .cell-sub').forEach(element=>element.remove());
  3157 |         root.querySelectorAll('.assignment-route-reference').forEach(element=>{if(element.textContent.includes('담당 선택 후'))element.remove();});
  3158 |         const randomKicker=root.querySelector('.random-kicker');if(randomKicker)randomKicker.textContent='미배정 객실 자동 분배';
  3159 |         const randomLive=root.querySelector('.random-live');if(randomLive)randomLive.textContent=state.randomAssignmentSnapshot?`${state.randomAssignmentSummary?.assigned||0}건 배정됨 · 아래에서 수정하세요`:'미배정 객실만 배정합니다.';
  3160 |         const filterContext=root.querySelector('.assignment-filter-context span');if(filterContext)filterContext.innerHTML=`<strong>${esc(ROOM_TYPES[state.assignmentTypeFilter]?.name||'전체 객실 타입')}</strong> · 배정된 객실만 저장·통보`;
  3161 |         root.querySelectorAll('.template-group-head p').forEach(paragraph=>{paragraph.textContent=`${paragraph.textContent.split(' · ')[0]} · 기본 청소요금`;});
  3162 |         root.querySelectorAll('.template-group-head > .badge').forEach(badge=>badge.remove());
  3163 |         root.querySelectorAll('[data-action="admin-pay-detail"]').forEach(button=>{
  3164 |           button.textContent=button.textContent.replace('산출 보기','상세 보기');
  3165 |           button.setAttribute('aria-label',(button.getAttribute('aria-label')||'').replace(/현재 원장/g,'현재 합계').replace(/산출 근거 보기/g,'청소 내역 보기'));
  3166 |         });
  3167 |         root.querySelectorAll('.toggle-row span').forEach(span=>{if(['외부 송금을 시작하기 전입니다.','확정 지급액이 생기면 이 자리에서 기록합니다.'].includes(span.textContent.trim()))span.remove();});
  3168 |         const quickCopy=root.querySelector('.quick-booking-hero-copy');
  3169 |         if(quickCopy)quickCopy.innerHTML=`<span class="quick-booking-kicker">빠른 예약 등록</span><div class="help-title"><h2>간편 예약 · 8월 15일 기준</h2>${infoTip('quick-booking','간편 예약','빈 날짜를 클릭하거나 같은 객실 행에서 가로로 드래그하세요. 터치는 0.35초 길게 누른 뒤 드래그합니다. 한 번 선택한 범위는 예약 한 건으로 저장됩니다.')}</div>`;
  3170 |         root.querySelectorAll('p').forEach(paragraph=>{if(!paragraph.closest('.notice')&&/서버 영속|fixture|스냅샷|불변 사용자 ID|PIN lease|식별값|이력 연결키|원장 비연결|예약 가능과 현재 입실 가능을 별도로 판단|사진 원본은 앱에 저장하지 않음/.test(paragraph.textContent))paragraph.remove();});
  3171 |         root.querySelectorAll('.meta').forEach(meta=>{if(/데모|스냅샷|정본/.test(meta.textContent))meta.remove();});
  3172 |         addAdminHelp(root,'총 청소요금을 먼저 맞추고 가까운 객실로 배정','random-assignment','랜덤 배정','근무 가능한 메이드의 총 청소요금이 비슷해지도록 먼저 나누고, 같은 엘리베이터와 가까운 호수를 다음 기준으로 사용합니다. 결과는 저장 전에 담당과 순서를 바꿀 수 있습니다.',{rename:'랜덤 배정'});
  3173 |         addAdminHelp(root,'메이드별 청소 순서 수정','assignment-result','청소 순서 수정','얼리 체크인·레이트 체크아웃의 예정 시각을 먼저 확인하고, 객실별 담당 메이드를 바꾸거나 위·아래 버튼으로 1번부터 순서를 정하세요. 담당과 순서가 정해진 객실만 저장·통보됩니다.');
  3174 |         addAdminHelp(root,'내일 청소 배정','next-day-assignment','내일 청소 배정','근무 가능일을 제출한 메이드에게만 배정할 수 있습니다. 랜덤 배정 뒤에도 객실별 담당과 메이드별 청소 순서를 직접 바꾼 다음 저장·통보하세요.');
  3175 |         addAdminHelp(root,'주간 근무 기록','work-history','주간 근무 기록','명은 해당 기록이 있는 메이드 수이고, 일은 메이드별 기록 날짜를 합한 값입니다. 가능 제출·담당 통보·실근무 완료를 서로 다른 표시로 확인합니다.');
  3176 |         addAdminHelp(root,'주별 지급 이력','weekly-pay','주별 지급 이력','월요일부터 일요일까지의 승인 청소를 합산합니다. 검수 대기는 예상액에만, 전체 반려와 본인 재청소는 0원으로 표시됩니다.');
  3177 |         addAdminHelp(root,'객실 기본정보','room-basics','객실 기본정보','관리자는 객실 타입과 엘리베이터를 수정할 수 있습니다. 변경값은 새로 만드는 작업부터 적용되고 객실번호는 이 화면에서 바꿀 수 없습니다.');
  3178 |         addAdminHelp(root,'현재 투숙 상태','occupancy','현재 투숙 상태','투숙 중에는 지금 체크아웃하거나 투숙 중 청소를 요청할 수 있습니다. 지금 체크아웃하면 공실·청소 필요 상태로 바뀝니다.');
  3179 |         addAdminHelp(root,'예약·입퇴실','reservation-times','예약·입퇴실','한 고객의 체크인부터 체크아웃 순서로 입력합니다. 체크인 16:00보다 빠르거나 체크아웃 11:00보다 늦으면 자동으로 표시되고, 체크아웃 날짜에 퇴실 청소가 추가됩니다.');
  3180 |         addAdminHelp(root,'타입별 촬영 구역을 확인하세요','templates','청소 템플릿','객실 타입과 실제 침실·욕실 수에 맞춰 촬영 구역을 정합니다. 수정한 내용은 새 작업부터 적용됩니다. 연락처·얼굴·고객 물품은 제외하고, TV는 켠 뒤 계정·QR·알림 없는 기본 화면을 촬영합니다.',{rename:'타입별 청소 템플릿'});
  3181 |         root.querySelectorAll('h3').forEach((heading,index)=>{if(/^왜 .+인가요\?$/.test(heading.textContent.trim()))addAdminHelpToElement(heading,`pay-detail-${index}`,'주급 계산','확정된 객실별 청소요금을 합산합니다. 폭탄방은 해당 객실만 기본요금을 한 번 더하고, 검수 대기 금액은 확정 주급에 포함하지 않습니다.');});
  3182 |         root.querySelectorAll('h3').forEach(heading=>{
  3183 |           const text=heading.textContent.trim();
  3184 |           if(text==='계산 규칙'||text==='객실 사건 타임라인')heading.closest('.card')?.remove();
  3185 |           if(text==='폭탄방 요금 원장')heading.textContent='폭탄방 청소비';
  3186 |           if(text==='저장된 전체 과거 주차')heading.textContent='과거 주차';
  3187 |         });
  3188 |         root.querySelectorAll('th').forEach(heading=>{if(heading.textContent.trim()==='청소 정보·등록 근거')heading.textContent='청소 유형';});
  3189 |         root.querySelectorAll('#modal-desc').forEach(description=>{
  3190 |           if(/이력 연결키|식별값/.test(description.textContent))description.textContent='객실 타입과 엘리베이터를 수정합니다.';
  3191 |           if(/시트 정본|예상시간만 데모/.test(description.textContent))description.textContent='객실 타입별 청소요금과 예상시간을 확인합니다.';
```

## 관리자 근무표: `메이드 근무표`

matches: 0

## 미배정 객실: `아직 순서가 없는 객실`

matches: 1

### occurrence 1 · line 5210

```html
  5165 |         const cancelledAt=`${state.selectedDate} ${state.time}`,reasonCode='reservation',reason='실제 체크아웃 기록 · 투숙 중 청소 종료',notices=[];
  5166 |         [...candidateById.values()].forEach(item=>{
  5167 |           const assignment=state.assignments[item.id]||(state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null}),selectedMaidId=assignment.maidId||null,notifiedMaidId=assignment.previousMaidId||(assignment.status==='notified'?assignment.maidId:null),notifiedOrder=assignment.previousOrder??assignment.order,beforeMaidId=notifiedMaidId||selectedMaidId||null,beforeOrder=notifiedOrder??assignment.order??null,snapshot=assignment.committedTarget||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),attempt=attemptForCleaningTarget(item),targetRecord=state.cleaningTargets[item.id]||cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate));
  5168 |           Object.assign(targetRecord,{...cleaningTargetSnapshot(item,targetPlanDate(item,state.selectedDate)),closed:true,closedAt:cancelledAt,closedBy:'관리자 · 데모',closeReasonCode:reasonCode,closeReason:reason,closeStatus:'cancelled'});state.cleaningTargets[item.id]=targetRecord;
  5169 |           const manualTarget=(state.manualAssignmentTargets||[]).find(target=>target.id===item.id);if(manualTarget)Object.assign(manualTarget,{cancelled:true,cancelledAt,cancelledBy:'관리자 · 데모',closeReasonCode:reasonCode,closeReason:reason});
  5170 |           if(attempt&&!attempt.startedAt&&!attempt.completedAt){attempt.status='superseded';attempt.endedAt=cancelledAt;attempt.endReason=reason;if(state.currentAttemptByRoom?.[roomNo]===attempt.id)delete state.currentAttemptByRoom[roomNo];}
  5171 |           Object.assign(assignment,{maidId:'',order:null,status:'cancelled',previousMaidId:null,previousOrder:null,cancelledMaidId:selectedMaidId,cancelledNotifiedMaidId:notifiedMaidId,cancelledOrder:assignment.order??null,cancelledPreviousOrder:notifiedOrder??null,cancelledStatus:assignment.status||'unassigned',cancelledAt,cancelledBy:'관리자 · 데모',cancelledNotifiedAt:assignment.notifiedAt||null,cancelledNotificationRevision:assignment.notificationRevision||null,cancelReasonCode:reasonCode,cancelReason:reason,cancelledReservationId:item.reservationId||null,cancelledObligationKey:cleaningTargetObligationKey(item),committedTarget:snapshot});
  5172 |           state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:item.id,assignmentDate:targetEffectiveDate(item),room:roomNo,beforeMaidId:beforeMaidId||null,afterMaidId:null,before:beforeMaidId?`${maidName(beforeMaidId)} · ${beforeOrder||'순서 없음'}${beforeOrder?'번째':''}`:'미배정',after:'투숙 종료로 요청 취소',reason});
  5173 |           appendEvent(`${roomNo}호 투숙 중 청소 요청 취소`,`${dateLabel(targetEffectiveDate(item))} · 실제 체크아웃으로 미시작 요청 종료 · 기존 배정·일정 기준 보존`);
  5174 |           if(notifiedMaidId)notices.push({maidId:notifiedMaidId,order:notifiedOrder,date:targetEffectiveDate(item),item});
  5175 |         });
  5176 |         const routeByMaidDate=new Map();notices.forEach(notice=>{const key=`${notice.maidId}:${notice.date}`;if(!routeByMaidDate.has(key))routeByMaidDate.set(key,commitRemainingNotifiedOrdersAfterCancellation(notice.maidId,notice.date));});
  5177 |         notices.forEach(notice=>{const remaining=routeByMaidDate.get(`${notice.maidId}:${notice.date}`),routeText=remaining?.route.length?`남은 순서 ${remaining.route.map(entry=>`${entry.order}.${entry.item.room}호(${assignmentScheduleText(entry.item)})`).join(' → ')}`:'남은 청소 없음';appendEvent('내 투숙 중 청소 요청 취소',`${roomNo}호 · 기존 ${notice.order||'순서 없음'}${notice.order?'번째':''} · 실제 체크아웃으로 미시작 요청 종료 · ${routeText}`,{maidIds:[notice.maidId],roomId:roomNo});});
  5178 |         return candidateById.size;
  5179 |       }
  5180 |       function assignmentTypeId(item) {
  5181 |         return assignmentPricingSnapshot(item).typeId;
  5182 |       }
  5183 |       function filteredAssignmentTargets() {
  5184 |         const filter=state.assignmentTypeFilter||'all';
  5185 |         return assignmentTargets().filter(item=>filter==='all'||assignmentTypeId(item)===filter);
  5186 |       }
  5187 |       function assignmentTypeFiltersMarkup() {
  5188 |         const targets=assignmentTargets(),filter=state.assignmentTypeFilter||'all',items=[{id:'all',name:'전체 객실 타입',count:targets.length,meta:'랜덤 배정 대상'},...Object.entries(ROOM_TYPES).map(([id,type])=>({id,name:type.name,count:targets.filter(item=>assignmentTypeId(item)===id).length,meta:`객실당 ${money(type.rate)}`}))];
  5189 |         return `<div class="assignment-type-filters" role="group" aria-label="청소대상 객실 타입 필터">${items.map(item=>`<button class="assignment-type-filter" type="button" data-action="assignment-type-filter" data-type="${esc(item.id)}" aria-pressed="${filter===item.id}" aria-label="${esc(item.name)} ${item.count}건${item.id==='all'?'':`, 청소 요금 ${item.meta.replace('객실당 ','')}`} 보기"><strong>${esc(item.name)}</strong><span>${item.count}건</span><small>${esc(item.meta)}</small></button>`).join('')}</div>`;
  5190 |       }
  5191 |       function assignmentRouteReference(item) {
  5192 |         const assignment=assignmentFor(item);
  5193 |         if(!assignment.maidId){const random=state.randomAssignments?.[item.id];return random?`<span class="assignment-random-note is-warning">${icon('alert','icon-sm')}${esc(random.reason)}</span>`:'<span class="assignment-route-reference">담당 선택 후 아래 순서 보드에 추가</span>';}
  5194 |         return `<span class="assignment-route-reference">${esc(maidName(assignment.maidId))} · 순서 보드 ${assignment.order}번째</span>${randomAssignmentNote(item)}`;
  5195 |       }
  5196 |       function maidOrderItemMarkup(item,ordered,index) {
  5197 |         const assignment=assignmentFor(item),context=assignmentContext(item),name=maidName(assignment.maidId),first=index===0,last=index===ordered.length-1,status=assignment.status==='notified'?'통보 완료':'저장 전',scheduleBadges=assignmentSchedulePriorityBadges(item),guestCount=assignmentGuestCount(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item),disabled=adjustmentBlock?'disabled':'',previous=ordered[index-1],next=ordered[index+1],upDisabled=first||!!adjustmentBlock||!!previous&&!cleaningTargetCanAdjust(previous),downDisabled=last||!!adjustmentBlock||!!next&&!cleaningTargetCanAdjust(next);
  5198 |         return `<article class="maid-order-item ${scheduleBadges.length?'has-schedule-attention':''}"><span class="maid-order-number" aria-hidden="true">${assignment.order}</span><div class="maid-order-copy"><strong>${assignment.order}번째 · ${item.room}호</strong>${scheduleBadges.length?`<div class="maid-order-schedule-badges" aria-label="${item.room}호 일정 주의">${scheduleBadges.join('')}</div>`:''}<span>${esc(context.type.name)} · ${money(context.type.rate)}${guestCount?` · 숙박 ${guestCountLabel(guestCount)}`:''}</span><span>${esc(elevatorLabel(context.room))} · ${esc(item.kind)} · ${status}</span>${adjustmentBlock?`<span>${esc(adjustmentBlock)}</span>`:''}</div><label class="maid-order-assignee"><span class="sr-only">${item.room}호 담당 메이드 변경</span><select class="select-control" data-control="assignment-maid" data-location="board" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 변경" ${disabled}>${assignmentOptions(item)}</select></label><div class="maid-order-controls"><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="up" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 위로 이동" ${upDisabled?'disabled':''}>${icon('arrowUp','icon-sm')}</button><button class="assignment-order-btn" type="button" data-action="move-assignment-order" data-target="${esc(item.id)}" data-direction="down" aria-label="${esc(name)}의 ${item.room}호 청소 순서를 아래로 이동" ${downDisabled?'disabled':''}>${icon('arrowDown','icon-sm')}</button></div></article>`;
  5199 |       }
  5200 |       function renderRandomAssignmentCard() {
  5201 |         const eligible=eligibleAssignmentMaids(),unassigned=assignmentTargets().filter(item=>!assignmentFor(item).maidId&&!roomIsOnHold(item.room)&&cleaningTargetCanAdjust(item)),summary=state.randomAssignmentSummary||{assigned:0,skipped:0},active=!!state.randomAssignmentSnapshot,disabled=state.role!=='admin'||isLocked()||!eligible.length||(!active&&!unassigned.length);
  5202 |         const actions=active?`${button('다시 동선 고려 랜덤 배정','random-assignments','outline',disabled?'disabled':'')}${button('랜덤 배정 전으로 되돌리기','undo-random-assignment','outline',disabled?'disabled':'')}`:button(`미배정 ${unassigned.length}건 동선 고려 랜덤 배정`,'random-assignments','primary',disabled?'disabled':'');
  5203 |         return `<section class="card assignment-random" aria-labelledby="assignment-random-title"><div class="assignment-random-copy"><span class="random-kicker">2단계 · 저장 전 랜덤 초안</span><div class="assignment-random-title-row"><h3 id="assignment-random-title">동선 고려 랜덤 배정</h3><div class="assignment-rule-help"><button class="assignment-rule-help-button" type="button" aria-label="랜덤 배정 기준 설명" aria-describedby="assignment-random-tooltip">${icon('info','icon-sm')}</button><div class="assignment-rule-tooltip" id="assignment-random-tooltip" role="tooltip"><strong>랜덤 배정 기준</strong><span>근무 가능·마감을 먼저 확인합니다.</span><span>총 청소요금 균형을 우선합니다.</span><span>같은 점수에서는 같은 엘리베이터·가까운 호수를 봅니다.</span><span>관리자가 담당과 순서를 최종 수정합니다.</span><span>실제 이동시간을 계산하는 경로 최적화는 아닙니다.</span></div></div></div><p>미배정 객실만 저장 전 초안으로 배정합니다.</p></div><div class="assignment-random-stats"><div><span>근무 가능</span><strong>${eligible.length}명</strong></div><div><span>초안 배정</span><strong>${active?`${summary.assigned}객실`:'실행 전'}</strong></div><div><span>남은 미배정</span><strong>${active?`${summary.skipped}객실`:`${unassigned.length}객실`}</strong></div></div><div class="assignment-random-actions"><div class="random-live" aria-live="polite">${active?`${summary.assigned}건을 랜덤 배정했습니다. 아래에서 담당과 순서를 바꾼 뒤 저장·통보하세요.`:'기존 통보와 관리자가 정한 담당은 유지하고 미배정 객실만 채웁니다.'}</div>${actions}</div></section>`;
  5204 |       }
  5205 |       function renderMaidOrderBoardContent() {
  5206 |         const targets=assignmentTargets(),unassigned=targets.filter(item=>!assignmentFor(item).maidId),assignedMaidIds=new Set(targets.map(item=>assignmentFor(item).maidId).filter(Boolean)),isEditingBalance=targets.some(item=>assignmentFor(item).status==='draft');
  5207 |         const visibleMaidIds=isEditingBalance?new Set([...assignedMaidIds,...eligibleAssignmentMaids().map(maid=>maid.id)]):assignedMaidIds,visibleMaids=MAIDS.filter(maid=>visibleMaidIds.has(maid.id));
  5208 |         const lanes=visibleMaids.map(maid=>{const ordered=orderedAssignmentsForMaid(maid.id),total=ordered.reduce((sum,item)=>sum+assignmentTargetRate(item),0);return `<section class="maid-order-lane" id="maid-order-${maid.id}" aria-labelledby="maid-order-title-${maid.id}"><div class="maid-order-lane-head"><div class="maid-order-lane-copy"><h4 id="maid-order-title-${maid.id}">${esc(maid.name)} 배정 객실·청소 순서</h4><p>각 객실의 담당을 바꾸거나 위·아래 버튼으로 1–N 순서를 조정할 수 있습니다.</p></div><div class="maid-order-lane-total" data-maid-id="${maid.id}" data-maid-total="${total}"><span>총 청소요금 · ${ordered.length}건</span><strong>${money(total)}</strong></div></div><div class="maid-order-list">${ordered.length?ordered.map((item,index)=>maidOrderItemMarkup(item,ordered,index)).join(''):'<div class="maid-order-empty">배정된 객실이 없습니다.</div>'}</div></section>`;}).join('');
  5209 |         const unassignedList=unassigned.length?unassigned.map(item=>{const context=assignmentContext(item);return `<span class="maid-order-unassigned-chip">${item.room}호 · ${esc(context.type.name)} · ${esc(elevatorLabel(context.room))} · ${money(context.type.rate)}</span>`;}).join(''):'<span class="maid-order-unassigned-chip">미배정 객실 없음</span>';
  5210 |         return `<section class="card maid-order-panel" aria-labelledby="maid-order-board-title"><div class="assignment-panel-head"><div><span class="assignment-step-label">4단계 · 세부 수정</span><h3 id="maid-order-board-title">메이드별 청소 순서 수정</h3><p>얼리 체크인·레이트 체크아웃의 조정된 예정 시각을 먼저 확인하고, 객실 담당과 1–N 순서를 직접 수정합니다.</p></div>${statusBadge(`${unassigned.length}건 미배정`,unassigned.length?'red':'green')}</div><div class="maid-order-board ${lanes?'':'is-empty'}">${lanes||'<div class="maid-order-empty">아직 배정된 객실이 없습니다. 랜덤 배정하거나 위 객실 표에서 담당을 선택하세요.</div>'}</div><div class="maid-order-unassigned"><div><h4>아직 순서가 없는 객실</h4><p>미배정 상태로 남겨 두고 담당이 정해진 객실만 먼저 통보할 수 있습니다.</p></div><div class="maid-order-unassigned-list">${unassignedList}</div></div><div class="assignment-foot"><p>랜덤 배정은 저장 전 초안입니다. 담당과 연속 순서가 정해진 객실만 저장·통보합니다.</p>${button(`배정된 변경 ${assignmentTargets().filter(item=>assignmentHasNetChange(item)&&assignmentFor(item).maidId).length}건 저장·통보`,'save-assignments','primary',assignmentCanSave()?'':'disabled')}</div></section>`;
  5211 |       }
  5212 |       function assignmentCountsForDate(assignmentDate=state.assignmentDate) {
  5213 |         const targets=assignmentTargetsForDate(assignmentDate),rows=targets.map(item=>state.assignments?.[item.id]||{maidId:'',status:'unassigned'}),assigned=rows.filter(item=>item.maidId).length,notified=targets.filter(item=>{const record=state.assignments?.[item.id];return !!(record?.status==='notified'&&record.maidId||record?.previousMaidId);}).length;
  5214 |         return {total:rows.length,assigned,notified,unassigned:rows.length-assigned,carryover:targets.filter(item=>item.carryReason).length,automatic:targets.filter(item=>item.source!=='manual').length,manual:targets.filter(item=>item.source==='manual').length,checkout:targets.filter(item=>item.source==='checkout').length,stayover:targets.filter(item=>item.source==='stayover').length,submitted:MAIDS.filter(maid=>availabilityForWorkDate(maid.id,assignmentDate)!=='missing').length};
  5215 |       }
  5216 |       function assignmentCounts() { return assignmentCountsForDate(state.assignmentDate); }
  5217 |       function assignmentCanSave() {
  5218 |         const targets=assignmentTargets(),changedTargets=targets.filter(item=>assignmentHasNetChange(item)&&!!assignmentFor(item).maidId),affectedMaidIds=[...new Set(changedTargets.flatMap(item=>[assignmentFor(item).maidId,assignmentFor(item).previousMaidId]).filter(Boolean))],allAssignedToAvailable=changedTargets.every(item=>availabilityForWorkDate(assignmentFor(item).maidId,targetEffectiveDate(item))==='available');
  5219 |         const continuousOrders=affectedMaidIds.every(maidId=>orderedAssignmentsForMaid(maidId).every((item,index)=>assignmentFor(item).order===index+1));
  5220 |         const allAssignedToActiveMaids=changedTargets.every(item=>maidCanReceiveNewAssignment(assignmentFor(item).maidId));
  5221 |         const noHeldRoomChanges=changedTargets.every(item=>!roomIsOnHold(item.room)&&item.carryReason!=='access-review');
  5222 |         const noStartedRoomChanges=changedTargets.every(cleaningTargetCanAdjust);
  5223 |         const randomFresh=!state.randomAssignmentSnapshot||(state.randomAssignmentSnapshot.contextSignature===randomAssignmentContextSignature()&&randomAssignmentStateMatches());
  5224 |         return changedTargets.length>0&&noHeldRoomChanges&&noStartedRoomChanges&&allAssignedToAvailable&&allAssignedToActiveMaids&&continuousOrders&&randomFresh&&!isLocked();
  5225 |       }
  5226 |       function renderAvailabilityMatrix() {
  5227 |         const start=weekStartIso(state.assignmentDate),days=['월','화','수','목','금','토','일'].map((name,index)=>{const iso=addIsoDays(start,index);return {name,iso,day:Number(iso.slice(8))};});
  5228 |         return `<div class="availability-matrix-wrap"><table class="availability-matrix"><thead><tr><th scope="col">메이드</th>${days.map(day=>`<th scope="col">${day.name} ${day.day}</th>`).join('')}</tr></thead><tbody>${MAIDS.map(maid=>`<tr><th scope="row">${esc(maid.name)}</th>${days.map((day,index)=>`<td>${availabilityCell(maid.id,index,day.iso)}</td>`).join('')}</tr>`).join('')}</tbody></table></div><div class="assignment-foot"><p>✓ 가능 · × 불가 · — 미제출. ${days[assignmentDayIndex()].name}요일 배정 후보는 해당 날짜 가능 제출자만 표시합니다.</p></div>`;
  5229 |       }
  5230 |       function assignmentOptions(item) {
  5231 |         const selected=assignmentFor(item).maidId||'',effectiveDate=targetEffectiveDate(item);
  5232 |         const eligible=MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,effectiveDate)==='available');
  5233 |         const legacy=selected&&!eligible.some(maid=>maid.id===selected)?`<option value="${esc(selected)}" selected disabled>${esc(maidName(selected))} (기존 담당 · 신규 배정 불가)</option>`:'';
  5234 |         return `<option value="">담당 선택</option>${legacy}${eligible.map(maid=>`<option value="${maid.id}" ${selected===maid.id?'selected':''}>${esc(maid.name)} (근무 가능)</option>`).join('')}${eligible.length?'':'<option value="" disabled>근무 가능 메이드 없음</option>'}`;
  5235 |       }
  5236 |       function assignmentContext(item) {
  5237 |         const liveRoom=ROOMS.find(entry=>entry.no===item.room),snapshot=assignmentPricingSnapshot(item),room=liveRoom?{...liveRoom,elevator:snapshot.elevator}:liveRoom,type={...(ROOM_TYPES[snapshot.typeId]||ROOM_TYPES.standard),rate:snapshot.rate,minutes:snapshot.minutes};
  5238 |         const roomStatus=roomReservationStatus(room),status=item.source==='stayover'?reservationTimeStatus(null,null):reservationTimeStatus(item.checkin||roomStatus.checkin,item.checkout||roomStatus.checkout);
  5239 |         return {room,type,...status};
  5240 |       }
  5241 |       function eligibleAssignmentMaids() {
  5242 |         return MAIDS.filter(maid=>maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,state.assignmentDate)==='available');
  5243 |       }
  5244 |       function assignmentPricingSnapshot(item) {
  5245 |         const room=ROOMS.find(entry=>entry.no===item.room),committed=state.assignments?.[item.id]?.committedTarget||null,source=committed||item,typeId=source.type||item.type||room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard;
  5246 |         const elevator=Object.prototype.hasOwnProperty.call(source,'elevatorSnapshot')?source.elevatorSnapshot:room?.elevator||null;
  5247 |         return {typeId,rate:Number(source.rateSnapshot)||Number(source.baseRateSnapshot)||Number(source.templateSnapshot?.rate)||Number(type.rate)||0,minutes:Number(source.minutesSnapshot)||Number(source.templateSnapshot?.minutes)||Number(type.minutes)||0,elevator};
  5248 |       }
  5249 |       function assignmentTargetMinutes(item) { return assignmentPricingSnapshot(item).minutes; }
  5250 |       function assignmentTargetElevator(item) { return assignmentPricingSnapshot(item).elevator; }
  5251 |       function assignmentTargetRate(item) { return assignmentPricingSnapshot(item).rate; }
  5252 |       function assignmentPayStats(totals) {
  5253 |         if(!totals.length)return {gap:0,deviation:0};
  5254 |         const sum=totals.reduce((total,value)=>total+value,0),count=totals.length;
  5255 |         return {gap:Math.max(...totals)-Math.min(...totals),deviation:totals.reduce((total,value)=>total+Math.abs(value*count-sum),0)};
  5256 |       }
  5257 |       function randomAssignmentContextSignature() {
  5258 |         const targets=assignmentTargets().map(item=>[item.id,item.room,item.kind,targetPlanDate(item),targetEffectiveDate(item),item.carryReason||'',item.rolloverCount||0,item.reservationId||'',item.guestCount??'',item.checkout||'',item.checkin||'',item.deadline||'',item.accessStart||'',item.requestDue||'',item.accessEnd||'',assignmentTargetElevator(item)||'',assignmentTargetRate(item),assignmentTargetMinutes(item)].join(':')).sort().join('|'),availability=eligibleAssignmentMaids().map(maid=>maid.id).sort().join('|');
  5259 |         return `${state.assignmentDate}::${targets}::${availability}`;
  5260 |       }
  5261 |       function assignmentTargetReleaseMinutes(item) { return timeMinutes(item.accessStart||item.checkout||'00:00'); }
  5262 |       function assignmentTargetDueMinutes(item) {
  5263 |         const values=[item.requestDue,item.deadline,item.accessEnd].filter(Boolean).map(timeMinutes).filter(Number.isFinite);return values.length?Math.min(...values):1439;
  5264 |       }
  5265 |       function assignmentRouteFinish(items) {
  5266 |         return items.reduce((finish,item)=>Math.max(finish,assignmentTargetReleaseMinutes(item))+assignmentTargetMinutes(item),0);
  5267 |       }
  5268 |       function assignmentRandomGenerator() {
  5269 |         let seed=(Date.now()^Math.floor(Math.random()*4294967296))>>>0;
  5270 |         if(globalThis.crypto?.getRandomValues){const value=new Uint32Array(1);globalThis.crypto.getRandomValues(value);seed=value[0]||seed;}
  5271 |         if(!seed)seed=0x9e3779b9;
  5272 |         return ()=>{seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296;};
  5273 |       }
  5274 |       function assignmentProximity(item,items) {
  5275 |         if(!items.length)return {zoneRank:1,roomDistance:0};
  5276 |         const zone=assignmentTargetElevator(item),number=Number(item.room)||0,known=items.filter(other=>assignmentTargetElevator(other)),same=known.filter(other=>assignmentTargetElevator(other)===zone),pool=same.length?same:known.length?known:items;
  5277 |         return {zoneRank:zone&&same.length?0:zone&&known.length?2:3,roomDistance:Math.min(...pool.map(other=>Math.abs(number-(Number(other.room)||0))))};
  5278 |       }
  5279 |       function randomAssignmentTrial(eligible,targets,random) {
```

## 객실별 담당 수정: `객실별 담당 수정`

matches: 1

### occurrence 1 · line 5361

```html
  5316 |         const snapshot=state.randomAssignmentSnapshot;if(!snapshot)return false;
  5317 |         Object.entries(snapshot.afterAssignments||{}).forEach(([targetId,after])=>{if(JSON.stringify(state.assignments[targetId]||null)!==JSON.stringify(after))return;const before=snapshot.beforeAssignments?.[targetId];if(before)state.assignments[targetId]=JSON.parse(JSON.stringify(before));else delete state.assignments[targetId];});
  5318 |         MAIDS.forEach(maid=>normalizeAssignmentOrderFor(maid.id));state.randomAssignments={};state.randomAssignmentSnapshot=null;state.randomAssignmentSummary=null;return true;
  5319 |       }
  5320 |       function randomAssignmentNote(item) {
  5321 |         const random=state.randomAssignments?.[item.id],assignment=assignmentFor(item);
  5322 |         if(!random||random.maidId!==assignment.maidId)return '';
  5323 |         return `<span class="assignment-random-note">${icon('sync','icon-sm')}랜덤 배정 · ${esc(random.reason)}</span>`;
  5324 |       }
  5325 |       function assignmentSchedulePriorityBadges(item) {
  5326 |         const context=assignmentContext(item),badges=[];
  5327 |         if(item.source==='stayover')badges.push(`<span class="schedule-priority-badge stayover">${icon('clock','icon-sm')}연박 청소 · 출입 ${esc(item.accessStart)}–${esc(item.accessEnd)}</span>`);
  5328 |         if(context.early)badges.push(`<span class="schedule-priority-badge">${icon('clock','icon-sm')}얼리 체크인 ${esc(context.checkin)} · ${esc(context.earlyOffset)} 빠름</span>`);
  5329 |         if(context.late)badges.push(`<span class="schedule-priority-badge late">${icon('clock','icon-sm')}레이트 체크아웃 ${esc(context.checkout)} · ${esc(context.lateOffset)} 늦음</span>`);
  5330 |         return badges;
  5331 |       }
  5332 |       function assignmentScheduleMarkup(item) {
  5333 |         const special=assignmentSchedulePriorityBadges(item),guestCount=assignmentGuestCount(item);
  5334 |         const primary=`${item.source==='stayover'?`요청 완료 ${esc(item.requestDue||item.deadline||'—')}`:`체크아웃 ${esc(item.checkout||'—')} → 준비 마감 ${esc(item.deadline||'—')}`}${guestCount?` · 숙박 ${guestCountLabel(guestCount)}`:''}`;
  5335 |         return `<div class="assignment-schedule"><strong>${primary}</strong>${item.carryReason?`<span class="assignment-rollover-plan">원 계획 ${esc(dateLabel(targetPlanDate(item)))} · 이월 ${Number(item.rolloverCount)||1}일째</span>`:special.length?`<div class="assignment-schedule-badges">${special.join('')}</div>`:'<span class="assignment-normal">특수 입퇴실 없음</span>'}</div>`;
  5336 |       }
  5337 |       function assignmentScheduleText(item) {
  5338 |         const context=assignmentContext(item),parts=[];
  5339 |         if(item.source==='stayover')parts.push(`연박 출입 ${item.accessStart}–${item.accessEnd} → ${item.requestDue} 요청 완료`);
  5340 |         else parts.push(`체크아웃 ${item.checkout||'—'} → 준비 마감 ${item.deadline||'—'}`);
  5341 |         if(assignmentGuestCount(item))parts.push(`숙박 인원 ${guestCountLabel(assignmentGuestCount(item))}`);
  5342 |         if(context.early)parts.push(reservationStatusText(context,'checkin'));
  5343 |         if(context.late)parts.push(reservationStatusText(context,'checkout'));
  5344 |         return parts.join(' · ');
  5345 |       }
  5346 |       function assignmentSourceMarkup(item) {
  5347 |         const cls=item.source==='manual'?'manual':item.source==='stayover'?'stayover':'',label=item.sourceLabel||'직접 등록';
  5348 |         const rollover=item.carryReason?`<span class="assignment-source stayover">${icon('clock','icon-sm')}${item.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료'}</span>`:'';
  5349 |         return `${rollover}<span class="assignment-source ${cls}">${icon(item.source==='manual'?'user':'sync','icon-sm')}${item.source==='manual'?'직접 등록':`자동 · ${esc(label)}`}</span>`;
  5350 |       }
  5351 |       function assignmentAdjustmentMarkup(item) {
  5352 |         const assignment=assignmentFor(item),activationBlocked=!!assignment.activationBlockedBy&&targetEffectiveDate(item)===state.selectedDate,status=activationBlocked?'활성화 보류':assignment.status==='notified'?'통보 완료':assignment.maidId?'저장 전':'미배정',tone=activationBlocked?'amber':assignment.status==='notified'?'green':assignment.maidId?'amber':'red',notified=!!(assignment.previousMaidId||assignment.status==='notified'),block=cleaningTargetAdjustmentBlock(item),label=notified?'청소 취소·통보':'청소대상 취소';
  5353 |         return `<div class="assignment-cell-stack">${statusBadge(status,tone)}${assignment.maidId?'<span class="cell-sub">순서 보드 반영</span>':''}${button(label,'cancel-cleaning-target','outline',`data-target="${esc(item.id)}" aria-label="${esc(dateLabel(targetEffectiveDate(item)))} ${item.room}호 ${esc(label)}" ${block?'disabled':''}`)}${block?`<span class="cell-sub">${esc(block)}</span>`:''}</div>`;
  5354 |       }
  5355 |       function renderAssignmentDashboard() {
  5356 |         const counts=assignmentCounts(),targets=assignmentTargets(),visibleTargets=filteredAssignmentTargets(),activeType=state.assignmentTypeFilter==='all'?null:ROOM_TYPES[state.assignmentTypeFilter];
  5357 |         const rows=visibleTargets.map(item=>{const context=assignmentContext(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item);return `<tr><td data-label="객실·타입·요금"><div class="assignment-cell-stack"><strong>${item.room}호</strong><span class="assignment-room-type">${esc(context.type.name)}</span><span class="assignment-elevator">${icon('mapPin','icon-sm')}${esc(elevatorLabel(context.room))}</span><span class="assignment-fee">${money(context.type.rate)} · 8월 시트</span></div></td><td data-label="청소 정보"><div class="assignment-cell-stack"><strong>${esc(item.kind)}</strong>${assignmentSourceMarkup(item)}</div></td><td data-label="일정">${assignmentScheduleMarkup(item)}</td><td data-label="담당 메이드"><div class="assignment-assignee"><select class="select-control" data-control="assignment-maid" data-location="table" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 · 근무 가능 제출자만 표시" ${adjustmentBlock?'disabled':''}>${assignmentOptions(item)}</select>${assignmentRouteReference(item)}</div></td><td data-label="상태·조정">${assignmentAdjustmentMarkup(item)}</td></tr>`;}).join('');
  5358 |         const history=state.assignmentHistory.map(entry=>`<div class="assignment-history-row"><strong>${esc(entry.time)}</strong><span>${esc(entry.room)}호</span><span>${esc(entry.before)} → ${esc(entry.after)}</span><span>${esc(entry.reason)}</span></div>`).join('');
  5359 |         const emptyRows=`<tr><td colspan="5"><div class="inline-empty"><h3>이 타입의 청소대상이 없습니다</h3><p>다른 타입을 선택하거나 전체 객실을 확인하세요.</p></div></td></tr>`;
  5360 |         const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일',weekStart=weekStartIso(state.assignmentDate),weekEnd=addIsoDays(weekStart,6);
  5361 |         return `<div class="assignment-page"><div class="assignment-intro"><div><h2>${dayWord} 청소 배정</h2><p>${dateLabel(state.assignmentDate)} · 근무표 확인 → 동선 고려 랜덤 초안 → 담당·순서 수정 → 저장·통보</p></div><div class="job-actions">${button('주간 근무 기록','go-work-history','outline')}${button(`${dayWord} 청소 추가`,'new-cleaning','outline')}</div></div><section class="card assignment-summary"><div><span>근무 가능일 제출</span><strong>${counts.submitted} / ${MAIDS.length}</strong><small>메이드 제출 현황</small></div><div><span>${dayWord} 청소 대상 객실</span><strong>${counts.total}</strong><small>전일 이월 ${counts.carryover} · 신규 ${counts.total-counts.carryover}</small></div><div class="summary-good"><span>담당 선택</span><strong>${counts.assigned}</strong><small>통보 완료 ${counts.notified}건</small></div><div class="summary-warn"><span>미배정</span><strong>${counts.unassigned}</strong><small>대기 유지 · 후속 배정 가능</small></div></section><section class="assignment-target-rule" aria-label="청소대상 자동 구성">${icon('sync')}<div><strong>${dayWord} 체크아웃·투숙 중 청소·전일 이월 객실을 한 목록에 모읍니다.</strong><p>${dayWord} 생긴 현장 요청은 직접 추가하고, 미시작 대상은 사유를 남겨 취소·통보할 수 있습니다.</p></div><div class="badge-row">${statusBadge(`전일 이월 ${counts.carryover}`,'amber')}${statusBadge(`체크아웃 ${counts.checkout}`,'blue')}${statusBadge(`연박 ${counts.stayover}`,'neutral')}${statusBadge(`직접 ${counts.manual}`,'amber')}</div></section><section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>${dateLabel(weekStart)}–${dateLabel(weekEnd)} · Asia/Seoul</p></div>${statusBadge(`${counts.submitted}/${MAIDS.length} 제출`,counts.submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section>${renderRandomAssignmentCard()}<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">3단계 · 세부 수정</span><h3>객실별 담당 수정</h3><p>랜덤 초안 뒤 필요한 객실만 조정합니다. 얼리·레이트·연박 일정은 해당 객실 행에서 함께 확인합니다.</p></div>${statusBadge(`${visibleTargets.length}/${targets.length}건 표시`,'blue')}</div>${assignmentTypeFiltersMarkup()}<div class="assignment-filter-context">${icon('filter','icon-sm')}<span><strong>${activeType?esc(activeType.name):'전체 객실 타입'}</strong> ${visibleTargets.length}건 표시 · 전체 ${targets.length}건 현황을 유지하며 배정된 객실만 통보합니다.</span></div><div class="assignment-table-wrap"><table class="assignment-table"><thead><tr><th scope="col">객실·타입·요금</th><th scope="col">청소 정보·등록 근거</th><th scope="col">일정</th><th scope="col">담당 메이드</th><th scope="col">상태·조정</th></tr></thead><tbody>${rows||emptyRows}</tbody></table></div><div class="assignment-foot"><p>담당을 바꾸면 해당 객실이 새 메이드 순서의 마지막으로 이동합니다. 이미 시작한 청소는 진행 중 탭에서 관리합니다.</p></div></section>${renderMaidOrderBoardContent()}<section class="card assignment-history"><div class="assignment-panel-head"><div><h3>배정·순서 통보 이력</h3><p>담당과 청소 순서의 이전 값을 덮어쓰지 않고 변경 이력을 추가합니다.</p></div>${statusBadge('관리자 전용','neutral')}</div><div class="assignment-history-list">${history}</div></section></div>`;
  5362 |       }
  5363 |       function cleaningTabButton(id,label,count) { return `<button type="button" role="tab" data-action="cleaning-tab" data-tab="${id}" aria-selected="${state.cleaningTab===id}">${label} ${count}</button>`; }
  5364 |       function rolloverMetaForRoom(no) {
  5365 |         const attempt=state.cleaningAttempts?.[currentAttemptId(no)];if(attemptIsRollover(attempt))return {carryReason:attempt.carryReason||'started-unfinished',planDate:attemptPlanDate(attempt),effectiveDate:attemptEffectiveDate(attempt),rolloverCount:Number(attempt.rolloverCount)||1};
  5366 |         const target=Object.values(state.cleaningTargets||{}).find(item=>item.room===no&&item.carryReason&&!item.closed);return target?{carryReason:target.carryReason,planDate:targetPlanDate(target),effectiveDate:targetEffectiveDate(target),rolloverCount:Number(target.rolloverCount)||1}:null;
  5367 |       }
  5368 |       function rolloverBadgeMarkup(meta,{compact=false}={}) {
  5369 |         if(!meta)return '';
  5370 |         const label=meta.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료',detail=`원 계획 ${dateLabel(meta.planDate)} · 이월 ${meta.rolloverCount}일째`;
  5371 |         return `<div class="badge-row${compact?' compact':''}" style="margin-top:7px">${statusBadge(label,'amber')}<span class="cell-sub">${esc(detail)}</span></div>`;
  5372 |       }
  5373 |       function cleaningProgressEntries() {
  5374 |         const allowed=['scheduled','claimed','cleaning','upload','reclean','hold'];
  5375 |         return Object.entries(state.jobs).filter(([no,job])=>{
  5376 |           if(!allowed.includes(job))return false;
  5377 |           const rollover=rolloverMetaForRoom(no);
  5378 |           return !rollover||rollover.carryReason==='started-unfinished'||!!activeUnfinishedAttempt(no);
  5379 |         });
  5380 |       }
  5381 |       function renderCleaningHub() {
  5382 |         const todayDate=state.selectedDate,tomorrowDate=addIsoDays(state.selectedDate,1),tabCounts={today:assignmentCountsForDate(todayDate).total,tomorrow:assignmentCountsForDate(tomorrowDate).total,progress:cleaningProgressEntries().length,inspection:Object.values(state.jobs).filter(v=>v==='inspection').length,done:Object.values(state.jobs).filter(v=>v==='approved').length};
  5383 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>청소 관리</h2><p>오늘 운영 조정과 내일 사전 배정을 분리하고, 변경 내용은 해당 메이드에게 다시 알립니다.</p></div></div><div class="tabs" role="tablist" aria-label="청소 상태">${cleaningTabButton('assignment-today','오늘 배정',tabCounts.today)}${cleaningTabButton('assignment-tomorrow','내일 배정',tabCounts.tomorrow)}${cleaningTabButton('progress','진행 중',tabCounts.progress)}${cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)}${cleaningTabButton('done','완료',tabCounts.done)}</div>${renderListState(renderCleaningTab())}</div>`;
  5384 |       }
  5385 |       function taskRow(no,job,extra='') {
  5386 |         const room=ROOMS.find(r=>r.no===no),liveType=ROOM_TYPES[room?.type||'standard'],validSubmission=currentSubmission(no),submittedContext=['inspection','approved'].includes(job),submission=submittedContext?(validSubmission||currentSubmissionRecord(no)):validSubmission,submissionMeta=submission?.roomMetaSnapshot,displayType=submittedContext?(ROOM_TYPES[submissionMeta?.typeId]||liveType):liveType,displayTypeName=submittedContext?(submissionMeta?.typeName||displayType.name):displayType.name,displayElevator=submittedContext?(submissionMeta?.elevator?`${submissionMeta.elevator} 엘리베이터`:'엘리베이터 미기재'):elevatorLabel(room),activeAttempt=state.cleaningAttempts?.[currentAttemptId(no)],rollover=rolloverMetaForRoom(no),report=submittedContext?(validSubmission?submittedBombRoomReport(no):rawBombRoomReportForSubmission(submission)):activeBombRoomReport(no),record=submittedContext?earningRecordFor(no):earningRecordForReport(report),wholeRejected=submittedContext&&submission?.status==='rejected',unpaidReclean=submittedContext?submission?.kind==='재청소':activeAttempt?.kind==='재청소',bombMeta=wholeRejected?{label:'청소 전체 반려 · 적립 없음',tone:'red'}:bombRoomStatusMeta(report),fee=record||bombRoomBreakdown(no,{pendingAsBonus:!unpaidReclean&&(submittedContext?submission?.status==='pending':true)&&report?.status==='pending',reportOverride:report,baseOverride:submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot}),performer=submittedContext?submission?.performerName:room?.assignee;
  5387 |         const displayRate=unpaidReclean?0:record?.base??(submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot)??displayType.rate,displayKind=(submittedContext?submission?.kind:activeAttempt?.kind)||(job==='reclean'?'재청소':'퇴실 청소');
  5388 |         const action=job==='inspection'?['전체 검수','cleaning-detail']:job==='approved'?['결과 보기','cleaning-detail']:['진행 보기','cleaning-detail'];
  5389 |         return `<article class="card task-row"><div><h3>${no}호 · ${esc(displayKind)} · ${statusLabel(job)}</h3><p>${esc(displayTypeName)} · ${esc(displayElevator)} · ${money(displayRate)} · ${submission?.templateSnapshot?.minutes??displayType.minutes}분 · 데모</p>${rolloverBadgeMarkup(rollover,{compact:true})}${submittedContext&&!validSubmission?`<div class="badge-row" style="margin-top:7px">${statusBadge('제출 연결 확인 필요','red')}</div>`:''}${report?`<div class="badge-row" style="margin-top:7px">${statusBadge(bombMeta.label,bombMeta.tone)}<span class="cell-sub">${wholeRejected?'적립':record?'확정':report.status==='pending'?'폭탄방 승인 시':'전체 승인 시'} ${money(wholeRejected?0:fee.total)}</span></div>`:unpaidReclean?`<div class="badge-row" style="margin-top:7px">${statusBadge('본인 재청소 · 무급','neutral')}<span class="cell-sub">수익 원장 없음 · 0원</span></div>`:''}${extra}</div><div class="task-meta"><span>일정</span><strong>${room?.checkout||'11:00'} → ${room?.checkin||'16:00'}</strong></div><div class="task-meta"><span>${submittedContext?'수행자':'담당'}</span><strong>${esc(performer||'미정')}</strong></div><div class="task-row-action">${button(action[0],action[1],job==='inspection'?'primary':'outline',`data-id="${no}"`)}</div></article>`;
  5390 |       }
  5391 |       function renderCleaningTab() {
  5392 |         if(isCleaningAssignmentTab(state.cleaningTab))return renderAssignmentDashboard();
  5393 |         const allowed=state.cleaningTab==='progress'?['scheduled','claimed','cleaning','upload','reclean','hold']:state.cleaningTab==='inspection'?['inspection']:['approved'];
  5394 |         const entries=state.cleaningTab==='progress'?cleaningProgressEntries():Object.entries(state.jobs).filter(([,v])=>allowed.includes(v)),rows=entries.map(([no,v])=>taskRow(no,v)).join('');
  5395 |         return `<div class="tab-panel">${rows||`<section class="inline-empty"><h3>이 상태의 작업이 없습니다</h3><p>다른 탭에서 진행 상태를 확인하세요.</p></section>`}</div>`;
  5396 |       }
  5397 | 
  5398 |       function addIsoDays(iso,offset) {
  5399 |         const [year,month,day]=iso.split('-').map(Number),date=new Date(Date.UTC(year,month-1,day+offset));
  5400 |         return `${date.getUTCFullYear()}-${String(date.getUTCMonth()+1).padStart(2,'0')}-${String(date.getUTCDate()).padStart(2,'0')}`;
  5401 |       }
  5402 |       function weekStartIso(iso) {
  5403 |         const [year,month,day]=String(iso).split('-').map(Number),date=new Date(Date.UTC(year,month-1,day)),mondayOffset=-((date.getUTCDay()+6)%7);
  5404 |         return addIsoDays(iso,mondayOffset);
  5405 |       }
  5406 |       function timestampIsoDate(value,fallback=state.selectedDate) {
  5407 |         const match=String(value||'').match(/(\d{4})[.-](\d{1,2})[.-](\d{1,2})/);
  5408 |         return match?`${match[1]}-${String(Number(match[2])).padStart(2,'0')}-${String(Number(match[3])).padStart(2,'0')}`:fallback;
  5409 |       }
  5410 |       function shortIsoDate(iso) {
  5411 |         const [,month,day]=iso.split('-').map(Number);return `${month}/${day}`;
  5412 |       }
  5413 |       function completedWorkDaysForWeek(start,maidId) {
  5414 |         return [...new Set(Object.values(state.cleaningAttempts||{}).filter(attempt=>{
  5415 |           const completedDate=attempt?.completedAt?timestampIsoDate(attempt.completedAt,''):'';
  5416 |           return attempt?.performerId===maidId&&completedDate&&weekStartIso(completedDate)===start;
  5417 |         }).map(attempt=>weekdayIndex(timestampIsoDate(attempt.completedAt))))].sort((left,right)=>left-right);
  5418 |       }
  5419 |       function assignedWorkDaysForWeek(start,maidId) {
  5420 |         const days=[];
  5421 |         if(start==='2026-08-17'&&notifiedAssignmentEntriesForMaid(maidId).length)days.push(assignmentDayIndex());
  5422 |         (state.assignmentHistory||[]).forEach(entry=>{
  5423 |           if(entry.assignmentDate&&weekStartIso(entry.assignmentDate)===start&&(entry.beforeMaidId===maidId||entry.afterMaidId===maidId))days.push(weekdayIndex(entry.assignmentDate));
  5424 |         });
  5425 |         return [...new Set(days)].sort((left,right)=>left-right);
  5426 |       }
  5427 |       function currentWorkHistoryWeek() {
  5428 |         const records={};
  5429 |         MAIDS.forEach(maid=>{
  5430 |           const versions=(state.availabilityHistory||[]).filter(item=>item.maidId===maid.id&&item.weekStart==='2026-08-17').sort((left,right)=>left.version-right.version),latest=versions.at(-1),current=state.weeklyAvailability[maid.id],availability=latest||(['submitted','change-requested'].includes(current?.status)?current:{days:[],status:'unsubmitted',submittedAt:null});
```

## 객실 정보 없음: `객실 정보 없음`

matches: 2

### occurrence 1 · line 4386

```html
  4341 |       function startQuickReservationTodayWatch() {
  4342 |         if(quickReservationTodayWatchTimer)return;
  4343 |         quickReservationTodayWatchTimer=window.setInterval(()=>refreshQuickReservationActualToday({rerender:true}),30000);
  4344 |       }
  4345 |       startQuickReservationTodayWatch();
  4346 |       function shiftIsoDate(iso,offset) { const value=dateObject(iso);value.setDate(value.getDate()+Number(offset||0));return dateIso(value); }
  4347 |       function quickWindowBounds(anchor=state.quickReservationAnchorDate) {
  4348 |         const start=shiftIsoDate(anchor,-QUICK_RESERVATION_PAST_DAYS),end=shiftIsoDate(anchor,QUICK_RESERVATION_FUTURE_DAYS);
  4349 |         return {start,end,endExclusive:shiftIsoDate(end,1)};
  4350 |       }
  4351 |       function quickWindowDates(anchor=state.quickReservationAnchorDate) {
  4352 |         const {start}=quickWindowBounds(anchor);
  4353 |         return Array.from({length:QUICK_RESERVATION_DAY_COUNT},(_,index)=>shiftIsoDate(start,index));
  4354 |       }
  4355 |       function quickCompactDate(iso,{year=false}={}) {
  4356 |         const value=dateObject(iso),prefix=year?`${value.getFullYear()}.`:'';
  4357 |         return `${prefix}${value.getMonth()+1}.${value.getDate()}`;
  4358 |       }
  4359 |       function quickWindowLabel(anchor=state.quickReservationAnchorDate) {
  4360 |         const {start,end}=quickWindowBounds(anchor),differentYear=dateObject(start).getFullYear()!==dateObject(end).getFullYear();
  4361 |         return `${quickCompactDate(start,{year:differentYear})}–${quickCompactDate(end,{year:differentYear})}`;
  4362 |       }
  4363 |       function quickHeaderDateLabel(iso,index=0) {
  4364 |         const value=dateObject(iso);
  4365 |         return index===0||value.getDate()===1?`${value.getMonth()+1}/${value.getDate()}`:`${value.getDate()}일`;
  4366 |       }
  4367 |       function quickDateLabel(iso) { const value=dateObject(iso),day=CALENDAR_WEEKDAYS[value.getDay()];return `${value.getMonth()+1}월 ${value.getDate()}일 (${day})`; }
  4368 |       function quickRangeLabel(reservation) {
  4369 |         const start=dateObject(reservation.checkInAt.slice(0,10)),end=dateObject(reservation.checkOutAt.slice(0,10));
  4370 |         return `${start.getMonth()+1}/${start.getDate()} ${reservation.checkInAt.slice(11,16)} → ${end.getMonth()+1}/${end.getDate()} ${reservation.checkOutAt.slice(11,16)}`;
  4371 |       }
  4372 |       function reservationMomentLabel(value) {
  4373 |         if(!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(value||''))return '일정 없음';
  4374 |         const [year,month,day]=value.slice(0,10).split('-').map(Number);
  4375 |         return `${month}/${day} ${value.slice(11,16)}`;
  4376 |       }
  4377 |       function reservationInQuickWindow(reservation,anchor=state.quickReservationAnchorDate) {
  4378 |         const {start,endExclusive}=quickWindowBounds(anchor);
  4379 |         return reservation.status==='active'&&reservation.checkInAt<`${endExclusive}T00:00`&&reservation.checkOutAt>`${start}T00:00`;
  4380 |       }
  4381 |       function quickFilteredRooms() {
  4382 |         const query=state.quickReservationSearch.trim();
  4383 |         return ROOMS.filter(room=>!query||room.no.includes(query)).filter(room=>state.quickReservationType==='all'||room.type===state.quickReservationType);
  4384 |       }
  4385 |       function reservationHardBlockReason(room) {
  4386 |         if(!room)return '객실 정보 없음';
  4387 |         if(isLocked())return state.network==='offline'?'오프라인 · 예약 등록 잠금':'오래된 데이터 · 예약 등록 잠금';
  4388 |         if(roomIsOnHold(room.no))return '확인 필요 · 예약 불가';
  4389 |         if(state.roomStopped[room.no])return `운영 중지 · ${state.roomStopReasons[room.no]||'예약 불가'}`;
  4390 |         return '';
  4391 |       }
  4392 |       function quickRoomBlockReason(room) { return reservationHardBlockReason(room); }
  4393 |       function currentOccupiedReservation(room) {
  4394 |         if(!room||room.occupancy!=='occupied')return null;
  4395 |         const pivot=reservationCurrentMoment(),reservations=activeReservationsFor(state,room.no),linked=room.currentStayReservationId?reservations.find(reservation=>reservation.id===room.currentStayReservationId):null,contained=reservations.find(reservation=>reservation.checkInAt<=pivot&&reservation.checkOutAt>pivot);
  4396 |         if(linked)return linked;
  4397 |         if(contained)return contained;
  4398 |         const actualCheckinAt=room.actualCheckinAt||'';
  4399 |         return reservations.find(reservation=>actualCheckinAt&&reservation.checkInAt<=actualCheckinAt&&reservation.checkOutAt>actualCheckinAt)||reservations.find(reservation=>reservation.id===room.reservationProjectionId&&reservation.checkInAt<=pivot)||null;
  4400 |       }
  4401 |       function occupiedReservationEnd(room) {
  4402 |         const current=currentOccupiedReservation(room);
  4403 |         return room?.actualCheckoutAt||room?.plannedCheckoutAt||current?.checkOutAt||'';
  4404 |       }
  4405 |       function occupiedStayNeedsCheckoutUpdate(room) {
  4406 |         const knownEnd=occupiedReservationEnd(room);
  4407 |         return !!(room?.occupancy==='occupied'&&knownEnd&&knownEnd<=reservationCurrentMoment());
  4408 |       }
  4409 |       function suggestedReservationStartDate(roomNo) {
  4410 |         const room=ROOMS.find(item=>item.no===String(roomNo));
  4411 |         if(!room)return state.selectedDate;
  4412 |         const knownEnd=occupiedReservationEnd(room),current=currentOccupiedReservation(room);
  4413 |         let candidate=(current||room.occupancy==='occupied')?(knownEnd?knownEnd.slice(0,10):shiftIsoDate(state.selectedDate,1)):state.selectedDate;
  4414 |         if(candidate<state.selectedDate)candidate=state.selectedDate;
  4415 |         for(let index=0;index<370;index+=1){
  4416 |           const checkInAt=`${candidate}T${DEFAULT_CHECKIN_TIME}`,checkOutAt=`${shiftIsoDate(candidate,1)}T${DEFAULT_CHECKOUT_TIME}`,overlap=reservationOverlaps(room.no,checkInAt,checkOutAt);
  4417 |           if((!knownEnd||checkInAt>=knownEnd)&&!overlap)return candidate;
  4418 |           const nextDate=overlap?.checkOutAt?.slice(0,10)||shiftIsoDate(candidate,1);candidate=nextDate>candidate?nextDate:shiftIsoDate(candidate,1);
  4419 |         }
  4420 |         return shiftIsoDate(state.selectedDate,1);
  4421 |       }
  4422 |       function quickOccupiedDateBlockReason(room,iso) {
  4423 |         if(!room||room.occupancy!=='occupied')return '';
  4424 |         const knownEnd=occupiedReservationEnd(room);
  4425 |         if(!knownEnd)return '투숙 중 · 체크아웃 일정 미입력';
  4426 |         if(occupiedStayNeedsCheckoutUpdate(room))return '투숙 중 · 예정 체크아웃 경과, 현재 예약을 먼저 갱신';
  4427 |         if(knownEnd&&iso<knownEnd.slice(0,10))return `투숙 중 · ${quickDateLabel(knownEnd.slice(0,10))} ${knownEnd.slice(11,16)} 퇴실 전`;
  4428 |         return '';
  4429 |       }
  4430 |       function reservationForNight(roomNo,iso) { return activeReservationsFor(state,roomNo).find(reservation=>reservationContainsNight(reservation,iso))||null; }
  4431 |       function cleaningAssignmentForReservation(reservation) {
  4432 |         if(!reservation)return {name:'청소 미배정',status:'미배정',maidId:null,assigned:false};
  4433 |         const checkoutDate=reservation.checkOutAt.slice(0,10),expectedId=`checkout-${reservation.room}-${checkoutDate}`;
  4434 |         const liveTarget=liveAssignmentTargets().find(target=>target.reservationId===reservation.id||(target.room===reservation.room&&target.kind==='퇴실 청소'&&(target.date===checkoutDate||target.id===expectedId||target.id.includes(checkoutDate)))),entry=liveTarget&&state.assignments?.[liveTarget.id]?[liveTarget.id,state.assignments[liveTarget.id]]:Object.entries(state.assignments||{}).find(([id,record])=>id===expectedId||(record?.committedTarget?.room===reservation.room&&(record.committedTarget.date===checkoutDate||id.includes(checkoutDate)||record.committedTarget.id===expectedId))),record=entry?.[1];
  4435 |         const maidId=record?.maidId||record?.previousMaidId||null;
  4436 |         if(!maidId)return {name:'청소 미배정',status:'미배정',maidId:null,assigned:false};
  4437 |         const status=record.status==='notified'?'통보 완료':record.status==='draft'?'저장 전':record.status==='cancelled'?'취소됨':'배정됨';
  4438 |         return {name:maidName(maidId),status,maidId,assigned:record.status!=='cancelled'};
  4439 |       }
  4440 |       function quickBookingTimes(firstNight,lastNight) {
  4441 |         const ordered=[firstNight,lastNight].sort();
  4442 |         return {firstNight:ordered[0],lastNight:ordered[1],checkInAt:`${ordered[0]}T${DEFAULT_CHECKIN_TIME}`,checkOutAt:`${shiftIsoDate(ordered[1],1)}T${DEFAULT_CHECKOUT_TIME}`};
  4443 |       }
  4444 |       function quickReservationConflict(roomNo,firstNight,lastNight,ignoreId='',actualCheckInAt='',actualCheckOutAt='',registeringCurrentStay=false) {
  4445 |         const room=ROOMS.find(item=>item.no===String(roomNo)),range=quickBookingTimes(firstNight,lastNight),checkInAt=actualCheckInAt||range.checkInAt,checkOutAt=actualCheckOutAt||range.checkOutAt;
  4446 |         if(!adminCanMutate())return {reason:'관리자 최신 온라인 상태에서만 예약할 수 있습니다.',date:range.firstNight};
  4447 |         const rowReason=reservationHardBlockReason(room);if(rowReason)return {reason:rowReason,date:range.firstNight};
  4448 |         const cursor=dateObject(range.firstNight),end=dateObject(range.lastNight),currentReservation=currentOccupiedReservation(room),editingProjectedStay=!!(ignoreId&&currentReservation?.id===ignoreId),knownOccupancyEnd=occupiedReservationEnd(room);
  4449 |         if(!editingProjectedStay&&!registeringCurrentStay&&room.occupancy==='occupied'&&!knownOccupancyEnd)return {reason:'투숙 중 · 체크아웃 일정을 먼저 입력해 주세요.',date:checkInAt.slice(0,10)};
  4450 |         if(!editingProjectedStay&&!registeringCurrentStay&&occupiedStayNeedsCheckoutUpdate(room))return {reason:'투숙 중 · 예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.',date:checkInAt.slice(0,10)};
  4451 |         if(!editingProjectedStay&&room.occupancy==='occupied'&&knownOccupancyEnd&&checkInAt<knownOccupancyEnd)return {reason:`투숙 중 · ${quickDateLabel(knownOccupancyEnd.slice(0,10))} ${knownOccupancyEnd.slice(11,16)} 체크아웃 전`,date:checkInAt.slice(0,10)};
  4452 |         while(cursor<=end){const iso=dateIso(cursor),occupiedReason=editingProjectedStay||registeringCurrentStay?'':quickOccupiedDateBlockReason(room,iso),existing=reservationForNight(roomNo,iso);if(occupiedReason)return {reason:occupiedReason,date:iso};if(existing&&existing.id!==ignoreId)return {reason:`기존 예약 · ${quickRangeLabel(existing)}`,date:iso,reservation:existing};cursor.setDate(cursor.getDate()+1);}
  4453 |         const overlap=reservationOverlaps(roomNo,checkInAt,checkOutAt,ignoreId);if(overlap)return {reason:`기존 예약 · ${quickRangeLabel(overlap)}`,date:overlap.checkInAt.slice(0,10),reservation:overlap};
  4454 |         return null;
  4455 |       }
```

### occurrence 2 · line 7096

```html
  7051 |           room.occupancy='vacant';room.plannedCheckoutAt=plannedCheckout==='미입력'?null:plannedCheckout;room.actualCheckoutAt=actualCheckoutAt;delete room.currentStayReservationId;delete room.stayoverRequest;projectReservationState(state,id);room.checkout=`${state.time} 완료`;room.checkin=room.nextCheckinAt?room.nextCheckinAt.slice(11,16):'예정 없음';if(!unstartedAttempt){room.assignee='미정';state.jobs[id]='draft';}state.candles[id]=0;
  7052 |           const cleaningResult=unstartedAttempt?`기존 ${unstartedAttempt.performerName} 담당·${unstartedAttempt.id} 회차 유지`:'퇴실 청소 초안 1건';
  7053 |           appendEvent(`${id}호 지금 체크아웃`,`${dateLabel(state.selectedDate)} ${state.time} 실제 퇴실 · 예정 ${plannedCheckout} 보존 · ${cleaningResult}${activeReservation?` · 예약 ${activeReservation.id} 실제 종료`:''}${cancelledStayover||cancelledStayoverTargets?' · 미시작 투숙 중 청소 요청 종료':''}`,{roomId:id});
  7054 |           closeModal();render();focusAfterRender(`[data-action="room-detail"][data-id="${id}"]`);toast(unstartedAttempt?`${id}호를 공실로 바꾸고 기존 청소 담당·회차의 시작 시각을 갱신했습니다.`:`${id}호를 공실·청소 필요로 바꾸고 퇴실 청소 초안을 연결했습니다.`);return;
  7055 |         }
  7056 |         if(a==='manual-checkin'){openManualCheckin(id,el);return;}
  7057 |         if(a==='confirm-manual-checkin'){
  7058 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',presentation=roomPresentation(id);
  7059 |           if(!adminCanMutate()||!room||roomIsOnHold(id)||room.occupancy!=='vacant'||roomMasterFingerprint(room)!==expected||presentation.available!==true){closeModal();render();toast('객실 준비 상태 또는 관리자 최신 상태가 바뀌어 투숙을 시작하지 않았습니다.','error');return;}
  7060 |           const actualCheckinAt=`${state.selectedDate}T${state.time}`,linkedReservation=activeReservationsFor(state,id).find(reservation=>reservation.checkInAt.slice(0,10)===state.selectedDate&&reservation.checkOutAt>actualCheckinAt)||activeReservationsFor(state,id).find(reservation=>reservation.id===room.reservationProjectionId)||null;
  7061 |           room.occupancy='occupied';room.actualCheckinAt=actualCheckinAt;room.currentStayReservationId=linkedReservation?.id||null;room.plannedCheckoutAt=linkedReservation?.checkOutAt||room.reservationCheckoutAt||room.nextCheckoutAt||null;delete room.actualCheckoutAt;room.checkin=`${state.time} 입실`;appendEvent(`${id}호 투숙 시작`,`${dateLabel(state.selectedDate)} ${state.time} · 고객 개인정보 미기록`,{roomId:id});
  7062 |           closeModal();render();focusAfterRender(`[data-action="manual-checkout"][data-id="${id}"]`);toast(`${id}호를 투숙 중으로 변경했습니다.`);return;
  7063 |         }
  7064 |         if(a==='pin-show'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 PIN을 조회할 수 없습니다.`,'error');return;}if(isLocked()){toast('최신 상태를 확인하기 전에는 PIN을 볼 수 없습니다.','error');return;}if(state.role==='maid'&&!maidPinAllowed(id)){toast('배정 작업의 시작 가능 시각이 된 뒤에만 PIN을 볼 수 있습니다.','error');return;}revealPin(id);return;}
  7065 |         if(a==='pin-hide'){maskPin();render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${id}"] [data-action="pin-show"]`)?.focus());return;}
  7066 |         if(a==='pin-edit'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 PIN을 편집할 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 PIN을 편집할 수 있습니다.','error');return;}maskPin();openPinEditor(id,el);return;}
  7067 |         if(a==='pin-clear'){if(!adminCanMutate())return;const input=document.getElementById('pin-edit-input');if(input){input.value='';input.focus();input.dispatchEvent(new Event('input',{bubbles:true}));}return;}
  7068 |         if(a==='pin-random'){if(!adminCanMutate())return;const input=document.getElementById('pin-edit-input');if(input){input.value=secureFourDigits();input.dispatchEvent(new Event('input',{bubbles:true}));input.focus();input.select();}return;}
  7069 |         if(a==='pin-review'){if(roomIsOnHold(id)||!adminCanMutate()){closeModal();render();toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 PIN을 저장할 수 없습니다.`:'관리자 권한 또는 최신 상태가 바뀌었습니다.','error');return;}const input=document.getElementById('pin-edit-input'),value=input?.value.trim()||'';if(!/^\d{4}$/.test(value)){toast('객실 PIN은 앞자리 0을 포함해 숫자 4자리여야 합니다.','error');input?.focus();return;}openPinReview(id,value);return;}
  7070 |         if(a==='pin-back'){pendingPin=null;dismissModal();return;}
  7071 |         if(a==='pin-save'){if(roomIsOnHold(id)||!adminCanMutate()||!pendingPin||pendingPin.room!==id){pendingPin=null;closeModal();render();toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 PIN을 저장하지 않았습니다.`:'관리자 권한 또는 최신 상태가 바뀌어 PIN을 저장하지 않았습니다.','error');return;}writeProtectedPin(id,pendingPin.value);appendEvent(`${id}호 PIN 변경`,'관리자 · 직접/랜덤 입력 · 원문 미기록');pendingPin=null;historyReturnFocus={action:'pin-hide',id};closeModal();revealPin(id);toast(`${id}호 객실 PIN을 변경했습니다. 30초 뒤 자동으로 숨깁니다.`);return;}
  7072 |         if(a==='publish-selected'){
  7073 |           if(isLocked()){toast('최신 상태를 확인하기 전에는 배정 준비 작업을 처리할 수 없습니다.','error');return;}
  7074 |           pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);});toast('청소 작업은 내일 배정에서 담당과 순서를 지정해 주세요.');return;
  7075 |         }
  7076 |         if(a==='confirm-publish'){
  7077 |           pendingDraftPublish=null;closeModal();pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='assignment-tomorrow';syncAssignmentDateForCleaningTab(state);});toast('공개 전환은 중단되었습니다. 담당 메이드를 내일 배정 화면에서 지정해 주세요.');return;
  7078 |         }
  7079 |         if(a==='reservation-edit'||a==='new-reservation'){
  7080 |           const roomRecords=id?(state.reservations||[]).filter(reservation=>reservation.room===String(id)):[],historyOnly=roomRecords.length>0&&roomRecords.every(reservationRecordIsPast);
  7081 |           if(!adminCanMutate()&&!(a==='reservation-edit'&&historyOnly)){toast('관리자 최신 상태에서만 예약을 등록·변경할 수 있습니다.','error');return;}
  7082 |           const block=id?quickRoomBlockReason(ROOMS.find(room=>room.no===id)):'' ,hasExisting=id?activeReservationsFor(state,id).length>0:false;if(block&&(a==='new-reservation'||!hasExisting)&&!historyOnly){toast(`${id}호는 ${block} 상태라 새 예약을 등록할 수 없습니다.`,'error');return;}openReservation(id||'211',a==='new-reservation'?'__new__':'');return;
  7083 |         }
  7084 |         if(a==='reservation-guest-change'){
  7085 |           const input=document.getElementById('res-guests'),roomNo=document.getElementById('res-room')?.value||'',policy=guestPolicyForRoom(roomNo),delta=Number(el.dataset.delta),current=Number(input?.value);
  7086 |           if(!input||!Number.isInteger(current)||![-1,1].includes(delta))return;
  7087 |           const next=current+delta;if(next<1||next>policy.maxGuestCount)return;
  7088 |           input.value=String(next);updateReservationGuestControls();const focusTarget=el.disabled?document.querySelector(`[data-action="reservation-guest-change"][data-delta="${-delta}"]`):el;focusTarget?.focus();return;
  7089 |         }
  7090 |         if(a==='save-reservation-v2'){
  7091 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 예약을 저장하지 않았습니다.','error');return;}
  7092 |           const reservationId=document.getElementById('res-id')?.value||'',existing=reservationId?state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null:null,no=existing?.room||document.getElementById('res-room')?.value||'211',room=ROOMS.find(item=>item.no===no);
  7093 |           if(reservationId&&!existing){closeModal();render();toast('이 예약은 이미 변경되었거나 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  7094 |           if(reservationWeekIsPast()||reservationRecordIsPast(existing)){closeModal();render();toast('지난 예약 기록은 조회만 가능하며 수정할 수 없습니다.','error');return;}
  7095 |           if(existing&&reservationFingerprint(existing)!==(document.getElementById('res-fingerprint')?.value||'')){closeModal();render();toast('예약 일정이 다른 화면에서 바뀌었습니다. 최신 예약을 다시 확인해 주세요.','error');return;}
  7096 |           if(!room||!existing&&quickRoomBlockReason(room)){closeModal();render();toast(`${no}호는 ${quickRoomBlockReason(room)||'객실 정보 없음'} 상태라 새 예약을 저장하지 않았습니다.`,'error');return;}
  7097 |           const checkinAt=document.getElementById('res-checkin')?.value||'', checkoutAt=document.getElementById('res-checkout')?.value||'',guestCount=document.getElementById('res-guests')?.value??'',currentStay=document.getElementById('res-current-stay')?.value==='1';
  7098 |           const validDateTime=value=>/^\d{4}-\d{2}-\d{2}T([01]\d|2[0-3]):[0-5]\d$/.test(value);
  7099 |           if(!validDateTime(checkinAt)||!validDateTime(checkoutAt)||checkinAt>=checkoutAt||checkinAt.slice(0,10)>=checkoutAt.slice(0,10)){toast('한 고객의 체크인 다음에 체크아웃이 오도록 입력하세요.','error');document.getElementById(!validDateTime(checkinAt)?'res-checkin':'res-checkout')?.focus();return;}
  7100 |           const checkinTime=checkinAt.slice(11,16), checkoutTime=checkoutAt.slice(11,16);
  7101 |           if(!checkinTime.endsWith(':00')||!checkoutTime.endsWith(':00')){toast('예정 체크인·체크아웃은 1시간 단위로 입력하세요.','error');(!checkinTime.endsWith(':00')?document.getElementById('res-checkin'):document.getElementById('res-checkout'))?.focus();return;}
  7102 |           const result=upsertReservationRecord({id:reservationId,roomNo:no,checkInAt:checkinAt,checkOutAt:checkoutAt,guestCount,source:'card',currentStay});
  7103 |           if(result.error){const overlap=result.conflict?.reservation||result.conflict?.checkInAt&&result.conflict,conflictField=overlap&&checkinAt<overlap.checkInAt?'res-checkout':'res-checkin';toast(result.error,'error');document.getElementById(result.guestError?'reservation-guest-stepper':result.conflict?conflictField:'res-checkin')?.focus();return;}
  7104 |           const cardReservation=activeReservationsFor(state,no).find(item=>!reservationRecordIsPast(item))||result.reservation;
  7105 |           state.quickLastCreated=null;historyReturnFocus=state.adminView==='quickReservation'?{quickCell:true,room:no,date:result.reservation.checkInAt.slice(0,10)}:state.detail?.type==='room'?{action:'reservation-edit',id:no}:{action:'quick-reservation-edit',id:cardReservation.id,room:no};closeModal();render();toast(`${no}호 ${reservationNights(result.reservation)}박 · ${reservationGuestCount(result.reservation)}명 예약을 저장했습니다.`);return;
  7106 |         }
  7107 |         if(a==='complete-checkout-inspection'){
  7108 |           const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!reservation||!checkoutInspectionPendingForReservation(reservation)){toast('현재 퇴실점검 대상이 아니거나 이미 완료되었습니다.','error');return;}showModal({title:`${no}호 퇴실점검을 완료할까요?`,subtitle:`${reservationMomentLabel(reservation.checkOutAt)} 체크아웃 · 예약 ${reservation.id}`,trigger:el,body:'<div class="notice notice-warning"><div><strong>청소 완료 처리와는 별도입니다.</strong><br>퇴실점검 대상 상태만 해제하고 객실의 청소 필요·배정 상태는 그대로 유지합니다.</div></div>',confirmLabel:'퇴실점검 완료 기록',confirmAction:'confirm-checkout-inspection',confirmVariant:'primary'});const confirm=document.querySelector('[data-action="confirm-checkout-inspection"]');if(confirm){confirm.dataset.id=no;confirm.dataset.reservation=reservation.id;}return;
  7109 |         }
  7110 |         if(a==='confirm-checkout-inspection'){
  7111 |           const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!adminCanMutate()||!reservation||reservation.id!==el.dataset.reservation||!checkoutInspectionPendingForReservation(reservation)){closeModal();render();toast('퇴실점검 대상 또는 관리자 최신 상태가 바뀌어 완료하지 않았습니다.','error');return;}const result=completeCheckoutInspection(no,{method:'manual'});if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-checkout-inspection-room="${no}"]`);toast(`${no}호 퇴실점검을 완료했습니다. 청소 필요 상태는 유지됩니다.`);return;
  7112 |         }
  7113 |         if(a==='toggle-room-cleaning'){
  7114 |           const no=String(id||''),request=activeManualCleaningRequest(no),block=request?manualCleaningCancelBlockReason(no):manualCleaningRequestBlockReason(no);if(block){toast(block,'error');return;}
  7115 |           const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:request?`${no}호 청소 요청을 취소할까요?`:`${no}호 청소를 요청할까요?`,subtitle:request?`${kind} · 대기열에서 취소`:`${kind} · 청소 대기열 등록`,trigger:el,body:request?'<div class="notice notice-warning"><div><strong>청소 대기열에서 요청을 취소합니다.</strong><br>아직 미배정·미공개·미착수인 요청만 취소되며, 이미 시작된 작업은 청소 상세에서 확인해야 합니다.</div></div>':'<div class="notice notice-info"><div><strong>확인하면 청소 대기열에 작업 1건을 등록합니다.</strong><br>투숙 중 객실은 연박 청소, 공실 객실은 추가 청소로 등록되며 담당은 관리자 배정 화면에서 정합니다.</div></div>',confirmLabel:request?'청소 취소':'청소 대기열에 넣기',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action="${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;
  7116 |         }
  7117 |         if(a==='confirm-room-cleaning-on'){
  7118 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 만들지 않았습니다.','error');return;}const result=createManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 대기열에 넣었습니다.`);return;
  7119 |         }
  7120 |         if(a==='confirm-room-cleaning-off'){
  7121 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 취소하지 않았습니다.','error');return;}const result=cancelManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind} 요청을 취소했습니다.`);return;
  7122 |         }
  7123 |         if(a==='create-stayover'){
  7124 |           const no=id||'142',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7125 |           if(state.role!=='admin'||isLocked()||roomIsOnHold(no)||room?.occupancy!=='occupied'){toast('최신 온라인 상태의 투숙 중 객실에서만 연박 청소 요청을 입력할 수 있습니다.','error');return;}
  7126 |           if(activeRecleanAttempt(no)){toast(`${no}호 본인 무급 재청소가 끝난 뒤 연박 청소 요청을 입력할 수 있습니다.`,'error');return;}
  7127 |           if(existing){toast(`${no}호 연박 청소 배정 준비 작업이 이미 있습니다.`,'error');return;}
  7128 |           openStayover(no,el);return;
  7129 |         }
  7130 |         if(a==='confirm-stayover'){
  7131 |           const no=id||'',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7132 |           if(state.role!=='admin'||isLocked()||!room||roomIsOnHold(no)||room.occupancy!=='occupied'){closeModal();render();toast('객실 점유·관리자 권한 또는 최신 상태가 바뀌어 요청을 저장하지 않았습니다.','error');return;}
  7133 |           if(activeRecleanAttempt(no)){closeModal();render();toast(`${no}호 본인 무급 재청소를 유지하기 위해 연박 청소 요청을 저장하지 않았습니다.`,'error');return;}
  7134 |           if(existing){closeModal();render();toast(`중복 생성을 막았습니다. 기존 ${no}호 배정 준비 작업을 확인하세요.`,'error');return;}
  7135 |           const planDate=document.getElementById('stayover-date')?.value||'',accessStart=document.getElementById('stayover-start')?.value||'',requestDue=document.getElementById('stayover-due')?.value||'',accessEnd=document.getElementById('stayover-end')?.value||'';
  7136 |           const validDate=/^\d{4}-\d{2}-\d{2}$/.test(planDate),validTimes=[accessStart,requestDue,accessEnd].every(value=>/^([01]\d|2[0-3]):[0-5]\d$/.test(value));
  7137 |           if(!validDate||!validTimes){toast('계획일과 세 시각을 모두 입력하세요.','error');document.getElementById(!validDate?'stayover-date':'stayover-start')?.focus();return;}
  7138 |           if(!(timeMinutes(accessStart)<timeMinutes(requestDue)&&timeMinutes(requestDue)<=timeMinutes(accessEnd))){toast('출입 시작 < 요청 완료 ≤ 출입 종료 순서로 입력하세요.','error');document.getElementById('stayover-due')?.focus();return;}
  7139 |           const templateSnapshot=templateSnapshotFor(no,'연박 청소');
  7140 |           state.drafts.push({id:`d${no}-stayover`,room:no,kind:'연박 청소',created:state.time,date:planDate,planDate,accessStart,requestDue,accessEnd,visibility:'private',templateSnapshot});
  7141 |           room.stayoverRequest={date:planDate,accessStart,requestDue,accessEnd};
  7142 |           const unfinished=activeUnfinishedAttempt(no);if(no==='142')state.stayoverCreated=true;if(!unfinished)state.jobs[no]='stayover-requested';
  7143 |           appendEvent(`${no}호 연박 청소 배정 준비 작업 생성`,`${planDate} · 출입 ${accessStart}–${accessEnd} · ${requestDue} 요청 완료 · ${templateSnapshot?.name||'연박 청소'} ${templateSnapshot?.version||''} 스냅샷${unfinished?` · 현재 ${unfinished.kind} ${unfinished.id} 상태 유지`:''}`);
  7144 |           closeModal();render();toast(unfinished?'연박 청소 요청을 저장하고 현재 미완료 청소 상태는 그대로 유지했습니다.':'현재 점유를 유지한 채 연박 청소 배정 준비 작업 1건을 만들었습니다.');return;
  7145 |         }
  7146 |         if(a==='operation-status'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 운영 상태를 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 운영 상태를 바꿀 수 있습니다.','error');return;}openOperationStatus(id);return;}
  7147 |         if(a==='confirm-operation-stop'){if(roomIsOnHold(id)||!adminCanMutate()){closeModal();render();toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 중지하지 않았습니다.`:'관리자 권한 또는 최신 상태가 바뀌어 운영을 중지하지 않았습니다.','error');return;}const to=document.getElementById('relocate-room')?.value||'',reason=document.getElementById('stop-reason')?.value.trim()||'';if(!reason){toast('운영 중지 사유를 입력하세요.','error');return;}state.roomStopped[id]=true;state.roomStopReasons[id]=reason;if(to)state.roomMoves[id]={to,reason};else delete state.roomMoves[id];appendEvent(`${id}호 운영 중지`,to?`${reason} · ${to}호 대체 배정 · 원 이력 보존`:reason);closeModal();render();toast(`${id}호 고객 배정을 중지했습니다.`);return;}
  7148 |         if(a==='resume-operation'){if(roomIsOnHold(id)||!adminCanMutate()){toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 재개할 수 없습니다.`:'관리자 최신 상태에서만 객실 운영을 재개할 수 있습니다.','error');return;}state.roomStopped[id]=false;appendEvent(`${id}호 운영 재개`,'대체 배정 이력은 보존');render();focusAfterRender(`[data-action="operation-status"][data-id="${id}"]`);toast('운영 정상 상태로 다시 계산했습니다.');return;}
  7149 |         if(a==='candle-change'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 촛불 수량을 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 촛불 수량을 변경할 수 있습니다.','error');return;}const room=ROOMS.find(r=>r.no===id);if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}state.candles[id]=Math.max(0,(state.candles[id]||0)+Number(el.dataset.delta));appendEvent(`${id}호 촛불 수량 변경`,`${state.candles[id]}개 · 관리자 데모`);const delta=el.dataset.delta;render();requestAnimationFrame(()=>document.querySelector(`[data-action="candle-change"][data-id="${id}"][data-delta="${delta}"]`)?.focus());return;}
  7150 |         if(a==='task-candle-change'){const no=el.dataset.room,room=ROOMS.find(r=>r.no===no);if(!maidCanEditCleaning(no)){toast('본인 담당 청소 결과를 입력하는 동안만 촛불 수량을 바꿀 수 있습니다.','error');return;}if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}const task=taskState(no);task.candle=Math.max(0,Math.min(9,(task.candle||0)+Number(el.dataset.delta)));const section=el.closest('.cleaning-section');section?.querySelector('[data-cleaning-section-meta]')?.replaceChildren(`${task.candle}개`);section?.querySelector('.candle-stepper-value strong')?.replaceChildren(`${task.candle}개`);const minus=section?.querySelector('[data-delta="-1"]'),plus=section?.querySelector('[data-delta="1"]');if(minus)minus.disabled=task.candle<1;if(plus)plus.disabled=task.candle>=9;el.focus();return;}
  7151 |         if(a==='direct-assign'){openDirectAssign(id);return;}
  7152 |         if(a==='confirm-direct-assign'){const name=document.getElementById('assign-maid')?.value||'',room=ROOMS.find(r=>r.no===id),maid=MAIDS.find(item=>item.name===name),hold=roomIsOnHold(id),reclean=activeRecleanAttempt(id),previousAttempt=activeUnfinishedAttempt(id),pinViewed=!!previousAttempt&&roomPinWasViewed(id,previousAttempt.id),target=directAssignmentTarget(id),workDate=directAssignmentWorkDate(id),beforeMaidId=previousAttempt?.performerId||MAIDS.find(item=>item.name===room?.assignee)?.id||null;if(state.role!=='admin'||isLocked()||hold||reclean||pinViewed||previousAttempt?.accessReviewRequired||!target||target.id!==el.dataset.target||target.kind!==el.dataset.kind||workDate!==el.dataset.workDate||(previousAttempt?.id||'')!==(el.dataset.attempt||'')||!['public','draft','future','scheduled','unassigned'].includes(state.jobs[id])){closeModal();render();toast(previousAttempt?.accessReviewRequired?'출입시간과 PIN 영향을 먼저 확인해 주세요.':pinViewed?`${id}호 PIN 조회 뒤에는 현장 영향 확인 전 담당을 바꿀 수 없습니다.`:hold?`${id}호는 운영 상태 확인 보류 객실이라 배정하지 않았습니다.`:reclean?'재청소는 처음 청소한 본인에게 고정되어 다른 메이드에게 직접 배정할 수 없습니다.':'청소대상·수행 회차·관리자 권한 또는 최신 상태가 바뀌어 직접 배정하지 않았습니다.','error');return;}if(!maid||beforeMaidId===maid.id||!maidCanReceiveNewAssignment(maid.id)||availabilityForWorkDate(maid.id,workDate)!=='available'){toast(beforeMaidId===maid?.id?'현재 담당과 같은 메이드는 새 담당으로 다시 배정할 수 없습니다.':maid&&!maidCanReceiveNewAssignment(maid.id)?'비활성 처리 중이거나 비활성인 메이드에게는 새 업무를 배정할 수 없습니다.':'해당 업무 주차에 근무 가능으로 제출한 메이드만 배정할 수 있습니다.','error');return;}if(room)room.assignee=name;const context=assignmentContext(target),baseRateSnapshot=previousAttempt?.baseRateSnapshot??context.type.rate,targetTemplateSnapshot=previousAttempt?.templateSnapshot||state.drafts.find(draft=>draft.id===target.id)?.templateSnapshot||templateSnapshotFor(id,target.kind),newAttempt=beginCleaningAttempt(id,{performerName:name,reason:'관리자 새 담당 직접 배정',kind:target.kind,baseRateSnapshot,workDate:attemptWorkDate(previousAttempt,workDate),effectiveDate:workDate,workTargetId:target.id,templateSnapshot:targetTemplateSnapshot,accessStart:previousAttempt?.accessStart||target.accessStart||target.checkout||null,requestDue:previousAttempt?.requestDue||target.requestDue||null,accessEnd:previousAttempt?.accessEnd||target.accessEnd||null,reservationIdSnapshot:previousAttempt?.reservationIdSnapshot||target.reservationId||null,guestCountSnapshot:previousAttempt?.guestCountSnapshot??assignmentGuestCount(target),checkoutSnapshot:previousAttempt?.checkoutSnapshot||target.checkout||null,checkinSnapshot:previousAttempt?.checkinSnapshot||target.checkin||null,deadlineSnapshot:previousAttempt?.deadlineSnapshot||target.deadline||null,nextReservationIdSnapshot:previousAttempt?.nextReservationIdSnapshot||target.nextReservationId||null});state.jobs[id]='claimed';state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:target.id,attemptId:newAttempt.id,assignmentDate:workDate,room:id,beforeMaidId,afterMaidId:maid.id,before:beforeMaidId?`${maidName(beforeMaidId)} · 기존 담당`:'미배정',after:`${name} · 직접 배정`,reason:`${newAttempt.kind} · 관리자 직접 배정 통보 · ${dateLabel(workDate)} 근무 가능 확인`});appendEvent(`${id}호 청소 직접 배정`,`${name} · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 제출 확인 · ${targetTemplateSnapshot?.id||'타입 템플릿'} ${targetTemplateSnapshot?.version||''} 스냅샷`);if(beforeMaidId&&beforeMaidId!==maid.id)appendEvent('내 청소 담당 변경 통보',`${id}호 기존 담당 종료 · ${previousAttempt?.id||'이전 회차'} 보존 · 새 담당 정보 비공개`,{maidIds:[beforeMaidId]});appendEvent('내 청소 담당 배정 통보',`${id}호 · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 확인${guestCountForAttempt(newAttempt)?` · 숙박 ${guestCountLabel(guestCountForAttempt(newAttempt))}`:''}`,{maidIds:[maid.id]});closeModal();render();toast(`${name}에게 ${id}호를 배정했습니다.`);return;}
  7153 |         if(a==='cleaning-tab'){
  7154 |           const tab=el.dataset.tab;if(!['assignment-today','assignment-tomorrow','progress','inspection','done'].includes(tab))return;
  7155 |           if(tab===state.cleaningTab){el.focus();return;}
  7156 |           if(isCleaningAssignmentTab(state.cleaningTab)&&tab!==state.cleaningTab&&state.randomAssignmentSnapshot){if(!restoreRandomAssignment())discardStaleRandomAssignment();toast('저장 전 랜덤 초안은 날짜를 바꾸기 전에 되돌렸습니다.');}
  7157 |           rememberCurrentHistoryRoute();state.cleaningTab=tab;syncAssignmentDateForCleaningTab(state);if(isCleaningAssignmentTab(tab)){initializeCleaningTargetLedger(state);state.assignmentTypeFilter='all';}
  7158 |           pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector(`[data-action="cleaning-tab"][data-tab="${tab}"]`)?.focus());return;
  7159 |         }
  7160 |         if(a==='assignment-type-filter'){
  7161 |           const type=el.dataset.type;
  7162 |           if(state.role!=='admin'||!['all',...Object.keys(ROOM_TYPES)].includes(type))return;
  7163 |           state.assignmentTypeFilter=type;render();requestAnimationFrame(()=>document.querySelector(`[data-action="assignment-type-filter"][data-type="${type}"]`)?.focus());return;
  7164 |         }
  7165 |         if(a==='admin-maid-tab'){const tab=el.dataset.tab;state.adminMaidTab=tab;render();requestAnimationFrame(()=>document.querySelector(`[data-action="admin-maid-tab"][data-tab="${tab}"]`)?.focus());return;}
```

## 장기투숙: `장기`

matches: 0

## 예약 모달: `openReservation`

matches: 9

### occurrence 1 · line 3703

```html
  3658 |       function pushPageTransition(update,focusSelector='#main-content') {
  3659 |         rememberCurrentHistoryRoute();update();pushHistoryOnNextRender();render();
  3660 |         requestAnimationFrame(()=>{window.scrollTo(0,0);document.querySelector(focusSelector)?.focus?.({preventScroll:true});});
  3661 |       }
  3662 |       function backPageTransition(fallback,focusDescriptor=null) {
  3663 |         if(isWireframeHistory(history.state)&&history.state.layer==='page'&&historyIndex()>0){historyReturnFocus=focusDescriptor;historyTraversalPending=true;history.back();return;}
  3664 |         fallback();render();requestAnimationFrame(()=>document.getElementById('main-content')?.focus({preventScroll:true}));
  3665 |       }
  3666 | 
  3667 |       function standardModalMarkup({title,subtitle='',body,confirmLabel='',confirmAction='',confirmVariant='primary',closeLabel='취소',secondaryLabel='',secondaryAction='',secondaryVariant='outline',secondaryExtra='',auxiliaryLabel='',auxiliaryAction='',auxiliaryVariant='outline',auxiliaryExtra='',large=false}) {
  3668 |         const secondary=secondaryAction?`<button class="btn btn-${secondaryVariant} modal-secondary" type="button" data-action="${secondaryAction}" ${secondaryExtra}>${esc(secondaryLabel)}</button>`:'',auxiliary=auxiliaryAction?`<button class="btn btn-${auxiliaryVariant} modal-auxiliary" type="button" data-action="${auxiliaryAction}" ${auxiliaryExtra}>${esc(auxiliaryLabel)}</button>`:'',leading=secondary||auxiliary?`<div class="modal-leading-actions">${secondary}${auxiliary}</div>`:'';
  3669 |         return `<div class="modal-backdrop" data-action="backdrop-close"><section class="modal ${large?'modal-lg':''}" role="dialog" aria-modal="true" aria-labelledby="modal-title"${subtitle?' aria-describedby="modal-desc"':''}><header class="modal-head"><div><h2 id="modal-title">${title}</h2>${subtitle?`<p id="modal-desc">${subtitle}</p>`:''}</div><button class="icon-btn" type="button" data-action="close-modal" aria-label="닫기">${icon('x')}</button></header><div class="modal-body">${body}</div><footer class="modal-foot ${leading?'has-leading':''}">${leading}${button(closeLabel,'close-modal','outline')}${confirmAction?button(confirmLabel,confirmAction,confirmVariant):''}</footer></section></div>`;
  3670 |       }
  3671 |       function showModal(options) {
  3672 |         closeInfoTips();
  3673 |         const {trigger=document.activeElement,historyKind='generic',historyPayload=null,historyStack=false}=options;
  3674 |         modalTrigger=trigger;
  3675 |         const root=document.getElementById('modal-root');
  3676 |         root.innerHTML=standardModalMarkup(options);
  3677 |         applyAdminCopyPolicy(root);
  3678 |         lockModalViewport();setModalBackgroundLocked(true);
  3679 |         registerModalHistory({stack:historyStack,kind:historyKind,payload:historyPayload});
  3680 |         queueMicrotask(()=>{if(root.hasChildNodes()&&history.state?.layer==='modal')captureCurrentModalHistory();});
  3681 |         requestAnimationFrame(()=>root.querySelector('button, input, select, textarea')?.focus({preventScroll:true}));
  3682 |       }
  3683 |       function setModalBackgroundLocked(locked){const app=document.getElementById('app');if(!app)return;app.inert=locked;if(locked)app.setAttribute('aria-hidden','true');else app.removeAttribute('aria-hidden');}
  3684 |       function closeModal() {
  3685 |         const root=document.getElementById('modal-root'),hadModal=!!root?.hasChildNodes(),entry=history.state,modalEntryId=entry?.modalEntryId,triggerFocus=historyFocusDescriptor(modalTrigger);
  3686 |         historyReturnFocus=historyReturnFocus||triggerFocus;
  3687 |         rawCloseModal();
  3688 |         if(!hadModal||!isWireframeHistory(entry)||entry.layer!=='modal'||historyTraversalPending)return;
  3689 |         queueMicrotask(()=>{
  3690 |           if(historyTraversalPending||history.state?.modalEntryId!==modalEntryId)return;
  3691 |           const route=historyRouteSnapshot(),depth=Math.max(1,Number(entry.modalDepth)||1);
  3692 |           if(!completedModalSessions.some(session=>session.modalSessionId===entry.modalSessionId))completedModalSessions.push({modalSessionId:entry.modalSessionId,route});
  3693 |           if(isPinHistoryKind(entry.modalKind))clearPinModalSecret(entry.modalSessionId);
  3694 |           historyTraversalOverride=route;historyTraversalPending=true;history.go(-depth);
  3695 |         });
  3696 |       }
  3697 |       function adminOperatorText(message) {
  3698 |         if(state.role!=='admin')return String(message||'');
  3699 |         return String(message||'').replace(/PIN lease|\blease\b/gi,'PIN 조회').replace(/수익 ID/g,'청소 내역').replace(/수익 원장|청소 원장|주급 원장/g,'청소 내역').replace(/스냅샷/g,'기준').replace(/fingerprint/gi,'확인값').replace(/수행 회차/g,'청소 작업').replace(/회차/g,'작업').replace(/미종결/g,'미완료').replace(/종결/g,'조치 완료').replace(/재계산/g,'다시 확인').replace(/충돌을 조치 완료하고/g,'충돌 조치를 완료하고').replace(/충돌을 조치 완료하지/g,'충돌 조치를 완료하지').replace(/청소 작업가/g,'청소 작업이').replace(/청소 작업를/g,'청소 작업을').replace(/담당·청소 작업·PIN 조회 조치 완료/g,'담당 변경·진행 중 청소·PIN 조회 확인').replace(/비공개 퇴실 청소 초안|퇴실 청소 초안/g,'퇴실 청소').replace(/\bOPEN\b/g,'지급 대기').replace(/\bPAYING\b/g,'지급 진행').replace(/\bCHECK\b/g,'정산 확인 필요').replace(/\bPAID\b/g,'지급 완료');
  3700 |       }
  3701 |       function toast(message,type='') { const display=adminOperatorText(message),root=document.getElementById('toast-region');root.innerHTML=`<div class="toast ${type}" role="status">${esc(display)}</div>`;clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',3400);document.getElementById('assertive-live').textContent=display; }
  3702 | 
  3703 |       function openReservation() {
  3704 |         showModal({title:'예약 등록 · 데모',subtitle:'체크인과 체크아웃 일정을 입력하세요.',large:true,body:`<form id="reservation-form" class="form-grid"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control"><option>211호 · 데모</option></select></div><div class="field"><label for="res-customer">고객 이름 · 선택</label><input id="res-customer" class="input-control" value="홍길동 (데모)"><small>관리자 예약 상세에서만 표시</small></div><div class="field"><label for="res-checkin">예정 체크인</label><input id="res-checkin" class="input-control" type="datetime-local" value="2026-08-15T16:00"></div><div class="field"><label for="res-checkout">예정 체크아웃</label><input id="res-checkout" class="input-control" type="datetime-local" value="2026-08-16T11:00"></div><div class="field"><label for="early">얼리 체크인</label><select id="early" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div><div class="field"><label for="late">레이트 체크아웃</label><select id="late" class="select-control"><option>없음</option><option>1시간</option><option>2시간</option></select></div></form>`,confirmLabel:'예약 저장',confirmAction:'save-reservation',historyKind:'reservation',historyPayload:{room:'211'}});
  3705 |       }
  3706 | 
  3707 |       function notificationCategoryLabel(category){return NOTIFICATION_CATEGORY_LABELS[category]||NOTIFICATION_CATEGORY_LABELS.general;}
  3708 |       function notificationFilterLabel(filter){return filter==='unread'?'안 읽음':filter==='action'?'처리 필요':'전체';}
  3709 |       function renderNotificationListMarkup({key=notificationAudienceKey(),filter=state.notificationFilter,includeActivity=true}={}){
  3710 |         ensureNotificationState();const bundles=notificationBundlesForKey(key),filtered=bundles.filter(bundle=>filter==='unread'?bundle.unread:filter==='action'?bundle.actionRequired:true),activity=(state.events||[]).filter(event=>!event.notify).slice(0,5),pushEnabled=notificationPushEnabled(key),filterButtons=[['all','전체'],['unread','안 읽음'],['action','처리 필요']].map(([value,label])=>`<button class="btn btn-ghost" type="button" data-action="notification-filter" data-filter="${value}" aria-pressed="${filter===value}">${label}${value==='unread'?` ${notificationUnreadCount(key)}`:''}</button>`).join('');
  3711 |         const cards=filtered.map(bundle=>{const event=bundle.latest,priority=event.priority==='urgent'?'urgent':'',status=event.status==='handled'&&!bundle.actionRequired?'처리 완료':bundle.actionRequired?'확인 필요':'안내',statusClass=status==='처리 완료'?'handled':bundle.actionRequired?'action':'',bundleText=bundle.bundleCount>1?` · 업데이트 ${bundle.bundleCount}건`:'';return `<button class="notification-card ${bundle.unread?'unread':''} ${priority}" type="button" data-action="notification-open" data-event-id="${esc(event.id)}" data-event-ids="${esc(bundle.eventIds.join(','))}" data-notification-card="${esc(event.category)}"><span class="notification-dot" aria-hidden="true"></span><span class="notification-copy"><span class="notification-title-line"><strong>${esc(event.title)}</strong>${bundle.bundleCount>1?`<span class="notification-chip">업데이트 ${bundle.bundleCount}건</span>`:''}</span><p>${esc(event.detail||'업무 상태가 변경되었습니다.')}</p><span class="notification-meta"><span>${esc(event.time)}</span><span>${esc(notificationCategoryLabel(event.category))}</span><span class="notification-chip ${statusClass}">${status}</span>${event.pushOptional?'<span>푸시 선택</span>':event.push?'<span>푸시 대상</span>':'<span>앱 내 기록</span>'}${bundleText}</span></span><span class="notification-cta">관련 화면 ${icon('chevronRight','icon-sm')}</span></button>`;}).join('');
  3712 |         const activityMarkup=includeActivity?`<section class="notification-activity"><h3>최근 활동 기록</h3><p>정상 청소 시작·사진 업로드·가능일 제출·관리자 직접 저장처럼 푸시하지 않는 활동입니다.</p><div class="notification-activity-list">${activity.length?activity.map(event=>`<div class="notification-activity-row"><span><strong>${esc(event.title)}</strong><span>${esc(event.detail||'')}</span></span><span>${esc(event.time||'')}</span></div>`).join(''):'<div class="notification-empty"><p>기록된 일반 활동이 없습니다.</p></div>'}</div></section>`:'';
  3713 |         return `<div class="notification-toolbar"><div class="notification-filter-group" role="group" aria-label="알림 필터">${filterButtons}</div><div class="notification-toolbar-actions"><button class="btn btn-outline" type="button" data-action="notification-mark-all-read" ${notificationUnreadCount(key)?'':'disabled'}>모두 읽음</button><button class="btn btn-outline" type="button" data-action="notification-toggle-push" aria-pressed="${pushEnabled}">${pushEnabled?'푸시 켜짐':'푸시 꺼짐'}</button></div></div><div class="notice notice-info notification-push-note"><div><strong>앱 내 알림은 항상 보존됩니다.</strong><br>푸시는 지금 확인하거나 행동해야 하는 상태 변경만 대상으로 하며, 이 정적 데모의 브라우저 알림은 화면이 열려 있는 동안만 동작합니다. 실제 백그라운드·모바일 푸시는 서비스 워커와 서버 발송 계층이 필요합니다.</div></div><div class="notification-list" data-notification-list="${esc(key)}" data-filter="${esc(filter)}">${cards||`<section class="notification-empty"><h3>${notificationFilterLabel(filter)} 알림이 없습니다</h3><p>새 상태 변경이 생기면 발생 시각 순서로 표시됩니다.</p></section>`}</div>${activityMarkup}`;
  3714 |       }
  3715 |       function openNotificationCenter(trigger=document.activeElement){const roleLabel=state.role==='admin'?'관리자 알림':'내 알림';showModal({title:roleLabel,subtitle:'업데이트를 시간순으로 보존하고 관련 업무 화면으로 바로 연결합니다.',large:true,trigger,body:renderNotificationListMarkup(),closeLabel:'닫기'});}
  3716 |       function openAlerts(){openNotificationCenter(document.activeElement);}
  3717 | 
  3718 |       function dispatchNotificationTarget(event){
  3719 |         const target=event?.target||{},action=target.action||'alerts';
  3720 |         if(action==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  3721 |         if(action==='go-cleaning-assignment'){const day=target.data?.day==='tomorrow'?'tomorrow':'today';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  3722 |         if(action==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  3723 |         if(action==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  3724 |         if(action==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  3725 |         if(action==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  3726 |         const button=document.createElement('button');button.type='button';button.hidden=true;button.dataset.action=action;if(target.id)button.dataset.id=target.id;Object.entries(target.data||{}).forEach(([key,value])=>button.dataset[key]=String(value));document.body.appendChild(button);button.dispatchEvent(new MouseEvent('click',{bubbles:true,cancelable:true,view:window}));button.remove();
  3727 |       }
  3728 |       function closeNotificationModalAndNavigate(notificationEvent){
  3729 |         const navigate=()=>requestAnimationFrame(()=>dispatchNotificationTarget(notificationEvent)),entry=history.state;
  3730 |         if(isWireframeHistory(entry)&&entry.layer==='modal'){
  3731 |           let completed=false;
  3732 |           const onPop=()=>{if(completed)return;completed=true;setTimeout(navigate,0);};
  3733 |           window.addEventListener('popstate',onPop,{once:true});
  3734 |           closeModal();
  3735 |           return;
  3736 |         }
  3737 |         rawCloseModal();navigate();
  3738 |       }
  3739 |       document.addEventListener('click',browserEvent=>{
  3740 |         const el=browserEvent.target.closest?.('[data-action]'),action=el?.dataset.action;
  3741 |         if(!['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].includes(action))return;
  3742 |         browserEvent.preventDefault();browserEvent.stopImmediatePropagation();
  3743 |         if(action==='notification-filter'){
  3744 |           const filter=el.dataset.filter;if(!['all','unread','action'].includes(filter))return;
  3745 |           state.notificationFilter=filter;rawCloseModal();openNotificationCenter(el);return;
  3746 |         }
  3747 |         if(action==='notification-mark-all-read'){
  3748 |           markAllNotificationsRead();render();rawCloseModal();openNotificationCenter(el);toast('현재 계정의 알림을 모두 읽음 처리했습니다.');return;
  3749 |         }
  3750 |         if(action==='notification-toggle-push'){
  3751 |           const enabled=!notificationPushEnabled();setNotificationPushEnabled(enabled);appendEvent('기기 푸시 설정 변경',enabled?'현재 계정 푸시 켜짐 · 앱 내 알림은 항상 유지':'현재 계정 푸시 꺼짐 · 앱 내 알림은 항상 유지',{notification:false});render();rawCloseModal();openNotificationCenter(el);toast(enabled?'행동이 필요한 업데이트의 푸시를 켰습니다.':'푸시를 껐습니다. 앱 내 알림은 계속 남습니다.');return;
  3752 |         }
  3753 |         const ids=String(el.dataset.eventIds||el.dataset.eventId||'').split(',').filter(Boolean),eventId=el.dataset.eventId||ids[0],notificationEvent=(state.events||[]).find(item=>item.id===eventId);
  3754 |         markNotificationRead(ids);render();if(notificationEvent)closeNotificationModalAndNavigate(notificationEvent);
  3755 |       },true);
  3756 | 
  3757 |       function openPublishConfirm() {
  3758 |         const selected=state.drafts.filter(d=>state.selectedDrafts.includes(d.id));
  3759 |         showModal({title:'내일 배정으로 이동할까요?',subtitle:'청소 담당은 공개 목록 없이 관리자가 직접 지정합니다.',body:`<div class="rail-list">${selected.map(d=>`<div class="rail-row"><strong>${d.room}호 · ${d.kind}</strong><span>${money(ROOM_TYPES[ROOMS.find(r=>r.no===d.room)?.type||'standard'].rate)} · 8월 시트</span></div>`).join('')}</div>`,confirmLabel:'내일 배정으로 이동',confirmAction:'confirm-publish',confirmVariant:'success'});
  3760 |       }
  3761 | 
  3762 |       function openConflictModal() {
  3763 |         showModal({title:'레이트 체크아웃·청소 출입 충돌 해결',subtitle:'현재 예약·작업 버전을 다시 확인한 뒤 필요한 항목을 모두 완료합니다.',large:true,body:`<div class="info-grid"><div class="info-item"><span>변경</span><strong>체크아웃 11:00 → 13:00</strong></div><div class="info-item"><span>영향</span><strong>PIN 조회 · 청소 시작됨</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step" value="coordinate" ${state.conflictSteps.coordinate?'checked':''}><span><strong>현장 조율 완료</strong><span>투숙객·메이드와 출입 상황 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step" value="replan" ${state.conflictSteps.replan?'checked':''}><span><strong>작업 중단·재계획</strong><span>기존 수행 회차를 이력으로 보존하고 새 일정 확정</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step" value="pin" ${state.conflictSteps.pin?'checked':''}><span><strong>실제 도어락 PIN 교체</strong><span>새 PIN 원문은 이 화면이나 영속 저장소에 보존하지 않음</span></span></label></div>`,confirmLabel:'충돌 종결',confirmAction:'confirm-conflict',confirmVariant:'danger'});
  3764 |       }
  3765 | 
  3766 |       function openCancelReview() {
  3767 |         const requestedEntry=Object.entries(state.cancelRequests||{}).find(([,request])=>request.status==='requested');
  3768 |         const no=requestedEntry?.[0]||state.cancelRequestRoom||'332', request=requestedEntry?.[1], room=ROOMS.find(item=>item.no===no), maid=request?.maid||room?.assignee||'김민지1', reason=request?.reason||'건강상 사유 · 데모';
  3769 |         state.cancelRequestRoom=no;
  3770 |         showModal({title:`${maid} 담당 취소 요청`,subtitle:'관리자 결정 전에는 담당이 유지되며 자동 취소·자동 재배정하지 않습니다.',body:`<div class="notice notice-warning">요청 사유: ${esc(reason)} · ${no}호 ${cleaningLabel(request?.job||state.jobs[no])}</div><div class="choice-list"><label class="choice"><input type="radio" name="cancel-decision" value="deny" checked><span><strong>거절 · 담당 유지</strong><span>메이드에게 관리자 사유 알림</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="republish"><span><strong>승인 · 관리자 재배정 대기</strong><span>수행 회차를 중단으로 보존하고 관리자 미배정 상태로 전환</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="direct"><span><strong>승인 · 직접 배정</strong><span>새 책임 메이드 담당 구간 생성</span></span></label><label class="choice"><input type="radio" name="cancel-decision" value="hold"><span><strong>승인 · 보류</strong><span>관리자 조치 대기 상태 유지</span></span></label></div>`,confirmLabel:'결정 저장',confirmAction:'confirm-cancel'});
  3771 |       }
  3772 | 
```

### occurrence 2 · line 6575

```html
  6530 |         const targetId=attempt.workTargetId||assignmentHistoryTargetId(no,attempt.kind,previousWorkDate),record=state.assignments?.[targetId]||null,maidId=MAIDS.some(maid=>maid.id===attempt.performerId)?attempt.performerId:null,order=record?.order||record?.previousOrder||null,maidLabel=maidId?maidName(maidId):'미배정',room=ROOMS.find(item=>item.no===no),typeId=attempt.roomMetaSnapshot?.typeId||room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard,ledgerTarget=state.cleaningTargets?.[targetId]||null,committed=record?.committedTarget||ledgerTarget||{id:targetId,room:no,type:typeId,kind:attempt.kind,source:'manual',sourceLabel:'현재 작업',rateSnapshot:Number(attempt.baseRateSnapshot)||Number(attempt.templateSnapshot?.rate)||type.rate,minutesSnapshot:Number(attempt.templateSnapshot?.minutes)||type.minutes,elevatorSnapshot:Object.prototype.hasOwnProperty.call(attempt.roomMetaSnapshot||{},'elevator')?attempt.roomMetaSnapshot.elevator:room?.elevator||null},committedReservationId=committed.reservationId||attempt.reservationIdSnapshot||null,committedGuestCount=assignmentGuestCount(committed)||(committedReservationId&&committedReservationId===attempt.reservationIdSnapshot?guestCountForAttempt(attempt):null),planDate=committed.planDate||committed.date||previousWorkDate,targetSnapshot={...committed,id:targetId,currentAttemptId:attempt.id,room:no,date:planDate,planDate,effectiveDate:state.selectedDate,checkout:attempt.checkoutSnapshot||state.time,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||state.time,reservationId:committedReservationId,guestCount:committedGuestCount};
  6531 |         if(record){
  6532 |           record.committedTarget=targetSnapshot;record.status='notified';record.scheduleChanged=false;record.guestCountChanged=false;record.reservationChanged=false;record.targetChanged=false;
  6533 |           if(record.maidId){record.previousMaidId=record.maidId;record.previousOrder=record.order;}
  6534 |         }
  6535 |         state.cleaningTargets[targetId]={...cleaningTargetSnapshot(targetSnapshot,planDate),...(state.cleaningTargets?.[targetId]||{}),...targetSnapshot,currentAttemptId:attempt.id};
  6536 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId,attemptId:attempt.id,assignmentDate:state.selectedDate,room:no,beforeMaidId:maidId,afterMaidId:maidId,before:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(previousWorkDate)} ${previousAccessStart}`:'미배정',after:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(state.selectedDate)} ${state.time}`:'미배정',reason:'실제 체크아웃 반영 · 기존 담당·수행 회차 유지 · 시작 시각 변경 재통보'});
  6537 |         if(maidId)appendEvent('내 청소 시작 시각 변경 통보',`${no}호 · ${dateLabel(previousWorkDate)} ${previousAccessStart} → ${dateLabel(state.selectedDate)} ${state.time} · 담당·회차 ${attempt.id} 유지`,{maidIds:[maidId],roomId:no});
  6538 |       }
  6539 |       function openManualCheckout(no,trigger=document.activeElement) {
  6540 |         const room=ROOMS.find(item=>item.no===no),blockingAttempt=manualCheckoutBlockingAttempt(no),unstartedAttempt=activeUnfinishedAttempt(no),pinViewed=unstartedAttempt&&roomPinWasViewed(no,unstartedAttempt.id);
  6541 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='occupied'){toast('관리자 최신 상태의 투숙 중 객실만 지금 체크아웃할 수 있습니다.','error');return;}
  6542 |         if(blockingAttempt){toast(`진행 중인 ${blockingAttempt.kind} ${blockingAttempt.id}을 먼저 마무리하세요.`,'error');return;}
  6543 |         showModal({title:`${no}호 지금 체크아웃`,subtitle:'예정 일정은 남기고 실제 퇴실만 지금 기록합니다.',trigger,body:`<div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>투숙 중</strong></div><div class="info-item"><span>실제 체크아웃</span><strong>${dateLabel(state.selectedDate)} ${esc(state.time)}</strong></div><div class="info-item"><span>예정 체크아웃</span><strong>${esc(plannedCheckoutLabel(room))}</strong></div><div class="info-item"><span>처리 결과</span><strong>공실 · 퇴실 청소 필요</strong></div></div><div class="notice notice-warning" style="margin-top:14px"><div><strong>예약 취소가 아닙니다.</strong><br>예정 일정과 미래 예약은 유지하고 오늘 퇴실 청소는 한 건만 만듭니다.${unstartedAttempt?'<br>이미 배정된 미시작 청소는 담당과 순서를 유지하고 실제 퇴실 시각부터 시작할 수 있습니다.':''}${pinViewed?'<br>기존 PIN 조회는 종료되며 실제 퇴실 시각 이후 다시 확인할 수 있습니다.':''}</div></div>`,confirmLabel:'투숙 종료·청소 준비',confirmAction:'confirm-manual-checkout',confirmVariant:'danger'});
  6544 |         const confirm=document.querySelector('[data-action="confirm-manual-checkout"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6545 |       }
  6546 |       function openManualCheckin(no,trigger=document.activeElement) {
  6547 |         const room=ROOMS.find(item=>item.no===no),presentation=roomPresentation(no);
  6548 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='vacant'||presentation.available!==true){toast('청소·촛불·운영 조건이 모두 준비된 공실만 투숙 중으로 바꿀 수 있습니다.','error');return;}
  6549 |         showModal({title:`${no}호 투숙 시작`,subtitle:'현재 객실에 손님이 들어온 사실만 기록합니다.',trigger,body:`<div class="notice notice-info"><div><strong>고객 개인정보는 입력하지 않습니다.</strong><br>${dateLabel(state.selectedDate)} ${esc(state.time)}부터 객실 상태를 투숙 중으로 바꿉니다.</div></div>`,confirmLabel:'투숙 중으로 변경',confirmAction:'confirm-manual-checkin'});
  6550 |         const confirm=document.querySelector('[data-action="confirm-manual-checkin"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6551 |       }
  6552 |       function reservationNextRegistrationState(room,existing,buckets) {
  6553 |         const weekPast=reservationWeekIsPast(buckets.window.startDate),occupiedEnd=occupiedReservationEnd(room),needsCheckoutUpdate=occupiedStayNeedsCheckoutUpdate(room);
  6554 |         return {canAdd:!!existing&&!weekPast&&adminCanMutate()&&(room.occupancy!=='occupied'||!!occupiedEnd&&!needsCheckoutUpdate),nextDate:suggestedReservationStartDate(room.no),weekPast,occupiedEnd,needsCheckoutUpdate};
  6555 |       }
  6556 |       function reservationWeekScheduleMarkup(room,existing,buckets) {
  6557 |         const nextRegistration=reservationNextRegistrationState(room,existing,buckets),records=buckets.weekRecords,countLabel=nextRegistration.weekPast?`기록 ${records.length}건`:`예약 ${records.filter(item=>item.status==='active'&&!reservationRecordIsPast(item)).length}건`,eligibilityNote=existing&&!nextRegistration.weekPast&&room.occupancy==='occupied'&&(!nextRegistration.occupiedEnd||nextRegistration.needsCheckoutUpdate)?`<p class="reservation-week-note">${icon('alert','icon-sm')}${nextRegistration.needsCheckoutUpdate?'예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리하세요.':'현재 투숙의 체크아웃을 먼저 입력하세요.'}</p>`:'',rows=records.map(reservation=>{
  6558 |           const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정'),content=`<span class="reservation-list-period"><strong>${esc(quickRangeLabel(reservation))}</strong></span><span class="reservation-list-meta">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span><span class="reservation-list-status">${esc(status)}</span><span class="reservation-list-arrow">${readOnly?'':icon('chevronRight','icon-sm')}</span>`;
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6608 |           bindRecordAction('confirm-finish-payment','CHECK');bindRecordAction('confirm-payment-open-v2','CHECK');return;
  6609 |         }
  6610 |         const confirmedTasks=context.tasks.filter(task=>task.stage==='confirmed'),bombTasks=confirmedTasks.filter(task=>task.bombBonus>0),bombText=bombTasks.length?bombTasks.map(task=>`${task.room} · ${money(task.baseAmount)} + ${money(task.bombBonus)} = ${money(task.amount)}`).join('<br>'):'해당 없음';
  6611 |         showModal({title:`${context.maid.name} 지급 진행을 시작할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확정합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong><br>외부 송금을 마친 뒤 같은 메이드 스위치에서 지급 완료를 기록하세요. 다른 메이드 상태는 바뀌지 않습니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>지급 주차</span><strong>${weekRangeLabel(context.cfg.start)}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.totals.confirmed)} · 데모</strong></div><div class="info-item"><span>확정 청소</span><strong>${confirmedTasks.length}건</strong></div><div class="info-item field-full"><span>폭탄방 포함 내역</span><strong>${bombText}</strong></div></div>`,confirmLabel:'지급 진행 시작',confirmAction:'confirm-toggle-payment',confirmVariant:'primary'});
  6612 |         const confirm=document.querySelector('[data-action="confirm-toggle-payment"]');if(confirm){confirm.dataset.week=context.cfg.start;confirm.dataset.maid=context.maid.id;confirm.dataset.expected='OPEN';confirm.dataset.amount=String(context.totals.confirmed);confirm.dataset.tasks=paymentTaskFingerprint(context);}
  6613 |       }
  6614 | 
  6615 |       function timeMinutes(t){const [h,m]=String(t).split(':').map(Number);return h*60+m;}
  6616 | 
  6617 |       function maskPin() {
  6618 |         clearTimeout(pinTimer);pinTimer=null;state.pinVisibleRoom=null;state.pinVisibleUntil=0;activePinRevealSecret=null;clearAllPinModalSecrets(true);
  6619 |       }
  6620 |       function revealPin(no) {
  6621 |         maskPin();const expiresAt=Date.now()+30000;state.pinVisibleRoom=no;state.pinVisibleUntil=expiresAt;activePinRevealSecret={room:no,value:readProtectedPin(no),expiresAt};
  6622 |         appendEvent(`${no}호 PIN 조회`,'원문 없이 조회 사용자·시각만 감사 기록',{maidIds:state.role==='maid'?[signedInMaidId()]:[],roomId:no,attemptId:currentAttemptId(no)||null});render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-hide"]`)?.focus());
  6623 |         pinTimer=setTimeout(()=>{if(state.pinVisibleRoom===no){maskPin();render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-show"]`)?.focus());toast('30초가 지나 객실 PIN을 다시 가렸습니다.');}},30000);
  6624 |       }
  6625 |       function toastUndo(message,action,id='') {
  6626 |         const root=document.getElementById('toast-region');
  6627 |         root.innerHTML=`<div class="toast undo-toast" role="status"><span>${esc(message)}</span><button type="button" data-action="${action}" ${id?`data-id="${id}"`:''}>실행 취소</button></div>`;
  6628 |         clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',10000);document.getElementById('assertive-live').textContent=`${message} 10초 동안 실행 취소할 수 있습니다.`;
  6629 |       }
  6630 |       function openBombRoomDecision(type,no,trigger=document.activeElement) {
  6631 |         const submission=currentSubmission(no),report=submittedBombRoomReport(no);
  6632 |         if(state.role!=='admin'||state.inspections[no]!=='pending'||state.jobs[no]!=='inspection'||submission?.status!=='pending'||report?.status!=='pending'||isLocked()){toast('검수 대기 중인 폭탄방 신고만 관리자가 결정할 수 있습니다.','error');return;}
  6633 |         if(type==='approve')showModal({title:`${no}호 폭탄방을 인정할까요?`,subtitle:`이미지 ${report.photos.length}장 확인 · 이 객실의 청소요금만 2배`,trigger,body:`${bombRoomFeeMarkup(no,report)}<div class="notice notice-success" style="margin-top:12px"><div><strong>해당 객실만 ${money(report.baseRateSnapshot*2)}</strong><br>주간 전체 금액이 아니라 ${no}호 기본 ${money(report.baseRateSnapshot)}에 같은 금액 한 건만 추가합니다.</div></div>`,confirmLabel:'폭탄방 인정 · 2배',confirmAction:'confirm-approve-bomb-room',confirmVariant:'success'});
  6634 |         else showModal({title:`${no}호 폭탄방 미인정`,subtitle:'증빙은 보존하고 해당 객실에는 기본 청소요금만 적용합니다.',trigger,body:`${bombRoomFeeMarkup(no,report)}<div class="field" style="margin-top:12px"><label for="bomb-room-reject-reason">미인정 사유</label><textarea id="bomb-room-reject-reason" class="input-control" rows="4" required>일반 청소 범위로 판단 · 데모</textarea></div>`,confirmLabel:'폭탄방 미인정',confirmAction:'confirm-reject-bomb-room',confirmVariant:'danger'});
  6635 |         const confirm=document.querySelector(`[data-action="confirm-${type==='approve'?'approve':'reject'}-bomb-room"]`);confirm?.setAttribute('data-id',no);confirm?.setAttribute('data-submission',submission.id);confirm?.setAttribute('data-report',report.id);
  6636 |       }
  6637 | 
  6638 |       function openInspectionDecisionV2(type,no) {
  6639 |         const submission=currentSubmission(no),report=submittedBombRoomReport(no),fee=bombRoomBreakdown(no,{reportOverride:report,baseOverride:submission?.baseRateSnapshot}),unpaidReclean=submission?.kind==='재청소';
  6640 |         if(state.role!=='admin'||state.inspections[no]!=='pending'||state.jobs[no]!=='inspection'||submission?.status!=='pending'||isLocked()){toast('최신 검수 대기 상태에서만 관리자가 전체 검수를 결정할 수 있습니다.','error');return;}
  6641 |         if(submission.reportId&&!report){toast('제출과 폭탄방 신고 연결이 일치하지 않아 검수를 진행할 수 없습니다. 최신 상태를 다시 확인해 주세요.','error');return;}
  6642 |         if(report?.status==='pending'){toast('폭탄방 신고를 먼저 인정하거나 미인정으로 결정하세요.','error');document.querySelector(`[data-action="approve-bomb-room"][data-id="${no}"]`)?.focus();return;}
  6643 |         if(type==='approve') showModal({title:`${no}호 전체 제출을 승인할까요?`,subtitle:unpaidReclean?'무급 재청소 완료 이력만 확정합니다.':'최신 제출 전체와 한 건의 확정 적립만 만듭니다.',body:`${bombRoomFeeMarkup(no,report)}${unpaidReclean?'<div class="notice notice-info" style="margin-top:12px"><div><strong>재청소 승인 · 적립 0원</strong><br>처음 청소한 본인의 완료 이력만 보존하며 폭탄방 추가요금과 수익 원장은 생성하지 않습니다.</div></div>':`<div class="notice notice-success" style="margin-top:12px"><div><strong>이번 승인 확정 ${money(fee.total)}</strong><br>기본 ${money(fee.base)}${fee.bonus?` + 폭탄방 추가 ${money(fee.bonus)} = 정확히 2배`:''}가 실제 수행자의 이번 주 내역에 한 번만 쌓입니다. 촛불·운영·점유 상태는 별도로 다시 계산합니다.</div></div>`}`,confirmLabel:unpaidReclean?'재청소 승인 · 0원':'전체 승인·금액 확정',confirmAction:'confirm-approve-v2',confirmVariant:'success'});
  6644 |         else showModal({title:`${no}호 전체 제출 반려`,subtitle:'사진별이 아니라 제출 전체를 반려하고 본인 재청소를 만듭니다.',body:`<div class="field"><label for="reject-reason-v2">반려 사유</label><textarea id="reject-reason-v2" class="input-control" rows="4" required>욕실 거울 얼룩 재확인 필요 · 데모</textarea></div><div class="notice notice-warning" style="margin-top:12px">기존 수행 이력과 제출 자료는 삭제하지 않습니다. 처음 청소한 본인에게 무급 재청소가 자동 배정되며 다른 메이드에게 넘길 수 없습니다.</div>`,confirmLabel:'전체 반려·본인 재청소',confirmAction:'confirm-reject-v2',confirmVariant:'danger'});
```

### occurrence 3 · line 6589

```html
  6544 |         const confirm=document.querySelector('[data-action="confirm-manual-checkout"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6545 |       }
  6546 |       function openManualCheckin(no,trigger=document.activeElement) {
  6547 |         const room=ROOMS.find(item=>item.no===no),presentation=roomPresentation(no);
  6548 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='vacant'||presentation.available!==true){toast('청소·촛불·운영 조건이 모두 준비된 공실만 투숙 중으로 바꿀 수 있습니다.','error');return;}
  6549 |         showModal({title:`${no}호 투숙 시작`,subtitle:'현재 객실에 손님이 들어온 사실만 기록합니다.',trigger,body:`<div class="notice notice-info"><div><strong>고객 개인정보는 입력하지 않습니다.</strong><br>${dateLabel(state.selectedDate)} ${esc(state.time)}부터 객실 상태를 투숙 중으로 바꿉니다.</div></div>`,confirmLabel:'투숙 중으로 변경',confirmAction:'confirm-manual-checkin'});
  6550 |         const confirm=document.querySelector('[data-action="confirm-manual-checkin"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6551 |       }
  6552 |       function reservationNextRegistrationState(room,existing,buckets) {
  6553 |         const weekPast=reservationWeekIsPast(buckets.window.startDate),occupiedEnd=occupiedReservationEnd(room),needsCheckoutUpdate=occupiedStayNeedsCheckoutUpdate(room);
  6554 |         return {canAdd:!!existing&&!weekPast&&adminCanMutate()&&(room.occupancy!=='occupied'||!!occupiedEnd&&!needsCheckoutUpdate),nextDate:suggestedReservationStartDate(room.no),weekPast,occupiedEnd,needsCheckoutUpdate};
  6555 |       }
  6556 |       function reservationWeekScheduleMarkup(room,existing,buckets) {
  6557 |         const nextRegistration=reservationNextRegistrationState(room,existing,buckets),records=buckets.weekRecords,countLabel=nextRegistration.weekPast?`기록 ${records.length}건`:`예약 ${records.filter(item=>item.status==='active'&&!reservationRecordIsPast(item)).length}건`,eligibilityNote=existing&&!nextRegistration.weekPast&&room.occupancy==='occupied'&&(!nextRegistration.occupiedEnd||nextRegistration.needsCheckoutUpdate)?`<p class="reservation-week-note">${icon('alert','icon-sm')}${nextRegistration.needsCheckoutUpdate?'예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리하세요.':'현재 투숙의 체크아웃을 먼저 입력하세요.'}</p>`:'',rows=records.map(reservation=>{
  6558 |           const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정'),content=`<span class="reservation-list-period"><strong>${esc(quickRangeLabel(reservation))}</strong></span><span class="reservation-list-meta">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span><span class="reservation-list-status">${esc(status)}</span><span class="reservation-list-arrow">${readOnly?'':icon('chevronRight','icon-sm')}</span>`;
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
  6590 |         const reservation=state.reservations.find(item=>item.id===reservationId&&item.status==='active')||null;
  6591 |         if(!adminCanMutate()){toast('관리자 최신 온라인 상태에서만 예약을 취소할 수 있습니다.','error');return;}
  6592 |         if(!reservation||reservationFingerprint(reservation)!==expectedFingerprint){toast('예약 일정이 바뀌었거나 이미 취소되었습니다. 최신 예약을 다시 열어 주세요.','error');return;}
  6593 |         const impact=reservationCancellationImpact(reservation);if(impact.blockedReason){toast(impact.blockedReason,'error');return;}
  6594 |         const assignmentStatus=impact.manualTarget?`별도 등록한 현장 청소 요청 · 담당과 일정 유지`:impact.assignmentRecord?(impact.notifiedMaidId?`${maidName(impact.notifiedMaidId)} · 통보 완료 → 담당 취소 통보`:(impact.selectedMaidId?`${maidName(impact.selectedMaidId)} · 저장 전 선택 해제`:'미배정 상태 취소')):'청소 미배정',adjacentText=impact.adjacentChanges.length?impact.adjacentChanges.map(entry=>`${entry.reservation.room}호 ${quickRangeLabel(entry.reservation)} · 준비 마감 ${entry.before.deadline} → ${entry.after.deadline}`).join('<br>'):'변경되는 인접 예약 없음',impactFingerprint=reservationCancellationImpactFingerprint(reservation,impact);
  6595 |         showModal({title:`${reservation.room}호 예약을 취소할까요?`,subtitle:'청소 담당과 일정 영향을 확인한 뒤 취소하세요.',trigger,historyKind:'reservation-cancel',historyPayload:{room:reservation.room,reservationId:reservation.id},historyStack:true,closeLabel:'돌아가기',body:`<div class="info-grid"><div class="info-item"><span>취소 대상</span><strong>${reservation.room}호 · ${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</strong></div><div class="info-item"><span>예약 일정</span><strong>${esc(quickRangeLabel(reservation))}</strong></div><div class="info-item"><span>퇴실 청소 준비</span><strong>${impact.privateDrafts.length}건 · 함께 취소</strong></div><div class="info-item"><span>청소 담당 영향</span><strong>${esc(assignmentStatus)}</strong></div><div class="info-item"><span>인접 예약 청소 마감</span><strong>${adjacentText}</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>외부 예약은 취소되지 않습니다.</strong><br>외부 OTA/PMS에서도 예약 취소 여부를 따로 확인하세요.</div></div><div class="field" style="margin-top:14px"><label for="reservation-cancel-reason">예약 취소 사유</label><select id="reservation-cancel-reason" class="select-control" data-control="reservation-cancel-reason" required><option value="">사유를 선택하세요</option>${Object.entries(RESERVATION_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>고객 개인정보를 적지 않는 정해진 운영 사유만 이력과 알림에 남깁니다.</small></div>`,confirmLabel:'예약 취소 확정',confirmAction:'confirm-reservation-cancel',confirmVariant:'danger'});
  6596 |         const confirm=document.querySelector('[data-action="confirm-reservation-cancel"]');if(confirm){confirm.dataset.id=reservation.id;confirm.dataset.fingerprint=expectedFingerprint;confirm.dataset.impact=impactFingerprint;confirm.disabled=true;}
  6597 |       }
  6598 |       function openPaymentConfirm(weekStart,maidId,trigger=document.activeElement) {
  6599 |         const context=paymentContextFor(weekStart,maidId);
  6600 |         if(!context||context.meta.locked||!['OPEN','PAYING','CHECK'].includes(context.meta.status)){toast(context?.meta.status==='PAID'?'지급 완료 기록은 직접 취소하지 않고 정정·상계로 처리합니다.':'현재 이 메이드의 지급 상태를 변경할 수 없습니다.','error');return;}
  6601 |         const bindRecordAction=(action,expected=context.meta.status)=>{const target=document.querySelector(`[data-action="${action}"]`);if(target){target.dataset.week=context.cfg.start;target.dataset.maid=context.maid.id;target.dataset.expected=expected;target.dataset.record=paymentRecordFingerprint(context.record);}};
  6602 |         if(context.meta.status==='PAYING'){
  6603 |           showModal({title:`${context.maid.name} 송금 결과를 기록할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확인합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>실제 전액 송금이 끝난 경우에만 완료하세요.</strong><br>송금 여부가 불명확하면 확인 필요로 두고, 송금하지 않았다면 사유를 남겨 지급 대기로 돌립니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 확인 전이라 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금 여부 확인 필요','mark-payment-check','outline')}${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6604 |           bindRecordAction('confirm-finish-payment','PAYING');bindRecordAction('mark-payment-check','PAYING');bindRecordAction('confirm-payment-open-v2','PAYING');return;
  6605 |         }
  6606 |         if(context.meta.status==='CHECK'){
  6607 |           showModal({title:`${context.maid.name} 지급 결과를 다시 확인하세요`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 송금 결과를 확인해 상태를 정합니다.`,trigger,body:`<div class="notice notice-danger"><div><strong>외부 송금 결과를 확인한 뒤 한 가지 결과만 기록하세요.</strong><br>완료라면 이번 지급액과 청소 내역으로 지급 완료를 기록하고, 미송금이면 사유를 남겨 지급 대기로 돌아갑니다.</div></div><div class="info-grid"><div class="info-item"><span>담당 관리자</span><strong>${esc(paymentManagerLabel(context.record))}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.record.amountSnapshot||0)} · 데모</strong></div><div class="info-item"><span>청소 내역</span><strong>${context.record.taskIds.length}건</strong></div><div class="info-item"><span>지급 진행 시작</span><strong>${esc(context.record.startedAt||'기록됨')}</strong></div></div><div class="field" style="margin-top:14px"><label for="payment-resolution-reason">송금하지 않음 사유</label><textarea id="payment-resolution-reason" class="input-control" rows="3" placeholder="예: 계좌 오류를 확인해 송금하지 않음"></textarea><small>지급 대기로 돌아갈 때 필수이며 변경 이력에 남습니다.</small></div><div class="job-actions" style="margin-top:12px">${button('송금하지 않음 · 대기 복귀','confirm-payment-open-v2','outline')}</div>`,confirmLabel:'외부 송금 완료 재기록',confirmAction:'confirm-finish-payment',confirmVariant:'success'});
  6608 |           bindRecordAction('confirm-finish-payment','CHECK');bindRecordAction('confirm-payment-open-v2','CHECK');return;
  6609 |         }
  6610 |         const confirmedTasks=context.tasks.filter(task=>task.stage==='confirmed'),bombTasks=confirmedTasks.filter(task=>task.bombBonus>0),bombText=bombTasks.length?bombTasks.map(task=>`${task.room} · ${money(task.baseAmount)} + ${money(task.bombBonus)} = ${money(task.amount)}`).join('<br>'):'해당 없음';
  6611 |         showModal({title:`${context.maid.name} 지급 진행을 시작할까요?`,subtitle:`${weekRangeLabel(context.cfg.start,true)} · 이번 지급액과 청소 내역을 확정합니다.`,trigger,body:`<div class="notice notice-warning"><div><strong>앱은 송금하지 않고 지급 여부만 기록합니다.</strong><br>외부 송금을 마친 뒤 같은 메이드 스위치에서 지급 완료를 기록하세요. 다른 메이드 상태는 바뀌지 않습니다.</div></div><div class="info-grid"><div class="info-item"><span>메이드</span><strong>${esc(context.maid.name)}</strong></div><div class="info-item"><span>지급 주차</span><strong>${weekRangeLabel(context.cfg.start)}</strong></div><div class="info-item"><span>이번 지급액</span><strong>${money(context.totals.confirmed)} · 데모</strong></div><div class="info-item"><span>확정 청소</span><strong>${confirmedTasks.length}건</strong></div><div class="info-item field-full"><span>폭탄방 포함 내역</span><strong>${bombText}</strong></div></div>`,confirmLabel:'지급 진행 시작',confirmAction:'confirm-toggle-payment',confirmVariant:'primary'});
  6612 |         const confirm=document.querySelector('[data-action="confirm-toggle-payment"]');if(confirm){confirm.dataset.week=context.cfg.start;confirm.dataset.maid=context.maid.id;confirm.dataset.expected='OPEN';confirm.dataset.amount=String(context.totals.confirmed);confirm.dataset.tasks=paymentTaskFingerprint(context);}
  6613 |       }
  6614 | 
  6615 |       function timeMinutes(t){const [h,m]=String(t).split(':').map(Number);return h*60+m;}
  6616 | 
  6617 |       function maskPin() {
  6618 |         clearTimeout(pinTimer);pinTimer=null;state.pinVisibleRoom=null;state.pinVisibleUntil=0;activePinRevealSecret=null;clearAllPinModalSecrets(true);
  6619 |       }
  6620 |       function revealPin(no) {
  6621 |         maskPin();const expiresAt=Date.now()+30000;state.pinVisibleRoom=no;state.pinVisibleUntil=expiresAt;activePinRevealSecret={room:no,value:readProtectedPin(no),expiresAt};
  6622 |         appendEvent(`${no}호 PIN 조회`,'원문 없이 조회 사용자·시각만 감사 기록',{maidIds:state.role==='maid'?[signedInMaidId()]:[],roomId:no,attemptId:currentAttemptId(no)||null});render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-hide"]`)?.focus());
  6623 |         pinTimer=setTimeout(()=>{if(state.pinVisibleRoom===no){maskPin();render();requestAnimationFrame(()=>document.querySelector(`[data-pin-room="${no}"] [data-action="pin-show"]`)?.focus());toast('30초가 지나 객실 PIN을 다시 가렸습니다.');}},30000);
  6624 |       }
  6625 |       function toastUndo(message,action,id='') {
  6626 |         const root=document.getElementById('toast-region');
  6627 |         root.innerHTML=`<div class="toast undo-toast" role="status"><span>${esc(message)}</span><button type="button" data-action="${action}" ${id?`data-id="${id}"`:''}>실행 취소</button></div>`;
  6628 |         clearTimeout(toastTimer);toastTimer=setTimeout(()=>root.innerHTML='',10000);document.getElementById('assertive-live').textContent=`${message} 10초 동안 실행 취소할 수 있습니다.`;
  6629 |       }
  6630 |       function openBombRoomDecision(type,no,trigger=document.activeElement) {
  6631 |         const submission=currentSubmission(no),report=submittedBombRoomReport(no);
  6632 |         if(state.role!=='admin'||state.inspections[no]!=='pending'||state.jobs[no]!=='inspection'||submission?.status!=='pending'||report?.status!=='pending'||isLocked()){toast('검수 대기 중인 폭탄방 신고만 관리자가 결정할 수 있습니다.','error');return;}
  6633 |         if(type==='approve')showModal({title:`${no}호 폭탄방을 인정할까요?`,subtitle:`이미지 ${report.photos.length}장 확인 · 이 객실의 청소요금만 2배`,trigger,body:`${bombRoomFeeMarkup(no,report)}<div class="notice notice-success" style="margin-top:12px"><div><strong>해당 객실만 ${money(report.baseRateSnapshot*2)}</strong><br>주간 전체 금액이 아니라 ${no}호 기본 ${money(report.baseRateSnapshot)}에 같은 금액 한 건만 추가합니다.</div></div>`,confirmLabel:'폭탄방 인정 · 2배',confirmAction:'confirm-approve-bomb-room',confirmVariant:'success'});
  6634 |         else showModal({title:`${no}호 폭탄방 미인정`,subtitle:'증빙은 보존하고 해당 객실에는 기본 청소요금만 적용합니다.',trigger,body:`${bombRoomFeeMarkup(no,report)}<div class="field" style="margin-top:12px"><label for="bomb-room-reject-reason">미인정 사유</label><textarea id="bomb-room-reject-reason" class="input-control" rows="4" required>일반 청소 범위로 판단 · 데모</textarea></div>`,confirmLabel:'폭탄방 미인정',confirmAction:'confirm-reject-bomb-room',confirmVariant:'danger'});
  6635 |         const confirm=document.querySelector(`[data-action="confirm-${type==='approve'?'approve':'reject'}-bomb-room"]`);confirm?.setAttribute('data-id',no);confirm?.setAttribute('data-submission',submission.id);confirm?.setAttribute('data-report',report.id);
  6636 |       }
  6637 | 
  6638 |       function openInspectionDecisionV2(type,no) {
  6639 |         const submission=currentSubmission(no),report=submittedBombRoomReport(no),fee=bombRoomBreakdown(no,{reportOverride:report,baseOverride:submission?.baseRateSnapshot}),unpaidReclean=submission?.kind==='재청소';
  6640 |         if(state.role!=='admin'||state.inspections[no]!=='pending'||state.jobs[no]!=='inspection'||submission?.status!=='pending'||isLocked()){toast('최신 검수 대기 상태에서만 관리자가 전체 검수를 결정할 수 있습니다.','error');return;}
  6641 |         if(submission.reportId&&!report){toast('제출과 폭탄방 신고 연결이 일치하지 않아 검수를 진행할 수 없습니다. 최신 상태를 다시 확인해 주세요.','error');return;}
  6642 |         if(report?.status==='pending'){toast('폭탄방 신고를 먼저 인정하거나 미인정으로 결정하세요.','error');document.querySelector(`[data-action="approve-bomb-room"][data-id="${no}"]`)?.focus();return;}
  6643 |         if(type==='approve') showModal({title:`${no}호 전체 제출을 승인할까요?`,subtitle:unpaidReclean?'무급 재청소 완료 이력만 확정합니다.':'최신 제출 전체와 한 건의 확정 적립만 만듭니다.',body:`${bombRoomFeeMarkup(no,report)}${unpaidReclean?'<div class="notice notice-info" style="margin-top:12px"><div><strong>재청소 승인 · 적립 0원</strong><br>처음 청소한 본인의 완료 이력만 보존하며 폭탄방 추가요금과 수익 원장은 생성하지 않습니다.</div></div>':`<div class="notice notice-success" style="margin-top:12px"><div><strong>이번 승인 확정 ${money(fee.total)}</strong><br>기본 ${money(fee.base)}${fee.bonus?` + 폭탄방 추가 ${money(fee.bonus)} = 정확히 2배`:''}가 실제 수행자의 이번 주 내역에 한 번만 쌓입니다. 촛불·운영·점유 상태는 별도로 다시 계산합니다.</div></div>`}`,confirmLabel:unpaidReclean?'재청소 승인 · 0원':'전체 승인·금액 확정',confirmAction:'confirm-approve-v2',confirmVariant:'success'});
  6644 |         else showModal({title:`${no}호 전체 제출 반려`,subtitle:'사진별이 아니라 제출 전체를 반려하고 본인 재청소를 만듭니다.',body:`<div class="field"><label for="reject-reason-v2">반려 사유</label><textarea id="reject-reason-v2" class="input-control" rows="4" required>욕실 거울 얼룩 재확인 필요 · 데모</textarea></div><div class="notice notice-warning" style="margin-top:12px">기존 수행 이력과 제출 자료는 삭제하지 않습니다. 처음 청소한 본인에게 무급 재청소가 자동 배정되며 다른 메이드에게 넘길 수 없습니다.</div>`,confirmLabel:'전체 반려·본인 재청소',confirmAction:'confirm-reject-v2',confirmVariant:'danger'});
  6645 |         const confirm=document.querySelector(`[data-action="confirm-${type==='approve'?'approve':'reject'}-v2"]`);confirm?.setAttribute('data-id',no);confirm?.setAttribute('data-submission',submission.id);if(report)confirm?.setAttribute('data-report',report.id);
  6646 |       }
  6647 | 
  6648 |       function selectedDraftBatch(ids=state.selectedDrafts) {
  6649 |         const raw=Array.isArray(ids)?ids:[], unique=[...new Set(raw)];
  6650 |         const selected=unique.map(draftId=>state.drafts.find(d=>d.id===draftId));
  6651 |         const rooms=selected.filter(Boolean).map(d=>d.room);
  6652 |         let reason='';
  6653 |         if(!unique.length) reason='내일 배정에서 처리할 준비 작업을 먼저 선택하세요.';
  6654 |         else if(unique.length!==raw.length||selected.some(d=>!d)) reason='선택 목록이 최신 초안과 일치하지 않습니다.';
  6655 |         else if(new Set(rooms).size!==rooms.length) reason='같은 객실의 중복 준비 작업은 함께 처리할 수 없습니다.';
  6656 |         else if(selected.some(d=>!ROOMS.some(room=>room.no===d.room)||!String(d.kind||'').trim()||!String(d.created||'').trim())) reason='객실·청소 유형·생성 시각이 완전한 준비 작업만 처리할 수 있습니다.';
  6657 |         else if(selected.some(d=>state.publications?.[d.id])) reason='이미 처리된 작업이 선택 목록에 포함되어 있습니다.';
  6658 |         return {valid:!reason,reason,ids:unique,selected:selected.filter(Boolean),rooms};
```

### occurrence 4 · line 6779

```html
  6734 |         showModal({title:'332호 영향 확인·충돌 해결',subtitle:'변경된 체크아웃과 현재 청소·PIN 조회 영향을 확인하세요.',large:true,trigger,body:`<div class="notice notice-danger"><div><strong>현재 상태 확인</strong><br>${record.autoCheckoutAt} 자동 체크아웃 기록은 남기고 ${record.afterCheckout}까지 투숙 중으로 표시합니다.</div></div><div class="info-grid"><div class="info-item"><span>체크아웃 전 → 후</span><strong>${record.beforeCheckout} → ${record.afterCheckout}</strong></div><div class="info-item"><span>청소 담당·단계</span><strong>${record.assignee} · ${record.stage}</strong></div><div class="info-item"><span>PIN 조회</span><strong>${record.pinViewedAt}</strong></div><div class="info-item"><span>PIN 조회 처리</span><strong>기존 조회 종료 후 다시 확인</strong></div></div><div class="choice-list" style="margin-top:14px"><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="coordinate" ${state.conflictSteps.coordinate?'checked':''} ${isLocked()?'disabled':''}><span><strong>현장 조율 완료</strong><span>투숙객·${record.assignee}에게 변경된 체크아웃과 출입 중단을 확인</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="replan" ${state.conflictSteps.replan?'checked':''} ${isLocked()?'disabled':''}><span><strong>청소 일정 변경 완료</strong><span>진행 중 청소를 중단 처리하고 ${record.afterCheckout} 새 청소 생성</span></span></label><label class="choice"><input type="checkbox" data-control="conflict-step-v2" value="pin" ${state.conflictSteps.pin?'checked':''} ${isLocked()?'disabled':''}><span><strong>도어락 PIN 확인 완료</strong><span>기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.</span></span></label></div>`,confirmLabel:'조치 완료',confirmAction:'confirm-conflict-v2',confirmVariant:'danger'});
  6735 |         const confirm=document.querySelector('[data-action="confirm-conflict-v2"]');
  6736 |         if(confirm)confirm.disabled=isLocked()||!Object.values(state.conflictSteps).every(Boolean);
  6737 |       }
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
  6785 |         if(a==='open-reservation-week-calendar'){
  6786 |           if(state.role!=='admin')return;state.reservationWeekRoom=el.dataset.room||state.reservationWeekRoom||'211';state.calendarMonth=weekStartIso(state.reservationWeekStart||state.selectedDate).slice(0,7);openCalendar(el,'reservation-week',true);return;
  6787 |         }
  6788 |         if(a==='reservation-add'){
  6789 |           const room=ROOMS.find(item=>item.no===String(el.dataset.room||'')),newDate=el.dataset.date||suggestedReservationStartDate(room?.no||'');
  6790 |           if(state.role!=='admin'||!adminCanMutate()||!room){toast('관리자 최신 상태에서만 다음 예약을 등록할 수 있습니다.','error');return;}
  6791 |           const block=reservationHardBlockReason(room);if(block){toast(`${room.no}호는 ${block} 상태라 다음 예약을 등록할 수 없습니다.`,'error');return;}
  6792 |           if(room.occupancy==='occupied'&&!occupiedReservationEnd(room)){toast('현재 투숙의 체크아웃을 먼저 입력해 주세요.','error');return;}
  6793 |           if(occupiedStayNeedsCheckoutUpdate(room)){toast('예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.','error');return;}
  6794 |           openReservation(room.no,'__new__',{weekStart:weekStartIso(newDate),newDate,historyStack:true,trigger:el});return;
  6795 |         }
  6796 |         if(a==='reservation-cancel-review'){openReservationCancellationReview(id,el.dataset.fingerprint||'',el);return;}
  6797 |         if(a==='confirm-reservation-cancel'){
  6798 |           const reasonCode=document.getElementById('reservation-cancel-reason')?.value||'',reasonError=reservationCancelReasonError(reasonCode);if(reasonError){toast(reasonError,'error');document.getElementById('reservation-cancel-reason')?.focus();return;}
  6799 |           const result=cancelReservationRecord({reservationId:id,expectedFingerprint:el.dataset.fingerprint||'',expectedImpactFingerprint:el.dataset.impact||'',reasonCode});
  6800 |           if(result.error){closeModal();render();toast(result.error,'error');return;}
  6801 |           const room=result.reservation.room,firstNight=result.reservation.checkInAt.slice(0,10),remaining=activeReservationsFor(state,room),pivot=`${state.selectedDate}T00:00`,cardReservation=remaining.find(item=>item.checkOutAt>pivot)||remaining[0]||null;
  6802 |           historyReturnFocus=state.adminView==='quickReservation'?{quickCell:true,room,date:firstNight}:state.detail?.type==='room'?{action:'reservation-edit',id:room}:cardReservation?{action:'quick-reservation-edit',id:cardReservation.id,room}:{action:'reservation-edit',id:room};
  6803 |           closeModal();render();if(state.adminView==='quickReservation')restoreQuickGridViewport(`[data-quick-cell][data-room="${room}"][data-date="${firstNight}"]`);toast(`${room}호 ${reservationNights(result.reservation)}박 예약을 취소했습니다.`);return;
  6804 |         }
  6805 |         if(a==='quick-reservation-undo'){
  6806 |           if(!adminCanMutate()||state.quickLastCreated?.reservationId!==id||Date.now()-Number(state.quickLastCreated?.createdAt)>10500){toast('실행 취소 시간이 지났거나 최신 상태가 바뀌었습니다.','error');return;}
  6807 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active'),room=state.quickLastCreated.room,firstNight=reservation?.checkInAt.slice(0,10);if(removeQuickReservation(id,{undo:true})){state.quickLastCreated=null;render();restoreQuickGridViewport(`[data-room="${room}"][data-date="${firstNight}"]`);toast(`${room}호 예약 접수를 되돌렸습니다.`);}else toast('청소 배정 또는 예약 상태가 바뀌어 방금 접수 실행 취소를 중단했습니다.','error');return;
  6808 |         }
  6809 |         if(a==='filter-rooms'){
  6810 |           const filter=el.dataset.filter;
  6811 |           if(state.role!=='admin'||!['occupied','cleaning','available','blocked','checkout-inspection'].includes(filter))return;
  6812 |           maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();
  6813 |           state.detail=null;state.adminView='rooms';state.roomSearch='';state.roomTypeFilter='all';state.roomFilter=filter;
  6814 |           pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.querySelector('[data-control="room-filter"]')?.focus({preventScroll:true});});return;
  6815 |         }
  6816 |         if(a==='filter-room-type'){
  6817 |           const typeId=el.dataset.type;if(state.role!=='admin'||state.adminView!=='rooms'||!(typeId==='all'||ROOM_TYPES[typeId]))return;
  6818 |           state.roomTypeFilter=typeId;state.roomFilter='all';state.roomSearch='';render();requestAnimationFrame(()=>document.querySelector(`[data-action="filter-room-type"][data-type="${typeId}"]`)?.focus({preventScroll:true}));return;
  6819 |         }
  6820 |         if(a==='back'){maskPin();backFromDetail();return;}
  6821 |         if(a==='close-modal'||a==='backdrop-close'||a==='calendar-close'||a==='calendar-backdrop'){pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;dismissModal();return;}
  6822 |         if(a==='room-detail'){maskPin();if(state.adminView==='quickReservation'&&!state.detail)rememberQuickGridViewport();openDetail('room',id||'350',el);return;}
  6823 |         if(a==='cleaning-detail'){maskPin();openDetail('cleaning',id||'639',el);return;}
  6824 |         if(a==='maid-detail'){maskPin();openDetail('maid',id||'m1',el);return;}
  6825 |         if(a==='resolve-conflict-v2'){if(!adminCanMutate()){toast('관리자 최신 상태에서만 충돌을 해결할 수 있습니다.','error');return;}if(activeRecleanAttempt('332')){toast('332호 본인 무급 재청소가 끝난 뒤 충돌 재계획을 진행할 수 있습니다.','error');return;}openConflictResolutionV2(el);return;}
  6826 |         if(a==='confirm-conflict-v2'){
  6827 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 충돌을 종결하지 않았습니다.','error');return;}
  6828 |           if(activeRecleanAttempt('332')){closeModal();render();toast('332호 본인 무급 재청소를 유지하기 위해 충돌 재계획을 적용하지 않았습니다.','error');return;}
  6829 |           const previousAttemptId=currentAttemptId('332'),previousAttempt=previousAttemptId?state.cleaningAttempts?.[previousAttemptId]:null;
  6830 |           if(state.conflict!=='active'||state.jobs['332']!=='cleaning'||previousAttempt?.status!=='cleaning'||previousAttempt.room!=='332') { closeModal();render();toast('332호 충돌 또는 수행 회차가 바뀌어 재계획을 적용하지 않았습니다.','error');return; }
  6831 |           if(!Object.values(state.conflictSteps).every(Boolean)){toast('현장 조율·작업 재계획·필요 PIN 교체를 모두 확인해야 합니다.','error');return;}
  6832 |           if(activeCleaningFor(previousAttempt.performerId)==='332')setActiveCleaningFor(previousAttempt.performerId,null);
  6833 |           const previousWorkDate=attemptWorkDate(previousAttempt,state.selectedDate),previousWorkTargetId=previousAttempt.workTargetId||assignmentHistoryTargetId('332',previousAttempt.kind,previousWorkDate),replannedAttempt=beginCleaningAttempt('332',{performerId:previousAttempt.performerId,performerName:previousAttempt.performerName,reason:'점유 재개 충돌 뒤 동일 수행자 새 일정 재계획',baseRateSnapshot:previousAttempt.baseRateSnapshot,kind:previousAttempt.kind,workDate:previousWorkDate,workTargetId:previousWorkTargetId,templateSnapshot:previousAttempt.templateSnapshot||templateSnapshotFor('332',previousAttempt.kind),accessStart:previousAttempt.accessStart,requestDue:previousAttempt.requestDue,accessEnd:previousAttempt.accessEnd,reservationIdSnapshot:previousAttempt.reservationIdSnapshot,guestCountSnapshot:previousAttempt.guestCountSnapshot});
  6834 |           state.conflict='resolved';state.conflictRecord.resolvedAt=state.time;state.jobs['332']='scheduled';
  6835 |           appendEvent('332호 점유 재개·출입 충돌 종결',`${state.conflictRecord.autoCheckoutAt} 자동 체크아웃 보존 · ${state.conflictRecord.afterCheckout} 점유 보정 · ${previousAttempt.performerName} ${previousAttempt.id} 중단 보존 → ${replannedAttempt.id} 재계획 · ${state.conflictRecord.leaseId} 종료`,{maidIds:[previousAttempt.performerId]});
  6836 |           closeModal();render();toast('충돌을 종결하고 점유·청소·PIN lease 상태를 재계산했습니다.');return;
  6837 |         }
  6838 |         if(a==='deactivate-maid-v2'){
  6839 |           const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
  6840 |           if(!maid){toast('메이드 계정을 찾을 수 없습니다.','error');return;}
  6841 |           if(!adminCanMutate()){toast('관리자 최신 상태에서만 비활성 처리를 시작할 수 있습니다.','error');return;}
  6842 |           if(maidStatusFor(maidId)!=='active'){toast(`${maid.name} 계정은 이미 ${maidDeactivationLabel(maidId)} 상태입니다.`,'error');return;}
  6843 |           if(reclean||pending||conflict){toast(reclean?`${reclean.room}호 본인 무급 재청소를 완료한 뒤 비활성 처리할 수 있습니다.`:pending?`${pending.room}호 검수 결정을 완료한 뒤 비활성 처리를 시작할 수 있습니다.`:`${conflict.room}호 출입·청소 충돌을 종결한 뒤 비활성 처리를 시작할 수 있습니다.`,'error');return;}
  6844 |           openMaidDeactivationV2(maidId,el);return;
  6845 |         }
  6846 |         if(a==='confirm-start-deactivation-v2'){
  6847 |           const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
  6848 |           if(!maid||!adminCanMutate()||maidStatusFor(maidId)!=='active'||reclean||pending||conflict){closeModal();render();toast(reclean?`${reclean.room}호 본인 무급 재청소가 남아 비활성 처리를 시작하지 않았습니다.`:pending?`${pending.room}호 검수 결정이 남아 비활성 처리를 시작하지 않았습니다.`:conflict?`${conflict.room}호 출입 충돌이 남아 비활성 처리를 시작하지 않았습니다.`:'메이드 계정 상태·관리자 권한 또는 최신 상태가 바뀌어 비활성 처리를 시작하지 않았습니다.','error');return;}
```

### occurrence 5 · line 6783

```html
  6738 | 
  6739 |       function openMaidDeactivationV2(maidId,trigger=document.activeElement) {
  6740 |         const maid=maidById(maidId),currentApproved=maidPayAmount(maid?.name||''),future=notifiedAssignmentEntriesForMaid(maidId).length,currentAttempts=unfinishedCurrentAttemptsForMaid(maidId),activeRoom=activeCleaningFor(maidId),uploadCount=currentAttempts.filter(({room})=>state.jobs[room]==='upload').length,pendingCount=validatedSubmissions().filter(submission=>submission.performerId===maidId&&submission.status==='pending').length,pinLeaseCount=activeRoom?1:0;
  6741 |         if(!maid)return;
  6742 |         showModal({title:`${maid.name} 비활성 영향 확인`,subtitle:'새 업무를 막기 전에 진행 중인 일과 지급 예정 금액을 확인하세요.',large:true,trigger,body:`<div class="info-grid"><div class="info-item"><span>다음 근무일 통보</span><strong>${future}건 · 완료 전 변경 통보 필요</strong></div><div class="info-item"><span>미시작·진행 중</span><strong>${currentAttempts.length}건 · 처리 방식 선택</strong></div><div class="info-item"><span>현장 완료·업로드</span><strong>${uploadCount}건 · 자료 보존</strong></div><div class="info-item"><span>검수 요청됨</span><strong>${pendingCount}건 · 새 제출은 먼저 검수</strong></div><div class="info-item"><span>미지급 청소비</span><strong>${money(currentApproved)} · 지급 이력 유지</strong></div><div class="info-item"><span>활성 PIN 조회</span><strong>${pinLeaseCount}건 · 종료 확인</strong></div></div><div class="notice notice-danger" style="margin-top:14px"><div><strong>처리 시작 즉시 잠금</strong><br>${maid.name}의 신규 업무 확인·직접 배정·새 PIN 조회를 차단합니다. 검수 요청 제출은 승인·반려를 결정하고, 반려 시 본인 무급 재청소까지 끝내야 비활성을 완료할 수 있습니다.</div></div><fieldset class="choice-list" style="margin-top:14px"><legend class="sr-only">진행 중 작업 처리 방식</legend><label class="choice"><input type="radio" name="maid-deactivation-choice" value="finish" checked><span><strong>마무리 후 비활성</strong><span>현재 작업의 전체 제출·관리자 검수 결정까지 허용</span></span></label><label class="choice"><input type="radio" name="maid-deactivation-choice" value="stop"><span><strong>즉시 중단·인계</strong><span>진행 중 청소를 중단 처리하고 새 담당에게 인계</span></span></label></fieldset>`,confirmLabel:'비활성 처리 시작',confirmAction:'confirm-start-deactivation-v2',confirmVariant:'danger'});
  6743 |         const confirm=document.querySelector('[data-action="confirm-start-deactivation-v2"]');if(confirm){confirm.disabled=isLocked();confirm.dataset.id=maidId;}
  6744 |       }
  6745 | 
  6746 |       document.addEventListener('click',event=>{const trigger=event.target.closest?.('[data-info-tip]');if(trigger){event.preventDefault();toggleInfoTip(trigger);return;}if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6747 |       document.addEventListener('focusin',event=>{if(!event.target.closest?.('.info-tip'))closeInfoTips();},true);
  6748 |       document.addEventListener('keydown',event=>{if(event.key!=='Escape'||document.querySelector('#modal-root .modal, .calendar-dialog'))return;if(closeInfoTips({restoreFocus:true})){event.preventDefault();event.stopImmediatePropagation();}},true);
  6749 | 
  6750 |       const rebuiltActions=new Set(['toggle-demo','reset','switch-role','nav','filter-rooms','filter-room-type','back','close-modal','backdrop-close','room-detail','cleaning-detail','maid-detail','complaint-detail','pay-detail','admin-pay-detail','template','template-detail','template-back-list','template-edit','template-cancel-edit','template-review','template-save','inspection-photo','open-room-export','export-rooms-csv','export-rooms-xls','open-calendar','open-pay-calendar','open-work-history-calendar','calendar-backdrop','calendar-close','calendar-month','calendar-select','calendar-today','date-shift','date-today','toggle-section','clear-room-filters','edit-room-info','save-room-info','pin-show','pin-hide','pin-edit','pin-clear','pin-random','pin-review','pin-back','pin-save','reservation-edit','new-reservation','save-reservation-v2','create-stayover','confirm-stayover','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','complete-checkout-inspection','confirm-checkout-inspection','operation-status','confirm-operation-stop','resume-operation','candle-change','task-candle-change','direct-assign','confirm-direct-assign','cleaning-tab','assignment-type-filter','admin-maid-tab','go-today','go-workforce','go-work-history','go-payroll','go-complaints','go-cleaning-drafts','go-cleaning-assignment','go-inspection','go-open','go-schedule','go-my','go-maid-pay','toggle-maid-pay-week','clear-maid-pay-week','new-cleaning','confirm-new-cleaning','toggle-week-day','submit-week-availability','edit-week-availability','request-availability-change','move-assignment-order','save-assignments','set-availability','change-availability','confirm-off-active','claim-job','confirm-claim','start-cleaning','confirm-start','capture-task-photo','choose-task-photo','remove-task-photo','remove-task-photo-item','retry-task-photo','retry-all-task-photos','field-complete-v2','submit-cleaning-v2','approve-inspection-v2','reject-inspection-v2','confirm-approve-v2','confirm-reject-v2','toggle-payment','confirm-toggle-payment','confirm-finish-payment','mark-payment-check','confirm-payment-open-v2','confirm-reverse-payment','delete-complaint','undo-complaint','publish-selected','confirm-publish','retry-network','alerts','audit-log','rates','logout','request-cancel','confirm-request-cancel','cancel-review','confirm-cancel','rule-complaint-v2','ack-complaint','object-complaint','confirm-objection','close-complaint-v2','correct-complaint-v2','confirm-correct-complaint-v2','reclean-existing','demo-info','notification-permission','confirm-notification-permission']);
  6751 |       ['quick-reservation-edit','quick-month-shift','quick-month-today','quick-reservation-undo','reservation-week-shift','open-reservation-week-calendar','reservation-add','reservation-guest-change','cancel-cleaning-target','confirm-cancel-cleaning-target','reservation-cancel-review','confirm-reservation-cancel'].forEach(action=>rebuiltActions.add(action));
  6752 |       ['random-assignments','undo-random-assignment'].forEach(action=>rebuiltActions.add(action));
  6753 |       ['resolve-conflict-v2','confirm-conflict-v2','deactivate-maid-v2','confirm-start-deactivation-v2','complete-deactivation-v2','admin-pay-week','export-rooms-xlsx','room-issue-photo','choose-room-issue-files','remove-room-issue-photo','save-room-issue','bomb-room-photo','choose-bomb-room-files','remove-bomb-room-photo','add-demo-bomb-room-photos','save-bomb-room-report','approve-bomb-room','reject-bomb-room','confirm-approve-bomb-room','confirm-reject-bomb-room'].forEach(action=>rebuiltActions.add(action));
  6754 |       const mutationActionLocks=new Set(),mutationActions=new Set(['complete-checkout-inspection','confirm-checkout-inspection','toggle-room-cleaning','confirm-room-cleaning-on','confirm-room-cleaning-off','save-reservation-v2','submit-cleaning-v2','confirm-approve-v2','confirm-reject-v2','confirm-toggle-payment','mark-payment-check','confirm-payment-open-v2','confirm-finish-payment']);
  6755 |       const deprecatedStateActions=new Set(['retry-photo','field-complete','submit-cleaning','approve-inspection','reject-inspection','confirm-approve','confirm-reject','recover-candle','confirm-candle','save-reservation','show-pin','hide-pin','resolve-conflict','confirm-conflict','deactivate-maid','confirm-deactivate','start-payment','confirm-payment','finish-payment','payment-check','payment-open','rule-complaint','confirm-ruling','close-complaint','correct-complaint','publish-template','change-availability','confirm-off-active']);
  6756 |       deprecatedStateActions.forEach(action=>rebuiltActions.add(action));
  6757 |       ['notification-filter','notification-mark-all-read','notification-toggle-push','notification-open'].forEach(action=>rebuiltActions.add(action));
  6758 | 
  6759 |       document.addEventListener('click', e => {
  6760 |         const el=e.target.closest('[data-action]');if(!el||!rebuiltActions.has(el.dataset.action))return;
  6761 |         const a=el.dataset.action,id=el.dataset.id;
  6762 |         if(a==='backdrop-close'&&e.target!==el)return;
  6763 |         if(a==='calendar-backdrop'&&e.target!==el)return;
  6764 |         e.preventDefault();e.stopImmediatePropagation();
  6765 |         const mutationKey=mutationActions.has(a)?[a,id||'',el.dataset.room||'',el.dataset.reservation||'',el.dataset.submission||'',el.dataset.week||'',el.dataset.maid||''].join(':'):'';if(mutationKey&&mutationActionLocks.has(mutationKey))return;if(mutationKey){mutationActionLocks.add(mutationKey);queueMicrotask(()=>mutationActionLocks.delete(mutationKey));}
  6766 |         if(deprecatedStateActions.has(a)){closeModal();render();toast('오래된 화면의 확정 동작은 차단했습니다. 최신 청소 상세에서 다시 진행해 주세요.','error');return;}
  6767 |         if(a==='toggle-demo'){state.demoOpen=!state.demoOpen;render();requestAnimationFrame(()=>document.querySelector('[data-action="toggle-demo"]')?.focus());return;}
  6768 |         if(a==='reset'){maskPin();releaseRoomIssuePhotoUrls();protectedPinOverrides.clear();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;state=makeScenario(state.scenario);hydrateTemplateSnapshotsForState();closeModal();render();requestAnimationFrame(()=>document.querySelector('[data-action="reset"]')?.focus());toast('시나리오를 초기 상태로 재설정했습니다.');return;}
  6769 |         if(a==='switch-role'){maskPin();pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;closeModal();rememberCurrentHistoryRoute();state.role=state.role==='admin'?'maid':'admin';state.detail=null;if(state.role==='admin'&&!adminNav.some(n=>n.id===state.adminView))state.adminView='today';if(state.role==='maid'&&!maidNav.some(n=>n.id===state.maidView))state.maidView='my';pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector('[data-action="switch-role"]')?.focus());toast(`${state.role==='admin'?'관리자':'메이드'} 화면으로 전환했습니다.`);return;}
  6770 |         if(a==='nav'){maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();state.detail=null;if(state.role==='admin')state.adminView=el.dataset.view;else state.maidView=el.dataset.view;pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.getElementById('main-content')?.focus({preventScroll:true});});return;}
  6771 |         if(a==='quick-month-shift'){
  6772 |           if(state.role!=='admin')return;rememberQuickGridViewport();state.quickReservationFollowsToday=false;state.quickReservationAnchorDate=shiftIsoDate(state.quickReservationAnchorDate,Number(el.dataset.offset)||0);state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector(`[data-action="quick-month-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6773 |         }
  6774 |         if(a==='quick-month-today'){
  6775 |           if(state.role!=='admin')return;state.quickReservationFollowsToday=true;state.quickReservationAnchorDate=DEMO_TODAY;state.quickGridScrollLeft=null;state.quickGridScrollTop=0;render();requestAnimationFrame(()=>document.querySelector('[data-action="quick-month-today"]')?.focus());return;
  6776 |         }
  6777 |         if(a==='quick-reservation-edit'){
  6778 |           if(state.role!=='admin'){toast('간편 예약 상세는 관리자만 볼 수 있습니다.','error');return;}
  6779 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active');if(!reservation){toast('예약이 취소되었거나 최신 목록에 없습니다.','error');return;}rememberQuickGridViewport();openReservation(reservation.room,reservation.id,{weekStart:el.dataset.week||''});return;
  6780 |         }
  6781 |         if(a==='reservation-week-shift'){
  6782 |           if(state.role!=='admin')return;const room=el.dataset.room||state.reservationWeekRoom||'211',nextStart=shiftIsoDate(weekStartIso(state.reservationWeekStart||state.selectedDate),7*Number(el.dataset.offset||0));
  6783 |           openReservation(room,'',{weekStart:nextStart});requestAnimationFrame(()=>document.querySelector(`[data-action="reservation-week-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;
  6784 |         }
  6785 |         if(a==='open-reservation-week-calendar'){
  6786 |           if(state.role!=='admin')return;state.reservationWeekRoom=el.dataset.room||state.reservationWeekRoom||'211';state.calendarMonth=weekStartIso(state.reservationWeekStart||state.selectedDate).slice(0,7);openCalendar(el,'reservation-week',true);return;
  6787 |         }
  6788 |         if(a==='reservation-add'){
  6789 |           const room=ROOMS.find(item=>item.no===String(el.dataset.room||'')),newDate=el.dataset.date||suggestedReservationStartDate(room?.no||'');
  6790 |           if(state.role!=='admin'||!adminCanMutate()||!room){toast('관리자 최신 상태에서만 다음 예약을 등록할 수 있습니다.','error');return;}
  6791 |           const block=reservationHardBlockReason(room);if(block){toast(`${room.no}호는 ${block} 상태라 다음 예약을 등록할 수 없습니다.`,'error');return;}
  6792 |           if(room.occupancy==='occupied'&&!occupiedReservationEnd(room)){toast('현재 투숙의 체크아웃을 먼저 입력해 주세요.','error');return;}
  6793 |           if(occupiedStayNeedsCheckoutUpdate(room)){toast('예정 체크아웃이 지났습니다. 예약 관리에서 체크아웃 시각을 갱신해 주세요.','error');return;}
  6794 |           openReservation(room.no,'__new__',{weekStart:weekStartIso(newDate),newDate,historyStack:true,trigger:el});return;
  6795 |         }
  6796 |         if(a==='reservation-cancel-review'){openReservationCancellationReview(id,el.dataset.fingerprint||'',el);return;}
  6797 |         if(a==='confirm-reservation-cancel'){
  6798 |           const reasonCode=document.getElementById('reservation-cancel-reason')?.value||'',reasonError=reservationCancelReasonError(reasonCode);if(reasonError){toast(reasonError,'error');document.getElementById('reservation-cancel-reason')?.focus();return;}
  6799 |           const result=cancelReservationRecord({reservationId:id,expectedFingerprint:el.dataset.fingerprint||'',expectedImpactFingerprint:el.dataset.impact||'',reasonCode});
  6800 |           if(result.error){closeModal();render();toast(result.error,'error');return;}
  6801 |           const room=result.reservation.room,firstNight=result.reservation.checkInAt.slice(0,10),remaining=activeReservationsFor(state,room),pivot=`${state.selectedDate}T00:00`,cardReservation=remaining.find(item=>item.checkOutAt>pivot)||remaining[0]||null;
  6802 |           historyReturnFocus=state.adminView==='quickReservation'?{quickCell:true,room,date:firstNight}:state.detail?.type==='room'?{action:'reservation-edit',id:room}:cardReservation?{action:'quick-reservation-edit',id:cardReservation.id,room}:{action:'reservation-edit',id:room};
  6803 |           closeModal();render();if(state.adminView==='quickReservation')restoreQuickGridViewport(`[data-quick-cell][data-room="${room}"][data-date="${firstNight}"]`);toast(`${room}호 ${reservationNights(result.reservation)}박 예약을 취소했습니다.`);return;
  6804 |         }
  6805 |         if(a==='quick-reservation-undo'){
  6806 |           if(!adminCanMutate()||state.quickLastCreated?.reservationId!==id||Date.now()-Number(state.quickLastCreated?.createdAt)>10500){toast('실행 취소 시간이 지났거나 최신 상태가 바뀌었습니다.','error');return;}
  6807 |           const reservation=state.reservations.find(item=>item.id===id&&item.status==='active'),room=state.quickLastCreated.room,firstNight=reservation?.checkInAt.slice(0,10);if(removeQuickReservation(id,{undo:true})){state.quickLastCreated=null;render();restoreQuickGridViewport(`[data-room="${room}"][data-date="${firstNight}"]`);toast(`${room}호 예약 접수를 되돌렸습니다.`);}else toast('청소 배정 또는 예약 상태가 바뀌어 방금 접수 실행 취소를 중단했습니다.','error');return;
  6808 |         }
  6809 |         if(a==='filter-rooms'){
  6810 |           const filter=el.dataset.filter;
  6811 |           if(state.role!=='admin'||!['occupied','cleaning','available','blocked','checkout-inspection'].includes(filter))return;
  6812 |           maskPin();pendingPin=null;pendingTemplateChange=null;closeModal();rememberCurrentHistoryRoute();
  6813 |           state.detail=null;state.adminView='rooms';state.roomSearch='';state.roomTypeFilter='all';state.roomFilter=filter;
  6814 |           pushHistoryOnNextRender();render();requestAnimationFrame(()=>{window.scrollTo(0,0);document.querySelector('[data-control="room-filter"]')?.focus({preventScroll:true});});return;
  6815 |         }
  6816 |         if(a==='filter-room-type'){
  6817 |           const typeId=el.dataset.type;if(state.role!=='admin'||state.adminView!=='rooms'||!(typeId==='all'||ROOM_TYPES[typeId]))return;
  6818 |           state.roomTypeFilter=typeId;state.roomFilter='all';state.roomSearch='';render();requestAnimationFrame(()=>document.querySelector(`[data-action="filter-room-type"][data-type="${typeId}"]`)?.focus({preventScroll:true}));return;
  6819 |         }
  6820 |         if(a==='back'){maskPin();backFromDetail();return;}
  6821 |         if(a==='close-modal'||a==='backdrop-close'||a==='calendar-close'||a==='calendar-backdrop'){pendingPin=null;pendingTemplateChange=null;pendingDraftPublish=null;dismissModal();return;}
  6822 |         if(a==='room-detail'){maskPin();if(state.adminView==='quickReservation'&&!state.detail)rememberQuickGridViewport();openDetail('room',id||'350',el);return;}
  6823 |         if(a==='cleaning-detail'){maskPin();openDetail('cleaning',id||'639',el);return;}
  6824 |         if(a==='maid-detail'){maskPin();openDetail('maid',id||'m1',el);return;}
  6825 |         if(a==='resolve-conflict-v2'){if(!adminCanMutate()){toast('관리자 최신 상태에서만 충돌을 해결할 수 있습니다.','error');return;}if(activeRecleanAttempt('332')){toast('332호 본인 무급 재청소가 끝난 뒤 충돌 재계획을 진행할 수 있습니다.','error');return;}openConflictResolutionV2(el);return;}
  6826 |         if(a==='confirm-conflict-v2'){
  6827 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 충돌을 종결하지 않았습니다.','error');return;}
  6828 |           if(activeRecleanAttempt('332')){closeModal();render();toast('332호 본인 무급 재청소를 유지하기 위해 충돌 재계획을 적용하지 않았습니다.','error');return;}
  6829 |           const previousAttemptId=currentAttemptId('332'),previousAttempt=previousAttemptId?state.cleaningAttempts?.[previousAttemptId]:null;
  6830 |           if(state.conflict!=='active'||state.jobs['332']!=='cleaning'||previousAttempt?.status!=='cleaning'||previousAttempt.room!=='332') { closeModal();render();toast('332호 충돌 또는 수행 회차가 바뀌어 재계획을 적용하지 않았습니다.','error');return; }
  6831 |           if(!Object.values(state.conflictSteps).every(Boolean)){toast('현장 조율·작업 재계획·필요 PIN 교체를 모두 확인해야 합니다.','error');return;}
  6832 |           if(activeCleaningFor(previousAttempt.performerId)==='332')setActiveCleaningFor(previousAttempt.performerId,null);
  6833 |           const previousWorkDate=attemptWorkDate(previousAttempt,state.selectedDate),previousWorkTargetId=previousAttempt.workTargetId||assignmentHistoryTargetId('332',previousAttempt.kind,previousWorkDate),replannedAttempt=beginCleaningAttempt('332',{performerId:previousAttempt.performerId,performerName:previousAttempt.performerName,reason:'점유 재개 충돌 뒤 동일 수행자 새 일정 재계획',baseRateSnapshot:previousAttempt.baseRateSnapshot,kind:previousAttempt.kind,workDate:previousWorkDate,workTargetId:previousWorkTargetId,templateSnapshot:previousAttempt.templateSnapshot||templateSnapshotFor('332',previousAttempt.kind),accessStart:previousAttempt.accessStart,requestDue:previousAttempt.requestDue,accessEnd:previousAttempt.accessEnd,reservationIdSnapshot:previousAttempt.reservationIdSnapshot,guestCountSnapshot:previousAttempt.guestCountSnapshot});
  6834 |           state.conflict='resolved';state.conflictRecord.resolvedAt=state.time;state.jobs['332']='scheduled';
  6835 |           appendEvent('332호 점유 재개·출입 충돌 종결',`${state.conflictRecord.autoCheckoutAt} 자동 체크아웃 보존 · ${state.conflictRecord.afterCheckout} 점유 보정 · ${previousAttempt.performerName} ${previousAttempt.id} 중단 보존 → ${replannedAttempt.id} 재계획 · ${state.conflictRecord.leaseId} 종료`,{maidIds:[previousAttempt.performerId]});
  6836 |           closeModal();render();toast('충돌을 종결하고 점유·청소·PIN lease 상태를 재계산했습니다.');return;
  6837 |         }
  6838 |         if(a==='deactivate-maid-v2'){
  6839 |           const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
  6840 |           if(!maid){toast('메이드 계정을 찾을 수 없습니다.','error');return;}
  6841 |           if(!adminCanMutate()){toast('관리자 최신 상태에서만 비활성 처리를 시작할 수 있습니다.','error');return;}
  6842 |           if(maidStatusFor(maidId)!=='active'){toast(`${maid.name} 계정은 이미 ${maidDeactivationLabel(maidId)} 상태입니다.`,'error');return;}
  6843 |           if(reclean||pending||conflict){toast(reclean?`${reclean.room}호 본인 무급 재청소를 완료한 뒤 비활성 처리할 수 있습니다.`:pending?`${pending.room}호 검수 결정을 완료한 뒤 비활성 처리를 시작할 수 있습니다.`:`${conflict.room}호 출입·청소 충돌을 종결한 뒤 비활성 처리를 시작할 수 있습니다.`,'error');return;}
  6844 |           openMaidDeactivationV2(maidId,el);return;
  6845 |         }
  6846 |         if(a==='confirm-start-deactivation-v2'){
  6847 |           const maidId=id||el.dataset.id,maid=maidById(maidId),reclean=unresolvedRecleanForMaid(maidId),pending=pendingInspectionForMaid(maidId),conflict=unresolvedCleaningConflictForMaid(maidId);
  6848 |           if(!maid||!adminCanMutate()||maidStatusFor(maidId)!=='active'||reclean||pending||conflict){closeModal();render();toast(reclean?`${reclean.room}호 본인 무급 재청소가 남아 비활성 처리를 시작하지 않았습니다.`:pending?`${pending.room}호 검수 결정이 남아 비활성 처리를 시작하지 않았습니다.`:conflict?`${conflict.room}호 출입 충돌이 남아 비활성 처리를 시작하지 않았습니다.`:'메이드 계정 상태·관리자 권한 또는 최신 상태가 바뀌어 비활성 처리를 시작하지 않았습니다.','error');return;}
  6849 |           const choice=document.querySelector('input[name="maid-deactivation-choice"]:checked')?.value||'finish',activeRoom=activeCleaningFor(maidId),activeAttempt=activeRoom?state.cleaningAttempts?.[currentAttemptId(activeRoom)]:null,ownsActive=activeAttempt?.room===activeRoom&&activeAttempt.performerId===maidId&&activeAttempt.kind!=='재청소',flow={choice,activeRoom:ownsActive?activeRoom:null,gates:{assignments:false,round:false,lease:false},startedAt:state.time,completedAt:null};
  6850 |           setMaidStatusFor(maidId,'deactivating');setMaidDeactivationFor(maidId,flow);if(maidId==='m1')state.handoff=choice;
  6851 |           if(choice==='stop'&&ownsActive){setActiveCleaningFor(maidId,null);if(state.jobs[activeRoom]==='cleaning'){state.jobs[activeRoom]='unassigned';const room=ROOMS.find(item=>item.no===activeRoom);if(room)room.assignee='미정';}}
  6852 |           appendEvent(`${maid.name} 비활성 처리 시작`,choice==='stop'?'즉시 중단·인계 · 신규 업무/배정/PIN 잠금':'현재 작업 마무리 후 비활성 · 신규 업무/배정/PIN 잠금',{maidIds:[maidId]});
```

## 예약 렌더: `renderReservation`

matches: 0

## 객실 상세: `openRoom`

matches: 6

### occurrence 1 · line 6047

```html
  6002 |       }
  6003 |       function releaseRoomIssuePhoto(photo) {
  6004 |         if(photo?.objectUrl&&photo.src)URL.revokeObjectURL(photo.src);
  6005 |       }
  6006 |       function releaseRoomIssuePhotoUrls(snapshot=state) {
  6007 |         const urls=new Set(),collect=photo=>{if(photo?.objectUrl&&photo.src)urls.add(photo.src);};
  6008 |         Object.values(snapshot?.taskInputs||{}).forEach(task=>{
  6009 |           task.issueDraft?.photos?.forEach(collect);
  6010 |           task.bombRoomDraft?.photos?.forEach(collect);
  6011 |           task.uploads?.forEach(upload=>uploadPhotoEntries(upload).forEach(item=>collect(item.image)));
  6012 |         });
  6013 |         Object.values(snapshot?.cleaningSubmissions||{}).forEach(submission=>submission.uploads?.forEach(upload=>uploadPhotoEntries(upload).forEach(item=>collect(item.image))));
  6014 |         Object.values(snapshot?.roomIssues||{}).flat().forEach(record=>record.photos?.forEach(collect));
  6015 |         Object.values(snapshot?.bombRoomReports||{}).forEach(report=>report.photos?.forEach(collect));
  6016 |         urls.forEach(url=>URL.revokeObjectURL(url));
  6017 |       }
  6018 |       function photoViewerConfig(payload) {
  6019 |         const no=String(payload?.room||''),room=ROOMS.find(item=>item.no===no);
  6020 |         if(!room)return null;
  6021 |         if(payload?.source==='inspection'){
  6022 |           const rawSubmission=state.cleaningSubmissions?.[payload?.recordId]||null,submission=validatedSubmission(rawSubmission)||rawSubmission;
  6023 |           let parent=null,photo=null,index=-1;
  6024 |           for(const upload of submission?.uploads||[]){
  6025 |             if(upload.id===payload.photoId&&upload.image){parent=upload;photo={id:upload.id,status:upload.status,image:upload.image};index=0;break;}
  6026 |             const itemIndex=uploadPhotoCollection(upload).findIndex(item=>item.id===payload.photoId);
  6027 |             if(itemIndex>=0){parent=upload;photo=upload.images[itemIndex];index=itemIndex;break;}
  6028 |           }
  6029 |           if(!rawSubmission||state.cleaningSubmissions?.[rawSubmission.id]!==rawSubmission||submission.room!==no||!parent||!photo?.image||state.role!=='admin'&&submission.performerId!==signedInMaidId())return null;
  6030 |           const upload={...parent,id:photo.id,status:photo.status,image:photo.image,label:uploadUsesPhotoCollection(parent)?`${parent.label} ${index+1}`:parent.label},captured=!!upload.image?.objectUrl,collectionLabel=uploadUsesPhotoCollection(parent)?`${index+1}/${uploadPhotoCount(parent)}번째 · 최대 ${photoUploadLimit(parent)}장`:'사진 1장';
  6031 |           return {title:`${no}호 · ${upload.label}`,subtitle:captured?'메이드가 전체 제출에 포함한 현장 촬영 이미지':'메이드가 전체 제출에 포함한 데모 이미지',large:true,body:`<div class="photo-viewer-visual">${inspectionPhotoSvg(upload,`${no}호 ${upload.label}`)}</div><div class="photo-meta"><div class="info-item"><span>구분</span><strong>${esc(collectionLabel)}</strong></div><div class="info-item"><span>촬영</span><strong>${esc(upload.image?.uploadedAt||'시각 없음')}</strong></div><div class="info-item"><span>제출 버전</span><strong>${esc(upload.image?.version||'현장 촬영')} · ${upload.status==='failed'?'검증 실패':'검증 완료'}</strong></div></div><p class="audit-note" style="margin:12px 0 0">확대 보기는 검수 참고용이며 사진별 승인·반려는 제공하지 않습니다. 사진 원문과 파일명은 URL·브라우저 이력에 저장하지 않습니다.</p>`};
  6032 |         }
  6033 |         if(payload?.source==='bomb-room'){
  6034 |           const linkedSubmission=Object.values(state.cleaningSubmissions||{}).find(item=>item.room===no&&item.reportId===payload?.recordId)||null,report=linkedSubmission?rawBombRoomReportForSubmission(linkedSubmission):state.bombRoomReports?.[payload?.recordId]||bombRoomReport(no),photo=report?.photos?.find(item=>item.id===payload.photoId),meta=bombRoomStatusMeta(report),submission=linkedSubmission||(report?.submissionId?state.cleaningSubmissions?.[report.submissionId]||null:null);
  6035 |           if(!report||report.room!==no||!photo||state.role!=='admin'&&report.reportedById!==signedInMaidId()&&submission?.performerId!==signedInMaidId())return null;
  6036 |           const decision=report.attemptStatus==='superseded'?`회차 종료 · ${esc(report.supersededAt||'시각 없음')} · ${esc(report.supersededReason||'담당 변경')}`:report.status==='pending'?'관리자 결정 대기':`${esc(report.decidedAt||'결정 시각 없음')} · ${esc(report.decisionReason|| (report.status==='approved'?'폭탄방 인정':'일반 청소 범위'))}`;
  6037 |           return {title:`${no}호 · 폭탄방 증빙`,subtitle:`${report.reportedBy} 신고 · ${meta.label} · 데모 메모리 이미지`,large:true,body:`<div class="photo-viewer-visual">${roomIssuePhotoVisual(photo,`${no}호 폭탄방 증빙 이미지`)}</div><div class="photo-meta"><div class="info-item"><span>신고자</span><strong>${esc(report.reportedBy)}</strong></div><div class="info-item"><span>신고 시각</span><strong>${esc(report.reportedAt)}</strong></div><div class="info-item"><span>검수 상태</span><strong>${esc(meta.label)}</strong></div><div class="info-item"><span>관리자 결정·회차</span><strong>${decision}</strong></div></div>${report.note?`<div class="notice notice-info" style="margin-top:12px"><div><strong>신고 메모</strong><br>${esc(report.note)}</div></div>`:''}<p class="audit-note" style="margin:12px 0 0">사진 파일명과 원본은 URL·알림·감사 이력·브라우저 영속 저장소에 남기지 않습니다.</p>`};
  6038 |         }
  6039 |         const linkedSubmission=Object.values(state.cleaningSubmissions||{}).find(item=>item.room===no&&item.roomIssuesSnapshot?.some(record=>record.id===payload?.recordId))||null,snapshotRecord=linkedSubmission?.roomIssuesSnapshot?.find(item=>item.id===payload?.recordId)||null,record=snapshotRecord||roomIssueRecords(no).find(item=>item.id===payload?.recordId),photo=record?.photos?.find(item=>item.id===payload?.photoId);
  6040 |         if(!record||!photo||state.role!=='admin'&&record.createdById!==signedInMaidId()&&linkedSubmission?.performerId!==signedInMaidId())return null;
  6041 |         return {title:`${no}호 · ${record.type||'객실 특이사항'}`,subtitle:`${record.createdBy} 등록 · 관리자 조회 가능 · 데모 메모리 이미지`,large:true,body:`<div class="photo-viewer-visual">${roomIssuePhotoVisual(photo,`${no}호 ${record.type} 특이사항 이미지`)}</div><div class="photo-meta"><div class="info-item"><span>등록자</span><strong>${esc(record.createdBy)}</strong></div><div class="info-item"><span>등록 시각</span><strong>${esc(record.createdAt)}</strong></div><div class="info-item"><span>보존 상태</span><strong>현재 탭 메모리 · 데모</strong></div></div><p class="audit-note" style="margin:12px 0 0">사진 파일명과 원본은 URL·알림·감사 이력·브라우저 영속 저장소에 남기지 않습니다.</p>`};
  6042 |       }
  6043 |       function photoViewerModalMarkup(payload) {
  6044 |         const config=photoViewerConfig(payload);
  6045 |         return config?standardModalMarkup(config):'';
  6046 |       }
  6047 |       function openRoomIssuePhoto(no,issueId,photoId,trigger=document.activeElement) {
  6048 |         const payload={source:'room-issue',room:no,recordId:issueId,photoId},config=photoViewerConfig(payload);
  6049 |         if(!config){toast('이 사진을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6050 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6051 |       }
  6052 |       function openBombRoomPhoto(no,reportId,photoId,trigger=document.activeElement) {
  6053 |         const payload={source:'bomb-room',room:no,recordId:reportId,photoId},config=photoViewerConfig(payload);
  6054 |         if(!config){toast('이 폭탄방 증빙을 볼 권한이 없거나 기록을 찾을 수 없습니다.','error');return;}
  6055 |         showModal({...config,trigger,historyKind:'photo-viewer',historyPayload:payload});
  6056 |       }
  6057 |       function renderAvailabilityCard() {
  6058 |         const saved=state.weeklyAvailability?.[signedInMaidId()]?.days||[],hasCommitted=state.availabilitySubmitted||state.availabilityChangeRequested,selected=hasCommitted?saved:state.availabilityDraft||[],statusLabel=state.availabilityChangeRequested?'다음 주 변경 요청':state.availabilitySubmitted?'다음 주 제출 완료':'다음 주 미제출';
  6059 |         return `<section class="card availability-card"><div class="availability-result">${statusBadge(statusLabel,state.availabilitySubmitted?'green':'amber')}<div><strong>8월 17일–23일 · 가능 ${selected.length}일</strong><span>${availabilitySubmissionWindowLabel()} 제출 · 객실 담당은 관리자만 배정</span></div>${button('근무 일정 열기','go-schedule','outline')}</div></section>`;
  6060 |       }
  6061 |       function renderMaidSchedule() {
  6062 |         const maidId=signedInMaidId(),accountActive=signedInMaidIsActive(),dayNames=[['월','17'],['화','18'],['수','19'],['목','20'],['금','21'],['토','22'],['일','23']],phase=availabilitySubmissionPhase(),submitted=state.availabilitySubmitted,editing=!!state.availabilityEditing&&phase==='open',savedSelected=state.weeklyAvailability?.[maidId]?.days||[],selected=editing||!submitted?state.availabilityDraft||[]:savedSelected,availableCount=selected.length;
  6063 |         const assigned=notifiedAssignmentEntriesForMaid(maidId);
  6064 |         const assignedCards=assigned.length?assigned.map(({item})=>{const guestCount=assignmentGuestCount(item);return `<div class="assigned-preview-grid"><div><span>근무일</span><strong>${esc(dateLabel(targetEffectiveDate(item)))}</strong></div><div><span>객실</span><strong>${item.room}호</strong></div><div><span>업무</span><strong>${esc(item.kind)}</strong></div>${guestCount?`<div><span>숙박 인원</span><strong>${esc(guestCountLabel(guestCount))}</strong></div>`:`<div><span>예약 연결</span><strong>없음</strong></div>`}<div><span>시작 가능</span><strong>${item.checkout} 이후</strong></div>${item.carryReason?`<div><span>이월</span><strong>원 계획 ${esc(dateLabel(targetPlanDate(item)))}</strong></div>`:''}</div>`;}).join(''):`<div class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 근무일 전날 밤 객실 담당을 확정하면 여기에 표시됩니다.</p></div>`;
  6065 |         const submissionWindow=availabilitySubmissionWindowLabel(),phaseText=!accountActive?'비활성 계정 · 과거 제출 읽기 전용':phase==='before'?`${submissionWindow} 제출 가능`:phase==='open'?`${submissionWindow} · 지금 제출 가능`:`${submissionWindow} 마감 · 변경은 관리자 확인 필요`;
  6066 |         const editorLocked=!accountActive||submitted&&!editing||state.availabilityChangeRequested||phase!=='open'||isLocked();
  6067 |         let actionMarkup='';
  6068 |         if(!accountActive)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>가능일 수정 잠금</strong><br>비활성 처리 중이거나 비활성인 계정은 과거 제출만 조회할 수 있습니다.</div></div>';
  6069 |         else if(state.availabilityChangeRequested)actionMarkup='<div class="notice notice-warning" style="margin:0"><div><strong>관리자 확인 요청됨</strong><br>기존 제출은 유지되고 변경 요청이 관리자 알림에 남았습니다.</div></div>';
  6070 |         else if(editing)actionMarkup=button('수정 내용 다시 제출','submit-week-availability','primary',isLocked()?'disabled':'');
  6071 |         else if(submitted&&phase==='open')actionMarkup=button('제출 내용 수정','edit-week-availability','primary',isLocked()?'disabled':'');
  6072 |         else if(submitted&&phase==='closed')actionMarkup=button('가능일 변경 요청','request-availability-change','outline',isLocked()?'disabled':'');
  6073 |         else if(submitted)actionMarkup=button('제출 기간 아님','edit-week-availability','outline','disabled');
  6074 |         else actionMarkup=button(phase==='open'?'다음 주 가능일 제출':phase==='before'?`${submissionWindow} 제출`:'제출 마감','submit-week-availability','primary',phase==='open'&&!isLocked()?'':'disabled');
  6075 |         return renderCoach()+renderNetworkNotice()+`<div class="weekly-availability"><section class="card week-card"><div class="week-card-head"><div><h2>8월 17일 (월)–8월 23일 (일)</h2><p>다음 주에 근무 가능한 요일을 모두 선택해 주세요.</p></div>${statusBadge(state.availabilityChangeRequested?'변경 요청':editing?'수정 중':submitted?'제출 완료':'미제출',state.availabilityChangeRequested||editing?'amber':submitted?'green':'amber')}</div><div class="deadline-bar">${icon('clock','icon-sm')}<span>${phaseText}</span></div><div class="week-days" aria-label="다음 주 근무 가능일">${dayNames.map((day,index)=>{const active=selected.includes(index);return `<button class="week-day" type="button" data-action="toggle-week-day" data-day="${index}" aria-pressed="${active}" ${editorLocked?'disabled':''}><strong>${day[0]} ${day[1]}</strong><span>${active?'근무 가능':'근무 불가'}</span><i class="week-toggle" aria-hidden="true"></i></button>`;}).join('')}</div><div class="week-total">${icon('calendar','icon-sm')}가능 ${availableCount}일 · 불가 ${7-availableCount}일</div><div class="week-submit-actions">${actionMarkup}</div><div class="assignment-notice">${icon('user')}<p>관리자가 각 근무일 전날 밤 객실을 직접 배정합니다. 메이드는 객실을 선택하거나 다른 메이드에게 배정할 수 없습니다.</p></div></section><section class="card assigned-preview"><div class="section-head"><div><h2>배정된 내 업무</h2><span class="meta">관리자 통보 완료 건만 표시</span></div>${statusBadge(`${assigned.length}건`,'blue')}</div>${assignedCards}<p class="audit-note" style="margin:10px 0 0">배정이 바뀌면 기존 담당 구간은 이력으로 남고 알림에서 변경 내용을 확인할 수 있습니다.</p></section></div>`;
  6076 |       }
  6077 |       function publicJobCard(no) {
  6078 |         const room=ROOMS.find(r=>r.no===no), type=ROOM_TYPES[room?.type||'standard'];
  6079 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${esc(cleaningLabel(state.jobs[no]))}</h3><p>${esc(type.name)}</p></div>${statusBadge('관리자 배정','green')}</div><div class="schedule-line">${icon('clock','icon-sm')}<span>시작 가능 ${startTimeFor(no)} · 담당 ${esc(room?.assignee||'미정')}</span></div><div class="notice notice-info" style="margin:0">메이드는 관리자에게 통보받은 업무만 확인하고 수행할 수 있습니다.</div></article>`;
  6080 |       }
  6081 |       function renderMaidOpen() {
  6082 |         return renderMaidSchedule();
  6083 |       }
  6084 |       function myJobCard(no) {
  6085 |         const job=state.jobs[no], room=ROOMS.find(r=>r.no===no),attempt=state.cleaningAttempts?.[currentAttemptId(no)],access=attemptAccessStatus(no,attempt),start=access.start,reached=access.allowed,rollover=rolloverMetaForRoom(no);
  6086 |         const guestCount=guestCountForAttempt(attempt),guestCountDisplay=guestCount?guestCountLabel(guestCount):'미기록',reclean=attempt?.kind==='재청소'?{reason:attempt.reason||'전체 반려 뒤 본인 재청소',previousMaid:currentSubmission(no)?.performerName||room?.assignee||'기존 메이드',originalKind:currentSubmission(no)?.kind||'퇴실 청소'}:null;
  6087 |         const labels={scheduled:reached?'일 시작':'시작 시각 대기',claimed:reached?'일 시작':'시작 시각 대기',cleaning:'계속 청소',upload:taskState(no).uploads.some(u=>u.status==='failed')?'미전송 재시도':'청소 전체 제출',inspection:'제출 결과 보기',approved:'완료 결과 보기',reclean:reached?'재청소 시작':'시작 시각 대기'};
  6088 |         const action='cleaning-detail';
  6089 |         const bomb=bombRoomReport(no),bombMeta=bombRoomStatusMeta(bomb),tone=job==='approved'?'green':job==='cleaning'||job==='upload'?'amber':job==='inspection'?'blue':'neutral';
  6090 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title"><h3>${no}호 · ${reclean?'재청소':cleaningLabel(job)}</h3><p>${esc(ROOM_TYPES[room?.type||'standard'].name)}</p></div><div class="badge-row">${statusBadge(statusLabel(job),tone)}${bomb?statusBadge(bombMeta.label,bombMeta.tone):''}</div></div>${rolloverBadgeMarkup(rollover,{compact:true})}<div class="schedule-line">${icon('clock','icon-sm')}<span>${job==='upload'?'현장 완료 · 사진 전송·전체 제출 필요':job==='cleaning'&&rollover?'계속 청소 가능':`시작 가능 ${start} · ${reached?'지금 시작 가능':esc(access.reason)}`}</span></div><div class="schedule-line">${icon('user','icon-sm')}<span>숙박 인원 ${guestCountDisplay}</span></div>${reclean?`<div class="job-meta"><div><span>재청소 요금</span><strong>0원 · 무급</strong></div><div><span>원 작업</span><strong>${no}호 ${esc(reclean.originalKind)}</strong></div></div><div class="notice notice-warning" style="margin:0"><div>처음 청소한 ${esc(reclean.previousMaid)} 본인에게 자동 배정 · 다른 메이드에게 넘길 수 없음 · ${esc(reclean.reason)}</div></div>`:''}<button class="btn ${job==='upload'&&taskState(no).uploads.some(u=>u.status==='failed')?'btn-danger':'btn-primary'} btn-block" type="button" data-action="${action}" data-id="${no}">${labels[job]||'상세 보기'}</button></article>`;
  6091 |       }
  6092 |       function renderMaidMy() {
  6093 |         const maidId=signedInMaidId(),maidName=signedInMaidName(),activeCleaning=activeCleaningFor(maidId),own=Object.entries(state.jobs).filter(([no,v])=>['scheduled','claimed','cleaning','upload','inspection','approved','reclean'].includes(v)&&(ROOMS.find(r=>r.no===no)?.assignee===maidName||(['inspection','approved'].includes(v)&&currentSubmission(no)?.performerId===maidId))).map(([no])=>no);
  6094 |         const upcoming=notifiedAssignmentEntriesForMaid(maidId);
  6095 |         const upcomingNotice=upcoming.length?`<div class="assignment-notice">${icon('bell')}<div><p><strong>통보된 청소 일정 ${upcoming.length}건</strong><br>오늘·내일 날짜와 관리자가 확정한 순서입니다.</p><ol class="maid-assignment-route">${upcoming.map(({item,assignment})=>`<li><b>${assignment.order}</b><span>${esc(dateLabel(targetEffectiveDate(item)))} · ${item.room}호 · ${esc(item.kind)} · ${esc(assignmentScheduleText(item))}${assignment.activationBlockedBy?' · 관리자 확인 대기':''}</span></li>`).join('')}</ol></div></div>`:'';
  6096 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack">${upcomingNotice}<section class="card work-hero"><span>${esc(maidName)} 현재 작업 상태</span><strong>${activeCleaning?`${activeCleaning}호 청소 중`:'청소 중 없음'}</strong><p>관리자에게 배정·통보된 업무만 표시합니다. 동시에 청소 중 한 건만 가능합니다.</p></section><div class="mobile-section-title"><div><h2>내 업무 ${own.length}건</h2><p>담당 확정부터 검수 결과까지 이어집니다.</p></div></div>${renderListState(own.length?`<div class="job-list">${own.map(myJobCard).join('')}</div>`:`<section class="inline-empty"><h3>배정된 업무가 없습니다</h3><p>관리자가 오늘·내일 배정을 통보하면 내 업무와 알림에 표시됩니다.</p>${button('근무 가능일 확인','go-schedule','primary')}</section>`)}</div>`;
  6097 |       }
  6098 |       function renderMaidAlerts(){
  6099 |         const key=notificationAudienceKey('maid',signedInMaidId());ensureNotificationState();return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><section><div class="section-head"><div><h2>알림</h2><p class="audit-note">배정·검수 결과·취소·마감·주급 업데이트를 시간순으로 확인합니다.</p></div>${statusBadge(`안 읽음 ${notificationUnreadCount(key)}건`,notificationUnreadCount(key)?'blue':'neutral')}</div><div class="tab-panel">${renderNotificationListMarkup({key,filter:state.notificationFilter,includeActivity:true})}</div></section></div>`;
  6100 |       }
  6101 | 
  6102 |       function renderMaidPay() {
  6103 |         return renderMaidPayFromLedger();
  6104 |         const paid=paymentStatusFor('2026-08-03',signedInMaidId())==='PAID',currentMaid=signedInMaid();
  6105 |         const currentWeekStart='2026-08-10',currentMaidId=currentMaid.id,submissionDate=submission=>{const match=String(submission?.submittedAt||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);return match?`${Number(match[1])}월 ${Number(match[2])}일`:'이번 주';},taskKind=(room,record)=>record?.kind||(room==='142'?'연박 청소':'퇴실 청소'),roundLabel=id=>id?String(id).split('-').slice(-2).join('-'):'';
  6106 |         const baselineTasksByMaid={
  6107 |           m1:[{room:'352호',kind:'퇴실 청소',date:'8월 14일',amount:16000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 13일',amount:16000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 11일',amount:20000,status:'승인 확정',tone:'green'}],
  6108 |           m2:[{room:'142호',kind:'연박 청소',date:'8월 14일',amount:30000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 12일',amount:20000,status:'승인 확정',tone:'green'},{room:'350호',kind:'퇴실 청소',date:'8월 10일',amount:16000,status:'승인 확정',tone:'green'}],
  6109 |           m3:[{room:'142호',kind:'연박 청소',date:'8월 15일',amount:30000,status:'승인 확정',tone:'green'},{room:'639호',kind:'퇴실 청소',date:'8월 13일',amount:20000,status:'승인 확정',tone:'green'},{room:'332호',kind:'퇴실 청소',date:'8월 10일',amount:20000,status:'승인 확정',tone:'green'}]
  6110 |         },baselineTasks=baselineTasksByMaid[currentMaidId]||[],baselineConfirmed=baselineTasks.reduce((sum,task)=>sum+task.amount,0);
  6111 |         const currentEarningTasks=validatedEarningRecords().filter(record=>record.weekStart===currentWeekStart&&record.performerId===currentMaidId).sort((a,b)=>String(b.creditedAt).localeCompare(String(a.creditedAt))).map(record=>{const submission=validatedSubmission(state.cleaningSubmissions?.[record.submissionId]||null),report=bombRoomReportForSubmission(submission);return {room:`${record.room}호`,roomNo:record.room,kind:taskKind(record.room,submission),date:submissionDate(submission),amount:record.total,status:record.bombBonus?'폭탄방 승인 · ×2':report?.status==='rejected'?'폭탄방 미인정 · 승인 확정':'승인 확정',tone:'green',baseAmount:record.base,bombBonus:record.bombBonus,bombStatus:report?.status||'none',reportId:report?.id||null,photoId:report?.photos?.[0]?.id||null,submissionId:record.submissionId,roundLabel:roundLabel(record.submissionId)};});
  6112 |         const isUnpaidRecleanSubmission=submission=>submission?.kind==='재청소';
  6113 |         const currentUnsettledTasks=validatedSubmissions().filter(submission=>submission.weekStart===currentWeekStart&&submission.performerId===currentMaidId&&!earningRecordForSubmission(submission)&&(['pending','rejected'].includes(submission.status)||(submission.status==='approved'&&isUnpaidRecleanSubmission(submission)))).sort((a,b)=>String(b.submittedAt).localeCompare(String(a.submittedAt))).map(submission=>{
  6114 |           const report=bombRoomReportForSubmission(submission),wholeRejected=submission.status==='rejected',unpaidReclean=isUnpaidRecleanSubmission(submission),unpaidApproved=unpaidReclean&&submission.status==='approved',fee=bombRoomBreakdown(submission.room,{pendingAsBonus:!wholeRejected&&!unpaidReclean&&report?.status==='pending',reportOverride:report,baseOverride:submission.baseRateSnapshot});
  6115 |           const rejectedDecision=report?.status==='approved'?'폭탄방 승인 결정':report?.status==='rejected'?'폭탄방 미인정 결정':'폭탄방 신고 없음',status=wholeRejected?`청소 전체 반려 · ${rejectedDecision} 보존`:unpaidApproved?'재청소 승인 · 무급':unpaidReclean?'재청소 검수 대기 · 무급':report?.status==='pending'?'폭탄방 검수 대기':report?.status==='approved'?'폭탄방 인정 · 전체 검수 대기':report?.status==='rejected'?'폭탄방 미인정 · 전체 검수 대기':'검수 대기';
  6116 |           const rejectedBreakdown=wholeRejected?`${rejectedDecision} · 기본 ${money(fee.base)} + 폭탄방 추가 ${money(fee.bonus)} = 결정 참고 ${money(fee.total)} · 청소 전체 반려로 실제 적립 0원`:'';
```

### occurrence 2 · line 6444

```html
  6399 |       function spreadsheetSafeCell(value) {
  6400 |         const text=String(value??'').replaceAll('\u0000','');
  6401 |         return /^\s*[=+\-@]/.test(text)?`'${text}`:text;
  6402 |       }
  6403 |       const XLSX_UTF8=new TextEncoder();
  6404 |       const XLSX_CRC32_TABLE=(()=>{const table=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=(c&1)?0xedb88320^(c>>>1):c>>>1;table[n]=c>>>0;}return table;})();
  6405 |       function xlsxCrc32(bytes){let crc=0xffffffff;for(const byte of bytes)crc=XLSX_CRC32_TABLE[(crc^byte)&0xff]^(crc>>>8);return (crc^0xffffffff)>>>0;}
  6406 |       const xlsxLe16=n=>Uint8Array.of(n&0xff,(n>>>8)&0xff);
  6407 |       const xlsxLe32=n=>Uint8Array.of(n&0xff,(n>>>8)&0xff,(n>>>16)&0xff,(n>>>24)&0xff);
  6408 |       function xlsxConcat(parts){const result=new Uint8Array(parts.reduce((sum,part)=>sum+part.length,0));let offset=0;for(const part of parts){result.set(part,offset);offset+=part.length;}return result;}
  6409 |       function xlsxZipStore(files){
  6410 |         const localParts=[],centralParts=[];let localOffset=0;
  6411 |         for(const [path,content] of files){
  6412 |           const name=XLSX_UTF8.encode(path),data=typeof content==='string'?XLSX_UTF8.encode(content):content,crc=xlsxCrc32(data);
  6413 |           const local=xlsxConcat([xlsxLe32(0x04034b50),xlsxLe16(20),xlsxLe16(0x0800),xlsxLe16(0),xlsxLe16(0),xlsxLe16(0x21),xlsxLe32(crc),xlsxLe32(data.length),xlsxLe32(data.length),xlsxLe16(name.length),xlsxLe16(0),name,data]);
  6414 |           localParts.push(local);
  6415 |           centralParts.push(xlsxConcat([xlsxLe32(0x02014b50),xlsxLe16(20),xlsxLe16(20),xlsxLe16(0x0800),xlsxLe16(0),xlsxLe16(0),xlsxLe16(0x21),xlsxLe32(crc),xlsxLe32(data.length),xlsxLe32(data.length),xlsxLe16(name.length),xlsxLe16(0),xlsxLe16(0),xlsxLe16(0),xlsxLe16(0),xlsxLe32(0),xlsxLe32(localOffset),name]));
  6416 |           localOffset+=local.length;
  6417 |         }
  6418 |         const central=xlsxConcat(centralParts),end=xlsxConcat([xlsxLe32(0x06054b50),xlsxLe16(0),xlsxLe16(0),xlsxLe16(files.length),xlsxLe16(files.length),xlsxLe32(central.length),xlsxLe32(localOffset),xlsxLe16(0)]);
  6419 |         return xlsxConcat([...localParts,central,end]);
  6420 |       }
  6421 |       const XLSX_XML_ESCAPES={'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'};
  6422 |       function xlsxXmlText(value){return String(value??'').replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\uFFFE\uFFFF]/g,'').replace(/[&<>"']/g,char=>XLSX_XML_ESCAPES[char]);}
  6423 |       function xlsxColumn(number){let result='';while(number>0){number--;result=String.fromCharCode(65+(number%26))+result;number=Math.floor(number/26);}return result;}
  6424 |       function createRoomXlsx(matrix){
  6425 |         const sheetRows=matrix.map((row,rowIndex)=>`<row r="${rowIndex+1}">${row.map((value,columnIndex)=>`<c r="${xlsxColumn(columnIndex+1)}${rowIndex+1}" t="inlineStr"><is><t xml:space="preserve">${xlsxXmlText(value)}</t></is></c>`).join('')}</row>`).join('');
  6426 |         const files=[
  6427 |           ['[Content_Types].xml','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>'],
  6428 |           ['_rels/.rels','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>'],
  6429 |           ['xl/workbook.xml','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="객실 현황" sheetId="1" r:id="rId1"/></sheets></workbook>'],
  6430 |           ['xl/_rels/workbook.xml.rels','<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'],
  6431 |           ['xl/worksheets/sheet1.xml',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>${sheetRows}</sheetData></worksheet>`]
  6432 |         ];
  6433 |         return new Blob([xlsxZipStore(files)],{type:'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'});
  6434 |       }
  6435 |       const ROOM_EXPORT_COLUMNS=['기준일','객실','객실 유형','기본 청소요금','엘리베이터 위치','정보 상태','투숙 상태','카드 주 상태','예정 체크아웃','실제 체크아웃','체크인','얼리 체크인','레이트 체크아웃','예약 등록','현재 입실','청소 상태','청소 담당','촛불 수량','운영 상태','운영 중지 사유','대체 객실'];
  6436 |       function roomExportRows(filtered=false) {
  6437 |         const rooms=filtered?filteredRooms():ROOMS;
  6438 |         return rooms.map(room=>{
  6439 |           const p=roomPresentation(room.no),special=roomReservationStatus(room),stop=state.roomMoves[room.no]||{},stopReason=state.roomStopReasons[room.no]||stop.reason||'사유 확인 필요',held=roomDataIssue(room.no);
  6440 |           const informationStatus=held?'확인 필요':'확인 완료',occupancyStatus=held?'미확정':room.occupancy==='occupied'?'투숙 중':'공실';
  6441 |           return [state.selectedDate,`${room.no}호`,ROOM_TYPES[room.type].name,money(ROOM_TYPES[room.type].rate),elevatorLabel(room),informationStatus,occupancyStatus,p.status,room.reservationCheckoutAt||room.nextCheckoutAt||room.checkout,room.actualCheckoutAt||'—',room.checkin,special.early?`자동 · ${special.earlyOffset} · ${special.checkin}`:'—',special.late?`자동 · ${special.lateOffset} · ${special.checkout}`:'—',held?'확인 필요':'가능',p.available?'가능':'불가',cleaningLabel(state.jobs[room.no]),held?'확인 필요':room.assignee,held?'확인 필요':`${room.occupancy==='occupied'?0:state.candles[room.no]||0}개`,held?'확인 필요':state.roomStopped[room.no]?'운영 중지':'정상',held||state.roomStopped[room.no]?held||stopReason:'—',state.roomStopped[room.no]&&stop.to?`${stop.to}호`:'—'];
  6442 |         });
  6443 |       }
  6444 |       function openRoomExport(trigger=document.activeElement) {
  6445 |         if(state.role!=='admin'){toast('객실 현황 내보내기는 관리자만 사용할 수 있습니다.','error');return;}
  6446 |         if(isLocked()){toast('최신 객실 상태를 확인한 뒤 내보낼 수 있습니다.','error');return;}
  6447 |         const filteredCount=filteredRooms().length;
  6448 |         showModal({title:'객실 현황 전체 내보내기',subtitle:`${dateLabel()} · 전체 ${ROOMS.length}객실 · 데모 화면 스냅샷`,trigger,body:`<div class="notice notice-info"><div><strong>PIN 원문과 고객 개인정보는 파일에 포함하지 않습니다.</strong><br>객실 유형·정본 청소요금·엘리베이터 위치·투숙/공실/정보 확인 필요와 고객 배정 가능 여부와 체크인·체크아웃, 청소, 촛불, 운영 중지 사유를 내보냅니다.</div></div><label class="room-export-scope" for="export-filtered"><input id="export-filtered" type="checkbox"><span><strong>현재 검색·필터 결과만 내보내기 · ${filteredCount}객실</strong><span>선택하지 않으면 ${dateLabel()} 전체 ${ROOMS.length}객실을 저장합니다.</span></span></label><div class="room-export-options"><button class="btn btn-outline" type="button" data-action="export-rooms-csv">${icon('download','icon-sm')}CSV 다운로드</button><button class="btn btn-primary" type="button" data-action="export-rooms-xls">${icon('download','icon-sm')}엑셀(.xlsx) 다운로드</button></div>`});
  6449 |       }
  6450 |       function downloadRoomExport(format) {
  6451 |         if(state.role!=='admin'){closeModal();toast('객실 현황 내보내기는 관리자만 사용할 수 있습니다.','error');return;}
  6452 |         if(isLocked()){closeModal();toast('오래된 데이터는 내보내지 않았습니다. 다시 시도해 최신 상태를 확인하세요.','error');return;}
  6453 |         const filtered=!!document.getElementById('export-filtered')?.checked,rows=roomExportRows(filtered),suffix=filtered?'filtered':'all',base=`castle-the-art_rooms_${state.selectedDate}_${suffix}_demo`;
  6454 |         if(filtered&&!rows.length){toast('현재 검색·필터 결과가 없어 파일을 만들지 않았습니다.','error');return;}
  6455 |         let blob,name;
  6456 |         if(format==='csv'){
  6457 |           const quote=value=>`"${spreadsheetSafeCell(value).replaceAll('"','""')}"`,csv=[ROOM_EXPORT_COLUMNS,...rows].map(row=>row.map(quote).join(',')).join('\r\n');
  6458 |           blob=new Blob(['\ufeff',csv],{type:'text/csv;charset=utf-8'});name=`${base}.csv`;
  6459 |         } else {
  6460 |           blob=createRoomXlsx([ROOM_EXPORT_COLUMNS,...rows]);name=`${base}.xlsx`;
  6461 |         }
  6462 |         const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=name;link.hidden=true;document.body.appendChild(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);appendEvent('객실 현황 내보내기',`${name} · ${rows.length}객실 · PIN 제외`);closeModal();toast(`${format==='csv'?'CSV':'엑셀'} 파일 다운로드를 시작했습니다.`);
  6463 |       }
  6464 | 
  6465 |       function secureFourDigits() {
  6466 |         const a=new Uint16Array(1);let n;
  6467 |         do { crypto.getRandomValues(a); n=a[0]; } while(n>=60000);
  6468 |         return String(n%10000).padStart(4,'0');
  6469 |       }
  6470 |       function pinEditorMarkup(no,value='') {
  6471 |         return `<div class="modal-backdrop pin-backdrop" data-action="backdrop-close"><section class="modal pin-sheet" role="dialog" aria-modal="true" aria-labelledby="pin-sheet-title" aria-describedby="pin-sheet-desc"><div class="pin-sheet-body"><h2 id="pin-sheet-title">${no}호 객실 PIN 수정</h2><p id="pin-sheet-desc">숫자 4자리를 직접 입력하거나 랜덤 생성하세요.</p><div class="field"><label for="pin-edit-input">새 4자리 PIN</label><div class="pin-edit-preview"><div class="pin-input-wrap"><input id="pin-edit-input" class="input-control" inputmode="numeric" pattern="[0-9]{4}" maxlength="4" autocomplete="off" aria-describedby="pin-edit-help" value="${esc(value)}"><button class="icon-btn pin-clear" type="button" data-action="pin-clear" aria-label="입력한 PIN 지우기">${icon('x')}</button></div><button class="btn btn-outline" type="button" data-action="pin-random">${icon('refresh','icon-sm')}랜덤 생성</button></div><small id="pin-edit-help">앞자리 0도 유지됩니다.</small></div></div><footer class="modal-foot"><button class="btn btn-outline" type="button" data-action="close-modal">취소</button><button class="btn btn-primary" type="button" data-action="pin-review" data-id="${no}">변경 내용 확인</button></footer></section></div>`;
  6472 |       }
  6473 |       function pinReviewMarkup(no,value) {
  6474 |         return `<div class="modal-backdrop pin-backdrop" data-action="backdrop-close"><section class="modal pin-sheet" role="dialog" aria-modal="true" aria-labelledby="pin-review-title"><div class="pin-sheet-body"><h2 id="pin-review-title">${no}호 변경 내용 확인</h2><p>저장할 새 객실 PIN을 다시 확인하세요.</p><div class="pin-edit-preview"><div class="input-control" style="min-height:58px;display:flex;align-items:center;font-size:1.3rem;font-weight:900;letter-spacing:.22em">${esc(value)}</div><div class="btn btn-soft" aria-hidden="true">새 PIN</div></div><p class="audit-note" style="margin-top:12px">감사 이력에는 PIN 원문을 남기지 않습니다.</p></div><footer class="modal-foot"><button class="btn btn-outline" type="button" data-action="pin-back" data-id="${no}">돌아가서 수정</button><button class="btn btn-primary" type="button" data-action="pin-save" data-id="${no}">저장</button></footer></section></div>`;
  6475 |       }
  6476 |       function openPinEditor(no,trigger=pinCardTrigger||document.activeElement) {
  6477 |         pendingPin=null;if(trigger?.dataset?.action==='pin-edit')pinCardTrigger=trigger;modalTrigger=pinCardTrigger||trigger;
  6478 |         const current=readProtectedPin(no);
  6479 |         document.getElementById('modal-root').innerHTML=pinEditorMarkup(no,current);
  6480 |         lockModalViewport();setModalBackgroundLocked(true);const entry=registerModalHistory({kind:'pin-editor',payload:{room:no}});if(entry?.modalSessionId){activePinModalSessionId=entry.modalSessionId;rememberPinModalSecret(entry.modalSessionId,no,current);}requestAnimationFrame(()=>document.getElementById('pin-edit-input')?.focus());
  6481 |       }
  6482 |       function openPinReview(no,value) {
  6483 |         captureCurrentModalHistory();
  6484 |         pendingPin={room:no,value};
  6485 |         document.getElementById('modal-root').innerHTML=pinReviewMarkup(no,value);
  6486 |         setModalBackgroundLocked(true);const entry=registerModalHistory({stack:true,kind:'pin-review',payload:{room:no}});if(entry?.modalSessionId){activePinModalSessionId=entry.modalSessionId;rememberPinModalSecret(entry.modalSessionId,no,value);}requestAnimationFrame(()=>document.querySelector('[data-action="pin-save"]')?.focus());
  6487 |       }
  6488 |       function openOperationStatus(no) {
  6489 |         const room=ROOMS.find(r=>r.no===no), same=ROOMS.find(r=>r.no!==no&&r.type===room.type&&roomPresentation(r.no).available), alternative=ROOMS.find(r=>r.no!==no&&roomPresentation(r.no).available);
  6490 |         showModal({title:`${no}호 운영 중지`,subtitle:'고객 배정을 멈추고 필요하면 이 흐름 안에서만 다른 객실을 배정합니다.',large:true,body:`<div class="notice notice-danger">운영 중지는 현재 예약·청소 이력을 삭제하지 않습니다. 투숙 중이면 현장 조율 후 대체 객실을 확정하세요.</div><div class="field"><label for="relocate-room">대체 객실 · 선택</label><select id="relocate-room" class="select-control"><option value="">배정하지 않음</option>${same?`<option value="${same.no}">${same.no}호 · 같은 타입 · 준비 완료 우선</option>`:''}${alternative&&alternative.no!==same?.no?`<option value="${alternative.no}">${alternative.no}호 · 다른 타입 · 준비 완료</option>`:''}</select></div><div class="field" style="margin-top:12px"><label for="stop-reason">운영 중지·다른 타입 배정 사유</label><textarea id="stop-reason" class="input-control" rows="3" required>시설 점검 · 데모</textarea></div>`,confirmLabel:'운영 중지 적용',confirmAction:'confirm-operation-stop',confirmVariant:'danger'});
  6491 |         document.querySelector('[data-action="confirm-operation-stop"]')?.setAttribute('data-id',no);
  6492 |       }
  6493 |       function openDirectAssign(no) {
  6494 |         const reclean=activeRecleanAttempt(no),hold=roomIsOnHold(no);if(state.role!=='admin'||isLocked()||hold||reclean||!['public','draft','future','scheduled','unassigned'].includes(state.jobs[no])){toast(hold?`${no}호는 운영 상태 확인 보류 객실이라 예약·청소대상·배정을 변경할 수 없습니다.`:reclean?'재청소는 처음 청소한 본인에게 고정되어 다른 메이드에게 직접 배정할 수 없습니다.':'관리자 최신 상태의 미시작 작업만 담당 후보를 확인하고 배정할 수 있습니다.','error');return;}
  6495 |         const room=ROOMS.find(entry=>entry.no===no)||ROOMS[0],currentAttempt=activeUnfinishedAttempt(no),pinViewed=!!currentAttempt&&roomPinWasViewed(no,currentAttempt.id);if(pinViewed){toast(`${no}호 PIN을 이미 조회해 담당을 바꾸기 전에 현장 영향 확인이 필요합니다.`,'error');return;}const todayTarget=assignmentTargetsForDate(state.selectedDate).find(entry=>entry.room===no),tomorrowTarget=assignmentTargetsForDate(addIsoDays(state.selectedDate,1)).find(entry=>entry.room===no),roomTarget=todayTarget||tomorrowTarget;if(roomTarget){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=targetEffectiveDate(roomTarget)===state.selectedDate?'assignment-today':'assignment-tomorrow';syncAssignmentDateForCleaningTab(state);state.assignmentTypeFilter=room.type;});toast(`${no}호 ${targetEffectiveDate(roomTarget)===state.selectedDate?'오늘':'내일'} 청소대상은 배정 화면에서 담당과 순서를 함께 저장·통보해 주세요.`);return;}const item=directAssignmentTarget(no),context=assignmentContext(item),displayRate=currentAttempt?.baseRateSnapshot??context.type.rate,workDate=directAssignmentWorkDate(no),currentPerformerId=currentAttempt?.performerId||MAIDS.find(maid=>maid.name===room.assignee)?.id||null,eligible=MAIDS.filter(maid=>maid.id!==currentPerformerId&&maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,workDate)==='available');
  6496 |         showModal({title:`${no}호 청소 담당 직접 배정`,subtitle:'미시작 작업의 담당 메이드는 관리자만 지정할 수 있습니다.',body:`<div class="info-grid"><div class="info-item"><span>객실</span><strong>${no}호</strong></div><div class="info-item"><span>객실 타입</span><strong>${esc(context.type.name)}</strong></div><div class="info-item"><span>엘리베이터 위치</span><strong>${esc(elevatorLabel(room))}</strong></div><div class="info-item"><span>청소 유형·요금</span><strong>${esc(item.kind)} · ${money(displayRate)} · 8월 시트</strong></div><div class="info-item"><span>입퇴실 일정</span><strong>${esc(assignmentScheduleText(item))}</strong></div></div><div class="field" style="margin-top:14px"><label for="assign-maid">근무 가능 메이드</label><select id="assign-maid" class="select-control">${eligible.map(maid=>`<option value="${esc(maid.name)}">${esc(maid.name)} (근무 가능)</option>`).join('')}${eligible.length?'':'<option value="" disabled>근무 가능 메이드 없음</option>'}</select><small>불가·미제출 메이드는 선택 목록에 표시되지 않습니다.</small></div><div class="notice notice-info" style="margin-top:12px">저장하면 새 담당 구간이 타임라인에 남고 해당 메이드에게 통보됩니다.</div>`,confirmLabel:'담당 배정·통보',confirmAction:'confirm-direct-assign'});
  6497 |         const confirm=document.querySelector('[data-action="confirm-direct-assign"]');confirm?.setAttribute('data-id',no);confirm?.setAttribute('data-target',item.id);confirm?.setAttribute('data-attempt',currentAttempt?.id||'');confirm?.setAttribute('data-work-date',workDate);confirm?.setAttribute('data-kind',item.kind);
  6498 |         if(!eligible.length)document.querySelector('[data-action="confirm-direct-assign"]')?.setAttribute('disabled','');
  6499 |       }
  6500 |       function reservationPreviewMarkup(checkinAt,checkoutAt) {
  6501 |         const status=reservationTimeStatus(checkinAt,checkoutAt),valid=checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;
  6502 |         return `<div class="field field-full"><div class="notice notice-info" style="margin:0"><div style="width:100%"><strong>예약 기간</strong><div class="info-grid" id="reservation-time-preview" aria-live="polite" style="margin-top:10px"><div class="info-item"><span>체크인 → 체크아웃</span><strong data-reservation-night-status>${valid?`${nights}박`:'입퇴실 시각 확인 필요'}</strong></div><div class="info-item"><span>체크인 · 16:00 기준</span><strong data-reservation-checkin-status>${esc(reservationStatusText(status,'checkin'))}</strong></div><div class="info-item"><span>체크아웃 · 11:00 기준</span><strong data-reservation-checkout-status>${esc(reservationStatusText(status,'checkout'))}</strong></div></div></div></div><small>체크인 다음에 체크아웃을 입력하며 1시간 단위로 선택합니다.</small></div>`;
  6503 |       }
  6504 |       function updateReservationTimePreview() {
  6505 |         const checkinAt=document.getElementById('res-checkin')?.value||'',checkoutAt=document.getElementById('res-checkout')?.value||'',status=reservationTimeStatus(checkinAt,checkoutAt);
  6506 |         const checkinStatus=document.querySelector('[data-reservation-checkin-status]'),checkoutStatus=document.querySelector('[data-reservation-checkout-status]'),nightStatus=document.querySelector('[data-reservation-night-status]');
  6507 |         if(checkinStatus)checkinStatus.textContent=reservationStatusText(status,'checkin');
  6508 |         if(checkoutStatus)checkoutStatus.textContent=reservationStatusText(status,'checkout');
  6509 |         if(nightStatus){const valid=checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;nightStatus.textContent=valid?`${nights}박`:'입퇴실 시각 확인 필요';}
  6510 |       }
  6511 |       function updateReservationGuestControls(resetToDefault=false) {
  6512 |         const roomNo=document.getElementById('res-room')?.value||'',policy=guestPolicyForRoom(roomNo),input=document.getElementById('res-guests'),value=document.getElementById('res-guests-value'),help=document.getElementById('res-guests-help'),stepper=document.getElementById('reservation-guest-stepper'),minus=document.querySelector('[data-action="reservation-guest-change"][data-delta="-1"]'),plus=document.querySelector('[data-action="reservation-guest-change"][data-delta="1"]');
  6513 |         if(!input||!value||!stepper)return;
```

### occurrence 3 · line 6520

```html
  6475 |       }
  6476 |       function openPinEditor(no,trigger=pinCardTrigger||document.activeElement) {
  6477 |         pendingPin=null;if(trigger?.dataset?.action==='pin-edit')pinCardTrigger=trigger;modalTrigger=pinCardTrigger||trigger;
  6478 |         const current=readProtectedPin(no);
  6479 |         document.getElementById('modal-root').innerHTML=pinEditorMarkup(no,current);
  6480 |         lockModalViewport();setModalBackgroundLocked(true);const entry=registerModalHistory({kind:'pin-editor',payload:{room:no}});if(entry?.modalSessionId){activePinModalSessionId=entry.modalSessionId;rememberPinModalSecret(entry.modalSessionId,no,current);}requestAnimationFrame(()=>document.getElementById('pin-edit-input')?.focus());
  6481 |       }
  6482 |       function openPinReview(no,value) {
  6483 |         captureCurrentModalHistory();
  6484 |         pendingPin={room:no,value};
  6485 |         document.getElementById('modal-root').innerHTML=pinReviewMarkup(no,value);
  6486 |         setModalBackgroundLocked(true);const entry=registerModalHistory({stack:true,kind:'pin-review',payload:{room:no}});if(entry?.modalSessionId){activePinModalSessionId=entry.modalSessionId;rememberPinModalSecret(entry.modalSessionId,no,value);}requestAnimationFrame(()=>document.querySelector('[data-action="pin-save"]')?.focus());
  6487 |       }
  6488 |       function openOperationStatus(no) {
  6489 |         const room=ROOMS.find(r=>r.no===no), same=ROOMS.find(r=>r.no!==no&&r.type===room.type&&roomPresentation(r.no).available), alternative=ROOMS.find(r=>r.no!==no&&roomPresentation(r.no).available);
  6490 |         showModal({title:`${no}호 운영 중지`,subtitle:'고객 배정을 멈추고 필요하면 이 흐름 안에서만 다른 객실을 배정합니다.',large:true,body:`<div class="notice notice-danger">운영 중지는 현재 예약·청소 이력을 삭제하지 않습니다. 투숙 중이면 현장 조율 후 대체 객실을 확정하세요.</div><div class="field"><label for="relocate-room">대체 객실 · 선택</label><select id="relocate-room" class="select-control"><option value="">배정하지 않음</option>${same?`<option value="${same.no}">${same.no}호 · 같은 타입 · 준비 완료 우선</option>`:''}${alternative&&alternative.no!==same?.no?`<option value="${alternative.no}">${alternative.no}호 · 다른 타입 · 준비 완료</option>`:''}</select></div><div class="field" style="margin-top:12px"><label for="stop-reason">운영 중지·다른 타입 배정 사유</label><textarea id="stop-reason" class="input-control" rows="3" required>시설 점검 · 데모</textarea></div>`,confirmLabel:'운영 중지 적용',confirmAction:'confirm-operation-stop',confirmVariant:'danger'});
  6491 |         document.querySelector('[data-action="confirm-operation-stop"]')?.setAttribute('data-id',no);
  6492 |       }
  6493 |       function openDirectAssign(no) {
  6494 |         const reclean=activeRecleanAttempt(no),hold=roomIsOnHold(no);if(state.role!=='admin'||isLocked()||hold||reclean||!['public','draft','future','scheduled','unassigned'].includes(state.jobs[no])){toast(hold?`${no}호는 운영 상태 확인 보류 객실이라 예약·청소대상·배정을 변경할 수 없습니다.`:reclean?'재청소는 처음 청소한 본인에게 고정되어 다른 메이드에게 직접 배정할 수 없습니다.':'관리자 최신 상태의 미시작 작업만 담당 후보를 확인하고 배정할 수 있습니다.','error');return;}
  6495 |         const room=ROOMS.find(entry=>entry.no===no)||ROOMS[0],currentAttempt=activeUnfinishedAttempt(no),pinViewed=!!currentAttempt&&roomPinWasViewed(no,currentAttempt.id);if(pinViewed){toast(`${no}호 PIN을 이미 조회해 담당을 바꾸기 전에 현장 영향 확인이 필요합니다.`,'error');return;}const todayTarget=assignmentTargetsForDate(state.selectedDate).find(entry=>entry.room===no),tomorrowTarget=assignmentTargetsForDate(addIsoDays(state.selectedDate,1)).find(entry=>entry.room===no),roomTarget=todayTarget||tomorrowTarget;if(roomTarget){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=targetEffectiveDate(roomTarget)===state.selectedDate?'assignment-today':'assignment-tomorrow';syncAssignmentDateForCleaningTab(state);state.assignmentTypeFilter=room.type;});toast(`${no}호 ${targetEffectiveDate(roomTarget)===state.selectedDate?'오늘':'내일'} 청소대상은 배정 화면에서 담당과 순서를 함께 저장·통보해 주세요.`);return;}const item=directAssignmentTarget(no),context=assignmentContext(item),displayRate=currentAttempt?.baseRateSnapshot??context.type.rate,workDate=directAssignmentWorkDate(no),currentPerformerId=currentAttempt?.performerId||MAIDS.find(maid=>maid.name===room.assignee)?.id||null,eligible=MAIDS.filter(maid=>maid.id!==currentPerformerId&&maidCanReceiveNewAssignment(maid.id)&&availabilityForWorkDate(maid.id,workDate)==='available');
  6496 |         showModal({title:`${no}호 청소 담당 직접 배정`,subtitle:'미시작 작업의 담당 메이드는 관리자만 지정할 수 있습니다.',body:`<div class="info-grid"><div class="info-item"><span>객실</span><strong>${no}호</strong></div><div class="info-item"><span>객실 타입</span><strong>${esc(context.type.name)}</strong></div><div class="info-item"><span>엘리베이터 위치</span><strong>${esc(elevatorLabel(room))}</strong></div><div class="info-item"><span>청소 유형·요금</span><strong>${esc(item.kind)} · ${money(displayRate)} · 8월 시트</strong></div><div class="info-item"><span>입퇴실 일정</span><strong>${esc(assignmentScheduleText(item))}</strong></div></div><div class="field" style="margin-top:14px"><label for="assign-maid">근무 가능 메이드</label><select id="assign-maid" class="select-control">${eligible.map(maid=>`<option value="${esc(maid.name)}">${esc(maid.name)} (근무 가능)</option>`).join('')}${eligible.length?'':'<option value="" disabled>근무 가능 메이드 없음</option>'}</select><small>불가·미제출 메이드는 선택 목록에 표시되지 않습니다.</small></div><div class="notice notice-info" style="margin-top:12px">저장하면 새 담당 구간이 타임라인에 남고 해당 메이드에게 통보됩니다.</div>`,confirmLabel:'담당 배정·통보',confirmAction:'confirm-direct-assign'});
  6497 |         const confirm=document.querySelector('[data-action="confirm-direct-assign"]');confirm?.setAttribute('data-id',no);confirm?.setAttribute('data-target',item.id);confirm?.setAttribute('data-attempt',currentAttempt?.id||'');confirm?.setAttribute('data-work-date',workDate);confirm?.setAttribute('data-kind',item.kind);
  6498 |         if(!eligible.length)document.querySelector('[data-action="confirm-direct-assign"]')?.setAttribute('disabled','');
  6499 |       }
  6500 |       function reservationPreviewMarkup(checkinAt,checkoutAt) {
  6501 |         const status=reservationTimeStatus(checkinAt,checkoutAt),valid=checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;
  6502 |         return `<div class="field field-full"><div class="notice notice-info" style="margin:0"><div style="width:100%"><strong>예약 기간</strong><div class="info-grid" id="reservation-time-preview" aria-live="polite" style="margin-top:10px"><div class="info-item"><span>체크인 → 체크아웃</span><strong data-reservation-night-status>${valid?`${nights}박`:'입퇴실 시각 확인 필요'}</strong></div><div class="info-item"><span>체크인 · 16:00 기준</span><strong data-reservation-checkin-status>${esc(reservationStatusText(status,'checkin'))}</strong></div><div class="info-item"><span>체크아웃 · 11:00 기준</span><strong data-reservation-checkout-status>${esc(reservationStatusText(status,'checkout'))}</strong></div></div></div></div><small>체크인 다음에 체크아웃을 입력하며 1시간 단위로 선택합니다.</small></div>`;
  6503 |       }
  6504 |       function updateReservationTimePreview() {
  6505 |         const checkinAt=document.getElementById('res-checkin')?.value||'',checkoutAt=document.getElementById('res-checkout')?.value||'',status=reservationTimeStatus(checkinAt,checkoutAt);
  6506 |         const checkinStatus=document.querySelector('[data-reservation-checkin-status]'),checkoutStatus=document.querySelector('[data-reservation-checkout-status]'),nightStatus=document.querySelector('[data-reservation-night-status]');
  6507 |         if(checkinStatus)checkinStatus.textContent=reservationStatusText(status,'checkin');
  6508 |         if(checkoutStatus)checkoutStatus.textContent=reservationStatusText(status,'checkout');
  6509 |         if(nightStatus){const valid=checkinAt&&checkoutAt&&checkinAt<checkoutAt&&checkinAt.slice(0,10)<checkoutAt.slice(0,10),nights=valid?Math.max(1,Math.round((dateObject(checkoutAt.slice(0,10))-dateObject(checkinAt.slice(0,10)))/86400000)):0;nightStatus.textContent=valid?`${nights}박`:'입퇴실 시각 확인 필요';}
  6510 |       }
  6511 |       function updateReservationGuestControls(resetToDefault=false) {
  6512 |         const roomNo=document.getElementById('res-room')?.value||'',policy=guestPolicyForRoom(roomNo),input=document.getElementById('res-guests'),value=document.getElementById('res-guests-value'),help=document.getElementById('res-guests-help'),stepper=document.getElementById('reservation-guest-stepper'),minus=document.querySelector('[data-action="reservation-guest-change"][data-delta="-1"]'),plus=document.querySelector('[data-action="reservation-guest-change"][data-delta="1"]');
  6513 |         if(!input||!value||!stepper)return;
  6514 |         const current=resetToDefault?policy.defaultGuestCount:Number(input.value),count=Number.isInteger(current)&&current>=1&&current<=policy.maxGuestCount?current:policy.defaultGuestCount;
  6515 |         input.value=String(count);value.textContent=guestCountLabel(count);if(help)help.textContent=`기본 ${policy.defaultGuestCount}명 · 최대 ${policy.maxGuestCount}명`;
  6516 |         stepper.dataset.max=String(policy.maxGuestCount);
  6517 |         if(minus){minus.disabled=count<=1;minus.setAttribute('aria-label',`${roomNo}호 예약 인원수 1명 줄이기`);}
  6518 |         if(plus){plus.disabled=count>=policy.maxGuestCount;plus.setAttribute('aria-label',`${roomNo}호 예약 인원수 1명 늘리기, 최대 ${policy.maxGuestCount}명`);}
  6519 |       }
  6520 |       function openRoomInfoEditor(no,trigger=document.activeElement) {
  6521 |         const room=ROOMS.find(item=>item.no===no);
  6522 |         if(!room||state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 객실 정보를 수정할 수 있습니다.','error');return;}
  6523 |         maskPin();
  6524 |         const held=roomIsOnHold(no),typeOptions=Object.entries(ROOM_TYPES).map(([id,type])=>`<option value="${id}" ${room.type===id?'selected':''}>${esc(type.name)} · ${money(type.rate)}</option>`).join('');
  6525 |         showModal({title:`${no}호 객실 정보 수정`,subtitle:'객실번호는 이력 연결키로 유지하고 타입·엘리베이터를 수정합니다.',trigger,body:`<form id="room-info-form" class="form-grid"><div class="field"><label for="room-info-number">객실번호</label><input id="room-info-number" class="input-control" value="${no}" readonly aria-readonly="true"><small>PIN·청소·주급 이력과 연결된 식별값</small></div><div class="field"><label for="room-info-type">객실 타입</label><select id="room-info-type" class="select-control">${typeOptions}</select></div><div class="field"><label for="room-info-elevator">엘리베이터</label><select id="room-info-elevator" class="select-control"><option value="" ${room.elevator?'':'selected'}>미기재</option>${['A','B','C'].map(value=>`<option value="${value}" ${room.elevator===value?'selected':''}>${value} 엘리베이터</option>`).join('')}</select></div>${held?`<div class="field"><label for="room-info-occupancy">현재 투숙 상태</label><select id="room-info-occupancy" class="select-control"><option value="">선택하세요</option><option value="vacant">공실</option><option value="occupied">투숙 중</option></select><small>선택하면 정보 확인 필요 상태가 해제됩니다.</small></div>`:''}<div class="field field-full"><div class="notice notice-info"><div><strong>적용 범위</strong><br>새 타입·엘리베이터는 이후 생성하는 작업부터 적용됩니다. 이미 완료·제출된 청소의 당시 단가와 템플릿은 그대로 보존됩니다.</div></div></div></form>`,confirmLabel:held?'정보 확정·보류 해제':'객실 정보 저장',confirmAction:'save-room-info'});
  6526 |         const confirm=document.querySelector('[data-action="save-room-info"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6527 |       }
  6528 |       function recordManualCheckoutScheduleChange(no,attempt,previousWorkDate,previousAccessStart) {
  6529 |         if(!attempt)return;
  6530 |         const targetId=attempt.workTargetId||assignmentHistoryTargetId(no,attempt.kind,previousWorkDate),record=state.assignments?.[targetId]||null,maidId=MAIDS.some(maid=>maid.id===attempt.performerId)?attempt.performerId:null,order=record?.order||record?.previousOrder||null,maidLabel=maidId?maidName(maidId):'미배정',room=ROOMS.find(item=>item.no===no),typeId=attempt.roomMetaSnapshot?.typeId||room?.type||'standard',type=ROOM_TYPES[typeId]||ROOM_TYPES.standard,ledgerTarget=state.cleaningTargets?.[targetId]||null,committed=record?.committedTarget||ledgerTarget||{id:targetId,room:no,type:typeId,kind:attempt.kind,source:'manual',sourceLabel:'현재 작업',rateSnapshot:Number(attempt.baseRateSnapshot)||Number(attempt.templateSnapshot?.rate)||type.rate,minutesSnapshot:Number(attempt.templateSnapshot?.minutes)||type.minutes,elevatorSnapshot:Object.prototype.hasOwnProperty.call(attempt.roomMetaSnapshot||{},'elevator')?attempt.roomMetaSnapshot.elevator:room?.elevator||null},committedReservationId=committed.reservationId||attempt.reservationIdSnapshot||null,committedGuestCount=assignmentGuestCount(committed)||(committedReservationId&&committedReservationId===attempt.reservationIdSnapshot?guestCountForAttempt(attempt):null),planDate=committed.planDate||committed.date||previousWorkDate,targetSnapshot={...committed,id:targetId,currentAttemptId:attempt.id,room:no,date:planDate,planDate,effectiveDate:state.selectedDate,checkout:attempt.checkoutSnapshot||state.time,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||state.time,reservationId:committedReservationId,guestCount:committedGuestCount};
  6531 |         if(record){
  6532 |           record.committedTarget=targetSnapshot;record.status='notified';record.scheduleChanged=false;record.guestCountChanged=false;record.reservationChanged=false;record.targetChanged=false;
  6533 |           if(record.maidId){record.previousMaidId=record.maidId;record.previousOrder=record.order;}
  6534 |         }
  6535 |         state.cleaningTargets[targetId]={...cleaningTargetSnapshot(targetSnapshot,planDate),...(state.cleaningTargets?.[targetId]||{}),...targetSnapshot,currentAttemptId:attempt.id};
  6536 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId,attemptId:attempt.id,assignmentDate:state.selectedDate,room:no,beforeMaidId:maidId,afterMaidId:maidId,before:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(previousWorkDate)} ${previousAccessStart}`:'미배정',after:maidId?`${maidLabel}${order?` · ${order}번째`:''} · ${dateLabel(state.selectedDate)} ${state.time}`:'미배정',reason:'실제 체크아웃 반영 · 기존 담당·수행 회차 유지 · 시작 시각 변경 재통보'});
  6537 |         if(maidId)appendEvent('내 청소 시작 시각 변경 통보',`${no}호 · ${dateLabel(previousWorkDate)} ${previousAccessStart} → ${dateLabel(state.selectedDate)} ${state.time} · 담당·회차 ${attempt.id} 유지`,{maidIds:[maidId],roomId:no});
  6538 |       }
  6539 |       function openManualCheckout(no,trigger=document.activeElement) {
  6540 |         const room=ROOMS.find(item=>item.no===no),blockingAttempt=manualCheckoutBlockingAttempt(no),unstartedAttempt=activeUnfinishedAttempt(no),pinViewed=unstartedAttempt&&roomPinWasViewed(no,unstartedAttempt.id);
  6541 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='occupied'){toast('관리자 최신 상태의 투숙 중 객실만 지금 체크아웃할 수 있습니다.','error');return;}
  6542 |         if(blockingAttempt){toast(`진행 중인 ${blockingAttempt.kind} ${blockingAttempt.id}을 먼저 마무리하세요.`,'error');return;}
  6543 |         showModal({title:`${no}호 지금 체크아웃`,subtitle:'예정 일정은 남기고 실제 퇴실만 지금 기록합니다.',trigger,body:`<div class="info-grid"><div class="info-item"><span>현재 상태</span><strong>투숙 중</strong></div><div class="info-item"><span>실제 체크아웃</span><strong>${dateLabel(state.selectedDate)} ${esc(state.time)}</strong></div><div class="info-item"><span>예정 체크아웃</span><strong>${esc(plannedCheckoutLabel(room))}</strong></div><div class="info-item"><span>처리 결과</span><strong>공실 · 퇴실 청소 필요</strong></div></div><div class="notice notice-warning" style="margin-top:14px"><div><strong>예약 취소가 아닙니다.</strong><br>예정 일정과 미래 예약은 유지하고 오늘 퇴실 청소는 한 건만 만듭니다.${unstartedAttempt?'<br>이미 배정된 미시작 청소는 담당과 순서를 유지하고 실제 퇴실 시각부터 시작할 수 있습니다.':''}${pinViewed?'<br>기존 PIN 조회는 종료되며 실제 퇴실 시각 이후 다시 확인할 수 있습니다.':''}</div></div>`,confirmLabel:'투숙 종료·청소 준비',confirmAction:'confirm-manual-checkout',confirmVariant:'danger'});
  6544 |         const confirm=document.querySelector('[data-action="confirm-manual-checkout"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6545 |       }
  6546 |       function openManualCheckin(no,trigger=document.activeElement) {
  6547 |         const room=ROOMS.find(item=>item.no===no),presentation=roomPresentation(no);
  6548 |         if(!room||state.role!=='admin'||isLocked()||roomIsOnHold(no)||room.occupancy!=='vacant'||presentation.available!==true){toast('청소·촛불·운영 조건이 모두 준비된 공실만 투숙 중으로 바꿀 수 있습니다.','error');return;}
  6549 |         showModal({title:`${no}호 투숙 시작`,subtitle:'현재 객실에 손님이 들어온 사실만 기록합니다.',trigger,body:`<div class="notice notice-info"><div><strong>고객 개인정보는 입력하지 않습니다.</strong><br>${dateLabel(state.selectedDate)} ${esc(state.time)}부터 객실 상태를 투숙 중으로 바꿉니다.</div></div>`,confirmLabel:'투숙 중으로 변경',confirmAction:'confirm-manual-checkin'});
  6550 |         const confirm=document.querySelector('[data-action="confirm-manual-checkin"]');if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=roomMasterFingerprint(room);}
  6551 |       }
  6552 |       function reservationNextRegistrationState(room,existing,buckets) {
  6553 |         const weekPast=reservationWeekIsPast(buckets.window.startDate),occupiedEnd=occupiedReservationEnd(room),needsCheckoutUpdate=occupiedStayNeedsCheckoutUpdate(room);
  6554 |         return {canAdd:!!existing&&!weekPast&&adminCanMutate()&&(room.occupancy!=='occupied'||!!occupiedEnd&&!needsCheckoutUpdate),nextDate:suggestedReservationStartDate(room.no),weekPast,occupiedEnd,needsCheckoutUpdate};
  6555 |       }
  6556 |       function reservationWeekScheduleMarkup(room,existing,buckets) {
  6557 |         const nextRegistration=reservationNextRegistrationState(room,existing,buckets),records=buckets.weekRecords,countLabel=nextRegistration.weekPast?`기록 ${records.length}건`:`예약 ${records.filter(item=>item.status==='active'&&!reservationRecordIsPast(item)).length}건`,eligibilityNote=existing&&!nextRegistration.weekPast&&room.occupancy==='occupied'&&(!nextRegistration.occupiedEnd||nextRegistration.needsCheckoutUpdate)?`<p class="reservation-week-note">${icon('alert','icon-sm')}${nextRegistration.needsCheckoutUpdate?'예정 체크아웃이 지났습니다. 현재 예약의 체크아웃을 갱신하거나 지금 체크아웃을 먼저 처리하세요.':'현재 투숙의 체크아웃을 먼저 입력하세요.'}</p>`:'',rows=records.map(reservation=>{
  6558 |           const readOnly=nextRegistration.weekPast||reservationRecordIsPast(reservation),assignment=cleaningAssignmentForReservation(reservation),status=readOnly?reservationHistoryStatus(reservation):(assignment.assigned?`${assignment.name} · ${assignment.status}`:'청소 미배정'),content=`<span class="reservation-list-period"><strong>${esc(quickRangeLabel(reservation))}</strong></span><span class="reservation-list-meta">${reservationNights(reservation)}박 · ${reservationGuestCount(reservation)}명</span><span class="reservation-list-status">${esc(status)}</span><span class="reservation-list-arrow">${readOnly?'':icon('chevronRight','icon-sm')}</span>`;
  6559 |           return readOnly?`<div class="reservation-list-row reservation-history-row" aria-label="${esc(`${quickRangeLabel(reservation)} ${reservationNights(reservation)}박 ${reservationGuestCount(reservation)}명 ${status}`)}">${content}</div>`:`<button class="reservation-list-row" type="button" data-action="quick-reservation-edit" data-id="${esc(reservation.id)}" data-room="${room.no}" data-week="${buckets.window.startDate}" ${existing?.id===reservation.id?'aria-current="true"':''}>${content}</button>`;
  6560 |         }).join('');
  6561 |         const list=rows?`<div class="reservation-list"><div class="reservation-list-head" aria-hidden="true"><span>예약 일정</span><span>숙박 · 인원</span><span>청소 상태</span><span></span></div>${rows}</div>`:`<p class="reservation-schedule-empty">이 주의 예약 기록이 없습니다.</p>`;
  6562 |         return `<div class="field field-full reservation-schedule"><section class="reservation-schedule-window" aria-label="${room.no}호 ${esc(weekRangeLabel(buckets.window.startDate))} 예약"><div class="reservation-week-nav"><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="-1" aria-label="이전 주 예약 보기">${icon('chevronLeft')}</button><button class="reservation-week-range" type="button" data-action="open-reservation-week-calendar" data-room="${room.no}" aria-haspopup="dialog" aria-label="${esc(weekRangeLabel(buckets.window.startDate,true))} 주차 선택, ${countLabel}"><strong>${esc(weekRangeLabel(buckets.window.startDate))}</strong><span>${countLabel}</span></button><button class="icon-btn" type="button" data-action="reservation-week-shift" data-room="${room.no}" data-offset="1" aria-label="다음 주 예약 보기">${icon('chevronRight')}</button></div>${nextRegistration.weekPast?`<p class="reservation-week-note">${icon('lock','icon-sm')}지난 예약 기록 · 조회만 가능</p>`:''}${eligibilityNote}${list}</section></div>`;
  6563 |       }
  6564 |       function reservationModalConfig(roomNo='211',reservationId='',newDate='') {
  6565 |         const requestedCurrent=reservationId==='__current__',isNew=reservationId==='__new__'||requestedCurrent,requestedId=reservationId&&!isNew?reservationId:'',requested=requestedId?state.reservations.find(item=>item.id===requestedId)||null:null,stale=!!(requestedId&&!requested);
  6566 |         const room=ROOMS.find(item=>item.no===(requested?.room||String(roomNo)))||ROOMS.find(item=>item.no==='211')||ROOMS[0],selectedWeek=weekStartIso(state.reservationWeekStart||state.selectedDate),buckets=reservationBucketsForRoom(state,room.no,selectedWeek),requestedCurrentStay=!!requested&&currentOccupiedReservation(room)?.id===requested.id,requestedVisible=requested&&(requestedCurrentStay||requested.checkInAt<buckets.window.endAt&&requested.checkOutAt>buckets.window.startAt)?requested:null,editableInWeek=buckets.withinWeek.filter(item=>!reservationRecordIsPast(item)),existing=requestedVisible||(!reservationId?editableInWeek[0]||null:null),weekPast=reservationWeekIsPast(selectedWeek),readOnly=weekPast&&!requestedCurrentStay||!!existing&&reservationRecordIsPast(existing),needsCurrentStayDetails=!existing&&room.occupancy==='occupied'&&!occupiedReservationEnd(room),currentEntry=requestedCurrent||(!reservationId&&needsCurrentStayDetails),validNewDate=/^\d{4}-\d{2}-\d{2}$/.test(newDate||'')?newDate:'',roomSpecificNew=reservationId==='__new__'&&!!validNewDate,baseDefaultDate=selectedWeek===weekStartIso(state.selectedDate)?state.selectedDate:selectedWeek,defaultDate=validNewDate||(!existing&&!currentEntry&&room.occupancy==='occupied'&&selectedWeek===weekStartIso(state.selectedDate)?suggestedReservationStartDate(room.no):baseDefaultDate),checkinAt=currentEntry?'':existing?.checkInAt||`${defaultDate}T${DEFAULT_CHECKIN_TIME}`,checkoutAt=currentEntry?'':existing?.checkOutAt||`${shiftIsoDate(defaultDate,1)}T${DEFAULT_CHECKOUT_TIME}`,guestPolicy=guestPolicyForRoom(room.no),guestCount=existing?reservationGuestCount(existing):guestPolicy.defaultGuestCount,cancelImpact=existing&&!readOnly?reservationCancellationImpact(existing):null,editingCurrentStay=!!existing&&currentOccupiedReservation(room)?.id===existing.id,historyReservationId=currentEntry?'__current__':isNew?'__new__':existing?.id||'';
  6567 |         const roomOptions=(currentEntry||roomSpecificNew?[room]:ROOMS.filter(item=>item.no===room.no||!quickRoomBlockReason(item)&&(item.occupancy!=='occupied'||!!occupiedReservationEnd(item)))).map(item=>`<option value="${item.no}" ${item.no===room.no?'selected':''}>${item.no}호 · ${esc(ROOM_TYPES[item.type].name)} · ${esc(item.elevator||'미기재')}</option>`).join('');
  6568 |         const scheduleList=reservationWeekScheduleMarkup(room,existing,buckets),nextRegistration=reservationNextRegistrationState(room,existing,buckets);
  6569 |         const managementNotice=existing&&!readOnly?`<div class="field field-full"><div class="notice ${cancelImpact.blockedReason?'notice-warning':'notice-info'}"><div><strong>${cancelImpact.stayStarted?'현재 예약 수정 가능 · 예약 취소 불가':cancelImpact.blockedReason?'예약 취소 불가':'예약정보 수정 또는 취소'}</strong><br>${cancelImpact.stayStarted?'인원수와 일정은 위에서 수정할 수 있습니다. 실제 투숙 종료는 객실 상세의 지금 체크아웃으로 처리하세요.':cancelImpact.blockedReason?esc(cancelImpact.blockedReason):'날짜·시각은 위에서 수정하고, 예약을 없앨 때만 예약 취소를 누르세요.'}</div></div></div>`:'';
  6570 |         const occupiedNotice=!existing&&room.occupancy==='occupied'?`<div class="field field-full"><div class="notice ${currentEntry?'notice-warning':'notice-info'}"><div><strong>${currentEntry?'현재 투숙 정보 입력':'현재 투숙 중 · 다음 예약 등록'}</strong><br>${currentEntry?'실제 체크인과 예정 체크아웃, 숙박 인원을 확인해 입력하세요. 체크아웃을 저장한 뒤 다음 예약을 등록할 수 있습니다.':`${quickDateLabel(occupiedReservationEnd(room).slice(0,10))} ${occupiedReservationEnd(room).slice(11,16)} 체크아웃 이후의 겹치지 않는 일정만 등록할 수 있습니다.`}</div></div></div>`:'';
  6571 |         if(stale)return {room:room.no,reservationId:requestedId,title:`${room.no}호 예약을 다시 확인해 주세요`,subtitle:'열어 둔 예약이 이미 변경되었거나 취소되었습니다.',closeLabel:'닫기',large:true,body:`<div class="notice notice-warning"><div><strong>최신 예약 목록에서 다시 선택해 주세요.</strong></div></div>${scheduleList}`,confirmLabel:'',confirmAction:''};
  6572 |         if(readOnly)return {room:room.no,reservationId:historyReservationId,title:`${room.no}호 지난 예약 기록`,subtitle:`${weekRangeLabel(selectedWeek,true)} · 지난 기록은 수정하거나 취소할 수 없습니다.`,closeLabel:'닫기',large:true,body:scheduleList,confirmLabel:'',confirmAction:''};
  6573 |         return {room:room.no,reservationId:historyReservationId,newDate:!existing&&!currentEntry?defaultDate:'',title:`${room.no}호 ${currentEntry?'현재 투숙 정보 입력':editingCurrentStay?'현재 예약 수정':existing?'예약 상세·변경':'다음 예약 등록'}`,subtitle:'체크인부터 체크아웃까지 한 고객의 일정을 입력합니다.',closeLabel:'닫기',secondaryLabel:existing&&!cancelImpact.blockedReason?'예약 취소':'',secondaryAction:existing&&!cancelImpact.blockedReason?'reservation-cancel-review':'',secondaryVariant:'danger',secondaryExtra:existing?`data-id="${esc(existing.id)}" data-fingerprint="${esc(reservationFingerprint(existing))}"`:'',auxiliaryLabel:nextRegistration.canAdd?'다음 예약 등록':'',auxiliaryAction:nextRegistration.canAdd?'reservation-add':'',auxiliaryVariant:'outline',auxiliaryExtra:nextRegistration.canAdd?`data-room="${room.no}" data-date="${nextRegistration.nextDate}"`:'',large:true,body:`<form id="reservation-form" class="form-grid"><input id="res-id" type="hidden" value="${esc(existing?.id||'')}"><input id="res-fingerprint" type="hidden" value="${esc(reservationFingerprint(existing))}"><input id="res-current-stay" type="hidden" value="${currentEntry?'1':'0'}"><div class="reservation-primary-row field-full"><div class="field"><label for="res-room">객실</label><select id="res-room" class="select-control" data-control="reservation-room" ${existing||currentEntry||roomSpecificNew?'disabled aria-disabled="true"':''}>${roomOptions}</select><small>${existing?'기존 예약의 객실은 변경하지 않습니다.':currentEntry?'현재 투숙 객실을 입력합니다.':roomSpecificNew?'선택한 객실의 다음 예약을 등록합니다.':'예약 가능한 객실만 표시합니다.'}</small></div><div class="field"><span class="label" id="res-guests-label">인원수</span><input id="res-guests" type="hidden" value="${guestCount}"><div class="reservation-guest-stepper" id="reservation-guest-stepper" role="group" tabindex="-1" aria-labelledby="res-guests-label" aria-describedby="res-guests-value res-guests-help" data-max="${guestPolicy.maxGuestCount}"><button type="button" data-action="reservation-guest-change" data-delta="-1" aria-label="${room.no}호 예약 인원수 1명 줄이기" ${guestCount<=1?'disabled':''}>−</button><output class="reservation-guest-value" id="res-guests-value" aria-live="polite" aria-atomic="true">${guestCount}명</output><button type="button" data-action="reservation-guest-change" data-delta="1" aria-label="${room.no}호 예약 인원수 1명 늘리기, 최대 ${guestPolicy.maxGuestCount}명" ${guestCount>=guestPolicy.maxGuestCount?'disabled':''}>+</button></div><small id="res-guests-help">기본 ${guestPolicy.defaultGuestCount}명 · 최대 ${guestPolicy.maxGuestCount}명</small></div></div><div class="field"><label for="res-checkin">1. 체크인 일시</label><input id="res-checkin" class="input-control" type="datetime-local" step="3600" value="${esc(checkinAt)}" required><small>${currentEntry?'실제 투숙 시작 일시를 입력하세요.':'기본 16:00 · 이보다 빠르면 얼리 체크인'}</small></div><div class="field"><label for="res-checkout">2. 체크아웃 일시</label><input id="res-checkout" class="input-control" type="datetime-local" step="3600" value="${esc(checkoutAt)}" required><small>${currentEntry?'예정 체크아웃 일시를 입력하세요.':'기본 11:00 · 이보다 늦으면 레이트 체크아웃'}</small></div>${reservationPreviewMarkup(checkinAt,checkoutAt)}${occupiedNotice}${managementNotice}${scheduleList}</form>`,confirmLabel:currentEntry?'현재 투숙 정보 저장':existing?'예약정보 수정 저장':'예약 접수',confirmAction:'save-reservation-v2'};
  6574 |       }
  6575 |       function openReservation(roomNo='211',reservationId='',options={}) {
  6576 |         const room=ROOMS.find(item=>item.no===String(roomNo))||ROOMS[0],requested=reservationId&&!['__new__','__current__',''].includes(reservationId)?state.reservations.find(item=>item.id===reservationId)||null:null,allRoomRecords=(state.reservations||[]).filter(item=>item.room===room.no),upcoming=activeReservationsFor(state,room.no).filter(item=>!reservationRecordIsPast(item)),latestRecord=[...allRoomRecords].sort((left,right)=>(right.cancelledAt||right.updatedAt||right.checkOutAt).localeCompare(left.cancelledAt||left.updatedAt||left.checkOutAt))[0]||null;
  6577 |         if(options.weekStart)state.reservationWeekStart=weekStartIso(options.weekStart);
  6578 |         else if(requested){const requestDate=!reservationRecordIsPast(requested)&&requested.checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:requested.checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6579 |         else if(reservationId==='__new__')state.reservationWeekStart=weekStartIso(options.newDate||state.selectedDate);
  6580 |         else if(reservationId==='__current__')state.reservationWeekStart=weekStartIso(state.selectedDate);
  6581 |         else if(upcoming[0]){reservationId=upcoming[0].id;const requestDate=upcoming[0].checkInAt.slice(0,10)<=state.selectedDate?state.selectedDate:upcoming[0].checkInAt.slice(0,10);state.reservationWeekStart=weekStartIso(requestDate);}
  6582 |         else if(latestRecord){reservationId=latestRecord.id;state.reservationWeekStart=weekStartIso(latestRecord.checkInAt.slice(0,10));}
  6583 |         else state.reservationWeekStart=weekStartIso(state.selectedDate);
  6584 |         state.reservationWeekRoom=room.no;
  6585 |         const config=reservationModalConfig(roomNo,reservationId,options.newDate||'');
  6586 |         const replacingReservationModal=!options.historyStack&&history.state?.layer==='modal'&&history.state?.modalKind==='reservation'&&document.getElementById('modal-root')?.hasChildNodes(),trigger=options.trigger||replacingReservationModal&&modalTrigger||document.activeElement;
  6587 |         showModal({...config,trigger,historyStack:!!options.historyStack,historyKind:'reservation',historyPayload:{room:config.room,weekStart:state.reservationWeekStart,...(config.reservationId?{reservationId:config.reservationId}:{}),...(config.newDate?{newDate:config.newDate}:{})}});
  6588 |       }
  6589 |       function openReservationCancellationReview(reservationId,expectedFingerprint,trigger=document.activeElement) {
```

### occurrence 4 · line 6946

```html
  6901 |         if(a==='template-review'){if(!adminCanMutate())return;openTemplateReview(id);return;}
  6902 |         if(a==='template-save'){
  6903 |           if(!adminCanMutate()){closeModal();render();toast('관리자 권한 또는 최신 상태가 바뀌어 템플릿을 저장하지 않았습니다.','error');return;}
  6904 |           const change=pendingTemplateChange,template=change&&templateById(change.id);if(!template||change.id!==id)return;
  6905 |           const previous={version:template.version,savedAt:template.lastSaved,minutes:template.minutes};
  6906 |           template.history.unshift(previous);template.version=`v${Number(template.version.replace(/\D/g,''))+1}`;template.minutes=change.minutes;template.lastSaved=`2026.08.18 ${state.time}`;state.template=`published ${template.version}`;
  6907 |           appendEvent(`${ROOM_TYPES[template.typeId].name} · ${template.name} ${template.version} 저장`,'기존 작업 스냅샷 유지 · 새 작업부터 적용 · 데모');pendingTemplateChange=null;closeModal();state.detail={type:'template',id:template.id,mode:'view'};render();toast(`${template.version}을 활성화했습니다. 기존 작업은 변경되지 않습니다.`);return;
  6908 |         }
  6909 |         if(a==='inspection-photo'){openInspectionPhoto(el.dataset.room,el.dataset.submission,el.dataset.photo,el);return;}
  6910 |         if(a==='bomb-room-photo'){openBombRoomPhoto(el.dataset.room,el.dataset.report,el.dataset.photo,el);return;}
  6911 |         if(a==='choose-bomb-room-files'){
  6912 |           const no=el.dataset.room;
  6913 |           if(!maidCanCreateBombRoomReport(no)){toast('본인 담당 객실의 전체 제출 전 단계에서만 폭탄방 증빙을 선택할 수 있습니다.','error');return;}
  6914 |           document.getElementById(`bomb-room-files-${no}`)?.click();return;
  6915 |         }
  6916 |         if(a==='remove-bomb-room-photo'){
  6917 |           const no=el.dataset.room,draft=bombRoomDraft(no);
  6918 |           if(!maidCanCreateBombRoomReport(no)){toast('지금은 선택한 폭탄방 증빙을 변경할 수 없습니다.','error');return;}
  6919 |           const index=draft.photos.findIndex(photo=>photo.id===el.dataset.photo);if(index<0)return;
  6920 |           releaseRoomIssuePhoto(draft.photos[index]);draft.photos.splice(index,1);render();focusAfterRender(`[data-action="choose-bomb-room-files"][data-room="${no}"]`);toast('선택한 폭탄방 증빙 한 장을 제거했습니다.');return;
  6921 |         }
  6922 |         if(a==='add-demo-bomb-room-photos'){
  6923 |           const no=el.dataset.room,draft=bombRoomDraft(no);
  6924 |           if(!maidCanCreateBombRoomReport(no)){toast('지금은 폭탄방 증빙을 추가할 수 없습니다.','error');return;}
  6925 |           const stamp=Date.now();['bed','bath'].forEach((fixture,index)=>draft.photos.push({id:`bomb-demo-${stamp}-${index}`,label:`선택한 증빙 ${draft.photos.length+1}`,image:{...demoUploadImageFixture(fixture)},size:286000+index*31000,type:'image/jpeg'}));
  6926 |           render();focusAfterRender(`[data-action="save-bomb-room-report"][data-room="${no}"]`);toast('폭탄방 증빙 데모 이미지 2장을 추가했습니다.');return;
  6927 |         }
  6928 |         if(a==='save-bomb-room-report'){
  6929 |           const no=el.dataset.room,job=state.jobs[no],draft=bombRoomDraft(no),note=draft.note.trim();
  6930 |           if(!maidCanCreateBombRoomReport(no)){toast('이미 신고했거나 전체 제출이 끝나 폭탄방 신고를 저장할 수 없습니다.','error');return;}
  6931 |           if(!draft.photos.length){toast('폭탄방 신고에는 이미지가 최소 1장 필요합니다.','error');document.querySelector(`[data-action="choose-bomb-room-files"][data-room="${no}"]`)?.focus();return;}
  6932 |           if(containsRoomIssuePersonalData(note)){toast('연락처·이메일 같은 개인정보를 삭제한 뒤 신고하세요.','error');document.getElementById(`bomb-room-note-${no}`)?.focus();return;}
  6933 |           const task=taskState(no),attempt=state.cleaningAttempts?.[task.attemptId],identity={performerId:attempt.performerId,performerName:attempt.performerName},report={id:`bomb-${no}-${Date.now()}`,attemptId:attempt.id,submissionId:null,room:no,status:'pending',reportedStage:bombRoomStageLabel(job),reportedAt:`${attemptWorkDate(attempt,state.selectedDate)} ${state.time}`,reportedBy:identity.performerName,reportedById:identity.performerId,note,baseRateSnapshot:cleaningBaseRate(no,null,attempt.baseRateSnapshot),submittedVersion:null,decidedAt:null,decidedBy:null,decisionReason:'',photos:draft.photos.map((photo,index)=>({...photo,label:`폭탄방 증빙 ${index+1}`}))};
  6934 |           state.bombRoomReports[report.id]=report;state.currentBombReportByRoom[no]=report.id;draft.note='';draft.photos=[];appendEvent(`${no}호 폭탄방 신고`,`${report.attemptId} · ${report.reportedStage} · 이미지 ${report.photos.length}장 · 해당 객실 ${money(report.baseRateSnapshot)} 승인 시 ${money(report.baseRateSnapshot*2)}`,{maidIds:[report.reportedById]});render();focusAfterRender(`[data-action="bomb-room-photo"][data-room="${no}"]`);toast(`${no}호 폭탄방 신고를 관리자 검수에 공유했습니다.`);return;
  6935 |         }
  6936 |         if(a==='approve-bomb-room'||a==='reject-bomb-room'){openBombRoomDecision(a==='approve-bomb-room'?'approve':'reject',id,el);return;}
  6937 |         if(a==='confirm-approve-bomb-room'){
  6938 |           const submission=currentSubmission(id),report=submittedBombRoomReport(id);if(state.role!=='admin'||state.inspections[id]!=='pending'||state.jobs[id]!=='inspection'||submission?.id!==el.dataset.submission||submission?.status!=='pending'||report?.id!==el.dataset.report||report?.submissionId!==submission.id||report?.status!=='pending'||isLocked()){closeModal();render();toast('폭탄방 신고 또는 동기화 상태가 바뀌어 승인하지 않았습니다.','error');return;}
  6939 |           report.status='approved';report.decidedAt=`${state.selectedDate} ${state.time}`;report.decidedBy='관리자';report.decisionReason='이미지 증빙 확인 · 폭탄방 인정';appendEvent(`${id}호 폭탄방 승인`,`${money(report.baseRateSnapshot)} + 추가 ${money(report.baseRateSnapshot)} = 해당 객실 ${money(report.baseRateSnapshot*2)}`,{maidIds:[report.reportedById]});closeModal();render();focusAfterRender(`[data-action="approve-inspection-v2"][data-id="${id}"]`);toast('해당 객실의 폭탄방 추가요금을 승인했습니다.');return;
  6940 |         }
  6941 |         if(a==='confirm-reject-bomb-room'){
  6942 |           const submission=currentSubmission(id),report=submittedBombRoomReport(id),reason=document.getElementById('bomb-room-reject-reason')?.value.trim()||'';if(!reason){toast('폭탄방 미인정 사유를 입력하세요.','error');document.getElementById('bomb-room-reject-reason')?.focus();return;}
  6943 |           if(state.role!=='admin'||state.inspections[id]!=='pending'||state.jobs[id]!=='inspection'||submission?.id!==el.dataset.submission||submission?.status!=='pending'||report?.id!==el.dataset.report||report?.submissionId!==submission.id||report?.status!=='pending'||isLocked()){closeModal();render();toast('폭탄방 신고 또는 동기화 상태가 바뀌어 결정하지 않았습니다.','error');return;}
  6944 |           report.status='rejected';report.decidedAt=`${state.selectedDate} ${state.time}`;report.decidedBy='관리자';report.decisionReason=reason;appendEvent(`${id}호 폭탄방 미인정`,`${reason} · 해당 객실 기본 ${money(report.baseRateSnapshot)} 적용`,{maidIds:[report.reportedById]});closeModal();render();focusAfterRender(`[data-action="approve-inspection-v2"][data-id="${id}"]`);toast('폭탄방 미인정 사유를 기록했습니다.');return;
  6945 |         }
  6946 |         if(a==='room-issue-photo'){openRoomIssuePhoto(el.dataset.room,el.dataset.issue,el.dataset.photo,el);return;}
  6947 |         if(a==='choose-room-issue-files'){
  6948 |           const no=el.dataset.room;
  6949 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 특이사항 이미지를 선택할 수 있습니다.','error');return;}
  6950 |           document.getElementById(`room-issue-files-${no}`)?.click();return;
  6951 |         }
  6952 |         if(a==='remove-room-issue-photo'){
  6953 |           const no=el.dataset.room,draft=roomIssueDraft(no);
  6954 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 선택 이미지를 제거할 수 있습니다.','error');return;}
  6955 |           const index=draft.photos.findIndex(photo=>photo.id===el.dataset.photo);if(index<0)return;
  6956 |           releaseRoomIssuePhoto(draft.photos[index]);draft.photos.splice(index,1);render();focusAfterRender(`[data-action="choose-room-issue-files"][data-room="${no}"]`);toast('선택한 이미지 한 장을 제거했습니다.');return;
  6957 |         }
  6958 |         if(a==='save-room-issue'){
  6959 |           const no=el.dataset.room,draft=roomIssueDraft(no),note=draft.note.trim();
  6960 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 특이사항을 등록할 수 있습니다.','error');return;}
  6961 |           if(!note&&!draft.photos.length){toast('업무 메모나 이미지 중 하나 이상을 입력하세요.','error');return;}
  6962 |           if(containsRoomIssuePersonalData(note)){toast('연락처·이메일 같은 개인정보를 삭제한 뒤 등록하세요.','error');document.getElementById(`room-issue-note-${no}`)?.focus();return;}
  6963 |           const attempt=state.cleaningAttempts?.[taskState(no).attemptId],record={id:`ri-${no}-${Date.now()}`,room:no,attemptId:attempt?.id||null,submissionId:null,type:draft.type||(!note?'사진 기록':'기타'),blocksCheckin:draft.type==='시설 고장',note,createdBy:attempt?.performerName||'김민지1',createdById:attempt?.performerId||'m1',createdAt:`${state.selectedDate} ${state.time}`,status:'open',photos:draft.photos.map((photo,index)=>({...photo,label:`특이사항 사진 ${index+1}`}))};
  6964 |           ensureRoomIssueRecords(no).unshift(record);draft.type='';draft.note='';draft.photos=[];appendEvent(`${no}호 객실 특이사항 등록`,`${record.type} · 사진 ${record.photos.length}장 · 관리자 확인 대기`,{maidIds:[record.createdById]});render();focusAfterRender(record.photos.length?`[data-room-issue="${record.id}"] [data-action="room-issue-photo"]`:`[data-action="choose-room-issue-files"][data-room="${no}"]`);toast(`객실 특이사항과 이미지 ${record.photos.length}장을 관리자에게 공유했습니다.`);return;
  6965 |         }
  6966 |         if(a==='open-room-export'){openRoomExport(el);return;}
  6967 |         if(a==='export-rooms-csv'){downloadRoomExport('csv');return;}
  6968 |         if(a==='export-rooms-xls'){downloadRoomExport('xlsx');return;}
  6969 |         if(a==='open-calendar'){openCalendar(el,'room');return;}
  6970 |         if(a==='open-pay-calendar'){
  6971 |           const context=el.dataset.context==='maid-pay'?'maid-pay':'admin-pay';
  6972 |           const selected=context==='maid-pay'?(state.maidPaySelectedWeek||state.maidPayOpenWeek||'2026-08-03'):(state.adminPayWeek||'2026-08-03');
  6973 |           state.calendarMonth=selected.slice(0,7);openCalendar(el,context);return;
  6974 |         }
  6975 |         if(a==='open-work-history-calendar'){if(!workHistoryCalendarAllowed()){toast('관리자 근무 기록 화면에서만 주차를 선택할 수 있습니다.','error');return;}state.calendarMonth=state.workHistoryWeek.slice(0,7);openCalendar(el,'work-history');return;}
  6976 |         if(a==='calendar-month'){const [y,m]=state.calendarMonth.split('-').map(Number),d=new Date(y,m-1+Number(el.dataset.offset),1);state.calendarMonth=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;rerenderCalendar();return;}
  6977 |         if(a==='calendar-select'){
  6978 |           const context=state.calendarContext;
  6979 |           if(context==='reservation-week'){
  6980 |             const start=weekStartIso(el.dataset.date),room=state.reservationWeekRoom||'211';state.reservationWeekStart=start;state.calendarMonth=start.slice(0,7);state.calendarContext=null;reservationWeekHistoryOverride={room:String(room),weekStart:start};dismissModal();toast(`${weekRangeLabel(start)} 예약을 표시합니다.`);return;
  6981 |           }
  6982 |           if(context==='admin-pay'||context==='maid-pay'||context==='work-history'){
  6983 |             if(context==='work-history'&&!workHistoryCalendarAllowed()){closeModal();state.calendarContext=null;render();toast('관리자 근무 기록 화면에서만 주차를 바꿀 수 있습니다.','error');return;}
  6984 |             const start=context==='work-history'?normalizeWorkHistoryWeek(el.dataset.date):weekStartIso(el.dataset.date);
  6985 |             if(!start){toast('선택할 수 없는 주차입니다.','error');return;}
  6986 |             if(context==='admin-pay')state.adminPayWeek=start;
  6987 |             else if(context==='maid-pay'){state.maidPaySelectedWeek=start;state.maidPayOpenWeek=start;state.maidPayFilter='all';}
  6988 |             else state.workHistoryWeek=start;
  6989 |             closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector(context==='work-history'?'[data-action="open-work-history-calendar"]':`[data-action="open-pay-calendar"][data-context="${context}"]`)?.focus());toast(`${weekRangeLabel(start)} ${context==='work-history'?'근무 기록':'지급 이력'}을 표시합니다.`);return;
  6990 |           }
  6991 |           applyOperationalDate(state,el.dataset.date);closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector('[data-action="open-calendar"]')?.focus());toast(`${dateLabel()} 현황을 표시합니다.`);return;
  6992 |         }
  6993 |         if(a==='calendar-today'){
  6994 |           const context=state.calendarContext;
  6995 |           if(context==='reservation-week'){
  6996 |             const start=weekStartIso(state.selectedDate),room=state.reservationWeekRoom||'211';state.reservationWeekStart=start;state.calendarMonth=start.slice(0,7);state.calendarContext=null;reservationWeekHistoryOverride={room:String(room),weekStart:start};dismissModal();return;
  6997 |           }
  6998 |           if(context==='admin-pay'||context==='maid-pay'||context==='work-history'){
  6999 |             if(context==='work-history'&&!workHistoryCalendarAllowed()){closeModal();state.calendarContext=null;render();toast('관리자 근무 기록 화면에서만 주차를 바꿀 수 있습니다.','error');return;}
  7000 |             const start='2026-08-10';
  7001 |             if(context==='admin-pay')state.adminPayWeek=start;
  7002 |             else if(context==='maid-pay'){state.maidPaySelectedWeek=start;state.maidPayOpenWeek=start;state.maidPayFilter='all';}
  7003 |             else state.workHistoryWeek=start;
  7004 |             closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector(context==='work-history'?'[data-action="open-work-history-calendar"]':`[data-action="open-pay-calendar"][data-context="${context}"]`)?.focus());return;
  7005 |           }
  7006 |           applyOperationalDate(state,'2026-08-15');closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector('[data-action="open-calendar"]')?.focus());return;
  7007 |         }
  7008 |         if(a==='date-shift'){const d=dateObject();d.setDate(d.getDate()+Number(el.dataset.offset));applyOperationalDate(state,dateIso(d));render();requestAnimationFrame(()=>document.querySelector(`[data-action="date-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;}
  7009 |         if(a==='date-today'){applyOperationalDate(state,'2026-08-15');render();requestAnimationFrame(()=>document.querySelector('[data-action="date-today"]')?.focus());return;}
  7010 |         if(a==='toggle-section'){const key=el.dataset.key;state.todaySections[key]=!state.todaySections[key];render();requestAnimationFrame(()=>document.querySelector(`[data-action="toggle-section"][data-key="${key}"]`)?.focus());return;}
  7011 |         if(a==='clear-room-filters'){state.roomSearch='';state.roomTypeFilter='all';state.roomFilter='all';state.listMode='data';render();focusAfterRender('[data-control="room-filter"]');return;}
  7012 |         if(a==='edit-room-info'){openRoomInfoEditor(id,el);return;}
  7013 |         if(a==='save-room-info'){
  7014 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',type=document.getElementById('room-info-type')?.value||'',elevator=document.getElementById('room-info-elevator')?.value??'',wasHeld=roomIsOnHold(id),occupancy=document.getElementById('room-info-occupancy')?.value||'';
  7015 |           if(!adminCanMutate()||!room||roomMasterFingerprint(room)!==expected){closeModal();render();toast('객실 정보 또는 관리자 상태가 바뀌어 저장하지 않았습니다. 다시 확인하세요.','error');return;}
```

### occurrence 5 · line 6966

```html
  6921 |         }
  6922 |         if(a==='add-demo-bomb-room-photos'){
  6923 |           const no=el.dataset.room,draft=bombRoomDraft(no);
  6924 |           if(!maidCanCreateBombRoomReport(no)){toast('지금은 폭탄방 증빙을 추가할 수 없습니다.','error');return;}
  6925 |           const stamp=Date.now();['bed','bath'].forEach((fixture,index)=>draft.photos.push({id:`bomb-demo-${stamp}-${index}`,label:`선택한 증빙 ${draft.photos.length+1}`,image:{...demoUploadImageFixture(fixture)},size:286000+index*31000,type:'image/jpeg'}));
  6926 |           render();focusAfterRender(`[data-action="save-bomb-room-report"][data-room="${no}"]`);toast('폭탄방 증빙 데모 이미지 2장을 추가했습니다.');return;
  6927 |         }
  6928 |         if(a==='save-bomb-room-report'){
  6929 |           const no=el.dataset.room,job=state.jobs[no],draft=bombRoomDraft(no),note=draft.note.trim();
  6930 |           if(!maidCanCreateBombRoomReport(no)){toast('이미 신고했거나 전체 제출이 끝나 폭탄방 신고를 저장할 수 없습니다.','error');return;}
  6931 |           if(!draft.photos.length){toast('폭탄방 신고에는 이미지가 최소 1장 필요합니다.','error');document.querySelector(`[data-action="choose-bomb-room-files"][data-room="${no}"]`)?.focus();return;}
  6932 |           if(containsRoomIssuePersonalData(note)){toast('연락처·이메일 같은 개인정보를 삭제한 뒤 신고하세요.','error');document.getElementById(`bomb-room-note-${no}`)?.focus();return;}
  6933 |           const task=taskState(no),attempt=state.cleaningAttempts?.[task.attemptId],identity={performerId:attempt.performerId,performerName:attempt.performerName},report={id:`bomb-${no}-${Date.now()}`,attemptId:attempt.id,submissionId:null,room:no,status:'pending',reportedStage:bombRoomStageLabel(job),reportedAt:`${attemptWorkDate(attempt,state.selectedDate)} ${state.time}`,reportedBy:identity.performerName,reportedById:identity.performerId,note,baseRateSnapshot:cleaningBaseRate(no,null,attempt.baseRateSnapshot),submittedVersion:null,decidedAt:null,decidedBy:null,decisionReason:'',photos:draft.photos.map((photo,index)=>({...photo,label:`폭탄방 증빙 ${index+1}`}))};
  6934 |           state.bombRoomReports[report.id]=report;state.currentBombReportByRoom[no]=report.id;draft.note='';draft.photos=[];appendEvent(`${no}호 폭탄방 신고`,`${report.attemptId} · ${report.reportedStage} · 이미지 ${report.photos.length}장 · 해당 객실 ${money(report.baseRateSnapshot)} 승인 시 ${money(report.baseRateSnapshot*2)}`,{maidIds:[report.reportedById]});render();focusAfterRender(`[data-action="bomb-room-photo"][data-room="${no}"]`);toast(`${no}호 폭탄방 신고를 관리자 검수에 공유했습니다.`);return;
  6935 |         }
  6936 |         if(a==='approve-bomb-room'||a==='reject-bomb-room'){openBombRoomDecision(a==='approve-bomb-room'?'approve':'reject',id,el);return;}
  6937 |         if(a==='confirm-approve-bomb-room'){
  6938 |           const submission=currentSubmission(id),report=submittedBombRoomReport(id);if(state.role!=='admin'||state.inspections[id]!=='pending'||state.jobs[id]!=='inspection'||submission?.id!==el.dataset.submission||submission?.status!=='pending'||report?.id!==el.dataset.report||report?.submissionId!==submission.id||report?.status!=='pending'||isLocked()){closeModal();render();toast('폭탄방 신고 또는 동기화 상태가 바뀌어 승인하지 않았습니다.','error');return;}
  6939 |           report.status='approved';report.decidedAt=`${state.selectedDate} ${state.time}`;report.decidedBy='관리자';report.decisionReason='이미지 증빙 확인 · 폭탄방 인정';appendEvent(`${id}호 폭탄방 승인`,`${money(report.baseRateSnapshot)} + 추가 ${money(report.baseRateSnapshot)} = 해당 객실 ${money(report.baseRateSnapshot*2)}`,{maidIds:[report.reportedById]});closeModal();render();focusAfterRender(`[data-action="approve-inspection-v2"][data-id="${id}"]`);toast('해당 객실의 폭탄방 추가요금을 승인했습니다.');return;
  6940 |         }
  6941 |         if(a==='confirm-reject-bomb-room'){
  6942 |           const submission=currentSubmission(id),report=submittedBombRoomReport(id),reason=document.getElementById('bomb-room-reject-reason')?.value.trim()||'';if(!reason){toast('폭탄방 미인정 사유를 입력하세요.','error');document.getElementById('bomb-room-reject-reason')?.focus();return;}
  6943 |           if(state.role!=='admin'||state.inspections[id]!=='pending'||state.jobs[id]!=='inspection'||submission?.id!==el.dataset.submission||submission?.status!=='pending'||report?.id!==el.dataset.report||report?.submissionId!==submission.id||report?.status!=='pending'||isLocked()){closeModal();render();toast('폭탄방 신고 또는 동기화 상태가 바뀌어 결정하지 않았습니다.','error');return;}
  6944 |           report.status='rejected';report.decidedAt=`${state.selectedDate} ${state.time}`;report.decidedBy='관리자';report.decisionReason=reason;appendEvent(`${id}호 폭탄방 미인정`,`${reason} · 해당 객실 기본 ${money(report.baseRateSnapshot)} 적용`,{maidIds:[report.reportedById]});closeModal();render();focusAfterRender(`[data-action="approve-inspection-v2"][data-id="${id}"]`);toast('폭탄방 미인정 사유를 기록했습니다.');return;
  6945 |         }
  6946 |         if(a==='room-issue-photo'){openRoomIssuePhoto(el.dataset.room,el.dataset.issue,el.dataset.photo,el);return;}
  6947 |         if(a==='choose-room-issue-files'){
  6948 |           const no=el.dataset.room;
  6949 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 특이사항 이미지를 선택할 수 있습니다.','error');return;}
  6950 |           document.getElementById(`room-issue-files-${no}`)?.click();return;
  6951 |         }
  6952 |         if(a==='remove-room-issue-photo'){
  6953 |           const no=el.dataset.room,draft=roomIssueDraft(no);
  6954 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 선택 이미지를 제거할 수 있습니다.','error');return;}
  6955 |           const index=draft.photos.findIndex(photo=>photo.id===el.dataset.photo);if(index<0)return;
  6956 |           releaseRoomIssuePhoto(draft.photos[index]);draft.photos.splice(index,1);render();focusAfterRender(`[data-action="choose-room-issue-files"][data-room="${no}"]`);toast('선택한 이미지 한 장을 제거했습니다.');return;
  6957 |         }
  6958 |         if(a==='save-room-issue'){
  6959 |           const no=el.dataset.room,draft=roomIssueDraft(no),note=draft.note.trim();
  6960 |           if(!maidCanEditRoomIssue(no)){toast('본인 담당 객실을 청소 중일 때만 특이사항을 등록할 수 있습니다.','error');return;}
  6961 |           if(!note&&!draft.photos.length){toast('업무 메모나 이미지 중 하나 이상을 입력하세요.','error');return;}
  6962 |           if(containsRoomIssuePersonalData(note)){toast('연락처·이메일 같은 개인정보를 삭제한 뒤 등록하세요.','error');document.getElementById(`room-issue-note-${no}`)?.focus();return;}
  6963 |           const attempt=state.cleaningAttempts?.[taskState(no).attemptId],record={id:`ri-${no}-${Date.now()}`,room:no,attemptId:attempt?.id||null,submissionId:null,type:draft.type||(!note?'사진 기록':'기타'),blocksCheckin:draft.type==='시설 고장',note,createdBy:attempt?.performerName||'김민지1',createdById:attempt?.performerId||'m1',createdAt:`${state.selectedDate} ${state.time}`,status:'open',photos:draft.photos.map((photo,index)=>({...photo,label:`특이사항 사진 ${index+1}`}))};
  6964 |           ensureRoomIssueRecords(no).unshift(record);draft.type='';draft.note='';draft.photos=[];appendEvent(`${no}호 객실 특이사항 등록`,`${record.type} · 사진 ${record.photos.length}장 · 관리자 확인 대기`,{maidIds:[record.createdById]});render();focusAfterRender(record.photos.length?`[data-room-issue="${record.id}"] [data-action="room-issue-photo"]`:`[data-action="choose-room-issue-files"][data-room="${no}"]`);toast(`객실 특이사항과 이미지 ${record.photos.length}장을 관리자에게 공유했습니다.`);return;
  6965 |         }
  6966 |         if(a==='open-room-export'){openRoomExport(el);return;}
  6967 |         if(a==='export-rooms-csv'){downloadRoomExport('csv');return;}
  6968 |         if(a==='export-rooms-xls'){downloadRoomExport('xlsx');return;}
  6969 |         if(a==='open-calendar'){openCalendar(el,'room');return;}
  6970 |         if(a==='open-pay-calendar'){
  6971 |           const context=el.dataset.context==='maid-pay'?'maid-pay':'admin-pay';
  6972 |           const selected=context==='maid-pay'?(state.maidPaySelectedWeek||state.maidPayOpenWeek||'2026-08-03'):(state.adminPayWeek||'2026-08-03');
  6973 |           state.calendarMonth=selected.slice(0,7);openCalendar(el,context);return;
  6974 |         }
  6975 |         if(a==='open-work-history-calendar'){if(!workHistoryCalendarAllowed()){toast('관리자 근무 기록 화면에서만 주차를 선택할 수 있습니다.','error');return;}state.calendarMonth=state.workHistoryWeek.slice(0,7);openCalendar(el,'work-history');return;}
  6976 |         if(a==='calendar-month'){const [y,m]=state.calendarMonth.split('-').map(Number),d=new Date(y,m-1+Number(el.dataset.offset),1);state.calendarMonth=`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}`;rerenderCalendar();return;}
  6977 |         if(a==='calendar-select'){
  6978 |           const context=state.calendarContext;
  6979 |           if(context==='reservation-week'){
  6980 |             const start=weekStartIso(el.dataset.date),room=state.reservationWeekRoom||'211';state.reservationWeekStart=start;state.calendarMonth=start.slice(0,7);state.calendarContext=null;reservationWeekHistoryOverride={room:String(room),weekStart:start};dismissModal();toast(`${weekRangeLabel(start)} 예약을 표시합니다.`);return;
  6981 |           }
  6982 |           if(context==='admin-pay'||context==='maid-pay'||context==='work-history'){
  6983 |             if(context==='work-history'&&!workHistoryCalendarAllowed()){closeModal();state.calendarContext=null;render();toast('관리자 근무 기록 화면에서만 주차를 바꿀 수 있습니다.','error');return;}
  6984 |             const start=context==='work-history'?normalizeWorkHistoryWeek(el.dataset.date):weekStartIso(el.dataset.date);
  6985 |             if(!start){toast('선택할 수 없는 주차입니다.','error');return;}
  6986 |             if(context==='admin-pay')state.adminPayWeek=start;
  6987 |             else if(context==='maid-pay'){state.maidPaySelectedWeek=start;state.maidPayOpenWeek=start;state.maidPayFilter='all';}
  6988 |             else state.workHistoryWeek=start;
  6989 |             closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector(context==='work-history'?'[data-action="open-work-history-calendar"]':`[data-action="open-pay-calendar"][data-context="${context}"]`)?.focus());toast(`${weekRangeLabel(start)} ${context==='work-history'?'근무 기록':'지급 이력'}을 표시합니다.`);return;
  6990 |           }
  6991 |           applyOperationalDate(state,el.dataset.date);closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector('[data-action="open-calendar"]')?.focus());toast(`${dateLabel()} 현황을 표시합니다.`);return;
  6992 |         }
  6993 |         if(a==='calendar-today'){
  6994 |           const context=state.calendarContext;
  6995 |           if(context==='reservation-week'){
  6996 |             const start=weekStartIso(state.selectedDate),room=state.reservationWeekRoom||'211';state.reservationWeekStart=start;state.calendarMonth=start.slice(0,7);state.calendarContext=null;reservationWeekHistoryOverride={room:String(room),weekStart:start};dismissModal();return;
  6997 |           }
  6998 |           if(context==='admin-pay'||context==='maid-pay'||context==='work-history'){
  6999 |             if(context==='work-history'&&!workHistoryCalendarAllowed()){closeModal();state.calendarContext=null;render();toast('관리자 근무 기록 화면에서만 주차를 바꿀 수 있습니다.','error');return;}
  7000 |             const start='2026-08-10';
  7001 |             if(context==='admin-pay')state.adminPayWeek=start;
  7002 |             else if(context==='maid-pay'){state.maidPaySelectedWeek=start;state.maidPayOpenWeek=start;state.maidPayFilter='all';}
  7003 |             else state.workHistoryWeek=start;
  7004 |             closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector(context==='work-history'?'[data-action="open-work-history-calendar"]':`[data-action="open-pay-calendar"][data-context="${context}"]`)?.focus());return;
  7005 |           }
  7006 |           applyOperationalDate(state,'2026-08-15');closeModal();state.calendarContext=null;render();requestAnimationFrame(()=>document.querySelector('[data-action="open-calendar"]')?.focus());return;
  7007 |         }
  7008 |         if(a==='date-shift'){const d=dateObject();d.setDate(d.getDate()+Number(el.dataset.offset));applyOperationalDate(state,dateIso(d));render();requestAnimationFrame(()=>document.querySelector(`[data-action="date-shift"][data-offset="${el.dataset.offset}"]`)?.focus());return;}
  7009 |         if(a==='date-today'){applyOperationalDate(state,'2026-08-15');render();requestAnimationFrame(()=>document.querySelector('[data-action="date-today"]')?.focus());return;}
  7010 |         if(a==='toggle-section'){const key=el.dataset.key;state.todaySections[key]=!state.todaySections[key];render();requestAnimationFrame(()=>document.querySelector(`[data-action="toggle-section"][data-key="${key}"]`)?.focus());return;}
  7011 |         if(a==='clear-room-filters'){state.roomSearch='';state.roomTypeFilter='all';state.roomFilter='all';state.listMode='data';render();focusAfterRender('[data-control="room-filter"]');return;}
  7012 |         if(a==='edit-room-info'){openRoomInfoEditor(id,el);return;}
  7013 |         if(a==='save-room-info'){
  7014 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',type=document.getElementById('room-info-type')?.value||'',elevator=document.getElementById('room-info-elevator')?.value??'',wasHeld=roomIsOnHold(id),occupancy=document.getElementById('room-info-occupancy')?.value||'';
  7015 |           if(!adminCanMutate()||!room||roomMasterFingerprint(room)!==expected){closeModal();render();toast('객실 정보 또는 관리자 상태가 바뀌어 저장하지 않았습니다. 다시 확인하세요.','error');return;}
  7016 |           if(!ROOM_TYPES[type]||!['','A','B','C'].includes(elevator)){toast('객실 타입과 엘리베이터 값을 다시 확인하세요.','error');return;}
  7017 |           const overCapacity=activeReservationsFor(state,id).find(reservation=>!reservationRecordIsPast(reservation)&&reservationGuestCount(reservation)>ROOM_TYPES[type].maxGuestCount);
  7018 |           if(overCapacity){toast(`${id}호 ${quickRangeLabel(overCapacity)} 예약이 ${reservationGuestCount(overCapacity)}명이라 최대 ${ROOM_TYPES[type].maxGuestCount}명인 ${ROOM_TYPES[type].name} 타입으로 바꿀 수 없습니다.`,'error');document.getElementById('room-info-type')?.focus();return;}
  7019 |           if(wasHeld&&!['vacant','occupied'].includes(occupancy)){toast('현재 투숙 상태를 선택해야 정보 확인 필요 상태를 해제할 수 있습니다.','error');document.getElementById('room-info-occupancy')?.focus();return;}
  7020 |           const before=`${ROOM_TYPES[room.type].name} · ${elevatorLabel(room)}${wasHeld?' · 정보 확인 필요':''}`;
  7021 |           room.type=type;room.elevator=elevator||null;
  7022 |           if(wasHeld){room.occupancyOverride=occupancy;room.occupancy=occupancy;room.catalogStatus='available';room.dataIssue=null;room.checkout=occupancy==='occupied'?'예정 미입력':'정보 없음';room.checkin=occupancy==='occupied'?'투숙 중':'정보 없음';}
  7023 |           const after=`${ROOM_TYPES[room.type].name} · ${elevatorLabel(room)}${wasHeld?` · ${room.occupancy==='occupied'?'투숙 중':'공실'}로 확인`:''}`;
  7024 |           appendEvent(`${id}호 객실 정보 수정`,`${before} → ${after} · 이후 새 작업부터 적용`,{roomId:id});
  7025 |           closeModal();render();focusAfterRender(`[data-action="edit-room-info"][data-id="${id}"]`);toast(wasHeld?'객실 정보를 확정하고 일반 운영 흐름을 열었습니다.':'객실 기본정보를 저장했습니다.');return;
  7026 |         }
  7027 |         if(a==='manual-checkout'){openManualCheckout(id,el);return;}
  7028 |         if(a==='confirm-manual-checkout'){
  7029 |           const room=ROOMS.find(item=>item.no===id),expected=el.dataset.fingerprint||'',blockingAttempt=manualCheckoutBlockingAttempt(id),unstartedAttempt=activeUnfinishedAttempt(id),pinViewed=unstartedAttempt&&roomPinWasViewed(id,unstartedAttempt.id);
  7030 |           if(!adminCanMutate()||!room||roomIsOnHold(id)||room.occupancy!=='occupied'||roomMasterFingerprint(room)!==expected||blockingAttempt){closeModal();render();toast(blockingAttempt?'진행 중인 청소 작업을 먼저 마무리하세요.':'투숙 상태 또는 관리자 최신 상태가 바뀌어 체크아웃하지 않았습니다.','error');return;}
  7031 |           const actualCheckoutAt=`${state.selectedDate}T${state.time}`,plannedCheckout=plannedCheckoutLabel(room),activeReservation=currentOccupiedReservation(room),manualDraftId=`manual-checkout-${id}-${state.selectedDate}`,reservationDraft=activeReservation?state.drafts.find(draft=>draft.reservationId===activeReservation.id)||null:null,existingDraft=reservationDraft||state.drafts.find(draft=>draft.id===manualDraftId)||state.drafts.find(draft=>draft.room===id&&draft.kind==='퇴실 청소'&&!draft.reservationId&&draft.date===state.selectedDate),templateSnapshot=existingDraft?.templateSnapshot||unstartedAttempt?.templateSnapshot||templateSnapshotFor(id,'퇴실 청소'),previousWorkDate=unstartedAttempt?attemptWorkDate(unstartedAttempt,state.selectedDate):null,previousAccessStart=unstartedAttempt?.accessStart||unstartedAttempt?.checkoutSnapshot||startTimeFor(id);
  7032 |           const nextReservation=activeReservationsFor(state,id).filter(reservation=>reservation.id!==activeReservation?.id).find(reservation=>reservation.checkInAt>=actualCheckoutAt)||null,sameDayNext=nextReservation?.checkInAt.slice(0,10)===state.selectedDate,nextCheckinSnapshot=sameDayNext?nextReservation.checkInAt.slice(11,16):DEFAULT_CHECKIN_TIME,nextDeadlineSnapshot=shiftClockTime(nextCheckinSnapshot,-30)||'15:30';
  7033 |           if(existingDraft){existingDraft.date=state.selectedDate;existingDraft.source='manual-checkout';existingDraft.actualCheckoutAt=actualCheckoutAt;if(activeReservation){if(!existingDraft.reservationId)existingDraft.reservationId=activeReservation.id;existingDraft.guestCount=reservationGuestCount(activeReservation);}if(!existingDraft.templateSnapshot)existingDraft.templateSnapshot=templateSnapshot;}
  7034 |           else if(!unstartedAttempt)state.drafts.push({id:manualDraftId,room:id,kind:'퇴실 청소',created:state.time,date:state.selectedDate,source:'manual-checkout',actualCheckoutAt,reservationId:activeReservation?.id||null,guestCount:activeReservation?reservationGuestCount(activeReservation):null,templateSnapshot});
  7035 |           const canonicalCheckoutDraft=existingDraft||state.drafts.find(draft=>draft.id===manualDraftId)||null;
```

## 객실 목록: `renderRooms`

matches: 4

### occurrence 1 · line 3240

```html
  3195 |         root.querySelectorAll('.info-item').forEach(item=>{
  3196 |           const label=item.querySelector('span'),value=item.querySelector('strong');if(!label||!value)return;
  3197 |           if(/PIN lease 영향|lease 영향/.test(label.textContent)){label.textContent='PIN 조회 처리';value.textContent='기존 조회 종료 후 다시 확인';}
  3198 |           if(/이전 PIN lease/.test(label.textContent)){label.textContent='이전 PIN 조회';value.textContent='종료됨';}
  3199 |           if(/활성 PIN lease/.test(label.textContent)){label.textContent='활성 PIN 조회';value.textContent=value.textContent.replace(/^[^·]+/,'1건');}
  3200 |         });
  3201 |         root.querySelectorAll('.choice').forEach(choice=>{
  3202 |           const title=choice.querySelector('strong'),copy=title?.nextElementSibling;if(!title||!copy)return;
  3203 |           if(title.textContent.includes('작업 재계획 완료')){title.textContent='청소 일정 변경 완료';copy.textContent=copy.textContent.replace('기존 수행 회차','진행 중 청소').replace('새 회차','새 청소');}
  3204 |           if(title.textContent.includes('필요 PIN 교체')){title.textContent='도어락 PIN 확인 완료';copy.textContent='기존 PIN 조회를 끝내고 필요하면 PIN을 변경합니다.';}
  3205 |         });
  3206 |         root.querySelectorAll('.notice-info').forEach(notice=>{
  3207 |           if(/새 작업은 시트 청소요금을 스냅샷|기존 확정 이력은 당시 기록|새 담당 구간이 타임라인/.test(notice.textContent))notice.textContent=/담당/.test(notice.textContent)?'저장하면 담당 메이드에게 통보됩니다.':'변경한 청소요금은 새 작업부터 적용됩니다.';
  3208 |           if(/새 타입·엘리베이터는 이후 생성하는 작업/.test(notice.textContent))notice.textContent='변경한 정보는 새 작업부터 적용됩니다.';
  3209 |         });
  3210 |         const catalogCopy=root.querySelector('.catalog-summary-copy');
  3211 |         if(catalogCopy){const occupied=ROOMS.filter(room=>room.occupancy==='occupied').length,vacant=ROOMS.filter(room=>room.occupancy==='vacant'&&!roomIsOnHold(room.no)).length,hold=ROOMS.filter(room=>roomIsOnHold(room.no)).length;catalogCopy.querySelector('span').textContent=`투숙 중 ${occupied}개 · 공실 ${vacant}개 · 확인 필요 ${hold}개`;catalogCopy.insertAdjacentHTML('beforeend',infoTip('room-status','객실 상태','고객 배정 가능은 공실 중 청소·촛불·운영 조건까지 모두 준비된 객실에만 표시됩니다.'));}
  3212 |         const replacements=new Map([
  3213 |           ['객실별 청소 원장 합계','청소 내역 합계'],['객실별 청소 원장','객실별 청소 내역'],['주급 산출 원장','주급 청소 내역'],['현재 원장 예상','승인 시 예상'],['현재 원장','현재 합계'],['공통 원장 산식','청소 내역 합계'],['카드·예약표 공통 원장','예약 일정'],['다중 예약 원장','예약 일정'],['비공개 퇴실 청소 초안','퇴실 청소 미배정'],['잠근 지급 기록액','지급 기록액'],['잠근 지급액','지급 기록액'],['지급 진행 스냅샷','지급 진행 상태'],['원장 변동 · 정정 필요','금액 확인 필요'],['지급 대기(OPEN)','지급 대기'],['지급 진행(PAYING)','지급 진행'],['정산 확인 필요(CHECK)','정산 확인 필요'],['지급 완료(PAID)','지급 완료'],['송금하지 않음 · OPEN 복귀','송금하지 않음 · 지급 대기'],['OPEN 복귀','지급 대기 복귀'],['잠근 수익 ID','청소 내역'],['수익 ID','청소 내역'],['잠근 수익','청소 내역'],['포함 수익','청소 내역'],['미지급 수익','미지급 청소비'],['PIN lease','PIN 조회 기록'],['활성 lease','활성 PIN 조회'],['lease 영향','PIN 조회 영향'],['lease','PIN 조회'],['기존 수행 회차','기존 청소 작업'],['수행 회차','청소 작업'],['기존 회차','기존 청소 작업'],['기존 청소 작업는','기존 청소 작업은'],['새 회차 생성','새 청소 생성'],['중단 이력으로 보존','중단 처리하고'],['상태 재계산','상태 다시 확인'],['재계산 완료','확인 완료'],['재검증','다시 확인'],['충돌 종결','충돌 조치 완료'],['충돌 조치 완료·상태 다시 확인','조치 완료'],['종결 전','조치 완료 전'],['종결 시각','조치 시각'],['기존 사건 삭제 금지','현재 상태 변경 전 확인'],['체크아웃 투숙 상태 복원을 추가합니다.','체크아웃 시각까지 투숙 중으로 표시합니다.'],['투숙 상태 복원와','투숙 상태 복원과'],['점유 재개 보정','투숙 상태 복원'],['점유 보정','투숙 상태'],['점유 재개','투숙 상태 복원'],['보정 대기','변경 대기'],['보정 완료','변경 완료'],['보정 이벤트','변경 기록'],[' · 원문 미표시',''],['브라우저 시뮬레이션','데모 화면'],['정적 파일','데모 화면'],['fixture','데모 기록'],['fingerprint','확인값'],['예약 ID별','예약별'],['예약 ID','예약'],['예약 식별','예약'],['식별값','확인값'],['식별자','확인값'],['스냅샷','기준'],['수익 원장','청소 내역'],['폭탄방 요금 원장','폭탄방 청소비'],['산출 원장','청소 내역'],['원장','내역'],['시트 정본','기본 요금'],[' · 8월 시트',''],['제출 당시 기준','제출 당시 기준'],['제출 버전 고정','제출 내용'],['현재 활성 템플릿 상세','템플릿 상세'],[' · 상태 이력 보존',''],['메이드 지정 · 사유 입력 · 삭제/복구 이력','메이드별 기록 관리'],['PIN 원문을 제외한 예약·업무·지급 감사 이력','예약·업무·지급 변경 내역'],['시트 청소요금·데모 예상시간과 템플릿','청소요금과 사진 템플릿'],['로그인 비밀번호는 객실 PIN과 분리','계정과 로그인 설정'],['OPEN','지급 대기'],['PAYING','지급 진행'],['CHECK','정산 확인 필요'],['PAID','지급 완료']
  3214 |         ]);
  3215 |         const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  3216 |         nodes.forEach(node=>{if(node.parentElement?.closest('.demo-strip'))return;let value=node.nodeValue;for(const [from,to] of replacements)value=value.split(from).join(to);value=value.replace(/\bLEASE-[A-Za-z0-9-]+\b/g,'기존 PIN 조회').replace(/\s*·\s*데모/g,'').replace(/\(데모\)/g,'').replace(/투숙 상태 복원와/g,'투숙 상태 복원과').replace(/중단 처리하고하고/g,'중단 처리하고').replace(/기존 청소 작업는/g,'기존 청소 작업은').replace(/청소 작업를/g,'청소 작업을').replace(/데모 데모 기록/g,'데모 기록');node.nodeValue=value.trim()==='데모'?'':value;});
  3217 |         root.querySelectorAll('.info-item').forEach(item=>{const label=item.querySelector('span'),value=item.querySelector('strong');if(label?.textContent.trim()==='PIN 조회'&&value?.textContent.includes('기존 조회 종료'))label.textContent='PIN 조회 처리';});
  3218 |         root.querySelectorAll('.badge').forEach(badge=>{if(!badge.textContent.trim())badge.remove();});
  3219 |       }
  3220 | 
  3221 |       function renderTopbar() {
  3222 |         return `<header class="topbar">
  3223 |           <div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 2026.08.14 ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div>
  3224 |           <div class="topbar-actions">
  3225 |             <button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기">${icon('bell')}<span class="count-dot">${state.role==='admin'?6:3}</span></button>
  3226 |             <button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button>
  3227 |           </div>
  3228 |         </header>`;
  3229 |       }
  3230 | 
  3231 |       function renderBottomNav(nav) {
  3232 |         return `<nav class="bottom-nav" aria-label="모바일 주요 내비게이션">${nav.map(n=>`<button type="button" data-action="nav" data-view="${n.id}" ${currentView()===n.id&&!state.detail?'aria-current="page"':''}>${icon(n.icon)}<span>${n.mobileLabel||n.label}</span></button>`).join('')}</nav>`;
  3233 |       }
  3234 | 
  3235 |       function renderMain() {
  3236 |         if (!state.loggedIn) return renderLogin();
  3237 |         if (state.detail) return renderDetail();
  3238 |         if (state.role==='admin') {
  3239 |           if (state.adminView==='today') return renderCheckoutInspectionQueueSummary()+renderAdminToday();
  3240 |           if (state.adminView==='rooms') return renderRooms();
  3241 |           if (state.adminView==='maids') return renderMaids();
  3242 |           return renderAdminMore();
  3243 |         }
  3244 |         if (state.maidView==='schedule') return renderMaidSchedule();
  3245 |         if (state.maidView==='my') return renderMaidMy();
  3246 |         if (state.maidView==='done') return renderMaidDone();
  3247 |         if (state.maidView==='pay') return renderMaidPay();
  3248 |         return renderMaidMore();
  3249 |       }
  3250 | 
  3251 |       function renderCoach() {
  3252 |         if (state.role==='admin'||state.scenario===0) return '';
  3253 |         const cfg=SCENARIOS[state.scenario];
  3254 |         return `<aside class="scenario-coach"><span class="step">${state.scenario}</span><div><strong>${esc(cfg.title)}</strong><p>${esc(cfg.next)}</p></div>${button('시나리오 재설정','reset','outline')}</aside>`;
  3255 |       }
  3256 | 
  3257 |       function renderNetworkNotice() {
  3258 |         if (state.network==='online' && state.listMode!=='stale') return '';
  3259 |         return `<div class="notice notice-danger">${icon('sync')}<div><strong>${state.network==='offline'?'오프라인 · 읽기 전용':'오래된 데이터 · 변경할 수 없음'}</strong><br>마지막 연결 09:48. 인터넷에 연결한 뒤 다시 시도하세요.</div>${button('다시 시도','retry-network','outline')}</div>`;
  3260 |       }
  3261 | 
  3262 |       function renderListState(content, kind='queue') {
  3263 |         if (state.listMode==='loading') return `<section class="card" aria-busy="true" aria-label="불러오는 중"><div class="skeleton-list"><div class="skeleton"></div><div class="skeleton"></div><div class="skeleton"></div></div></section>`;
  3264 |         if (state.listMode==='empty') return `<section class="card state-panel"><div class="state-icon">${icon('check','icon-lg')}</div><h2>표시할 항목이 없습니다</h2><p>현재 선택한 날짜에 실제 운영 항목이 0건입니다.</p></section>`;
  3265 |         if (state.listMode==='filterEmpty') return `<section class="card state-panel"><div class="state-icon">${icon('filter','icon-lg')}</div><h2>필터 결과가 없습니다</h2><p>데이터는 있지만 현재 필터와 일치하는 항목이 없습니다.</p>${button('필터 초기화','clear-filter','outline')}</section>`;
  3266 |         return content;
  3267 |       }
  3268 | 
  3269 |       function legacyRoomPresentation(no) {
  3270 |         const job=state.jobs[no], candles=state.candles[no]||0;
  3271 |         if (no==='350') {
  3272 |           if (state.jobs['350']==='approved' && candles===0) {
  3273 |             if (timeMinutes(state.time)>=timeMinutes('16:00')) return {tone:'neutral',status:'예약상 투숙 중',reason:'입실 시각 후 차단 해소 · 전이 1회 기록',action:'상세 보기',act:'room-detail'};
  3274 |             return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3275 |           }
  3276 |           return {tone:'red',status:'입실 차단',reason:`${state.jobs['350']==='approved'?'검수 승인':'미검수'} · 촛불 ${candles}개`,action:'입실 차단 해결',act:'room-detail'};
  3277 |         }
  3278 |         if (no==='332') return state.conflict==='active'?{tone:'red',status:'출입 충돌',reason:'레이트 체크아웃 · PIN 조회 후 일정 변경',action:'영향 확인',act:'room-detail'}:{tone:'amber',status:'청소 중',reason:'김민지1 수행 중',action:'상세 보기',act:'cleaning-detail'};
  3279 |         if (no==='528') return {tone:'amber',status:job==='inspection'?'검수 대기':'업로드 대기',reason:job==='inspection'?'전체 제출 완료':'현장 완료 · 사진 1건 미전송',action:job==='inspection'?'검수':'미전송 보기',act:'cleaning-detail'};
  3280 |         if (no==='536') return {tone:'green',status:'입실 준비 완료',reason:'검수 승인 · 촛불 0 · 차단 없음',action:'상세 보기',act:'room-detail'};
  3281 |         if (no==='639') return state.inspection.status==='approved'?{tone:'green',status:'입실 준비 완료',reason:'전체 승인 · 촛불 0',action:'결과 보기',act:'cleaning-detail'}:{tone:'amber',status:state.inspection.status==='rejected'?'재청소 배정':'검수 대기',reason:state.inspection.status==='rejected'?'기존 메이드 기본 담당':'전체 제출 v2',action:state.inspection.status==='rejected'?'재청소 보기':'검수',act:'cleaning-detail'};
  3282 |         if (no==='142') return {tone:'neutral',status:'예약상 투숙 중',reason:state.stayoverCreated?'연박 청소 배정 준비 작업 생성':'연박 청소 요청',action:state.stayoverCreated?'작업 보기':'연박 청소 생성',act:'room-detail'};
  3283 |         return {tone:'neutral',status:state.reservationSaved?'미래 예약 · 초안 생성':'미래 예약',reason:'내일 16:00 입실 예정',action:'상세 보기',act:'room-detail'};
  3284 |       }
  3285 | 
  3286 |       function renderRoomRows() {
  3287 |         const rows=ROOMS.filter(r => state.roomFilter==='all' || (state.roomFilter==='inspection' && ['528','639'].includes(r.no)) || (state.roomFilter==='blocked' && ['350','332'].includes(r.no)));
  3288 |         return rows.map(r=>{
  3289 |           const p=legacyRoomPresentation(r.no), type=ROOM_TYPES[r.type];
  3290 |           return `<article class="room-row" data-room="${r.no}">
  3291 |             <div class="room-no">${r.no}</div>
  3292 |             <div class="room-type"><strong>${esc(type.name)}</strong><span>${money(type.rate)} · 8월 시트 · 예상 ${type.minutes}분(데모)</span></div>
  3293 |             <div class="status-cell">${statusBadge(p.status,p.tone,p.tone==='red'?'alert':p.tone==='green'?'check':'clock')}<p>${esc(p.reason)}</p></div>
  3294 |             <div class="schedule-cell"><strong>체크인 ${esc(r.checkin)} → 체크아웃 ${esc(r.checkout)}</strong><span class="cell-sub">한 고객 예약 · 담당 ${esc(r.assignee)}</span></div>
  3295 |             <div><strong>${r.no==='142'?'연박 요청':r.no==='211'?'예정':'준비 마감 '+(r.no==='350'?'15:30':'14:30')}</strong><span class="cell-sub">${state.selectedDate} · KST</span></div>
  3296 |             <div class="row-action"><button class="btn ${p.tone==='red'?'btn-danger':'btn-outline'}" type="button" data-action="${p.act}" data-id="${r.no}" ${isLocked()&&p.act!=='room-detail'?'disabled':''}>${esc(p.action)}</button></div>
  3297 |           </article>`;
  3298 |         }).join('');
  3299 |       }
  3300 | 
  3301 |       function renderRoomTable() {
  3302 |         return `<section class="card room-table" aria-label="객실 일별 현황">
  3303 |           <div class="room-head"><div>객실</div><div>객실 유형</div><div>상태</div><div>일정·담당</div><div>마감</div><div>주 행동</div></div>
  3304 |           ${renderRoomRows()}
  3305 |         </section>`;
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
```

### occurrence 2 · line 3351

```html
  3306 |       }
  3307 | 
  3308 |       function renderDateTools() {
  3309 |         return `<div class="date-tools">
  3310 |           <button class="icon-btn" type="button" data-action="date-prev" aria-label="이전 날짜">${icon('chevronLeft')}</button>
  3311 |           <div class="date-current">${icon('calendar','icon-sm')}<span>${state.selectedDate==='2026-08-14'?'2026.08.14 · 오늘':state.selectedDate.replaceAll('-','.')} </span></div>
  3312 |           <button class="icon-btn" type="button" data-action="date-next" aria-label="다음 날짜">${icon('chevronRight')}</button>
  3313 |           ${button('오늘','date-today','outline')}
  3314 |           <div class="filter-wrap"><label for="room-filter">필터</label><select id="room-filter" class="select-control" data-control="room-filter"><option value="all" ${state.roomFilter==='all'?'selected':''}>전체 객실</option><option value="blocked" ${state.roomFilter==='blocked'?'selected':''}>입실 차단·충돌</option><option value="inspection" ${state.roomFilter==='inspection'?'selected':''}>검수·업로드</option></select></div>
  3315 |         </div>`;
  3316 |       }
  3317 | 
  3318 |       function queueCard(tone,badge,title,count,desc,action,label,id='') {
  3319 |         return `<article class="card queue-card ${tone}">${statusBadge(badge,tone==='danger'?'red':tone==='warning'?'amber':tone==='success'?'green':'neutral')}<h3>${title}</h3><div class="count">${count}</div><p>${desc}</p><button class="btn ${tone==='danger'?'btn-danger':'btn-outline'}" type="button" data-action="${action}" ${id?`data-id="${id}"`:''} ${isLocked()&&action!=='room-detail'?'disabled':''}>${label}</button></article>`;
  3320 |       }
  3321 | 
  3322 |       function renderAdminToday() {
  3323 |         const content=`
  3324 |           <section class="section-head"><h2>즉시 조치 큐</h2><span class="meta">색상은 원본 상태에서 파생 · 우선순위는 마감 여유로 계산</span></section>
  3325 |           <div class="queue-grid">
  3326 |             ${queueCard('danger','긴급','350호 입실 미준비','1건','미검수 · 촛불 1개','room-detail','입실 차단 해결','350')}
  3327 |             ${queueCard('warning','대기','관리자 미배정 작업','3건','시작 가능 시각이 지나 재배정이 필요한 작업','view-open-jobs','목록 보기')}
  3328 |             ${queueCard('warning','주의','마감 위험','2건','예상 소요시간 반영 시 여유 부족','view-open-jobs','목록 보기')}
  3329 |             ${queueCard('success','대기','검수 대상 목록','4건','전체 제출 검수가 필요합니다','cleaning-detail','639호 검수','639')}
  3330 |             ${queueCard('neutral','요청','담당 취소 요청','1건',state.cancelRequest==='requested'?'15분 이내 관리자 결정 필요':'처리 완료 · 타임라인 보존','cancel-review',state.cancelRequest==='requested'?'요청 처리':'결과 보기')}
  3331 |             ${queueCard('neutral','동기화','동기화·PIN·정산','2건','충돌 또는 확인 필요 사건','alerts','알림 보기')}
  3332 |           </div>
  3333 |           <div class="dashboard-layout">
  3334 |             <div><div class="section-head"><h2>객실 일별 현황</h2><span class="meta">총 7개 · 한국시간</span></div>${renderDateTools()}${renderRoomTable()}</div>
  3335 |             <aside class="rail" aria-label="보조 운영 큐">${renderDraftRail()}${renderInspectionRail()}${renderPayRail()}</aside>
  3336 |           </div>`;
  3337 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  3338 |       }
  3339 | 
  3340 |       function renderScenario13Controls() {
  3341 |         if (state.scenario!==13) return '';
  3342 |         return `<section class="notice notice-info"><div style="flex:1"><strong>목록 상태 계약 데모</strong><br>상태를 바꾸면 정상 데이터·위험 행동 잠금 여부가 함께 변합니다.</div><label for="list-mode" class="sr-only">목록 상태</label><select id="list-mode" class="select-control" data-control="list-mode"><option value="loading" ${state.listMode==='loading'?'selected':''}>불러오는 중</option><option value="empty" ${state.listMode==='empty'?'selected':''}>진짜 0건</option><option value="filterEmpty" ${state.listMode==='filterEmpty'?'selected':''}>필터 결과 없음</option><option value="data" ${state.listMode==='data'?'selected':''}>데이터 있음</option><option value="stale" ${state.listMode==='stale'?'selected':''}>오래된 데이터·오류</option></select></section>`;
  3343 |       }
  3344 | 
  3345 |       function renderDraftRail() {
  3346 |         return `<section class="card"><div class="section-head"><h3>배정 준비 청소 작업</h3><span class="meta">${state.drafts.length}건</span></div><p class="cell-sub">근무일 전날 관리자 담당 배정을 기다립니다.</p><div class="rail-list">${state.drafts.length?state.drafts.map(d=>`<label class="rail-row"><input type="checkbox" data-control="draft" value="${d.id}" ${state.selectedDrafts.includes(d.id)?'checked':''} ${isLocked()?'disabled':''}><strong>${d.room}호 · ${d.kind}</strong><span>${d.created}</span></label>`).join(''):'<div class="state-panel" style="padding:12px"><p>배정 준비 작업 0건</p></div>'}</div>${button('내일 배정에서 보기','publish-selected','success',`${isLocked()?'disabled':''}`)}</section>`;
  3347 |       }
  3348 |       function renderInspectionRail() { return `<section class="card"><div class="section-head"><h3>검수 대상 목록</h3><span class="meta">4건</span></div><div class="rail-list"><div class="rail-row"><strong>639호 · 전체 제출 v2</strong><span>10:18</span></div><div class="rail-row"><strong>528호 · 업로드 완료</strong><span>10:14</span></div></div>${button('검수 대상 목록 보기','cleaning-detail','outline','data-id="639"')}</section>`; }
  3349 |       function renderPayRail() { const summary=paymentWeekSummaryFor();return `<section class="card"><div class="section-head"><h3>지난주 지급</h3>${statusBadge(summary.label,summary.tone)}</div><p class="cell-sub">메이드별 외부 전액 송금 완료를 각각 기록합니다. 앱은 송금하지 않습니다.</p>${button('지급 주차 상세','pay-detail','outline')}</section>`; }
  3350 | 
  3351 |       function renderRooms() {
  3352 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>객실 일별 현황</h2><span class="meta">과거는 읽기 전용, 미래는 확정 계획만 표시</span></div><div class="actions">${button('예약 등록','new-reservation','primary',isLocked()?'disabled':'')}</div></div>${renderDateTools()}${renderListState(renderRoomTable())}`;
  3353 |       }
  3354 | 
  3355 |       function renderMaids() {
  3356 |         const cards=MAIDS.map(m=>`<article class="card setting-card"><div class="avatar">${m.name[0]}</div><div style="min-width:0;flex:1"><h3>${m.name} · 데모</h3><p>${m.phone} · 관리자 배정 ${m.assigned}건<br>${m.id==='m1'&&state.maidStatus!=='active'?state.maidStatus:m.active}</p>${button('상세 보기','maid-detail','outline',`data-id="${m.id}"`)}</div></article>`).join('');
  3357 |         return renderCoach()+renderNetworkNotice()+`<div class="section-head"><div><h2>메이드 계정·업무 현황</h2><span class="meta">담당·실제 수행·제출·수익 귀속을 분리해 보존</span></div><div class="actions">${button('계정 추가','demo-info','primary')}</div></div><div class="settings-grid">${cards}</div>`;
  3358 |       }
  3359 | 
  3360 |       function renderAdminMore() {
  3361 |         return renderCoach()+renderNetworkNotice()+`<div class="settings-grid">
  3362 |           ${settingCard('wallet','주급·지급',`지난주 상태 ${paymentWeekSummaryFor().label} · 메이드별 외부 송금 기록`,button('지급 상세','pay-detail','outline'))}
  3363 |           ${settingCard('settings','객실 타입 청소요금·예상시간','청소요금은 8월 시트 정본 · 예상시간은 데모',button('청소요금 보기','rates','outline'))}
  3364 |           ${settingCard('list','청소 템플릿',`초안·미리보기·게시 버전 · 현재 ${state.template}`,button('템플릿 관리','template','outline'))}
  3365 |           ${settingCard('bell','알림 상태',state.notificationsEnabled?'이 기기 알림 허용 데모':'권한 요청 전 · 앱 내부 알림 사용',button(state.notificationsEnabled?'상태 보기':'알림 켜기','notification-permission','outline'))}
  3366 |           ${settingCard('shield','감사 이력','PIN 조회 사실·검수·단가·지급 수행자 기록',button('최근 이력 보기','audit-log','outline'))}
  3367 |           ${settingCard('lock','로그인·보안 상태','최초 변경·5회 실패·15분 잠금 데모',button('로그인 상태 보기','logout','outline'))}
  3368 |         </div>`;
  3369 |       }
  3370 | 
  3371 |       function settingCard(iconName,title,desc,action) { return `<article class="card setting-card"><div class="setting-icon">${icon(iconName)}</div><div style="min-width:0;flex:1"><h3>${title}</h3><p>${desc}</p>${action}</div></article>`; }
  3372 | 
  3373 |       function publicJobs() {
  3374 |         return [
  3375 |           {room:'350',type:'standard',kind:'퇴실 청소',date:'8월 14일',tone:'red',priority:'마감 위험',available:'지금 가능',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'},
  3376 |           {room:'142',type:'oceanFamily',kind:'연박 청소',date:'8월 14일',tone:'blue',priority:'연박',available:'13:00부터 시작',schedule:'13:00–15:00 출입 가능 → 14:30 요청 완료'},
  3377 |           {room:'211',type:'oceanFamily',kind:'퇴실 청소',date:'8월 15일',tone:'neutral',priority:'미래 일정',available:'내일 11:00부터',schedule:'이전 예약 체크아웃 11:00 → 15:30 준비 마감 → 다음 예약 체크인 16:00'}
  3378 |         ];
  3379 |       }
  3380 | 
  3381 |       function renderJobCard(j, claimed=false) {
  3382 |         const type=ROOM_TYPES[j.type];
  3383 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(j.priority,j.tone)}<h3 style="margin-top:10px">${j.room}호 · 데모</h3><p>${type.name}</p></div><div class="availability">${statusBadge(j.available,j.available.includes('지금')?'green':'neutral')}</div></div><div class="job-meta"><div><span>청소요금</span><strong>${money(type.rate)} · 8월 시트</strong></div><div><span>예상 소요시간</span><strong>${type.minutes}분 · 데모</strong></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions">${button(claimed?'내 업무 보기':'선택',claimed?'go-my':'claim-job',claimed?'outline':'primary',`data-id="${j.room}" ${isLocked()?'disabled':''}`)}</div></article>`;
  3384 |       }
  3385 | 
  3386 |       function renderMaidOpen() {
  3387 |         const jobs=publicJobs().filter(j=>state.jobs[j.room]==='public'||j.room==='142'||j.room==='211');
  3388 |         return renderCoach()+renderNetworkNotice()+`<div class="summary-strip"><span>${icon('list','icon-sm')}선택한 일감 <strong>2건</strong></span><span>${icon('clock','icon-sm')}예상 <strong>135분</strong></span><span>${icon('alert','icon-sm')}가장 가까운 마감 <strong>15:30</strong></span></div>${renderListState(`<section class="job-list">${jobs.map(j=>renderJobCard(j,false)).join('')}</section>`)}`;
  3389 |       }
  3390 | 
  3391 |       function renderMaidMy() {
  3392 |         const myJobs=[
  3393 |           {room:'350',type:'standard',kind:'퇴실 청소',status:state.jobs['350'],schedule:'11:00부터 시작 · 15:30 준비 마감'},
  3394 |           {room:'528',type:'premium',kind:'퇴실 청소',status:state.jobs['528'],schedule:'10:00 시작 가능 · 14:00 다음 입실'}
  3395 |         ];
  3396 |         return renderCoach()+renderNetworkNotice()+`<div class="notice notice-info">${icon('briefcase')}<div><strong>동시에 청소 중은 한 건만</strong><br>현장 완료·업로드 대기는 물리적 진행 슬롯을 해제하지만 다음 작업은 온라인 재검증 뒤 시작합니다.</div></div><section class="job-list">${myJobs.map(j=>renderMyJob(j)).join('')}</section>`;
  3397 |       }
  3398 | 
  3399 |       function renderMyJob(j) {
  3400 |         const type=ROOM_TYPES[j.type], canStart=timeMinutes(state.time)>=timeMinutes(j.room==='350'?'11:00':'10:00'), status=j.status;
  3401 |         let label='상세 보기',action='cleaning-detail',tone='neutral';
  3402 |         if (status==='claimed') { label=canStart?'시작':'출입 대기'; action='cleaning-detail'; tone=canStart?'green':'neutral'; }
  3403 |         if (status==='cleaning') { label='계속 청소'; tone='amber'; }
  3404 |         if (status==='upload') { label='미전송 재시도'; tone='red'; }
  3405 |         if (status==='inspection') { label='제출 결과 보기'; tone='amber'; }
  3406 |         return `<article class="card job-card"><div class="job-card-top"><div class="job-title">${statusBadge(statusLabel(status),tone)}<h3 style="margin-top:10px">${j.room}호 · ${j.kind}</h3><p>${type.name}</p></div></div><div class="schedule-line">${icon('clock','icon-sm')}<span>${j.schedule}</span></div><div class="job-actions"><button class="btn ${tone==='red'?'btn-danger':'btn-primary'}" type="button" data-action="${action}" data-id="${j.room}" ${isLocked()&&action!=='cleaning-detail'?'disabled':''}>${label}</button></div></article>`;
  3407 |       }
  3408 | 
  3409 |       function statusLabel(s) { return ({public:'관리자 배정 대기',unassigned:'관리자 배정 대기',claimed:'관리자 배정 확정',cleaning:'청소 중',upload:'현장 완료 · 업로드 대기',inspection:'검수 요청됨',approved:'승인',rejected:'반려',reclean:'재청소'})[s]||'예정'; }
  3410 | 
  3411 |       function renderMaidDone() {
  3412 |         return renderCoach()+`<section class="card room-table"><div class="room-head" style="grid-template-columns:90px 1fr 140px 140px"><div>현장 완료일</div><div>객실·수행</div><div>검수 결과</div><div>주 행동</div></div>${[
  3413 |           ['8/14','536호 · 실제 수행 김민지2','승인','536'],['8/13','639호 · 실제 수행 이서연','반려 → 재청소','639'],['8/12','332호 · 담당 김민지1 / 제출 이서연','승인 · 인계 이력','332']
  3414 |         ].map(r=>`<article class="room-row" style="grid-template-columns:90px 1fr 140px 140px"><div><strong>${r[0]}</strong></div><div><strong>${r[1]}</strong><span class="cell-sub">계획일과 현장 완료일 분리</span></div><div>${statusBadge(r[2],r[2].startsWith('승인')?'green':'amber')}</div><div>${button('결과 보기','cleaning-detail','outline',`data-id="${r[3]}"`)}</div></article>`).join('')}</section>`;
  3415 |       }
  3416 | 
  3417 |       function renderMaidPayFromLedger() {
  3418 |         const currentMaid=signedInMaid(),weeks=adminPayWeeks().map((week,index)=>{const tasks=week.tasksByMaid?.[currentMaid.id]||[],totals=payrollTaskTotals(tasks),payment=paymentStatusMeta(week.start,currentMaid.id,totals.confirmed),record=paymentRecordFor(week.start,currentMaid.id),displayAmount=paymentDisplayAmount(record,totals.confirmed),paymentDrift=displayAmount!==totals.confirmed,paidAt=payment.status==='PAID'?(record.paidAt||`${payrollDateLabel(addIsoDays(week.start,7))} 지급 기록`):['PAYING','CHECK'].includes(record.status)?payment.label:index===0?'다음 월요일 지급 예정':payment.label;return {id:week.start,group:index===0?'current':index===1?'last':'older',label:index===0?'이번 주':index===1?'지난주':'이전 주',period:weekRangeLabel(week.start),confirmed:displayAmount,ledgerConfirmed:totals.confirmed,pending:totals.pending,paymentDrift,status:payment.label,tone:payment.tone,paidAt,tasks};}),current=weeks[0],selectedWeek=state.maidPaySelectedWeek,shown=selectedWeek?weeks.filter(week=>week.id===selectedWeek):weeks;
  3419 |         const weekCard=week=>{const open=state.maidPayOpenWeek===week.id;return `<article class="card maid-pay-week"><div class="maid-pay-week-head"><div><span class="maid-pay-week-label">${week.label} · ${week.period}</span><strong>${money(week.confirmed)}</strong><small>${week.paymentDrift?'잠근 지급 기록액':'승인 확정'} · ${esc(currentMaid.name)} 데모 지급 이력</small></div>${statusBadge(week.status,week.tone)}</div>${week.paymentDrift?`<div class="notice notice-danger" style="margin:10px 0 0"><div><strong>현재 원장 ${money(week.ledgerConfirmed)}</strong><br>지급 기록액과의 차이는 관리자 정정·상계 대상으로 분리됩니다.</div></div>`:''}<div class="maid-pay-week-stats"><div><span>현재 원장 예상</span><strong>${money(week.ledgerConfirmed+week.pending)}</strong></div><div><span>검수 대기</span><strong>${money(week.pending)}</strong></div><div><span>지급 기록</span><strong>${week.paidAt}</strong></div></div><button class="maid-pay-disclosure" type="button" data-action="toggle-maid-pay-week" data-id="${week.id}" aria-expanded="${open}" aria-controls="maid-pay-week-${week.id}"><span>작업 상세 ${week.tasks.length}건</span><span>${open?'접기':'자세히 보기'} ${icon('chevronRight','icon-sm')}</span></button><div id="maid-pay-week-${week.id}" class="maid-pay-task-list" ${open?'':'hidden'}>${week.tasks.map(task=>`<div class="maid-pay-task"><div><strong>${esc(task.room)} · ${esc(task.kind)}</strong><span>${esc(task.date)} · ${esc(task.typeName)} · ${esc(task.elevator)}${task.roundLabel?` · 제출/회차 ${esc(task.roundLabel)}`:''}</span><span class="bomb-room-pay-breakdown">${esc(payrollTaskFormula(task))}</span>${task.reportId&&task.photoId?button('폭탄방 증빙 보기','bomb-room-photo','outline',`data-room="${task.roomNo}" data-report="${task.reportId}" data-photo="${task.photoId}"`):''}</div><div><b>${task.stage==='pending'?'승인 시 ':''}${money(task.stage==='excluded'?0:task.amount)}</b>${statusBadge(task.status,task.tone)}</div></div>`).join('')}</div></article>`;};
  3420 |         const selectedLabel=selectedWeek?weekRangeLabel(selectedWeek,true):'달력에서 주차 선택',historyBody=shown.length?shown.map(weekCard).join(''):`<section class="inline-empty"><h3>${weekRangeLabel(selectedWeek,true)} 주급 기록이 없습니다</h3><p>해당 월요일–일요일 주차에는 저장된 데모 작업 이력이 없습니다.</p></section>`;
```

### occurrence 3 · line 4036

```html
  3991 |         return renderCoach()+renderNetworkNotice()+detailHeader('청소 사진 템플릿','객실번호 → 타입 → 타입별 고정 구성 → 고정 사진 슬롯')+`<div class="template-page"><section class="card template-hero"><div class="template-hero-copy"><h2>같은 타입은 하나의 고정 템플릿을 사용합니다</h2><p>객실번호는 현재 객실 마스터에서 타입을 찾는 키이며, 같은 타입의 모든 객실은 동일한 공간 구성과 사진 슬롯을 사용합니다.</p></div><div class="template-hero-stat"><span>객실</span><strong>121실</strong></div><div class="template-hero-stat"><span>객실 타입</span><strong>4종</strong></div><div class="template-hero-stat"><span>활성 조합</span><strong>12개</strong></div></section><div class="notice notice-info"><div><strong>객실별 보정이나 슬롯 범위는 사용하지 않습니다.</strong><br>객실번호를 타입에 매칭한 뒤 해당 타입의 고정 공간 구성과 고정 슬롯 계약을 작업 스냅샷으로 저장합니다.</div></div>${groups}</div>`;
  3992 |       }
  3993 |       function renderTemplateTimeline(template) {
  3994 |         const latest=template.history[0];
  3995 |         return `<section class="card template-timeline"><h3>버전·적용 타임라인</h3><ol class="timeline">${latest?`<li><strong>${esc(template.version)} 저장·활성</strong><span>${esc(template.lastSaved)} · 예상시간 변경 · 데모</span></li>`:''}<li><strong>${latest?esc(latest.version):esc(template.version)} 활성 버전 기록</strong><span>${latest?esc(latest.savedAt):esc(template.lastSaved)} · 사진 전용 템플릿</span></li><li><strong>기존 작업 유지</strong><span>이미 시작된 작업의 청소요금·예상시간·사진 구역은 변경하지 않음</span></li><li><strong>새 작업부터 적용</strong><span>저장 뒤 생성되는 퇴실·연박·재청소 작업에 ${esc(template.version)} 고정</span></li></ol></section>`;
  3996 |       }
  3997 |       function renderTemplateDetail(id,mode='view') {
  3998 |         const template=templateById(id);
  3999 |         if(!template)return renderTemplateList();
  4000 |         const type=ROOM_TYPES[template.typeId],profile=TYPE_LAYOUT_PROFILES[template.typeId],rooms=templateRooms(template),snapshot=templateFixedSnapshot(template),fixedPhotos=snapshot?.photos||template.photos,required=fixedPhotos.filter(item=>item.required).length,optional=fixedPhotos.length-required,stats=templateSlotStats(template),evidence=PHOTO_TEMPLATE_EVIDENCE[template.typeId];
  4001 |         if(mode==='edit')return renderCoach()+templateDetailHead(template,'edit')+`<form id="template-edit-form" class="card template-section template-edit-form"><div class="template-section-head"><div><h3>템플릿 수정</h3><p>${esc(type.name)} · ${esc(template.name)} · 현재 ${esc(template.version)} · 데모</p></div>${statusBadge('새 작업부터 적용','blue')}</div><div class="template-edit-time"><div class="field"><label for="template-minutes">예상시간 · 데모</label><input id="template-minutes" class="input-control" type="number" min="10" max="180" step="5" value="${template.minutes}" inputmode="numeric" required><small>10~180분, 5분 단위로 입력합니다.</small></div><div class="template-summary-item"><span>타입 고정 사진 슬롯</span><strong>${fixedPhotos.length}개 · 적용 객실 ${rooms.length}실</strong></div></div><div class="notice notice-warning"><div><strong>이 화면에서는 예상시간만 수정합니다.</strong><br>공간 구성과 사진 슬롯은 객실 타입별로 고정되어 있으며, 저장한 예상시간은 새 작업부터 적용됩니다. 기존 작업·제출은 당시 스냅샷을 유지합니다.</div></div><div class="template-actions">${button('수정 취소','template-cancel-edit','outline',`data-id="${esc(template.id)}"`)}${button('변경 내용 확인','template-review','primary',`data-id="${esc(template.id)}"`)}</div></form>`;
  4002 |         const slotCards=fixedPhotos.map((item,index)=>`<article class="template-photo-item" data-template-fixed-slot="${esc(item.id)}" data-template-fixed-order="${index}" data-template-fixed-zone="${esc(item.zone||'사진')}" data-template-fixed-label="${esc(item.label)}" data-template-fixed-description="${esc(item.description||'청소 완료 상태를 촬영합니다.')}" data-template-fixed-required="${item.required?'true':'false'}" data-template-max-photos="${photoUploadLimit(item)}"><span class="photo-slot-zone">${esc(item.zone||'사진')}</span><strong>${esc(item.label)}</strong><span class="photo-slot-guide">${photoUploadLimit(item)>1?`최대 ${photoUploadLimit(item)}장`:'1장 이상'}${item.instanceCount>1?` · ${item.instance}/${item.instanceCount}`:''}</span></article>`).join('');
  4003 |         const sourceNote=template.kindId==='checkout'?`참고 사진 ${evidence.rooms.join('·')}호 ${evidence.photoCount}장은 촬영 항목을 정리하는 근거로만 사용했으며 객실별 다른 구조를 뜻하지 않습니다.`:`${template.name}는 현재 타입별 공통 데모 규칙이며 같은 타입의 모든 객실에 동일하게 적용됩니다.`;
  4004 |         return renderCoach()+renderNetworkNotice()+templateDetailHead(template)+`<div class="template-page"><section class="card template-section"><div class="template-section-head"><div><h3>활성 버전</h3><p>${esc(type.name)} × ${esc(template.name)} · 청소요금 ${money(type.rate)} (8월 시트)</p></div><div class="template-row-version">${statusBadge(`활성 ${template.version}`,'green')}${statusBadge('타입 고정 구성','blue')}</div></div><div class="template-summary"><div class="template-summary-item"><span>예상시간 · 데모</span><strong>${template.minutes}분</strong></div><div class="template-summary-item"><span>적용 객실</span><strong>${rooms.length}실</strong></div><div class="template-summary-item"><span>고정 사진 슬롯</span><strong>${fixedPhotos.length}개</strong></div><div class="template-summary-item"><span>인증 / 기타 슬롯</span><strong>${required} / ${optional}</strong></div></div></section><section class="card template-section"><div class="template-section-head"><div><h3>메이드 고정 촬영 슬롯</h3><p>같은 타입의 모든 객실과 관리자 검수가 동일한 슬롯 계약을 사용합니다.</p></div><div class="badge-row">${statusBadge('타입 내 동일','green')}${statusBadge('슬롯 구조 일치','green')}</div></div><div class="template-summary"><div class="template-summary-item"><span>객실 타입 고정 구성</span><strong>${esc(profile.composition)}</strong></div><div class="template-summary-item"><span>객실번호 역할</span><strong>타입 매칭 키</strong></div><div class="template-summary-item"><span>기본 규칙</span><strong>${stats.baseTotal}개</strong></div><div class="template-summary-item"><span>적용 결과</span><strong>${stats.total}개 고정 슬롯</strong></div></div><div class="notice notice-success" style="margin-top:14px"><div><strong>같은 타입이면 객실번호가 달라도 구성이 같습니다.</strong><br>객실별 선택기·레이아웃 보정·확인 보류 없이 이 고정 구성을 새 작업 스냅샷에 저장합니다.</div></div><div class="template-photo-grid" data-template-fixed-grid data-template-id="${esc(template.id)}" data-template-type="${esc(template.typeId)}" data-template-photo-count="${fixedPhotos.length}" style="margin-top:14px">${slotCards}</div><div class="template-evidence"><div class="template-evidence-row"><strong>타입 매칭</strong><span>현재 객실 마스터에서 ${rooms.length}실이 ${esc(type.name)}으로 연결됩니다.</span></div><div class="template-evidence-row"><strong>근거 범위</strong><span>${esc(sourceNote)}</span></div></div></section><div class="notice notice-warning"><div><strong>일반 슬롯은 1장, 기타 슬롯은 최대 10장을 유지합니다.</strong><br>일반 슬롯은 재촬영 시 기존 사진을 교체하고, 기타 슬롯은 각 사진을 따로 추가·삭제합니다. TV 슬롯이 있으면 계정·QR·알림 없는 중립 화면의 전원·출력을 촬영합니다.</div></div>${renderTemplateTimeline(template)}<div class="template-actions">${button('예상시간 수정','template-edit','primary',`data-id="${esc(template.id)}"`)}</div></div>`;
  4005 |       }
  4006 |       function readTemplateChange(id) {
  4007 |         const template=templateById(id),input=document.getElementById('template-minutes');
  4008 |         if(!template||!input) return null;
  4009 |         const minutes=Number(input.value);
  4010 |         if(!Number.isInteger(minutes)||minutes<10||minutes>180){toast('예상시간은 10분부터 180분 사이로 입력하세요.','error');input.focus();return null;}
  4011 |         return {id,minutes};
  4012 |       }
  4013 |       function openTemplateReview(id) {
  4014 |         const template=templateById(id),change=readTemplateChange(id);if(!template||!change)return;
  4015 |         pendingTemplateChange=change;rememberCurrentHistoryRoute();
  4016 |         const nextVersion=`v${Number(template.version.replace(/\D/g,''))+1}`;
  4017 |         showModal({title:'템플릿 변경 내용 확인',subtitle:`${ROOM_TYPES[template.typeId].name} · ${template.name} · 데모`,body:`<div class="template-review-summary"><div class="template-review-row"><span>활성 버전</span><strong>${esc(template.version)} → ${esc(nextVersion)}</strong></div><div class="template-review-row"><span>예상시간 · 데모</span><strong>${template.minutes}분 → ${change.minutes}분</strong></div><div class="template-review-row"><span>촬영 규칙</span><strong>인증 ${template.photos.filter(item=>item.required).length}개 · 기타 ${template.photos.filter(item=>!item.required).length}개</strong></div></div><div class="notice notice-warning" style="margin:12px 0 0">사진 구역은 유지되고 예상시간 변경은 새 작업부터 적용됩니다.</div>`,confirmLabel:'변경 저장·활성',confirmAction:'template-save',confirmVariant:'primary',historyKind:'template-review',historyPayload:change});
  4018 |         document.querySelector('[data-action="template-save"]')?.setAttribute('data-id',id);
  4019 |       }
  4020 | 
  4021 |       function titleForView() {
  4022 |         if (state.detail) {
  4023 |           const map={room:`${state.detail.id}호 객실 상세`,cleaning:`${state.detail.id}호 청소 상세`,maid:`${maidById(state.detail.id)?.name||'메이드'} 상세`,complaint:'컴플레인·벌점 상세',pay:'주급 정산 상세',templates:'청소 템플릿 설정',template:'청소 템플릿 상세'};
  4024 |           return map[state.detail.type]||'상세';
  4025 |         }
  4026 |         const admin={today:'오늘 할 일',rooms:'객실 현황',quickReservation:'간편 예약',cleaning:'청소 관리',maids:'메이드',more:'더보기'};
  4027 |         const maid={my:'내 업무',schedule:'다음 주 근무 가능일',alerts:'알림',pay:'내 주급',more:'더보기'};
  4028 |         return (state.role==='admin'?admin:maid)[currentView()]||'객실관리';
  4029 |       }
  4030 | 
  4031 |       function renderMain() {
  4032 |         if (!state.loggedIn) return renderLogin();
  4033 |         if (state.detail) return renderDetail();
  4034 |         if (state.role==='admin') {
  4035 |           if (state.adminView==='today') return renderAdminToday();
  4036 |           if (state.adminView==='rooms') return renderRooms();
  4037 |           if (state.adminView==='quickReservation') return renderQuickReservation();
  4038 |           if (state.adminView==='cleaning') return renderCleaningHub();
  4039 |           if (state.adminView==='maids') return renderMaids();
  4040 |           return renderAdminMore();
  4041 |         }
  4042 |         if (state.maidView==='my') return renderMaidMy();
  4043 |         if (state.maidView==='schedule') return renderMaidSchedule();
  4044 |         if (state.maidView==='alerts') return renderMaidAlerts();
  4045 |         if (state.maidView==='pay') return renderMaidPay();
  4046 |         return renderMaidMore();
  4047 |       }
  4048 | 
  4049 |       function renderTopbar() {
  4050 |         const alertCount=notificationUnreadCount(notificationAudienceKey()),countMarkup=alertCount?`<span class="count-dot">${alertCount}</span>`:'';
  4051 |         return `<header class="topbar"><div class="topbar-title"><h1>${esc(titleForView())}</h1><p>한국시간 · 마지막 동기화 ${state.selectedDate.replaceAll('-','.')} ${state.network==='online'?state.time:'09:48'} ${state.network==='online'?'':'· 읽기 전용'}</p></div><div class="topbar-actions"><button class="icon-btn" type="button" data-action="alerts" aria-label="알림함 열기 · 안 읽음 ${alertCount}건">${icon('bell')}${countMarkup}</button><button class="btn btn-outline" type="button" data-action="switch-role" aria-label="${state.role==='admin'?'메이드 보기':'관리자 보기'}">${icon('users','icon-sm')}<span>${state.role==='admin'?'메이드 보기':'관리자 보기'}</span></button></div></header>`;
  4052 |       }
  4053 | 
  4054 |       function dateObject(value=state.selectedDate) {
  4055 |         const [y,m,d]=value.split('-').map(Number);
  4056 |         return new Date(y,m-1,d);
  4057 |       }
  4058 |       function dateIso(date) {
  4059 |         return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`;
  4060 |       }
  4061 |       function calendarDayMeta(iso) {
  4062 |         const value=dateObject(iso),weekday=value.getDay(),holiday=KR_HOLIDAY_FIXTURE.dates[iso]||null,isSunday=weekday===0,isSaturday=weekday===6;
  4063 |         return {
  4064 |           weekday,weekdayLabel:CALENDAR_WEEKDAYS[weekday],holiday,isSunday,isSaturday,
  4065 |           tone:holiday?'holiday':isSunday?'sunday':isSaturday?'saturday':'weekday',
  4066 |           classes:[isSunday?'is-sunday':'',isSaturday?'is-saturday':'',holiday?'is-holiday':''].filter(Boolean).join(' ')
  4067 |         };
  4068 |       }
  4069 |       function calendarWeekdayHeaderMarkup() {
  4070 |         return CALENDAR_WEEKDAYS.map((label,index)=>`<span class="${index===0?'is-sunday':index===6?'is-saturday':''}">${label}</span>`).join('');
  4071 |       }
  4072 |       function calendarDateAriaLabel(iso,{today=false,weekSelected=false}={}) {
  4073 |         const value=dateObject(iso),meta=calendarDayMeta(iso),parts=[`${value.getFullYear()}년 ${value.getMonth()+1}월 ${value.getDate()}일 ${meta.weekdayLabel}요일`];
  4074 |         if(meta.holiday)parts.push(meta.holiday.name);
  4075 |         if(today)parts.push('오늘');
  4076 |         if(weekSelected)parts.push('선택 주차');
  4077 |         return parts.join(', ');
  4078 |       }
  4079 |       function dateLabel(value=state.selectedDate) {
  4080 |         const d=dateObject(value), day=CALENDAR_WEEKDAYS[d.getDay()];
  4081 |         return `${d.getMonth()+1}월 ${d.getDate()}일 (${day})`;
  4082 |       }
  4083 |       function weekStartIso(value) {
  4084 |         const d=dateObject(value), offset=(d.getDay()+6)%7;
  4085 |         d.setDate(d.getDate()-offset);
  4086 |         return dateIso(d);
  4087 |       }
  4088 |       function normalizePayWeek(value) {
  4089 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4090 |         const date=dateObject(value);
  4091 |         if(dateIso(date)!==value)return null;
  4092 |         const start=weekStartIso(value);
  4093 |         return start<='2026-08-10'?start:null;
  4094 |       }
  4095 |       function normalizeWorkHistoryWeek(value) {
  4096 |         if(!/^\d{4}-\d{2}-\d{2}$/.test(value||''))return null;
  4097 |         const date=dateObject(value);
  4098 |         if(dateIso(date)!==value)return null;
  4099 |         const start=weekStartIso(value);
  4100 |         return start<='2026-08-17'?start:null;
  4101 |       }
  4102 |       function workHistoryCalendarAllowed() { return state.loggedIn!==false&&state.role==='admin'&&state.adminView==='maids'&&state.adminMaidTab==='history'; }
  4103 |       function weekRangeLabel(start,withYear=false) {
  4104 |         const from=dateObject(start),to=new Date(from);to.setDate(from.getDate()+6);
  4105 |         const prefix=withYear?`${from.getFullYear()}년 `:'';
```

## 청소 대상: `cleaningCandidates`

matches: 0

## 청소 가능 여부: `isCleaning`

matches: 5

### occurrence 1 · line 4918

```html
  4873 |         const inspectionBody=`<div class="rail-row"><strong>350호 · 얼리 체크인 우선</strong><span>검수 요청됨</span></div><div class="rail-row"><strong>639호 · 전체 제출</strong><span>검수 요청됨</span></div><div style="margin-top:10px">${button('검수 대상 목록 열기','go-inspection','outline')}</div>`;
  4874 |         const lastWeekMaidPay=maidPayAmount('김민지1','2026-08-03'),payBody=`<div class="rail-row"><strong>김민지1 지난주 지급 대상</strong><span>${money(lastWeekMaidPay)} · 폭탄방 승인 1건 포함 · 데모</span></div><p class="audit-note">앱은 송금하지 않고 지급 여부만 기록합니다.</p><div style="margin-top:10px">${button('주급 정산 열기','go-payroll','outline')}</div>`;
  4875 |         const requestedEntry=Object.entries(state.cancelRequests||{}).find(([,request])=>request.status==='requested'), cancelRequested=state.cancelRequest==='requested'||!!requestedEntry, cancelResolved=!!state.cancelDecision;
  4876 |         const cancelNo=requestedEntry?.[0]||state.cancelRequestRoom||'332', cancelRequest=requestedEntry?.[1], cancelMaid=cancelRequest?.maid||ROOMS.find(room=>room.no===cancelNo)?.assignee||'김민지1';
  4877 |         const cancelBody=cancelRequested?`<div class="rail-row"><strong>${esc(cancelMaid)} · ${esc(cancelNo)}호</strong><span>${esc(cancelRequest?.reason||'건강상 사유 · 데모')} · 결정 전 담당 유지</span></div><div style="margin-top:10px">${button('요청 처리','cancel-review','danger',isLocked()?'disabled':'')}</div>`:`<div class="rail-row"><strong>처리 완료</strong><span>${state.cancelDecision==='deny'?'거절 · 기존 담당 유지':state.cancelDecision==='republish'?'승인 · 관리자 재배정 대기':state.cancelDecision==='direct'?'승인 · 김민지2 직접 배정':'승인 · 관리자 조치 대기'}</span></div><p class="audit-note">원 요청·사유·결정 이벤트는 감사 이력에 보존됩니다.</p>`;
  4878 |         const cancelAccordion=cancelRequested||cancelResolved?renderAccordion('cancel',cancelRequested?'담당 취소 요청':'담당 취소 처리 결과',cancelRequested?'1건':'처리됨',cancelBody,cancelRequested):'';
  4879 |         const assignmentCountsToday=assignmentCountsForDate(state.selectedDate), assignmentBody=`<div class="rail-row"><strong>${dateLabel(state.selectedDate)} 청소</strong><span>${assignmentCountsToday.assigned}/${assignmentCountsToday.total} 담당 선택 · ${assignmentCountsToday.unassigned}건 미배정</span></div><p class="audit-note">당일 추가·취소와 담당·순서 변경도 관리자만 저장·통보합니다.</p><div style="margin-top:10px">${button('오늘 배정 열기','go-cleaning-assignment',assignmentCountsToday.unassigned?'danger':'outline','data-day="today"')}</div>`;
  4880 |         const content=`<div class="view-stack"><div>${renderDateTools(false)}</div><section aria-labelledby="summary-title" data-admin-home-section="room-summary"><div class="mobile-section-title"><div><h2 id="summary-title">오늘 객실 요약</h2></div></div><div class="today-summary"><button class="card metric-card neutral" type="button" data-action="filter-rooms" data-filter="occupied" aria-label="투숙 중 객실 ${occupiedCount}개 목록 보기"><span>투숙 중</span><strong>${occupiedCount}</strong></button><button class="card metric-card amber" type="button" data-action="filter-rooms" data-filter="cleaning" aria-label="청소 필요 객실 ${cleaningCount}개 목록 보기"><span>청소 필요</span><strong>${cleaningCount}</strong></button><button class="card metric-card green" type="button" data-action="filter-rooms" data-filter="available" aria-label="배정 가능 객실 ${availableCount}개 목록 보기"><span>배정 가능</span><strong>${availableCount}</strong></button><button class="card metric-card red" type="button" data-action="filter-rooms" data-filter="blocked" aria-label="배정 불가 객실 ${blockedCount}개 목록 보기"><span>배정 불가</span><strong>${blockedCount}</strong></button></div></section><div class="accordion-list" data-admin-home-section="cleaning-actions">${renderAccordion('assignment','오늘 청소 배정',`${assignmentCountsToday.unassigned}건 미배정`,assignmentBody,true)}${renderAccordion('inspection','청소 검수','2건',inspectionBody)}</div><div data-admin-home-section="cleaning-cost">${cleaningCostSection}</div></div>`;
  4881 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  4882 |       }
  4883 | 
  4884 |       function maidName(id) { return MAIDS.find(maid=>maid.id===id)?.name||'미배정'; }
  4885 |       function availabilityFor(maidId,dayIndex=0) {
  4886 |         const record=state.weeklyAvailability?.[maidId];
  4887 |         if(!record||!['submitted','change-requested'].includes(record.status))return 'missing';
  4888 |         return record.days.includes(dayIndex)?'available':'unavailable';
  4889 |       }
  4890 |       function availabilityForWorkDate(maidId,iso) {
  4891 |         const start=weekStartIso(iso),dayIndex=weekdayIndex(iso);
  4892 |         if(start==='2026-08-17')return availabilityFor(maidId,dayIndex);
  4893 |         const versions=(state.availabilityHistory||[]).filter(item=>item.maidId===maidId&&item.weekStart===start).sort((left,right)=>left.version-right.version),snapshot=versions.at(-1),fixture=WORK_HISTORY_FIXTURES.find(week=>week.start===start)?.records?.[maidId],days=snapshot?.days||fixture?.submitted;
  4894 |         if(!days)return 'missing';
  4895 |         return days.includes(dayIndex)?'available':'unavailable';
  4896 |       }
  4897 |       function assignmentDayIndex() {
  4898 |         return weekdayIndex(state.assignmentDate||state.selectedDate);
  4899 |       }
  4900 |       function weekdayIndex(iso=state.selectedDate) {
  4901 |         const [year,month,day]=String(iso).split('-').map(Number),value=new Date(Date.UTC(year,month-1,day)).getUTCDay();
  4902 |         return (value+6)%7;
  4903 |       }
  4904 |       const AVAILABILITY_SUBMISSION_DATE='2026-08-16',AVAILABILITY_OPEN_TIME='12:00',AVAILABILITY_CLOSE_TIME='23:59';
  4905 |       function availabilitySubmissionWindowLabel() { return `일요일 ${AVAILABILITY_OPEN_TIME}부터 ${AVAILABILITY_CLOSE_TIME}까지`; }
  4906 |       function availabilitySubmissionPhase() {
  4907 |         const minutes=timeMinutes(state.time),openingMinutes=timeMinutes(AVAILABILITY_OPEN_TIME),closingMinutes=timeMinutes(AVAILABILITY_CLOSE_TIME);
  4908 |         if(state.selectedDate<AVAILABILITY_SUBMISSION_DATE||(state.selectedDate===AVAILABILITY_SUBMISSION_DATE&&minutes<openingMinutes))return 'before';
  4909 |         if(state.selectedDate===AVAILABILITY_SUBMISSION_DATE&&minutes<=closingMinutes)return 'open';
  4910 |         return 'closed';
  4911 |       }
  4912 |       function availabilityCell(maidId,dayIndex,iso=addIsoDays(weekStartIso(state.assignmentDate),dayIndex)) {
  4913 |         const value=availabilityForWorkDate(maidId,iso),label=value==='available'?'근무 가능':value==='unavailable'?'근무 불가':'미제출',day=['월','화','수','목','금','토','일'][dayIndex];
  4914 |         return `<span class="availability-cell ${value}" role="img" aria-label="${esc(maidName(maidId))} ${day}요일 ${label}"><span aria-hidden="true">${value==='available'?'✓':value==='unavailable'?'×':'—'}</span></span>`;
  4915 |       }
  4916 |       function targetPlanDate(item,fallback=state.assignmentDate) { return item?.planDate||item?.date||fallback; }
  4917 |       function targetEffectiveDate(item,fallback=state.assignmentDate) { return item?.effectiveDate||item?.date||targetPlanDate(item,fallback); }
  4918 |       function isCleaningAssignmentTab(tab=state.cleaningTab) { return ['assignment-today','assignment-tomorrow','assignment'].includes(tab); }
  4919 |       function assignmentDateForCleaningTab(targetState=state,tab=targetState.cleaningTab) { return tab==='assignment-tomorrow'||tab==='assignment'?addIsoDays(targetState.selectedDate,1):targetState.selectedDate; }
  4920 |       function syncAssignmentDateForCleaningTab(targetState=state) {
  4921 |         if(isCleaningAssignmentTab(targetState.cleaningTab))targetState.assignmentDate=assignmentDateForCleaningTab(targetState);
  4922 |         return targetState.assignmentDate;
  4923 |       }
  4924 |       function cleaningTargetObligationKey(item) {
  4925 |         if(item?.obligationKey)return item.obligationKey;
  4926 |         if(item?.reservationId)return `reservation:${item.reservationId}:${item.kind||'퇴실 청소'}`;
  4927 |         return `room:${item?.room||'unknown'}:${item?.kind||'퇴실 청소'}:${targetPlanDate(item,'')}`;
  4928 |       }
  4929 |       function cleaningTargetSnapshot(item,fallbackDate=state.assignmentDate) {
  4930 |         const planDate=targetPlanDate(item,fallbackDate),effectiveDate=targetEffectiveDate(item,fallbackDate);
  4931 |         return {...item,planDate,effectiveDate,date:planDate,obligationKey:cleaningTargetObligationKey({...item,planDate})};
  4932 |       }
  4933 |       function cleaningTargetOperationalSnapshot(item,fallbackDate=state.assignmentDate) {
  4934 |         const snapshot=cleaningTargetSnapshot(item,fallbackDate);['closed','closedAt','closedBy','closeReasonCode','closeReason','closeStatus','closeHistory','reopenedAt','reopenReason'].forEach(key=>delete snapshot[key]);return snapshot;
  4935 |       }
  4936 |       function reopenCancelledAssignmentForNewReservation(targetState,item,{allowSameReservation=false}={}) {
  4937 |         const key=item?.id,record=key?targetState.assignments?.[key]:null;
  4938 |         const sameReservation=!!record&&!!item?.reservationId&&(record.cancelledReservationId||null)===item.reservationId;if(!record||record.status!=='cancelled'||!item.reservationId||sameReservation&&!allowSameReservation)return record;
  4939 |         const cancellationRevision={cancelledAt:record.cancelledAt||null,cancelledBy:record.cancelledBy||null,cancelledMaidId:record.cancelledMaidId||null,cancelledNotifiedMaidId:record.cancelledNotifiedMaidId||null,cancelledOrder:record.cancelledOrder??null,cancelledPreviousOrder:record.cancelledPreviousOrder??null,cancelledStatus:record.cancelledStatus||null,cancelReasonCode:record.cancelReasonCode||null,cancelReason:record.cancelReason||record.cancelledReason||null,notifiedAt:record.cancelledNotifiedAt||record.notifiedAt||null,notificationRevision:record.cancelledNotificationRevision??record.notificationRevision??null,committedTarget:record.cancelledTarget||record.committedTarget||null,cancelledReservationId:record.cancelledReservationId||null};
  4940 |         const reopened={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]};targetState.assignments[key]=reopened;
  4941 |         const ledger=targetState.cleaningTargets?.[key]||null,closeRevision=ledger?{closedAt:ledger.closedAt||null,closedBy:ledger.closedBy||null,closeReasonCode:ledger.closeReasonCode||null,closeReason:ledger.closeReason||null,closeStatus:ledger.closeStatus||null,target:cleaningTargetOperationalSnapshot(ledger,targetState.assignmentDate)}:null;
  4942 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};targetState.cleaningTargets[key]={...cleaningTargetSnapshot(item,targetState.assignmentDate),closed:false,reopenedAt:`${targetState.selectedDate||state.selectedDate} ${targetState.time||state.time}`,reopenReason:'새 예약 청소 의무',closeHistory:[...(ledger?.closeHistory||[]),...(closeRevision?[closeRevision]:[])]};
  4943 |         return reopened;
  4944 |       }
  4945 |       function reopenCancelledManualCleaningTarget(item,reopenReason='관리자 직접 다시 추가') {
  4946 |         const manual=(state.manualAssignmentTargets||[]).find(target=>target.id===item?.id),record=item?.id?state.assignments?.[item.id]:null;
  4947 |         if(!manual||!record||record.status!=='cancelled')return false;
  4948 |         Object.assign(manual,item);delete manual.cancelled;delete manual.cancelledAt;delete manual.cancelledBy;delete manual.closeReasonCode;delete manual.closeReason;
  4949 |         const cancellationRevision={cancelledAt:record.cancelledAt||null,cancelledBy:record.cancelledBy||null,cancelledMaidId:record.cancelledMaidId||null,cancelledNotifiedMaidId:record.cancelledNotifiedMaidId||null,cancelledOrder:record.cancelledOrder??null,cancelledPreviousOrder:record.cancelledPreviousOrder??null,cancelledStatus:record.cancelledStatus||null,cancelReasonCode:record.cancelReasonCode||null,cancelReason:record.cancelReason||record.cancelledReason||null,notifiedAt:record.cancelledNotifiedAt||record.notifiedAt||null,notificationRevision:record.cancelledNotificationRevision??record.notificationRevision??null,committedTarget:record.cancelledTarget||record.committedTarget||null,cancelledReservationId:record.cancelledReservationId||null};
  4950 |         state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]};
  4951 |         const closedTarget=state.cleaningTargets?.[item.id]||{},closeRevision={closedAt:closedTarget.closedAt||null,closedBy:closedTarget.closedBy||null,closeReasonCode:closedTarget.closeReasonCode||null,closeReason:closedTarget.closeReason||null,closeStatus:closedTarget.closeStatus||null,target:cleaningTargetOperationalSnapshot(closedTarget,targetPlanDate(item,state.assignmentDate))};
  4952 |         state.cleaningTargets[item.id]={...cleaningTargetSnapshot(item,targetPlanDate(item,state.assignmentDate)),closed:false,reopenedAt:`${state.selectedDate} ${state.time}`,reopenReason,closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]};
  4953 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:item.id,assignmentDate:targetEffectiveDate(item),room:item.room,beforeMaidId:null,afterMaidId:null,before:'청소 대상 취소',after:'미배정',reason:`${reopenReason} · 취소 이력 보존`});
  4954 |         return true;
  4955 |       }
  4956 |       function initializeCleaningTargetLedger(targetState) {
  4957 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};
  4958 |         const live=liveAssignmentTargetsForState(targetState),committed=Object.values(targetState.assignments||{}).map(record=>record?.committedTarget).filter(Boolean),attemptTargets=Object.entries(targetState.currentAttemptByRoom||{}).map(([roomNo,attemptId])=>{
  4959 |           const attempt=targetState.cleaningAttempts?.[attemptId],room=ROOMS.find(item=>item.no===roomNo);if(!attempt||attempt.status==='superseded'||!attempt.workTargetId)return null;
  4960 |           const planDate=attemptPlanDate(attempt,targetState.selectedDate),effectiveDate=attemptEffectiveDate(attempt,planDate);
  4961 |           const checkout=attempt.checkoutSnapshot||attempt.accessStart||room?.actualCheckoutAt?.slice(11,16)||DEFAULT_CHECKOUT_TIME;
  4962 |           return {id:attempt.workTargetId,currentAttemptId:attempt.id,room:roomNo,type:attempt.roomMetaSnapshot?.typeId||room?.type||'standard',kind:attempt.kind||'퇴실 청소',date:planDate,planDate,effectiveDate,checkout,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||shiftClockTime(attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,-30)||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||attempt.checkoutSnapshot||null,requestDue:attempt.requestDue||null,accessEnd:attempt.accessEnd||null,reservationId:attempt.reservationIdSnapshot||null,guestCount:attempt.guestCountSnapshot??null,source:'attempt',sourceLabel:'수행 회차',rateSnapshot:attempt.baseRateSnapshot||null,minutesSnapshot:attempt.templateSnapshot?.minutes||ROOM_TYPES[room?.type||'standard'].minutes,elevatorSnapshot:attempt.roomMetaSnapshot?.elevator??room?.elevator??null};
  4963 |         }).filter(Boolean);
  4964 |         [...attemptTargets,...live,...committed].forEach(item=>{if(!item?.id)return;const existing=targetState.cleaningTargets[item.id];targetState.cleaningTargets[item.id]=existing?{...cleaningTargetSnapshot(item,targetState.assignmentDate),...existing}:cleaningTargetSnapshot(item,targetState.assignmentDate);});
  4965 |         return targetState.cleaningTargets;
  4966 |       }
  4967 |       function attemptForCleaningTarget(target,targetState=state) {
  4968 |         const attempts=targetState.cleaningAttempts||{},matches=attempt=>attempt?.workTargetId===target.id&&attempt.status!=='superseded',currentId=targetState.currentAttemptByRoom?.[target.room],targetAttemptId=target.currentAttemptId;
  4969 |         if(currentId&&matches(attempts[currentId]))return attempts[currentId];
  4970 |         if(targetAttemptId&&matches(attempts[targetAttemptId]))return attempts[targetAttemptId];
  4971 |         return Object.values(attempts).reverse().find(matches)||null;
  4972 |       }
  4973 |       function cleaningTargetAdjustmentBlock(target) {
  4974 |         if(!target)return '';
  4975 |         const holdReason=assignmentRoomHoldReason(target.room);if(holdReason)return holdReason;
  4976 |         if(target.kind==='재청소')return '재청소는 기존 수행자가 완료해야 합니다.';
  4977 |         if(target.carryReason==='access-review')return 'PIN·출입 영향 확인이 끝난 뒤 조정할 수 있습니다.';
  4978 |         const attempt=attemptForCleaningTarget(target);
  4979 |         const roomAttempt=targetEffectiveDate(target)===state.selectedDate?activeUnfinishedAttempt(target.room):null;
  4980 |         if(roomAttempt&&roomAttempt.workTargetId!==target.id)return roomAttempt.status==='submitted'?'이 객실의 이전 청소 검수가 남아 검수 대기에서 먼저 종결해야 합니다.':'이 객실의 다른 청소가 진행 중이라 청소 상세에서 조정해야 합니다.';
  4981 |         if(!attempt)return '';
  4982 |         if(attempt.startedAt||attempt.completedAt||!['active','scheduled'].includes(attempt.status))return '이미 시작한 청소는 진행 중에서 조정합니다.';
  4983 |         return '';
  4984 |       }
  4985 |       function cleaningTargetCanAdjust(target) { return !cleaningTargetAdjustmentBlock(target); }
  4986 |       function cleaningTargetAdjustmentFingerprint(target) {
  4987 |         const assignment=target?state.assignments?.[target.id]:null,attempt=target?attemptForCleaningTarget(target):null;
```

### occurrence 2 · line 4921

```html
  4876 |         const cancelNo=requestedEntry?.[0]||state.cancelRequestRoom||'332', cancelRequest=requestedEntry?.[1], cancelMaid=cancelRequest?.maid||ROOMS.find(room=>room.no===cancelNo)?.assignee||'김민지1';
  4877 |         const cancelBody=cancelRequested?`<div class="rail-row"><strong>${esc(cancelMaid)} · ${esc(cancelNo)}호</strong><span>${esc(cancelRequest?.reason||'건강상 사유 · 데모')} · 결정 전 담당 유지</span></div><div style="margin-top:10px">${button('요청 처리','cancel-review','danger',isLocked()?'disabled':'')}</div>`:`<div class="rail-row"><strong>처리 완료</strong><span>${state.cancelDecision==='deny'?'거절 · 기존 담당 유지':state.cancelDecision==='republish'?'승인 · 관리자 재배정 대기':state.cancelDecision==='direct'?'승인 · 김민지2 직접 배정':'승인 · 관리자 조치 대기'}</span></div><p class="audit-note">원 요청·사유·결정 이벤트는 감사 이력에 보존됩니다.</p>`;
  4878 |         const cancelAccordion=cancelRequested||cancelResolved?renderAccordion('cancel',cancelRequested?'담당 취소 요청':'담당 취소 처리 결과',cancelRequested?'1건':'처리됨',cancelBody,cancelRequested):'';
  4879 |         const assignmentCountsToday=assignmentCountsForDate(state.selectedDate), assignmentBody=`<div class="rail-row"><strong>${dateLabel(state.selectedDate)} 청소</strong><span>${assignmentCountsToday.assigned}/${assignmentCountsToday.total} 담당 선택 · ${assignmentCountsToday.unassigned}건 미배정</span></div><p class="audit-note">당일 추가·취소와 담당·순서 변경도 관리자만 저장·통보합니다.</p><div style="margin-top:10px">${button('오늘 배정 열기','go-cleaning-assignment',assignmentCountsToday.unassigned?'danger':'outline','data-day="today"')}</div>`;
  4880 |         const content=`<div class="view-stack"><div>${renderDateTools(false)}</div><section aria-labelledby="summary-title" data-admin-home-section="room-summary"><div class="mobile-section-title"><div><h2 id="summary-title">오늘 객실 요약</h2></div></div><div class="today-summary"><button class="card metric-card neutral" type="button" data-action="filter-rooms" data-filter="occupied" aria-label="투숙 중 객실 ${occupiedCount}개 목록 보기"><span>투숙 중</span><strong>${occupiedCount}</strong></button><button class="card metric-card amber" type="button" data-action="filter-rooms" data-filter="cleaning" aria-label="청소 필요 객실 ${cleaningCount}개 목록 보기"><span>청소 필요</span><strong>${cleaningCount}</strong></button><button class="card metric-card green" type="button" data-action="filter-rooms" data-filter="available" aria-label="배정 가능 객실 ${availableCount}개 목록 보기"><span>배정 가능</span><strong>${availableCount}</strong></button><button class="card metric-card red" type="button" data-action="filter-rooms" data-filter="blocked" aria-label="배정 불가 객실 ${blockedCount}개 목록 보기"><span>배정 불가</span><strong>${blockedCount}</strong></button></div></section><div class="accordion-list" data-admin-home-section="cleaning-actions">${renderAccordion('assignment','오늘 청소 배정',`${assignmentCountsToday.unassigned}건 미배정`,assignmentBody,true)}${renderAccordion('inspection','청소 검수','2건',inspectionBody)}</div><div data-admin-home-section="cleaning-cost">${cleaningCostSection}</div></div>`;
  4881 |         return renderCoach()+renderNetworkNotice()+renderScenario13Controls()+renderListState(content);
  4882 |       }
  4883 | 
  4884 |       function maidName(id) { return MAIDS.find(maid=>maid.id===id)?.name||'미배정'; }
  4885 |       function availabilityFor(maidId,dayIndex=0) {
  4886 |         const record=state.weeklyAvailability?.[maidId];
  4887 |         if(!record||!['submitted','change-requested'].includes(record.status))return 'missing';
  4888 |         return record.days.includes(dayIndex)?'available':'unavailable';
  4889 |       }
  4890 |       function availabilityForWorkDate(maidId,iso) {
  4891 |         const start=weekStartIso(iso),dayIndex=weekdayIndex(iso);
  4892 |         if(start==='2026-08-17')return availabilityFor(maidId,dayIndex);
  4893 |         const versions=(state.availabilityHistory||[]).filter(item=>item.maidId===maidId&&item.weekStart===start).sort((left,right)=>left.version-right.version),snapshot=versions.at(-1),fixture=WORK_HISTORY_FIXTURES.find(week=>week.start===start)?.records?.[maidId],days=snapshot?.days||fixture?.submitted;
  4894 |         if(!days)return 'missing';
  4895 |         return days.includes(dayIndex)?'available':'unavailable';
  4896 |       }
  4897 |       function assignmentDayIndex() {
  4898 |         return weekdayIndex(state.assignmentDate||state.selectedDate);
  4899 |       }
  4900 |       function weekdayIndex(iso=state.selectedDate) {
  4901 |         const [year,month,day]=String(iso).split('-').map(Number),value=new Date(Date.UTC(year,month-1,day)).getUTCDay();
  4902 |         return (value+6)%7;
  4903 |       }
  4904 |       const AVAILABILITY_SUBMISSION_DATE='2026-08-16',AVAILABILITY_OPEN_TIME='12:00',AVAILABILITY_CLOSE_TIME='23:59';
  4905 |       function availabilitySubmissionWindowLabel() { return `일요일 ${AVAILABILITY_OPEN_TIME}부터 ${AVAILABILITY_CLOSE_TIME}까지`; }
  4906 |       function availabilitySubmissionPhase() {
  4907 |         const minutes=timeMinutes(state.time),openingMinutes=timeMinutes(AVAILABILITY_OPEN_TIME),closingMinutes=timeMinutes(AVAILABILITY_CLOSE_TIME);
  4908 |         if(state.selectedDate<AVAILABILITY_SUBMISSION_DATE||(state.selectedDate===AVAILABILITY_SUBMISSION_DATE&&minutes<openingMinutes))return 'before';
  4909 |         if(state.selectedDate===AVAILABILITY_SUBMISSION_DATE&&minutes<=closingMinutes)return 'open';
  4910 |         return 'closed';
  4911 |       }
  4912 |       function availabilityCell(maidId,dayIndex,iso=addIsoDays(weekStartIso(state.assignmentDate),dayIndex)) {
  4913 |         const value=availabilityForWorkDate(maidId,iso),label=value==='available'?'근무 가능':value==='unavailable'?'근무 불가':'미제출',day=['월','화','수','목','금','토','일'][dayIndex];
  4914 |         return `<span class="availability-cell ${value}" role="img" aria-label="${esc(maidName(maidId))} ${day}요일 ${label}"><span aria-hidden="true">${value==='available'?'✓':value==='unavailable'?'×':'—'}</span></span>`;
  4915 |       }
  4916 |       function targetPlanDate(item,fallback=state.assignmentDate) { return item?.planDate||item?.date||fallback; }
  4917 |       function targetEffectiveDate(item,fallback=state.assignmentDate) { return item?.effectiveDate||item?.date||targetPlanDate(item,fallback); }
  4918 |       function isCleaningAssignmentTab(tab=state.cleaningTab) { return ['assignment-today','assignment-tomorrow','assignment'].includes(tab); }
  4919 |       function assignmentDateForCleaningTab(targetState=state,tab=targetState.cleaningTab) { return tab==='assignment-tomorrow'||tab==='assignment'?addIsoDays(targetState.selectedDate,1):targetState.selectedDate; }
  4920 |       function syncAssignmentDateForCleaningTab(targetState=state) {
  4921 |         if(isCleaningAssignmentTab(targetState.cleaningTab))targetState.assignmentDate=assignmentDateForCleaningTab(targetState);
  4922 |         return targetState.assignmentDate;
  4923 |       }
  4924 |       function cleaningTargetObligationKey(item) {
  4925 |         if(item?.obligationKey)return item.obligationKey;
  4926 |         if(item?.reservationId)return `reservation:${item.reservationId}:${item.kind||'퇴실 청소'}`;
  4927 |         return `room:${item?.room||'unknown'}:${item?.kind||'퇴실 청소'}:${targetPlanDate(item,'')}`;
  4928 |       }
  4929 |       function cleaningTargetSnapshot(item,fallbackDate=state.assignmentDate) {
  4930 |         const planDate=targetPlanDate(item,fallbackDate),effectiveDate=targetEffectiveDate(item,fallbackDate);
  4931 |         return {...item,planDate,effectiveDate,date:planDate,obligationKey:cleaningTargetObligationKey({...item,planDate})};
  4932 |       }
  4933 |       function cleaningTargetOperationalSnapshot(item,fallbackDate=state.assignmentDate) {
  4934 |         const snapshot=cleaningTargetSnapshot(item,fallbackDate);['closed','closedAt','closedBy','closeReasonCode','closeReason','closeStatus','closeHistory','reopenedAt','reopenReason'].forEach(key=>delete snapshot[key]);return snapshot;
  4935 |       }
  4936 |       function reopenCancelledAssignmentForNewReservation(targetState,item,{allowSameReservation=false}={}) {
  4937 |         const key=item?.id,record=key?targetState.assignments?.[key]:null;
  4938 |         const sameReservation=!!record&&!!item?.reservationId&&(record.cancelledReservationId||null)===item.reservationId;if(!record||record.status!=='cancelled'||!item.reservationId||sameReservation&&!allowSameReservation)return record;
  4939 |         const cancellationRevision={cancelledAt:record.cancelledAt||null,cancelledBy:record.cancelledBy||null,cancelledMaidId:record.cancelledMaidId||null,cancelledNotifiedMaidId:record.cancelledNotifiedMaidId||null,cancelledOrder:record.cancelledOrder??null,cancelledPreviousOrder:record.cancelledPreviousOrder??null,cancelledStatus:record.cancelledStatus||null,cancelReasonCode:record.cancelReasonCode||null,cancelReason:record.cancelReason||record.cancelledReason||null,notifiedAt:record.cancelledNotifiedAt||record.notifiedAt||null,notificationRevision:record.cancelledNotificationRevision??record.notificationRevision??null,committedTarget:record.cancelledTarget||record.committedTarget||null,cancelledReservationId:record.cancelledReservationId||null};
  4940 |         const reopened={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]};targetState.assignments[key]=reopened;
  4941 |         const ledger=targetState.cleaningTargets?.[key]||null,closeRevision=ledger?{closedAt:ledger.closedAt||null,closedBy:ledger.closedBy||null,closeReasonCode:ledger.closeReasonCode||null,closeReason:ledger.closeReason||null,closeStatus:ledger.closeStatus||null,target:cleaningTargetOperationalSnapshot(ledger,targetState.assignmentDate)}:null;
  4942 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};targetState.cleaningTargets[key]={...cleaningTargetSnapshot(item,targetState.assignmentDate),closed:false,reopenedAt:`${targetState.selectedDate||state.selectedDate} ${targetState.time||state.time}`,reopenReason:'새 예약 청소 의무',closeHistory:[...(ledger?.closeHistory||[]),...(closeRevision?[closeRevision]:[])]};
  4943 |         return reopened;
  4944 |       }
  4945 |       function reopenCancelledManualCleaningTarget(item,reopenReason='관리자 직접 다시 추가') {
  4946 |         const manual=(state.manualAssignmentTargets||[]).find(target=>target.id===item?.id),record=item?.id?state.assignments?.[item.id]:null;
  4947 |         if(!manual||!record||record.status!=='cancelled')return false;
  4948 |         Object.assign(manual,item);delete manual.cancelled;delete manual.cancelledAt;delete manual.cancelledBy;delete manual.closeReasonCode;delete manual.closeReason;
  4949 |         const cancellationRevision={cancelledAt:record.cancelledAt||null,cancelledBy:record.cancelledBy||null,cancelledMaidId:record.cancelledMaidId||null,cancelledNotifiedMaidId:record.cancelledNotifiedMaidId||null,cancelledOrder:record.cancelledOrder??null,cancelledPreviousOrder:record.cancelledPreviousOrder??null,cancelledStatus:record.cancelledStatus||null,cancelReasonCode:record.cancelReasonCode||null,cancelReason:record.cancelReason||record.cancelledReason||null,notifiedAt:record.cancelledNotifiedAt||record.notifiedAt||null,notificationRevision:record.cancelledNotificationRevision??record.notificationRevision??null,committedTarget:record.cancelledTarget||record.committedTarget||null,cancelledReservationId:record.cancelledReservationId||null};
  4950 |         state.assignments[item.id]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(record.cancellationHistory||[]),cancellationRevision]};
  4951 |         const closedTarget=state.cleaningTargets?.[item.id]||{},closeRevision={closedAt:closedTarget.closedAt||null,closedBy:closedTarget.closedBy||null,closeReasonCode:closedTarget.closeReasonCode||null,closeReason:closedTarget.closeReason||null,closeStatus:closedTarget.closeStatus||null,target:cleaningTargetOperationalSnapshot(closedTarget,targetPlanDate(item,state.assignmentDate))};
  4952 |         state.cleaningTargets[item.id]={...cleaningTargetSnapshot(item,targetPlanDate(item,state.assignmentDate)),closed:false,reopenedAt:`${state.selectedDate} ${state.time}`,reopenReason,closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]};
  4953 |         state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:item.id,assignmentDate:targetEffectiveDate(item),room:item.room,beforeMaidId:null,afterMaidId:null,before:'청소 대상 취소',after:'미배정',reason:`${reopenReason} · 취소 이력 보존`});
  4954 |         return true;
  4955 |       }
  4956 |       function initializeCleaningTargetLedger(targetState) {
  4957 |         if(!targetState.cleaningTargets)targetState.cleaningTargets={};
  4958 |         const live=liveAssignmentTargetsForState(targetState),committed=Object.values(targetState.assignments||{}).map(record=>record?.committedTarget).filter(Boolean),attemptTargets=Object.entries(targetState.currentAttemptByRoom||{}).map(([roomNo,attemptId])=>{
  4959 |           const attempt=targetState.cleaningAttempts?.[attemptId],room=ROOMS.find(item=>item.no===roomNo);if(!attempt||attempt.status==='superseded'||!attempt.workTargetId)return null;
  4960 |           const planDate=attemptPlanDate(attempt,targetState.selectedDate),effectiveDate=attemptEffectiveDate(attempt,planDate);
  4961 |           const checkout=attempt.checkoutSnapshot||attempt.accessStart||room?.actualCheckoutAt?.slice(11,16)||DEFAULT_CHECKOUT_TIME;
  4962 |           return {id:attempt.workTargetId,currentAttemptId:attempt.id,room:roomNo,type:attempt.roomMetaSnapshot?.typeId||room?.type||'standard',kind:attempt.kind||'퇴실 청소',date:planDate,planDate,effectiveDate,checkout,checkin:attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,deadline:attempt.deadlineSnapshot||shiftClockTime(attempt.checkinSnapshot||DEFAULT_CHECKIN_TIME,-30)||'15:30',nextReservationId:attempt.nextReservationIdSnapshot||null,accessStart:attempt.accessStart||attempt.checkoutSnapshot||null,requestDue:attempt.requestDue||null,accessEnd:attempt.accessEnd||null,reservationId:attempt.reservationIdSnapshot||null,guestCount:attempt.guestCountSnapshot??null,source:'attempt',sourceLabel:'수행 회차',rateSnapshot:attempt.baseRateSnapshot||null,minutesSnapshot:attempt.templateSnapshot?.minutes||ROOM_TYPES[room?.type||'standard'].minutes,elevatorSnapshot:attempt.roomMetaSnapshot?.elevator??room?.elevator??null};
  4963 |         }).filter(Boolean);
  4964 |         [...attemptTargets,...live,...committed].forEach(item=>{if(!item?.id)return;const existing=targetState.cleaningTargets[item.id];targetState.cleaningTargets[item.id]=existing?{...cleaningTargetSnapshot(item,targetState.assignmentDate),...existing}:cleaningTargetSnapshot(item,targetState.assignmentDate);});
  4965 |         return targetState.cleaningTargets;
  4966 |       }
  4967 |       function attemptForCleaningTarget(target,targetState=state) {
  4968 |         const attempts=targetState.cleaningAttempts||{},matches=attempt=>attempt?.workTargetId===target.id&&attempt.status!=='superseded',currentId=targetState.currentAttemptByRoom?.[target.room],targetAttemptId=target.currentAttemptId;
  4969 |         if(currentId&&matches(attempts[currentId]))return attempts[currentId];
  4970 |         if(targetAttemptId&&matches(attempts[targetAttemptId]))return attempts[targetAttemptId];
  4971 |         return Object.values(attempts).reverse().find(matches)||null;
  4972 |       }
  4973 |       function cleaningTargetAdjustmentBlock(target) {
  4974 |         if(!target)return '';
  4975 |         const holdReason=assignmentRoomHoldReason(target.room);if(holdReason)return holdReason;
  4976 |         if(target.kind==='재청소')return '재청소는 기존 수행자가 완료해야 합니다.';
  4977 |         if(target.carryReason==='access-review')return 'PIN·출입 영향 확인이 끝난 뒤 조정할 수 있습니다.';
  4978 |         const attempt=attemptForCleaningTarget(target);
  4979 |         const roomAttempt=targetEffectiveDate(target)===state.selectedDate?activeUnfinishedAttempt(target.room):null;
  4980 |         if(roomAttempt&&roomAttempt.workTargetId!==target.id)return roomAttempt.status==='submitted'?'이 객실의 이전 청소 검수가 남아 검수 대기에서 먼저 종결해야 합니다.':'이 객실의 다른 청소가 진행 중이라 청소 상세에서 조정해야 합니다.';
  4981 |         if(!attempt)return '';
  4982 |         if(attempt.startedAt||attempt.completedAt||!['active','scheduled'].includes(attempt.status))return '이미 시작한 청소는 진행 중에서 조정합니다.';
  4983 |         return '';
  4984 |       }
  4985 |       function cleaningTargetCanAdjust(target) { return !cleaningTargetAdjustmentBlock(target); }
  4986 |       function cleaningTargetAdjustmentFingerprint(target) {
  4987 |         const assignment=target?state.assignments?.[target.id]:null,attempt=target?attemptForCleaningTarget(target):null;
  4988 |         return [target?.id||'',target?targetEffectiveDate(target):'',target?.reservationId||'',target?cleaningTargetObligationKey(target):'',target?.kind||'',target?.checkout||'',target?.checkin||'',target?.deadline||'',assignment?.status||'',assignment?.maidId||'',assignment?.order??'',assignment?.previousMaidId||'',assignment?.previousOrder??'',attempt?.id||'',attempt?.status||'',attempt?.startedAt||'',attempt?.completedAt||'',state.currentAttemptByRoom?.[target?.room]||''].join('|');
  4989 |       }
  4990 |       function rolloverUnresolvedTargets(targetState,toDate) {
```

### occurrence 3 · line 5392

```html
  5347 |         const cls=item.source==='manual'?'manual':item.source==='stayover'?'stayover':'',label=item.sourceLabel||'직접 등록';
  5348 |         const rollover=item.carryReason?`<span class="assignment-source stayover">${icon('clock','icon-sm')}${item.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료'}</span>`:'';
  5349 |         return `${rollover}<span class="assignment-source ${cls}">${icon(item.source==='manual'?'user':'sync','icon-sm')}${item.source==='manual'?'직접 등록':`자동 · ${esc(label)}`}</span>`;
  5350 |       }
  5351 |       function assignmentAdjustmentMarkup(item) {
  5352 |         const assignment=assignmentFor(item),activationBlocked=!!assignment.activationBlockedBy&&targetEffectiveDate(item)===state.selectedDate,status=activationBlocked?'활성화 보류':assignment.status==='notified'?'통보 완료':assignment.maidId?'저장 전':'미배정',tone=activationBlocked?'amber':assignment.status==='notified'?'green':assignment.maidId?'amber':'red',notified=!!(assignment.previousMaidId||assignment.status==='notified'),block=cleaningTargetAdjustmentBlock(item),label=notified?'청소 취소·통보':'청소대상 취소';
  5353 |         return `<div class="assignment-cell-stack">${statusBadge(status,tone)}${assignment.maidId?'<span class="cell-sub">순서 보드 반영</span>':''}${button(label,'cancel-cleaning-target','outline',`data-target="${esc(item.id)}" aria-label="${esc(dateLabel(targetEffectiveDate(item)))} ${item.room}호 ${esc(label)}" ${block?'disabled':''}`)}${block?`<span class="cell-sub">${esc(block)}</span>`:''}</div>`;
  5354 |       }
  5355 |       function renderAssignmentDashboard() {
  5356 |         const counts=assignmentCounts(),targets=assignmentTargets(),visibleTargets=filteredAssignmentTargets(),activeType=state.assignmentTypeFilter==='all'?null:ROOM_TYPES[state.assignmentTypeFilter];
  5357 |         const rows=visibleTargets.map(item=>{const context=assignmentContext(item),adjustmentBlock=cleaningTargetAdjustmentBlock(item);return `<tr><td data-label="객실·타입·요금"><div class="assignment-cell-stack"><strong>${item.room}호</strong><span class="assignment-room-type">${esc(context.type.name)}</span><span class="assignment-elevator">${icon('mapPin','icon-sm')}${esc(elevatorLabel(context.room))}</span><span class="assignment-fee">${money(context.type.rate)} · 8월 시트</span></div></td><td data-label="청소 정보"><div class="assignment-cell-stack"><strong>${esc(item.kind)}</strong>${assignmentSourceMarkup(item)}</div></td><td data-label="일정">${assignmentScheduleMarkup(item)}</td><td data-label="담당 메이드"><div class="assignment-assignee"><select class="select-control" data-control="assignment-maid" data-location="table" data-target="${esc(item.id)}" aria-label="${item.room}호 ${esc(item.kind)} 담당 메이드 · 근무 가능 제출자만 표시" ${adjustmentBlock?'disabled':''}>${assignmentOptions(item)}</select>${assignmentRouteReference(item)}</div></td><td data-label="상태·조정">${assignmentAdjustmentMarkup(item)}</td></tr>`;}).join('');
  5358 |         const history=state.assignmentHistory.map(entry=>`<div class="assignment-history-row"><strong>${esc(entry.time)}</strong><span>${esc(entry.room)}호</span><span>${esc(entry.before)} → ${esc(entry.after)}</span><span>${esc(entry.reason)}</span></div>`).join('');
  5359 |         const emptyRows=`<tr><td colspan="5"><div class="inline-empty"><h3>이 타입의 청소대상이 없습니다</h3><p>다른 타입을 선택하거나 전체 객실을 확인하세요.</p></div></td></tr>`;
  5360 |         const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일',weekStart=weekStartIso(state.assignmentDate),weekEnd=addIsoDays(weekStart,6);
  5361 |         return `<div class="assignment-page"><div class="assignment-intro"><div><h2>${dayWord} 청소 배정</h2><p>${dateLabel(state.assignmentDate)} · 근무표 확인 → 동선 고려 랜덤 초안 → 담당·순서 수정 → 저장·통보</p></div><div class="job-actions">${button('주간 근무 기록','go-work-history','outline')}${button(`${dayWord} 청소 추가`,'new-cleaning','outline')}</div></div><section class="card assignment-summary"><div><span>근무 가능일 제출</span><strong>${counts.submitted} / ${MAIDS.length}</strong><small>메이드 제출 현황</small></div><div><span>${dayWord} 청소 대상 객실</span><strong>${counts.total}</strong><small>전일 이월 ${counts.carryover} · 신규 ${counts.total-counts.carryover}</small></div><div class="summary-good"><span>담당 선택</span><strong>${counts.assigned}</strong><small>통보 완료 ${counts.notified}건</small></div><div class="summary-warn"><span>미배정</span><strong>${counts.unassigned}</strong><small>대기 유지 · 후속 배정 가능</small></div></section><section class="assignment-target-rule" aria-label="청소대상 자동 구성">${icon('sync')}<div><strong>${dayWord} 체크아웃·투숙 중 청소·전일 이월 객실을 한 목록에 모읍니다.</strong><p>${dayWord} 생긴 현장 요청은 직접 추가하고, 미시작 대상은 사유를 남겨 취소·통보할 수 있습니다.</p></div><div class="badge-row">${statusBadge(`전일 이월 ${counts.carryover}`,'amber')}${statusBadge(`체크아웃 ${counts.checkout}`,'blue')}${statusBadge(`연박 ${counts.stayover}`,'neutral')}${statusBadge(`직접 ${counts.manual}`,'amber')}</div></section><section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">1단계</span><h3>메이드 주간 근무표</h3><p>${dateLabel(weekStart)}–${dateLabel(weekEnd)} · Asia/Seoul</p></div>${statusBadge(`${counts.submitted}/${MAIDS.length} 제출`,counts.submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section>${renderRandomAssignmentCard()}<section class="card assignment-panel"><div class="assignment-panel-head"><div><span class="assignment-step-label">3단계 · 세부 수정</span><h3>객실별 담당 수정</h3><p>랜덤 초안 뒤 필요한 객실만 조정합니다. 얼리·레이트·연박 일정은 해당 객실 행에서 함께 확인합니다.</p></div>${statusBadge(`${visibleTargets.length}/${targets.length}건 표시`,'blue')}</div>${assignmentTypeFiltersMarkup()}<div class="assignment-filter-context">${icon('filter','icon-sm')}<span><strong>${activeType?esc(activeType.name):'전체 객실 타입'}</strong> ${visibleTargets.length}건 표시 · 전체 ${targets.length}건 현황을 유지하며 배정된 객실만 통보합니다.</span></div><div class="assignment-table-wrap"><table class="assignment-table"><thead><tr><th scope="col">객실·타입·요금</th><th scope="col">청소 정보·등록 근거</th><th scope="col">일정</th><th scope="col">담당 메이드</th><th scope="col">상태·조정</th></tr></thead><tbody>${rows||emptyRows}</tbody></table></div><div class="assignment-foot"><p>담당을 바꾸면 해당 객실이 새 메이드 순서의 마지막으로 이동합니다. 이미 시작한 청소는 진행 중 탭에서 관리합니다.</p></div></section>${renderMaidOrderBoardContent()}<section class="card assignment-history"><div class="assignment-panel-head"><div><h3>배정·순서 통보 이력</h3><p>담당과 청소 순서의 이전 값을 덮어쓰지 않고 변경 이력을 추가합니다.</p></div>${statusBadge('관리자 전용','neutral')}</div><div class="assignment-history-list">${history}</div></section></div>`;
  5362 |       }
  5363 |       function cleaningTabButton(id,label,count) { return `<button type="button" role="tab" data-action="cleaning-tab" data-tab="${id}" aria-selected="${state.cleaningTab===id}">${label} ${count}</button>`; }
  5364 |       function rolloverMetaForRoom(no) {
  5365 |         const attempt=state.cleaningAttempts?.[currentAttemptId(no)];if(attemptIsRollover(attempt))return {carryReason:attempt.carryReason||'started-unfinished',planDate:attemptPlanDate(attempt),effectiveDate:attemptEffectiveDate(attempt),rolloverCount:Number(attempt.rolloverCount)||1};
  5366 |         const target=Object.values(state.cleaningTargets||{}).find(item=>item.room===no&&item.carryReason&&!item.closed);return target?{carryReason:target.carryReason,planDate:targetPlanDate(target),effectiveDate:targetEffectiveDate(target),rolloverCount:Number(target.rolloverCount)||1}:null;
  5367 |       }
  5368 |       function rolloverBadgeMarkup(meta,{compact=false}={}) {
  5369 |         if(!meta)return '';
  5370 |         const label=meta.carryReason==='unassigned'?'전일 이월 · 미배정':'전일 이월 · 미완료',detail=`원 계획 ${dateLabel(meta.planDate)} · 이월 ${meta.rolloverCount}일째`;
  5371 |         return `<div class="badge-row${compact?' compact':''}" style="margin-top:7px">${statusBadge(label,'amber')}<span class="cell-sub">${esc(detail)}</span></div>`;
  5372 |       }
  5373 |       function cleaningProgressEntries() {
  5374 |         const allowed=['scheduled','claimed','cleaning','upload','reclean','hold'];
  5375 |         return Object.entries(state.jobs).filter(([no,job])=>{
  5376 |           if(!allowed.includes(job))return false;
  5377 |           const rollover=rolloverMetaForRoom(no);
  5378 |           return !rollover||rollover.carryReason==='started-unfinished'||!!activeUnfinishedAttempt(no);
  5379 |         });
  5380 |       }
  5381 |       function renderCleaningHub() {
  5382 |         const todayDate=state.selectedDate,tomorrowDate=addIsoDays(state.selectedDate,1),tabCounts={today:assignmentCountsForDate(todayDate).total,tomorrow:assignmentCountsForDate(tomorrowDate).total,progress:cleaningProgressEntries().length,inspection:Object.values(state.jobs).filter(v=>v==='inspection').length,done:Object.values(state.jobs).filter(v=>v==='approved').length};
  5383 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>청소 관리</h2><p>오늘 운영 조정과 내일 사전 배정을 분리하고, 변경 내용은 해당 메이드에게 다시 알립니다.</p></div></div><div class="tabs" role="tablist" aria-label="청소 상태">${cleaningTabButton('assignment-today','오늘 배정',tabCounts.today)}${cleaningTabButton('assignment-tomorrow','내일 배정',tabCounts.tomorrow)}${cleaningTabButton('progress','진행 중',tabCounts.progress)}${cleaningTabButton('inspection','검수 대상 목록',tabCounts.inspection)}${cleaningTabButton('done','완료',tabCounts.done)}</div>${renderListState(renderCleaningTab())}</div>`;
  5384 |       }
  5385 |       function taskRow(no,job,extra='') {
  5386 |         const room=ROOMS.find(r=>r.no===no),liveType=ROOM_TYPES[room?.type||'standard'],validSubmission=currentSubmission(no),submittedContext=['inspection','approved'].includes(job),submission=submittedContext?(validSubmission||currentSubmissionRecord(no)):validSubmission,submissionMeta=submission?.roomMetaSnapshot,displayType=submittedContext?(ROOM_TYPES[submissionMeta?.typeId]||liveType):liveType,displayTypeName=submittedContext?(submissionMeta?.typeName||displayType.name):displayType.name,displayElevator=submittedContext?(submissionMeta?.elevator?`${submissionMeta.elevator} 엘리베이터`:'엘리베이터 미기재'):elevatorLabel(room),activeAttempt=state.cleaningAttempts?.[currentAttemptId(no)],rollover=rolloverMetaForRoom(no),report=submittedContext?(validSubmission?submittedBombRoomReport(no):rawBombRoomReportForSubmission(submission)):activeBombRoomReport(no),record=submittedContext?earningRecordFor(no):earningRecordForReport(report),wholeRejected=submittedContext&&submission?.status==='rejected',unpaidReclean=submittedContext?submission?.kind==='재청소':activeAttempt?.kind==='재청소',bombMeta=wholeRejected?{label:'청소 전체 반려 · 적립 없음',tone:'red'}:bombRoomStatusMeta(report),fee=record||bombRoomBreakdown(no,{pendingAsBonus:!unpaidReclean&&(submittedContext?submission?.status==='pending':true)&&report?.status==='pending',reportOverride:report,baseOverride:submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot}),performer=submittedContext?submission?.performerName:room?.assignee;
  5387 |         const displayRate=unpaidReclean?0:record?.base??(submittedContext?submission?.baseRateSnapshot:activeAttempt?.baseRateSnapshot)??displayType.rate,displayKind=(submittedContext?submission?.kind:activeAttempt?.kind)||(job==='reclean'?'재청소':'퇴실 청소');
  5388 |         const action=job==='inspection'?['전체 검수','cleaning-detail']:job==='approved'?['결과 보기','cleaning-detail']:['진행 보기','cleaning-detail'];
  5389 |         return `<article class="card task-row"><div><h3>${no}호 · ${esc(displayKind)} · ${statusLabel(job)}</h3><p>${esc(displayTypeName)} · ${esc(displayElevator)} · ${money(displayRate)} · ${submission?.templateSnapshot?.minutes??displayType.minutes}분 · 데모</p>${rolloverBadgeMarkup(rollover,{compact:true})}${submittedContext&&!validSubmission?`<div class="badge-row" style="margin-top:7px">${statusBadge('제출 연결 확인 필요','red')}</div>`:''}${report?`<div class="badge-row" style="margin-top:7px">${statusBadge(bombMeta.label,bombMeta.tone)}<span class="cell-sub">${wholeRejected?'적립':record?'확정':report.status==='pending'?'폭탄방 승인 시':'전체 승인 시'} ${money(wholeRejected?0:fee.total)}</span></div>`:unpaidReclean?`<div class="badge-row" style="margin-top:7px">${statusBadge('본인 재청소 · 무급','neutral')}<span class="cell-sub">수익 원장 없음 · 0원</span></div>`:''}${extra}</div><div class="task-meta"><span>일정</span><strong>${room?.checkout||'11:00'} → ${room?.checkin||'16:00'}</strong></div><div class="task-meta"><span>${submittedContext?'수행자':'담당'}</span><strong>${esc(performer||'미정')}</strong></div><div class="task-row-action">${button(action[0],action[1],job==='inspection'?'primary':'outline',`data-id="${no}"`)}</div></article>`;
  5390 |       }
  5391 |       function renderCleaningTab() {
  5392 |         if(isCleaningAssignmentTab(state.cleaningTab))return renderAssignmentDashboard();
  5393 |         const allowed=state.cleaningTab==='progress'?['scheduled','claimed','cleaning','upload','reclean','hold']:state.cleaningTab==='inspection'?['inspection']:['approved'];
  5394 |         const entries=state.cleaningTab==='progress'?cleaningProgressEntries():Object.entries(state.jobs).filter(([,v])=>allowed.includes(v)),rows=entries.map(([no,v])=>taskRow(no,v)).join('');
  5395 |         return `<div class="tab-panel">${rows||`<section class="inline-empty"><h3>이 상태의 작업이 없습니다</h3><p>다른 탭에서 진행 상태를 확인하세요.</p></section>`}</div>`;
  5396 |       }
  5397 | 
  5398 |       function addIsoDays(iso,offset) {
  5399 |         const [year,month,day]=iso.split('-').map(Number),date=new Date(Date.UTC(year,month-1,day+offset));
  5400 |         return `${date.getUTCFullYear()}-${String(date.getUTCMonth()+1).padStart(2,'0')}-${String(date.getUTCDate()).padStart(2,'0')}`;
  5401 |       }
  5402 |       function weekStartIso(iso) {
  5403 |         const [year,month,day]=String(iso).split('-').map(Number),date=new Date(Date.UTC(year,month-1,day)),mondayOffset=-((date.getUTCDay()+6)%7);
  5404 |         return addIsoDays(iso,mondayOffset);
  5405 |       }
  5406 |       function timestampIsoDate(value,fallback=state.selectedDate) {
  5407 |         const match=String(value||'').match(/(\d{4})[.-](\d{1,2})[.-](\d{1,2})/);
  5408 |         return match?`${match[1]}-${String(Number(match[2])).padStart(2,'0')}-${String(Number(match[3])).padStart(2,'0')}`:fallback;
  5409 |       }
  5410 |       function shortIsoDate(iso) {
  5411 |         const [,month,day]=iso.split('-').map(Number);return `${month}/${day}`;
  5412 |       }
  5413 |       function completedWorkDaysForWeek(start,maidId) {
  5414 |         return [...new Set(Object.values(state.cleaningAttempts||{}).filter(attempt=>{
  5415 |           const completedDate=attempt?.completedAt?timestampIsoDate(attempt.completedAt,''):'';
  5416 |           return attempt?.performerId===maidId&&completedDate&&weekStartIso(completedDate)===start;
  5417 |         }).map(attempt=>weekdayIndex(timestampIsoDate(attempt.completedAt))))].sort((left,right)=>left-right);
  5418 |       }
  5419 |       function assignedWorkDaysForWeek(start,maidId) {
  5420 |         const days=[];
  5421 |         if(start==='2026-08-17'&&notifiedAssignmentEntriesForMaid(maidId).length)days.push(assignmentDayIndex());
  5422 |         (state.assignmentHistory||[]).forEach(entry=>{
  5423 |           if(entry.assignmentDate&&weekStartIso(entry.assignmentDate)===start&&(entry.beforeMaidId===maidId||entry.afterMaidId===maidId))days.push(weekdayIndex(entry.assignmentDate));
  5424 |         });
  5425 |         return [...new Set(days)].sort((left,right)=>left-right);
  5426 |       }
  5427 |       function currentWorkHistoryWeek() {
  5428 |         const records={};
  5429 |         MAIDS.forEach(maid=>{
  5430 |           const versions=(state.availabilityHistory||[]).filter(item=>item.maidId===maid.id&&item.weekStart==='2026-08-17').sort((left,right)=>left.version-right.version),latest=versions.at(-1),current=state.weeklyAvailability[maid.id],availability=latest||(['submitted','change-requested'].includes(current?.status)?current:{days:[],status:'unsubmitted',submittedAt:null});
  5431 |           records[maid.id]={nameSnapshot:maid.name,submitted:[...(availability.days||[])],assigned:assignedWorkDaysForWeek('2026-08-17',maid.id),completed:completedWorkDaysForWeek('2026-08-17',maid.id),submittedAt:availability.submittedAt||'—',submissionVersions:versions.length};
  5432 |         });
  5433 |         return {start:'2026-08-17',status:'계획 중',records};
  5434 |       }
  5435 |       function workHistoryWeeks() {
  5436 |         const fixtures=WORK_HISTORY_FIXTURES.map(week=>({...week,records:Object.fromEntries(Object.entries(week.records).map(([maidId,record])=>[maidId,{...record,assigned:[...new Set([...(record.assigned||[]),...assignedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right),completed:[...new Set([...(record.completed||[]),...completedWorkDaysForWeek(week.start,maidId)])].sort((left,right)=>left-right)}]))}));
  5437 |         return [currentWorkHistoryWeek(),...fixtures];
  5438 |       }
  5439 |       function renderWorkHistory() {
  5440 |         const weeks=workHistoryWeeks(),week=weeks.find(item=>item.start===state.workHistoryWeek)||{start:state.workHistoryWeek,status:'기록 없음',records:{}},selectedMaid=state.workHistoryMaid||'all';
  5441 |         const people=MAIDS.filter(maid=>selectedMaid==='all'||maid.id===selectedMaid).map(maid=>({maid,record:week.records[maid.id]})).filter(item=>item.record);
  5442 |         const totals=people.reduce((sum,item)=>({submitted:sum.submitted+item.record.submitted.length,assigned:sum.assigned+item.record.assigned.length,completed:sum.completed+item.record.completed.length}),{submitted:0,assigned:0,completed:0});
  5443 |         const maidCounts={submitted:people.filter(item=>item.record.submitted.length>0).length,assigned:people.filter(item=>item.record.assigned.length>0).length,completed:people.filter(item=>item.record.completed.length>0).length};
  5444 |         const dayNames=['월','화','수','목','금','토','일'];
  5445 |         const cards=people.map(({maid,record})=>{const days=dayNames.map((name,index)=>{const iso=addIsoDays(week.start,index),flags=[];if(record.submitted.includes(index))flags.push('<span class="work-history-flag">가능 제출</span>');if(record.assigned.includes(index))flags.push('<span class="work-history-flag assigned">담당 통보</span>');if(record.completed.includes(index))flags.push('<span class="work-history-flag completed">실근무 완료</span>');return `<div class="work-history-day"><strong>${name}요일</strong><span>${shortIsoDate(iso)}</span>${flags.length?`<div class="work-history-flags">${flags.join('')}</div>`:'<span class="work-history-empty">기록 없음</span>'}</div>`;}).join('');return `<article class="card work-history-person"><div class="work-history-person-head"><div><h3>${esc(record.nameSnapshot)} · 데모</h3><p>당시 이름 스냅샷 · 가능일 제출 ${esc(record.submittedAt)}${record.submissionVersions?` · 제출 버전 ${record.submissionVersions}개 보존`:''}</p></div><div class="work-history-counts">${statusBadge(`가능 ${record.submitted.length}일`,'blue')}${statusBadge(`배정 ${record.assigned.length}일`,'amber')}${statusBadge(`실근무 ${record.completed.length}일`,'green')}</div></div><div class="work-history-days" aria-label="${esc(record.nameSnapshot)} ${weekRangeLabel(week.start)} 주간 기록">${days}</div></article>`;}).join('');
  5446 |         const list=cards||`<section class="card empty-state"><h3>이 주차에는 저장된 근무 기록이 없습니다.</h3><p>다른 주차를 달력에서 선택하거나 메이드 필터를 바꿔 보세요.</p></section>`;
  5447 |         return `<div class="work-history-page"><section class="card work-history-hero"><div><h2>주간 근무 기록</h2><p>가능일 제출, 관리자 배정 통보, 실제 청소 완료일을 구분해 사람별·주차별로 확인합니다.</p></div>${statusBadge(`${week.status} · 관리자 전용`,week.status==='계획 중'?'blue':'neutral')}</section><section class="card"><div class="work-history-toolbar"><div class="work-history-week-field"><span id="work-history-week-label">조회 주차</span><button class="pay-week-picker work-history-week-picker" type="button" data-action="open-work-history-calendar" aria-haspopup="dialog" aria-labelledby="work-history-week-label work-history-week-value">${icon('calendar','icon-sm')}<span id="work-history-week-value">${weekRangeLabel(week.start,true)} · ${week.status}</span>${icon('chevronRight','icon-sm')}</button></div><label for="work-history-maid">메이드<select id="work-history-maid" class="select-control" data-control="work-history-maid"><option value="all" ${selectedMaid==='all'?'selected':''}>전체 메이드</option>${MAIDS.map(maid=>`<option value="${maid.id}" ${selectedMaid===maid.id?'selected':''}>${esc(maid.name)}</option>`).join('')}</select></label></div><div class="work-history-summary"><div class="planned"><span>가능 제출 메이드</span><strong>${maidCounts.submitted}명</strong><small>메이드별 가능일 합계 ${totals.submitted}일</small></div><div class="assigned"><span>담당 통보 메이드</span><strong>${maidCounts.assigned}명</strong><small>메이드별 배정일 합계 ${totals.assigned}일</small></div><div class="completed"><span>실제 근무 메이드</span><strong>${maidCounts.completed}명</strong><small>메이드별 실근무일 합계 ${totals.completed}일</small></div></div><p class="work-history-unit-note"><strong>단위 안내:</strong> ‘명’은 해당 기록이 한 번 이상 있는 메이드 수, ‘일’은 메이드별 기록 날짜를 합한 일수입니다.</p><div class="work-history-legend"><span><i class="history-dot"></i>가능 제출 · 계획</span><span><i class="history-dot assigned"></i>담당 통보 · 예정</span><span><i class="history-dot completed"></i>실근무 완료 · 수행 실적</span></div></section><div class="work-history-list">${list}</div><section class="card work-history-contract"><p><strong>기록 기준:</strong> 가능일은 제출 버전, 배정일은 관리자 통보 이벤트, 실근무일은 정상 청소 수행 회차의 현장 완료일입니다. 가능일만 제출한 날짜는 실제 근무로 세지 않으며, 과거 주차는 현재 제출·재배정으로 덮어쓰지 않습니다. 이 화면은 서버 영속 저장이 아닌 결정적 데모 fixture입니다.</p></section></div>`;
  5448 |       }
  5449 | 
  5450 |       function renderMaids() {
  5451 |         const tab=state.adminMaidTab||'workforce';
  5452 |         return renderCoach()+renderNetworkNotice()+`<div class="view-stack"><div class="tab-header"><div><h2>메이드 운영</h2><p>주간 근무 가능일·배정 업무·과거 근무 기록·주급·컴플레인을 분리해 관리합니다.</p></div></div><div class="tabs" role="tablist" aria-label="메이드 관리"><button type="button" role="tab" data-action="admin-maid-tab" data-tab="workforce" aria-selected="${tab==='workforce'}">주간 근무표</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="history" aria-selected="${tab==='history'}">근무 기록</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="pay" aria-selected="${tab==='pay'}">주급 정산</button><button type="button" role="tab" data-action="admin-maid-tab" data-tab="complaints" aria-selected="${tab==='complaints'}">컴플레인·벌점</button></div>${tab==='history'?renderWorkHistory():tab==='pay'?renderAdminPayroll():tab==='complaints'?renderComplaintsPanel():renderWorkforce()}</div>`;
  5453 |       }
  5454 |       function renderWorkforce() {
  5455 |         const submitted=Object.values(state.weeklyAvailability).filter(item=>['submitted','change-requested'].includes(item.status)).length;
  5456 |         const cards=MAIDS.map(maid=>{const record=state.weeklyAvailability[maid.id],availableDays=record.days.map(index=>['월','화','수','목','금','토','일'][index]).join('·')||'없음',accountStatus=maidStatusFor(maid.id),activity=accountStatus==='active'?maid.active:accountStatus==='deactivating'?'비활성 처리 중':'비활성';return `<article class="card pay-person" data-maid-card="${maid.id}"><div class="pay-person-head"><div class="avatar">${maid.name[0]}</div><div><h3>${maid.name} · 데모</h3><p>${maid.phone} · ${activity}</p></div>${statusBadge(accountStatus==='active'?(record.status==='submitted'?'제출 완료':record.status==='change-requested'?'변경 요청':'미제출'):accountStatus==='deactivating'?'비활성 처리 중':'비활성',accountStatus==='active'?(record.status==='submitted'?'green':record.status==='change-requested'?'amber':'red'):accountStatus==='deactivating'?'amber':'neutral')}</div><div class="pay-stats"><div class="pay-stat"><span>다음 주 가능</span><strong>${availableDays}</strong></div><div class="pay-stat"><span>예정 배정</span><strong>${assignmentTargets().filter(item=>assignmentFor(item).maidId===maid.id).length}객실</strong></div><div class="pay-stat"><span>제출 시각</span><strong>${record.submittedAt||'—'}</strong></div></div>${button('상세·이력','maid-detail','outline',`data-id="${maid.id}"`)}</article>`;}).join('');
  5457 |         return `<section class="card assignment-panel"><div class="assignment-panel-head"><div><h3>메이드 주간 근무표</h3><p>8월 17일–23일 · 일요일 23:59 마감</p></div>${statusBadge(`${submitted}/${MAIDS.length} 제출`,submitted===MAIDS.length?'green':'amber')}</div>${renderAvailabilityMatrix()}</section><div class="room-list-v2">${cards}</div>`;
  5458 |       }
  5459 |       function payrollDateLabel(value) {
  5460 |         const match=String(value||'').match(/(?:\d{4}[.-])?(\d{1,2})[.-](\d{1,2})/);
  5461 |         return match?`${Number(match[1])}월 ${Number(match[2])}일`:'날짜 미입력';
```

### occurrence 4 · line 7156

```html
  7111 |           const no=String(id||''),reservation=checkoutInspectionReservationForRoom(no);if(!adminCanMutate()||!reservation||reservation.id!==el.dataset.reservation||!checkoutInspectionPendingForReservation(reservation)){closeModal();render();toast('퇴실점검 대상 또는 관리자 최신 상태가 바뀌어 완료하지 않았습니다.','error');return;}const result=completeCheckoutInspection(no,{method:'manual'});if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-checkout-inspection-room="${no}"]`);toast(`${no}호 퇴실점검을 완료했습니다. 청소 필요 상태는 유지됩니다.`);return;
  7112 |         }
  7113 |         if(a==='toggle-room-cleaning'){
  7114 |           const no=String(id||''),request=activeManualCleaningRequest(no),block=request?manualCleaningCancelBlockReason(no):manualCleaningRequestBlockReason(no);if(block){toast(block,'error');return;}
  7115 |           const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:request?`${no}호 청소 요청을 취소할까요?`:`${no}호 청소를 요청할까요?`,subtitle:request?`${kind} · 대기열에서 취소`:`${kind} · 청소 대기열 등록`,trigger:el,body:request?'<div class="notice notice-warning"><div><strong>청소 대기열에서 요청을 취소합니다.</strong><br>아직 미배정·미공개·미착수인 요청만 취소되며, 이미 시작된 작업은 청소 상세에서 확인해야 합니다.</div></div>':'<div class="notice notice-info"><div><strong>확인하면 청소 대기열에 작업 1건을 등록합니다.</strong><br>투숙 중 객실은 연박 청소, 공실 객실은 추가 청소로 등록되며 담당은 관리자 배정 화면에서 정합니다.</div></div>',confirmLabel:request?'청소 취소':'청소 대기열에 넣기',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action="${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;
  7116 |         }
  7117 |         if(a==='confirm-room-cleaning-on'){
  7118 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 만들지 않았습니다.','error');return;}const result=createManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 대기열에 넣었습니다.`);return;
  7119 |         }
  7120 |         if(a==='confirm-room-cleaning-off'){
  7121 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 취소하지 않았습니다.','error');return;}const result=cancelManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind} 요청을 취소했습니다.`);return;
  7122 |         }
  7123 |         if(a==='create-stayover'){
  7124 |           const no=id||'142',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7125 |           if(state.role!=='admin'||isLocked()||roomIsOnHold(no)||room?.occupancy!=='occupied'){toast('최신 온라인 상태의 투숙 중 객실에서만 연박 청소 요청을 입력할 수 있습니다.','error');return;}
  7126 |           if(activeRecleanAttempt(no)){toast(`${no}호 본인 무급 재청소가 끝난 뒤 연박 청소 요청을 입력할 수 있습니다.`,'error');return;}
  7127 |           if(existing){toast(`${no}호 연박 청소 배정 준비 작업이 이미 있습니다.`,'error');return;}
  7128 |           openStayover(no,el);return;
  7129 |         }
  7130 |         if(a==='confirm-stayover'){
  7131 |           const no=id||'',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7132 |           if(state.role!=='admin'||isLocked()||!room||roomIsOnHold(no)||room.occupancy!=='occupied'){closeModal();render();toast('객실 점유·관리자 권한 또는 최신 상태가 바뀌어 요청을 저장하지 않았습니다.','error');return;}
  7133 |           if(activeRecleanAttempt(no)){closeModal();render();toast(`${no}호 본인 무급 재청소를 유지하기 위해 연박 청소 요청을 저장하지 않았습니다.`,'error');return;}
  7134 |           if(existing){closeModal();render();toast(`중복 생성을 막았습니다. 기존 ${no}호 배정 준비 작업을 확인하세요.`,'error');return;}
  7135 |           const planDate=document.getElementById('stayover-date')?.value||'',accessStart=document.getElementById('stayover-start')?.value||'',requestDue=document.getElementById('stayover-due')?.value||'',accessEnd=document.getElementById('stayover-end')?.value||'';
  7136 |           const validDate=/^\d{4}-\d{2}-\d{2}$/.test(planDate),validTimes=[accessStart,requestDue,accessEnd].every(value=>/^([01]\d|2[0-3]):[0-5]\d$/.test(value));
  7137 |           if(!validDate||!validTimes){toast('계획일과 세 시각을 모두 입력하세요.','error');document.getElementById(!validDate?'stayover-date':'stayover-start')?.focus();return;}
  7138 |           if(!(timeMinutes(accessStart)<timeMinutes(requestDue)&&timeMinutes(requestDue)<=timeMinutes(accessEnd))){toast('출입 시작 < 요청 완료 ≤ 출입 종료 순서로 입력하세요.','error');document.getElementById('stayover-due')?.focus();return;}
  7139 |           const templateSnapshot=templateSnapshotFor(no,'연박 청소');
  7140 |           state.drafts.push({id:`d${no}-stayover`,room:no,kind:'연박 청소',created:state.time,date:planDate,planDate,accessStart,requestDue,accessEnd,visibility:'private',templateSnapshot});
  7141 |           room.stayoverRequest={date:planDate,accessStart,requestDue,accessEnd};
  7142 |           const unfinished=activeUnfinishedAttempt(no);if(no==='142')state.stayoverCreated=true;if(!unfinished)state.jobs[no]='stayover-requested';
  7143 |           appendEvent(`${no}호 연박 청소 배정 준비 작업 생성`,`${planDate} · 출입 ${accessStart}–${accessEnd} · ${requestDue} 요청 완료 · ${templateSnapshot?.name||'연박 청소'} ${templateSnapshot?.version||''} 스냅샷${unfinished?` · 현재 ${unfinished.kind} ${unfinished.id} 상태 유지`:''}`);
  7144 |           closeModal();render();toast(unfinished?'연박 청소 요청을 저장하고 현재 미완료 청소 상태는 그대로 유지했습니다.':'현재 점유를 유지한 채 연박 청소 배정 준비 작업 1건을 만들었습니다.');return;
  7145 |         }
  7146 |         if(a==='operation-status'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 운영 상태를 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 운영 상태를 바꿀 수 있습니다.','error');return;}openOperationStatus(id);return;}
  7147 |         if(a==='confirm-operation-stop'){if(roomIsOnHold(id)||!adminCanMutate()){closeModal();render();toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 중지하지 않았습니다.`:'관리자 권한 또는 최신 상태가 바뀌어 운영을 중지하지 않았습니다.','error');return;}const to=document.getElementById('relocate-room')?.value||'',reason=document.getElementById('stop-reason')?.value.trim()||'';if(!reason){toast('운영 중지 사유를 입력하세요.','error');return;}state.roomStopped[id]=true;state.roomStopReasons[id]=reason;if(to)state.roomMoves[id]={to,reason};else delete state.roomMoves[id];appendEvent(`${id}호 운영 중지`,to?`${reason} · ${to}호 대체 배정 · 원 이력 보존`:reason);closeModal();render();toast(`${id}호 고객 배정을 중지했습니다.`);return;}
  7148 |         if(a==='resume-operation'){if(roomIsOnHold(id)||!adminCanMutate()){toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 재개할 수 없습니다.`:'관리자 최신 상태에서만 객실 운영을 재개할 수 있습니다.','error');return;}state.roomStopped[id]=false;appendEvent(`${id}호 운영 재개`,'대체 배정 이력은 보존');render();focusAfterRender(`[data-action="operation-status"][data-id="${id}"]`);toast('운영 정상 상태로 다시 계산했습니다.');return;}
  7149 |         if(a==='candle-change'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 촛불 수량을 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 촛불 수량을 변경할 수 있습니다.','error');return;}const room=ROOMS.find(r=>r.no===id);if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}state.candles[id]=Math.max(0,(state.candles[id]||0)+Number(el.dataset.delta));appendEvent(`${id}호 촛불 수량 변경`,`${state.candles[id]}개 · 관리자 데모`);const delta=el.dataset.delta;render();requestAnimationFrame(()=>document.querySelector(`[data-action="candle-change"][data-id="${id}"][data-delta="${delta}"]`)?.focus());return;}
  7150 |         if(a==='task-candle-change'){const no=el.dataset.room,room=ROOMS.find(r=>r.no===no);if(!maidCanEditCleaning(no)){toast('본인 담당 청소 결과를 입력하는 동안만 촛불 수량을 바꿀 수 있습니다.','error');return;}if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}const task=taskState(no);task.candle=Math.max(0,Math.min(9,(task.candle||0)+Number(el.dataset.delta)));const section=el.closest('.cleaning-section');section?.querySelector('[data-cleaning-section-meta]')?.replaceChildren(`${task.candle}개`);section?.querySelector('.candle-stepper-value strong')?.replaceChildren(`${task.candle}개`);const minus=section?.querySelector('[data-delta="-1"]'),plus=section?.querySelector('[data-delta="1"]');if(minus)minus.disabled=task.candle<1;if(plus)plus.disabled=task.candle>=9;el.focus();return;}
  7151 |         if(a==='direct-assign'){openDirectAssign(id);return;}
  7152 |         if(a==='confirm-direct-assign'){const name=document.getElementById('assign-maid')?.value||'',room=ROOMS.find(r=>r.no===id),maid=MAIDS.find(item=>item.name===name),hold=roomIsOnHold(id),reclean=activeRecleanAttempt(id),previousAttempt=activeUnfinishedAttempt(id),pinViewed=!!previousAttempt&&roomPinWasViewed(id,previousAttempt.id),target=directAssignmentTarget(id),workDate=directAssignmentWorkDate(id),beforeMaidId=previousAttempt?.performerId||MAIDS.find(item=>item.name===room?.assignee)?.id||null;if(state.role!=='admin'||isLocked()||hold||reclean||pinViewed||previousAttempt?.accessReviewRequired||!target||target.id!==el.dataset.target||target.kind!==el.dataset.kind||workDate!==el.dataset.workDate||(previousAttempt?.id||'')!==(el.dataset.attempt||'')||!['public','draft','future','scheduled','unassigned'].includes(state.jobs[id])){closeModal();render();toast(previousAttempt?.accessReviewRequired?'출입시간과 PIN 영향을 먼저 확인해 주세요.':pinViewed?`${id}호 PIN 조회 뒤에는 현장 영향 확인 전 담당을 바꿀 수 없습니다.`:hold?`${id}호는 운영 상태 확인 보류 객실이라 배정하지 않았습니다.`:reclean?'재청소는 처음 청소한 본인에게 고정되어 다른 메이드에게 직접 배정할 수 없습니다.':'청소대상·수행 회차·관리자 권한 또는 최신 상태가 바뀌어 직접 배정하지 않았습니다.','error');return;}if(!maid||beforeMaidId===maid.id||!maidCanReceiveNewAssignment(maid.id)||availabilityForWorkDate(maid.id,workDate)!=='available'){toast(beforeMaidId===maid?.id?'현재 담당과 같은 메이드는 새 담당으로 다시 배정할 수 없습니다.':maid&&!maidCanReceiveNewAssignment(maid.id)?'비활성 처리 중이거나 비활성인 메이드에게는 새 업무를 배정할 수 없습니다.':'해당 업무 주차에 근무 가능으로 제출한 메이드만 배정할 수 있습니다.','error');return;}if(room)room.assignee=name;const context=assignmentContext(target),baseRateSnapshot=previousAttempt?.baseRateSnapshot??context.type.rate,targetTemplateSnapshot=previousAttempt?.templateSnapshot||state.drafts.find(draft=>draft.id===target.id)?.templateSnapshot||templateSnapshotFor(id,target.kind),newAttempt=beginCleaningAttempt(id,{performerName:name,reason:'관리자 새 담당 직접 배정',kind:target.kind,baseRateSnapshot,workDate:attemptWorkDate(previousAttempt,workDate),effectiveDate:workDate,workTargetId:target.id,templateSnapshot:targetTemplateSnapshot,accessStart:previousAttempt?.accessStart||target.accessStart||target.checkout||null,requestDue:previousAttempt?.requestDue||target.requestDue||null,accessEnd:previousAttempt?.accessEnd||target.accessEnd||null,reservationIdSnapshot:previousAttempt?.reservationIdSnapshot||target.reservationId||null,guestCountSnapshot:previousAttempt?.guestCountSnapshot??assignmentGuestCount(target),checkoutSnapshot:previousAttempt?.checkoutSnapshot||target.checkout||null,checkinSnapshot:previousAttempt?.checkinSnapshot||target.checkin||null,deadlineSnapshot:previousAttempt?.deadlineSnapshot||target.deadline||null,nextReservationIdSnapshot:previousAttempt?.nextReservationIdSnapshot||target.nextReservationId||null});state.jobs[id]='claimed';state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:target.id,attemptId:newAttempt.id,assignmentDate:workDate,room:id,beforeMaidId,afterMaidId:maid.id,before:beforeMaidId?`${maidName(beforeMaidId)} · 기존 담당`:'미배정',after:`${name} · 직접 배정`,reason:`${newAttempt.kind} · 관리자 직접 배정 통보 · ${dateLabel(workDate)} 근무 가능 확인`});appendEvent(`${id}호 청소 직접 배정`,`${name} · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 제출 확인 · ${targetTemplateSnapshot?.id||'타입 템플릿'} ${targetTemplateSnapshot?.version||''} 스냅샷`);if(beforeMaidId&&beforeMaidId!==maid.id)appendEvent('내 청소 담당 변경 통보',`${id}호 기존 담당 종료 · ${previousAttempt?.id||'이전 회차'} 보존 · 새 담당 정보 비공개`,{maidIds:[beforeMaidId]});appendEvent('내 청소 담당 배정 통보',`${id}호 · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 확인${guestCountForAttempt(newAttempt)?` · 숙박 ${guestCountLabel(guestCountForAttempt(newAttempt))}`:''}`,{maidIds:[maid.id]});closeModal();render();toast(`${name}에게 ${id}호를 배정했습니다.`);return;}
  7153 |         if(a==='cleaning-tab'){
  7154 |           const tab=el.dataset.tab;if(!['assignment-today','assignment-tomorrow','progress','inspection','done'].includes(tab))return;
  7155 |           if(tab===state.cleaningTab){el.focus();return;}
  7156 |           if(isCleaningAssignmentTab(state.cleaningTab)&&tab!==state.cleaningTab&&state.randomAssignmentSnapshot){if(!restoreRandomAssignment())discardStaleRandomAssignment();toast('저장 전 랜덤 초안은 날짜를 바꾸기 전에 되돌렸습니다.');}
  7157 |           rememberCurrentHistoryRoute();state.cleaningTab=tab;syncAssignmentDateForCleaningTab(state);if(isCleaningAssignmentTab(tab)){initializeCleaningTargetLedger(state);state.assignmentTypeFilter='all';}
  7158 |           pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector(`[data-action="cleaning-tab"][data-tab="${tab}"]`)?.focus());return;
  7159 |         }
  7160 |         if(a==='assignment-type-filter'){
  7161 |           const type=el.dataset.type;
  7162 |           if(state.role!=='admin'||!['all',...Object.keys(ROOM_TYPES)].includes(type))return;
  7163 |           state.assignmentTypeFilter=type;render();requestAnimationFrame(()=>document.querySelector(`[data-action="assignment-type-filter"][data-type="${type}"]`)?.focus());return;
  7164 |         }
  7165 |         if(a==='admin-maid-tab'){const tab=el.dataset.tab;state.adminMaidTab=tab;render();requestAnimationFrame(()=>document.querySelector(`[data-action="admin-maid-tab"][data-tab="${tab}"]`)?.focus());return;}
  7166 |         if(a==='admin-pay-week'){
  7167 |           if(!/^\d{4}-\d{2}-\d{2}$/.test(el.dataset.week||''))return;
  7168 |           state.adminPayWeek=el.dataset.week;
  7169 |           render();
  7170 |           requestAnimationFrame(()=>document.querySelector(`[data-action="admin-pay-week"][data-week="${state.adminPayWeek}"]`)?.focus());
  7171 |           return;
  7172 |         }
  7173 |         if(a==='go-today'){pushPageTransition(()=>{state.detail=null;state.adminView='today';});return;}
  7174 |         if(a==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  7175 |         if(a==='go-work-history'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='history';});return;}
  7176 |         if(a==='go-payroll'){const week=/^\d{4}-\d{2}-\d{2}$/.test(el.dataset.week||'')&&adminPayWeeks().some(item=>item.start===el.dataset.week)?el.dataset.week:null;pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='pay';if(week)state.adminPayWeek=week;});return;}
  7177 |         if(a==='go-complaints'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='complaints';});return;}
  7178 |         if(a==='go-cleaning-drafts'||a==='go-cleaning-assignment'){const day=el.dataset.day==='today'?'today':'tomorrow';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  7179 |         if(a==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  7180 |         if(a==='go-open'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});toast('메이드는 객실을 선택할 수 없습니다. 다음 주 가능일을 제출해 주세요.');return;}
  7181 |         if(a==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  7182 |         if(a==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  7183 |         if(a==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  7184 |         if(a==='toggle-maid-pay-week'){state.maidPayOpenWeek=state.maidPayOpenWeek===id?null:id;render();requestAnimationFrame(()=>document.querySelector(`[data-action="toggle-maid-pay-week"][data-id="${id}"]`)?.focus());return;}
  7185 |         if(a==='clear-maid-pay-week'){state.maidPaySelectedWeek=null;state.maidPayFilter='all';state.maidPayOpenWeek='2026-08-03';render();requestAnimationFrame(()=>document.querySelector('[data-action="open-pay-calendar"][data-context="maid-pay"]')?.focus());return;}
  7186 |         if(a==='new-cleaning'){
  7187 |           if(state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 청소대상을 직접 등록할 수 있습니다.','error');return;}
  7188 |           const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일';
  7189 |           showModal({title:`${dayWord} 청소대상 직접 등록 · 데모`,subtitle:`${dateLabel(state.assignmentDate)} 자동 대상에 없는 청소를 추가합니다.`,trigger:el,body:`<div class="notice notice-info" style="margin:0 0 14px"><div><strong>자동 대상은 이미 포함되어 있습니다.</strong><br>${dayWord} 체크아웃과 연박 청소 신청은 다시 등록하지 않아도 됩니다. 같은 날짜·객실·청소 유형은 중복 등록할 수 없습니다. 재청소는 검수 반려 시 처음 청소한 본인에게만 자동 생성됩니다. 확인 보류 객실과 해당 배정일 요청·퇴실 일정이 없는 투숙 중 객실은 목록에서 제외합니다.</div></div><div class="field"><label for="new-cleaning-room">객실</label><select id="new-cleaning-room" class="select-control">${ROOMS.filter(r=>!roomIsOnHold(r.no)&&(state.assignmentDate!==state.selectedDate||!activeUnfinishedAttempt(r.no))&&(r.occupancy!=='occupied'||r.stayoverRequest?.date===state.assignmentDate||r.nextCheckoutAt?.slice(0,10)===state.assignmentDate)).map(r=>`<option value="${r.no}">${r.no}호 · ${ROOM_TYPES[r.type].name}</option>`).join('')}</select></div><div class="field" style="margin-top:12px"><label for="new-cleaning-kind">청소 유형</label><select id="new-cleaning-kind" class="select-control"><option>퇴실 청소</option><option>연박 청소</option></select></div>`,confirmLabel:'청소대상에 추가',confirmAction:'confirm-new-cleaning'});return;}
  7190 |         if(a==='confirm-new-cleaning'){
  7191 |           if(state.role!=='admin'||isLocked()){closeModal();render();toast('관리자 권한 또는 동기화 상태가 바뀌어 청소대상을 등록하지 않았습니다.','error');return;}
  7192 |           const no=document.getElementById('new-cleaning-room')?.value||'352',kind=document.getElementById('new-cleaning-kind')?.value||'퇴실 청소',key=`manual-${no}-${kind.replaceAll(' ','-')}-${state.assignmentDate}`,room=ROOMS.find(item=>item.no===no),dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일';
  7193 |           if(roomIsOnHold(no)){closeModal();render();toast(`${no}호는 운영 상태 확인 보류 객실이라 청소대상을 등록하지 않았습니다.`,'error');return;}
  7194 |           if(state.assignmentDate===state.selectedDate&&activeUnfinishedAttempt(no)){closeModal();render();toast(`${no}호는 이미 당일 미완료 청소가 있어 새 청소대상을 등록하지 않았습니다.`,'error');return;}
  7195 |           if(!room||room.occupancy==='occupied'&&kind==='퇴실 청소'&&room.nextCheckoutAt?.slice(0,10)!==state.assignmentDate){closeModal();render();toast('투숙 중 객실은 해당 배정일의 퇴실 일정을 먼저 입력한 뒤 청소대상으로 등록하세요.','error');return;}
  7196 |           if(kind==='연박 청소'&&(!room.stayoverRequest||room.stayoverRequest.date!==state.assignmentDate)){closeModal();render();toast('해당 날짜의 실제 연박 청소 요청과 출입 가능 시간을 먼저 입력하세요.','error');return;}
  7197 |           if(activeRecleanAttempt(no)){closeModal();render();toast(`${no}호 본인 무급 재청소를 유지하기 위해 새 청소대상을 등록하지 않았습니다.`,'error');return;}
  7198 |           if(!['퇴실 청소','연박 청소'].includes(kind)){closeModal();render();toast('재청소는 검수 반려에서만 처음 청소한 본인에게 자동 생성됩니다.','error');return;}
  7199 |           const cancelledManual=state.manualAssignmentTargets.find(item=>item.id===key&&state.assignments?.[item.id]?.status==='cancelled'),duplicate=assignmentTargets().find(item=>item.room===no&&item.kind===kind);
  7200 |           if(duplicate){toast(`${no}호 ${kind}은 이미 ${duplicate.source==='manual'?'직접 등록':'자동 포함'}된 청소대상입니다.`,'error');document.getElementById('new-cleaning-room')?.focus();return;}
  7201 |           const templateSnapshot=templateSnapshotFor(no,kind),special=roomReservationStatus(room),target={id:key,room:no,type:room.type,kind,date:state.assignmentDate,checkout:startTimeFor(no),checkin:special.checkin,deadline:shiftClockTime(special.checkin,-30)||'—',source:'manual',sourceLabel:'직접 등록',priorJobState:state.jobs[no]??null,priorAssignee:room.assignee||'미정',priorAttemptId:state.currentAttemptByRoom?.[no]||null};
  7202 |           if(kind==='연박 청소')Object.assign(target,{...room.stayoverRequest,deadline:room.stayoverRequest.requestDue,sourceLabel:'직접 등록 · 연박 청소 요청'});
  7203 |           if(cancelledManual){
  7204 |             Object.assign(cancelledManual,target);delete cancelledManual.cancelled;delete cancelledManual.cancelledAt;delete cancelledManual.cancelledBy;delete cancelledManual.closeReasonCode;delete cancelledManual.closeReason;
  7205 |             const cancelledAssignment=state.assignments[key]||{},cancellationRevision={cancelledAt:cancelledAssignment.cancelledAt||null,cancelledBy:cancelledAssignment.cancelledBy||null,cancelledMaidId:cancelledAssignment.cancelledMaidId||null,cancelledNotifiedMaidId:cancelledAssignment.cancelledNotifiedMaidId||null,cancelledOrder:cancelledAssignment.cancelledOrder??null,cancelledPreviousOrder:cancelledAssignment.cancelledPreviousOrder??null,cancelledStatus:cancelledAssignment.cancelledStatus||null,cancelReasonCode:cancelledAssignment.cancelReasonCode||null,cancelReason:cancelledAssignment.cancelReason||null,notifiedAt:cancelledAssignment.cancelledNotifiedAt||cancelledAssignment.notifiedAt||null,notificationRevision:cancelledAssignment.cancelledNotificationRevision??cancelledAssignment.notificationRevision??null,committedTarget:cancelledAssignment.committedTarget||null};
  7206 |             state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(cancelledAssignment.cancellationHistory||[]),cancellationRevision]};
  7207 |             const closedTarget=state.cleaningTargets[key]||{},closeRevision={closedAt:closedTarget.closedAt||null,closedBy:closedTarget.closedBy||null,closeReasonCode:closedTarget.closeReasonCode||null,closeReason:closedTarget.closeReason||null,closeStatus:closedTarget.closeStatus||null,target:cleaningTargetOperationalSnapshot(closedTarget,state.assignmentDate)};
  7208 |             state.cleaningTargets[key]={...cleaningTargetSnapshot(target,state.assignmentDate),closed:false,reopenedAt:`${state.selectedDate} ${state.time}`,reopenReason:'관리자 직접 다시 추가',closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]};state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:key,assignmentDate:state.assignmentDate,room:no,beforeMaidId:null,afterMaidId:null,before:'청소 대상 취소',after:'미배정',reason:'관리자 직접 다시 추가 · 취소 이력 보존'});
  7209 |           }else{state.manualAssignmentTargets.push(target);state.cleaningTargets[target.id]=cleaningTargetSnapshot(target,state.assignmentDate);assignmentFor(target);}state.assignmentTypeFilter=room.type;
  7210 |           state.drafts=state.drafts.filter(draft=>draft.id!==key);state.drafts.push({id:key,room:no,kind,created:state.time,date:state.assignmentDate,templateSnapshot,source:'manual'});
  7211 |           if(state.assignmentDate===state.selectedDate)state.jobs[no]='draft';appendEvent(`${no}호 ${kind} 청소대상 ${cancelledManual?'다시 추가':'직접 등록'}`,`${dateLabel(state.assignmentDate)} · ${templateSnapshot?.id||'데모 템플릿'} ${templateSnapshot?.version||''} 스냅샷 · 자동 대상과 중복 검사 완료${cancelledManual?' · 기존 취소 이력 보존':''}`);historyReturnFocus={control:'assignment-maid',target:key};closeModal();render();focusAfterRender(`[data-control="assignment-maid"][data-target="${key}"]`);toast(`${no}호 ${kind}을 ${dayWord} 청소대상에 ${cancelledManual?'다시 ':''}추가했습니다.`);return;
  7212 |         }
  7213 |         if(a==='cancel-cleaning-target'){
  7214 |           if(state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 청소대상을 취소할 수 있습니다.','error');return;}
  7215 |           const targetId=el.dataset.target,item=assignmentTargets().find(target=>target.id===targetId),assignment=item?assignmentFor(item):null,block=item?cleaningTargetAdjustmentBlock(item):'대상이 바뀌었습니다.';
  7216 |           if(!item||!assignment){render();toast('청소대상이 바뀌었습니다. 최신 목록에서 다시 선택해 주세요.','error');return;}
  7217 |           if(block){toast(block,'error');return;}
  7218 |           const notifiedMaidId=assignment.previousMaidId||(assignment.status==='notified'?assignment.maidId:null),notifiedOrder=assignment.previousOrder??assignment.order,actionLabel=notifiedMaidId?'청소 취소·통보':'청소대상 취소';
  7219 |           showModal({title:`${item.room}호 ${actionLabel}`,subtitle:`${dateLabel(targetEffectiveDate(item))} · ${item.kind}`,trigger:el,body:`<div class="info-grid"><div class="info-item"><span>현재 담당</span><strong>${notifiedMaidId?`${esc(maidName(notifiedMaidId))} · ${notifiedOrder||'순서 없음'}${notifiedOrder?'번째':''}`:assignment.maidId?`${esc(maidName(assignment.maidId))} · 저장 전`:'미배정'}</strong></div><div class="info-item"><span>적용 결과</span><strong>${notifiedMaidId?'메이드 업무 제거·취소 알림':'관리자 이력만 보존'}</strong></div></div><div class="field" style="margin-top:14px"><label for="cleaning-cancel-reason">청소 취소 사유</label><select id="cleaning-cancel-reason" class="select-control" required><option value="">사유를 선택하세요</option>${Object.entries(CLEANING_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>정해진 운영 사유만 이력과 앱 내부 알림에 남겨 고객 개인정보 입력을 막습니다.</small></div><div class="notice notice-warning" style="margin-top:14px"><div><strong>저장 즉시 반영됩니다.</strong><br>${notifiedMaidId?'기존 메이드에게 객실·순서와 선택한 운영 사유를 앱 내부 알림으로 남기고 남은 순서를 다시 정리합니다.':'아직 통보하지 않은 대상이므로 메이드 알림은 만들지 않습니다.'}</div></div>`,confirmLabel:actionLabel,confirmAction:'confirm-cancel-cleaning-target',confirmVariant:'danger'});
  7220 |           const confirm=document.querySelector('[data-action="confirm-cancel-cleaning-target"]');if(confirm){confirm.dataset.target=item.id;confirm.dataset.fingerprint=cleaningTargetAdjustmentFingerprint(item);}return;
  7221 |         }
  7222 |         if(a==='confirm-cancel-cleaning-target'){
  7223 |           if(state.role!=='admin'||isLocked()){closeModal();render();toast('관리자 권한 또는 동기화 상태가 바뀌어 취소하지 않았습니다.','error');return;}
  7224 |           const targetId=el.dataset.target,item=assignmentTargets().find(target=>target.id===targetId),reasonCode=document.getElementById('cleaning-cancel-reason')?.value||'',reason=cleaningCancelReasonLabel(reasonCode);
  7225 |           if(!item||el.dataset.fingerprint!==cleaningTargetAdjustmentFingerprint(item)||!cleaningTargetCanAdjust(item)){closeModal();render();toast('담당 또는 청소 진행 상태가 바뀌었습니다. 최신 목록에서 다시 확인해 주세요.','error');return;}
```

### occurrence 5 · line 7157

```html
  7112 |         }
  7113 |         if(a==='toggle-room-cleaning'){
  7114 |           const no=String(id||''),request=activeManualCleaningRequest(no),block=request?manualCleaningCancelBlockReason(no):manualCleaningRequestBlockReason(no);if(block){toast(block,'error');return;}
  7115 |           const fingerprint=manualCleaningRequestFingerprint(no),kind=request?.kind||(ROOMS.find(item=>item.no===no)?.occupancy==='occupied'?'연박 청소':'추가 청소');showModal({title:request?`${no}호 청소 요청을 취소할까요?`:`${no}호 청소를 요청할까요?`,subtitle:request?`${kind} · 대기열에서 취소`:`${kind} · 청소 대기열 등록`,trigger:el,body:request?'<div class="notice notice-warning"><div><strong>청소 대기열에서 요청을 취소합니다.</strong><br>아직 미배정·미공개·미착수인 요청만 취소되며, 이미 시작된 작업은 청소 상세에서 확인해야 합니다.</div></div>':'<div class="notice notice-info"><div><strong>확인하면 청소 대기열에 작업 1건을 등록합니다.</strong><br>투숙 중 객실은 연박 청소, 공실 객실은 추가 청소로 등록되며 담당은 관리자 배정 화면에서 정합니다.</div></div>',confirmLabel:request?'청소 취소':'청소 대기열에 넣기',confirmAction:request?'confirm-room-cleaning-off':'confirm-room-cleaning-on',confirmVariant:request?'danger':'primary'});const confirm=document.querySelector(`[data-action="${request?'confirm-room-cleaning-off':'confirm-room-cleaning-on'}"]`);if(confirm){confirm.dataset.id=no;confirm.dataset.fingerprint=fingerprint;}return;
  7116 |         }
  7117 |         if(a==='confirm-room-cleaning-on'){
  7118 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 만들지 않았습니다.','error');return;}const result=createManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind}를 청소 대기열에 넣었습니다.`);return;
  7119 |         }
  7120 |         if(a==='confirm-room-cleaning-off'){
  7121 |           const no=String(id||'');if(manualCleaningRequestFingerprint(no)!==el.dataset.fingerprint){closeModal();render();toast('객실 또는 청소 상태가 바뀌어 요청을 취소하지 않았습니다.','error');return;}const result=cancelManualCleaningRequest(no);if(result.error){closeModal();render();toast(result.error,'error');return;}closeModal();render();focusAfterRender(`[data-action="toggle-room-cleaning"][data-id="${no}"]`);toast(`${no}호 ${result.request.kind} 요청을 취소했습니다.`);return;
  7122 |         }
  7123 |         if(a==='create-stayover'){
  7124 |           const no=id||'142',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7125 |           if(state.role!=='admin'||isLocked()||roomIsOnHold(no)||room?.occupancy!=='occupied'){toast('최신 온라인 상태의 투숙 중 객실에서만 연박 청소 요청을 입력할 수 있습니다.','error');return;}
  7126 |           if(activeRecleanAttempt(no)){toast(`${no}호 본인 무급 재청소가 끝난 뒤 연박 청소 요청을 입력할 수 있습니다.`,'error');return;}
  7127 |           if(existing){toast(`${no}호 연박 청소 배정 준비 작업이 이미 있습니다.`,'error');return;}
  7128 |           openStayover(no,el);return;
  7129 |         }
  7130 |         if(a==='confirm-stayover'){
  7131 |           const no=id||'',room=ROOMS.find(item=>item.no===no),existing=state.drafts.some(d=>d.room===no&&d.kind==='연박 청소');
  7132 |           if(state.role!=='admin'||isLocked()||!room||roomIsOnHold(no)||room.occupancy!=='occupied'){closeModal();render();toast('객실 점유·관리자 권한 또는 최신 상태가 바뀌어 요청을 저장하지 않았습니다.','error');return;}
  7133 |           if(activeRecleanAttempt(no)){closeModal();render();toast(`${no}호 본인 무급 재청소를 유지하기 위해 연박 청소 요청을 저장하지 않았습니다.`,'error');return;}
  7134 |           if(existing){closeModal();render();toast(`중복 생성을 막았습니다. 기존 ${no}호 배정 준비 작업을 확인하세요.`,'error');return;}
  7135 |           const planDate=document.getElementById('stayover-date')?.value||'',accessStart=document.getElementById('stayover-start')?.value||'',requestDue=document.getElementById('stayover-due')?.value||'',accessEnd=document.getElementById('stayover-end')?.value||'';
  7136 |           const validDate=/^\d{4}-\d{2}-\d{2}$/.test(planDate),validTimes=[accessStart,requestDue,accessEnd].every(value=>/^([01]\d|2[0-3]):[0-5]\d$/.test(value));
  7137 |           if(!validDate||!validTimes){toast('계획일과 세 시각을 모두 입력하세요.','error');document.getElementById(!validDate?'stayover-date':'stayover-start')?.focus();return;}
  7138 |           if(!(timeMinutes(accessStart)<timeMinutes(requestDue)&&timeMinutes(requestDue)<=timeMinutes(accessEnd))){toast('출입 시작 < 요청 완료 ≤ 출입 종료 순서로 입력하세요.','error');document.getElementById('stayover-due')?.focus();return;}
  7139 |           const templateSnapshot=templateSnapshotFor(no,'연박 청소');
  7140 |           state.drafts.push({id:`d${no}-stayover`,room:no,kind:'연박 청소',created:state.time,date:planDate,planDate,accessStart,requestDue,accessEnd,visibility:'private',templateSnapshot});
  7141 |           room.stayoverRequest={date:planDate,accessStart,requestDue,accessEnd};
  7142 |           const unfinished=activeUnfinishedAttempt(no);if(no==='142')state.stayoverCreated=true;if(!unfinished)state.jobs[no]='stayover-requested';
  7143 |           appendEvent(`${no}호 연박 청소 배정 준비 작업 생성`,`${planDate} · 출입 ${accessStart}–${accessEnd} · ${requestDue} 요청 완료 · ${templateSnapshot?.name||'연박 청소'} ${templateSnapshot?.version||''} 스냅샷${unfinished?` · 현재 ${unfinished.kind} ${unfinished.id} 상태 유지`:''}`);
  7144 |           closeModal();render();toast(unfinished?'연박 청소 요청을 저장하고 현재 미완료 청소 상태는 그대로 유지했습니다.':'현재 점유를 유지한 채 연박 청소 배정 준비 작업 1건을 만들었습니다.');return;
  7145 |         }
  7146 |         if(a==='operation-status'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 운영 상태를 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 운영 상태를 바꿀 수 있습니다.','error');return;}openOperationStatus(id);return;}
  7147 |         if(a==='confirm-operation-stop'){if(roomIsOnHold(id)||!adminCanMutate()){closeModal();render();toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 중지하지 않았습니다.`:'관리자 권한 또는 최신 상태가 바뀌어 운영을 중지하지 않았습니다.','error');return;}const to=document.getElementById('relocate-room')?.value||'',reason=document.getElementById('stop-reason')?.value.trim()||'';if(!reason){toast('운영 중지 사유를 입력하세요.','error');return;}state.roomStopped[id]=true;state.roomStopReasons[id]=reason;if(to)state.roomMoves[id]={to,reason};else delete state.roomMoves[id];appendEvent(`${id}호 운영 중지`,to?`${reason} · ${to}호 대체 배정 · 원 이력 보존`:reason);closeModal();render();toast(`${id}호 고객 배정을 중지했습니다.`);return;}
  7148 |         if(a==='resume-operation'){if(roomIsOnHold(id)||!adminCanMutate()){toast(roomIsOnHold(id)?`${id}호는 확인 보류 객실이라 운영을 재개할 수 없습니다.`:'관리자 최신 상태에서만 객실 운영을 재개할 수 있습니다.','error');return;}state.roomStopped[id]=false;appendEvent(`${id}호 운영 재개`,'대체 배정 이력은 보존');render();focusAfterRender(`[data-action="operation-status"][data-id="${id}"]`);toast('운영 정상 상태로 다시 계산했습니다.');return;}
  7149 |         if(a==='candle-change'){if(roomIsOnHold(id)){toast(`${id}호는 확인 보류 객실이라 촛불 수량을 바꿀 수 없습니다.`,'error');return;}if(!adminCanMutate()){toast('관리자 최신 상태에서만 객실 촛불 수량을 변경할 수 있습니다.','error');return;}const room=ROOMS.find(r=>r.no===id);if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}state.candles[id]=Math.max(0,(state.candles[id]||0)+Number(el.dataset.delta));appendEvent(`${id}호 촛불 수량 변경`,`${state.candles[id]}개 · 관리자 데모`);const delta=el.dataset.delta;render();requestAnimationFrame(()=>document.querySelector(`[data-action="candle-change"][data-id="${id}"][data-delta="${delta}"]`)?.focus());return;}
  7150 |         if(a==='task-candle-change'){const no=el.dataset.room,room=ROOMS.find(r=>r.no===no);if(!maidCanEditCleaning(no)){toast('본인 담당 청소 결과를 입력하는 동안만 촛불 수량을 바꿀 수 있습니다.','error');return;}if(room?.occupancy==='occupied'){toast('투숙 중 객실에는 촛불을 둘 수 없습니다.','error');return;}const task=taskState(no);task.candle=Math.max(0,Math.min(9,(task.candle||0)+Number(el.dataset.delta)));const section=el.closest('.cleaning-section');section?.querySelector('[data-cleaning-section-meta]')?.replaceChildren(`${task.candle}개`);section?.querySelector('.candle-stepper-value strong')?.replaceChildren(`${task.candle}개`);const minus=section?.querySelector('[data-delta="-1"]'),plus=section?.querySelector('[data-delta="1"]');if(minus)minus.disabled=task.candle<1;if(plus)plus.disabled=task.candle>=9;el.focus();return;}
  7151 |         if(a==='direct-assign'){openDirectAssign(id);return;}
  7152 |         if(a==='confirm-direct-assign'){const name=document.getElementById('assign-maid')?.value||'',room=ROOMS.find(r=>r.no===id),maid=MAIDS.find(item=>item.name===name),hold=roomIsOnHold(id),reclean=activeRecleanAttempt(id),previousAttempt=activeUnfinishedAttempt(id),pinViewed=!!previousAttempt&&roomPinWasViewed(id,previousAttempt.id),target=directAssignmentTarget(id),workDate=directAssignmentWorkDate(id),beforeMaidId=previousAttempt?.performerId||MAIDS.find(item=>item.name===room?.assignee)?.id||null;if(state.role!=='admin'||isLocked()||hold||reclean||pinViewed||previousAttempt?.accessReviewRequired||!target||target.id!==el.dataset.target||target.kind!==el.dataset.kind||workDate!==el.dataset.workDate||(previousAttempt?.id||'')!==(el.dataset.attempt||'')||!['public','draft','future','scheduled','unassigned'].includes(state.jobs[id])){closeModal();render();toast(previousAttempt?.accessReviewRequired?'출입시간과 PIN 영향을 먼저 확인해 주세요.':pinViewed?`${id}호 PIN 조회 뒤에는 현장 영향 확인 전 담당을 바꿀 수 없습니다.`:hold?`${id}호는 운영 상태 확인 보류 객실이라 배정하지 않았습니다.`:reclean?'재청소는 처음 청소한 본인에게 고정되어 다른 메이드에게 직접 배정할 수 없습니다.':'청소대상·수행 회차·관리자 권한 또는 최신 상태가 바뀌어 직접 배정하지 않았습니다.','error');return;}if(!maid||beforeMaidId===maid.id||!maidCanReceiveNewAssignment(maid.id)||availabilityForWorkDate(maid.id,workDate)!=='available'){toast(beforeMaidId===maid?.id?'현재 담당과 같은 메이드는 새 담당으로 다시 배정할 수 없습니다.':maid&&!maidCanReceiveNewAssignment(maid.id)?'비활성 처리 중이거나 비활성인 메이드에게는 새 업무를 배정할 수 없습니다.':'해당 업무 주차에 근무 가능으로 제출한 메이드만 배정할 수 있습니다.','error');return;}if(room)room.assignee=name;const context=assignmentContext(target),baseRateSnapshot=previousAttempt?.baseRateSnapshot??context.type.rate,targetTemplateSnapshot=previousAttempt?.templateSnapshot||state.drafts.find(draft=>draft.id===target.id)?.templateSnapshot||templateSnapshotFor(id,target.kind),newAttempt=beginCleaningAttempt(id,{performerName:name,reason:'관리자 새 담당 직접 배정',kind:target.kind,baseRateSnapshot,workDate:attemptWorkDate(previousAttempt,workDate),effectiveDate:workDate,workTargetId:target.id,templateSnapshot:targetTemplateSnapshot,accessStart:previousAttempt?.accessStart||target.accessStart||target.checkout||null,requestDue:previousAttempt?.requestDue||target.requestDue||null,accessEnd:previousAttempt?.accessEnd||target.accessEnd||null,reservationIdSnapshot:previousAttempt?.reservationIdSnapshot||target.reservationId||null,guestCountSnapshot:previousAttempt?.guestCountSnapshot??assignmentGuestCount(target),checkoutSnapshot:previousAttempt?.checkoutSnapshot||target.checkout||null,checkinSnapshot:previousAttempt?.checkinSnapshot||target.checkin||null,deadlineSnapshot:previousAttempt?.deadlineSnapshot||target.deadline||null,nextReservationIdSnapshot:previousAttempt?.nextReservationIdSnapshot||target.nextReservationId||null});state.jobs[id]='claimed';state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:target.id,attemptId:newAttempt.id,assignmentDate:workDate,room:id,beforeMaidId,afterMaidId:maid.id,before:beforeMaidId?`${maidName(beforeMaidId)} · 기존 담당`:'미배정',after:`${name} · 직접 배정`,reason:`${newAttempt.kind} · 관리자 직접 배정 통보 · ${dateLabel(workDate)} 근무 가능 확인`});appendEvent(`${id}호 청소 직접 배정`,`${name} · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 제출 확인 · ${targetTemplateSnapshot?.id||'타입 템플릿'} ${targetTemplateSnapshot?.version||''} 스냅샷`);if(beforeMaidId&&beforeMaidId!==maid.id)appendEvent('내 청소 담당 변경 통보',`${id}호 기존 담당 종료 · ${previousAttempt?.id||'이전 회차'} 보존 · 새 담당 정보 비공개`,{maidIds:[beforeMaidId]});appendEvent('내 청소 담당 배정 통보',`${id}호 · ${newAttempt.id} · ${dateLabel(workDate)} 근무 가능 확인${guestCountForAttempt(newAttempt)?` · 숙박 ${guestCountLabel(guestCountForAttempt(newAttempt))}`:''}`,{maidIds:[maid.id]});closeModal();render();toast(`${name}에게 ${id}호를 배정했습니다.`);return;}
  7153 |         if(a==='cleaning-tab'){
  7154 |           const tab=el.dataset.tab;if(!['assignment-today','assignment-tomorrow','progress','inspection','done'].includes(tab))return;
  7155 |           if(tab===state.cleaningTab){el.focus();return;}
  7156 |           if(isCleaningAssignmentTab(state.cleaningTab)&&tab!==state.cleaningTab&&state.randomAssignmentSnapshot){if(!restoreRandomAssignment())discardStaleRandomAssignment();toast('저장 전 랜덤 초안은 날짜를 바꾸기 전에 되돌렸습니다.');}
  7157 |           rememberCurrentHistoryRoute();state.cleaningTab=tab;syncAssignmentDateForCleaningTab(state);if(isCleaningAssignmentTab(tab)){initializeCleaningTargetLedger(state);state.assignmentTypeFilter='all';}
  7158 |           pushHistoryOnNextRender();render();requestAnimationFrame(()=>document.querySelector(`[data-action="cleaning-tab"][data-tab="${tab}"]`)?.focus());return;
  7159 |         }
  7160 |         if(a==='assignment-type-filter'){
  7161 |           const type=el.dataset.type;
  7162 |           if(state.role!=='admin'||!['all',...Object.keys(ROOM_TYPES)].includes(type))return;
  7163 |           state.assignmentTypeFilter=type;render();requestAnimationFrame(()=>document.querySelector(`[data-action="assignment-type-filter"][data-type="${type}"]`)?.focus());return;
  7164 |         }
  7165 |         if(a==='admin-maid-tab'){const tab=el.dataset.tab;state.adminMaidTab=tab;render();requestAnimationFrame(()=>document.querySelector(`[data-action="admin-maid-tab"][data-tab="${tab}"]`)?.focus());return;}
  7166 |         if(a==='admin-pay-week'){
  7167 |           if(!/^\d{4}-\d{2}-\d{2}$/.test(el.dataset.week||''))return;
  7168 |           state.adminPayWeek=el.dataset.week;
  7169 |           render();
  7170 |           requestAnimationFrame(()=>document.querySelector(`[data-action="admin-pay-week"][data-week="${state.adminPayWeek}"]`)?.focus());
  7171 |           return;
  7172 |         }
  7173 |         if(a==='go-today'){pushPageTransition(()=>{state.detail=null;state.adminView='today';});return;}
  7174 |         if(a==='go-workforce'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='workforce';});return;}
  7175 |         if(a==='go-work-history'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='history';});return;}
  7176 |         if(a==='go-payroll'){const week=/^\d{4}-\d{2}-\d{2}$/.test(el.dataset.week||'')&&adminPayWeeks().some(item=>item.start===el.dataset.week)?el.dataset.week:null;pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='pay';if(week)state.adminPayWeek=week;});return;}
  7177 |         if(a==='go-complaints'){pushPageTransition(()=>{state.detail=null;state.adminView='maids';state.adminMaidTab='complaints';});return;}
  7178 |         if(a==='go-cleaning-drafts'||a==='go-cleaning-assignment'){const day=el.dataset.day==='today'?'today':'tomorrow';pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab=`assignment-${day}`;syncAssignmentDateForCleaningTab(state);});return;}
  7179 |         if(a==='go-inspection'){pushPageTransition(()=>{state.detail=null;state.adminView='cleaning';state.cleaningTab='inspection';});return;}
  7180 |         if(a==='go-open'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});toast('메이드는 객실을 선택할 수 없습니다. 다음 주 가능일을 제출해 주세요.');return;}
  7181 |         if(a==='go-schedule'){pushPageTransition(()=>{state.detail=null;state.maidView='schedule';});return;}
  7182 |         if(a==='go-my'){pushPageTransition(()=>{state.detail=null;state.maidView='my';});return;}
  7183 |         if(a==='go-maid-pay'){pushPageTransition(()=>{state.detail=null;state.maidView='pay';});return;}
  7184 |         if(a==='toggle-maid-pay-week'){state.maidPayOpenWeek=state.maidPayOpenWeek===id?null:id;render();requestAnimationFrame(()=>document.querySelector(`[data-action="toggle-maid-pay-week"][data-id="${id}"]`)?.focus());return;}
  7185 |         if(a==='clear-maid-pay-week'){state.maidPaySelectedWeek=null;state.maidPayFilter='all';state.maidPayOpenWeek='2026-08-03';render();requestAnimationFrame(()=>document.querySelector('[data-action="open-pay-calendar"][data-context="maid-pay"]')?.focus());return;}
  7186 |         if(a==='new-cleaning'){
  7187 |           if(state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 청소대상을 직접 등록할 수 있습니다.','error');return;}
  7188 |           const dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일';
  7189 |           showModal({title:`${dayWord} 청소대상 직접 등록 · 데모`,subtitle:`${dateLabel(state.assignmentDate)} 자동 대상에 없는 청소를 추가합니다.`,trigger:el,body:`<div class="notice notice-info" style="margin:0 0 14px"><div><strong>자동 대상은 이미 포함되어 있습니다.</strong><br>${dayWord} 체크아웃과 연박 청소 신청은 다시 등록하지 않아도 됩니다. 같은 날짜·객실·청소 유형은 중복 등록할 수 없습니다. 재청소는 검수 반려 시 처음 청소한 본인에게만 자동 생성됩니다. 확인 보류 객실과 해당 배정일 요청·퇴실 일정이 없는 투숙 중 객실은 목록에서 제외합니다.</div></div><div class="field"><label for="new-cleaning-room">객실</label><select id="new-cleaning-room" class="select-control">${ROOMS.filter(r=>!roomIsOnHold(r.no)&&(state.assignmentDate!==state.selectedDate||!activeUnfinishedAttempt(r.no))&&(r.occupancy!=='occupied'||r.stayoverRequest?.date===state.assignmentDate||r.nextCheckoutAt?.slice(0,10)===state.assignmentDate)).map(r=>`<option value="${r.no}">${r.no}호 · ${ROOM_TYPES[r.type].name}</option>`).join('')}</select></div><div class="field" style="margin-top:12px"><label for="new-cleaning-kind">청소 유형</label><select id="new-cleaning-kind" class="select-control"><option>퇴실 청소</option><option>연박 청소</option></select></div>`,confirmLabel:'청소대상에 추가',confirmAction:'confirm-new-cleaning'});return;}
  7190 |         if(a==='confirm-new-cleaning'){
  7191 |           if(state.role!=='admin'||isLocked()){closeModal();render();toast('관리자 권한 또는 동기화 상태가 바뀌어 청소대상을 등록하지 않았습니다.','error');return;}
  7192 |           const no=document.getElementById('new-cleaning-room')?.value||'352',kind=document.getElementById('new-cleaning-kind')?.value||'퇴실 청소',key=`manual-${no}-${kind.replaceAll(' ','-')}-${state.assignmentDate}`,room=ROOMS.find(item=>item.no===no),dayWord=state.cleaningTab==='assignment-today'?'오늘':'내일';
  7193 |           if(roomIsOnHold(no)){closeModal();render();toast(`${no}호는 운영 상태 확인 보류 객실이라 청소대상을 등록하지 않았습니다.`,'error');return;}
  7194 |           if(state.assignmentDate===state.selectedDate&&activeUnfinishedAttempt(no)){closeModal();render();toast(`${no}호는 이미 당일 미완료 청소가 있어 새 청소대상을 등록하지 않았습니다.`,'error');return;}
  7195 |           if(!room||room.occupancy==='occupied'&&kind==='퇴실 청소'&&room.nextCheckoutAt?.slice(0,10)!==state.assignmentDate){closeModal();render();toast('투숙 중 객실은 해당 배정일의 퇴실 일정을 먼저 입력한 뒤 청소대상으로 등록하세요.','error');return;}
  7196 |           if(kind==='연박 청소'&&(!room.stayoverRequest||room.stayoverRequest.date!==state.assignmentDate)){closeModal();render();toast('해당 날짜의 실제 연박 청소 요청과 출입 가능 시간을 먼저 입력하세요.','error');return;}
  7197 |           if(activeRecleanAttempt(no)){closeModal();render();toast(`${no}호 본인 무급 재청소를 유지하기 위해 새 청소대상을 등록하지 않았습니다.`,'error');return;}
  7198 |           if(!['퇴실 청소','연박 청소'].includes(kind)){closeModal();render();toast('재청소는 검수 반려에서만 처음 청소한 본인에게 자동 생성됩니다.','error');return;}
  7199 |           const cancelledManual=state.manualAssignmentTargets.find(item=>item.id===key&&state.assignments?.[item.id]?.status==='cancelled'),duplicate=assignmentTargets().find(item=>item.room===no&&item.kind===kind);
  7200 |           if(duplicate){toast(`${no}호 ${kind}은 이미 ${duplicate.source==='manual'?'직접 등록':'자동 포함'}된 청소대상입니다.`,'error');document.getElementById('new-cleaning-room')?.focus();return;}
  7201 |           const templateSnapshot=templateSnapshotFor(no,kind),special=roomReservationStatus(room),target={id:key,room:no,type:room.type,kind,date:state.assignmentDate,checkout:startTimeFor(no),checkin:special.checkin,deadline:shiftClockTime(special.checkin,-30)||'—',source:'manual',sourceLabel:'직접 등록',priorJobState:state.jobs[no]??null,priorAssignee:room.assignee||'미정',priorAttemptId:state.currentAttemptByRoom?.[no]||null};
  7202 |           if(kind==='연박 청소')Object.assign(target,{...room.stayoverRequest,deadline:room.stayoverRequest.requestDue,sourceLabel:'직접 등록 · 연박 청소 요청'});
  7203 |           if(cancelledManual){
  7204 |             Object.assign(cancelledManual,target);delete cancelledManual.cancelled;delete cancelledManual.cancelledAt;delete cancelledManual.cancelledBy;delete cancelledManual.closeReasonCode;delete cancelledManual.closeReason;
  7205 |             const cancelledAssignment=state.assignments[key]||{},cancellationRevision={cancelledAt:cancelledAssignment.cancelledAt||null,cancelledBy:cancelledAssignment.cancelledBy||null,cancelledMaidId:cancelledAssignment.cancelledMaidId||null,cancelledNotifiedMaidId:cancelledAssignment.cancelledNotifiedMaidId||null,cancelledOrder:cancelledAssignment.cancelledOrder??null,cancelledPreviousOrder:cancelledAssignment.cancelledPreviousOrder??null,cancelledStatus:cancelledAssignment.cancelledStatus||null,cancelReasonCode:cancelledAssignment.cancelReasonCode||null,cancelReason:cancelledAssignment.cancelReason||null,notifiedAt:cancelledAssignment.cancelledNotifiedAt||cancelledAssignment.notifiedAt||null,notificationRevision:cancelledAssignment.cancelledNotificationRevision??cancelledAssignment.notificationRevision??null,committedTarget:cancelledAssignment.committedTarget||null};
  7206 |             state.assignments[key]={maidId:'',order:null,status:'unassigned',previousMaidId:null,previousOrder:null,cancellationHistory:[...(cancelledAssignment.cancellationHistory||[]),cancellationRevision]};
  7207 |             const closedTarget=state.cleaningTargets[key]||{},closeRevision={closedAt:closedTarget.closedAt||null,closedBy:closedTarget.closedBy||null,closeReasonCode:closedTarget.closeReasonCode||null,closeReason:closedTarget.closeReason||null,closeStatus:closedTarget.closeStatus||null,target:cleaningTargetOperationalSnapshot(closedTarget,state.assignmentDate)};
  7208 |             state.cleaningTargets[key]={...cleaningTargetSnapshot(target,state.assignmentDate),closed:false,reopenedAt:`${state.selectedDate} ${state.time}`,reopenReason:'관리자 직접 다시 추가',closeHistory:[...(closedTarget.closeHistory||[]),closeRevision]};state.assignmentHistory.unshift({time:`${dateLabel(state.selectedDate)} ${state.time}`,targetId:key,assignmentDate:state.assignmentDate,room:no,beforeMaidId:null,afterMaidId:null,before:'청소 대상 취소',after:'미배정',reason:'관리자 직접 다시 추가 · 취소 이력 보존'});
  7209 |           }else{state.manualAssignmentTargets.push(target);state.cleaningTargets[target.id]=cleaningTargetSnapshot(target,state.assignmentDate);assignmentFor(target);}state.assignmentTypeFilter=room.type;
  7210 |           state.drafts=state.drafts.filter(draft=>draft.id!==key);state.drafts.push({id:key,room:no,kind,created:state.time,date:state.assignmentDate,templateSnapshot,source:'manual'});
  7211 |           if(state.assignmentDate===state.selectedDate)state.jobs[no]='draft';appendEvent(`${no}호 ${kind} 청소대상 ${cancelledManual?'다시 추가':'직접 등록'}`,`${dateLabel(state.assignmentDate)} · ${templateSnapshot?.id||'데모 템플릿'} ${templateSnapshot?.version||''} 스냅샷 · 자동 대상과 중복 검사 완료${cancelledManual?' · 기존 취소 이력 보존':''}`);historyReturnFocus={control:'assignment-maid',target:key};closeModal();render();focusAfterRender(`[data-control="assignment-maid"][data-target="${key}"]`);toast(`${no}호 ${kind}을 ${dayWord} 청소대상에 ${cancelledManual?'다시 ':''}추가했습니다.`);return;
  7212 |         }
  7213 |         if(a==='cancel-cleaning-target'){
  7214 |           if(state.role!=='admin'||isLocked()){toast('관리자 최신 상태에서만 청소대상을 취소할 수 있습니다.','error');return;}
  7215 |           const targetId=el.dataset.target,item=assignmentTargets().find(target=>target.id===targetId),assignment=item?assignmentFor(item):null,block=item?cleaningTargetAdjustmentBlock(item):'대상이 바뀌었습니다.';
  7216 |           if(!item||!assignment){render();toast('청소대상이 바뀌었습니다. 최신 목록에서 다시 선택해 주세요.','error');return;}
  7217 |           if(block){toast(block,'error');return;}
  7218 |           const notifiedMaidId=assignment.previousMaidId||(assignment.status==='notified'?assignment.maidId:null),notifiedOrder=assignment.previousOrder??assignment.order,actionLabel=notifiedMaidId?'청소 취소·통보':'청소대상 취소';
  7219 |           showModal({title:`${item.room}호 ${actionLabel}`,subtitle:`${dateLabel(targetEffectiveDate(item))} · ${item.kind}`,trigger:el,body:`<div class="info-grid"><div class="info-item"><span>현재 담당</span><strong>${notifiedMaidId?`${esc(maidName(notifiedMaidId))} · ${notifiedOrder||'순서 없음'}${notifiedOrder?'번째':''}`:assignment.maidId?`${esc(maidName(assignment.maidId))} · 저장 전`:'미배정'}</strong></div><div class="info-item"><span>적용 결과</span><strong>${notifiedMaidId?'메이드 업무 제거·취소 알림':'관리자 이력만 보존'}</strong></div></div><div class="field" style="margin-top:14px"><label for="cleaning-cancel-reason">청소 취소 사유</label><select id="cleaning-cancel-reason" class="select-control" required><option value="">사유를 선택하세요</option>${Object.entries(CLEANING_CANCEL_REASONS).map(([value,label])=>`<option value="${value}">${esc(label)}</option>`).join('')}</select><small>정해진 운영 사유만 이력과 앱 내부 알림에 남겨 고객 개인정보 입력을 막습니다.</small></div><div class="notice notice-warning" style="margin-top:14px"><div><strong>저장 즉시 반영됩니다.</strong><br>${notifiedMaidId?'기존 메이드에게 객실·순서와 선택한 운영 사유를 앱 내부 알림으로 남기고 남은 순서를 다시 정리합니다.':'아직 통보하지 않은 대상이므로 메이드 알림은 만들지 않습니다.'}</div></div>`,confirmLabel:actionLabel,confirmAction:'confirm-cancel-cleaning-target',confirmVariant:'danger'});
  7220 |           const confirm=document.querySelector('[data-action="confirm-cancel-cleaning-target"]');if(confirm){confirm.dataset.target=item.id;confirm.dataset.fingerprint=cleaningTargetAdjustmentFingerprint(item);}return;
  7221 |         }
  7222 |         if(a==='confirm-cancel-cleaning-target'){
  7223 |           if(state.role!=='admin'||isLocked()){closeModal();render();toast('관리자 권한 또는 동기화 상태가 바뀌어 취소하지 않았습니다.','error');return;}
  7224 |           const targetId=el.dataset.target,item=assignmentTargets().find(target=>target.id===targetId),reasonCode=document.getElementById('cleaning-cancel-reason')?.value||'',reason=cleaningCancelReasonLabel(reasonCode);
  7225 |           if(!item||el.dataset.fingerprint!==cleaningTargetAdjustmentFingerprint(item)||!cleaningTargetCanAdjust(item)){closeModal();render();toast('담당 또는 청소 진행 상태가 바뀌었습니다. 최신 목록에서 다시 확인해 주세요.','error');return;}
  7226 |           const reasonError=cleaningCancelReasonError(reasonCode);if(reasonError){toast(reasonError,'error');document.getElementById('cleaning-cancel-reason')?.focus();return;}
```

## 세션: `roomManagementMaidSession`

matches: 0

## 초기 렌더: `DOMContentLoaded`

matches: 0
