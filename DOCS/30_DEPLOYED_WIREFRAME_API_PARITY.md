# 배포 UI 정합성과 백엔드 협의

기준일: 2026-09-29. 사용자 요청은 로컬 데모가 아니라 Production과 Preview에 적용한다. 화면 정본은 `WIREFRAME/index.html`의 기존 와이어프레임이며 최종 감사 원문은 수정하지 않았다. 프런트 컨펌 전이므로 이 문서는 백엔드 이슈 게시용 초안이다.

## 확인 기준

- 운영 OpenAPI: `https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api/openapi.json`, 재조회 결과 **0.6.0**.
- 최초 대조 main: `5303fd505f18ed45fe9945d35239ccef25df2b13`. OpenAPI뿐 아니라 실제 Edge route, payroll/room issue/PIN 처리와 DB 명령도 대조했다.
- 최종 재확인 main: `1780728a02144c0816565ba091e43a8b3e126c4f`, dev: `e19f81fabe1ff202b5a42ba37b9d5dccbf8215c2`. PIN 설정 수정 #316은 release [PR #319](https://github.com/wrongstory/room-management-system-backend/pull/319)로 운영 v0.7.1에 배포됐다. PR에 2026-09-29 07:16 KST 관리자 PIN 조회 smoke 성공이 기록돼 있다. main diff는 PIN 구현/테스트/릴리스 문서이며 아래 지급·메이드 권한·객실 목록 규약은 변하지 않았다.
- 보호 API의 실제 데이터 변경은 하지 않았다. 아래 브라우저 쓰기 검증은 합성 데이터로 모든 요청을 가로챈 테스트다.

## 요청별 결과

| 요청 | 프런트 반영 | 남은 사항 |
| --- | --- | --- |
| 청소 배정을 와이어프레임과 동일하게 | 목차, 요약, 접는 근무표, 랜덤 배정, 타입 필터와 5열 담당 표, 메이드별 요약, 저장·통보, 이력의 공통 렌더러를 데모/운영이 공유. 담당 선택은 저장·통보 전까지 로컬 초안 | API 미제공 항목은 기존 자리에 표시. 미배정 종류/이월/취소 정보는 B04 |
| 청소 순서/더보기 템플릿 제거 | 두 UI 모두 제거 유지. API가 요구하는 `sequenceNumber`만 adapter 내부에서 생성 | 서버 필수 필드가 사라지기 전까지 호환값 유지 |
| 홈 배정 위치와 정확한 이동 | 검수 아래 배정. 검수 버튼은 검수 탭, 배정 버튼은 선택일 다음 날짜의 배정 탭으로 이동 | 없음 |
| 홈·객실 날짜 변경 | 이전/다음/달력/오늘 활성화. KST 날짜의 예약 범위 조회, 다음 날짜 배정 조회, URL/Back/Forward 유지. 청소 탭 변경 때 선택 날짜 유지 | 과거 점유·청소·촛불 상태와 과거 시점 검수 대기/주급 재구성은 B05 |
| 객실 운영 상태 → 이슈 팝업 | 기존 팝업을 운영 상태의 주요 버튼으로 연결. 분류·심각도·배정 차단·설명과 version/idempotency 요청 검증 | 실제 업무 데이터에 이슈를 만들지는 않음 |
| 객실 상세 조건 7개 | 상태 조건 아래 요청한 7개를 추가. 추가 인원/공실/촛불/특이사항/얼리/레이트를 실제 예약·객실·타입·이슈 데이터로 필터 | 퇴실점검 대상 판별은 B06 |
| 메이드 본인 완료 내역에서 촛불/새 특이사항 | 본인 제출 상세에 현재 객실 상태 변경 위치를 유지 | **운영 저장 미완료**. 현재 규약에서는 메이드에게 허용되지 않아 비활성. B01 |
| 송금 여부 토글만 저장 | 참조번호 입력 팝업 제거. 조회된 송금 여부는 스위치로 표시 | **운영 토글 저장 미완료**. 임의 은행 참조번호를 만들지 않고 비활성. B02 |
| 비밀번호 저장·조회 | 객실 PIN의 prepare → 물리 변경 확인 → confirm → reveal 경로 기존 연결 확인. 최초 PIN version 0 처리와 30초/단일 객실 노출 회귀 통과 | 실제 도어락/PIN 변경은 미실행. 백엔드 조회 복구 배포 기록은 B03. 계정 로그인 비밀번호는 별도 POST `/v1/auth/password`이며 원문 조회 API가 아님 |
| 사진/검수/주급 조회 | 일반 사진 1~20장, 갤러리 다중 선택 후 남은 수량 내 추가, 증빙 별도, 확대, 7일 이력, 본인 주급/관리자 주급 조회 회귀 통과 | 실제 휴대폰 갤러리·운영 업로드/승인/지급 기록 UAT는 미실행 |

## 백엔드에 전달할 항목

### B01 · 제출 후 메이드의 객실 상태 변경

현재 `POST /v1/rooms/{roomId}/candles`는 `x-required-roles: admin`이다. `expectedRoomVersion`, `reasonCode`, `count`가 필수이며 `physicallyVerified`는 선택이다. 메이드의 현재 촛불 수량과 객실 version 조회도 필요하다.

`POST /v1/attempts/{attemptId}/room-issues`는 제출 전 담당 메이드만 허용하고 `memo`와 `evidencePhotoIds` 1~10개를 요구한다. DB는 제출 후 상태를 `ROOM_ISSUE_REPORT_ACCESS_REQUIRED` 또는 `INVALID_ROOM_ISSUE_REPORT`로 거부하며 증빙 업로드에도 상태 제한이 있다.

필요 동작: 메이드가 최근 본인 청소 내역을 열어 검수 대기/승인 후에도 촛불을 추가·회수하고 새 특이사항을 별도 기록한다. 제출 당시 촛불 스냅샷, 청소 사진, 기존 검수 결과, 주급은 바뀌지 않아야 한다. 조회/쓰기/증빙 추가 경로와 CAS를 제공하고 다른 메이드 접근은 차단한다. 담당 종료·재배정·새 고객 입실 후 허용 범위는 서버 권한 규약으로 명시해 달라.

수용 검사: 제출 → 촛불 변경 → 새 이슈 → 검수 승인 후 재변경 → 재조회; 과거 제출본/주급 불변; 다른 메이드 403; 충돌 409 후 최신 수량; 실패/중복 클릭/응답 유실 처리.

### B02 · 송금 표시 전용 on/off 저장

현재 `/v1/payroll/start` 이후 `/v1/payroll/payment-attempts/{attemptId}/paid`는 `expectedVersion`, `paymentMethod: bank_transfer`, **`providerReferenceId` 필수**다. 이 요청은 실제 외부 전액 송금의 확인 기록이며 결과는 immutable이다. `/reopen`은 PAYING/CHECK만 허용하므로 PAID를 끄는 용도로 쓸 수 없다.

필요 동작: 별도 확인창·코드 없이 관리자 스위치 한 번으로 송금 표시를 저장/해제. 금액 계산 및 원장은 그대로 두고 표시 변경자·시각을 기록한다. 주차/메이드(또는 cycleId), boolean 상태, expectedVersion, Idempotency-Key를 받는 경로 또는 현재 규약의 명시적 개정을 제공해 달라. 가짜 `providerReferenceId`를 생성해 기존 전액 송금 기록으로 보내지는 않는다.

수용 검사: 새로고침과 다른 관리자 세션에서도 동일한 상태; on/off 모두 저장; 409 재조회; 동일 요청 재시도; 다른 메이드·주차 영향 없음; 토글로 금액/실제 송금이 발생하지 않음.

### B03 · 객실 PIN 저장 경로와 조회 장애

API는 이미 있다: `/v1/rooms/{roomId}/pin-changes/prepare`, `/pin-changes/{leaseId}/confirm`, `/pin/reveal`. 새 값을 prepare하는 것만으로 확정되지 않고, 실제 도어락 변경을 확인한 confirm 성공 뒤 새 revision을 조회하는 구조다. 프런트에서 원문을 웹 저장소·URL·로그에 남기지 않는다.

[이슈 #315](https://github.com/wrongstory/room-management-system-backend/issues/315)의 hosted PIN 조회 503 관련 설정 수정은 [PR #316](https://github.com/wrongstory/room-management-system-backend/pull/316)에 있다. 작업 중 후속 [릴리스 #319](https://github.com/wrongstory/room-management-system-backend/pull/319)가 main에 병합/운영 배포됐고 기존 PIN 조회 및 자동 마스킹 smoke 성공이 보고됐다. 실제 PIN 값·키·계정 비밀번호를 이슈에 적지 않는다. 실제 도어락 변경 테스트는 여전히 미실행이며 현장 확인 가능한 별도 대상이 필요하다.

프런트 최종 배포에서도 관리자 기존 객실 PIN 조회 성공과 즉시 숨김을 직접 확인했다. 원문을 출력하거나 실제 PIN을 바꾸지 않았다. 따라서 현재 남은 항목은 조회 장애가 아니라 현장과 함께 하는 실제 변경·저장 UAT다.

### B04 · 배정 화면의 미배정 대상/취소 정보

`AssignmentCard`에는 이미 `cleaningKind`, `feeSnapshot`, `rolloverCount`, 타입·위치가 있다. 해당 값은 그대로 사용한다. 반면 `AssignmentCommitUnassignedTarget`에는 `cleaningTargetId`, 객실, 서비스일, assignment version, 시작/마감만 있고 종류·단가 스냅샷·이월 근거가 없다. `AssignmentPreviewRow`는 단가를 제공하지만 종류·이월 근거는 없다.

프런트가 놓쳤던 타입 카탈로그 로딩을 추가해 현재 타입/위치와 기본 청소요금을 표시했다. 확정 배정의 `feeSnapshot`은 우선 사용한다. 미배정 target에도 종류/단가 스냅샷/이월 정보를 제공해 달라. 자동·수동 등록 근거는 종류만 보고 추측하지 않는다.

와이어프레임의 `청소대상 취소`/`청소 취소·통보`는 `담당 해제`와 다르다. 수동 요청 취소는 `/v1/reservations/cleaning-requests/{targetId}/cancel`에 있지만 현재 배정 projection에는 수동 요청 여부와 해당 target version이 없다. 취소 가능 여부·원인·CAS와 자동 생성 target 취소 규약을 제공해 달라. 프런트는 담당 해제 명령으로 대체하지 않고 원래 버튼 위치에서 비활성 표시한다.

메이드 배정에는 현재 업무에 연결된 얼리/레이트의 정확한 예약 시각도 필요하다. 관리자는 예약 API로 실제 해당 날짜의 시각 배지를 표시하지만 메이드에게 관리자 예약 API 권한을 우회하지 않는다.

### B05 · 날짜별 운영 상태

날짜 UI가 막혀 있던 것은 프런트 문제였으며 해제했다. `/v1/reservations?from=...&to=...`의 KST 하루 범위와 pagination, `/v1/assignments?serviceDate=...`를 연결했다.

그러나 `/v1/rooms`에는 `date`/`asOf` 인자가 없다. 과거/미래 날짜에서는 받은 예약의 객실·일정을 표시하고 당시 점유/청소/PIN/촛불/배정 가능 여부를 현재 상태로 꾸미지 않는다. 과거 입실 중 객실 이동은 목록의 roomId만으로 전체 stay segment를 복원할 수 없어, 정확한 해당 날짜 객실 projection이 필요하다. 홈의 검수 대기와 주급은 현재 조회이며 과거 날짜의 대기열/원장을 재구성한 값이 아니다.

필요한 계약: 날짜별 객실 상태 projection 또는 해당 날짜의 예약/투숙 segment, 퇴실점검/청소/촛불 상태와 평가 시각. 현재 상태 변경 명령과 과거 조회를 구분한다.

### B06 · 퇴실점검 대상

요청한 필터 자리는 구현했지만 `RoomProjection`에 퇴실점검 완료/대상 상태가 없다. 청소 필요와 퇴실점검 미완료는 동일하지 않으므로 `퇴실점검 완료 여부 API 미제공`으로 표시한다. 대상 boolean 또는 상태/이유/검사 기록과 처리 명령을 제공해 달라.

### B07 · 객실 목록의 pagination 쿼리를 Edge route가 거부

실제 관리자 세션의 읽기 전용 확인에서 `/v1/rooms/{roomId}/issues?limit=100`와 `/operation-blocks?limit=100`가 400 `VALIDATION_ERROR`를 반환했다. 오류 내용은 각각 `status는 open만 사용할 수 있습니다.`와 `status는 actionable만 사용할 수 있습니다.`였다. status를 명시해도 실패했다.

원인은 백엔드 `supabase/functions/api/index.ts`의 두 GET route가 `params.keys()`에서 `status` 이외 키를 전부 거부하는 것이다(main 기준 1575~1576, 1603~1604). OpenAPI와 `_shared/room-api.ts`는 limit 1~100과 cursor를 지원하지만 route guard가 먼저 막는다. status 기본값 오류로 오인하지 않도록 오류 문구도 수정해야 한다.

프런트는 명시적인 limit을 빼고 `status=open`/`status=actionable`과 서버 기본 page 크기를 사용한다. nextCursor가 있으면 기존 pagination을 시도하고 실패를 전체 조회 성공으로 숨기지 않는다. 백엔드는 route allowlist에 limit/cursor를 추가하고 실제 hosted 다중 페이지 회귀를 넣어 달라. 운영 문의 번호: status 명시 후 issues `cdc16031-5c59-4f1c-839a-cc7e586271b6`, blocks `91960749-f0e0-447e-83a9-9c2c6fa50972`. 원문 PIN/사진/고객 데이터 없이 오류 식별자만 기록했다.

최종 Production에서 기본 크기 조회로 운영 상태 팝업이 오류 없이 열리고 이슈 등록 팝업까지 진입하는 것을 직접 확인했다. 현재 객실의 단일 페이지 조회 복구와 50개 초과 pagination 계약 수정은 구분한다.

## 한 번에 확인할 내용

위 B01/B02가 이미 구현됐다는 설명과 현재 공개 OpenAPI/Edge 코드가 다르다. 이미 가능한 기능이라면 **실제 운영 배포 commit, endpoint, 요청/응답 예시, 권한/허용 상태**를 한 번에 공유해 달라. 새 정책을 프런트에서 추측하거나 저장 성공을 가장하지 않고 그 계약에 맞춰 연결한다. B03은 코드 병합이 아니라 운영 복구 여부, B04~B06은 기존 endpoint의 추가 필드로 해결 가능한지 함께 확인한다.

검증 기록과 대표 합성 데이터 PNG는 `WIREFRAME/QA.md`의 2026-09-29 배포 정합성 절에 있다. 인증된 운영 업무 변경 및 실제 모바일 OS 사진 선택창은 별도 UAT 범위다.
