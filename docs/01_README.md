# Reading ELLA Rebuild v1 README

## 1. 문서 목적

이 문서 세트는 현재 폴더를 직접 고치는 문서가 아니다.
다른 새 폴더에서 프로젝트를 다시 빌드할 때 참고하는 기준 문서다.

이번 리빌드의 핵심 방향은 아래와 같다.

- 최종 제품명: `Reading ELLA`
- 문제 제작과 검수: Python
- 학생용 백엔드: FastAPI
- 학생용 프론트엔드: Next.js / React
- 프론트 패키지 매니저: `pnpm`
- 문제 원본 저장: JSON 파일
- 번역 오버레이 저장: JSON 파일
- 학습 기록 저장: SQLite
- 외부 유료 API: 기본 꺼짐, 필요할 때만 수동 사용
- 선택형 텍스트 보조 모델: `gemini-3.1-flash-lite-preview`, `gemini-2.5-flash`

쉽게 말하면:
운영자는 Python으로 문제를 만들고,
학생은 Next.js 화면에서 문제를 풀고,
필요하면 번역과 TTS를 선택해서 쓰고,
FastAPI가 채점과 기록 저장을 맡는다.

## 2. 목표

이 프로젝트는 영어 리딩 문제를 아주 저비용으로 운영하는 것이 목표다.

- 운영자는 문제를 계속 수동으로 추가할 수 있어야 한다.
- 학생은 웹에서 바로 문제를 풀 수 있어야 한다.
- 학생이 문제를 푸는 중 외부 유료 API가 자동으로 켜지면 안 된다.
- 오답과 팔로업 데이터를 남길 수 있어야 한다.
- 번역과 TTS를 필요할 때만 켤 수 있어야 한다.
- 데이터는 파일과 로컬 DB만 백업해도 보존 가능해야 한다.

## 3. 이번 1차에서 만드는 것

- 리딩 지문 1개 표시
- 객관식 6문항 표시
- 답 선택
- 제출
- 점수 계산
- 오답 저장
- 팔로업용 데이터 저장
- 지문 TTS
- 문항 TTS
- 보기 TTS
- 지문 번역 보기
- 문항 번역 보기
- 보기 번역 보기
- 오답 해석 보기
- 프론트엔드 API 사용 토글

이번 1차에서 만들지 않는 것:

- 로그인
- 결제
- 클라우드 DB
- 사용자 동의 없는 실시간 외부 유료 API 호출
- Writing / Speaking
- 적응형 난이도
- Vocab 확장 탭
- 항상 자동으로 외부 API를 호출하는 모드

## 4. 기술 방향

### Python

Python은 운영 도구와 백엔드 언어로 사용한다.

- 새 문제 파일 생성
- 문제 파일 검증
- 번역 오버레이 템플릿 생성
- FastAPI 백엔드 구현

### FastAPI

FastAPI는 학생용 백엔드다.

- 문제 로드 API
- 채점 API
- 오답 기록 저장
- 팔로업 데이터 저장
- 번역 오버레이 로드
- 선택적 외부 번역 API 호출
- 선택적 외부 오답 해석 API 호출
- 선택적 외부 TTS API 호출
- 번역 / 오답 해석용 모델 라우팅

### Next.js / React

Next.js는 학생용 웹 화면이다.

- 문제 가져오기
- 문제 보여주기
- 답 상태 관리
- 제출 처리
- 결과 표시
- TTS 버튼
- 번역 표시 토글
- API 사용 토글

### pnpm

프론트엔드 실행 패키지는 `pnpm`으로 고정한다.

반드시 문서, 스크립트, 실행 예시는 모두 `pnpm` 기준으로 적는다.

예:

```bash
pnpm install
pnpm dev
pnpm build
pnpm lint
```

`npm`이나 `yarn` 기준으로 문서를 쓰지 않는다.

## 5. 권장 폴더 구조

새 프로젝트는 아래처럼 시작하는 것을 권장한다.

```text
reading-ella/
  packs/
  translations/
    ko/
  scripts/
    create_pack.py
    validate_packs.py
    create_translation_template.py
    generate_local_translations.py
    validate_translations.py
  backend/
    app/
      api/
      db/
      models/
      schemas/
      services/
      main.py
    data/
      app.db
    requirements.txt
  frontend/
    app/
    components/
    lib/
    public/
    package.json
    pnpm-lock.yaml
  docs/
    01_README.md
    02_PRD.md
    03_ARCHITECTURE.md
    04_DATA_CONTRACT.md
    05_BUILD_PLAN.md
    06_TECH_STACK.md
    07_CONTENT_MODEL.md
    08_UX_FLOW.md
    09_SCREEN_SPEC.md
    10_COMPONENT_MAP.md
    11_LEVEL_GUIDE.md
    12_CONTENT_DIFFICULTY_MATRIX.md
    13_LEVEL_PROFILES_SPEC.md
    14_MANUAL_REVIEW_GUIDE.md
    TODO.md
```

## 6. 읽는 순서

새 폴더에서 빌드를 시작할 때는 아래 순서로 읽으면 된다.

1. `01_README.md`
2. `02_PRD.md`
3. `03_ARCHITECTURE.md`
4. `04_DATA_CONTRACT.md`
5. `05_BUILD_PLAN.md`
6. `06_TECH_STACK.md`
7. `07_CONTENT_MODEL.md`
8. `08_UX_FLOW.md`
9. `09_SCREEN_SPEC.md`
10. `10_COMPONENT_MAP.md`
11. `11_LEVEL_GUIDE.md`
12. `12_CONTENT_DIFFICULTY_MATRIX.md`
13. `13_LEVEL_PROFILES_SPEC.md`
14. `14_MANUAL_REVIEW_GUIDE.md`
15. `TODO.md`

## 6.1 구현 역할 분담

프론트엔드 작업은 아래처럼 나눈다.

- 코덱스 CLI: 전체 구조, 페이지 뼈대, 컴포넌트 뼈대, 상태 관리, API 연결, 백엔드 구현
- 안티그래비티: 본격적인 프론트엔드 디자인, 비주얼 완성도, 최종 디자인 구현

중요:

- 코덱스 CLI는 프론트엔드 디자인 작업에서도 먼저 뼈대와 구조만 구현한다
- 최종 디자인 감도와 화면 완성도는 안티그래비티에서 구현한다

## 7. 실행 원칙

- 프론트엔드 개발 서버는 `pnpm dev`
- 프론트엔드 빌드는 `pnpm build`
- 프론트엔드 의존성 설치는 `pnpm install`
- 백엔드는 FastAPI로 실행
- 문제 원본은 `packs/*.json`
- 번역 오버레이는 `translations/*.json`
- 로컬 한국어 번역 초안은 `python scripts/generate_local_translations.py`
- 번역 오버레이 검사는 `python scripts/validate_translations.py translations/ko`
- 학습 기록은 SQLite에 저장
- 백엔드는 `backend/.env`가 있으면 먼저 읽는다
- 기본 TTS는 브라우저 기능을 우선 사용
- 외부 API는 프론트 토글로 명시적으로 켰을 때만 사용
- 번역과 오답 해석 모델은 FastAPI가 선택한다

권장 모델 역할:

- `gemini-3.1-flash-lite-preview`: v1 기본 번역, 짧은 오답 해설
- `gemini-2.5-flash`: 자세한 오답 해석, 더 긴 근거 설명

실제 설정 예시는 [backend/.env.example](/C:/reading_ella/backend/.env.example) 기준으로 보면 된다.
핵심 변수는 `READING_ELLA_ASSIST_MODEL_DEFAULT`, `READING_ELLA_ASSIST_MODEL_DEEP`,
`READING_ELLA_TRANSLATION_PROVIDER`, `READING_ELLA_EXPLANATION_PROVIDER`, `READING_ELLA_TTS_PROVIDER`다.

루트에서 바로 쓰는 빠른 명령은 아래처럼 정리한다.

```bash
pnpm dev
pnpm dev:backend
pnpm packs:generate
pnpm packs:validate
pnpm check:final
```

쉽게 말하면:

- `pnpm packs:generate`: 300세트 실문항 다시 만들기
- `scripts/create_pack.py`는 개별 작성용 `pack 템플릿`을 만들고, `scripts/generate_pack_bank.py`는 실문항 300세트를 일괄 생성한다
- 실문항 생성 로직은 `scripts/content/gt_generator.py`, `scripts/content/s_generator.py`, `scripts/content/mgt_generator.py`로 나뉘어 있다
- 주제와 보기 후보 같은 재료는 `scripts/content/data/*.json`에서 관리한다
- 계획 개수를 늘리고 싶으면 `python scripts/create_pack_bank_plan.py --packs-per-level 120 --force`처럼 개수를 바꿔 새 계획표를 만들 수 있다
- `pnpm packs:validate`: 현재 pack 전체 검사
- `pnpm check:final`: 프론트 빌드 + pack 검사 + 백엔드 통합 점검 한 번에 실행

즉, 역할은 아래처럼 나뉜다.

- Python scripts: 문제 제작
- FastAPI: 채점 / 저장 / 팔로업 기록 / 선택적 보조 API 연결
- Next.js: 문제 풀이 화면 / 번역 / TTS / API 토글
- 코덱스 CLI: 구조 / 코드 / 백엔드 / 프론트 뼈대
- 안티그래비티: 프론트 디자인 구현

## 8. 성공 기준

아래가 되면 1차 빌드 방향이 맞다고 본다.

- 운영자가 Python으로 새 문제를 만들 수 있다
- 검증 스크립트가 문제 형식을 검사할 수 있다
- FastAPI가 문제를 읽고 채점할 수 있다
- Next.js 화면에서 문제를 읽어올 수 있다
- 학생이 6문항을 풀 수 있다
- 제출 후 점수가 맞게 계산된다
- 오답과 팔로업 데이터가 SQLite에 저장된다
- 지문/문항/보기 번역을 선택적으로 볼 수 있다
- 지문/문항/보기를 선택적으로 읽을 수 있다
- 오답 해석을 필요할 때만 요청해서 볼 수 있다
- 외부 API는 토글을 켰을 때만 호출된다
