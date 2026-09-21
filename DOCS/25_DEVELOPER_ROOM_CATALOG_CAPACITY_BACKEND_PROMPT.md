# 개발자 객실·유형별 인원 관리 백엔드 구현 프롬프트

상태: 백엔드 전달용 제안 계약  
작성 기준: production OpenAPI `0.4.0` · 120 paths / 130 operations

아래 프롬프트를 백엔드 구현 작업에 그대로 전달한다.

---

Repo: `wrongstory/room-management-system-backend`

목표:

프런트 개발자 화면에서 객실 총계만 보는 수준을 넘어 다음 기준정보를 안전하게 관리할 수 있는 API를 추가한다.

1. 객실 유형별 `기준 인원`과 `최대 인원` 조회·변경
2. 객실 호수와 유형을 지정한 객실 추가
3. 예약·점유·청소·PIN 이력을 보존하는 객실 비활성화(프런트 문구는 객실 삭제)

현재 계약과의 차이:

- 현재 `DeveloperOverview.rooms`에는 `total`만 있다.
- 현재 `GET /v1/room-types`는 active business admin 전용이고 `RoomTypeCatalogItem`에는 기준·최대 인원 필드가 없다.
- 현재 `GET /v1/rooms`와 `PATCH /v1/rooms/{roomId}/master-data`도 admin 전용이다.
- 현재 객실 생성, 삭제 또는 비활성화 명령과 객실 유형 인원 변경 명령은 없다.
- 기존 인계 문서의 developer 역할은 계정·운영 상태만 허용한다. 이번 작업에서는 **객실 기준정보 관리만** developer에게 새로 허용하고, 예약·점유·청소·PIN 원문 등 운영 데이터 권한은 계속 금지한다.

## 1. 공통 원칙

- OpenAPI를 HTTP 계약의 정본으로 갱신하고 codegen 가능한 request/response schema, example, `x-required-roles`를 모두 제공한다.
- developer 응답에는 고객명, 예약 상세, PIN 상태·원문, 청소 사진, 메이드 개인정보를 포함하지 않는다.
- 모든 응답은 `Cache-Control: no-store`를 사용한다.
- 모든 변경 명령은 `Idempotency-Key`와 `expectedVersion` CAS를 사용한다. 응답 유실로 같은 body를 재전송할 때만 같은 key를 재사용한다.
- 오류는 `{ error: { code, message }, requestId }` 형태와 안정적인 `error.code`를 사용한다.
- 객실 삭제는 DB hard delete로 구현하지 않는다. 감사·예약·점유·청소·PIN 이력을 보존하는 `inactive` 전환으로 구현한다.
- service-role key, provider secret, PIN 원문은 응답·로그·감사 이벤트에 포함하지 않는다.

## 2. 객실 유형 인원 필드

기존 `RoomTypeCatalogItem`에 다음 required 필드를 추가한다.

```yaml
baseOccupancy:
  type: integer
  minimum: 1
  description: 기준 인원. 예약 인원이 이 값보다 클 때 프런트가 실제 총 인원을 강조한다.
maxOccupancy:
  type: integer
  minimum: 1
  description: 이 객실 유형에 허용되는 예약 총 인원 상한.
```

항상 `baseOccupancy <= maxOccupancy`여야 한다. 상한의 최대 허용값이 별도로 있다면 OpenAPI `maximum`과 사람이 읽는 설명에 정확히 명시한다.

이 문서의 JSON 숫자는 schema 설명용 예시일 뿐 production 초기값 승인으로 사용하지 않는다. 기존 네 유형의 실제 기준·최대 인원은 사용자 승인된 운영 자료로 migration backfill하고, 승인 근거가 없으면 프런트 데모값이나 임의 default로 채우지 않는다.

기존 admin용 `GET /v1/room-types`도 이 두 필드를 반환해 예약 등록·수정 화면이 같은 서버 값을 사용하게 한다. 프런트가 객실 유형 코드별 인원 값을 하드코딩하게 하지 않는다.

## 3. developer 전용 안전 조회

### `GET /v1/developer/room-catalog`

권한: 비밀번호 변경을 완료한 active `developer` 전용.

운영 객실 projection을 재사용하지 말고 다음 기준정보만 반환한다.

```json
{
  "generatedAt": "2026-09-20T00:00:00Z",
  "summary": {
    "total": 121,
    "active": 121,
    "inactive": 0
  },
  "roomTypes": [
    {
      "id": "uuid",
      "code": "standard",
      "displayName": "스탠다드",
      "baseOccupancy": 2,
      "maxOccupancy": 2,
      "active": true,
      "version": 1,
      "roomCount": 22
    }
  ],
  "rooms": [
    {
      "id": "uuid",
      "roomNumber": "350",
      "roomTypeId": "uuid",
      "roomTypeCode": "standard",
      "active": true,
      "version": 1
    }
  ]
}
```

`roomNumber`는 숫자가 아니라 안정적인 문자열로 유지한다. 목록에는 운영 상태, 예약 ID, 고객 정보, PIN·청소 정보를 넣지 않는다.

## 4. 유형별 인원 변경

### `POST /v1/developer/room-types/{roomTypeId}/capacity/preview`

```json
{
  "baseOccupancy": 2,
  "maxOccupancy": 4,
  "expectedVersion": 3
}
```

응답에는 다음을 포함한다.

- `roomTypeId`, 현재값, 변경값
- `roomCount`
- 현재·미래 active 예약 수
- 변경 후 최대 인원을 초과하게 되는 active 예약 수
- PII 없는 blocker reason code 목록
- 짧은 만료시간을 가진 `impactFingerprint`, `evaluatedAt`, `expiresAt`

### `PATCH /v1/developer/room-types/{roomTypeId}/capacity`

필수 header: `Idempotency-Key`

```json
{
  "baseOccupancy": 2,
  "maxOccupancy": 4,
  "expectedVersion": 3,
  "impactFingerprint": "opaque-preview-value",
  "reasonCode": "CAPACITY_POLICY_CHANGE"
}
```

preview와 값·version·영향이 달라졌으면 `409`로 거절한다. 최대 인원을 낮춰 기존 active 예약이 초과되는 경우에는 자동으로 예약을 취소하거나 인원을 줄이지 않는다. 서버 정책에 따라 변경을 차단하고 안정적인 reason code를 반환한다. 성공 시 증가한 room type version과 최신 카탈로그 항목을 반환하고 감사 이벤트를 남긴다.

## 5. 객실 추가

### `POST /v1/developer/rooms`

필수 header: `Idempotency-Key`

```json
{
  "roomNumber": "516",
  "roomTypeId": "uuid",
  "expectedRoomTypeVersion": 3,
  "reasonCode": "ROOM_CATALOG_ADD"
}
```

- `roomNumber` 정규화·중복 검증을 서버에서 수행한다.
- active 객실 유형만 선택할 수 있다.
- 새 객실은 불변 UUID와 version을 가진다.
- 새 객실을 즉시 `READY`로 만들지 않는다. 운영 준비·PIN·기준정보 확인에 필요한 안전한 초기 상태를 사용한다.
- 성공 응답에는 developer용 객실 항목, 최신 총계, 사용한 객실 유형 항목만 반환한다.

## 6. 객실 삭제 영향 확인과 비활성화

### `POST /v1/developer/rooms/{roomId}/deactivation/preview`

```json
{
  "expectedVersion": 4
}
```

응답에는 PII 없이 다음 영향 수와 blocker를 반환한다.

- 현재 점유 여부
- active·future 예약 수
- 진행 중 청소 대상·배정·attempt 수
- 활성 PIN 변경 lease 존재 여부
- 미해결 운영 차단·이슈 수
- `canDeactivate`, `reasonCodes`
- `impactFingerprint`, `evaluatedAt`, `expiresAt`

### `POST /v1/developer/rooms/{roomId}/deactivate`

필수 header: `Idempotency-Key`

```json
{
  "expectedVersion": 4,
  "impactFingerprint": "opaque-preview-value",
  "reasonCode": "ROOM_CATALOG_REMOVE"
}
```

현재 점유, active/future 예약, 진행 중 청소, 활성 PIN lease가 있으면 거절한다. 성공하면 객실을 inactive로 바꾸고 신규 예약·배정 후보에서 제외하되 기존 이력과 참조 무결성을 보존한다. 같은 명령 재전송은 중복 감사 이벤트나 중복 상태 전이를 만들지 않는다.

## 7. 예약 인원 계약 연결

- `POST /v1/reservations/bookability/preview`의 `guestCount`는 선택 필드다. 모달을 열기 전처럼 값을 생략하면 capacity 필터 없이 기간 bookability만 판정하고, 실제 인원 값이 있으면 각 candidate가 해당 유형의 `maxOccupancy`를 초과하는지 함께 판단한다. 임의 기본값을 서버나 프런트에서 보충하지 않는다.
- 초과 후보는 `intervalBookable=false`와 안정적인 `GUEST_COUNT_EXCEEDS_ROOM_TYPE_CAPACITY` reason code를 반환한다. 이 판정은 `checkInReady`와 섞지 않는다.
- 예약 생성·변경의 `guestCount`는 계속 필수다. 동일한 maxOccupancy를 다시 검증하며 preview를 통과했더라도 최신 type version과 capacity를 기준으로 commit 시 재검증한다.
- `baseOccupancy` 초과는 예약 불가 사유가 아니다. 프런트의 `N명` 강조와 `인원 추가` 필터 기준으로만 사용한다.
- 인원 기준 변경은 기존 예약의 guestCount, 과거 정산·청소 snapshot을 소급 수정하지 않는다.

## 8. 안정적인 오류 코드

최소 다음 code를 OpenAPI enum과 테스트에 추가한다.

- `ROOM_TYPE_CAPACITY_INVALID`
- `ROOM_TYPE_CAPACITY_ACTIVE_RESERVATION_CONFLICT`
- `ROOM_TYPE_CAPACITY_PREVIEW_STALE`
- `ROOM_TYPE_VERSION_CONFLICT`
- `ROOM_NUMBER_ALREADY_EXISTS`
- `ROOM_TYPE_INACTIVE`
- `ROOM_DEACTIVATION_BLOCKED`
- `ROOM_DEACTIVATION_PREVIEW_STALE`
- `GUEST_COUNT_EXCEEDS_ROOM_TYPE_CAPACITY`

권한·세션 오류는 기존 `401/403`, CAS·preview stale은 `409`, 존재하지 않는 ID는 `404`, 유효성 오류는 `400`을 유지한다.

## 9. 검증과 완료 조건

- developer는 위 developer catalog API만 사용할 수 있고 기존 운영 객실·예약·PIN endpoint는 계속 `403`이다.
- admin과 maid가 developer 변경 endpoint를 호출하면 `403`이다.
- 기준 인원 0, 최대 인원 0, 소수, `baseOccupancy > maxOccupancy`를 거절한다.
- 동일 Idempotency-Key·동일 body 재전송은 같은 결과를 반환하고 중복 변경을 만들지 않는다.
- 다른 body에 같은 key를 사용하면 기존 멱등성 충돌 규칙으로 거절한다.
- stale expectedVersion과 stale impactFingerprint를 `409`로 거절한다.
- 객실 호수 중복 생성 경쟁을 DB unique constraint로 막는다.
- 참조 이력이 있는 객실은 hard delete되지 않으며 비활성화 뒤에도 과거 예약·청소·감사 조회의 참조가 유지된다.
- OpenAPI 생성 타입과 backend tests를 갱신한다.
- 새 계약 배포 뒤 OpenAPI version, 전체 paths/operations 수, 배포 source commit, migration 수를 프런트 인계 문서에 기록한다.

금지:

- 기존 admin 운영 projection을 developer에게 그대로 공개하기
- 프런트에 service-role key나 provider secret 전달하기
- 객실 삭제 시 예약·청소·PIN·감사 이력을 cascade hard delete하기
- 한국어 `message` 문자열을 프런트 분기 계약으로 사용하기
- 기준 인원 초과를 최대 인원 초과와 같은 예약 불가로 처리하기
- 최대 인원을 초과한 예약을 서버가 임의로 취소하거나 인원 변경하기
