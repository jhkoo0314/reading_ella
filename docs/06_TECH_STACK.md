# Rebuild v1 Tech Stack

## 1. 문서 목적

이 문서는 새 폴더에서 프로젝트를 다시 만들 때,
"정확히 어떤 기술을 쓰는가"를 한 번에 확인하기 위한 문서다.

쉽게 말하면:
기술 선택표다.

## 2. 핵심 기술 요약

이번 리빌드 1차의 핵심 기술스택은 아래와 같다.

- 프론트엔드: Next.js
- UI 라이브러리: React
- 프론트 언어: TypeScript
- 프론트 패키지 매니저: `pnpm`
- 백엔드 프레임워크: FastAPI
- 백엔드 언어: Python 3.11+
- 문제 원본 저장: JSON 파일
- 번역 오버레이 저장: JSON 파일
- 학습 기록 저장: SQLite
- 실시간 외부 유료 API: 기본 OFF
- 선택형 외부 보조 API: 토글 기반 사용
- 텍스트 보조 모델: `gemini-3.1-flash-lite-preview`, `gemini-2.5-flash`

## 3. 프론트엔드 스택

## 3.1 Next.js

학생이 실제로 사용하는 웹 화면은 Next.js로 만든다.

선정 이유:

- React 기반이라 화면 구성이 유연하다
- 파일 기반 라우팅이 편하다
- 학생용 웹 UI를 빠르게 만들기 좋다

## 3.2 React

Next.js 내부 UI 구성은 React로 한다.

선정 이유:

- 문제 화면 상태 관리가 쉽다
- 컴포넌트 단위로 화면 분리가 쉽다
- 이후 확장성이 좋다

## 3.3 TypeScript

프론트엔드 코드는 TypeScript로 작성한다.

선정 이유:

- API 응답 구조를 코드에서 명확히 표현할 수 있다
- 데이터 형식 실수를 줄일 수 있다
- 나중에 유지보수할 때 안전하다

## 3.4 pnpm

프론트엔드 패키지 매니저는 `pnpm`으로 고정한다.

이 프로젝트 문서에서 프론트 실행 예시는 전부 `pnpm` 기준으로 작성한다.

권장 명령:

```bash
pnpm install
pnpm dev
pnpm build
pnpm lint
```

초기 앱 생성 예:

```bash
pnpm dlx create-next-app@latest frontend --ts --eslint --app --src-dir false --import-alias "@/*"
```

`npm`, `yarn` 기준 문서는 만들지 않는다.

## 4. 백엔드 스택

## 4.1 FastAPI

학생용 백엔드는 FastAPI로 만든다.

선정 이유:

- Python 로직 재사용이 쉽다
- 채점 API와 저장 API를 간단하게 만들 수 있다
- 오답정리와 팔로업 기능을 붙이기 쉽다
- 1인 운영에도 과하지 않은 구조다

## 4.2 Python 3.11+

FastAPI와 운영 스크립트는 Python 3.11+로 작성한다.

선정 이유:

- 현재 프로젝트 자산과 연결하기 좋다
- JSON 파일 처리와 검증에 적합하다
- 빠르게 스크립트를 만들기 쉽다

## 4.3 Python의 역할

Python은 아래 역할을 맡는다.

- 새 pack 템플릿 생성
- pack 검증
- FastAPI 백엔드 구현
- 번역 템플릿 생성

## 5. 저장 스택

## 5.1 JSON 파일 저장

문제 원본과 번역 자산은 JSON 파일로 저장한다.

- 문제 파일: `packs/*.json`
- 번역 파일: `translations/*.json`

선정 이유:

- 운영자가 직접 보고 수정할 수 있다
- 버전 관리가 쉽다
- 문제 제작 흐름이 단순하다

## 5.2 SQLite

학생 기록은 SQLite에 저장한다.

- 시도 기록
- 문항별 정오답
- 오답 목록
- 팔로업 대상

선정 이유:

- 별도 DB 서버가 필요 없다
- 파일 하나로 관리 가능하다
- 검색과 집계가 JSON 파일보다 쉽다
- 1인 운영 규모에 충분하다

## 6. 보조 학습 기능 스택

## 6.1 기본 TTS

기본 TTS는 브라우저의 내장 TTS 기능을 우선 사용한다.

선정 이유:

- 추가 비용이 없다
- 구현이 가볍다
- 기본 읽기 기능으로 충분하다

## 6.2 선택형 외부 TTS

필요하면 FastAPI를 통해 외부 TTS API를 붙일 수 있다.

원칙:

- 기본값은 OFF
- 프론트엔드 토글로만 ON 가능
- API 키는 백엔드 환경변수에만 둔다

## 6.3 번역 방식

번역은 아래 우선순위를 권장한다.

1. 수동 번역 JSON
2. 캐시된 API 번역
3. 사용자가 직접 요청한 실시간 API 번역

즉, 가능한 한 로컬 자산을 먼저 쓰고, 없을 때만 API를 쓴다.

## 6.4 텍스트 보조 모델

번역과 오답 해석에 쓰는 텍스트 모델은 아래 2개를 기준으로 한다.

- `gemini-3.1-flash-lite-preview`: 기본 번역과 짧은 해설용
- `gemini-2.5-flash`: 더 자세한 해설용

권장 역할:

- `gemini-3.1-flash-lite-preview`: 기본 번역, 짧은 문항 번역, 한 줄 오답 힌트
- `gemini-2.5-flash`: 추론형 문항 해설, 긴 오답 해석, 팔로업용 설명

중요:

- 이 2개는 텍스트 생성 / 해석용 모델이다
- TTS 음성 출력은 브라우저 TTS 또는 별도 TTS API가 맡는다
- 실제 모델 선택은 프론트가 아니라 FastAPI가 맡는다

## 6.5 시간 기록 규칙

결과 저장 시간은 ISO8601 `+09:00` 형식으로 기록한다.

예:

```text
2026-03-01T17:15:33+09:00
```

## 7. 서버 처리 원칙

1차에서는 FastAPI가 아래 작업을 처리한다.

- `packs/*.json` 읽기
- `translations/*.json` 읽기
- 제출 답안 채점
- SQLite 저장
- 오답 / 팔로업 조회
- 선택적 외부 번역 API 호출
- 선택적 외부 오답 해석 API 호출
- 선택적 외부 TTS API 호출

이유:

- 채점 규칙을 한 곳에서 유지하기 위해
- 오답과 팔로업 데이터를 누적하기 위해
- 프론트엔드는 화면에 집중하게 하기 위해
- 외부 API 키를 프론트에 두지 않기 위해

## 8. 테스트 / 검증 권장안

1차에서 권장하는 방향은 아래와 같다.

- Python / FastAPI 검증: `pytest`
- 프론트 정적 검사: `pnpm lint`
- 프론트 타입 검사: TypeScript 기본 검사
- API 토글 ON/OFF 동작 검사

추후 필요하면 아래를 추가할 수 있다.

- UI 테스트
- e2e 테스트

## 9. 스타일링 정책

1차에서는 스타일링 기술을 과하게 복잡하게 잡지 않는다.

권장 방향:

- Next.js 기본 CSS 또는 단순한 전역 CSS부터 시작
- 필요하면 이후 Tailwind CSS 도입 검토

즉, 처음부터 디자인 시스템을 크게 만들지 않는다.
먼저 동작이 우선이다.

## 10. 외부 API 정책

이번 기술스택의 중요한 원칙은
"학생이 문제를 풀 때 외부 유료 API가 자동으로 켜지지 않는다"는 것이다.

### 기본 금지

- 실시간 문제 생성 API
- 실시간 채점 API
- 페이지 진입 시 자동 외부 API 호출
- 제출 시 외부 API 호출
- 토글 OFF 상태에서 번역 / 오답 해석 / TTS 외부 API 호출

### 제한적 허용

- 운영자가 문제 초안을 수동으로 만들 때
- 운영자가 번역 초안을 수동으로 만들 때
- 학생이 번역, 오답 해석, 또는 고품질 TTS를 직접 요청했을 때

단, 이 경우에도 자동 운영이 아니라 수동 보조여야 한다.

## 11. 배포 전제

1차는 아래 환경을 전제로 한다.

- 로컬 개발 환경
- 파일 읽기와 SQLite 쓰기가 가능한 단일 서버 환경

즉:

- FastAPI는 `packs/*.json`을 읽을 수 있어야 한다
- FastAPI는 `translations/*.json`을 읽을 수 있어야 한다
- FastAPI는 SQLite 파일에 쓸 수 있어야 한다
- 외부 API를 쓸 경우에도 키는 백엔드 환경변수로 관리해야 한다

향후 사용자가 늘면 SQLite를 다른 DB로 교체할 수 있다.
하지만 1차에서는 SQLite로 충분하다.

## 12. 최종 기술스택 표

```text
Frontend Framework: Next.js
UI Library: React
Frontend Language: TypeScript
Package Manager: pnpm
Backend Framework: FastAPI
Backend Language: Python 3.11+
Content Storage: JSON files
Translation Storage: JSON files
Learner Data Storage: SQLite
Default TTS: Browser Web Speech
Optional Assist API: Manual toggle only
Assist Models: gemini-3.1-flash-lite-preview / gemini-2.5-flash
```
