# 기획·와이어프레임·운영 API 구현 대조표

기준일: 2026-09-28. 사용자 검토용이며 백엔드 이슈 등록 전 초안이다.

## 먼저 볼 결론

**백엔드 API는 핵심 업무 대부분을 제공한다. 지금 남은 문제를 전부 ‘API 미구현’으로 보면 안 된다.** 운영 프런트의 미연결·축약된 화면, 실제 부족한 응답 필드, 실제 계정으로 아직 검증하지 않은 흐름이 섞여 있다.

- 운영 OpenAPI는 `0.6.0`, 131 paths / 141 operations다. API 개수는 제품 완성률이 아니다.
- 이번 점검에서 메이드 상세 버튼 미연결, 검수 목록 첫 페이지만 조회, 청소 변경 후 주급 캐시 유지 문제를 확인해 수정했다. 홈 배정은 검수 아래로 옮기고 내일 배정으로 연결했다.
- 개발자 객실 관리, PIN 시트 상태/전체 재동기화, 객실 이벤트, 운영 중지/이슈 목록은 **API가 있는데 프런트 연결이 빠져 있다.**
- 객실별 주급 산출과 기존 조정의 재정정에는 **실제로 부족한 API 필드**가 있다.
- 사진 전송 전 프런트 최적화, 여러 객실을 오가며 추가할 수 있는 업로드 큐는 **문서의 목표와 현재 코드가 다르다.**
- 실제 운영 계정의 사진 업로드 → 제출 → 검수 → 주급 반영을 이 점검에서 완료했다고 보지 않는다. 현재 브라우저는 로그인 화면으로 확인됐다. 운영 업무·송금 기록을 테스트용으로 임의 변경하지 않았다.

## 판정 기준

| 표기 | 뜻 |
| --- | --- |
| 구현 | 운영 OpenAPI와 백엔드 코드에서 계약/처리를 확인 |
| 연결 | 운영 모드의 프런트 요청과 버튼/화면 연결이 있음 |
| 부분 | 일부 경로·필드·상태만 연결되거나 기획과 차이가 있음 |
| 미연결 | API는 있지만 현재 운영 UI에 해당 호출/동작이 없음 |
| 계약 부족 | 필요한 응답 필드·조회 범위가 현재 공개 계약에 없음 |
| 운영 미검증 | 코드·fixture 검증과 별개로 실제 계정/실기기 UAT가 남음 |

`연결`은 ‘실운영에서 모든 경계조건까지 통과’라는 뜻이 아니다. 아래 연결된 업무도 별도 표시가 없는 한 운영 mutation UAT는 남아 있다. 정적 문구 검색만으로 미구현을 판단하지 않고 마지막 유효 함수와 실제 live 분기를 확인했다. 꺼진 feature flag용 대기 화면과 이전에 덮어쓰인 함수는 미연결 근거에서 제외했다.

기획 적용 순서는 현재 사용자 결정 → 문서 19 → 문서 16 → 문서 17 → FINAL_UX_AUDIT → 문서 14다. 공개 일감 선점/재공개, 구역별 필수 사진, 사진 180일 영속 보관 같은 이전 문구는 최신 결정으로 대체됐으므로 미구현 목록에 다시 넣지 않았다. `FINAL_UX_AUDIT.md` 원문은 수정하지 않았다.

## 현재 테스트 데이터

운영 DB 읽기 전용 집계에서 확인한 상태다. 개인명·객실 PIN·사진 원문·인증정보는 이 문서에 기록하지 않았다.

| 항목 | 확인값 | 화면 해석 |
| --- | ---: | --- |
| 최근 7일 현장 완료 | 1건 | 청소 내역에서 조회할 기록은 있음 |
| 제출 상태 | 승인 1건 | 이 제출은 이미 검수 완료 |
| 검수 대기 제출 | 0건 | 빈 검수 목록 자체는 API 실패의 증거가 아님 |
| 수행 상태 | 승인 1건, 미시작 2건 | 새 검수를 보려면 유효한 미시작 업무의 실제 수행·제출이 필요 |
| 이번 주 확정 수익 | 0건 | 이번 주 확정액 0원과 일치 |
| 지난주 확정 수익 | 1건 | 주급의 ‘이전 주’에서 확인할 대상이 있음 |

현재 주차는 KST 2026-09-28~10-04, 지난주는 2026-09-21~09-27이다. `이번 주 예상`과 `이번 주 승인 확정`, `지난주 지급 대상`은 서로 다른 값이다. 현재 주차는 조회할 수 있지만 지급 시작은 마감 뒤만 가능하다.

## 전체 기능표

### 로그인·계정·공통

| ID | 기획 기능 | 백엔드 | 프런트 | 남은 확인/차이 |
| --- | --- | --- | --- | --- |
| A01 | 로그인·첫 비밀번호 변경·역할 분리 | 구현: auth login/me/password | 연결 | 실제 관리자/메이드 계정 UAT |
| A02 | 계정 생성·동명이인·초기화·잠금 해제 | 구현: accounts 및 하위 명령 | 부분 | 개발자 계정 화면에 연결. 관리자의 기존 메이드 화면에는 진입/액션이 빠짐. F11 |
| A03 | 마지막 관리자 보호·계정 역할/상태 | 구현: role/status 및 서버 검증 | 부분 | 개발자 화면 연결. 관리자 상세의 계정 관리 복원 필요. 운영 계정을 임의 변경하지 않음 |
| A04 | 비활성 시 현재 업무 마무리/인계 | 구현: lifecycle-impact/lifecycle, limited attempts | 부분 | 일반 관리자 lifecycle 화면은 연결. 제한 세션의 별도 작업 조회/완료 UI는 미연결. 일반 메이드 진입 가드와 함께 검증 필요 |
| A05 | 모바일 이전 화면·모달 복귀 | 서버 대상 아님 | 연결·로컬 검증 | 설치 PWA의 Android 물리 Back/iOS 복귀 실기기 미검증 |
| A06 | PWA 설치·업데이트·민감 데이터 캐시 금지 | 서버 대상 아님 | 연결 | 새 브라우저 SW 검사 완료. 기존 설치 탭 업데이트 실기기 확인 필요 |
| A07 | 실제 송금·물리 도어락 자동 변경 | 대상 아님 | 제공 안 함 | 앱 밖에서 처리하는 정책. 미구현 결함으로 세지 않음 |

### 홈·객실·예약·PIN

| ID | 기획 기능 | 백엔드 | 프런트 | 남은 확인/차이 |
| --- | --- | --- | --- | --- |
| R01 | 홈 요약·검수/배정 바로가기 | 구현: rooms/inspections/assignments | 이번 수정 | 검수 아래 내일 배정. URL 하위 탭 고정, 내일 배정 건수 별도 조회 |
| R02 | 객실 주 상태·검색·타입별 목록 | 구현: rooms/room-types | 연결 | 현재 상태와 미래 예약 가능성을 구분 |
| R03 | 객실 타입·엘리베이터 수정 | 구현: rooms/{id}/master-data | 연결 | 기존 작업 스냅샷 불변은 서버 기준 |
| R04 | 과거 일마감/미래 날짜별 객실 상태 | 계약 부족: rooms GET에 날짜 파라미터 없음 | 미연결 | 예약 달력은 있음. 날짜별 객실 상태 재현과 같은 기능이 아님 |
| R05 | 예약 달력·등록·변경·중복 검사 | 구현: reservations, bookability/preview | 연결 | 실제 운영 동시 등록 UAT 남음; 로컬 fixture 회귀 별도 |
| R06 | 고객명 단건 조회·예약 인원 | 구현: 예약 단건, room-types | 연결 | 고객명은 관리자 단건에서만 표시 |
| R07 | 종료일 없는 장기 투숙·얼리/레이트 | 구현: reservation 계약 | 연결 | 구체적인 운영 사례 UAT 필요 |
| R08 | 예약 취소·예정 전 수동 체크아웃 | 구현: cancel/manual-checkout | 연결 | 진행 중 청소/PIN 영향 거부 조건은 실제 시나리오 확인 필요 |
| R09 | 예약 전 객실 변경·투숙 중 이동 | 구현: room-change/preview, room-change | 연결 | 운영 중지 모달의 별도 ‘대체 객실 API 미제공’ 문구는 낡음. 기존 이동 흐름과 연결 필요 |
| R10 | 투숙 중/추가 청소 요청·취소 | 구현: reservations/cleaning-requests | 연결 | 실제 통보/시작 이후 취소 차단 UAT |
| R11 | 운영 중지·재개·객실 이슈 등록/해결 | 구현: GET/POST operation-blocks, GET/POST issues | 부분 | 생성/해제 명령은 연결. 기존 항목 GET 미연결이라 새로고침·다른 관리자 세션의 해제 대상 복원이 안 됨. F03 |
| R12 | 촛불 기록·회수·입실 차단 | 구현: rooms/{id}/candles, 제출 candleCount | 연결 | 감소 시 현장 확인 포함. 실제 수량은 테스트로 변경하지 않음 |
| R13 | 객실 업무 이벤트 타임라인 | 구현: rooms/{id}/events | 미연결 | 현재 브라우저에서 만든 일부 항목만 표시. F02 |
| R14 | 관리자·담당 메이드 PIN 조회/변경 | 구현: pin/reveal, pin-changes | 연결 | 원문 단일 객실 30초·숨김 로컬 검증. 다른 기기의 PIN 변경 즉시 반영은 별도 확인 필요 |
| R15 | PIN 시트 상태·전체 복구/재동기화 | 구현: room-pin-sheet-sync/status, full-resync | 미연결 | PIN 원문을 프런트로 받아 엑셀을 만드는 방식이 아님. F01 |
| R16 | 객실 CSV/엑셀 내보내기 | 일부 표시 데이터는 API 제공 | 미연결 | 운영 목록의 내보내기 비활성. PIN 시트 동기화와 구분 |
| R17 | 점유/표시 상태 정정 | 구현: occupancy-corrections, display-status-overrides | 미연결 | 기존 업무 목적/권한에 맞는 확인 UI와 사유 연결 필요 |

### 근무·배정·청소·검수

| ID | 기획 기능 | 백엔드 | 프런트 | 남은 확인/차이 |
| --- | --- | --- | --- | --- |
| C01 | 다음 주 근무 가능일 상시 제출/수정 | 구현: availability/submissions | 연결 | 현재 제출을 수정 중에도 유지하는 CAS 흐름 |
| C02 | 메이드 근무표·과거 주간 근무 기록 | 구현: availability, work-history | 연결 | 가능 제출/담당 통보/실완료를 분리 |
| C03 | 오늘/내일 배정·대상 생성·부분 통보 | 구현: assignments, commit-impact, commit | 연결 | 다음날 활성화·반복 이월·스케줄러는 서버 구현/검사와 실운영 자동 실행을 구분 |
| C04 | 동선 고려 랜덤 초안·수동 담당 변경 | 구현: preview/drafts/change/unassign | 연결 | 백엔드 core에 fee spread/deviation와 이동 기준 존재. 전역 최적성/모든 운영 케이스를 이번 점검에서 재증명하지 않음 |
| C05 | 타입 필터·고정 단가·메이드별 총요금·위아래 순서 조정 | API에 feeSnapshot/sequence 등 제공 | 부분 | live 배정 요약은 건수 중심이고 순서는 별도 모달 입력. 정본의 총 청소요금/인라인 위아래 조정/타입 필터와 차이. F06 |
| C06 | 시작 전 변경/해제·취소 요청 | 구현: assignment 명령 및 change requests | 연결 | started 작업은 lifecycle로 분리. unavailable-cancel 직접 연결 여부 등 세부 취소 경로 재점검 필요 |
| C07 | 본인 통보 업무·한 객실 시작·현장 완료 | 구현: attempts/current/start/complete-field-work | 연결 | 실제 역할/시간/재배정 경쟁 UAT 필요 |
| C08 | 미퇴실 신고·관리자 조치·인계 | 구현: checkout-not-completed/incidents/lifecycle | 연결 | 실제 미퇴실 사유로 테스트 데이터는 만들지 않음 |
| C09 | 일반 사진 1~20장·다중 갤러리·추가/삭제 | 구현: photo-slots 컬렉션·DELETE | 연결·로컬 검증 | 0/1/20/21, 20장 한 번 선택, 7+13/7+14, 부분 실패 검증. 실제 OS 갤러리 미검증 |
| C10 | 브라우저 사진 축소·메타데이터 제거 | 서버 정규화 구현 | 프런트 미구현 | 현재 브라우저는 raw File 전송, 5MiB 초과 즉시 거절. F07 |
| C11 | 화면을 오가며 사진 추가·업로드 큐 | 개별 업로드 API 구현 | 부분 | 한 선택 묶음의 순차 전송은 있음. global busy 동안 다른 사진 추가 차단. 다중 객실 큐·재개 UI 부족. F07 |
| C12 | 전체 제출·멱등성·검수 사진 확대 | 구현: submissions/inspections/photo content | 연결·로컬 검증 | 일반 사진과 폭탄방/특이사항 별도. 실제 Drive 업로드/원본 조회 UAT 남음 |
| C13 | 폭탄방 증빙·인정/미인정·한 객실 ×2 | 구현: bomb reports/decision·수익 | 연결·부분 | 폭탄방 결정 전 전체 승인 버튼의 프런트 잠금이 부족, 서버 거부에 의존. F10 |
| C14 | 객실 특이사항 메모/사진·검수 조회 | 구현: room-issues·submission.roomIssues | 연결·부분 | 제출 상세는 연결. 객실 청소 요약은 0건 고정 표시가 남음. F09 |
| C15 | 전체 승인/반려·본인 무급 재청소 | 구현: approve/reject·서버 트랜잭션 | 연결 | 첫 페이지 누락 및 승인 후 주급 캐시를 이번에 수정. 실운영 승인/반려 UAT 필요 |
| C16 | 최근 7일 완료·사진 이력 | 구현: cleaning-history 목록/단건 | 연결 | 관리자/실제 수행자 범위. 메이드 관리 카드 진입을 이번에 추가 연결 |
| C17 | 사진 보존 만료·원본 정리 | 구현: retention/purge worker | 상태 표시 연결 | 만료 이후 실제 Drive 원본 정리 작업의 운영 실행/실패 재처리 확인 필요 |
| C18 | 오프라인 현장 완료·충돌 격리 | 구현: start-with-lease/offline-events/offline-quarantines | 부분 | lease 시작만 연결, 이벤트 제출/격리 해결 UI 미연결. 사진 원문 기기 영속 저장은 최신 정책상 제외. F08 |
| C19 | 템플릿 버전·예상시간 | 구현: cleaning-templates/duration-policy | 연결·부분 | API 편집은 있으나 데모 템플릿 설명에 옛 구역/고정 슬롯 문구가 남음. 최신 1~20장 정책으로 정리 필요 |

### 주급·컴플레인·알림·개발자

| ID | 기획 기능 | 백엔드 | 프런트 | 남은 확인/차이 |
| --- | --- | --- | --- | --- |
| P01 | 이번 주 확정/예상/검수대기 금액 | 구현: payroll projection 4개 필드 | 연결 | 이번 주 0건/지난주 1건 확인. 이번 수정에 새로고침·청소 변경 후 캐시 무효화 포함 |
| P02 | 객실별 기본/폭탄방/총액 산출·대기/반려 포함 원장 | 계약 부족: PayrollItem | 부분 | 날짜·확정 amount만 제공. 객실/타입/종류/기본/가산/미확정 행 필요. B01 |
| P03 | 마감 주차 지급 시작·결과 기록·확인 필요 | 구현: payroll/start, payment-attempts | 연결·부분 | 현재 주 지급 금지. paying 상태에서 ‘미송금 확인 후 복귀’는 check를 거쳐야 보이는 UI 차이. 0원 카드는 지급 컨트롤 자리도 생략 |
| P04 | 수익 정정·취소·늦은 확정·상계 | 구현: adjustments, late-earnings, carry-forward | 연결 | 실제 금전 원장 변경은 미실행 |
| P05 | 기존 adjustment의 재정정/취소 | 명령 구현, 조회 버전 부족 | 비활성 | entries에 bookVersion 없음. B02 |
| P06 | 컴플레인 접수·판정·이의·종결·재청소 | 구현: complaints 및 하위 명령 | 연결·부분 | 원 청소 선택은 현재 로드된 payroll nested items에 의존. 이전 주/다음 페이지 원장 선택을 보강해야 함. 벌점 자동 차감은 하지 않음 |
| N01 | 알림함·읽음 | 구현: notifications/read | 연결·부분 | 최대 100건 첫 페이지만 소비. nextCursor 더보기 미연결. F05 |
| N02 | 알림 클릭 시 정확한 업무/주차/요청 | 구현: deepLink kind/entityId | 부분 | 검수/컴플레인 단건은 연결. cleaningTarget/assignmentRequest는 큰 탭 이동만, payrollCycle은 특정 주차/건 복원 부족. F05 |
| N03 | Web Push 구독·해제·회전 | 구현: push-subscriptions | 연결 | 실제 iOS/Android 전달, provider/worker 상태 UAT 미검증 |
| D01 | 개발자 runtime/DB/scheduler 요약 | 구현 | 연결 | 요약 조회와 실제 자동 작업 성공은 별도 |
| D02 | 개발자 객실 등록/비활성·정원 변경 | 구현: room-catalog, capacity, rooms | 미연결 | 화면에 구버전 ‘API 미제공’ 안내가 남음. F04 |
| D03 | 개발자 감사/활동/진단 | 구현: audit-events/activity-events/diagnostics | 미연결 | 권한에 맞는 운영 도구 연결 필요 |

## 먼저 고칠 프런트 누락

아래 ID로 질문하면 해당 항목만 좁혀 논의할 수 있다. 아직 GitHub 이슈는 생성하지 않았다.

| ID | 현재 현상·재현 | 근거와 필요한 작업 | 우선도 |
| --- | --- | --- | --- |
| F01 | PIN 시트 복구/동기화 상태를 운영 앱에서 실행·확인할 수 없음 | `renderLiveMore`, 객실 내보내기 disabled. 이미 있는 `GET /v1/room-pin-sheet-sync/status`, `POST .../full-resync`에 CAS/확인창 연결. 원문 PIN 가져오기 금지 | 높음 |
| F02 | 객실 상세 타임라인이 새로고침 뒤 사실상 비어 있고 ‘API 미제공’으로 보임 | `liveRoomTimeline`은 메모리 roomOperations만 사용. `GET /v1/rooms/{roomId}/events` 이미 있음. 최신 50건 범위이며 전체 과거 일마감 API는 아님 | 높음 |
| F03 | 다른 세션에서 만든 중지/이슈를 현재 관리자가 조회·해제하기 어려움 | `resolveLiveRoomOperation` 명령은 있음. GET operation-blocks/issues 페이지를 읽어 기존 entityId/version과 해제 행동 복원 | 높음 |
| F04 | 개발자 화면에서 객실/정원 저장이 ‘API 미제공’으로 비활성 | `renderLiveDeveloperRooms`가 v0.4.0 안내를 사용. 현재 카탈로그·정원 preview/PATCH·객실 생성·비활성 preview/commit API 6개 연결 | 중간 |
| F05 | 알림 클릭 후 정확한 객실·요청·주차로 안 가거나 오래된 알림이 없음 | `openLiveNotificationTarget`, `loadLiveNotifications`. kind/entityId를 검증해 원래 상세로 이동하고 cursor 소비 | 높음 |
| F06 | 배정 화면이 정본보다 축약됨 | `renderLiveAssignmentTableRow`, `renderLiveMaidOrderBoard`: 요금 합계·타입 필터·인라인 순서 버튼 복원. API 필드가 없다고 화면 구조를 대체하지 않기 | 높음 |
| F07 | 큰 모바일 사진은 바로 거절, 다른 객실 사진 추가는 업로드가 끝나야 가능 | `uploadLiveCleaningPhoto`: `rawBody:file`, 전체 slice.busy. 브라우저 decode 가능 형식 최적화와 메모리 큐 연결. 서버 5MiB/300KiB 계약 유지. 앱 종료 후 업로드 보장은 하지 않음 | 높음 |
| F08 | 오프라인/제한 계정의 마무리 흐름이 live UI에 없음 | `start-with-lease`는 있음. offline-events/quarantines, limited attempts API와 권한별 화면 연결이 남음 | 높음 |
| F09 | 객실 청소 요약에서 ‘특이사항 0건’ 또는 ‘신고 없음’이 실제 제출과 다를 수 있음 | `renderLiveRoomCleaningDetailPage`의 고정 빈 상태, 관리자 loadLiveCleaning에서 attempt/submission 상세를 채우지 않는 경로. 제출 상세의 실제 roomIssues/bombReport와 연결해야 함 | 높음 |
| F10 | 폭탄방 판정 전에도 전체 승인/반려 버튼이 활성일 수 있음 | `renderLiveInspectionDetailPage`의 decisionLocked에 bomb 판정 대기를 반영하지 않음. 서버 거부로 보호되지만 UI가 성공 가능한 동작처럼 보임 | 중간 |
| F11 | 관리자에게 새 계정/비활성/초기화 진입점이 안 보임 | API는 admin/developer 모두 허용. 마지막 `renderMainContent`는 developer의 accounts에서만 `renderLiveAccounts`를 호출하며 adminNav에 accounts가 없음. 이번 메이드 상세는 조회만 복원했으므로 기존 상세 하단 계정 관리 연결은 남음 | 높음 |

이번에 고친 항목은 F 목록과 구분한다: 홈 내일 링크/순서/날짜별 건수, 메이드 상세·최근 사진 이력, 검수 cursor, 청소 변경 후 주급·이력 freshness 무효화, 주급 새로고침, 홈 예상액에 expectedAmount 사용. 이 수정은 백엔드 schema를 변경하지 않는다.

## 실제 API 계약이 부족한 부분

| ID | 정확한 계약 | 부족한 값/범위 | 프런트 원칙 |
| --- | --- | --- | --- |
| B01 | `GET /v1/payroll/entries?kind=items`, `PayrollItem` | 현재 earningId/earnedOn/amount/alreadyClaimed만 있음. 객실·타입·청소 종류·기본요금·폭탄방 추가요금·검수/정산 상태, 검수 대기/반려/무급 재청소 행이 없음 | 최근 7일 청소 기록을 주급 원장에 추측 join하지 않음. 과거 주차와 여러 수익/이월을 잘못 연결할 수 있음 |
| B02 | `GET /v1/payroll/entries?kind=adjustments`, `PayrollAdjustmentEntry` | 현재 adjustmentId/availableWeekStart/amount/reasonCode/alreadyClaimed. 재정정·취소의 expectedVersion에 필요한 bookVersion 없음 | 0 또는 임의 버전을 전송하지 않고 후속 정정 버튼 비활성 유지 |
| B03 | `GET /v1/rooms`, `GET /v1/rooms/{roomId}/events` | rooms는 현재 projection, events는 최신 제한 건수. 과거 일마감 상태/미래 특정 날짜 상태를 재현하는 계약 없음 | 예약 목록만으로 과거 객실 상태를 만들어내지 않음 |

전체 작업 단가/기간별 이력·관리자 업무 영향 요약은 위 endpoint와 기존 projection을 더 조합할 수 있다. ‘전용 endpoint가 없다’만으로 백엔드 신규 개발을 요청하지 않고, F 항목의 기존 데이터 연결을 먼저 끝낸 뒤 정말 부족한 필드만 이슈화한다.

## 실제 테스트 순서

1. 관리자 → 메이드 → 주급 정산 → 이전 주. 2026-09-21 주차의 기존 확정 1건과 산출 상세를 읽는다. 지급 진행/완료는 테스트 목적으로 누르지 않는다.
2. 메이드 계정 → 청소 내역. 본인에게 해당하는 최근 7일 완료만 확인한다. 관리자 메이드 상세에서도 해당 수행자의 사진 이력을 확인한다.
3. 별도 지정된 테스트 객실/메이드의 업무로만 시작 → 현장 완료 → 일반 사진 1~20장 → 전체 제출을 실행한다. 기존 승인 기록을 되돌려 테스트하지 않는다.
4. 관리자 → 홈 ‘검수 보기’ → 새 제출. 확대 사진·폭탄방/특이사항을 확인한 뒤 승인 또는 반려를 선택한다.
5. 승인 뒤 이번 주 주급을 새로고침한다. 승인 금액과 현장 완료일 기준 귀속 주차를 대조한다. 반려는 기존 담당 무급 재청소와 적립 제외를 확인한다.
6. 휴대폰에서 20장 한 번 선택, 7장 뒤 13장 추가, 21장 차단, 업로드 일부 실패 재시도, 상세/사진/탭 뒤로가기를 확인한다.

## 검증 근거와 한계

- 운영 계약: [OpenAPI](https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api/openapi.json), [공개 API 문서](https://wrongstory.github.io/room-management-system-backend/).
- 백엔드 대조 기준: main `5303fd505f18ed45fe9945d35239ccef25df2b13`, Git tag `v0.7.0`. main CI run `36417908729`의 application/migration 성공 확인. Git 태그와 OpenAPI 버전은 별도다.
- DB 읽기 전용: 실제 attempt/submission 상태, 최근 완료 건수, 이번 주/지난주 earnings 개수만 집계. 개인 데이터·금액·인증정보를 출력하지 않았다.
- 프런트 대조: [index.html](../WIREFRAME/index.html)의 live adapter 및 마지막 유효 render/handler. [문서 19](19_ROOM_PIN_SHEET_CLEANING_HISTORY_DECISIONS.md), [문서 16](16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md), [문서 17](17_ROOM_CATALOG_LONG_STAY_DECISIONS.md), [최종 기획](FINAL_UX_AUDIT.md)을 범위별 정본으로 사용.
- 이번 코드 회귀: `scripts/check-live-navigation.mjs`, `scripts/check-cleaning-workflow.mjs`, `scripts/check-workspace.mjs`. 360/390/768/1440px, URL·Back·Forward·이미지 확대·포커스·권한·console/overflow 확인. 모든 브라우저 업무 API는 로컬 fixture로 가로챘다.
- 미완료: 실제 로그인 이후 live API 전체왕복, 실기기 갤러리/카메라/설치 앱 Back, Drive 원본 생성·만료 purge, Push 수신, 다중 관리자 동시 변경, 실제 지급 기록 UAT.
- 오래된 문서의 ‘API 없음’ 문구는 이 표보다 우선하지 않는다. 특히 문서 21의 운영 차단/이슈 GET 부재, 문서 23의 완료 목록 부재 및 업로드 최적화/전역 큐 완료처럼 읽힐 수 있는 설명은 현재 코드와 불일치한다.

## 사용자 확인 후 정할 것

- F01~F11 중 업무 테스트를 막는 항목부터 연결할지, 와이어프레임 차이까지 묶어 다음 개편으로 처리할지.
- 실제 쓰기 UAT에 사용할 객실·메이드·업무 범위. 운영 지급 완료 기록은 별도 승인 없이 테스트하지 않음.
- 프런트 화면 확인 뒤 B01~B03 중 합의된 차이만 백엔드 이슈로 등록. 화면/endpoint/schema/기대 결과/재현 절차를 함께 넘긴다.

이 문서는 구현 상태 점검표이며 정책 변경 승인서나 모든 기능의 운영 완료 선언이 아니다.
