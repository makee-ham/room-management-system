# 6. 권장 데이터 모델

관계형 DB와 이벤트·읽기 모델 조합을 권장한다. 표시 이름이나 색상 대신 불변 ID와 원본 상태를 저장한다.

## 사용자·권한

### `users`

- `id` UUID PK
- `login_id` unique
- `display_name`
- `role` (`admin`, `maid`)
- `employment_status` (`active`, `inactive`, `retired`)
- `login_enabled`
- `created_at`, `updated_at`, `retired_at`

### `admin_permissions`

- 객실 운영, 고객 배정, 검수, 촛불 회수, 정산, 벌점, 계정, 비밀번호 이력 권한

### `maid_profiles`

- 전화번호, 입사일, 메모
- 과거 작업과 연결되는 불변 `user_id`

## 객실·운영

### `rooms`

- `id`, `room_number`, `room_type_id`
- `operation_status`
- `operation_reason`
- `current_candle_count` 캐시 컬럼
- `version` optimistic lock

### `room_operation_events`

- 전후 상태, 사유, actor, 시각

### `room_issues`

- 카테고리, 설명, 심각도
- `blocks_guest_assignment`
- 상태, 등록·해결자와 시각

### `room_candle_events`

- `id`, `room_id`
- `action` (`maid_added`, `admin_set`, `admin_adjusted`, `admin_recovered`)
- `count_before`, `count_after`
- `added_count`
- `location_note`
- `reason`
- `source` (`cleaning_task`, `admin_room_check`)
- `cleaning_task_id` nullable
- `actor_id`
- `physically_verified` boolean
- `created_at`
- `room_version_before`, `room_version_after`

제약:

- `count_after >= 0`
- 메이드 명령은 `count_after >= count_before`
- 양수에서 감소 또는 0으로의 전이는 촛불 회수 권한이 있는 관리자만 가능
- `current_candle_count > 0`이면 고객 배정·입실 읽기 모델은 차단

### `room_access_codes`, `access_code_view_logs`

- 암호화 코드, 유효 기간, 생성·폐기자
- 조회자, 작업 ID, 시각

## 예약·투숙

### `reservations`

- 외부 채널·예약 ID
- 기본 체크인 16:00, 체크아웃 11:00
- 실제 체크인·체크아웃
- 얼리·레이트 시각
- 상태

### `reservation_room_assignments`

- 예약, 객실, 상태
- 배정·이동·해제·체크인·체크아웃 이력
- 한 예약에 활성 객실 배정 최대 1개

## 청소·검수

### `cleaning_tasks`

- 객실, 서비스 일자, 유형
- 상태
- 가능·마감 시각
- 가격 스냅샷
- 공개·배정 가능 여부
- `version`

### `cleaning_task_assignments`

- 작업, 메이드, 출처(`admin`, `maid_claim`)
- 활성·종료·중단
- 전후 담당과 사유
- 작업당 활성 담당 최대 1명

### `cleaning_submissions`

- 제출 버전
- 체크리스트 스냅샷
- 메모
- `candle_count_before`
- `maid_added_candle_count`
- `candle_count_after`
- 제출자·시각

서버는 `candle_count_after >= candle_count_before`를 검증한다. 관리자가 청소 도중 회수해 객실 버전이 바뀌었으면 제출을 재검토하게 한다.

### `cleaning_photos`

- 카테고리, 원본·썸네일 URL
- 촬영·업로드 시각
- 업로드 상태
- 제출 버전

### `inspections`, `inspection_photo_reviews`

- 승인·반려
- 검사자, 사유, 사진별 결과
- 검수 승인은 촛불 상태를 바꾸지 않는다.

## 주급·벌점

- `weekly_pay_periods`
- `weekly_pay_items`
- `weekly_payment_events` (`marked_paid`, `reverted_unpaid`)
- `penalties` (`active`, `void`)와 부여·삭제·복구 사유

## 이력·알림·읽기 모델

### `audit_events`

- aggregate, event type
- before/after JSON
- actor, reason
- request ID, idempotency key, 시각

### `room_daily_snapshots` 또는 `room_operation_read_models`

특정 날짜의 객실 운영판을 빠르게 조회하는 재생성 가능한 읽기 모델이다. 원본 진실은 예약·작업·이벤트 테이블이다.

### `notifications`, `notification_outbox`

- 수신자, 유형, payload, 읽음, 푸시 상태, 재시도

## 핵심 DB 제약

- 운영 중지 객실에 활성 예약 배정·활성 청소 작업 금지
- 촛불 양수 객실에 신규 예약 객실 배정·체크인 명령 금지
- 한 작업에 활성 담당 최대 1명
- 한 예약에 활성 객실 배정 최대 1개
- 검수 승인·주급 항목은 동일 제출 버전에 한 번만
- 메이드 퇴사는 물리 삭제 금지
- 과거 정정은 원본 UPDATE 금지
