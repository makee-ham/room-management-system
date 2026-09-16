# 청소관리 운영 API 연동

기준일: 2026-09-16
운영 계약: `CASTLE THE ART Room Management API` v0.3.0, 109 paths / 117 operations
백엔드 기준 source: `main@6604b2215e06b9e9ebf0b3138e3716a000c57ddb`

이 문서는 청소관리 프런트의 현재 운영 연결 정본이다. 요청·응답 타입과 endpoint는 운영 `openapi.json`만을 기계 판독 정본으로 사용한다. 이전 `DOCS/22_OPTIONAL_CLEANING_DURATION_FRONTEND_RELEASE.md`의 운영 OFF 상태와 PR #166 임시 계약은 이 문서로 대체한다.

## 사진 슬롯 A안 전환

새 퇴실 청소 fixture와 백엔드 #179 계약은 v8부터 객실 타입별 총 9 / 10 / 12 / 14 슬롯과 필수 8 / 9 / 11 / 13 슬롯을 사용한다. `tv-on`과 `entry-storage`는 필수로 유지하고 중복 `entry-number`는 제거하며, 마지막 `extra-proof`만 선택·`maxPhotos: 10`이다. pre-A v7의 10 / 11 / 13 / 15 스냅샷은 그대로 재생한다. 실제 다중 사진 업로드·개별 삭제·제출 봉인은 백엔드 #180 완료 전 운영 활성화하지 않는다.

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
| 관리자/메이드 배정 목록 | `GET /v1/assignments` | `serviceDate`; 메이드 응답은 `isCurrent && notifiedAt`만 표시 | 목록 교체 |
| 배정 이력 | `GET /v1/assignments/{cleaningTargetId}/history` | 서버 target ID | revision 목록 표시 |
| 자동 배정 Preview | `POST /v1/assignments/preview` | `serviceDate` | 비영속 Preview로만 표시 |
| 배정 초안 저장 | `POST /v1/assignments/drafts` | Preview의 `expectedAssignmentVersion` | 배정 목록 재조회 |
| 통보 영향/확정 | `GET /v1/assignments/commit-impact`, `POST /v1/assignments/commit` | `impactFingerprint`, 각 target/availability version | Preview·영향 폐기 후 목록 재조회 |
| 담당 변경/해제 | `POST .../change`, `POST .../unassign` | 현재 assignment ID와 `targetAssignmentVersion` | 목록 재조회 |
| 메이드 취소 요청/관리자 결정 | `POST .../cancellation-requests`, `GET /v1/assignment-change-requests`, `POST .../decision` | 현재 assignment ID/version | 요청·배정 목록 재조회 |
| 메이드 현재 수행 | `GET /v1/attempts/current` | 통보 assignment ID | 본인 작업만 표시 |
| 시작/lease 시작/현장 완료 | `POST .../start`, `POST .../start-with-lease`, `POST .../complete-field-work` | execution version, assignment ID/revision | 수행과 배정 재조회 |
| 미퇴실/특이 객실 신고 | `POST .../checkout-not-completed`, `POST .../bomb-room-reports` | current attempt와 verified photo ID | 서버 상태 재조회 |
| 관리자 lifecycle | `GET /v1/attempts/lifecycle-impact`, `POST .../lifecycle` | execution/assignment/profile version | 영향과 배정 재조회 |
| 사진 슬롯/업로드 | `GET .../photo-slots`, `POST .../{slotId}/upload` | assignment ID/revision, slot `currentRevision` | 슬롯을 다시 읽어 `verified` 확인 |
| 청소 제출 | `GET/POST .../submissions` | 명시적 client submission UUID, current submission revision | immutable 제출 이력 재조회 |
| 관리자 검수 | `GET /v1/inspections`, `GET /v1/inspections/{submissionId}`, approve/reject/bomb decision | 서버 submission ID; stale 여부는 서버가 판정 | 검수 목록 재조회 |
| 사진 원본 | `GET /v1/photos/{photoId}/content` | 현재 로그인 권한 재검증 | 메모리 object URL로만 표시하고 모달 종료 시 폐기 |
| 알림 | `GET /v1/notifications`, `POST .../{notificationId}/read` | 서버 notification ID | 목록 재조회; deep-link 대상 API 재조회 |

## 관리자 흐름

관리자는 서비스 날짜의 배정과 미통보 초안을 함께 본다. Preview 결과는 저장 상태가 아니며 행별 초안 저장 뒤에만 배정 목록에 나타난다. 통보 확정 전 commit impact를 읽고, 그 응답의 fingerprint 및 assignment/availability version을 그대로 보낸다. Commit 성공 뒤에는 응답만으로 화면을 확정하지 않고 `/v1/assignments`를 다시 읽는다.

현재 배정의 이력, 담당·순서 변경, 시작 전 해제, 메이드 담당 취소 요청의 승인·거절을 제공한다. 수행 중인 작업은 lifecycle impact를 먼저 읽고 서버가 요구하는 version으로 마무리 허용, 업로드 전용, 미착수 만료 또는 인계를 요청한다.

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

앱 내부 알림 목록과 외부 Web Push 전달은 별도 상태다. 허용 kind는 OpenAPI의 `cleaningTarget`, `assignmentRequest`, `submission`, `complaintCase`, `payrollCycle`, `payrollProfile`뿐이다. 현재 청소 화면은 앞의 세 kind만 직접 처리한다. 알림의 UUID와 category는 탐색 힌트일 뿐 권한·소유권 근거가 아니며 대상 화면 진입 시 assignment 또는 inspection API를 다시 읽는다.

## 와이어프레임 UI와 운영 데이터 매핑

화면 정보 구조와 상호작용은 기존 와이어프레임을 정본으로 유지하고, 운영 API 응답을 그 화면 모델에 투영한다. endpoint나 응답 객체를 그대로 나열하는 별도 운영 화면을 만들지 않는다.

- 관리자 오늘 화면의 `투숙 중·청소 필요·배정 가능·배정 불가` 카드는 기존 객실 목록과 상태 필터로 이동한다.
- 객실 목록은 기존 `객실 / 객실 유형·위치 / 체크인·체크아웃 / 상태 / PIN 관리` 열, 짧은 객실 유형명, `예약 / 운영 상태 / 청소 / 전체 상세` 네 작업을 유지한다.
- 예약 버튼은 기존 예약 상세·변경 모달, 운영 상태 버튼은 기존 운영 중지 확인 모달, 청소 버튼은 해당 객실로 좁힌 진행 탭, 전체 상세는 기존 2열 객실 상세 화면으로 이동한다. 백엔드가 청소요금 같은 값을 제공하지 않으면 fixture를 넣지 않고 `API 미제공`으로 표시한다.
- 객실 PIN `보기·수정`은 `/pin/reveal`과 `/pin-changes/prepare → confirm|rollback`에 연결한다. 원문과 새 PIN 입력은 URL·console·웹 저장소에 남기지 않으며 background/pagehide 때 즉시 지운다.
- 관리자 청소는 기존 `오늘 배정 / 내일 배정 / 진행 중 / 검수 대상 목록 / 완료` 탭과 단계형 배정 화면을 유지한다. Preview·impact·current revision·검수 submission만 API 데이터로 바꾼다.
- 완료 전용 목록처럼 OpenAPI에 없는 조회는 샘플 완료 이력으로 대체하지 않고 같은 탭 안에서 계약 부재를 표시한다.

## 검증과 남은 hosted smoke

로컬 Chromium 회귀는 모든 업무 API를 OpenAPI 형태의 fixture로 가로채고 다음을 확인한다: 관리자 Preview/초안/Commit, 본인 작업과 타인 403, 시작 replay, 409 CAS, 필수 사진 누락, 업로드 실패/성공, 중복 제출 차단, 승인/반려, stale 검수, 알림 읽음, 객실 요약 4개 필터, 객실 카드 4개 목적 화면, PIN reveal·변경 lease/version/idempotency, 401/403, console·URL의 token/PIN/고객 PII 부재, 360/390/768/1440px 넘침과 44px 컨트롤.

운영에서는 `/health`, `/docs`, `/openapi.json`과 CORS만 읽기 smoke한다. 승인된 운영 계정이 없으므로 실제 로그인, 역할별 protected GET, production 사진 content, mutation, 실제 DB 동시성, 실기기 카메라, 장시간 refresh, 외부 Web Push 전달은 통과로 기록하지 않는다. 운영 데이터로 임의 mutation을 실행하지 않는다.
