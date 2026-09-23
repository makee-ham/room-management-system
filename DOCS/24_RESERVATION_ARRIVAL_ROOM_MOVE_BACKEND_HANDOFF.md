# 예약 임박 상태·객실 변경 백엔드 구현 인계

- 결정일: 2026-09-16
- 대상: 운영 백엔드 Codex
- UI 정본: `WIREFRAME/index.html`
- 제품 정책 정본: `DOCS/17_ROOM_CATALOG_LONG_STAY_DECISIONS.md`의 2026-09-16 절
- 현재 운영 API 상태: 객실 변경·방 이동 계약 미제공. 프런트 운영 모드는 성공을 가장하지 않고 `API 미제공`으로 표시한다.

## 1. 구현 목표

다음 네 가지를 서로 다른 축으로 모델링한다.

1. 현재 점유: `VACANT | OCCUPIED`
2. 예약 임박 단계: `NONE | FUTURE | RESERVATION_PRESENT | ARRIVAL_PENDING | OCCUPIED`
3. 현재 준비 상태: `READY | CLEANING_REQUIRED | CHECKIN_BLOCKED`
4. 요청 구간 예약 가능 여부: `isBookableForInterval(roomId, checkInAt, checkOutAt)`

`allocationReady` 같은 현재 시점 boolean 하나로 미래 예약 가능 여부를 판단하지 않는다. 미래 예약이 있어도 요청 구간이 겹치지 않으면 예약할 수 있다.

## 2. 시간 규칙

모든 비교는 숙소 운영 시간대 `Asia/Seoul`에서 하고 API 시각은 offset이 있는 ISO 8601로 주고받는다. 예약 구간은 반열림 구간 `[checkInAt, checkOutAt)`이다.

| 조건 | `reservationLifecycle` | 화면 큰 상태 후보 |
| --- | --- | --- |
| 현재 구간에 포함 | `OCCUPIED` | `투숙 중` |
| 다음 체크인 날짜 = 오늘, 현재 < 체크인 시각 | `ARRIVAL_PENDING` | `입실 예정` |
| 다음 체크인 날짜 = 내일 | `RESERVATION_PRESENT` | `예약 있음` |
| 다음 체크인 날짜 ≥ 모레 | `FUTURE` | 현재 준비 상태 유지 |
| 다음 예약 없음 | `NONE` | 현재 준비 상태 유지 |

큰 상태 우선순위는 `BLOCKED → OCCUPIED → ARRIVAL_PENDING → RESERVATION_PRESENT → CLEANING_REQUIRED → READY`다. `BLOCKED`는 운영 중지·입실 차단·PIN/기준정보 확인 보류 같은 실제 차단만 뜻한다. 청소 미완료는 `CLEANING_REQUIRED`이고, 예약 임박 상태와 동시에 보조 상태로 반환할 수 있다.

체크인 시각 전환은 반복 실행해도 결과가 같은 idempotent projection이어야 한다. 배치 작업만 신뢰하지 말고 객실 조회 시에도 서버 시각을 기준으로 파생값을 계산해 지연된 스케줄러를 보정한다.

## 3. 조회 모델 변경

`GET /v1/rooms`와 `GET /v1/rooms/{roomId}`에 다음 필드를 추가한다. 이름은 기존 백엔드 명명 규칙에 맞게 바꿔도 되지만 의미를 합치지 않는다.

```json
{
  "occupancyStatus": "VACANT",
  "reservationLifecycle": "ARRIVAL_PENDING",
  "readinessStatus": "CLEANING_REQUIRED",
  "primaryDisplayStatus": "ARRIVAL_PENDING",
  "nextReservationId": "uuid-or-null",
  "nextCheckInAt": "2026-09-16T16:00:00+09:00",
  "nextCheckOutAt": "2026-09-17T11:00:00+09:00",
  "blockingReasonCodes": [],
  "readinessReasonCodes": ["CLEANING_REQUIRED"],
  "stateVersion": 14,
  "serverTime": "2026-09-16T10:32:00+09:00"
}
```

`isBookable`을 객실 목록의 영구 속성으로 추가하지 않는다. 예약 생성·변경·이동 preview에서 요청 구간을 받아 계산한다.

## 4. 저장 모델

### 4.1 예약 전 객실 변경

기존 `reservations.id`는 유지하고 `room_id`, `version`, `updated_at`만 변경한다. 감사 이벤트는 별도 append-only 테이블에 남긴다.

### 4.2 투숙 중 방 이동

투숙 중에는 기존 예약 행의 객실을 덮어쓰지 않는다. 아래 중 현재 모델과 잘 맞는 하나를 택한다.

- 권장: `stays` 1건 + `stay_room_segments` N건
- 기존 예약 중심 모델을 유지해야 한다면: 동일 `stay_group_id`로 연결된 예약 구간 N건

권장 최소 필드:

```text
stay_room_segments
- id uuid pk
- stay_id uuid not null
- room_id uuid not null
- starts_at timestamptz not null
- ends_at timestamptz null
- source_reservation_id uuid null
- move_event_id uuid null
- version bigint not null
- created_at / updated_at timestamptz

reservation_room_move_events
- id uuid pk
- reservation_id uuid not null
- stay_id uuid null
- from_room_id uuid not null
- to_room_id uuid not null
- effective_at timestamptz not null
- mode text check in ('BEFORE_CHECKIN','DURING_STAY')
- reason_code text not null
- actor_profile_id uuid not null
- source_version bigint not null
- target_room_version bigint not null
- idempotency_key text not null unique
- created_at timestamptz not null
```

활성 예약/구간에는 PostgreSQL exclusion constraint로 같은 객실의 `tstzrange(starts_at, ends_at, '[)')` 겹침을 DB에서도 막는다. soft-cancel/종료 행은 partial predicate로 제외한다. 애플리케이션 사전 검사만으로 동시 요청을 막지 않는다.

## 5. API 계약

### 5.1 Preview

`POST /v1/reservations/{reservationId}/room-change/preview`

```json
{
  "targetRoomId": "uuid",
  "effectiveAt": "2026-09-16T18:20:00+09:00",
  "reasonCode": "GUEST_REQUEST",
  "expectedReservationVersion": 7,
  "expectedSourceRoomVersion": 14,
  "expectedTargetRoomVersion": 9
}
```

체크인 전에는 `effectiveAt`을 생략하거나 예약 체크인 시각과 같게 한다. 투숙 중에는 서버 현재 시각보다 과거이거나 체크아웃 이후일 수 없다.

응답에는 다음을 포함한다.

```json
{
  "mode": "DURING_STAY",
  "allowed": true,
  "impactFingerprint": "opaque-hash",
  "effectiveAt": "2026-09-16T18:20:00+09:00",
  "sourceOutcome": {"occupancyStatus": "VACANT", "readinessStatus": "CLEANING_REQUIRED"},
  "targetOutcome": {"occupancyStatus": "OCCUPIED"},
  "warnings": [],
  "blockingReasonCodes": [],
  "expiresAt": "2026-09-16T18:22:00+09:00"
}
```

### 5.2 Commit

`POST /v1/reservations/{reservationId}/room-change`

Preview payload에 다음을 추가한다.

```json
{
  "impactFingerprint": "opaque-hash",
  "idempotencyKey": "uuid"
}
```

HTTP `Idempotency-Key` 헤더를 정본으로 써도 된다. 같은 key와 같은 payload 재시도는 같은 성공 응답을 반환하고, 같은 key의 다른 payload는 `409 IDEMPOTENCY_KEY_REUSED`다.

성공 응답은 변경된 예약/stay, 원·대상 객실 projection, 생성·변경된 청소 대상 ID, PIN lease 처리 결과, 새 version을 반환한다. 고객 이름·PIN 원문은 응답에 넣지 않는다.

## 6. 단일 트랜잭션 순서

1. 인증 사용자가 활성 관리자임을 확인한다.
2. 예약/stay와 원·대상 객실을 UUID 정렬 순서로 `FOR UPDATE` 잠근다.
3. expected version과 preview fingerprint를 비교한다.
4. 서버 시각으로 `BEFORE_CHECKIN` 또는 `DURING_STAY`를 다시 계산한다.
5. 대상 객실의 전체 적용 구간 겹침과 운영 차단을 확인한다.
6. 투숙 중 이동이면 대상 객실의 현재 `VACANT + READY`와 활성 PIN/청소 충돌을 확인한다.
7. 체크인 전이면 예약의 `room_id`만 변경하고 ID·일정·고객·인원은 유지한다.
8. 투숙 중이면 원 구간을 `effectiveAt`에 닫고 대상 객실 새 구간을 원 체크아웃까지 생성한다.
9. 원 객실 퇴실 청소 대상을 생성/재사용하고, 최종 체크아웃 청소 대상을 새 객실로 연결한다. 공개·담당·시작된 작업은 묵시적으로 이동하지 않는다.
10. 원 객실 PIN lease를 폐기하고 대상 객실 접근 권한을 새 구간에 연결한다. PIN 원문은 이벤트·로그에 쓰지 않는다.
11. append-only 이동 이벤트와 감사 로그를 기록하고 양쪽 객실 `stateVersion`을 증가시킨다.
12. outbox 이벤트를 같은 트랜잭션에 기록한 뒤 commit한다. 알림 전송 실패로 본 트랜잭션을 롤백하지 않는다.

중간 단계 하나라도 실패하면 예약·구간·청소·PIN·projection을 전부 롤백한다.

## 7. 오류 코드

| HTTP | code | 의미 |
| --- | --- | --- |
| 400 | `INVALID_MOVE_EFFECTIVE_AT` | 적용 시각이 허용 범위 밖 |
| 403 | `ADMIN_ROLE_REQUIRED` | 관리자 권한 없음 |
| 404 | `RESERVATION_NOT_FOUND` | 예약 없음 또는 접근 불가 |
| 409 | `RESERVATION_VERSION_CONFLICT` | 예약 version 변경 |
| 409 | `SOURCE_ROOM_VERSION_CONFLICT` | 원 객실 상태 변경 |
| 409 | `TARGET_ROOM_VERSION_CONFLICT` | 대상 객실 상태 변경 |
| 409 | `ROOM_CHANGE_PREVIEW_STALE` | preview fingerprint 만료/불일치 |
| 409 | `TARGET_ROOM_OVERLAP` | 적용 구간에 다른 예약/투숙이 겹침 |
| 409 | `TARGET_ROOM_BLOCKED` | 운영·입실 차단 상태 |
| 409 | `TARGET_ROOM_NOT_READY` | 투숙 중 이동 대상이 청소 미완료 |
| 409 | `CLEANING_ASSIGNMENT_LOCKED` | 공개·담당·시작된 청소 영향 |
| 409 | `PIN_LEASE_ACTIVE` | 안전하게 종료할 수 없는 PIN lease |
| 409 | `OPEN_ENDED_STAY_REQUIRES_END` | 종료일 미정 장기 투숙 |
| 409 | `MOVE_ALREADY_APPLIED` | 다른 key로 같은 이동이 이미 반영됨 |
| 409 | `IDEMPOTENCY_KEY_REUSED` | 같은 key에 다른 payload |

409 응답에는 최신 version, 재조회 대상 리소스, 사용자에게 표시할 안전한 reason code를 넣는다. 고객명·PIN·사진 URL은 오류나 로그에 포함하지 않는다.

## 8. 청소·PIN·알림 영향

- 체크인 전 변경: 아직 비공개인 최종 퇴실 청소 초안은 새 객실로 이동한다. 이미 공개/담당/시작이면 `CLEANING_ASSIGNMENT_LOCKED`다.
- 투숙 중 이동: 원 객실에는 이동 시각부터 시작 가능한 퇴실 청소 1건을 멱등 생성한다. 새 객실에는 원래 최종 체크아웃의 퇴실 청소를 유지/생성한다.
- 동일 예약/stay와 청소 종류별 멱등 키로 재시도 중복을 막는다.
- 원 객실 담당 메이드가 PIN을 조회했다면 lease를 즉시 폐기한다. 새 객실 PIN은 새 배정과 허용 시간에 따라 별도 조회한다.
- 알림은 객실번호, 적용 시각, 작업 ID만 포함하고 PIN·고객명을 넣지 않는다.

## 9. 마이그레이션·백필

1. move event와 segment 테이블, version/index/exclusion constraint를 추가한다.
2. 기존 활성 예약을 stay 1건·segment 1건으로 백필한다.
3. 백필 검증에서 객실별 구간 겹침을 먼저 보고하고 자동 삭제/수정하지 않는다.
4. read model 필드를 feature flag 아래 계산한다.
5. preview를 먼저 배포하고 UI와 shadow 비교한다.
6. commit endpoint와 outbox consumer를 배포한 뒤 feature flag를 켠다.

## 10. 필수 테스트

- D+2 예약은 주 상태를 바꾸지 않고, 겹치지 않는 다른 기간 예약이 가능하다.
- D-1 23:59:59는 `RESERVATION_PRESENT`, D-day 00:00부터 체크인 직전까지 `ARRIVAL_PENDING`, 체크인 시각부터 `OCCUPIED`다.
- 얼리 체크인/레이트 체크아웃의 실제 예약 시각을 사용한다.
- 체크인 전 변경은 예약 ID를 유지하고 원 객실 구간을 해제한다.
- 투숙 중 이동은 원 구간 종료·새 구간 시작 시각이 정확히 같고 과거 원 객실 이력이 보존된다.
- 투숙 중 이동 직후 원 객실은 `VACANT + CLEANING_REQUIRED`, 대상은 `OCCUPIED`다.
- 같은 객실·같은 기간 동시 이동 두 건 중 하나만 성공한다.
- stale version/fingerprint, 공개 청소, 진행 청소, PIN lease, 운영 중지 대상은 각각 지정된 409로 실패하고 부분 반영이 없다.
- 같은 idempotency key 재시도는 예약·segment·청소·이벤트를 중복 생성하지 않는다.
- 관리자 외 역할과 URL 직접 호출은 403이며 존재하지 않는 타인의 리소스를 노출하지 않는다.
- 애플리케이션 로그, 감사 로그, outbox, URL에 PIN 원문·고객명이 없다.

## 11. 완료 조건

- OpenAPI와 생성 타입에 위 조회 필드, preview/commit 요청·응답, 409 error enum이 반영된다.
- DB constraint와 트랜잭션 동시성 테스트가 통과한다.
- 운영 프런트가 fixture 없이 서버 projection을 기존 와이어프레임 자리에 표시한다.
- 운영 프런트의 `객실 변경·방 이동 API 미제공` 잠금이 실제 endpoint 성공/409 처리로 교체된다.
- 체크인 전 변경과 투숙 중 이동의 감사 이벤트를 관리자 타임라인에서 재조회할 수 있다.
