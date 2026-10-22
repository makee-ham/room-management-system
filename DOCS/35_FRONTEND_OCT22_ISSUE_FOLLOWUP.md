# 10월 22일 프런트 이슈 후속 연결

기준: `origin/dev`의 `29bafc9`. 관련 이슈: 프런트 [#206](https://github.com/makee-ham/room-management-system/issues/206), [#207](https://github.com/makee-ham/room-management-system/issues/207), [#219](https://github.com/makee-ham/room-management-system/issues/219), [#220](https://github.com/makee-ham/room-management-system/issues/220).

## 확인한 서버와 적용 경계

- 백엔드 최신 [사진 재시도 인계](https://github.com/makee-ham/room-management-system/issues/206#issuecomment-6330557032)는 main `ad1b1a0`, API51, migration120의 운영 반영을 보고한다. 서버 DB 적용을 프런트에서 재실행하지 않았다.
- 직접 읽기 확인: 운영 `/health` 200, `/openapi.json` 200, OpenAPI `0.6.0`, 154 paths / 166 operations. 로컬 origin의 CORS·publishable key 검증도 통과했다. 보호된 업무 mutation은 실행하지 않았다.
- 운영 OpenAPI 원문 SHA-256: `929c0fc8af53f839d4464d29e99b1088df6d159a52420d9aab5b8a73e48e871c`. `JSON.stringify({paths,components})` SHA-256: `916e561a8121d595a7e7b3ae23f8ab9a7c4a2fb9de70b9c98a56330587a09ccf`.
- 같은 날 게시 Swagger JSON은 151 paths / 163 operations로 응답했다. 캐시 무효화 query를 붙여도 같았다. 배포 API와 다른 문서를 최신 운영 계약으로 취급하지 않으며, 생성기는 고정 운영 API의 `/openapi.json`을 읽도록 변경했다. 검사 수를 완화하지 않고 정확한 154/166 및 필요한 schema·권한·멱등·다운로드 계약을 검증한다.
- `WIREFRAME/cleaning-api.d.ts`와 전체 `src/api/generated/room-management-api.ts`를 재생성했다. 전체 타입은 `openapi-typescript@7.13.0`을 사용했다. 전체 타입의 큰 diff에는 이전 snapshot 이후 제공된 다른 기존 API 갱신도 포함된다. 생성 파일은 수동 수정하지 않았다.

## 이슈별 변경과 남은 범위

| 이슈 | 이번 변경·확인 | 남은 범위 |
| --- | --- | --- |
| #206 사진 | `PHOTO_UPLOAD_IN_FLIGHT`를 처리 중으로, provider/quota 조회 503을 저장소 연결 문제로 안내. 파일·item·key·CAS·Blob을 보존하는 수동 재시도. 저장공간 초과·lease 한도·terminal은 반복 실행 차단 및 문의 번호 표시 | 실제 사용자 사진·첫 503 원인·모바일 성능 UAT |
| #207 조회 | 기존 가능일 일괄 조회, 송금 표시 batch, 첫 페이지 우선 표시, 늦은 응답·금액 검증 회귀 통과. 기존 구현을 중복 작성하지 않음 | 운영 네트워크/실기기 p50·p95 |
| #219 계획일 | 검증된 서버 계약을 사용하는 빌드·로컬 실행 설정을 기본 ON. 선택일 change body·availability, planningDate와 원 serviceDate 구분, 자정 stale write 보호 유지 | 실제 관리자/메이드·서버 자정 업무 UAT |
| #220 PIN | Excel 내보내기만 독립 활성화. 기존 내보내기 모달·CSV/xlsx/앱→Drive 목적 유지. 가져오기는 준비 사유와 함께 비활성. 현재 장기 예약의 4/6자리 직접 입력 활성 경로 유지. 다른 세대의 늦은 다운로드 응답이 새 세대의 중복 방지를 풀지 않음 | Drive 인증·물리 확인 경로 및 실제 업무 UAT |

사진은 자동 재전송하지 않는다. 재시도는 같은 요청으로 수동 확인하며 collection 쓰기는 앱 전체 1개씩이다. `accepted`와 유효 snapshot/최신 슬롯 확인 전에는 완료로 표시하지 않는다. 원본은 현재 문서 메모리에만 있고 로그아웃·앱 종료 뒤 재전송을 보장하지 않는다.

백엔드가 문서화한 `PHOTO_UPLOAD_IN_FLIGHT`, `PHOTO_PROVIDER_UNAVAILABLE`, `PHOTO_UPLOAD_LEASE_LIMIT`, `PHOTO_OPERATION_TERMINAL` 등 일부 코드가 배포 OpenAPI의 `ErrorCode` enum에는 없다. 프런트는 [#206 최신 인계](https://github.com/makee-ham/room-management-system/issues/206#issuecomment-6330557032)와 백엔드 `docs/PHOTO_UPLOAD_RETRY_464.md`의 고정 코드만 매핑하며, generated enum에 값을 임의 추가하지 않는다. 알 수 없는 코드는 기존 HTTP 안내를 유지한다.

## 설정과 롤백

| 설정 | 빌드·로컬 기본값 | 의미 |
| --- | --- | --- |
| `RMS_PHOTO_UPLOAD_SNAPSHOT` | `true` | 검증된 accepted snapshot 사용, null/불일치 시 GET 확인 |
| `RMS_ASSIGNMENT_PLANNING_DATE` | `true` | 배포된 계획일 계약 |
| `RMS_ROOM_PIN_EXPORT` | `true` | 관리자 전용 앱→Excel |
| `RMS_ROOM_PIN_TRANSFER` | `false` | Drive→앱 preview/apply 잠금 |

명시적 환경변수 → `.env.local` → 기본값 순서다. 이전 환경에 남은 `false` 값은 자동으로 덮어쓰지 않는다. 이전 서버 rollback 시 계획일·Excel을 각각 `false`로 빌드한다. `roomPinTransfer=true`는 기존 후보 설정과의 호환상 가져오기와 내보내기를 모두 허용하므로, 가져오기 준비 전에는 계속 false를 유지한다. `demo`는 운영 설정을 사용하지 않는다.

Drive 가져오기는 [백엔드 #463](https://github.com/wrongstory/room-management-system-backend/issues/463)의 인증·시트 접근 확인이 남아 있다. 또한 import 후 mismatch 객실에서 일반 reveal이 차단되지만 `ACTUAL_PIN_REENTRY` prepare는 `expectedPinVersion`이 필요하고 `RoomProjection`에는 해당 version이 없다. 추측값이나 0을 보내는 복구 경로를 만들지 않는다. 기존 앱→Drive 업데이트는 별도 기능이며 가져오기를 대체하지 않는다.

이번 작업은 소스·PR의 준비와 검증이다. 운영/Preview 배포, 운영 환경변수 변경, 실제 Excel/PIN/Drive 처리·예약/배정/사진 쓰기는 실행하지 않았다. 서비스 워커는 `2026-10-22-1`로 갱신했으며 강제 새로고침은 추가하지 않았다.

## 검증·재현

- `node scripts/check-workspace.mjs`
- `node scripts/check-pwa.mjs`
- `node scripts/check-photo-rollout.mjs` — production/preview/serve 설정 일치, 명시 rollback·환경 우선순위·demo 격리
- `node scripts/check-api-integration.mjs` — 공개 GET·CORS만 사용
- `node scripts/generate-cleaning-client.mjs --production --check`
- `node scripts/check-backend-handoff-oct13.mjs` — 실제 xlsx 파싱은 openpyxl 필요
- `RMS_QA_SKIP_BENCH=1 node scripts/check-photo-performance.mjs`
- `node scripts/check-photo-queue-handoff.mjs`
- `node scripts/check-cleaning-workflow.mjs`
- `node scripts/check-live-navigation.mjs`
- `node scripts/check-lazy-cleaning.mjs`
- `node scripts/check-data-performance.mjs`
- `node scripts/check-operational-api.mjs`

실행은 `python3 scripts/serve.py --port 4177`, 브라우저 회귀 origin은 `http://127.0.0.1:4177`이다. Browser plugin not available이므로 기존 번들 Playwright Chromium을 사용했다. Node 패키지 검색 경로와 `RMS_QA_PYTHON`은 사용 환경의 설치 경로를 지정하며 개인 컴퓨터 경로를 저장소에 고정하지 않는다. 실제 결과·화면 비교·한계는 `WIREFRAME/QA.md` 최신 절에 기록한다.
