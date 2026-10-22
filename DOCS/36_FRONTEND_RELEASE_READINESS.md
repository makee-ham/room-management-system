# 10월 22일 프런트 릴리스 준비

기준: dev `10c46b9` (PR #222) 이후. 사용자 요청: 열린 프런트 이슈 처리 → 관련 PR 병합 → 보호된 Preview 검증 → main PR 병합. 실제 사진 업로드/재시도 UAT는 [백엔드 최신 인계](https://github.com/makee-ham/room-management-system/issues/206#issuecomment-6331210551)에 따라 사용자가 진행한다.

## 이슈 판정

| 이슈 | 프런트 처리 | 남은 항목 |
| --- | --- | --- |
| #168 | 취소·체크아웃 완료 예약은 읽기 전용 상세. 편집용 bookability·객실 변경·저장 호출 없음 | 실제 운영 데이터 변경 없이 fixture 검증 |
| #170 | 사전 중복·생성 409 뒤 기존 모달 DOM과 기간·인원·고객 이름 유지. 안내 확인 뒤 객실 선택 포커스, 다른 객실로 재시도. 503은 기존 동일 key 결과 확인 흐름 유지 | 고객 이름은 현재 메모리에만 보존 |
| #188 | 용량/형식 로컬 오류를 고정 문구로 구분하고 서버 미전송 표시. 5MiB -1/정확히/+1 검사 | 디코딩 가능한 사진의 기존 최적화 유지. 실제 휴대폰 HEIC codec 미검증 |
| #189 | 기존 슬롯 범위 갱신·accepted snapshot·null GET fallback·직렬 큐 회귀 검증 | 실기기 지연은 #206 UAT |
| #202 | 과거/종료 업무는 cleaning-history 목록·상세로 읽기. 과거 미종료는 관리자 처리 필요. 수행 API·버튼 없음. 객실별 403/409/410/503 격리 | 운영 512호를 임의 종료하지 않음 |
| #194 | 같은 scope의 중복 함수 선언 26종 제거. 단일 live 진입점, demo 유지. 구형 API 미구현 fallback을 설정 비활성 안내로 교체. 빌드에 sourceCommit/index SHA/SW 버전 기록 | 실제 계정·실기기/PWA UAT와 운영 Vercel 배포는 별도. 이슈 유지 |
| #142 | 배포 API51 snapshot 154/166, 정확한 생성기/lockfile, 전체 타입·34 CAS·20 cursor·Idempotency/error 검사, 보수적 호환성 비교와 모든 PR CI | 임의 어휘·복잡 조건 schema 변경은 보수적으로 차단하여 검토 |
| #140 | 최신 제공/소비/활성/UAT/인증 상태를 아래에 분리. 과거 문서에 최신 인계 링크 | 독립 백엔드 검토는 미수행. 사진 보관 정책 변경 없음 |
| #84, #89 | 구역별/복층·계단/샘플 템플릿 요구는 최신 정책으로 대체됨 | 일반 사진 1–20장 및 별도 증빙 유지. 삭제된 템플릿 UI 복원 안 함 |
| #206, #207, #219, #220 | PR #222 구현과 후속 회귀 유지 | 실제 사진 UAT·모바일 p50/p95·자정 역할 UAT·Drive 인증/물리 PIN 복구는 아래 참조 |

## 최신 API 연결 상태

백엔드 최신 인계는 main `ad1b1a0ce54865a1b28f9eded2467c856241bf6f`, API51 / migration history120이다. dev `c1707ee`는 역통합이며 추가 운영 배포·migration으로 보지 않는다. 공개 health/OpenAPI 읽기와 합성 API 회귀를 구분한다. 운영 DB/마이그레이션을 다시 실행하지 않았다.

| 기능 | 백엔드 제공 | 프런트 소비 | 빌드 활성 | 실제 UAT·차단 |
| --- | --- | --- | --- | --- |
| 사진 snapshot/수동 재시도 | 배포 API51 | 연결·합성 회귀 통과 | snapshot 기본 true | 사용자 실사진 UAT 대기. 첫 503 원인 미확정 |
| 인증 문맥/가능일/객실/주급 성능 | 배포됨 | 필요한 범위 batch·지연 조회 연결 | 기존 조회 활성 | 실제 p50/p95 미측정. bounded hydration RPC #415 미제공 |
| 계획일·KST 자정 | 배포됨 | 원 serviceDate/계획일 구분·stale 차단 | planningDate 기본 true | 실제 관리자/메이드 자정 UAT 대기 |
| PIN 문자열·Excel | 배포됨 | export 및 장기 4/6자리 직접 입력 연결 | export 기본 true | 실제 export/물리 PIN UAT 대기 |
| Drive→앱 import | 계약 존재 | 기존 preview/apply 후보 | transfer false | 백엔드 #463 인증·시트 접근, secret-free pinVersion/ACTUAL_PIN_REENTRY 해결 전 활성 불가 |
| OAuth PR #462 | dev 후보 | 운영 연결 안 함 | 비활성 | 배포 완료로 취급하지 않음 |

실제 Preview 활성값은 배포 후 기록한다. 환경의 명시적 false가 기본값보다 우선한다. 현재 PIN 문자열을 숫자 전용 v0.9.4로 되돌리지 않는다. 복구는 v0.9.5 호환 경로를 사용한다. pinVersion을 0이나 추측값으로 보내지 않는다.

## API 계약 자동화

- 입력 `contracts/backend-openapi.json`, 신원 `contracts/backend-openapi.manifest.json`, 전체 타입 `src/api/generated/room-management-api.ts`. 원문 SHA `929c0fc8af53f839d4464d29e99b1088df6d159a52420d9aab5b8a73e48e871c`.
- 닫힌 PR #143의 최종 수정본을 최신 계약에 맞춰 이식했다. 오래된 snapshot/전역 checksum 강제 재작성은 가져오지 않았다.
- `npm ci`, `npm run contract:generate`, `npm run contract:check`, `npm run contract:test-diff`, `npm run contract:diff -- --base-ref origin/dev`.
- `openapi-typescript@7.13.0` 고정. 전체·cleaning 타입을 오프라인 snapshot에서 재검사한다. path/operation 제거·operationId·request narrowing/response widening·required/header/CAS/cursor/error/민감 필드 검증.
- CI는 paths 필터 없이 모든 PR과 dev/main push에 실행되어 generator/workspace/lockfile 변경을 포함한다. base commit을 먼저 검증하며 잘못된 ref/읽기 실패를 초기 baseline으로 오인하지 않는다. 실제 base에 snapshot이 없을 때만 최초 도입으로 통과한다.
- 일반 JSON Schema 포함 관계 판정기는 아니다. if/then/else·dependent/pattern/contains/prefix/unevaluated/multipleOf 변경은 자동 허용하지 않고 검토를 요구한다. 생성 타입은 수동 수정하지 않는다.

## 검증과 배포 경계

Browser plugin not available로 기존 번들 Playwright Chromium 151을 사용했다. 합성 fixture는 승인된 데모 데이터만 사용하고 모든 업무 요청을 가로챘다. 360/390/768/1440px에서 기존 카드·버튼 목적지, overflow, 키보드·포커스·모달/Back, 접근성 이름, 콘솔·역할 가드를 검증했다. 상세 결과와 PNG는 `WIREFRAME/QA.md`를 따른다.

새 빌드의 `build-info.json`은 sourceCommit, indexSha256, serviceWorkerVersion, deploymentChannel을 기록한다. 서비스워커 `2026-10-22-2`. Preview 보안 보호를 유지하며, 실제 운영 업무 mutation과 production Vercel 승격은 이 문서 작성 시 수행하지 않았다. Preview 검증·main 병합 결과는 후속 릴리스 기록에 추가한다.
