# 7. API와 트랜잭션 설계

## 조회 API 예시

```text
GET /api/room-operations?date=2026-08-14&view=guest-unavailable
GET /api/rooms/{roomId}?date=2026-08-14
GET /api/rooms?candleState=present
GET /api/cleaning-tasks/market?date=2026-08-14
GET /api/maids/me/tasks?date=2026-08-14
GET /api/inspections?status=pending
GET /api/weekly-pay?week=2026-W33
GET /api/audit-events?roomId=608&date=2026-08-14
```

## 명령 API 예시

```text
POST /api/rooms/{id}/commands/stop-operation
POST /api/rooms/{id}/commands/resume-operation
POST /api/rooms/{id}/commands/set-candles
POST /api/rooms/{id}/commands/confirm-candle-recovery
POST /api/reservations/{id}/commands/assign-room
POST /api/reservations/{id}/commands/transfer-room
POST /api/reservations/{id}/commands/release-room
POST /api/reservations/{id}/commands/check-in
POST /api/reservations/{id}/commands/check-out
POST /api/cleaning-tasks/{id}/commands/open-claim
POST /api/cleaning-tasks/{id}/commands/claim
POST /api/cleaning-tasks/{id}/commands/assign
POST /api/cleaning-tasks/{id}/commands/unassign
POST /api/cleaning-tasks/{id}/commands/start
POST /api/cleaning-tasks/{id}/commands/submit
POST /api/inspections/{id}/commands/approve
POST /api/inspections/{id}/commands/reject
POST /api/weekly-pay/{periodId}/maids/{maidId}/commands/mark-paid
POST /api/weekly-pay/{periodId}/maids/{maidId}/commands/revert-unpaid
POST /api/penalties/{id}/commands/void
POST /api/penalties/{id}/commands/restore
```

중요 명령 공통 필드:

```json
{
  "expectedVersion": 42,
  "reason": "관리자 입력 사유",
  "idempotencyKey": "uuid",
  "clientConfirmedAt": "2026-08-14T18:00:00+09:00"
}
```

## 고객 배정·입실 트랜잭션

1. 객실·예약 행 잠금 또는 expectedVersion 검증.
2. 운영 정상, 공실, 촛불 0, 차단 이슈 없음, 청소 승인 확인.
3. 활성 객실 배정 중복 확인.
4. 조건 불충족 시 409와 구체 코드 반환.
5. 배정·입실 이벤트와 감사 로그·알림 outbox를 같은 트랜잭션에 저장.

권장 오류 코드:

- `ROOM_OUT_OF_SERVICE`
- `ROOM_HAS_CANDLES`
- `ROOM_BLOCKING_ISSUE_OPEN`
- `ROOM_CLEANING_NOT_APPROVED`
- `ROOM_ALREADY_OCCUPIED`
- `RESERVATION_ROOM_CONFLICT`

## 촛불 수량 변경 트랜잭션

### 메이드 작업 제출

1. 청소 작업과 객실을 잠근다.
2. 현재 객실 촛불 수량을 `floor`로 읽는다.
3. `submitted_count >= floor`인지 검사한다.
4. 추가 수량과 작업 제출을 저장한다.
5. 수량이 양수면 고객 배정·입실 읽기 모델을 차단한다.
6. 감사 이벤트·관리자 알림을 저장한다.

메이드가 변조 요청으로 수량을 낮추면 422 `MAID_CANNOT_REDUCE_EXISTING_CANDLES`.

### 관리자 회수 확정

1. 객실 잠금·버전 확인.
2. 관리자 `can_manage_candles` 권한 확인.
3. 현재 수량, 변경 후 수량, 위치, 현장 확인 사유를 저장.
4. 감소 또는 0 전이는 `physically_verified=true` 필수.
5. 0이 되면 촛불 차단만 해제하고 전체 가용 조건을 재계산.
6. 기존 예약이 있다면 입실 잠금 해제 가능 여부를 다시 계산.

## 메이드 일감 claim

```sql
UPDATE cleaning_tasks
SET status = 'assigned', assignee_id = :maid_id, claim_open = false, version = version + 1
WHERE id = :task_id
  AND assignee_id IS NULL
  AND claim_open = true
  AND assignment_enabled = true
  AND status IN ('waiting','claimable')
  AND version = :expected_version
RETURNING *;
```

0행이면 이미 선택됐거나 상태가 바뀐 것이다.

## 운영 중지

- 예약·투숙이 있으면 409.
- 활성 담당이 있으면 중단 이력.
- 청소 작업 취소·제외.
- 공개 닫힘·배정 불가.
- 감사 이벤트와 outbox.

## 검수 승인

- 최신 제출 버전과 모든 필수 사진 업로드 확인.
- 승인과 주급 항목을 한 번만 생성.
- 객실 청소 상태는 준비 완료로 바꾸되 촛불·이슈·운영 상태는 변경하지 않는다.
- 전체 고객 가용성을 다시 계산한다.

## 사진·알림·보안

- 사전 서명 URL, 업로드 완료 검증, 썸네일, 오프라인 큐.
- 상태 변경과 알림 outbox를 같은 DB 트랜잭션에 저장.
- 접근 코드 평문 로그 금지, 조회 로그 필수.
- 메이드 API는 본인 담당만 반환.
- 사진 URL은 짧은 만료의 서명 URL.
- 모든 명령은 RBAC와 idempotency를 서버에서 검증.
