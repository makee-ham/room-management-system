# 최신 API 연결과 백엔드 인계

기준일: 2026-10-08 KST. Production/Preview용 프런트 변경이다. 정책 정본을 재작성하지 않고 기존 와이어프레임에 adapter로 연결한다. 문서 28~30의 과거 API 부족 목록은 이 문서의 최신 상태와 구분한다. 프런트 컨펌 전이므로 백엔드 GitHub 이슈는 아직 게시하지 않았다.

## 확인한 백엔드

- 저장소 `wrongstory/room-management-system-backend`, main `d9e053b01deea4e3d68facdd190dc41d32978538`, [v0.9.0 릴리스 PR #403](https://github.com/wrongstory/room-management-system-backend/pull/403).
- [릴리스 #387](https://github.com/wrongstory/room-management-system-backend/issues/387)의 실제 배포 기록: 111 migrations, API v41, reservation-scheduler v18. 소스 문서의 과거 `source-registered-not-deployed` 표시는 최신 배포 증거와 구분했다.
- 운영 `/health`, `/openapi.json` 읽기 확인. 공개 문서 version은 여전히 0.6.0이지만 현재 150 paths / 162 operations다. 생성 타입도 이 계약으로 갱신했다.
- 실제 운영 업무 쓰기는 하지 않았다. 아래 기능 회귀의 저장/충돌/재시도는 모든 요청을 가로챈 합성 데이터 검증이다.

## 이번 연결

| 사용자 동선 | 최신 API와 프런트 연결 | 상태 |
| --- | --- | --- |
| 홈·객실 날짜 변경 | `GET /v1/rooms?serviceDate=YYYY-MM-DD`, `projectionMode`, `primaryDisplayStatus`, `detailConditionCodes`, 표시 예약 projection. 현재/과거 일마감/미래 시작 기준 분리. 과거 화면 변경 버튼 잠금, URL/Back 유지 | 계약·브라우저 회귀 통과 |
| 객실 상세 조건 7개 | 퇴실점검·인원 추가·공실·촛불·특이사항·얼리·레이트를 서버 code로 판정 | 회귀 통과. 퇴실점검 완료 쓰기는 별도 미제공 |
| 청소 배정 | 원래 목차·6개 섹션·5열·메이드별 요약 유지. `roomTypeSnapshot`, `feeSnapshot`(0원 포함), `sourceKind`, `scheduleSnapshot`, `currentDeparture`, `canCancel`, `targetAssignmentVersion` 사용 | 회귀 통과. 청소 순서 UI와 템플릿 메뉴 없음 |
| 메이드 본인 청소 내역 → 촛불 변경/회수 | `GET /v1/rooms/candles?roomId=...` → `POST /v1/rooms/{roomId}/candles`; 현재 version, `CANDLE_ADJUSTED`, 감소 시 현장 회수 확인 | 회귀 통과. 제출 당시 촛불·검수·수익 불변 |
| 제출 후 새 특이사항 | `GET/POST /v1/cleaning-history/submissions/{id}/supplemental-room-issues`, draft 생성/복구, 전용 raw evidence 업로드, 최종 확정, content 확대, 관리자 close | 회귀 통과. 신규 증빙 1~10장은 이 API의 별도 한도 |
| 주급 → 송금 스위치 | `GET/PUT /v1/payroll/remittance-marker`, `marked`, `expectedVersion`, `expectedBasisFingerprint`, Idempotency-Key. 팝업/은행 참조번호/실제 송금 API 없이 on/off. 금액 근거 변경 시 별도 재확인 | **프런트 회귀 통과 / 운영 PUT CORS 차단** |
| 주급 → 객실별 산출 | `GET /v1/payroll/work-details` earnings/workflow 전체 페이지. 기본·폭탄방·합계와 미확정 업무. 페이지 간 summary 변경 시 중단 | 회귀 통과 |
| 주급 → 금액 정정/취소 | `GET /v1/payroll/adjustment-book`의 최신 `currentBookVersion`으로 기존 append-only 명령 | 회귀 통과. 0 추정 제거 |
| 객실 운영 상태 → 메이드 신고 | `GET /v1/rooms/{roomId}/reports?limit=10` 전체 페이지, 제출 전 폭탄방/특이사항 메모·상태·사진. 보관 만료와 조회 불가 분리 | 회귀 통과 |
| 청소 → 진행 중 → 미퇴실 신고 | `GET /v1/checkout-incidents` 전체 페이지 → 기존 단건 상세 → 최신 version/impactFingerprint 확인 팝업과 기존 결정 명령 | 목록/상세/CAS 진입 회귀 통과. 실제 사건 결정 UAT 별도 |
| PIN·청소 제출·검수·사진 이력 | 기존 PIN prepare/물리 확인/confirm/reveal, 일반 사진 1~20장 다중 선택, 폭탄방 별도 판정, 7일 이력·확대 유지 | 기존 흐름 회귀 통과. 실제 도어락 변경/Drive 삭제는 미실행 |

일반 사진의 1~20장과 추가 특이사항의 1~10장은 서로 다른 계약이다. 사진 원문은 메모리에만 두며 브라우저 저장소/URL/history에 넣지 않는다. 추가 특이사항 업로드 응답이 유실되면 draft를 다시 읽어 이미 수락된 사진을 확인하고 중복 제출을 피한다. 등록 중 다른 화면으로 이동해도 팝업을 강제로 다시 열지 않는다.

송금 표시는 기존 `cycle.status=paid`와 독립이다. 기존 지급 원장만 보고 송금 스위치를 켜지 않으며, 스위치를 꺼도 지급 원장을 취소하거나 실제 돈을 이체하지 않는다.

## 백엔드 수정 요청

### P1. 운영 CORS에 PUT 허용 누락

대상: `PUT /v1/payroll/remittance-marker`. Production origin의 실제 preflight는 204지만 다음 헤더를 반환한다.

```text
Access-Control-Allow-Methods: GET,POST,PATCH,DELETE,OPTIONS
```

PUT이 없으므로 브라우저는 저장 요청을 보내지 못한다. 이는 송금 표시 endpoint 자체가 없다는 뜻이 아니다. 최신 소스 `supabase/functions/_shared/runtime.ts`의 CORS 헤더도 같은 값이다.

읽기 전용 재현:

```bash
curl -i -X OPTIONS \
  'https://aodikrxcczbogjpsjwjt.supabase.co/functions/v1/api/v1/payroll/remittance-marker' \
  -H 'Origin: https://room-management-system-prod.vercel.app' \
  -H 'Access-Control-Request-Method: PUT' \
  -H 'Access-Control-Request-Headers: authorization,content-type,idempotency-key'
```

요청: 공통 허용 메서드에 PUT 추가, Edge 재배포, Production 및 허용된 Preview origin에서 실제 브라우저 preflight 회귀. Authorization/Content-Type/Idempotency-Key와 증빙용 If-Draft-Revision/If-Evidence-Revision/If-Item-Revision 허용도 유지한다. 프런트는 응답 실패를 저장 성공으로 바꾸지 않는다. 수정 뒤 지정 테스트 계정에서 on→새로고침→off→다른 관리자 조회 UAT가 필요하다.

### 계약 문서 정합성

- 공개 OpenAPI 신규 endpoint의 `x-implementation-status: source-registered-not-deployed`는 v0.9.0 실제 운영 배포 상태와 다르다. 릴리스별 상태를 맞춰 달라.
- `AttemptPhotoSlots.slots[].maxPhotos`와 photos 배열은 20장을 허용하지만 같은 스키마의 `photoCount.maximum`은 10이다. 20장 응답의 생성 client 검증이 실패하지 않도록 일치가 필요하다. 프런트는 실제 사진 배열과 해당 slot의 maxPhotos로 1~20장을 제한한다.

## 아직 완료로 보고하지 않는 범위

| 항목 | 현 상태 / 다음 작업 |
| --- | --- |
| 제한 계정 재진입(문서 28 B04) | 신규 `GET /v1/limited/attempts`와 기존 세션 정책은 확인했다. **현재 프런트 부팅은 여전히 active-only이며 이 특수 흐름은 미연결**이다. 일반 계정을 active로 위장하지 않는다. 보존된 기존 세션 전용 부팅, 만료/철회/refresh, finish_current·upload_submit·evidence_upload별 동작/권한을 별도 구현·검증해야 한다. 단건/사진 슬롯 응답에 submission pointer revision이 없고 제한 계정은 일반 submissions GET을 사용할 수 없으므로 cold-start 제출 CAS 조회 방법도 확인 필요하다 |
| 추가 증빙 관리자 인계/복구 | 정상 draft·수락 사진 복구·완료 이슈 조회/종결은 연결했다. 다른 관리자의 provider 업로드 operation 인계(`.../handover`)와 장기 reconciliation/compensation 운영 화면은 미연결이다. 완료 이슈를 원 제출과 합쳐 처리하지 않는다 |
| 실제 운영 UAT | 테스트 메이드/객실/주차가 지정된 후 실제 사진 업로드→완료→제출→검수→주급→촛불/추가 신고→이력 재조회가 필요하다. 실기기 갤러리·PWA OS Back·Drive purge·도어락 물리 변경은 합성 브라우저 테스트로 대체하지 않았다 |
| 과거 홈 검수/주급 | 날짜별 객실판과 다음날 배정은 선택일 기준이다. 검수 대기열은 현재, 비용은 표시된 주차의 현재 원장이다. 과거 시점 검수 대기열/주급을 재구성했다고 주장하지 않는다 |

## 확인 순서

1. 배포/Preview에서 원래 와이어프레임 청소 배정·날짜·객실 필터·운영 이슈 팝업을 확인한다.
2. 백엔드가 PUT CORS를 먼저 수정한다. 일반 HTTP smoke와 브라우저 송금 저장을 구분한다.
3. 지정 테스트 데이터로 메이드와 관리자 양쪽 운영 UAT를 수행한다. 원 제출/원장 불변과 재조회 결과까지 확인한다.
4. 제한 계정과 업로드 관리자 인계는 미완료 범위로 별도 확인한다. ‘프런트 전체가 더 할 일이 없음’으로 넘기지 않는다.
5. 프런트 컨펌 뒤 위 항목 중 합의된 것만 백엔드 이슈로 등록한다.

실행 증거와 실패/보완 이력은 [QA](../WIREFRAME/QA.md)의 2026-10-08 절에 기록한다. 배포 URL과 최종 확인 결과는 같은 절을 따른다.

## 메이드 사진·계정 후속 협의 (2026-10-08)

사용자가 지정한 프런트 기준은 `dev`이며 백엔드 main 기준과 별개다. 이번 후속도 프런트 컨펌 전 이슈를 게시하지 않았다.

| 항목 | 이번 프런트 처리 | 백엔드 협의 사항 |
| --- | --- | --- |
| 계정 관리 개발자 전용 | 관리자 더보기/메이드 상세에서 관리 메뉴·변경 액션 제거, 직접 액션/구 history 차단. 개발자 화면 유지 | UI 제한만으로 서버 권한이 줄지는 않는다. 계정 생성·역할·상태·잠금 해제·비밀번호 초기화 명령도 developer-only가 제품 정책이면 서버 권한을 동일하게 제한해야 한다. 업무 관리자의 메이드 목록/배정용 조회는 계속 필요하다 |
| 제출 촛불/현재 수량 | `GET /v1/rooms/candles?roomId=...` → 필요한 경우 `POST /v1/rooms/{roomId}/candles` (`count`, `expectedRoomVersion`, `CANDLE_ADJUSTED`, 감소 시 `physicallyVerified:true`) → `POST /v1/attempts/{attemptId}/submissions`. 입력 초안 유지, CAS 실패 시 제출 중단 | `create_cleaning_submission`은 candle snapshot만 저장하고 공유 candle ledger를 갱신하지 않는다. 현재 두 명령 사이에는 원자성이 없다. 제출 API에서 room version/회수 확인을 함께 받아 한 트랜잭션으로 저장하는 계약을 권장한다. 앞 명령만 성공한 경우 현재 촛불은 저장되고 제출은 미완료일 수 있다. 과거 제출 열기만으로 현재 수량을 덮으면 안 된다 |
| 사진 처리 속도 | 정상 20장 배치의 중복 슬롯 GET 40→21, 재인코딩된 업로드 사진 재다운로드 제거, 상세 먼저 표시·최대 4개 사진 읽기·개별 재시도 | 브라우저에서 제거 가능한 중복을 줄였다. 서버 저장/Drive 조회 지연은 별도다. 사진 원문/토큰 없이 endpoint별 서버 처리 시간과 provider 시간 분리 계측이 필요하다. thumbnail 또는 batch metadata 계약은 현재 있다고 가정하지 않았다 |

검증은 로컬 합성 쓰기와 운영 읽기 전용이다. 기존 현재 수량이 이미 제출값과 다르면, 이후 회수/추가 여부를 서버 응답으로 구분할 근거가 없으므로 자동 과거 보정을 하지 않는다.
