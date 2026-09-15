# 백엔드 OpenAPI 생성 클라이언트 계약

연결: 프런트 Issue #142 · 백엔드 `wrongstory/room-management-system-backend#173`

## 목적

백엔드 OpenAPI를 프런트 타입의 정본으로 사용하고, 사람이 옮겨 적은 타입이나 오래된 문서가 API 계약보다 앞서지 않게 한다. 이 기반은 타입 생성과 호환성 검증만 제공하며 현재 화면의 수동 adapter를 즉시 제거하지 않는다.

## 고정 입력과 산출물

- 입력: `contracts/backend-openapi.json`
- 입력 신원: `contracts/backend-openapi.manifest.json`의 백엔드 저장소·commit·SHA-256
- 산출물: `WIREFRAME/generated/backend-api.d.ts`
- 생성기: `openapi-typescript@7.13.0`
- 호환성 검사기: `scripts/openapi-breaking-diff-lib.mjs`의 OpenAPI 3.1 보수적 비교

스냅샷은 백엔드 `wrongstory/room-management-system-backend`의 `c32aa9eec3945334ddda956afc62cc92d801c410`에서 `npm run openapi:export:full`로 생성했다. 서버 주소는 비밀정보나 운영 project ref가 없는 예시 주소로 치환되어 있다.

## 갱신 절차

1. 백엔드의 검증된 작업 commit에서 `npm run openapi:export:full`을 실행한다.
2. 출력한 `.tmp/full-openapi.json`으로 `contracts/backend-openapi.json`을 교체한다.
3. `scripts/generate-backend-client.mjs`의 `backendSourceCommit`을 그 백엔드 commit으로 변경한다.
4. `npm ci`와 `npm run contract:generate`을 실행한다.
5. `npm run contract:check`, `npm run contract:test-diff`, `npm run contract:diff -- --base-ref origin/dev`를 실행한다.
6. 백엔드 PR/commit과 프런트 PR을 서로 연결한다.

## 자동 차단 기준

- 스냅샷 SHA-256, 백엔드 commit 신원, 생성 타입 해시가 일치하지 않음
- path/operation 수, `operationId` 유일성 또는 필수 업무 영역 누락
- mutation의 `Idempotency-Key`, 주요 CAS request의 `expectedVersion`, 목록 cursor 계약 누락
- 안정적인 `ErrorEnvelope` 또는 민감 필드 차단 계약 훼손
- 기존 path/method 제거, 기존 `operationId` 변경, request/response schema의 호환성 파괴

처음 이 기반을 도입하는 PR은 비교할 base 스냅샷이 없으므로 baseline 생성으로 기록한다. 이후 PR부터 base branch의 snapshot과 자동 비교한다.

## 현재 범위 밖

- 기존 `WIREFRAME/cleaning-api.d.ts`와 화면 adapter 제거
- 생성 타입을 이용한 모든 화면 전환
- 운영 자격증명, 실제 로그인, 실제 API 호출
- 미확정 UI 정책 결정과 브라우저 전체 E2E

이 항목들은 별도 Issue에서 화면 단위로 전환하고 회귀 QA를 통과한 뒤 처리한다.
