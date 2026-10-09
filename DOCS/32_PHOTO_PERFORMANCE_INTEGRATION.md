# 사진 업로드·조회 성능 연동

작업 기준: 프런트 `dev`의 `314f0d7`, [프런트 #206](https://github.com/makee-ham/room-management-system/issues/206).
2026-10-09 확인: [백엔드 PR #412](https://github.com/wrongstory/room-management-system-backend/pull/412)는 Draft·미병합·운영 미배포다. 계약 정본은 해당 PR의 `5630b62`에 있는 `docs/PHOTO_PERFORMANCE_409.md`다. 프런트 기능과 미배포 API 옵션을 구분한다.

## 현재 제공

- 기존 청소 사진 섹션·촬영/갤러리·완료/검수 요청 위치 유지. 일반 사진 1~20장, 갤러리 다중 선택과 한도 내 추가, 폭탄방·특이사항 별도 유지.
- 선택한 JPEG/WebP는 메모리 Blob URL로 즉시 미리보기. HEIC 디코딩 불가 시 준비 상태를 표시하고 서버 확인 뒤 인증 content로 조회. 선택 사진을 등록 완료로 간주하지 않는다.
- 현재 사진 전송 중 다음 1장만 미리 준비한다. 기존 1920px/JPEG .82의 더 작은 결과만 사용하며 같은 앱의 전송은 계속 1건씩이다. 실패 재시도는 원 요청의 key·경로·revision·Blob bytes를 보존한다.
- 진행률은 선택 배치의 완료/전체 누적값이다. 업로드 중 추가 선택도 합산한다. 사진별 재시도와 슬롯 단위 대기 취소를 제공한다.
- accepted 뒤 확인 GET 실패는 파일 업로드 실패와 구분한다. 재시도는 조회만 수행한다. 미완료 operation은 `/v1/photo-uploads/{operationId}`로 확인하며 새 key로 재업로드하지 않는다.
- 사진 content는 기존 인증/no-store 조회를 유지한다. 현재 화면에서 보이는 사진부터 최대 4개씩 조회하며 완료된 이미지 노드와 검수 버튼 상태만 갱신한다. 업로드 진행도 해당 사진 섹션을 갱신하고 완료 시 제출 버튼을 갱신한다.
- 내부 화면 이동 중 큐는 계속되지만 preview URL은 해제한다. 로그아웃/권한 세대 변경 시 파일·URL을 해제하고 늦은 준비/조회 결과는 반영하지 않는다. 종료 후 복구나 백그라운드 업로드 보장은 없다.

## 백엔드 배포 후 켤 옵션

빌드 환경값 `RMS_PHOTO_UPLOAD_SNAPSHOT=true`를 주면 runtime `featureFlags.photoUploadSnapshot`을 켠다. 기본값은 **false**다. 구버전 API는 알 수 없는 query를 거부하므로 운영 배포 확인 전 켜지 않는다.

1. 일반/collection upload POST에만 `includePhotoSlots=true`를 추가한다. false/빈 값은 보내지 않는다.
2. accepted 응답의 `photoSlots`가 attempt/assignment/revision과 일치하고, 대상 photo/item의 verified 상태 및 최신 collection/item revision을 확인하면 후속 GET을 생략한다.
3. null·누락·불일치는 기존 photo-slots GET으로 확인한다. GET 실패 때도 accepted 영수증은 유지한다.
4. snapshot은 별도 조회이므로 다음 CAS가 409일 수 있다. 로컬 성공 전이나 병렬 POST로 우회하지 않는다.
5. 롤백은 false로 재빌드·배포한다. 이미 진행한 요청은 동일 key/bytes 계약을 유지한다.

활성화 전 백엔드 담당 확인: #412 실제 배포 SHA와 운영 OpenAPI, 옵션을 넣은 accepted/null 응답, CORS `Server-Timing` 노출. 이후 지정 테스트 계정/객실로 운영 UAT를 하고 옵션을 켠다. 사진이 들어간 운영 쓰기를 이 작업에서 임의 실행하지 않았다.

`Server-Timing`의 `photo_db/body/decoder_init/decode/drive/total`은 인증 후 서버 구간이다. 브라우저 준비/전송/렌더 시간과 같지 않으며 이번 프런트는 사진·개인정보가 포함된 계측 로그를 추가하지 않았다. private thumbnail 및 안전한 업로드 병렬 계약은 백엔드 #411 후속 범위다.

## 검증 방법과 한계

`scripts/check-photo-performance.mjs`는 `314f0d7`과 현재 HTML, snapshot 활성 fixture를 같은 합성 JPEG로 비교한다. Chromium의 CPU 4배 감속, 준비 80ms/POST 140ms/metadata GET 60ms 지연을 주입한다. 최초 이미지는 `complete && naturalWidth > 0`, 업로드는 큐 종료, 전체 표시는 모든 확인된 이미지 디코딩 완료로 구분한다. 운영 Drive 속도나 실제 스마트폰 개선율이 아니다.

오류/회귀: null·불일치 snapshot, accepted 후 GET 503, 응답 유실, CAS 409, 미완료 operation, 동일 key/bytes, 한도 내 추가와 초과 거부, HEIC 디코딩 불가 원본 fallback, 이동 중 계속 전송, 로그아웃 중 준비/전송, 4개 폭, 보이는 사진 우선·placeholder 크기·키보드 확대/Escape/포커스. 실제 HEIC codec 지원·iOS/Android 갤러리·OS 앱 종료·물리 저속망·운영 provider 성능은 미검증이다.

실행에는 기존 Playwright 환경과 `RMS_QA_ORIGIN` 로컬 서버를 사용한다. Browser plugin 미제공으로 Playwright를 사용했으며 외부 API 쓰기는 전부 fixture로 가로챘다. 수치와 배포 식별자는 `WIREFRAME/QA.md` 최신 항목에 기록한다.
