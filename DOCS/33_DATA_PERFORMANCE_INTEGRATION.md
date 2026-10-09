# 근무 가능일과 주급 조회 성능 인계

2026-10-09 기준. 프런트 [#207](https://github.com/makee-ham/room-management-system/issues/207)의 기존 API 활용 개선이다. 화면 구조·청소 배정·송금 토글 목적은 바꾸지 않는다. 출발점은 `dev`의 `41ac17a`이며 사진 운영 인계 PR #209를 먼저 검증·병합했다.

## 반영 범위

| 기능 | 프런트 변경 | 보존한 계약 |
| --- | --- | --- |
| 다음 주 근무표 | 관리자 가능일을 메이드별 N회 대신 전체 1회 조회. 변경 요청은 병행 조회 | 퇴사 계정 제외, 본인 범위, 최신 제출과 초안, auth/load revision |
| 주급 목록 | 페이지가 도착할 때마다 기존 카드 표시. 전체 목록 전에는 총액을 표시하지 않음 | 주차·금액 검증, 중복과 반복 cursor 차단, 실패를 0원으로 대체하지 않음 |
| 송금 표시 | 한 목록 로드에서 최대 3건씩 단건 GET. 실패한 카드만 재조회 | 독립 송금 토글, CAS version/basisFingerprint, 금액 재확인, 실제 송금 원장 불변 |
| 산출 상세 | 버튼 즉시 상세 진입 후 선택 메이드의 독립 조회 병행 | 페이지별/목록 대비 summary 검사 완료 전 정정 액션 미노출, Back/권한/세대 가드 |
| 홈 첫 표시 | 각 핵심 데이터가 도착하면 해당 화면 갱신. 느린 주급·알림 때문에 객실 요약을 기다리지 않음 | 기존 카드 위치와 검수/내일 배정 목적지, 로드 중/오류/0건 구분 |

사진 타입은 실제 운영 Swagger로 재생성했다. 미완료 operation의 nullable 보존 필드와 선택 photoSlots를 반영했고, nullable 상태를 저장 완료·만료로 해석하지 않는다. 사진 옵션은 **false 유지**다. 운영 인증 업로드 UAT에 사용할 계정·객실 지정이 남아 있으며, 이미 배포된 백엔드와 미완료 UAT를 혼동하지 않는다. 세부 조건은 [문서 32](32_PHOTO_PERFORMANCE_INTEGRATION.md)를 따른다.

## 확인한 백엔드

- 운영 source `32c100ea3f1eecbd43ebc900feafdb6af63173c2`, v0.9.2/API 43. 직접 GET한 운영 OpenAPI와 [게시 Swagger](https://wrongstory.github.io/room-management-system-backend/)의 paths/components가 일치한다. 150 paths/162 operations, health 200, 게시 SHA256 `b1ab571818063e07964f139fa10a2225f93ba3945a98e303784b4b8bf22a6eff`.
- `GET /v1/availability?weekStart=...`는 관리자 전체 현재 version을 지원한다. 같은 운영 commit의 `supabase/functions/_shared/availability-api.ts`와 Node service를 확인했다. 계정별 새 API를 만들지 않는다.
- 해당 조회는 cursor/전체 건수를 제공하지 않는다. 저장소 `supabase/config.toml`의 `max_rows=1000`에 닿는 응답은 현재 표시할 메이드별 GET(최대 3건씩)으로 재조회한다. 이 값은 저장소 설정 확인이며 원격 PostgREST 설정 실측은 아니다. 운영 상한을 변경할 때는 인계가 필요하다.
- 주급 batch `GET /v1/payroll/remittance-markers`는 운영 OpenAPI에 **없다**. [백엔드 PR #418](https://github.com/wrongstory/room-management-system-backend/pull/418)은 미배포 후보이므로 호출하지 않는다. 공통 api_total timing(#417)·배정 조회 개선(#419)도 이번 운영 계약에 포함되지 않았다.

## 백엔드 협의와 후속

1. 사진: 지정 계정/객실에서 accepted snapshot·null fallback·인증 성공 CORS/Server-Timing UAT를 한 뒤 프런트 옵션 활성화. 현재 전역 업로드 1건과 조회 4건 상한은 유지한다.
2. 주급 batch: 실제 배포 SHA/OpenAPI 인계 뒤 페이지별 최대 10명 CSV 계약으로 교체한다. 실패를 미송금으로 처리하지 않고 현 단건 fallback과 CAS 검증을 보존한다. 이번 프런트 변경은 HTTP 요청 수를 줄이는 batch 구현이 아니라 순차 대기 감소다.
3. 가능일: 운영 `max_rows`와 데이터 증가 시 응답 완전성 확인. 1,000행 도달 fallback은 구현했지만, API의 명시적 truncation/total/cursor 계약이 없으므로 임의의 더 낮은 운영 상한까지 자동 탐지한다고 보장하지 않는다. 변경 요청 목록도 기존 비페이지 계약이어서 별도 완전성 개선 대상이다.
4. 상세: 현재 선택 메이드의 모든 페이지를 읽고 summary를 대조한 다음 금액 정정을 연다. 페이지별 더보기는 별도 UI 결정을 거치며 이번에는 넣지 않았다.

## 검증

`scripts/check-data-performance.mjs`: 1/10/20명, 늦은 페이지·marker, 부분 오류·중복·cursor 반복, 행 상한 fallback, 주차 응답 역전, 로그아웃, 본인 범위, 상세 로드 중 Back, summary 불일치, 4개 폭과 포커스를 합성 응답으로 검증한다. 기존 사진·청소·송금·정정·내비게이션 검사는 `WIREFRAME/QA.md` 최신 기록을 따른다.

비교 기준 `fe09fa7`, 동일 합성 HTTP 지연(목록 첫 페이지 30ms/후속 60ms, marker 80ms), 각 조합 3회. 첫 카드는 DOM 삽입 시점, 전체 표시는 로드 완료와 송금 조회 중 표시 종료 뒤 측정한다. p95는 3회 중 최댓값이며 서비스 SLA나 실기기 p95가 아니다. 실제 운영 사진 쓰기, 휴대폰 갤러리/HEIC/통신망 UAT는 미실행이다.

배포 식별자·수치·스크린샷은 `WIREFRAME/QA.md`에 기록한다. 캐시 갱신 worker는 `2026-10-09-3`이며 API/인증/사진 cache 금지 정책은 변경하지 않는다.
