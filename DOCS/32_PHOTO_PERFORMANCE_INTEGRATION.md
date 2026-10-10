# 사진 업로드·조회 성능 연동

프런트 구현 기준: `dev`의 `fe09fa7592e03b30e79068633b99125f07c6cb3f`([PR #208](https://github.com/makee-ham/room-management-system/pull/208)), [프런트 #206](https://github.com/makee-ham/room-management-system/issues/206). 아래 합성 성능 비교의 과거 기준은 계속 `314f0d7`이다.
2026-10-09 최신 확인: [백엔드 PR #412](https://github.com/wrongstory/room-management-system-backend/pull/412)는 `dev`에 병합됐고, [릴리스 PR #426](https://github.com/wrongstory/room-management-system-backend/pull/426)을 거쳐 **v0.9.2 / 운영 API 43**에 반영됐다. 운영 source는 `32c100ea3f1eecbd43ebc900feafdb6af63173c2`다. 백엔드 배포 완료와 프런트 옵션 활성화·실사용 점검 완료는 구분한다.

계약 정본: 해당 운영 commit의 [사진 응답·시간 계측 계약](https://github.com/wrongstory/room-management-system-backend/blob/32c100ea3f1eecbd43ebc900feafdb6af63173c2/docs/PHOTO_PERFORMANCE_409.md), [미완료 operation nullable 계약](https://github.com/wrongstory/room-management-system-backend/blob/32c100ea3f1eecbd43ebc900feafdb6af63173c2/docs/PHOTO_OPERATION_NULLABILITY_410.md), [운영 Swagger](https://wrongstory.github.io/room-management-system-backend/). 실제 배포 증거와 한계는 [v0.9.2 릴리스 기록](https://github.com/wrongstory/room-management-system-backend/releases/tag/v0.9.2)과 [백엔드 인계 댓글](https://github.com/makee-ham/room-management-system/issues/206#issuecomment-6080543398)을 따른다.

## 백엔드 운영 반영 확인

- 두 업로드 POST의 선택 `includePhotoSlots=true`, 응답 snapshot/null fallback 및 인증된 사진 성공 응답의 `Server-Timing`이 배포됐다. 기존 요청의 권한·CAS·멱등성·no-store·보존 정책은 유지된다.
- `reserved`/`reconciliation_pending` operation의 `retentionPolicy`·`mediaAvailability`는 둘 다 null 또는 둘 다 기존 enum이다. `provider_succeeded`/`accepted`/`compensation_pending`/`compensated`는 기존 enum 필수이며 공통 사진 item은 non-null이다. null을 삭제·만료·저장 완료로 해석하지 않는다.
- 운영 OpenAPI와 게시 Swagger의 paths/components 일치, 150 paths / 162 operations 확인. 게시 명세 SHA256은 `b1ab571818063e07964f139fa10a2225f93ba3945a98e303784b4b8bf22a6eff`다. OpenAPI API 버전 `0.6.0`은 앱 릴리스 `v0.9.2`와 별개다.
- 백엔드 Node 2,713 tests, 독립 코드 QA 295 tests, Edge/Python 및 릴리스 필수 CI PASS. 배포 후 공개 GET/OPTIONS와 독립 QA에서 health 200, 허용 Origin preflight 204, 비허용 Origin 403, 인증 없는 보호 조회 401/no-store 및 새 명세를 확인했다.
- 위 항목은 2026-10-09 배포 checkpoint다. 당시 실제 사진 UAT는 미실행이었으며, 다음 절의 2026-10-10 정상 UAT로 확인 범위를 갱신한다. 공개 점검이나 fixture 검증을 실제 업로드 성공으로 간주하지 않는다.

## 2026-10-10 지정 계정 정상 UAT

프런트 `dev 7f04adc`와 동일한 운영 HTML에서 사용자가 직접 5장 다중 선택 후 1장을 추가했다. 인앱 브라우저 제어 도구로 현재 탭의 runtime 응답에만 `photoUploadSnapshot=true`를 일회성 적용했다. 이 UAT 당시에는 배포 설정·소스·인증·API 응답을 변경하지 않았고 전체 운영/프리뷰 옵션은 false였다. 이후 사용자가 전체 적용을 지시해 아래 전역 활성화를 별도로 완료했다.

- 6개 POST 모두 `includePhotoSlots=true`, HTTP 200, 등록 완료. 배치별 시작 전 슬롯 GET 1회 이후 업로드 사이/직후 재조회가 없어 유효 snapshot 경로 작동을 확인했다.
- 다른 화면을 거쳐 돌아온 뒤 인증 content GET 6건과 저장본 6장의 디코딩을 확인했다. 확대, Escape, 확대에서 브라우저 뒤로가기와 사진 유지도 확인했다. 확대를 닫을 때 추가 content 요청은 없었다. 일시 계측을 제거하고 일반 설정으로 새로고침한 뒤에도 6장 디코딩을 확인했다. 검수 제출·승인·삭제는 실행하지 않았다.
- 추가 1장 성공 응답에서 브라우저 JS로 `Server-Timing` 및 `Cache-Control: no-store`를 읽었다. 계측은 현재 탭 메모리의 시간·바이트 수·상태·timing 헤더만 사용하고 종료 후 제거했다. 사진·파일명·개인정보·인증값·업무 식별자는 증거에 기록하지 않았다.

| 측정 | 결과 | 해석 범위 |
| --- | --- | --- |
| 첫 5장 POST 각각 | 10.703 / 6.654 / 6.442 / 6.141 / 5.935초 | Resource Timing 요청 시간 |
| 첫 POST 시작부터 5장 완료 | 35.893초 | 선행 슬롯 GET 포함 37.503초. 파일 선택·준비·렌더 전체 시간은 아님 |
| POST 사이 공백 합계 | 약 18ms | 프런트 큐 대기가 주요 병목이라는 근거 없음 |
| 추가 1장 | 493,071 bytes, 약 10.58초 | 별도 선택 배치, 동일 사진 반복 벤치마크 아님 |
| 추가 1장 서버 timing | DB 4128.2 / Drive 4491.5 / body 9.9 / decoder init 140.2 / decode 489.3 / photo total 9263.8 / API total 9851.5ms | 포함 관계의 total을 세부 구간에 다시 더하지 않음 |
| 재조회 6장 | 요청당 2.156~2.443초, 첫 응답 2.156초, 전체 약 4.647초 | 최대 4개 동시 조회, 전체 화면 렌더 시점과 구분 |

이 표본에서는 서버 `api_total`이 추가 1장 요청의 약 93%다. 추가 압축만으로 해결된다고 판단하지 않는다. DB 세부 왕복/잠금/최종 확정·snapshot과 Drive 폴더/토큰/업로드 단계 계측, 권한·보존 연계 작은 썸네일, 안전한 병렬 계약을 [백엔드 #411 실측 인계](https://github.com/wrongstory/room-management-system-backend/issues/411#issuecomment-6095870502)에 요청했다. [프런트 #206 결과](https://github.com/makee-ham/room-management-system/issues/206#issuecomment-6095868309)에도 같은 근거와 한계를 기록했다.

정상 UAT 통과와 체감 속도 개선 완료는 별개다. 실제 모바일 갤러리/HEIC/20장/저속망, 실제 null·409·응답 유실 복구는 이번 UAT에서 **NOT RUN**이다. 실패는 운영에 강제로 유발하지 않았고 기존 fixture 회귀와 구분한다.

## 2026-10-10 운영·프리뷰 전체 적용

사용자의 전체 적용 지시에 따라 `RMS_PHOTO_UPLOAD_SNAPSHOT=true`를 Vercel Production·Preview 환경에 저장하고 두 채널을 다시 빌드·배포했다. 빌더 기본값과 `.env.example`도 true로 바꾸어 이후 배포에서 누락으로 꺼지지 않게 했다. 명시적인 false 환경값은 계속 우선하며, 앱은 runtime flag가 없으면 기존 조회 방식으로 동작한다.

- Production `dpl_6ETg12p2mjZQ3Kse8eBMyvQs8v1n`: 고정 운영 주소에서 live/production/local 및 snapshot true 확인.
- Preview `dpl_AbqkYLb5GSzRPraMnULknm599fQc`: 고정 프리뷰 주소에서 인증 CLI로 live/preview/session 및 snapshot true 확인. 기존 배포 보호 302 유지.
- 두 산출물의 HTML·worker는 기존 정본과 동일하다. Preview HTML의 Vercel feedback script 하나만 제외하고 비교했다. API/DB·사진 원문·검수 상태·동시성·권한·보존 정책은 변경하지 않았다.
- 배포 후 인앱 화면을 일반 새로고침하여 저장된 6장 디코딩, 확대, 브라우저 Back과 포커스 복귀, console warning/error 없음 확인. 추가 사진 업로드·제출·삭제는 실행하지 않았다.
- `check-photo-rollout.mjs`는 격리된 임시 fixture에서 양 채널 기본 true, 명시적 false 롤백, 환경 우선순위와 demo 분리를 검증한다. 사진 1/5/20장·실패 복구·4개 폭 합성 회귀와 기존 청소 30그룹도 통과했다.

열려 있는 다른 기기에는 다음 앱 진입 또는 새로고침부터 적용된다. 메모리 업로드 큐가 진행 중일 때는 새로고침하지 않는다. 서버 DB·Drive 성능 개선은 별도 백엔드 작업이며 이 전역 활성화를 서버 지연 해결로 표시하지 않는다. 상세 증거·미실행 범위는 `WIREFRAME/QA.md`를 따른다.

## 2026-10-10 전송 중 다른 업무 처리

사용자 요청으로 앱 내부 업무 이동과 여러 객실 추가 선택을 검토했다. 큐는 이미 앱 전체에서 1건씩 전송하며 내부 내비게이션과 분리돼 있었지만, 다른 객실 시작/현장 완료 후의 오래된 photo-slots 조회가 새 저장 응답을 덮는 경합과 큐 종료의 전체 화면 재렌더링을 발견했다.

- 같은 attempt/assignment/revision/slot의 단조 증가 revision만 비교해 늦은 조회의 역행을 막는다. 더 최신 삭제, 같은 revision의 만료/보존 metadata, 다른 담당/수행 범위는 과거 사진으로 덮지 않는다.
- 선택 즉시 메모리 큐 접수와 `사진 N장 전송 대기`를 표시한다. 서버 저장 접수나 완료로 표시하지 않는다. 기존 상단 연결 표시 영역에서 전체 남은 장수/확인 필요를 갱신하고, 사진 영역과 해당 객실 버튼만 갱신한다.
- 다른 객실 시작·현장 완료, 여러 객실 다중 선택, 내부 이동 중 계속 전송한다. 한 슬롯 실패는 해당 슬롯만 대기시키며 다른 객실은 진행한다. 재시도는 기존 key/bytes/경로를 사용한다. 전송은 계속 앱 전체 1건이다.
- 해당 수행에 전송·확인 대기가 하나라도 남으면 검수 제출 버튼과 명령 모두 차단한다. 실제 서버 verified 응답 후 활성화하며 자동 제출하지 않는다.
- 앱 열린 상태의 내부 이동만 대상으로 한다. OS가 앱을 중지/종료하거나 새로고침·로그아웃하면 메모리 큐의 완료/복구를 보장하지 않는다. Service Worker·IndexedDB·브라우저 저장소에 사진을 보관하지 않는다. 진행 중 앱을 새로고침하지 않는다.

`check-photo-queue-handoff.mjs`에서 변경 전 dev의 늦은 조회 경합을 재현했고 변경 후 두 객실 업무 전환·4장 연속 추가·입력 노드/선택 영역/커서 유지·다른 객실 실패 격리·제출 차단·revision 범위·4개 화면 폭을 합성 API로 검증했다. 평상시 390px 화면은 변경 전후 PNG byte 동일하다. 실제 운영 데이터를 추가하거나 삭제하지 않았으며 휴대폰 OS 백그라운드 실행 보장이나 서버 전송 시간 개선으로 해석하지 않는다. 배포와 세부 회귀 결과는 `WIREFRAME/QA.md`를 따른다.

## 현재 제공

2026-10-09 후속 프런트: 인계 PR #209를 dev에 병합하고 운영 OpenAPI와 게시 paths/components 일치를 재확인했다. `cleaning-api.d.ts`의 nullable 보존 필드·선택 snapshot을 재생성하고 생성기 계약 검사와 null operation 회귀 fixture를 보강했다. 2026-10-10 정상 UAT와 전역 활성화는 위 절을 따른다. 병행한 가능일·주급 조회 개선은 [문서 33](33_DATA_PERFORMANCE_INTEGRATION.md)에 분리했다.

- 기존 청소 사진 섹션·촬영/갤러리·완료/검수 요청 위치 유지. 일반 사진 1~20장, 갤러리 다중 선택과 한도 내 추가, 폭탄방·특이사항 별도 유지.
- 선택한 JPEG/WebP는 메모리 Blob URL로 즉시 미리보기. HEIC 디코딩 불가 시 준비 상태를 표시하고 서버 확인 뒤 인증 content로 조회. 선택 사진을 등록 완료로 간주하지 않는다.
- 현재 사진 전송 중 다음 1장만 미리 준비한다. 기존 1920px/JPEG .82의 더 작은 결과만 사용하며 같은 앱의 전송은 계속 1건씩이다. 실패 재시도는 원 요청의 key·경로·revision·Blob bytes를 보존한다.
- 진행률은 선택 배치의 완료/전체 누적값이다. 업로드 중 추가 선택도 합산한다. 사진별 재시도와 슬롯 단위 대기 취소를 제공한다.
- accepted 뒤 확인 GET 실패는 파일 업로드 실패와 구분한다. 재시도는 조회만 수행한다. 미완료 operation은 `/v1/photo-uploads/{operationId}`로 확인하며 새 key로 재업로드하지 않는다.
- 사진 content는 기존 인증/no-store 조회를 유지한다. 현재 화면에서 보이는 사진부터 최대 4개씩 조회하며 완료된 이미지 노드와 검수 버튼 상태만 갱신한다. 업로드 진행도 해당 사진 섹션을 갱신하고 완료 시 제출 버튼을 갱신한다.
- 내부 화면 이동 중 큐는 계속되지만 preview URL은 해제한다. 로그아웃/권한 세대 변경 시 파일·URL을 해제하고 늦은 준비/조회 결과는 반영하지 않는다. 종료 후 복구나 백그라운드 업로드 보장은 없다.

## 활성화 옵션과 롤백

빌드 환경값 `RMS_PHOTO_UPLOAD_SNAPSHOT=true`를 주면 runtime `featureFlags.photoUploadSnapshot`을 켠다. 현재 빌더 기본값과 두 배포 환경값은 **true**다. 구버전 API는 알 수 없는 query를 거부하므로 구버전으로 롤백하기 전에 양 채널 환경값을 false로 바꾸고 `RMS_PHOTO_UPLOAD_SNAPSHOT=false`로 재빌드·배포한다. 환경값 변경만으로 기존 정적 산출물이 바뀌지는 않는다. 새 runtime 응답에서 false를 확인하고 사용 중 문서도 전송 종료 후 새로 열어야 한다.

1. 일반/collection upload POST에만 `includePhotoSlots=true`를 추가한다. false/빈 값은 보내지 않는다.
2. accepted 응답의 `photoSlots`가 attempt/assignment/revision과 일치하고, 대상 photo/item의 verified 상태 및 최신 collection/item revision을 확인하면 후속 GET을 생략한다.
3. null·누락·불일치는 기존 photo-slots GET으로 확인한다. GET 실패 때도 accepted 영수증은 유지한다.
4. snapshot은 별도 조회이므로 다음 CAS가 409일 수 있다. 로컬 성공 전이나 병렬 POST로 우회하지 않는다.
5. 롤백은 false로 재빌드·배포한다. 이미 진행한 요청은 동일 key/bytes 계약을 유지한다.

프런트 확인 및 후속:

1. 완료: 운영 Swagger 기준 nullable 타입과 snapshot 응답 처리 대조.
2. 정상 경로 완료: 지정 테스트 계정/객실의 실제 업로드와 accepted snapshot. 실제 null fallback·동일 key/bytes 재시도는 미검증이며 fixture 결과와 구분한다.
3. 완료: 허용 Origin의 인증된 사진 **성공** 응답에서 CORS `Server-Timing` 노출 확인. 오류/anonymous 401에는 timing 헤더를 요구하지 않는다.
4. 전역 옵션 활성화 완료: 결과는 #206과 `WIREFRAME/QA.md`에 기록한다. 실제 모바일 1/5/20장 실측은 남아 있다. 전역 업로드 1건·조회 최대 4건 상한은 그대로 유지한다.

2026-10-10 운영 사진 쓰기는 사용자가 지정한 테스트 대상에 직접 수행했다. 현재 탭에 한정한 UAT와 이후 전체 배포 활성화를 별도 기록하며, 이번 활성화 후 새 운영 쓰기를 다시 수행했다고 표시하지 않는다.

`Server-Timing`의 `photo_db/body/decoder_init/decode/drive/total`은 인증 후 서버 구간이다. 브라우저 준비/전송/렌더 시간과 같지 않으며 이번 프런트는 사진·개인정보가 포함된 계측 로그를 추가하지 않았다. private thumbnail 및 안전한 업로드 병렬 계약은 백엔드 #411 후속 범위다.

## 합성 검증 방법과 한계

`scripts/check-photo-performance.mjs`는 `314f0d7`과 현재 HTML, snapshot 활성 fixture를 같은 합성 JPEG로 비교한다. Chromium의 CPU 4배 감속, 준비 80ms/POST 140ms/metadata GET 60ms 지연을 주입한다. 최초 이미지는 `complete && naturalWidth > 0`, 업로드는 큐 종료, 전체 표시는 모든 확인된 이미지 디코딩 완료로 구분한다. 운영 Drive 속도나 실제 스마트폰 개선율이 아니다.

합성 오류/회귀: null·불일치 snapshot, accepted 후 GET 503, 응답 유실, CAS 409, 미완료 operation, 동일 key/bytes, 한도 내 추가와 초과 거부, HEIC 디코딩 불가 원본 fallback, 이동 중 계속 전송, 로그아웃 중 준비/전송, 4개 폭, 보이는 사진 우선·placeholder 크기·키보드 확대/Escape/포커스. 이 합성 검증으로 실제 HEIC codec 지원·iOS/Android 갤러리·OS 앱 종료·물리 저속망·운영 provider 성능을 확인하지 않았다. 실제 운영 표본은 위 2026-10-10 UAT 절로 구분한다.

합성 검증 실행에는 기존 Playwright 환경과 `RMS_QA_ORIGIN` 로컬 서버를 사용한다. 당시 Browser plugin 미제공으로 Playwright를 사용했으며 해당 합성 테스트의 외부 API 쓰기는 전부 fixture로 가로챘다. 수치와 배포 식별자는 `WIREFRAME/QA.md`에 기록한다.
