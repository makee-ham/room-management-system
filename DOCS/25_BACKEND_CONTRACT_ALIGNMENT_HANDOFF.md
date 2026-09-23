# 백엔드 계약 정합화 Codex 실행 인계

> 이 문서 전체를 백엔드 저장소에서 실행할 Codex에게 그대로 입력한다. 요약하거나 일부 항목만 떼어 전달하지 않는다.

---

## 실행 프롬프트 시작

당신은 `wrongstory/room-management-system-backend` 저장소의 백엔드 구현 담당 Codex다.

프런트엔드의 운영 API 연결은 완료되었고, 이제 최신 제품 정책과 기존 와이어프레임을 바꾸지 않은 채 백엔드 계약을 맞춰야 한다. 이 작업은 화면 재설계 요청이 아니다. 프런트는 서버 응답을 기존 표시 모델로 변환하는 adapter/view-model 구조를 유지한다. API 구조를 이유로 기존 카드, 내비게이션, 버튼의 목적 화면, 문구 체계를 바꾸라고 요구하지 마라.

이 프롬프트의 목표는 다음과 같다.

1. 현재 백엔드에서 최신 제품 정책과 반대로 동작하는 계약을 먼저 바로잡는다.
2. 기존 화면이 `API 미제공`·비활성 상태로 남아 있는 지점을 실제 운영 계약으로 채운다.
3. 이미 소스가 있는 Google PIN 시트, Web Push, 사진 저장소 기능을 중복 개발하지 않고, 소스 구현과 호스팅 활성화 상태를 분리해 마무리한다.
4. OpenAPI, 마이그레이션, 권한, 상태 전이, 오류 코드, 테스트, 운영 문서를 함께 완료한다.
5. 각 단계가 끝날 때 프런트엔드가 기존 UI를 그대로 유지하며 연결할 수 있는 정확한 계약 변경 내역을 인계한다.

### 기준 스냅샷

- 프런트엔드 기준 저장소: `makee-ham/room-management-system`
- 프런트엔드 기준 브랜치/커밋: `dev@280ff34bc99ee8e2b6ba00a2d99d3ef87f12e3b8` (`기능: 메이드 객실 접기와 즉시 촬영 추가`)
- 백엔드 최신 독립 검토 기준: PR #258 head `1fae325`, `dev` 병합 커밋 `40edb068`
- 검토한 운영 OpenAPI: `v0.5.1`, 128 paths / 138 operations
- 이 인계서 최종 갱신일: 2026-09-23 KST

작업 시작 시 원격 브랜치를 다시 fetch하고 위 기준 이후 변경을 먼저 비교하라. 이미 해결된 항목은 중복 구현하지 말고, 커밋·OpenAPI·테스트 근거와 함께 `해결됨`으로 표시하라. 문서가 오래됐다는 이유로 최신 제품 정책을 되돌리지는 마라.

### 2026-09-23 사진 업로드 최신 확정과 PR #258 독립 리뷰 후속

아래 항목은 이 문서의 오래된 사진 전송 가정보다 우선한다.

1. 사진은 슬롯별 개별 raw body 업로드만 사용한다. ZIP 생성·업로드·보관과 batch endpoint는 전부 폐기한다.
2. PR #258의 고정 `5초 전체 수신 제한`을 제거한다. 바이트가 계속 유입되면 5초를 넘어도 읽고, 최대 5MiB는 유지한다. `30초 동안 새 바이트가 하나도 들어오지 않을 때`만 idle timeout `408`, 5MiB 초과는 `413`으로 종료한다.
3. 수신 중단·취소·provider 실패 뒤 임시 객체와 metadata가 고아로 남지 않게 rollback/cleanup을 보장한다. 같은 슬롯 재시도는 기존 revision CAS와 idempotency 계약을 유지한다.
4. 서버는 권한 확인된 `roomId`에서 객실호수를 조회하고, 업로드 시각의 KST 날짜로 `객실호수_YYYY-MM-DD` 비공개 Drive 폴더를 만든다. 클라이언트가 경로나 폴더명을 지정하지 않는다. 객체명은 opaque ID이며 DB가 attempt·slot·revision·hash·MIME·크기·보존기한을 정본으로 가진다.
5. 같은 객실·날짜의 여러 수행 회차는 같은 폴더를 쓸 수 있지만 DB 원장과 opaque 객체 ID가 충돌 없이 구분해야 한다. 폴더명은 권한이나 도메인 식별의 근거가 아니다.
6. 프런트는 앱이 열린 동안 메모리 큐에서 한 장씩 업로드하고, 디코딩 가능한 사진은 전송 전에 더 작은 JPEG/WebP로 최적화한다. 브라우저 영속 저장소나 서비스 워커에 원본을 남기지 않으므로 앱 종료 뒤 background upload를 백엔드가 전제하지 않는다.
7. PR #258 독립 리뷰에서 12MP·HEIC 실부하의 Edge resource gate가 확인되지 않았다. 최소 12MP JPEG와 실제 HEIC/HEIF 표본으로 peak RSS·CPU·wall time·동시 업로드를 기록하고 Supabase 제한 안에서 실패가 격리되는지 검증한다. 4MP 단색 JPEG와 32px HEIF만으로 완료 처리하지 않는다.
8. 위 public 동작 변경과 오류 응답을 OpenAPI에 반영하고 `0.5.1`을 그대로 유지하지 않는다. 배포 전 generated client/type 검증과 migration/release note를 함께 제공한다.

필수 회귀는 다음을 포함한다: 5초를 넘지만 30초 안에 계속 진행되는 업로드 성공, 30초 무진행 `408`, 5MiB+1 `413`, 한 사진 실패 뒤 그 사진만 재시도, KST 자정 폴더명, 같은 방·날짜 복수 attempt, client-supplied path 무시, ZIP 관련 endpoint·객체 없음, provider 부분 실패 cleanup, 실제 12MP JPEG/HEIC의 Edge 부하 측정.

## 1. 반드시 읽을 정본과 충돌 우선순위

백엔드 저장소의 `AGENTS.md`와 `docs/AI_BACKEND_PRODUCT_GUIDE.md`를 먼저 읽고, 아래 프런트엔드 정본을 순서대로 끝까지 읽어라.

프런트엔드 저장소가 같은 작업공간에 없다면 `https://github.com/makee-ham/room-management-system`을 읽기 전용 임시 checkout으로 받아 위 기준 커밋을 확인하라. 백엔드 작업 브랜치 안으로 프런트 파일을 복사하거나 두 저장소의 변경을 한 PR에 섞지 마라. 저장소 접근이 불가능한 경우에도 아래에 필요한 계약을 자체 포함했으므로 구현 분석은 계속하되, 원문 대조를 하지 못한 사실과 범위를 완료 보고에 명시하라.

1. `DOCS/19_ROOM_PIN_SHEET_CLEANING_HISTORY_DECISIONS.md`
2. `DOCS/16_WEEKLY_AVAILABILITY_ASSIGNMENT_POLICY.md`
3. `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`
4. `DOCS/FINAL_UX_AUDIT.md`
5. `DOCS/14_CLICKABLE_WIREFRAME_HANDOFF.md`
6. `DOCS/24_RESERVATION_ARRIVAL_ROOM_MOVE_BACKEND_HANDOFF.md`
7. `DOCS/23_CLEANING_API_INTEGRATION.md`
8. `DOCS/21_PRODUCTION_API_PWA_INTEGRATION.md`
9. `WIREFRAME/README.md`
10. `WIREFRAME/QA.md`
11. `DOCS/WIREFRAME_TASK_PROMPT.md`

충돌 우선순위는 다음과 같다.

`현재 사용자의 명시적 결정 → DOCS/19의 객실 PIN·청소 사진 이력 정책 → DOCS/16의 청소 배정 정책 → DOCS/17의 객실 기준정보·점유 정책 → FINAL_UX_AUDIT → DOCS/24의 예약·방 이동 계약 → 나머지 최신 인계 문서 → 백엔드의 과거 가정`

`CURRENT/`, `HISTORY/`, 프런트엔드 `DOCS/01`~`DOCS/13`, 과거 시안은 감사 근거와 시각 참고일 뿐 최신 정책 정본이 아니다. 이미 적용된 DB 마이그레이션도 제품 정책 정본이 아니다. 잘못된 계약이 마이그레이션에 들어갔다면 새 append-only 마이그레이션으로 고쳐라.

먼저 `docs/AI_BACKEND_PRODUCT_GUIDE.md`가 현재 프런트엔드 스냅샷과 아래 정책을 가리키도록 갱신하라. 특히 그 문서의 오래된 사진 보존, PIN 접근, 카드 우선순위 가정을 구현 근거로 사용하지 마라.

## 2. 변경 불가 원칙

- 프런트엔드 와이어프레임의 정보 구조, 카드, 버튼 위치와 목적 화면은 유지한다.
- 운영 API가 필요한 값을 제공하지 않는 동안 프런트는 fixture나 추측값으로 채우지 않는다. 따라서 백엔드는 화면에 필요한 읽기 모델을 명시적으로 제공해야 한다.
- 기존 공개 계약은 가능한 한 additive하게 확장한다. 의미가 바뀌거나 nullable 범위가 넓어지는 계약은 OpenAPI 버전을 올리고 migration note를 제공한다.
- 모든 쓰기 명령은 역할 권한, 소유권, 상태 전이, CAS/expected version, idempotency, 트랜잭션, 감사 로그, outbox를 검토한다.
- 시간은 전송 시 RFC 3339 offset을 사용하고, 서비스 일자·주차·최근 7일 계산은 KST로 정의한다.
- PIN 원문, 고객명, 사진 원문/locator, 민감한 메모를 URL, 로그, 알림 payload, idempotency 기록에 남기지 않는다.
- 객실 PIN 원문은 명시적 조회 뒤 한 객실만 최대 30초 메모리에 두고, 응답 캐시 금지 헤더를 유지한다.
- 메이드는 본인 업무·주급·평가만 볼 수 있어야 하며, 관리자 URL 직접 진입도 서버에서 차단한다.
- 적용된 마이그레이션 파일을 수정하지 않는다. 새 마이그레이션과 forward/backfill 전략을 추가한다.
- 운영 credential, 실제 Google Sheet ID, VAPID private key, OAuth refresh token이 필요한 활성화는 사용자 승인과 비밀값 주입 없이 실행하지 않는다.
- 실제 운영 데이터에 변경 smoke test를 하지 않는다. 허용된 fixture 또는 격리 환경을 사용한다.
- `main`·`dev`에 직접 푸시하지 않는다. `codex/` 브랜치에서 범위가 작은 PR을 `dev` 기준으로 만들고, 저장소 보호 규칙과 필수 검사를 지킨다.
- 거대한 한 개 PR로 묶지 않는다. 아래 단계별 PR을 만들되, 최종 목표가 완료될 때까지 계속 진행한다.

## 3. 현재 상태를 잘못 해석하지 말 것

### 3.1 소스가 이미 있는 기능

다음은 “엔드포인트가 전혀 없음”이 아니다. 같은 기능을 새로 만들지 마라.

- Google PIN 시트 상태/전체 재동기화:
  - `GET /v1/room-pin-sheet-sync/status`
  - `POST /v1/room-pin-sheet-sync/full-resync`
- Web Push provider/worker와 알림 outbox 처리 코드
- 사진 저장소 adapter, content 조회, purge worker/Cron 관련 코드
- 객실 기준정보 변경:
  - `PATCH /v1/rooms/{roomId}/master-data`
- 청소 템플릿:
  - `GET /v1/cleaning-templates`
  - `POST /v1/cleaning-templates`
- 객실 운영 차단/이슈의 생성·해제·해결 명령

위 기능은 `소스 구현 완료`, `호스팅 설정 완료`, `실제 provider 양성 smoke 완료`를 서로 다른 상태로 보고하라. 현재 검토 기준에서는 Google target/service account/ACL/Cron, VAPID/provider invoke secret, Drive OAuth/upload/read/purge/Cron의 운영 양성 검증이 남아 있다. 이를 새 API 개발과 혼동하지 마라.

### 3.2 실제로 없거나 정책과 어긋난 기능

다음은 실제 백엔드 계약 작업이다.

- 사진 보존 기산점과 권한
- 담당 메이드 PIN 접근 수명주기
- 객실의 예약/점유/준비/대표 상태 투영
- 임의 기간 예약 가능 여부와 예약 범위 조회
- 원자적 방 이동 preview/commit
- 장기 투숙 및 종료 미정 계약
- 객실 타입 카탈로그
- 청소 완료 이력과 메이드 근무 이력
- 배정 카드용 금액·종류·이월 snapshot
- 객실 운영 차단/이슈 목록과 사건 타임라인
- 급여 상세 투영과 정정용 버전
- 알림 deep-link의 entityId 재조회 가능성
- 계정 비활성화 영향도·유예·최종화 workflow
- 컴플레인 내용·증빙·검토/결정/이의 메모

## 4. 단계 0 — 정책 가이드와 계약 기준선 고정

첫 PR에서 다음을 처리하라.

1. `docs/AI_BACKEND_PRODUCT_GUIDE.md`가 최신 프런트 정본과 커밋을 참조하도록 갱신한다.
2. 아래 두 가지 기존 가정을 명시적으로 폐기한다.
   - 모든 사진을 업로드 후 7일에 삭제한다는 가정
   - 메이드 PIN 접근을 `availableFrom` 이후이며 attempt가 `scheduled|in_progress`일 때만 허용한다는 가정
3. 객실 대표 상태 우선순위를 확정한다.
   - `BLOCKED > OCCUPIED > ARRIVAL_PENDING > RESERVATION_PRESENT > CLEANING_REQUIRED > READY`
4. `pinSyncStatus`가 의미하는 축을 분리한다.
   - 미래 기간 예약 가능 여부(`intervalBookable`)
   - 현재 체크인/배정 준비 상태(`readinessStatus`, `checkInReady`)
   - PIN 동기화 상태(`pinSyncStatus`)

현재 백엔드 가이드에는 PIN 불일치/미설정을 예약 생성 자체의 차단 사유로 보지 않는 과거 가정이 있고, 최신 프런트 정책에는 PIN 불일치/확인 대기가 `배정 불가` 사유로 표시된다. 하나의 boolean으로 합치지 마라. 미래 예약은 기간상 가능하면서 현재 체크인 준비는 불가할 수 있다. 정본 의미를 위 세 축으로 문서화하고, 정말 해소되지 않는 제품 충돌만 정확한 선택지와 영향 범위로 보고하라.

완료 조건:

- API/DB 작업보다 먼저 정책 테스트 이름과 상태 정의가 문서에 고정된다.
- OpenAPI 변경 계획, 마이그레이션 계획, 기존 데이터 backfill 계획을 PR 본문에 적는다.
- 이후 PR이 이 기준을 테스트로 참조한다.

## 5. 단계 1 — 최우선 안전 계약: 사진과 PIN

### 5.1 청소 제출 사진 보존 계약 수정

현재의 `purge_after = uploaded_at + 7 days` 일괄 정책은 최신 정본과 다르다. 사진 종류와 사건 상태에 따라 보존 정책을 분리하라.

청소 제출 사진:

- 검사 최종 결정 전에는 원본을 보존한다.
- 승인 또는 반려가 최종 결정된 시각부터 `7 × 24시간` 뒤에 원본·미리보기·캐시를 삭제한다.
- 검사 대기 시간이 길어져도 최종 결정 전에는 삭제하지 않는다.
- 실제 수행 메이드와 관리자는 만료 전까지 조회할 수 있다.
- 만료 뒤에도 제출·슬롯·검사·수행자·시각·삭제 상태 metadata는 영구 이력으로 남긴다.

그 밖의 증빙:

- 객실 이슈/컴플레인 증빙: 해결 또는 종결 후 180일
- 중단 업무/동기화 충돌 증빙: 관리자 해결 후 180일
- 어떤 도메인에도 묶이지 않은 진짜 orphan 업로드: 업로드 후 30일

필수 구현:

- 기존 적용 마이그레이션을 편집하지 말고 새 마이그레이션을 추가한다.
- 사진 레코드가 보존 정책 종류, 기산 사건, `retentionStartsAt`, `expiresAt`, `purgedAt`, `mediaAvailability`를 설명할 수 있어야 한다.
- 이미 삭제된 원본은 복구했다고 표시하지 않는다. metadata는 `expired`/`unavailable`로 정직하게 backfill한다.
- 아직 검사 대기인 연결된 사진은 purge 대상에서 제외한다.
- `/v1/photos/{photoId}/content`는 실제 수행 메이드의 과거 본인 제출도 만료 전이면 허용하고, 타 메이드·권한 없는 관리자는 거부한다.
- content 응답은 `Cache-Control: no-store`를 유지한다.
- 삭제 worker는 race/CAS를 방어하고, 도메인 연결이 늦게 생긴 업로드를 잘못 orphan으로 지우지 않는다.

역할별 오류를 안정적으로 구분하라. 예시 코드는 `PHOTO_ACCESS_REQUIRED`, `PHOTO_EXPIRED`, `PHOTO_NOT_AVAILABLE`, `RETENTION_STATE_CONFLICT`다. 기존 오류 규칙이 있으면 그 규칙에 맞추되 의미를 OpenAPI에 명시하라.

필수 테스트:

- 업로드 후 7일이 지나도 검사 대기 사진은 존재한다.
- 승인과 반려 각각 `decidedAt + 7일` 전후 경계를 검증한다.
- 실제 수행 메이드는 만료 전 과거 본인 제출을 읽을 수 있다.
- 다른 메이드는 읽을 수 없다.
- 만료 뒤 content는 거부되지만 history metadata는 남는다.
- 이슈/컴플레인/중단 증빙과 orphan이 서로 다른 보존 정책을 따른다.
- worker 재실행이 idempotent하다.

### 5.2 담당 메이드 PIN 접근 수명주기 수정

PIN 접근 권한과 30초 원문 reveal lease를 분리하라.

담당 메이드의 PIN 접근 권한은 다음과 같다.

- 주간 배정을 저장하고 알림 outbox가 생성되는 시점부터 시작한다.
- `availableFrom` 전이어도 이미 알림된 본인 배정이면 접근할 수 있다.
- 현장 완료, 사진 업로드 대기, 제출 완료, 검사 대기 동안 유지된다.
- 다음 중 하나가 최종 발생할 때 종료된다.
  - 검사 최종 승인 또는 반려
  - 취소 승인
  - 재배정으로 담당자 교체
  - 계정 비활성화 workflow의 해당 권한 최종 정리
- PIN 변경 시 열려 있는 원문 lease와 과거 revision을 즉시 무효화한다.
- 변경된 revision은 현재 담당자와 이미 알림된 다음 근무일 담당자에게 적용된다.
- 원문 자체를 알림 payload나 로그에 넣지 않는다.

필수 구현:

- 장기 수명의 assignment entitlement와 최대 30초 reveal lease를 별도 모델로 둔다.
- entitlement는 정확한 assignment/room/maid/revision에 귀속한다.
- reveal 때 현재 assignment 소유권과 PIN revision을 다시 검증한다.
- 재배정·취소·최종 검사·비활성화가 entitlement를 원자적으로 종료하고 outbox/audit를 남긴다.
- 관리자 PIN 변경 권한과 메이드의 허용된 PIN 변경 범위는 기존 역할 정책을 유지하되, 변경 뒤 구 revision을 재사용할 수 없어야 한다.

필수 테스트:

- 알림된 배정은 시작 시각 전에도 본인만 PIN을 조회할 수 있다.
- 현장 완료·업로드 대기·검사 대기에도 접근이 유지된다.
- 승인/반려/취소/재배정/비활성화 완료 직후 접근이 끊긴다.
- lease 발급 뒤 PIN을 바꾸면 구 lease가 남은 30초와 무관하게 실패한다.
- 다음 근무일에 이미 알림된 담당자는 새 revision을 얻고, 그 밖의 메이드는 얻지 못한다.
- URL·로그·알림·감사 metadata에 PIN 원문이 없다.

## 6. 단계 2 — 객실·예약·장기 투숙·방 이동

### 6.1 객실 대표 상태 투영

DB의 여러 상태를 하나로 덮어쓰지 말고 읽기 projection으로 제공하라. `RoomProjection` 또는 호환되는 응답에 다음 축을 추가한다.

- `occupancyStatus`
- `reservationLifecycle`
- `readinessStatus`
- `primaryDisplayStatus`
- `nextReservationId`
- `nextCheckInAt`
- `nextCheckOutAt`
- `blockingReasonCodes`
- `readinessReasonCodes`
- `pinSyncStatus`
- `serverTime`

예약 수명주기 의미:

- `NONE`
- `FUTURE`
- `RESERVATION_PRESENT`: 체크인 전날(D-1)
- `ARRIVAL_PENDING`: 체크인 당일이며 체크인 시각 전
- `OCCUPIED`

대표 상태 우선순위:

`BLOCKED > OCCUPIED > ARRIVAL_PENDING > RESERVATION_PRESENT > CLEANING_REQUIRED > READY`

`allocationReady` 같은 현재 시점 준비 boolean은 미래 기간 예약 가능 여부로 재사용하지 마라.

### 6.2 임의 기간 예약 가능 여부와 범위 조회

빠른 예약/예약 변경에서 사용할 read-only preview를 추가하라. 권장 계약은 다음과 같다. 저장소 naming 규칙에 맞춰 경로를 조정할 수 있지만 의미와 필드는 유지하라.

`POST /v1/reservations/bookability/preview`

요청:

```json
{
  "checkInAt": "2026-09-20T15:00:00+09:00",
  "checkOutAt": "2026-09-22T11:00:00+09:00",
  "reservationType": "standard",
  "excludeReservationId": null,
  "roomTypeIds": []
}
```

응답의 각 후보 객실:

```json
{
  "roomId": "uuid",
  "roomNumber": "201",
  "roomTypeId": "uuid",
  "roomStateVersion": 12,
  "intervalBookable": true,
  "checkInReady": false,
  "reasonCodes": [],
  "evaluatedAt": "2026-09-16T12:00:00+09:00"
}
```

- 시간 구간은 `[checkInAt, checkOutAt)`로 정의한다.
- DB exclusion constraint 또는 동등한 최종 제약이 race의 최종 권위다.
- preview 결과는 예약 생성/변경 성공을 보장하지 않으며, commit은 동일 조건을 트랜잭션 안에서 재검증한다.
- `excludeReservationId`는 자기 예약 변경 preview에만 권한 검증 후 사용한다.
- 종료 미정 장기 투숙은 별도 규칙에 따라 미래 무한대까지 차단한다.

달력의 29일 구간과 이전/다음 주 이동을 위해 범위 조회를 제공하라.

`GET /v1/reservations?from={rfc3339}&to={rfc3339}&roomId={optional}&cursor={optional}`

- 요청 범위와 겹치는 예약을 반환한다.
- 메이드에게 고객명/연락처 같은 예약 PII를 노출하지 않는다.
- 안정적인 정렬, cursor, serverTime을 제공한다.

### 6.3 장기 투숙과 종료 미정

예약에 명시적인 타입을 추가한다.

- `reservationType`: `standard | long_stay`
- `standard`는 `checkOutAt` 필수
- `long_stay`는 종료 확정 또는 `checkOutAt = null` 허용
- 종료 미정 장기 투숙은 해당 객실의 미래 예약 가능 기간을 무한대로 막는다.
- 종료 시각이 없을 때 체크아웃 청소 target/obligation을 미리 만들지 않는다.
- 종료 시각을 나중에 확정하면 정확히 하나의 체크아웃 청소 obligation을 생성하거나 갱신한다.
- 수동 체크아웃도 정확히 하나의 청소 target을 만든다.
- 재시도나 동시 요청으로 중복 청소가 생기지 않아야 한다.
- 응답은 프런트가 `장기` badge와 종료 미정을 표시할 수 있어야 한다.

기존 non-null `checkOutAt` 및 checkout obligation 제약을 새 append-only 마이그레이션으로 안전하게 확장하고, standard 기존 데이터 backfill을 제공하라.

### 6.4 방 이동 preview/commit

`DOCS/24_RESERVATION_ARRIVAL_ROOM_MOVE_BACKEND_HANDOFF.md`의 계약을 그대로 구현하라. 그 문서의 request/response, 오류 코드, 구간 분할, PIN/청소/outbox, CAS/idempotency, 트랜잭션 요구를 임의로 축약하지 마라.

핵심 불변식:

- preview와 commit을 분리한다.
- commit은 원 예약/객실 version과 가용성을 다시 검증한다.
- 예약 구간은 겹치지 않는다.
- 이동 전/후 체류 구간과 청소 obligation이 정확히 한 번 생성된다.
- 현재/미래 담당자의 PIN entitlement와 알림이 새 객실 기준으로 정리된다.
- 종료 미정 장기 투숙 이동에서 종료 시각이 필요한 경우 `OPEN_ENDED_STAY_REQUIRES_END`를 반환한다.
- 일부만 반영된 상태를 남기지 않는다.

필수 통합 테스트는 같은 객실, 점유/예약 충돌, stale version, preview 이후 경쟁 예약, 부분 체류 이동, D-day 도착 전 이동, 점유 중 이동, 종료 미정 장기 투숙, idempotent retry, outbox 실패를 포함한다.

## 7. 단계 3 — UI를 채우는 안전한 읽기 계약

### 7.1 객실 타입 카탈로그

기존 `PATCH /v1/rooms/{roomId}/master-data`를 다시 만들지 마라. 안전한 선택값이 없어서 프런트가 편집을 잠근 상태다.

관리자용 `GET /v1/room-types`를 추가한다.

최소 필드:

```json
{
  "items": [
    {
      "id": "uuid",
      "code": "DOUBLE",
      "displayName": "더블",
      "baseCleaningFee": 20000,
      "active": true,
      "version": 3,
      "roomCount": 8
    }
  ]
}
```

- `baseCleaningFee`는 정수 원화다.
- 비활성 타입과 기존 객실 참조 정책을 문서화한다.
- master-data mutation은 room의 expected stateVersion으로 CAS한다.
- 존재하지 않거나 비활성인 타입, stale version을 안정적인 오류 코드로 구분한다.

### 7.2 배정 카드 projection 확장

배정 목록과 이력이 내부 테이블 추가 조회 없이 기존 카드에 필요한 값을 갖도록 snapshot을 추가한다.

- `cleaningKind`
- `roomTypeCode`
- `roomTypeName`
- `elevatorZone`
- `feeSnapshot`
- `durationMinutes` (미정이면 `null`)
- `originalServiceDate`
- `serviceDate`
- `rolloverCount`
- `rolloverReason`
- `targetStatus`
- 필요한 최소 attempt/submission 요약

금액과 객실 타입은 사후 master-data 변경에 흔들리지 않는 immutable snapshot을 우선한다. live 값과 snapshot 값이 모두 필요하면 필드 이름으로 구분한다. `0`과 `null`을 혼동하지 마라.

### 7.3 청소 완료 이력

권장 경로:

- `GET /v1/cleaning-history`
- `GET /v1/cleaning-history/{submissionId}`

목록 규칙:

- 관리자 `완료` 탭의 선택일 D를 포함해 KST `D-6 ... D` 정확히 7일을 조회한다.
- `fieldCompletedAt`의 KST 일자로 그룹화한다.
- 최신 그룹·최신 항목부터 정렬한다.
- 관리자만 `maidProfileId`, 객실 번호/실제 수행자 표시명 `query` 필터를 사용할 수 있다.
- 메이드는 본인 기록만 볼 수 있다.
- 관리자 메이드 상세에서도 같은 source of truth를 쓴다.
- cursor/limit와 안정 정렬을 제공한다.

안전한 상세 필드:

- `submissionId`, `attemptId`, `cleaningTargetId`
- 객실 ID/번호/타입 snapshot
- 실제 수행자 ID/표시명
- 청소 종류
- 원래 서비스 일자와 실제 서비스 일자
- `startedAt`, `fieldCompletedAt`, `submittedAt`
- 검사 결정/사유/결정자 역할/`decidedAt`
- `photoCount`, `mediaAvailability`, `expiresAt`
- 제출 당시 immutable 사진 슬롯 label/status
- 촛불 개수와 폭탄 처리 결정
- 허용된 제출 메모
- 수입 breakdown

현재 제출 생성 계약에 메모가 없다면 bounded·PII-screened `submissionNote`를 optional로 추가하고 제출 시 immutable하게 저장한다. 과거 체크리스트를 되살리지 마라. 최신 사진 슬롯 정책이 정본이다. `reviewContext`에도 관리자 검수 화면에 필요한 실제 수행자 표시명을 안전하게 추가한다.

### 7.4 주간 근무 이력

`DOCS/16`의 서로 다른 세 사건을 합치지 말고 별도 배열/집합으로 제공하라.

- 근무 가능일 제출 날짜
- 배정 저장·알림 날짜
- 실제 현장 완료 날짜

권장 경로:

`GET /v1/work-history?weekStart={yyyy-mm-dd}&maidProfileId={admin-only}&cursor={optional}`

응답에는 주차, 대상 메이드, 세 사건별 날짜/개수, 데이터 기준 시각을 포함한다. 집계 표현은 `distinct maid 수 = N명`, `메이드별 기록 일수 합 = N일`을 구분한다. 가능일 또는 배정일을 실제 근무일로 추정하지 마라. 관리자는 전체/개별, 메이드는 노출할 경우 본인만 허용한다.

### 7.5 객실 운영 차단·이슈 목록과 타임라인

현재 생성/해제/해결 command가 있어도 과거 브라우저 세션이나 새 기기에서 entity ID를 재조회할 목록이 없다. 다음 read model을 추가하라.

- `GET /v1/rooms/{roomId}/operation-blocks?status=active|all`
- `GET /v1/rooms/{roomId}/issues?status=open|all`
- `GET /v1/rooms/{roomId}/events?cursor={optional}&limit={optional}`

타임라인에는 객실 기준정보, 예약/점유, 차단/해제, 촛불, 이슈/해결, 청소 상태, PIN 변경 metadata를 포함할 수 있다. 다음은 포함하지 않는다.

- PIN 원문
- 고객 PII
- 사진 원문 또는 provider locator
- 비공개 인증 정보

각 항목에는 안정적인 entity ID, 상태, version, 발생 시각, 행위자 역할, 안전한 요약을 제공한다. 새 세션에서도 유효한 항목을 열고 권한 있는 command를 수행할 수 있어야 한다.

메이드가 현장에서 객실 이슈와 증빙을 올리는 흐름이 현재 없다면 다음 의미의 command를 추가하라.

`POST /v1/attempts/{attemptId}/room-issues`

- category
- optional bounded PII-screened note
- evidence photo IDs
- expected attempt/assignment versions
- idempotency key

본인 현재 attempt만 허용하고, 관리자 목록/상세/해결과 연결한다. 증빙은 해결 후 180일 정책을 따른다.

### 7.6 급여 상세와 정정 version

`PayrollAdjustmentEntry`에 정정/취소 command가 사용할 `bookVersion` 또는 저장소의 동등한 CAS version을 반드시 반환하라.

급여 원장 각 행에는 최소 다음 immutable snapshot을 제공한다.

- 객실 번호
- 객실 타입
- 청소 종류
- 기본 청소비
- 폭탄/추가 수당
- 총액
- 지급/정산 상태
- 수입 발생 ID와 일자

알림의 `payrollCycle` entityId를 다시 읽을 수 있도록 역할/소유권이 적용된 resolver를 추가한다.

- `GET /v1/payroll/cycles/{cycleId}` 또는 동등한 by-ID 계약
- 필요하면 cycle별 entries endpoint

기존 weekStart 기반 조회만으로 entityId deep-link를 해결하게 추측하지 마라.

### 7.7 알림 deep-link 재조회 불변식

현재 deep-link 구조가 `{kind, entityId}`라면 구조 자체를 불필요하게 바꾸지 마라. 대신 다음 불변식을 지켜라.

> 백엔드는 수신 역할이 해당 `entityId`를 서버에서 다시 읽을 수 있을 때만 deep-link kind를 발행한다.

아래 kind를 전수 점검하라.

- `cleaningTarget`
- `assignmentRequest`
- `submission`
- `complaintCase`
- `payrollCycle`
- `payrollProfile`

없는 by-ID resolver를 역할/소유권 검증과 함께 추가하거나, 해결할 수 없는 kind의 발행을 중단한다. `payrollProfile`처럼 주차가 필요한 화면은 entityId만으로 정확한 destination을 복원할 수 있는 서버 read model을 제공한다. 알림 payload에 고객 PII, PIN, 사진 locator를 추가해서 해결하지 마라.

## 8. 단계 4 — 계정 비활성화와 이의/증빙 workflow

### 8.1 메이드 계정 비활성화

현재 `active → inactive/departed` 직접 변경만으로는 진행 중 업무와 업로드 권한을 안전하게 정리할 수 없다. 다음 상태 의미를 지원하라.

- `active`
- `deactivation_pending`
- `upload_only`
- 최종 `inactive | departed`

관리자가 시작 전에 확인할 영향도:

- 시작하지 않은 배정
- 진행 중 attempt
- 현장 완료했지만 미제출
- 제출 완료/검사 대기
- 미지급 수입
- 열린 PIN entitlement/lease와 업로드 capability

권장 계약:

- `GET /v1/accounts/{profileId}/deactivation-impact`
- `POST /v1/accounts/{profileId}/deactivation/start`
- `GET /v1/accounts/{profileId}/deactivation`
- `POST /v1/accounts/{profileId}/deactivation/finalize`

`start`는 목표 최종 상태, 진행 중 attempt별 `finish_current | interrupt_and_handover`, expected account version 또는 impact fingerprint, idempotency key를 받는다.

정책:

- 시작 즉시 신규 업무·신규 배정·신규 PIN entitlement를 차단한다.
- 진행 중 업무는 관리자가 `현재 업무 완료` 또는 `중단 후 인계`를 선택한다.
- 현장 완료/미제출 업무는 24시간의 제한적 업로드·유효 제출 권한을 가질 수 있다.
- 중단된 이전 메이드는 증빙 업로드만 가능하고 유효 제출·수입 획득은 불가하다.
- 검사 대기와 미지급 수입 기록은 소실하지 않는다.
- 모든 assignment, attempt, lease, capability가 정책대로 정리된 뒤에만 최종화한다.
- 최종화에서 세션을 폐기한다.
- 마지막 활성 관리자 보호를 유지한다.
- 기존 direct status endpoint는 영향이 없는 안전한 경우만 허용하거나 `ACCOUNT_DEACTIVATION_WORKFLOW_REQUIRED`로 거부한다.

전체 과정은 CAS, idempotency, transaction/outbox, 감사 event를 가져야 한다.

### 8.2 컴플레인 계약 보강

현재 category/finding/penalty/rework/reason enum만으로는 기존 UI의 사실 확인과 이의 기록을 보존할 수 없다. 다음을 optional·bounded·PII-screened 필드 또는 append-only event로 추가하라.

- 민감정보를 제거한 complaint content
- evidence photo IDs
- 관리자 review/fact-check note
- decision/evaluation note
- 메이드 appeal/objection note
- 행위자 역할·시각·version을 가진 append-only 사건 이력

고객 PII를 메이드에게 노출하지 않는다. 컴플레인 생성 또는 결정만으로 급여를 자동 차감하지 않는다. 차감은 별도 급여 조정 command와 CAS/audit를 거쳐야 한다. 증빙은 종결 후 180일 정책을 따른다.

## 9. 단계 5 — provider 운영 활성화

기능 소스를 중복 작성하지 말고 현재 adapter/worker를 기준으로 다음을 검증한다.

### Google PIN 시트

- 운영 Sheet/탭/컬럼 mapping
- service account 권한과 ACL
- 암호화된 secret 주입
- 전체 resync와 증분/outbox worker
- 실패/재시도/dead-letter 또는 운영 경보
- status endpoint가 실제 마지막 성공/실패를 정직하게 반환하는지
- Cron/스케줄러 양성 smoke

### Web Push

- VAPID public/private key
- provider invoke secret
- subscription 등록/폐기
- 만료 endpoint 정리
- 실제 기기 양성 delivery
- heartbeat/worker 관찰성

### 사진 저장소

- Drive/OAuth 또는 현재 선택된 provider credential
- 개별 사진 upload/read 권한과 `객실호수_YYYY-MM-DD` KST 폴더 생성
- client path를 받지 않는 서버 파생 폴더명과 opaque 객체명
- ZIP·batch 업로드·ZIP provider 객체 없음
- content 조회 no-store
- 도메인별 retention worker
- purge Cron 양성 smoke
- provider 실패 시 metadata 일관성

운영 비밀값이나 외부 계정 승인이 없어 실행할 수 없는 항목은 우회하지 마라. 정확한 secret 이름, 소유자에게 필요한 조치, 실행할 smoke 명령, 기대 결과를 체크리스트로 남긴다. `코드 있음`을 `운영 활성`로 보고하지 마라.

## 10. OpenAPI와 오류 계약

모든 public 변경은 구현과 같은 PR에서 OpenAPI를 갱신한다.

- 현재 검토 기준 `0.5.1`에서 사진 수신 시간·오류·저장 구조의 public 의미가 바뀌므로 버전을 그대로 두지 않는다. 저장소 release 규칙에 맞는 다음 버전을 선택하고 migration note를 남긴다.
- request/response example을 추가한다.
- nullable, enum, money 단위, KST date 계산, RFC 3339 timestamp를 명시한다.
- 각 endpoint의 역할과 소유권을 명시한다.
- `401`, `403`, `404`, `409`, `422`를 숨기지 말고 안정적인 domain error code를 문서화한다.
- `expectedVersion`과 `Idempotency-Key`가 필요한 곳을 정확히 표시한다.
- list endpoint는 정렬, cursor, limit, 빈 결과 의미를 명시한다.

기존 저장소 naming 규칙을 우선하되 다음 오류 의미가 구분되어야 한다.

- 권한 없음 / 소유권 없음
- stale version
- idempotency payload mismatch
- 예약 기간 겹침
- 종료 미정 장기 투숙 제약
- 객실 타입 없음/비활성
- PIN entitlement 종료/구 revision
- 사진 만료/권한 없음/provider unavailable
- 잘못된 이력 범위
- 비활성화 workflow 필요/영향도 변경/최종화 불가

`DOCS/24`에 이미 정의된 방 이동 오류 코드는 그 문서를 그대로 따른다.

## 11. 필수 검증

각 PR마다 다음 중 해당 항목을 실제로 실행하고, 실행하지 못한 항목은 이유를 적는다.

- formatter/linter/typecheck
- 전체 application unit/integration test
- 새 마이그레이션을 포함한 빈 DB reset
- 기존 `0.3.0` 형태 데이터에서 forward migration/backfill 검증
- OpenAPI schema validation과 generated type/build 검증
- 역할 matrix 테스트: admin / assigned maid / other maid / inactive maid
- CAS 경쟁 테스트
- idempotent retry와 payload mismatch 테스트
- transaction rollback/outbox retry 테스트
- KST 날짜 경계, DST에 의존하지 않는 계산 테스트
- 민감정보가 URL·로그·알림·감사 metadata에 없는지 테스트
- 사진·PIN·예약 겹침의 DB 수준 불변식 테스트
- 실제 12MP JPEG와 HEIC/HEIF의 Edge peak RSS·CPU·wall time·동시 업로드 resource gate
- 진행 중인 느린 stream, 30초 idle, 5MiB+1, client abort의 수신·cleanup 테스트

프런트 UI 회귀 조건도 API acceptance test로 표현하라.

- 기존 객실 카드가 재설계 없이 대표 상태를 표시할 수 있다.
- 객실 기본정보 편집이 room type catalog와 기존 master-data mutation으로 동작한다.
- 빠른 예약과 이전/다음 기간 조회가 fixture 없이 동작한다.
- 장기/종료 미정 표시와 예약 차단이 가능하다.
- 방 이동 버튼이 preview 후 commit으로 원래 목적을 수행한다.
- 관리자 청소 완료 7일 이력과 메이드 본인 이력이 같은 source of truth를 사용한다.
- 주간 가능일/배정일/실근무일을 혼동하지 않는다.
- 급여 정정 UI가 응답의 version으로 재요청할 수 있다.
- 알림의 모든 발행된 deep-link가 새 세션에서 열릴 수 있다.
- 과거 세션에서도 객실 차단/이슈를 목록으로 재조회할 수 있다.
- 비활성화 중인 메이드가 정책 밖 신규 업무/PIN을 얻지 못한다.

## 12. PR 분리 권장안

서로 독립 검토와 rollback이 가능하도록 최소 다음 단위로 나눈다.

1. `문서: 백엔드 제품 정책 기준선을 갱신하라`
2. `수정: 사진 개별 업로드 수신과 저장 계약을 바로잡아라`
3. `수정: 사진 보존 시점과 조회 권한을 바로잡아라`
4. `수정: 담당 메이드 PIN 접근 수명주기를 바로잡아라`
5. `기능: 객실 예약 상태와 기간 가용성 계약을 추가하라`
6. `기능: 장기 투숙과 방 이동 계약을 구현하라`
7. `기능: 객실 타입과 청소·근무 이력 조회를 추가하라`
8. `기능: 객실 사건·급여·알림 조회 계약을 보강하라`
9. `기능: 계정 비활성화와 이의 증빙 절차를 완성하라`
10. `운영: 외부 provider 활성화 상태를 검증하라`

실제 코드 결합도에 따라 인접 PR을 조정할 수 있지만 사진/PIN 안전 수정은 거대한 기능 PR에 묶어 지연시키지 마라. 각 PR은 `dev` 기준이며, 필수 검사가 통과하고 리뷰/보호 규칙이 허용할 때만 병합한다.

## 13. 완료 보고 형식

최종 답변은 아래 표를 채워 제공하라.

| 영역 | 소스 구현 | OpenAPI | 마이그레이션 | 자동 테스트 | 호스팅 활성 | PR/커밋 | 프런트 후속 |
|---|---|---|---|---|---|---|---|
| 사진 보존 |  |  |  |  |  |  |  |
| PIN 접근 |  |  |  |  |  |  |  |
| 객실 상태/가용성 |  |  |  |  |  |  |  |
| 장기 투숙/방 이동 |  |  |  |  |  |  |  |
| 카탈로그/이력 |  |  |  |  |  |  |  |
| 급여/알림 |  |  |  |  |  |  |  |
| 비활성화/컴플레인 |  |  |  |  |  |  |  |
| 외부 provider |  |  |  |  |  |  |  |

그리고 반드시 다음을 별도로 적어라.

1. PR URL과 기준/병합 커밋
2. 실제 적용된 migration 파일 목록과 backfill 결과
3. OpenAPI 이전/이후 버전과 endpoint/schema diff
4. 역할별 권한 matrix
5. 실행한 검증 명령과 결과
6. `소스 구현 완료`와 `운영 활성 확인`의 구분
7. 아직 막힌 항목의 정확한 credential/외부 승인/제품 결정
8. 프런트가 제거할 수 있는 각 `API 미제공` 문구와 대응 endpoint/필드
9. 프런트 adapter가 알아야 할 breaking/additive 변경

아래와 같은 모호한 완료 보고는 금지한다.

- “API 연결 완료”
- “대부분 구현됨”
- “환경변수만 넣으면 됨”
- “테스트는 통과할 것임”

구현, 문서, 테스트, 호스팅 양성 검증을 각각 근거와 함께 보고하라. 작업 도중 계약 충돌이 발생하면 화면을 바꾸라는 결론부터 내리지 말고, 충돌한 정본 문구, 현재 schema/endpoint, 가능한 최소 계약 변경, 데이터 migration 영향을 제시하라.

이제 기준선 비교부터 시작하고, 단계 0부터 순서대로 구현하라.

## 실행 프롬프트 끝

---

## 프런트엔드 담당자 참고

이 문서는 백엔드 Codex 입력용 실행 계약이다. 백엔드가 각 단계의 OpenAPI와 배포 상태를 인계하기 전까지 프런트 운영 모드에서 누락값을 fixture로 대체하지 않는다. 응답 계약이 도착하면 기존 `WIREFRAME/index.html`의 화면 구조를 유지하고 adapter/view-model 및 기존 버튼의 실제 command 연결만 갱신한다.
