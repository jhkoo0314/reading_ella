# Rebuild v1 Architecture

## 1. 한 눈에 보는 구조

이 프로젝트는 크게 4개 영역으로 나눈다.

- Python scripts: 운영자용 문제 제작 도구
- Content files: 문제 / 번역 자산
- FastAPI: 학생용 백엔드
- Next.js: 학생용 프론트엔드

쉽게 말하면:
Python은 문제를 준비하고,
콘텐츠 파일은 학습 재료를 담고,
FastAPI는 채점과 저장 및 선택적 API 연결을 담당하고,
Next.js는 문제를 보여준다.

## 2. 전체 구성

```text
운영자
  -> Python scripts
  -> packs/*.json 생성 및 검증
  -> translations/*.json 생성 및 검증

학생
  -> Next.js frontend
  -> 문제 조회 / 답 선택 / 제출 / 번역 / TTS

Next.js frontend
  -> FastAPI backend 호출

FastAPI backend
  -> packs/*.json 읽기
  -> translations/*.json 읽기
  -> 채점
  -> SQLite 저장
  -> 오답 / 팔로업 조회
  -> 선택적 외부 번역 / 오답 해석 / TTS API 호출
  -> Gemini 모델 라우팅
```

## 3. 왜 이렇게 나누는가

이 구조를 추천하는 이유는 아래와 같다.

- Python 문제 제작 흐름을 그대로 살릴 수 있다
- 채점, 오답정리, 팔로업 처리를 백엔드에서 일관되게 할 수 있다
- 문제 원본은 JSON이라 관리가 쉽다
- 번역 자산도 JSON이라 수동 검수와 수정이 쉽다
- 학생 기록은 SQLite라 조회와 정리가 쉽다
- 외부 API 없이도 기본 운영이 가능하다
- 외부 API를 쓰더라도 토글 기반으로 제한할 수 있다

## 4. Python scripts 영역

## 4.1 역할

Python scripts는 운영 도구다.

담당 기능:

- 새 pack 템플릿 생성
- pack 형식 검사
- 여러 pack 일괄 검사
- 번역 템플릿 생성
- 로컬 번역 초안 일괄 생성
- 번역 오버레이 구조 검사

## 4.2 권장 스크립트

- `scripts/create_pack.py`
- `scripts/validate_packs.py`
- `scripts/create_translation_template.py`
- `scripts/generate_local_translations.py`
- `scripts/validate_translations.py`

## 4.3 Python scripts가 하지 않는 것

- 학생 화면 렌더링
- 학생 기록 저장 API 운영
- 프론트엔드 상태 관리

## 5. Content files 영역

## 5.1 역할

콘텐츠 파일은 학습 재료를 저장하는 영역이다.

구성:

- `packs/*.json`: 영어 원본 문제
- `translations/{lang}/*.json`: 선택형 번역 오버레이

## 5.2 원칙

- 원본 문제와 번역은 분리 저장한다
- 번역은 부분적으로만 채워져 있어도 된다
- API로 만든 번역도 최종적으로는 파일로 남길 수 있어야 한다

## 6. FastAPI 영역

## 6.1 역할

FastAPI는 학생이 실제로 호출하는 백엔드다.

담당 기능:

- 문제 로드 API
- 제출 채점 API
- 시도 기록 저장
- 오답 기록 저장
- 팔로업용 조회 API
- 번역 오버레이 제공 API
- 선택적 외부 번역 API 브리지
- 선택적 외부 오답 해석 API 브리지
- 선택적 외부 TTS API 브리지

## 6.2 권장 내부 구조

```text
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
```

## 6.3 저장 위치

- 문제 원본: `packs/*.json`
- 번역 오버레이: `translations/{lang}/*.json`
- 학생 기록 DB: `backend/data/app.db`

## 6.4 텍스트 보조 모델 라우팅

번역과 오답 해석은 FastAPI가 아래 기준으로 모델을 고른다.

- `gemini-3.1-flash-lite-preview`: v1 기본 번역, 짧은 오답 해설
- `gemini-2.5-flash`: 자세한 오답 해석, 추론형 문항 설명, 팔로업 설명

즉, 프론트가 모델 이름을 직접 결정하기보다,
FastAPI가 요청 목적에 맞게 모델을 나누는 구조를 권장한다.

## 7. Next.js 영역

## 7.1 역할

Next.js는 학생이 쓰는 웹 화면이다.

담당 기능:

- 시작 화면
- 난이도 선택
- 지문 / 문항 표시
- 답 상태 관리
- 제출 처리
- 결과 표시
- 번역 열기 / 닫기
- TTS 재생 / 정지
- API 사용 토글

## 7.2 실행 패키지

프론트엔드 패키지 매니저는 `pnpm` 고정이다.

권장 실행 예:

```bash
pnpm install
pnpm dev
pnpm build
pnpm lint
```

## 8. 데이터 흐름

## 8.1 문제 제작 흐름

1. 운영자가 Python으로 새 문제 파일 생성
2. 운영자가 내용 수동 작성
3. Python 검증 스크립트 실행
4. 통과한 파일을 `packs/`에 저장
5. 필요하면 번역 오버레이를 수동 작성하거나 보조 생성
6. 번역 파일도 검증 후 `translations/`에 저장

## 8.2 학생 풀이 흐름

1. 학생이 웹에 접속
2. Next.js가 FastAPI에 문제 요청
3. FastAPI가 `packs/*.json`에서 문제를 읽음
4. 필요하면 번역 오버레이도 함께 읽음
5. 화면에 지문과 6문항 표시
6. 학생이 답 선택
7. 학생이 필요하면 번역이나 TTS를 선택적으로 사용
8. 제출
9. FastAPI가 채점
10. SQLite에 기록 저장
11. 결과 화면 표시
12. 학생이 필요하면 오답 해석을 요청

## 8.3 보조 기능 흐름

### 번역

1. 학생이 번역 버튼을 누른다
2. 프론트는 로컬 번역이 있는지 확인한다
3. 있으면 바로 보여준다
4. 없고 API 토글이 OFF면 "번역 없음" 상태를 보여준다
5. 없고 API 토글이 ON이면 FastAPI가 목적에 맞는 Gemini 모델을 골라 외부 API를 호출할 수 있다
6. 결과는 캐시 또는 파일 반영 대상으로 남길 수 있다

### 오답 해석

1. 학생이 결과 화면에서 오답 해석 버튼을 누른다
2. 프론트는 pack의 `rationale` 또는 저장된 해설이 있는지 먼저 본다
3. 있으면 로컬 해설을 먼저 보여준다
4. 없고 API 토글이 OFF면 "추가 해설 없음" 상태를 보여준다
5. 없고 API 토글이 ON이면 FastAPI가 설명 길이에 맞는 Gemini 모델을 골라 호출한다
6. 짧은 해설은 `gemini-3.1-flash-lite-preview`를 우선 사용한다
7. 자세한 해설은 `gemini-2.5-flash`를 우선 사용한다

### TTS

1. 학생이 읽기 버튼을 누른다
2. 기본값은 브라우저 TTS를 사용한다
3. 학생이 API TTS 토글을 직접 켠 경우에만 외부 TTS를 사용할 수 있다

## 9. 채점 위치

1차에서는 채점과 보조 기능 연결을 FastAPI 백엔드에서 처리한다.

이유:

- 채점 규칙을 한 곳에서 통제할 수 있다
- 오답과 팔로업 데이터를 바로 저장할 수 있다
- 브라우저에 정답 데이터를 불필요하게 많이 노출하지 않아도 된다
- 외부 API 키를 프론트에 노출하지 않아도 된다

단, 채점 규칙은 반드시 결정적이어야 한다.
즉, 같은 답이면 항상 같은 결과가 나와야 한다.

## 10. 저장소 정책

### 문제 파일

- 위치: `packs/*.json`
- 수정 주체: 운영자

### 학생 기록

- 위치: SQLite
- 생성 주체: FastAPI

### 번역 파일

- 위치: `translations/*.json`
- 선택 기능
- 수정 주체: 운영자 또는 승인된 API 캐시 결과

## 11. 외부 API 정책

기본 구조에는 외부 유료 API가 없다.

허용:

- 운영자가 수동으로 문제 초안 생성할 때
- 운영자가 수동으로 번역 초안 생성할 때
- 학생이 프론트 토글을 켠 뒤 번역, 오답 해석, 또는 고품질 TTS를 요청할 때

금지:

- 학생이 문제를 푸는 순간
- 제출할 때 자동으로 외부 API를 붙이는 것
- 페이지 진입 시 자동 호출
- 토글 OFF 상태에서 외부 API 호출

## 12. 배포 관점 메모

1차는 아래 환경을 전제로 한다.

- 로컬 개발 환경
- 파일 읽기와 DB 쓰기가 가능한 단일 서버 환경

즉:

- FastAPI는 `packs/*.json`을 읽을 수 있어야 한다
- FastAPI는 `translations/*.json`을 읽을 수 있어야 한다
- FastAPI는 SQLite 파일에 쓸 수 있어야 한다
- 외부 API를 쓸 경우에도 키는 백엔드 환경변수로만 관리해야 한다

향후 트래픽이나 사용자 수가 늘면 DB만 교체하면 된다.
하지만 1차에서는 SQLite로 충분하다.
