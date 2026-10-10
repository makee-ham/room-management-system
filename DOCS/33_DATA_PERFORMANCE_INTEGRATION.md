# 근무 가능일과 주급 조회 성능 인계

2026-10-10 기준. 프런트 [#207](https://github.com/makee-ham/room-management-system/issues/207)의 조회 개선과 백엔드 v0.9.3 연결 현황이다. 이번 출발점은 `dev`의 `e2b95d8`이다. 화면 구조·청소 배정·송금 토글 목적은 바꾸지 않는다. 10월 9일 단건 병렬 개선에 이어 실제 배포된 묶음 조회를 연결했다.

## 반영 범위

| 기능 | 프런트 변경 | 보존한 계약 |
| --- | --- | --- |
| 다음 주·배정 주 근무표 | 관리자 가능일을 메이드별 N회 대신 전체 1회 조회. 다음 주 변경 요청/배정일 후보는 별도 병행 조회 | 다음 주 퇴사 제외, 배정 주 활성 계정만, 본인 범위, 최신 제출과 초안, auth/load revision |
| 주급 목록 | 페이지가 도착할 때마다 기존 카드 표시. 전체 목록 전에는 총액을 표시하지 않음 | 주차·금액 검증, 중복과 반복 cursor 차단, 실패를 0원으로 대체하지 않음 |
| 송금 표시 | 도착한 페이지 최대 10명을 CSV 묶음 GET. 묶음은 한 번에 1개, 실패한 카드의 명시적 재조회는 단건 GET | 응답 순서/인원/주차/전체 marker 검증, 독립 송금 토글, CAS version/basisFingerprint, 금액 재확인, 실제 지급 원장 불변 |
| 산출 상세 | 버튼 즉시 상세 진입 후 선택 메이드의 독립 조회 병행 | 페이지별/목록 대비 summary 검사 완료 전 정정 액션 미노출, Back/권한/세대 가드 |
| 홈 첫 표시 | 각 핵심 데이터가 도착하면 해당 화면 갱신. 느린 주급·알림 때문에 객실 요약을 기다리지 않음 | 기존 카드 위치와 검수/내일 배정 목적지, 로드 중/오류/0건 구분 |

묶음 응답은 전체 검증 후 기존 카드에 반영한다. 401/403/500, 업무 404, 누락·순서 오류는 해당 묶음 전체를 조회 실패로 두고 토글을 잠근다. `404 ROUTE_NOT_FOUND`만 이번 목록 로드에서 단건 최대 3병렬로 전환한다. 주차·역할·세션이 바뀌면 늦은 결과를 폐기하고 아직 시작하지 않은 묶음을 보내지 않는다. 조회 실패 버튼은 작은 화면에서 다음 줄에 배치한다.

사진 타입의 nullable/선택 snapshot 계약은 보존했다. 2026-10-10 지정 계정에서 인앱 탭에만 옵션을 적용해 5+1장 정상 업로드·서버 재조회·확대·성공 Server-Timing 접근을 확인한 뒤, 사용자의 지시에 따라 **운영·프리뷰 전체 true 적용과 재배포를 완료**했다. UAT 당시 5장 POST 약 35.89초, 추가 1장 약 10.58초 중 서버 약 9.85초였으며 서버 성능 개선은 별도 작업이다. 모바일·20장 실측과 정상 UAT를 구분하며, 세부 조건은 [문서 32](32_PHOTO_PERFORMANCE_INTEGRATION.md)를 따른다.

## 확인한 백엔드

- 운영 source `72771b5f7d87cc749ed57a845b9ecf8bf18aa290`, [v0.9.3 릴리스](https://github.com/wrongstory/room-management-system-backend/releases/tag/v0.9.3), API ACTIVE44는 [백엔드 최신 인계](https://github.com/makee-ham/room-management-system/issues/207#issuecomment-6094034492) 기준이다. 직접 GET한 운영 OpenAPI와 [게시 Swagger](https://wrongstory.github.io/room-management-system-backend/)의 paths/components가 일치한다. 151 paths/163 operations, health 200. `info.version=0.6.0`은 앱 릴리스 버전과 별개다.
- 해당 commit의 `docs/PAYROLL_REMITTANCE_BATCH_414.md`, `docs/AVAILABILITY_READ_COMPLETENESS_427.md`, `docs/API_PERFORMANCE_413.md`를 대조했다. 각 파일 안의 이전 미배포 checkpoint는 최신 배포 인계와 구분한다.
- `GET /v1/payroll/remittance-markers?weekStart=...&maidProfileIds=UUID,UUID`는 CSV 문자열 하나를 받는다. 관리자 1~10명, 메이드 본인 1명. `{weekStart, markers}`는 요청 순서이며 단일 DB snapshot은 아니다. HTTP 10회를 1회로 줄이지만 DB RPC는 N회, 요청 내 동시성은 3이다.
- 가능일 current/변경 요청/후보 목록은 서버가 exact count와 반환 수, 일별 7개 row를 검증한다. 잘림·상한 초과·불완전 응답은 `500 AVAILABILITY_COMMAND_FAILED`다. 프런트는 오류·재시도로 표시하고 미제출/불가/후보 없음으로 대체하지 않는다. 과거 1,000행 추정 fallback은 제거했다. 명시적 pagination은 여전히 미제공이며 운영 row cap 실측 완료를 뜻하지 않는다.
- 성공 업무 응답의 `Server-Timing: api_total`은 허용 Origin에서 확인할 수 있는 handler 시간이다. 화면 전체 시간이나 DB 단독 시간으로 해석하지 않는다. 인증/오류/HEAD/OPTIONS에서 헤더가 없는 것은 정상이다. 프런트에 원문 응답·사용자별 계측 로그나 영속 수집기를 추가하지 않았다. 사진 성공 실측은 문서 32에 기록했고, batch/근무표 인증 성공 실측은 아직 미실행이다.
- 배정 관계 조회 병렬화는 기존 API/DTO 그대로여서 별도 화면 변경 없이 적용된다. 이번 프런트는 별도로 배정 주 근무표의 N회 조회도 1회로 줄였다. DB/migration 변경은 하지 않았다.

## 백엔드 협의와 후속

1. 사진 정상 UAT와 snapshot 옵션 전역 활성화는 완료했다. 실제 모바일·20장 실측은 후속이다. null은 fixture에서 검증했고 운영에서 장애를 강제로 만들어 재현하지 않는다. 실제 null 미발생은 NOT RUN으로 남기며 다른 기능 개발을 막지 않는다. 전역 업로드 1건/조회 4건 상한은 유지한다.
2. 프런트 후속: 실제 계정에서 batch/근무표 정상 조회 및 1/10/20명 첫 표시·전체 표시·요청 수·p50/p95 확인. 이번 공개 계약/합성 QA는 인증 성공 UAT를 대신하지 않는다.
3. 백엔드 후속: #414 반복 DB 집계/왕복 축소, #416 실측 진단, #427 실제 row cap/1,000 초과 pagination, #411 비공개 썸네일. 이번 v0.9.3 배포 미완료나 프런트 연결 차단으로 분류하지 않는다. 이번 대조에서 새 백엔드 계약 결함은 확인하지 않았다.
4. 상세는 모든 페이지와 summary를 대조한 뒤 금액 정정을 허용한다. 임의의 부분 합계로 변경하지 않는다. 전체 백업/복원·DB 초기화는 사용자 결정대로 별도 후속이다.

## 검증

`scripts/check-data-performance.mjs`: 0/1/10/20명, CSV/묶음 전체 검증, 정확한 404 fallback, 401/403/500/업무 404, 단건 재조회, 늦은 페이지·marker, 부분 오류·중복·cursor 반복, 주차 응답 역전, 로그아웃, 본인 범위, 상세/Back/summary 불일치, 가능일 500/배정 잠금, 정상·오류 4개 폭과 포커스를 검증한다. 같은 fixture의 390/1440px 정상 화면 PNG는 이전 dev와 byte 단위로 같다.

비교 기준 `e2b95d8`, 각 조합 3회. 합성 목록 지연 30ms/후속 60ms, 단건 marker 80ms, batch는 네트워크 60ms + 3개 병렬 그룹당 20ms로 가정했다. 실제 DB 속도 측정이 아니다. 첫 카드는 DOM 삽입, 전체 표시는 송금 조회 중 표시 종료 뒤 측정한다. p95는 3회 중 최댓값이며 서비스 SLA나 실기기 p95가 아니다. 20명 주급 HTTP는 22→4회, 10명은 11→2회다. 정확한 수치와 기존 사진·청소·송금·정정·내비게이션 검증 결과는 `WIREFRAME/QA.md` 최신 기록을 따른다.

배포 식별자·스크린샷은 `WIREFRAME/QA.md`에 기록한다. 캐시 갱신 worker는 `2026-10-10-2`이며 API/인증/사진 cache 금지 정책은 변경하지 않는다.
