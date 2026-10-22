# 새 특이사항 메모 단독 등록 연동 준비

2026-10-22 추가된 [프런트 #227](https://github.com/makee-ham/room-management-system/issues/227), [backend #474](https://github.com/wrongstory/room-management-system-backend/issues/474)의 후속이다. 기준 프런트 dev `6fc4d44`, 운영 main `d59a755`다.

## 현재 운영과 후보 구분

- 현재 배포 계약은 사후 특이사항의 사진을 1~10장 요구한다. 프런트 guard만 제거하면 API·DB에서 실패한다. 고정 OpenAPI snapshot을 미배포 후보 schema로 덮어쓰지 않는다.
- [최신 정책 인계](https://github.com/makee-ham/room-management-system/issues/227#issuecomment-6342432586)는 **메모 필수 + 사진 선택 0~10장**이다. 사진만 등록하는 정책이 아니며 일반 청소 필수 사진·폭탄방 증빙·제출 전 특이사항 규칙은 바꾸지 않는다.
- 새 runtime flag `supplementalMemoOnly` / 빌드·로컬 환경 `RMS_SUPPLEMENTAL_MEMO_ONLY`는 production/preview 모두 기본 `false`다. 누락·문자열 등 boolean true가 아닌 runtime 값은 활성화되지 않는다.
- OFF에서는 기존 1~10장 guard를 유지하고, `메모만 등록은 준비 중입니다. 현재는 사진을 1장 이상 함께 첨부하세요.`라고 안내한다. 준비 중 UI를 운영 사용 가능으로 표현하지 않는다.

## 프런트에서 준비한 경로

1. ON에서 메모 1~500자를 필수로 검사하고 사진은 0~10장으로 안내한다. 빈 메모+0장과 빈 메모+사진은 요청 전 차단한다.
2. 사진 0장은 기존 draft 저장 뒤 서버가 반환한 정수 `draftRevision`/`evidenceRevision`을 사용한다. 초기 evidenceRevision=0을 허용하되 누락·음수·비정수 값을 0으로 추측하지 않는다.
3. 사진 업로드 호출을 생략하고 기존 finalize endpoint로 `evidence: []` 및 반환된 revision을 보낸다. 사진이 있으면 기존 exact evidence ID/revision/order·CAS·한 장씩 업로드를 유지한다.
4. `evidence: []` 신고는 목록에 `사진 없음 · 메모 기록`으로 표시하고 사진 버튼·다운로드를 만들지 않는다. 관리자의 기존 해결 처리와 제출/수익 이력은 유지한다.
5. 409 뒤 draft 재조회·재시도, finalize 응답 유실 뒤 같은 key/payload 결과 확인과 이미 생성된 report 복구를 기존 흐름으로 처리한다. 고객/PIN/메모/사진 원문을 history·로그·영속 저장소에 새로 넣지 않는다.

## 활성화 전 필요한 백엔드 인계

- Fastify/Edge 입력·응답·OpenAPI·DB check/RPC가 evidence 0~10장과 revision0을 함께 허용하는 릴리스의 실제 운영 반영 증거.
- 사진 collection이 생성되지 않은 draft의 finalize/receipt replay/목록·단건·해결·retention 권한 회귀.
- 같은 배포 OpenAPI에서 finalize·report evidence 최소 개수 0 및 revision0 계약을 확인하고 고정 snapshot/generated client/호환성 CI 갱신.
- 합성 ON 회귀 후 승인된 활성화 배포에서만 `RMS_SUPPLEMENTAL_MEMO_ONLY=true`. 프런트 작업에서 backend migration·실제 신고 생성을 실행하지 않는다.

#227은 위 배포와 실제 활성화가 끝날 때까지 OPEN이다. 프런트 후보와 준비 중 안내를 배포한 것만으로 메모 단독 등록의 운영 완료를 표시하지 않는다.

## 검증

`scripts/check-backend-v090.mjs`에서 OFF의 0장 쓰기 차단과 기존 사진 등록, ON의 메모+0/1/10장·11장 선택 거절·빈 메모 거절, 0장 업로드 0회, 반환 revision0과 누락 revision 차단, 목록/해결, 409 복구·응답 유실 동일 key replay·역할 가드를 합성 API로 검증한다. 일반 청소·폭탄방 사진 규칙은 별도 기존 회귀로 확인한다.

Browser plugin not available로 기존 Playwright Chromium 151을 사용한다. 360/390/768/1440px·키보드/모달/Back·포커스·history 메모 비저장·overflow·console을 검증하며, 같은 역할/fixture의 기본 OFF 화면을 변경 전과 비교한다. 실서버 0장 신고·실기기·업무 데이터 mutation은 미실행이다. 대표 PNG와 상세 결과는 `WIREFRAME/QA.md`, 최종 main SHA/배포 신원은 릴리스 PR에 기록한다.
