# 예상 청소시간 선택사항 · 프론트 구현과 운영 활성화 보류

> 역사 기록: 2026-09-16 운영 OpenAPI v0.3.0 연동과 live 플래그 활성화로 이 문서의 `운영 OFF` 판단은 종료됐다. 현재 구현·설정·검증 정본은 `DOCS/23_CLEANING_API_INTEGRATION.md`다. 아래 내용은 당시 보류 근거를 보존하기 위한 기록이며 현재 실행 지침으로 사용하지 않는다.

2026-09-15 현재 사용자 결정이 이 범위의 이전 예상시간 필수 정책보다 우선한다. `FINAL_UX_AUDIT.md` 원문은 수정하지 않는다.

## 구현 계약

- `PublishCleaningTemplateRequest.durationMinutes?: number | null | undefined`, 응답은 `number | null`이다. 생략과 null을 null로 정규화하며 입력한 정수의 1~10080 범위는 유지한다.
- 운영 청소 템플릿 수정 폼은 예상시간을 자동 입력하지 않는다. null은 `미설정(선택사항)`이다. 타입별 필수 사진 슬롯, CAS `expectedVersion`, `Idempotency-Key`를 유지한다. 409 뒤 최신 템플릿을 다시 조회해 재편집한다.
- 예약 등록·변경 요청은 예상시간을 요구하지 않는다. `CLEANING_TEMPLATE_NOT_CONFIGURED`는 게시된 checkout 템플릿이 없는 경우의 설정 안내다. 예약에서 예정 퇴실 청소대상이 생성되는 것은 정상이다.
- 계획 화면은 서버의 `availableFrom`과 `dueAt`만 표시한다. 시작+1분, 임의 종료 예상시각, 로컬 충돌 없음 판정을 만들지 않는다. 수동 추가 청소 요청은 열린 checkout 계획 때문에 차단하지 않으며 새 폼의 업무 마감은 비어 있다.
- 메이드 수행 명령 직전에 배정과 current attempt를 재조회한다. `expectedExecutionVersion`, `expectedAssignmentId`, `expectedAssignmentRevision`을 그대로 보낸다. 시작·완료 결과는 서버 응답으로만 반영한다. PIN 확인은 시작 명령이 아니다.
- 실제 시간은 해당 attempt의 `startedAt → fieldCompletedAt`만 사용한다. 진행 타이머나 중단·재시작 시간 합산은 제공하지 않는다.
- 고객 미퇴실 신고 후 `관리자 확인 대기`로 표시하고 시작·완료·이후 PIN 접근·사진 제출을 차단한다. 표시됐던 PIN을 회수했다는 문구, 분 단위 polling, 예상시간 자동 해제는 없다.
- 신고받은 사건의 opaque ID만 계정별 sessionStorage에 최대 50개 보관한다. 재로드·명시적 새로고침에서 Edge 사건 조회로 차단 상태를 확인하며 조회 실패 시 수행 컨트롤을 잠근다. 개인정보·PIN·사진·명령 payload는 이 저장소에 보관하지 않고 로그아웃·계정 전환 시 지운다.
- 관리자 사건 조회·결정은 최신 사건 version/fingerprint와 예약·배정·수행 영향을 보여준다. 세 결정과 각각의 reasonCode, 연장 시각, 새 담당·순서·서비스일·시작 가능·마감을 보낸다. 409 후 입력과 영향 확인 체크를 초기화하고 재조회한 영향을 다시 확인한다. 자동 덮어쓰기는 없다.
- 안정적인 error code로 안내하고 오류 UI에는 문의 번호만 추가한다. 서버 message·토큰·고객명·전화번호·PIN·요청 본문을 로그에 출력하지 않는다. 업무 데이터는 Edge API만 사용한다.
- 응답 유실·5xx 등 결과 불명 요청은 메모리에 유지한다. 같은 payload와 같은 키로 결과를 확인하기 전 다른 mutation을 차단한다. 결과 확인 뒤 payload 변경에는 새 키를 쓴다. 페이지를 닫으면 이 메모리는 사라지므로 새로 열린 화면은 최신 서버 상태를 다시 읽는다.

## 소스와 운영 계약 구분

백엔드는 `wrongstory/room-management-system-backend`의 PR #166 exact source `84cf863c4152f985eed8c322dc97cb78805f1b12`를 읽었다. GitHub 조회 당시 PR은 MERGED였으나 운영 56번째 migration·API exact source 배포·nullable 반영 완료의 증거로 취급하지 않는다.

`WIREFRAME/cleaning-api.d.ts`는 위 소스의 OpenAPI로 생성한 임시 클라이언트 타입이다. 소스 QA는 109 paths / 117 operations, 요청의 duration 필수 제거, 요청·응답 nullable, 입력 범위 1~10080을 확인했다. 운영 타입 재생성은 아직 하지 않았다.

`featureFlags.optionalCleaningWorkflow`는 런타임 설정에서 명시적인 boolean true만 인정한다. `scripts/serve.py`와 `scripts/build-pages-artifact.mjs`는 **false를 고정 생성**한다. URL·로컬 저장소·화면 토글로 켤 수 없다. 회귀 테스트의 가로챈 설정에서만 켜며 실제 운영 API는 호출하지 않는다. 기존 데모 시나리오와 OFF 상태의 운영 화면은 유지한다.

## 운영 활성화 순서 · 미실행

1. 프론트 구현, 플래그 OFF.
2. PR #166 독립 QA 및 main 병합 확인.
3. 운영 56번째 migration 적용 확인.
4. main exact source API 배포 확인.
5. 운영 정본 `GET /functions/v1/api/openapi.json`, `GET /functions/v1/api/docs`의 109 paths / 117 operations 및 optional/nullable 계약 확인.
6. 운영 OpenAPI로 클라이언트 타입 재생성, 예약/템플릿 smoke, 실제 서버 동시 시작·미퇴실 수행 차단·해결 후 새 담당 smoke.
7. 아래 연동 한계를 해소하고 검증한 후 별도 릴리즈에서 플래그 ON.

운영 배포 후 읽기 검증과 재생성 명령:

```sh
node scripts/generate-cleaning-client.mjs --production --check
node scripts/generate-cleaning-client.mjs --production
```

이 명령은 플래그를 변경하지 않는다. 소스 QA용 생성은 `--source <OpenAPI JSON 파일>`을 사용한다. 기존 `scripts/check-api-integration.mjs`는 현재 OFF 릴리즈의 v0.2.0 계약 검사를 그대로 유지한다. 새 계약 검증은 위 전용 검증기로 분리한다.

## 현재 API / 기존 프론트 연동 한계

- 사건 단건 GET은 사건 ID가 필요하지만 알림 projection의 deepLink는 cleaningTarget ID만 제공한다. 사건 목록이나 target→incident ID 조회 계약도 없다. 관리자 화면은 신고 응답의 사건 번호를 입력해 조회한다. 자동 사건 큐 연결에는 백엔드가 사건 ID를 전달하는 안정적인 계약이 필요하다. groupId나 target ID를 incident ID로 추측하지 않는다.
- 기존 운영 프론트의 PIN 공개·사진 업로드/제출은 별도 연동 대기 상태다. 이 변경은 해당 버튼의 사건 차단 표시를 유지하며 이 기능들을 구현한 것으로 표현하지 않는다.
- 새 탭·다른 기기에서 이미 열린 사건 ID를 알 수 없는 경우, 사전 비활성화는 위 projection 보완이 필요하다. 실제 시작·완료 요청은 서버 409가 최종 차단하며 로컬 성공으로 반영하지 않는다.
- 브라우저 회귀는 가로챈 데모 Edge 응답을 사용했다. 실제 DB 동시성·운영 mutation·migration·도어락·송금·푸시를 검증한 것으로 기록하지 않는다.
