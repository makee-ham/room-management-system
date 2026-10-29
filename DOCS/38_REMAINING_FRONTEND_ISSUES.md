# 남은 프런트 이슈와 운영 연결 상태

## 2026-10-29 재점검

GitHub 열린 이슈6개와 PR2개, 최근 병합PR30개 및 각 이슈의 최신 댓글을 다시 확인했다. 기준 dev `c0a6bea`, 운영 main `da6acc1`. 아래 10월22일 기록은 당시 상태이며 현재 판단은 이 절과 릴리스 PR의 실제 배포 검증을 우선한다.

| 항목 | 현재 프런트 판단·처리 | 남은 범위 |
| --- | --- | --- |
| #227 메모 단독 특이사항 | backend #474 완료·PR477/main `3e805249` API53/DB122 인계와 실제 운영 OpenAPI를 대조. snapshot/client를 갱신하고 production/preview 빌드·로컬 기본 `supplementalMemoOnly=true`로 활성화. 메모 필수·사진0~10·빈 배열/정수revision0·기존 사진CAS/동일키 재시도·관리자/메이드 목록·해결 회귀 | 실제 사용자0/1/10장·모바일·오류 UAT. 프런트 배포를 실제 업무 쓰기 성공으로 표시하지 않고 이슈OPEN 유지 |
| #206 사진 | 현재 snapshot/메모리 큐/순차CAS/4조회/재시도 경로 유지. 1/5/20장·1/10/20배정·snapshot/null/유실/409·동일key/bytes·HEIC fallback 회귀 | 사용자가 직접 수행하는 실사진/실기기/실제 지연 UAT. API52 DB 최적화는 배포됐지만 프런트 재연결 변경 없음 |
| #207 조회 | 기존 일괄 가능일·송금batch·첫페이지 우선·부분실패/금액 불일치/세대 차단12그룹 재검증 | 실제 동일 역할·기기·네트워크 p50/p95 |
| #219 배정 | planningDate ON·대상일·CAS·사진큐 유지. 배정 연속 저장·미시작 변경·진행중 변경 차단 회귀 유지 | 실제 KST 자정 전후 관리자/메이드 업무 UAT |
| #220 PIN | Excel ON, Drive 가져오기 OFF 유지. backend #463은 API50 배포·전용시트 접근 준비까지 완료로 종료됐으므로 더 이상 Google 인증 미완료로 단정하지 않음 | 운영 RoomProjection에는 pinVersion이 없고 mismatch의 일반 reveal은 차단됨. ACTUAL_PIN_REENTRY의 필수 expectedPinVersion을 원문 없이 얻을 공개 경로가 여전히 없음. 버전 추측·기존PIN 우회조회·Drive apply는 하지 않음. 실제 export/물리PIN UAT |
| #194 메이드 | live 전용 경로와 역할 차단·본인 이력·새 특이사항의 합성 회귀 유지, 배포된 소스/설정 신원 대조 | 승인된 실제 메이드 계정·실기기/PWA/카메라 UAT |
| PR #169/#171 | 현재 코드의 종료예약 읽기 전용·preview0회, 사전중복/생성409 입력/DOM/포커스 유지가 #223/#224에 통합돼 있음을 패치·코드·예약11그룹으로 대조. 검증 근거를 본문에 남겨 중복PR 종료 | 오래된 stacked branch는 재병합하지 않음 |

고정 계약: 운영 OpenAPI154paths/166operations, snapshot SHA `94a412a9cd0336c7e09682acd8a2adebb81b5d931791c8e3752e410cddf26bc4`. 사진0장 응답3곳과 finalize oneOf 분기는 의도적인 계약 전환이므로 `contracts/reviewed-breaking-changes.json`에 이전/새 snapshot 해시와 정확한4개 차이만 기록했다. 다른 문서 바이트·다른 endpoint/차이는 기존 CI 실패를 유지한다. 일반 청소/폭탄방 사진 조건·권한·CAS·멱등 계약은 변경하지 않는다. 배포 결과는 구현/릴리스 PR에서 기록한다.

---

> 같은 날 후속으로 새로 등록된 #227의 프런트 준비·운영 비활성 상태는 [문서 39](39_SUPPLEMENTAL_MEMO_ONLY_HANDOFF.md)를 따른다. 아래 6개는 앞선 재점검 당시의 목록이다.

2026-10-22에 열린 이슈 6개(#140/#194/#206/#207/#219/#220)의 본문·최신 댓글과 현재 코드를 다시 대조했다. 프런트 기준은 dev `6dee336`, 현재 운영 기준은 main `3482da8` 및 [PR #226](https://github.com/makee-ham/room-management-system/pull/226)이다. 이번 수정의 병합 SHA와 배포 신원은 최종 PR의 검증 기록에서 확인한다.

문서 21은 현재 소비 API와 권한을 갱신했다. 문서 27/28/34/35/36의 날짜별 표는 당시 감사 기록이며 현재 상태를 덮어쓰지 않는다. 정책 정본 문서 19/16/17/FINAL_UX_AUDIT는 수정하지 않는다.

## 이슈별 판정

| 이슈 | 프런트에서 확인·처리한 범위 | 남은 범위 |
| --- | --- | --- |
| [#140](https://github.com/makee-ham/room-management-system/issues/140) 문서 정합화 | 실제 소비·제공·활성·UAT 분리. 계정 관리 개발자 전용, 객실 이슈/차단/이벤트 목록, 주급 조정 version, 사진 큐 구현 상태의 오래된 설명 정정. snapshot 신원과 운영 PR 연결 | 오래된 uploaded_at + 7일 요구는 아래 확정 정책으로 대체. 독립 사람 리뷰를 수행했다고 주장하지 않음 |
| [#194](https://github.com/makee-ham/room-management-system/issues/194) 메이드 혼용 | 중복 함수 26종/구형 live fallback 제거, 단일 live 진입점·0건/오류/역할 가드·직접 URL/복귀 회귀, 실제 배포 sourceCommit/SW 검증 | 승인된 실제 메이드 계정 protected GET·휴대폰 카메라/PWA UAT. 관리자 세션 검증을 메이드 검증으로 대체하지 않음 |
| [#206](https://github.com/makee-ham/room-management-system/issues/206) 사진 | 한 장씩 전송/다음 한 장 준비, 로컬 미리보기·누적 진행률·viewport 우선 읽기, accepted snapshot/null GET fallback, 같은 key/Blob/item/CAS 수동 재시도. main에 추가됐던 배정 1/10/20개 조회량 회귀를 dev에도 유지 | 실사진 업로드·재시도는 사용자 직접 UAT. 저사양 휴대폰/HEIC codec/실제 지연은 미검증. 백엔드 #472/#473의 DB 최적화 후보를 현재 운영 적용으로 간주하지 않음 |
| [#207](https://github.com/makee-ham/room-management-system/issues/207) 조회 성능 | 가능일 전체 1회, 주급 첫 페이지/페이지별 송금 batch·상세 병행 유지. 추가로 관리자 청소관리의 배정/변경요청/검수 목록을 병렬 조회하고 이전 날짜·세션·실패한 조회의 후속 cursor 중단 | 실제 동일 조건 역할별 p50/p95와 운영 네트워크·실기기 측정. 합성 조회 병행을 운영 개선율로 환산하지 않음 |
| [#219](https://github.com/makee-ham/room-management-system/issues/219) 계획일/자정 | 실제 대상일을 모든 명령·근무표에 전달, planningDate와 원 serviceDate 구분, KST 주/월/연말·응답 역전·stale 저장·복귀·큐 보존 회귀. 운영 planningDate ON | 실제 관리자/메이드 자정 전후 업무 UAT는 backend #446과 구분해 유지. 브라우저에서 scheduler·이월·담당 해제를 실행하지 않음 |
| [#220](https://github.com/makee-ham/room-management-system/issues/220) PIN 전송 | 관리자 Excel ON/Drive import OFF 분리, 현재 장기 4/6자리/일반·자동 4자리, 서버 조회/다운로드 문자열 보존. 합성 실제 XLSX 파싱·권한·오류·같은 요청 재확인 회귀 | backend #463 Google 인증/Sheets 접근, 원문 없는 최신 pinVersion/ACTUAL_PIN_REENTRY 경로와 실제 export/물리 PIN UAT |

프런트 완료와 외부 UAT를 분리해 이슈 상태를 기록한다. 완전한 승인 기준이 남은 이슈를 단순 배포 성공만으로 닫지 않는다. 실제 사진/PIN/예약/배정/급여를 검증용으로 변경하지 않는다.

## 사진 보관 정책 충돌 해소

#140 최초 본문의 `uploaded_at + 7일`은 현재 정책이 아니다. [backend #175](https://github.com/wrongstory/room-management-system-backend/issues/175)의 확정 기준선도 최종 검수 결정 전 보존·결정 후 168시간을 명시한다. 프런트의 문서 19 §6 최신 사용자 결정과 일치하므로 과거 요구를 되살리거나 최종 감사 원문을 재작성하지 않는다. 사진의 실제 만료·삭제 상태는 서버 projection으로 표시하며 만료 원본을 복원됐다고 표현하지 않는다.

## 제공 API와 실제 소비

고정 계약 신원: backend source `ad1b1a0ce54865a1b28f9eded2467c856241bf6f`, 배포 인계 API51/migration120. `contracts/backend-openapi.manifest.json`의 snapshot SHA `929c0fc8af53f839d4464d29e99b1088df6d159a52420d9aab5b8a73e48e871c`, OpenAPI 3.1.1 / info.version 0.6.0 / 154 paths / 166 operations. Git release 번호와 HTTP 명세 버전은 별개다. dev 최적화 후보의 병합은 운영 DB 적용·API 배포 증거가 아니다.

| 기능 | 공개 계약/프런트 실제 소비 | 활성·한계 |
| --- | --- | --- |
| 로그인/세션 | auth login/me 및 세션 갱신. AUTH_CONTEXT_UNAVAILABLE 503 재확인 | 운영 live/production/local, Preview live/preview/session. 비밀번호·토큰을 문서/fixture에 복제하지 않음 |
| 계정 | GET accounts로 관리자 메이드 목록. 계정 생성·역할/상태/잠금/초기화는 개발자 화면·권한 가드 | 관리자·메이드의 개발자 명령 직접 호출 차단 |
| 객실·예약 | rooms/room-types, reservations 기간 cursor·bookability·등록/수정/객실 이동·취소/체크아웃 | 기존 카드·모달 유지. 종료 예약은 읽기 전용, 중복 입력은 현재 모달에 보존 |
| 객실 기록/차단 | room events·operation-blocks·issues 전체 목록, 기존 entityId/version 해제/해결 | 다른 세션 기록도 조회. API 객체 나열 화면으로 바꾸지 않음 |
| 개발자 객실 | catalog, capacity preview/confirm, room create/deactivate | 개발자 전용. fingerprint·expiry·CAS 적용 |
| 근무 가능일 | availability 주 전체와 candidates, change-requests | 일괄 조회·완전성 오류 유지. 불가·미제출·비활성은 신규 후보에서 제외 |
| 배정/검수 목록 | assignments, commit-impact, assignment-change-requests cursor, inspections cursor | 선택 대상일 일치·검수 목록 완전성 확인 뒤 기존 카드 표시. 서로 독립적인 읽기만 병행 |
| 수행/제출 | attempts current/detail/lifecycle, photo-slots/upload/delete, submissions/inspection | 일반 1~20장·별도 증빙·본인 업무. 실제 provider·업무 쓰기 QA는 미실행 |
| 사진 snapshot | includePhotoSlots opt-in, photo upload operation/result, authenticated content | snapshot ON. accepted+null은 대상 GET만 재조회. 앱 전체 업로드 1건·인증 사진 읽기 최대 4건 |
| 과거 청소/근무 | cleaning-history 목록·상세, work-history | 과거/종료 업무는 읽기. 이력을 수행 API로 대체하지 않음 |
| 주급·송금 표시 | payroll cursor, remittance-markers batch/단건, entries/work-details/adjustment-book | partial 합계 숨김, summary 불일치 차단, 최신 currentBookVersion CAS. 실제 송금 기능 아님 |
| PIN Excel/직접 입력 | GET rooms/pins/export, 명시 reveal, prepare/confirm | export ON. 서버의 현재 장기 판정으로 입력 제한, 반환 문자열은 자르지 않음 |
| Drive 가져오기 | import preview/apply 계약 및 비활성 후보 UI | transfer OFF. #463과 pinVersion 경로 해결 전 켜지 않음 |
| 앱 내부 알림/Push | notifications cursor·read·안전한 딥링크, push config/register/rotate/revoke | 프런트 연결과 실제 외부 provider 발송을 구분. 민감 정보 알림 금지 |

## 검증·운영 증거

Browser plugin not available로 기존 Playwright Chromium 151과 합성 API fixture를 사용한다. 새 `scripts/check-admin-cleaning-reads.mjs`는 응답을 의도적으로 보류해 3개 독립 조회가 모두 시작하는지, cursor 완전성·503·날짜/세션 역전·기존 두 버튼·4개 너비·키보드/포커스/Back을 검증한다. 시간 임계값으로 속도 개선율을 주장하지 않는다. 기존 data-performance·cleaning-workflow·assignment-continuity·lazy-cleaning·photo-performance·backend-handoff·live-connections 결과는 `WIREFRAME/QA.md`에 기록한다.

현재 운영 검증 근거는 PR #226의 main `3482da8`, deployment `dpl_Dx5Civkwm9K49jZN3vcjNyy1VMiJ`, index SHA `e21991d1f79d939c451516640bdb264396e1edec47fe91dcc0bbf0d2e42de955`, SW `2026-10-22-3`다. 실제 관리자 세션의 진행중 두 버튼·관리창/이력 읽기와 배포 자산 일치를 확인한 기록이며 실제 메이드·실기기 UAT를 포함하지 않는다. 이번 변경의 운영 배포는 검증과 PR 병합 뒤 새 main SHA로 실행하고 최종 PR에 실제 신원을 기록한다.
