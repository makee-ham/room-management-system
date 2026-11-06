# 객실별 담당 작업 메모 프런트 인계

기준: 2026-11-02 사용자 요청, 프런트 [#292](https://github.com/makee-ham/room-management-system/issues/292), 기존 API 인계 [#270](https://github.com/makee-ham/room-management-system/issues/270), 백엔드 [#539](https://github.com/wrongstory/room-management-system-backend/pull/539).

## 2026-11-06 통보 후 수행 생성 전 저장 수정

현재 통보 배정에 `attemptStatus=null`이 명시된 경우 수행 회차가 없으므로 관리자 lifecycle 조회를 저장의 선행 조건으로 두지 않는다. 기존 `POST /v1/assignments/{cleaningTargetId}/change`가 관리자 권한·현재 배정·버전·착수 여부를 재검증한다. 수행이 있거나 상태 필드가 누락된 경우 기존 lifecycle 조회를 유지하며403을 성공으로 취급하지 않는다. 메모 작성 → 저장·통보라는 기존 흐름과 시작한 작업의 수정 금지는 유지한다. 실제 운영 RPC의 수행 없음403 조건을 읽기 확인하고 같은 조건의 수정 전 실패/수정 후 성공, 동시 착수 거절·입력 보존을 합성 회귀로 확인했다. 자세한 범위와 한계는 `WIREFRAME/QA.md`를 따른다.

## 2026-11-06 운영 활성화 수정

- 원인: 운영 DB/API 배포 후에도 프런트 `assignmentInstructionMemo=false`가 유지돼 기존 입력란이 `메모 저장 준비 중 · API 미제공`으로 잠겨 있었다.
- 운영 API62 `ACTIVE`, health 200, OpenAPI의 메모 요청 2종·읽기 5종을 확인했다. 전체 운영 명세는 server URL을 제외하면 현재 고정 계약과 동일하므로 snapshot/client를 다시 생성하지 않는다. 명세의 `#534 미배포 후보` 설명과 아래 11월 2일 기록은 과거 상태다.
- 설치된 CLI로 읽기 전용 조회해 `cleaning_assignments.instruction_memo`와 `assignment_instruction_memo` 적용 이력, 전체 migration 152개를 확인했다. DB 변경·migration 실행은 없다.
- 빌드·로컬 서버·Pages·환경 예시의 기본값을 true로 변경한다. 운영 배포 artifact는 현재 공개 runtime을 읽어 메모 플래그만 true로 바꾸고 API 주소·세션 방식·다른 플래그를 보존한다. 명시 false는 롤백용으로 계속 지원한다.
- 기존 관리자 입력/저장·통보, 메이드 본인 카드/상세, 초안·이력·CAS/동일 키 재확인·500 UTF-16 제한·착수 후 잠금은 그대로다. 새 화면이나 API를 만들지 않는다.
- 실제 API의 두 POST 경로 CORS와 익명 조회 401, 합성 API의 관리자 작성/삭제/통보·본인 메이드 조회·충돌·실패를 확인한다. 실제 운영 업무를 테스트 문구로 변경하거나 메이드에게 테스트 통보하지 않는다. 실사용 저장·기기 수신은 이 검증에 포함하지 않는다.
- 서비스워커 `2026-11-06-11`. 상세 실행 결과와 배포 신원은 `WIREFRAME/QA.md`를 따른다.

## 화면과 저장 범위

- 기존 청소 관리 → 객실별 담당 표의 담당 선택 아래에 객실별 `작업 메모 · 선택` 입력과 저장 버튼을 둔다. 기존 5열·객실 상세·담당 선택·취소 버튼의 목적은 유지한다.
- 이 메모는 해당 청소 대상의 배정에 붙는다. 객실의 영구 메모, 예약 메모, 검수 후 특이사항과 구분하며 객실번호로 다른 청소에 복사하지 않는다.
- 담당 선택 전에도 작성할 수 있지만 서버 저장에는 담당이 필요하다. 새 배정은 메모를 포함한 미통보 초안으로 저장하고 기존 배정 요약의 `저장·통보`로 전달한다. 이미 통보된 미시작 배정은 행의 `메모 저장·통보`로 변경한다.
- 메이드의 본인 통보 업무 카드와 펼친 업무 정보에 줄바꿈을 보존한 읽기 전용 메모를 표시한다. 관리자 요약과 배정 이력도 해당 revision의 서버 값을 사용한다.
- 500 UTF-16 단위를 제한한다. 빈값/공백은 명시 삭제, 손대지 않은 메모는 요청에서 생략한다. 개인정보·PIN·인증정보를 입력하지 않도록 안내한다.
- 입력 초안은 날짜·청소 대상·원 배정 ID/버전에 묶어 메모리에만 둔다. 새로고침·날짜 전환·로그아웃 후 초안은 복원하지 않는다. 저장 실패 시 입력을 유지하고, 409 이후에는 최신 담당/메모를 확인한 뒤 다시 저장한다. 시작한 작업은 기존 lifecycle 절차를 따른다.
- 메모 변경은 새 요청 키, 응답 유실 재확인은 같은 body/key를 사용한다. 서버 성공 응답에 메모가 없거나 다르면 성공으로 표시하지 않고 최신 배정을 다시 읽는다. 원문을 URL·브라우저 저장소·history·알림 문구에 추가하지 않는다.

## 2026-11-02 연결 계약과 운영 차단 기록

백엔드 dev 병합 `46e47ed0ddb080c293fa5e02152d1683ee8b5eee`의 `docs/ASSIGNMENT_INSTRUCTION_MEMO_534.md`를 확인했다.

| 항목 | 연결 |
| --- | --- |
| 초안 | `POST /v1/assignments/drafts` 선택 `instructionMemo` |
| 미시작 변경 | `POST /v1/assignments/{cleaningTargetId}/change` 선택 `instructionMemo`; 기존 CAS·담당·sequence 필수값 유지 |
| 읽기 | Assignment/AssignmentCard/commit-impact의 대상별 `instructionMemo`; 이력은 각 과거 revision 값 |
| 입력 거절 | `VALIDATION_ERROR`, `ASSIGNMENT_INSTRUCTION_INVALID`; 입력을 오류에 반사하지 않음 |
| 충돌 | `ASSIGNMENT_VERSION_CONFLICT` 및 기존 lifecycle/권한 오류 |
| 미제공 | `assignmentInstructionMemo !== true`이면 입력·저장 비활성, `API 미제공` 표시 |

2026-11-02 공개 운영 OpenAPI에서 `instructionMemo`가 없는 것을 확인했다. 고정 운영 계약은 API53 / migration122를 유지하며 후보 계약으로 덮어쓰지 않았다. 백엔드 PR #539는 migration140을 포함한 feature→dev 통합이며 실제 SQL/RLS/DB 경합 및 운영 적용은 NOT RUN이라고 명시한다. 프런트 배포만으로 운영 저장·전달 완료라고 기록하지 않는다.

`RMS_ASSIGNMENT_INSTRUCTION_MEMO=false`가 빌드·로컬 서버·Pages의 기본값이다. false에서는 기존 배정 API를 그대로 사용한다. 데모는 실제 서버/알림이 없는 메모리 시뮬레이션이다.

## 2026-11-02 활성화 후속 계획 기록

1. 백엔드의 최종 통합 DB 검증, 운영 pending migration 검토·적용, API/Swagger 배포를 해당 릴리스 절차로 완료한다. 프런트 작업에서 미검증 선행 migration123~140을 한꺼번에 적용하지 않는다.
2. 실제 운영 health/OpenAPI와 배포 SHA를 확인하고 `contracts/backend-openapi.json`, manifest, 생성 client를 정식 절차로 갱신·검증한다.
3. 보호된 검증 환경에서 관리자 작성/수정/삭제 → 통보 → 본인 메이드 읽기, 타인/미통보 차단, 재배정·새 청소 대상 분리, 응답 유실·409를 실제 API로 확인한다.
4. `RMS_ASSIGNMENT_INSTRUCTION_MEMO=true`로 프런트를 재배포하고 허가된 운영 UAT를 수행한다. 실패 시 false로 되돌리며 서버 이력은 삭제하지 않는다.

## 검증

재현: `python3 scripts/serve.py --port 4187` (Windows는 `python`) 후 Playwright가 설치된 환경에서 `node scripts/check-assignment-instruction-memo.mjs`. 브라우저 합성 API 검증과 실제 운영 검증은 구분한다. 화면 비교 및 실행 결과는 `WIREFRAME/QA.md` 최신 절을 따른다.
