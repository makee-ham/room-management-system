# 10월 13일 백엔드 추가 이슈 프런트 인계

## 기준과 적용 경계

- 프런트 기준: dev 795da7e. 작업 브랜치 codex/backend-handoff-oct13.
- 확인 이슈: 프런트 [#215](https://github.com/makee-ham/room-management-system/issues/215), [#218](https://github.com/makee-ham/room-management-system/issues/218), [#219](https://github.com/makee-ham/room-management-system/issues/219), [#220](https://github.com/makee-ham/room-management-system/issues/220), [#207](https://github.com/makee-ham/room-management-system/issues/207).
- 운영 계약 재확인: 공개 OpenAPI 0.6.0, 151 paths / 163 operations. 운영 v0.9.4 / API46과 백엔드 dev 후보를 구분한다.
- 후보 근거: 백엔드 dev dbc22320의 ROOM_PIN_TRANSFER, ASSIGNMENT_PLANNING_TABS_446, ASSIGNMENT_MIDNIGHT_ROLLOVER_446 문서, transfer route/service/error mapper 및 OpenAPI 소스.
- 추가 확인: 백엔드 [#458](https://github.com/wrongstory/room-management-system-backend/issues/458)의 v0.9.5 Draft PR #460 후보 19dff141은 전체 DB CI 실행 중이라는 인계다. 운영 DB 적용·main 병합·API 배포가 완료됐다는 뜻이 아니다.
- 기존 와이어프레임 구조와 버튼 목적지를 유지한다. 청소 순서 UI나 청소 템플릿은 복원하지 않는다. 서버가 요구하는 sequenceNumber는 호환 필드로만 유지한다.

## 이번 프런트 변경

| 이슈 | 연결/수정 | 운영 적용 |
| --- | --- | --- |
| #218 예약 기본 날짜 | 당일 또는 명시적으로 선택한 날짜, 다음 날 11시 체크아웃. 겹침/레이트가 있어도 객실·날짜 자동 변경 없음. 느린 preview가 입력/다른 모달을 덮지 않음 | 적용 가능 |
| #215 미퇴실 신고 | loading / ready empty / ready items / error 분리. 실패 때 이전 목록과 '신고 없음'을 숨기고 재조회 제공. 인증·요청 revision 검사 | 적용 가능 |
| #207 인증 문맥 503 | AUTH_CONTEXT_UNAVAILABLE 안내. 로그인 후 me 실패·기존 세션 갱신 실패에서 유효 세션을 강제 삭제하지 않음 | 기존 계약과 호환 |
| #219 날짜 경계 | KST 날짜 감지, 복귀/재연결 재조회, 이전 날짜 응답 폐기, 자정에 오래된 배정 명령 차단. 저장 전 초안은 재확인, 진행 중 업로드 큐 유지 | 적용 가능 |
| #219 계획일 계약 | change에 선택 serviceDate 전달, 해당 일 availability 조회. planningDate와 원 serviceDate 구분 표시. 같은 객실의 별도 target을 합치지 않고 행 이동도 target ID 사용 | 후보 flag OFF |
| #220 PIN 전송 | 기존 내보내기 안에 앱→xlsx, Drive→앱 preview/apply. 건수/고정 오류 사유만 표시, 명시 저장, 유실 응답 동일 token/key 확인 | 후보 flag OFF |
| #220 PIN 입력 | 서버의 현재 장기 예약이면 직접 4/6자리, 일반 4자리, 랜덤 4자리. 가져오는 원문은 프런트가 파싱·절단·재검증하지 않음 | 후보 flag OFF |

예약의 과거 시각·겹침·최소 숙박·현재 준비도 검증은 우회하지 않는다. 기본 날짜를 보존하는 것과 해당 시간에 실제 예약이 가능하다는 것은 별개다. 기존 예약 상세는 원 날짜를 그대로 표시한다.

KST 감시는 열린 앱에서 30초 간격 및 페이지 복원·화면 복귀·온라인 복귀 때 수행하며 배정 명령 직전에도 검사한다. 서버의 자정 담당 해제/이월을 프런트가 대신 실행하지 않는다. 작성 모달/요청 중에는 자동 초기화를 미루고 이전 날짜 저장을 거부한다. 명시적으로 선택한 과거/미래 조회일은 유지한다. 새로고침·앱 종료 뒤 업로드 복구를 보장하지 않는다.

## PIN 계약

- `GET /v1/rooms/pins/export`: 인증 no-store blob, xlsx MIME/ZIP 시작 검증 후 명시 다운로드, 메모리 URL 해제. 서버가 만든 시트 1의 B/C열을 그대로 전달한다.
- `POST /v1/rooms/pins/import/preview`: 빈 JSON 객체. preview의 valid/total/changed/unchanged/ignored/issues/expiresAt/previewToken만 취급한다.
- `POST /v1/rooms/pins/import/apply`: previewToken과 Idempotency-Key. 유실 시 새 preview/key를 만들지 않고 같은 요청으로 확인한다. 토큰 만료 뒤에도 이미 처리된 receipt 재확인을 허용한다. 확정 오류/충돌은 다시 preview한다.
- 업무 관리자만 사용, developer/maid 직접 실행도 차단. 전체 PIN 목록·token·고객 정보는 URL/history/web storage/로그에 저장하지 않는다. 다운로드는 사용자가 명시적으로 내보낸 민감 자료다.
- 장기 여부는 최신 RoomProjection.reservationPhase=current + displayReservationId의 Reservation.reservationType=long_stay로만 판정한다. PIN 길이, 시트 메모, 투숙 기간으로 추정하지 않는다.
- 기존 PIN 없는 객실 현황 CSV/xlsx 및 앱→Drive 동기화는 별도로 유지한다. 새 '쓰기'를 기존 outbound worker로 대체하지 않는다.

## 백엔드 확인 필요

[#220의 프런트 확인 댓글](https://github.com/makee-ham/room-management-system/issues/220#issuecomment-6144790369):

import 후 SHEET_PIN_AWAITING_PHYSICAL_CONFIRMATION으로 mismatch가 된 객실은 관리자 일반 reveal이 차단된다. RoomProjection에는 pinVersion이 없고, ACTUAL_PIN_REENTRY prepare에는 expectedPinVersion이 필수다. 원문 없이 최신 PIN version을 얻는 공개 경로를 확인해야 한다. 없으면 metadata 계약이 필요하다. 프런트가 version을 0이나 추측값으로 보내지 않는다.

이 확인과 실제 DB/API 배포를 마치기 전 PIN 전송은 운영에서 활성화하지 않는다. 서버 가져오기 성공을 물리 도어락 변경 완료로 표시하지 않는다.

## 활성화·롤백

- `RMS_ASSIGNMENT_PLANNING_DATE=false`, `RMS_ROOM_PIN_TRANSFER=false` 기본값. production/preview 모두 같다.
- 백엔드의 118/119 관련 migration·API release 및 필요한 Drive/HMAC 설정 검증 후 별도 승인된 활성화로 true를 적용한다. 프런트 작업에서 SQL·Drive 설정·서버 배포를 실행하지 않았다.
- 기존 생성 client는 운영 151/163 계약을 유지한다. 미배포 dev 154/166을 운영 정본으로 덮어쓰지 않는다.
- 이전 API로 rollback할 때 두 flag를 false로 빌드한다. 사진 snapshot flag는 true 유지한다.

## 검증

WIREFRAME/QA.md 최신 절에 실행 결과와 배포 증거를 기록한다. 새 검사는 scripts/check-backend-handoff-oct13.mjs이며 Playwright와 openpyxl을 사용한다. RMS_QA_PYTHON으로 Python 경로를 지정할 수 있다. 모든 쓰기는 합성 API fixture이며 실제 PIN 전송·예약 생성·배정 변경은 실행하지 않는다.

## 전달 결과

- 프런트 [PR #221](https://github.com/makee-ham/room-management-system/pull/221), 앱 소스 221ebfe. 기준 브랜치는 dev이며 main에 직접 반영하지 않는다.
- [운영](https://room-management-system-prod.vercel.app/)과 [보호된 프리뷰](https://room-management-system-prod-preview.vercel.app/)에 동일 앱 소스를 배포했다. 두 후보 flag는 false이고 기존 사진 snapshot은 true다.
- #215/#218 수정은 활성 상태다. #219 날짜 경계 보호는 활성 상태이며 계획일 확장 계약은 서버 배포 후 활성화해야 한다. #220은 최신 pinVersion 경로 확인과 서버 배포 이후 활성화해야 한다.
- #140 최신 백엔드 댓글의 배정 CPU/조회 집계 개선은 API 호출 변경 없음이며 운영 미배포라는 점을 확인했다. 합성 CPU 수치를 실제 모바일/네트워크 개선 수치로 취급하지 않는다.
- 실제 운영 메이드 세션에서 업데이트·날짜 이동·뒤로가기와 콘솔을 읽기 검수했다. 관리자 쓰기, 실제 PIN Excel/Drive 처리와 실기기 갤러리는 검수하지 않았다.
