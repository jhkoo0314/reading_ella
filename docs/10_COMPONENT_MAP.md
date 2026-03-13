# Rebuild v1 Component Map

## 1. 문서 목적

이 문서는 화면을 실제 React 컴포넌트 단위로 어떻게 나눌지 정하는 문서다.

쉽게 말하면:
무엇을 어떤 조각으로 만들지 정하는 문서다.

## 2. 가장 중요한 역할 분담

이 프로젝트는 프론트엔드 작업을 아래처럼 나눈다.

### 코덱스 CLI 담당

- 전체 폴더 구조
- 페이지 구조
- 컴포넌트 뼈대
- 상태 관리
- API 연결
- 타입 정의
- 데이터 흐름 연결
- 백엔드 구현
- SQLite 연결
- 테스트용 기본 UI

### 안티그래비티 담당

- 프론트엔드 본격 디자인
- 시각 스타일 방향
- 색상 시스템
- 타이포그래피
- 간격과 배치의 최종 정리
- 애니메이션과 인터랙션 감도
- 디자인 완성도 높은 화면 구현

## 2.1 개발자에게 주는 명시적 지시

프론트엔드 구현 시 아래 원칙을 따른다.

- 코덱스 CLI는 디자인 구현이 필요한 화면에서도 먼저 구조와 뼈대만 구현한다
- 코덱스 CLI는 레이아웃, 상태, 데이터 연결, 기본 접근성까지 우선 구현한다
- 코덱스 CLI는 최종 비주얼 디자인을 확정하지 않는다
- 본격적인 프론트엔드 디자인 구현은 안티그래비티에서 담당한다
- 디자인 디테일, 분위기, 비주얼 완성도 조정은 안티그래비티로 넘긴다

쉽게 말하면:

`코덱스 = 작동하는 뼈대`

`안티그래비티 = 완성도 높은 디자인`

## 2.2 코덱스가 프론트에서 해도 되는 것

- 단순한 박스 배치
- 버튼 위치 고정
- 임시 spacing
- 기본 폰트 적용
- 상태별 placeholder UI
- loading / error / empty UI

즉, "보이기 위한 최소 UI"까지는 코덱스가 해도 된다.

## 2.3 코덱스가 프론트에서 깊게 하지 않는 것

- 최종 컬러 시스템 결정
- 브랜드 느낌의 시각 언어
- 고급 애니메이션
- 섬세한 타이포그래피 조정
- 디자인 시스템의 최종 미감
- 화면 분위기를 만드는 디테일

이 부분은 안티그래비티 담당으로 남긴다.

## 3. 페이지 구성 지도

v1 페이지는 아래처럼 나눈다.

```text
app/
  page.tsx                    -> 시작 화면
  solve/[packId]/page.tsx     -> 문제 풀이 화면
  result/[attemptId]/page.tsx -> 결과 화면
  review/page.tsx             -> 복습 화면
```

필요하면 난이도 기반 라우트로 바꿀 수 있지만,
기본 페이지 책임은 위 구조를 권장한다.

## 4. 공통 컴포넌트

공통 컴포넌트는 여러 화면에서 같이 쓰는 조각이다.

### AppShell

역할:

- 화면 바깥 공통 뼈대
- 최대 폭
- 공통 여백

1차 담당:

- 코덱스 CLI가 뼈대 구현
- 안티그래비티가 최종 스타일 고도화

### PageHeader

역할:

- 페이지 제목
- 간단한 설명
- 우측 액션 버튼 영역

### SectionCard

역할:

- 지문, 점수 요약, 오답 카드 같은 블록 공통 컨테이너

### EmptyStateCard

역할:

- 빈 상태 메시지

### ErrorStateCard

역할:

- 오류 메시지

### LoadingBlock

역할:

- 로딩 표시

### ApiStatusBadge

역할:

- `API OFF`
- `API ON`

## 5. 시작 화면 컴포넌트

## 5.1 HomePage

역할:

- 시작 화면 전체 조립

하위 컴포넌트:

- `HeroBlock`
- `DifficultySelector`
- `AssistToggleCard`
- `PrimaryStartButton`
- `ReviewEntryButton`

## 5.2 HeroBlock

역할:

- 서비스 제목
- 한 줄 설명

제목 예시:

- `Reading ELLA`

담당:

- 코덱스 CLI는 텍스트 구조와 기본 배치
- 안티그래비티는 시각적 인상과 레이아웃 완성

## 5.3 DifficultySelector

역할:

- `GT / S / MGT` 선택

상태:

- selected
- unselected

## 5.4 AssistToggleCard

역할:

- API 사용 토글 모음

하위 항목:

- `Use Assist API`
- `Use API Translation`
- `Use API TTS`
- `Use API Explain`

## 5.5 PrimaryStartButton

역할:

- 문제 시작

규칙:

- 난이도 선택 전에는 비활성화

## 5.6 ReviewEntryButton

역할:

- 복습 화면 진입

## 6. 문제 풀이 화면 컴포넌트

## 6.1 SolvePage

역할:

- 문제 풀이 화면 전체 조립

하위 컴포넌트:

- `SolveHeader`
- `PassageSection`
- `QuestionList`
- `StickySubmitBar`
- `SubmitConfirmModal`

## 6.2 SolveHeader

역할:

- 난이도 표시
- pack 제목 표시
- 미응답 수 표시

## 6.3 PassageSection

역할:

- 지문 제목과 본문 표시
- 지문 번역
- 지문 TTS

하위 컴포넌트:

- `PassageBody`
- `TranslationPanel`
- `TtsControls`

## 6.4 QuestionList

역할:

- 6개 문항 렌더링

## 6.5 QuestionCard

역할:

- 문항 1개 표시

하위 컴포넌트:

- `SkillBadge`
- `ChoiceGroup`
- `QuestionActions`

## 6.6 ChoiceGroup

역할:

- 선택지 4개 표시
- 현재 선택 상태 반영

## 6.7 QuestionActions

역할:

- 문항 번역 열기
- 보기 번역 열기
- 문항 듣기
- 보기 듣기

## 6.8 StickySubmitBar

역할:

- 남은 미응답 수
- 제출 버튼

모바일에서 중요:

- 하단 고정 가능

## 6.9 SubmitConfirmModal

역할:

- 실수 제출 방지

## 7. 결과 화면 컴포넌트

## 7.1 ResultPage

역할:

- 결과 화면 전체 조립

하위 컴포넌트:

- `ScoreSummaryCard`
- `SkillScoreGrid`
- `WrongQuestionList`
- `ResultActionBar`

## 7.2 ScoreSummaryCard

역할:

- 총점
- 맞은 개수
- 한 줄 요약

## 7.3 SkillScoreGrid

역할:

- 스킬별 결과 카드 묶음

## 7.4 WrongQuestionList

역할:

- 틀린 문항 목록 표시

## 7.5 WrongQuestionCard

역할:

- 틀린 문항 1개 표시

하위 컴포넌트:

- `AnswerCompareBlock`
- `ExplanationPanel`
- `WrongQuestionActions`

## 7.6 AnswerCompareBlock

역할:

- 내가 고른 답
- 정답
- 스킬

## 7.7 ExplanationPanel

역할:

- 오답 해석 표시
- 출처 표시
- 사용 모델 표시

## 7.8 WrongQuestionActions

역할:

- `짧게 보기`
- `자세히 보기`
- 번역 보기

## 7.9 ResultActionBar

역할:

- `다시 복습하기`
- `홈으로`

## 8. 복습 화면 컴포넌트

## 8.1 ReviewPage

역할:

- 복습 화면 전체 조립

하위 컴포넌트:

- `ReviewHeader`
- `ReviewList`
- `ReviewItemCard`

## 8.2 ReviewHeader

역할:

- 화면 제목
- 복습 개수

## 8.3 ReviewList

역할:

- 틀린 문제 목록 렌더링

## 8.4 ReviewItemCard

역할:

- 복습할 문제 1개 표시

하위 요소:

- 문제 번호
- 스킬
- 이전 선택
- 정답
- 해설 다시 보기
- 번역 버튼
- TTS 버튼

## 9. 보조 컴포넌트

### TranslationPanel

역할:

- 번역 본문 표시
- 번역 출처 표시

### TtsControls

역할:

- 재생
- 정지

### SkillBadge

역할:

- `main_idea`, `detail`, `inference`, `vocab_in_context` 표시

### AnswerOption

역할:

- 선택지 1개 표시

### InlineMessage

역할:

- 작은 상태 메시지 표시

예:

- 번역 없음
- API 토글 필요
- 해설 불러오는 중

## 10. 상태 관리 책임

프론트 상태는 아래처럼 나누는 것을 권장한다.

### 코덱스 CLI가 먼저 구현할 상태

- 선택한 난이도
- API 토글 값
- 현재 답안 상태
- 제출 가능 여부
- 번역 열림 여부
- TTS 재생 여부
- 오답 해석 열림 여부
- 로딩 / 오류 상태

### 안티그래비티가 주로 손보는 상태 표현

- 어떤 상태를 더 강조할지
- 어떤 카드가 더 두드러져 보일지
- 애니메이션과 시각적 전환감

## 11. 구현 순서 권장

1. 코덱스 CLI가 페이지와 컴포넌트 파일 뼈대를 만든다
2. 코덱스 CLI가 API 연결과 상태 관리를 붙인다
3. 코덱스 CLI가 기본 동작 가능한 최소 UI를 만든다
4. 안티그래비티가 본격적인 시각 디자인을 입힌다
5. 필요하면 코덱스 CLI가 안티그래비티 디자인에 맞춰 구조를 미세 조정한다

## 12. 개발자용 한 줄 지시문

아래 문장을 그대로 개발자 지시문으로 써도 된다.

`코덱스 CLI는 프론트엔드에서 페이지 구조, 컴포넌트 뼈대, 상태 관리, API 연결, 기본 동작 UI까지만 구현하고, 본격적인 시각 디자인과 디자인 완성도 높은 프론트엔드 구현은 안티그래비티에서 담당한다.`

## 13. 문서 결론

이 문서는 구현을 시작할 때

- 어떤 컴포넌트를 만들지
- 누가 어디까지 맡을지
- 어떤 순서로 붙일지

를 한 번에 보게 하는 기준 문서다.
