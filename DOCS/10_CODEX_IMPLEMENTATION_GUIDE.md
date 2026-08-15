# 10. Codex 구현 가이드

## 권장 구조

- Frontend: React + TypeScript + Vite, 모바일 PWA
- Server state: TanStack Query
- Forms: React Hook Form + schema validation
- Backend: TypeScript 서버 프레임워크
- DB: PostgreSQL
- 사진: S3 호환 object storage
- Push: Web Push/FCM 계열
- Tests: unit + DB integration + API + Playwright E2E

## 프런트엔드 모듈

```text
src/
  app/ auth/
  rooms/
    operations/ guest-allocation/ reservation-conflicts/
    issues/ candles/ access-codes/ schedules/
  cleaning/
    market/ assignments/ task-detail/ photos/ inspections/
  workforce/
    maids/ weekly-pay/ penalties/
  history/ notifications/ shared/
```

## 도메인 서비스

```text
RoomOperationService
RoomAvailabilityPolicy
ReservationAssignmentService
RoomCandleService
CleaningTaskService
CleaningAssignmentService
InspectionService
WeeklyPayService
PenaltyService
AuditService
NotificationService
```

React 컴포넌트에서 여러 필드를 직접 바꾸지 말고 도메인 명령을 호출한다.

## 구현 단계

### 0. 규칙·데이터 확정

- 상태 enum과 상태 전이 표
- 객실·청소비·체크리스트
- 촛불 회수 권한·증빙 정책
- 주급·벌점 운영 규정

### 1. 인증·읽기 전용 객실 운영판

- DB·마이그레이션
- RBAC
- 일자별 읽기 모델
- 네 운영 목록·필터
- 608 불변식과 촛불 하드 차단 테스트

### 2. 객실 운영·예약·촛불

- 운영 중지·재개
- 예약 배정·이동·해제·입실·퇴실
- 차단 특이사항
- 얼리·레이트
- 촛불 배치·관리자 회수·예약 충돌
- 접근 코드

### 3. 청소 배정

- 작업 생성
- 오픈·클로즈
- 원자적 claim
- 관리자 배정·변경·미배정
- 중단 이력

### 4. 메이드 현장 PWA

- 담당 작업과 비밀번호 권한
- 체크리스트·오프라인 사진 큐
- 촛불 추가 수량만 기록, 기존 수량 하한 검증
- 완료 제출

### 5. 검수·알림

- 사진별 검수
- 승인·반려
- 재청소 알림
- 승인 후 전체 가용성 재계산

### 6. 주급·벌점·계정

- 주차별 정산·지급·취소
- 벌점 소프트 삭제·복구
- 메이드 소프트 삭제

### 7. 외부 연동

- CSV
- PMS/OTA
- 도어락

## 첫 구현 순서

1. 문서의 상태 규칙을 TypeScript 순수 함수로 옮긴다.
2. `08_ACCEPTANCE_CRITERIA.md`를 테스트로 먼저 만든다.
3. PostgreSQL 제약과 트랜잭션 테스트를 작성한다.
4. 608, 촛불 배치·회수, 예약 충돌, 일감 claim, 검수 승인부터 구현한다.
5. 프로토타입의 390px UI를 기준으로 화면을 재구성한다.
6. 360/390/430px와 키보드·스크린리더를 검수한다.

## 금지할 구현

- 색상이나 단일 `room_status`를 진실 원본으로 저장
- UI에서만 버튼을 숨기고 API는 허용
- 촛불 양수 객실을 서버에서 배정·입실 허용
- 메이드가 기존 촛불 수량을 낮추는 요청 허용
- 검수 승인 시 촛불을 자동 회수 처리
- 운영 중지 객실에 예약·청소를 만들고 화면에서만 숨김
- 표시 이름을 foreign key로 사용
- 과거 이력을 UPDATE로 덮어쓰기
- 벌점 자동 임금 차감
- 업로드 완료 전 검수 요청
