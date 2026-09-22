# 청소관리 운영 API 연동

기준일: 2026-09-23
운영 계약: `CASTLE THE ART Room Management API` v0.5.1, 128 paths / 138 operations
OpenAPI 코드 생성 정본: `https://wrongstory.github.io/room-management-system-backend/openapi.json`

이 문서는 청소관리 프런트의 현재 운영 연결 정본이다. 요청·응답 타입과 endpoint는 운영 `openapi.json`만을 기계 판독 정본으로 사용한다. 이전 `DOCS/22_OPTIONAL_CLEANING_DURATION_FRONTEND_RELEASE.md`의 운영 OFF 상태와 PR #166 임시 계약은 이 문서로 대체한다.

## 운영 설정

`scripts/serve.py`는 저장소 루트의 `.env.local` 또는 프로세스 환경변수에서 다음 공개 브라우저 설정을 읽는다.

```text
RMS_API_BASE_URL=https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api
SUPABASE_URL=https://aodikrxcczbogjpsjwjt.supabase.co
SUPABASE_PUBLISHABLE_KEY=<Supabase browser publishable key>
RMS_RUNTIME_MODE=live
```

`featureFlags.optionalCleaningWorkflow`는 로컬 서버와 Pages live 산출물에서 `true`로 생성된다. 운영 설정이 없거나 잘못되면 fixture로 전환하지 않고 연결 오류를 표시한다. 의도적인 정적 데모는 `RMS_RUNTIME_MODE=demo`로만 실행한다.

로그인 세션의 access token은 `Authorization: Bearer`로 전송한다. token, PIN, 고객 PII, 사진 원문, 업로드 응답의 내부 정보를 console이나 URL에 넣지 않는다. 브라우저 저장소에는 운영 청소 데이터와 mutation payload를 저장하지 않는다. 응답 유실 재확인용 payload·idempotency key와 오프라인 시작 lease는 현재 탭 메모리에만 둔다.

## 화면별 API 매핑

| 화면/행동 | 운영 endpoint | 프런트에서 보내는 동시성 근거 | 성공 후 처리 |
| --- | --- | --- | --- |
| 관리자/메이드 배정 목록·관리자 확정 영향 | `GET /v1/assignments`, `GET /v1/assignments/commit-impact` | `serviceDate`; 메이드 응답은 `isCurrent && notifiedAt`만 표시 | 배정과 미배정·미통보·차단 목록을 각각 교체 |
| 배정 이력 | `GET /v1/assignments/{cleaningTargetId}/history` | 서버 target ID | revision 목록 표시 |
| 자동 배정 Preview | `POST /v1/assignments/preview` | `serviceDate` | 비영속 Preview로만 표시 |
| 배정 초안 저장 | `POST /v1/assignments/drafts` | Preview의 target·maid·sequence·`expectedAssignmentVersion`, 제안별 안정적인 Idempotency-Key | 대상 1건씩 순차 저장하고 건별 결과를 유지한 채 배정·영향 재조회 |
| 통보 영향/확정 | `GET /v1/assignments/commit-impact`, `POST /v1/assignments/commit` | 직전 재조회한 `impactFingerprint`, 각 target/availability version | 성공 뒤 배정·영향을 다시 읽고 남은 대상의 다음 배정 주기 유지 |
| 담당 변경/해제 | `POST .../change`, `POST .../unassign` | lifecycle impact가 `scheduled`인 현재 assignment ID와 `targetAssignmentVersion` | 서버 생성 알림/outbox를 중복 생성하지 않고 목록 재조회 |
| 메이드 취소 요청/관리자 결정 | `POST .../cancellation-requests`, `GET /v1/assignment-change-requests`, `POST .../decision` | 현재 assignment ID/version | 요청·배정 목록 재조회 |
| 메이드 현재 수행 | `GET /v1/attempts/current` | 통보 assignment ID | 본인 작업만 표시 |
| 시작/lease 시작/현장 완료 | `POST .../start`, `POST .../start-with-lease`, `POST .../complete-field-work` | execution version, assignment ID/revision | 수행과 배정 재조회 |
| 미퇴실/특이 객실 신고 | `POST .../checkout-not-completed`, `POST .../bomb-room-reports` | current attempt와 verified photo ID | 서버 상태 재조회 |
| 관리자 lifecycle | `GET /v1/attempts/lifecycle-impact`, `POST .../lifecycle` | execution/assignment/profile version | 영향과 배정 재조회 |
| 사진 슬롯/업로드 | `GET .../photo-slots`, `POST .../{slotId}/upload` | assignment ID/revision, slot `currentRevision` | 슬롯을 다시 읽어 `verified` 확인 |
| 청소 제출 | `GET/POST .../submissions` | 명시적 client submission UUID, current submission revision | immutable 제출 이력 재조회 |
| 관리자 검수 | `GET /v1/inspections`, `GET /v1/inspections/{submissionId}`, approve/reject/bomb decision | 서버 submission ID; stale 여부는 서버가 판정 | 검수 목록 재조회 |
| 사진 원본 | `GET /v1/photos/{photoId}/content` | 현재 로그인 권한 재검증 | 메모리 object URL로만 표시하고 상세 화면 이탈 시 폐기 |
| 알림 | `GET /v1/notifications`, `POST .../{notificationId}/read` | 서버 notification ID | 목록 재조회; deep-link 대상 API 재조회 |
| 주급 목록/상세 | `GET /v1/payroll`, `GET /v1/payroll/entries` | 마감 주차, 메이드 ID, kind별 opaque cursor | 기존 주급 카드·산출 상세에 pagination 전체 투영 |
| 지급 시작/상계 | `POST /v1/payroll/start`, `POST /v1/payroll/carry-forward` | cycle `version`, 메이드 ID, 주차 | 주급 목록 재조회 |
| 지급 결과 | `POST /v1/payroll/payment-attempts/{attemptId}/check|paid|reopen` | payment attempt ID와 cycle `version` | 송금 자체가 아닌 외부 결과만 기록 후 재조회 |
| 주급 정정 | corrections/reversals/late carry endpoint | earning은 `expectedVersion: 0`; adjustment는 응답의 `bookVersion` 필요 | append-only 원장 재조회 |
| 컴플레인 목록/상세 | `GET/POST /v1/complaints`, `GET .../{id}`, `GET .../history` | 원 청소 earning ID, category, case version/cursor | 기존 컴플레인 카드·상세·감사 이력 투영 |
| 컴플레인 상태 전이 | review/decision/corrections/response/close/rework | case `version`, current decision ID | 사건과 history 재조회; 주급 자동 차감 없음 |
| Web Push | `GET /v1/push-subscriptions/config`, `POST /v1/push-subscriptions`, `POST .../{id}/retire` | session-bound proof, logical subscription version | 안전 projection만 저장; endpoint/key는 비영속 |

## 관리자 흐름

관리자는 배정 화면 진입 시 서비스 날짜의 배정과 commit impact를 함께 읽어 미통보 초안·확정 차단·미배정 청소 대상을 구분해서 본다. 미배정 대상은 Preview 전부터 객실 목록으로 표시하며 청소 완료로 취급하거나 fixture로 채우지 않는다. Preview의 고정 배정·저장 전 제안·남은 미배정·제안 차단은 각각 구분한다. 여러 제안의 `제안 전체 초안 저장`은 원자적 일괄 명령이 아니라 제안별 안정적인 Idempotency-Key로 `/v1/assignments/drafts`를 순차 호출하는 편의 동작이다. 성공·실패를 건별로 보존하고 일부 실패 뒤 최신 배정과 commit impact를 다시 읽는다. 통보 확정 직전 commit impact를 다시 읽고 그 응답의 fingerprint 및 assignment/availability version을 그대로 보낸다. Commit 성공 뒤에도 남은 미배정을 잠그지 않고 `/v1/assignments`와 commit impact를 다시 읽어 같은 날짜의 다음 Preview·초안 저장·알림 확정을 허용한다.

현재 배정의 이력, 담당·순서 변경, 시작 전 해제, 메이드 담당 취소 요청의 승인·거절을 제공한다. 통보된 배정을 변경하거나 해제하기 전 lifecycle impact로 미착수 상태를 확인하며, 이미 시작한 작업은 `/change`·`/unassign`으로 우회하지 않는다. 수행 중인 작업은 lifecycle impact를 읽고 서버가 요구하는 version으로 마무리 허용, 업로드 전용, 미착수 만료 또는 중단·인계를 요청한다. 변경 알림과 outbox는 백엔드 명령만 생성하며 프런트는 별도 알림 mutation을 보내지 않는다.

검수 목록은 서버의 current immutable submission만 사용한다. 상세 사진은 인증된 content proxy로 읽으며 provider locator를 표시하지 않는다. 승인·반려·특이 객실 결정은 처리 중 중복 버튼을 잠그고 완료 뒤 목록을 다시 읽는다. stale submission 409는 로컬 성공으로 바꾸지 않고 최신 제출 확인을 안내한다.

## 메이드 현장 흐름

메이드는 서버가 본인에게 실제 통보한 현재 배정만 본다. 미통보 draft와 다른 메이드의 assignment/attempt는 화면에 섞지 않는다. 작업 시작과 현장 완료에는 마지막 조회의 execution version과 assignment ID/revision을 사용한다. 예상 청소시간이 없더라도 계획을 표시하지만 완료 예상시각은 계산하지 않는다.

`start-with-lease` 응답의 lease는 현재 탭 메모리에만 두고 만료 시각을 표시한다. 실제 수행 완료는 서버 명령 결과로만 확정한다. `field_completed`는 현장 완료일 뿐 검수 완료나 정산 생성으로 표시하지 않는다.

사진 UI는 attempt 응답의 슬롯 배열을 그대로 사용한다. 필수 목록을 프런트에서 만들지 않는다. JPEG/WebP, 300KB 이하 파일을 slot revision CAS와 함께 보내고, 성공 응답 뒤 슬롯을 다시 읽어 `verified`일 때만 충족으로 본다. 모든 필수 슬롯이 verified이고 수행 상태가 제출 가능할 때만 submission을 만든다. 제출 뒤에는 `관리자 검수 대기`로 표시한다.

## 오류·재시도·권한 상태

- `401`: 세션 갱신 뒤에도 거부되면 재로그인 안내.
- `403`: 버튼 숨김과 별개로 서버 역할/소유권 거부를 권한 없음으로 표시.
- `404`: 대상이 사라졌음을 안내하고 최신 목록 확인.
- `409`: stable code에 따라 assignment/attempt/submission 최신 상태를 다시 읽으며 로컬 성공 전이 금지.
- `422`: 서버 검증 조건과 입력값 확인.
- `429`: `Retry-After`를 진단 객체에 보존하고 같은 명령의 결과 확인 안내.
- 네트워크·5xx: 결과 불명 mutation의 정확한 payload와 `Idempotency-Key`를 메모리에 유지. 다른 mutation을 막고 동일 key/payload로만 재확인.

사용자 문구는 stable `error.code`와 HTTP 범주로 선택한다. 4xx의 계약상 안전한 안내 `message`는 알려지지 않은 코드의 보조 문구로만 사용하고, 5xx 원문은 표시하지 않는다. 진단에는 stable code와 `requestId`만 노출한다.

## 알림과 deep-link

앱 내부 알림 목록과 외부 Web Push 전달은 별도 상태다. 허용 kind는 OpenAPI의 `cleaningTarget`, `assignmentRequest`, `submission`, `complaintCase`, `payrollCycle`, `payrollProfile`뿐이다. 앞의 세 kind는 청소/검수, `complaintCase`는 컴플레인 상세, `payrollCycle`·`payrollProfile`은 역할별 주급 화면으로 이동하며 대상 API를 다시 읽는다. 알림의 UUID와 category는 탐색 힌트일 뿐 권한·소유권 근거가 아니다.

## 주급·컴플레인·Web Push 연결 원칙

- 주급 금액은 서버 원장만 사용한다. 프런트가 객실 단가를 다시 계산하거나 벌점을 차감하지 않는다. 지급 완료는 앱이 송금했다는 뜻이 아니라 관리자 입력의 외부 송금 참조번호와 서버 상태 전이를 기록한 것이다.
- 모든 주급·컴플레인 mutation은 `Idempotency-Key`와 현재 응답의 CAS version을 사용한다. 응답 유실 시 다른 mutation을 잠그고 같은 key/payload만 재확인한다.
- `PayrollAdjustmentEntry`에 `bookVersion`이 없는 현재 계약에서는 기존 adjustment의 재정정·취소를 활성화하지 않는다. earning/late-earning의 생성형 명령은 계약상 초기 version `0`을 사용한다.
- 컴플레인 상세는 사건과 history pagination을 별도로 읽는다. 관리자는 접수·검토·판정/정정·종결·재청소, 메이드는 본인 사건의 확인/이의만 수행한다.
- Web Push 원문 capability(endpoint, `p256dh`, `auth`)와 binding proof는 요청 순간에만 메모리에 둔다. 브라우저에는 서버가 반환한 safe projection의 ID/version/status만 보존한다.

## 와이어프레임 UI와 운영 데이터 매핑

화면 정보 구조와 상호작용은 기존 와이어프레임을 정본으로 유지하고, 운영 API 응답을 그 화면 모델에 투영한다. endpoint나 응답 객체를 그대로 나열하는 별도 운영 화면을 만들지 않는다.

- 관리자 오늘 화면의 `투숙 중·청소 필요·배정 가능·배정 불가` 카드는 기존 객실 목록과 상태 필터로 이동한다.
- 객실 목록은 기존 `객실 / 객실 유형·위치 / 체크인·체크아웃 / 상태 / PIN 관리` 열, 짧은 객실 유형명, `예약 / 운영 상태 / 청소 / 전체 상세` 네 작업을 유지한다.
- 간편 예약은 별도 API 목록 화면을 만들지 않는다. 기존 29일 연속 객실×날짜표, 고정 객실 열·날짜 머리글, 노란 1박·파란 연박, 객실번호/유형 필터, 전체화면, 마우스 클릭·가로 드래그와 터치 길게 누르기·가로 드래그를 그대로 사용한다. 운영 객실·예약 응답은 이 표의 표시 모델로만 변환하며 빈 범위를 선택하면 기존 예약 등록 폼에 선택 객실과 체크인·체크아웃을 채운다. 서버 성공 전에는 예약 칸을 만들지 않는다.
- 예약 버튼은 기존 예약 상세·변경 모달, 운영 상태 버튼은 기존 운영 중지 확인 모달, 청소 버튼은 기존 객실별 청소 상세, 전체 상세는 기존 2열 객실 상세 화면으로 이동한다. 팝업과 상세 화면의 제목·정보 순서·카드·하단 고정 행동은 와이어프레임을 그대로 유지한다. 백엔드가 청소요금·장기숙박 유형처럼 해당 자리에 필요한 값을 제공하지 않으면 fixture나 새 API 필드를 만들지 않고 같은 UI 자리에서 `API 미제공`으로 표시한다.
- 객실 PIN `보기·수정`은 `/pin/reveal`과 `/pin-changes/prepare → confirm|rollback`에 연결한다. 원문과 새 PIN 입력은 URL·console·웹 저장소에 남기지 않으며 background/pagehide 때 즉시 지운다.
- 관리자 청소는 기존 `오늘 배정 / 내일 배정 / 진행 중 / 검수 대상 목록 / 완료` 탭과 `근무표 → 동선 고려 랜덤 배정 → 객실별 담당 수정 → 메이드별 배정 요약·알림 확정` 구조를 유지한다. commit impact의 미배정·미통보·차단은 랜덤 배정 카드 안에서 Preview 전부터 표시하고, Preview의 고정·제안·남은 미배정·차단도 같은 카드 안에서 구분한다. `Preview·확정 영향` 같은 API 전용 독립 패널은 만들지 않는다. current revision과 검수 submission만 해당 와이어프레임 자리에 투영한다. 검수 대상은 기존 전체 페이지 상세와 하단 승인·반려 행동으로 열고, API 응답을 별도 축약 모달로 바꾸지 않는다.
- 완료 전용 목록처럼 OpenAPI에 없는 조회는 샘플 완료 이력으로 대체하지 않고 같은 탭 안에서 계약 부재를 표시한다.

## 검증과 남은 hosted smoke

로컬 Chromium 회귀는 모든 업무 API를 OpenAPI 형태의 fixture로 가로채고 다음을 확인한다: 운영 간편 예약의 29일 표와 가로 드래그→예약 폼, Preview 전 commit impact 미배정 목록, Preview 고정·제안·미배정·차단 구분, 다건 제안 순차 초안 저장과 건별 안정 키, 일부 실패 뒤 복구, 첫 확정 뒤 남은 대상의 반복 배정, 제안 0건 사유, 미시작 `/change`, 진행 중 직접 변경 차단과 lifecycle 인계, API 전용 배정 패널 부재, 본인 작업과 타인 403, 시작 replay, 409 CAS, 필수 사진 누락, 업로드 실패/성공, 중복 제출 차단, 승인/반려, stale 검수, 알림 읽음, 객실 요약 4개 필터, 객실 카드 4개 목적 화면, 예약·운영·PIN 팝업, 객실 전체 상세·객실별 청소 상세·검수 전체 상세, PIN reveal·변경 lease/version/idempotency, 401/403, console·URL의 token/PIN/고객 PII 부재, 360/390/768/1440px 넘침과 44px 컨트롤.

운영에서는 `/health`, `/docs`, `/openapi.json`과 CORS만 읽기 smoke한다. 승인된 운영 계정이 없으므로 실제 로그인, 역할별 protected GET, production 사진 content, mutation, 실제 DB 동시성, 실기기 카메라, 장시간 refresh, 외부 Web Push 전달은 통과로 기록하지 않는다. 운영 데이터로 임의 mutation을 실행하지 않는다.
