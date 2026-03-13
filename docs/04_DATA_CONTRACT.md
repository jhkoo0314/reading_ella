# Rebuild v1 Data Contract

## 1. 문서 목적

이 문서는 문제 파일, 번역 파일, API 입력/출력, 기록 저장 구조의 약속을 정하는 문서다.
프론트엔드와 백엔드는 이 문서를 기준으로 움직여야 한다.

쉽게 말하면:
이 문서는 "데이터 약속서"다.

## 2. 핵심 원칙

- `pack.json` 형식을 쉽게 바꾸지 않는다
- `translation.json` 형식을 쉽게 바꾸지 않는다
- API 요청 / 응답 형식을 쉽게 바꾸지 않는다
- SQLite 테이블 구조는 문서 기준으로 관리한다
- 형식을 바꾸려면 문서를 먼저 갱신한다

## 3. pack.json

## 3.1 목적

한 개의 리딩 문제 세트를 담는 파일이다.

## 3.2 예시

```json
{
  "meta": {
    "pack_id": "g1_gt_0001",
    "level": "GT",
    "topic": "Weather Board",
    "created_at": "2026-03-01",
    "version": "0.1"
  },
  "passage": {
    "title": "GT Set #1",
    "text": "Our class has a weather board by the door.",
    "word_count": 150
  },
  "questions": [
    {
      "id": "q1",
      "skill": "main_idea",
      "prompt": "Which choice best tells what this passage is mostly about?",
      "choices": ["A", "B", "C", "D"],
      "answer_index": 1,
      "rationale": "Optional dev note"
    }
  ]
}
```

## 3.3 필수 필드

### root

- `meta`
- `passage`
- `questions`

### meta

- `pack_id`: string
- `level`: string (`GT`, `S`, `MGT` 중 하나)
- `topic`: string
- `created_at`: string
- `version`: string

### passage

- `title`: string
- `text`: string
- `word_count`: integer

### question

- `id`: string
- `skill`: string
- `prompt`: string
- `choices`: string array
- `answer_index`: integer
- `rationale`: optional string

## 3.4 하드 규칙

이 규칙은 어기면 pack을 사용할 수 없다.

- `questions.length == 6`
- 각 문항의 `choices.length == 4`
- `answer_index`는 `0` 이상 `3` 이하
- `level`은 `GT`, `S`, `MGT` 중 하나
- `skill`은 아래 4개 중 하나

```text
main_idea
detail
inference
vocab_in_context
```

## 3.5 권장 규칙

이 규칙은 경고로 처리할 수 있다.

- `word_count`는 150~350 권장
- 선택지 완전 중복은 피한다
- 질문과 선택지는 지문 외부 지식 의존을 줄인다

## 3.6 pack_id 규칙

1차에서는 아래 형태를 권장한다.

```text
g1_{level}_{number}
```

예:

- `g1_gt_0001`
- `g1_s_0007`
- `g1_mgt_0010`

## 3.7 translation.json

## 3.7.1 목적

번역은 원본 pack과 분리된 오버레이 파일로 관리한다.

이유:

- 원본 영어 문제를 보존하기 쉽다
- 번역을 부분적으로만 추가할 수 있다
- 수동 번역과 API 번역을 구분하기 쉽다

## 3.7.2 예시

```json
{
  "meta": {
    "pack_id": "g1_gt_0001",
    "lang": "ko",
    "version": "0.1",
    "source": "manual"
  },
  "passage": {
    "title_translated": "GT 세트 1",
    "text_translated": "우리 반은 문 옆에 날씨 게시판이 있다."
  },
  "questions": [
    {
      "id": "q1",
      "prompt_translated": "이 글의 중심 내용을 가장 잘 나타내는 것은 무엇인가?",
      "choices_translated": [
        "A",
        "B",
        "C",
        "D"
      ]
    }
  ]
}
```

## 3.7.3 필수 필드

- `meta.pack_id`
- `meta.lang`
- `meta.version`
- `meta.source`
- `passage`
- `questions`

## 3.7.4 부분 번역 허용

번역 파일은 부분적으로만 채워져 있어도 된다.

예:

- 지문 번역만 있음
- 특정 문항 prompt 번역만 있음
- 보기 번역은 없음

즉, 번역은 `none / partial / complete` 모두 허용한다.

## 4. FastAPI 응답 계약

## 4.1 문제 시작 응답

프론트엔드에 문제를 보여줄 때는 정답을 숨긴 공개용 응답을 사용한다.

예시:

```json
{
  "pack_id": "g1_gt_0001",
  "topic": "Weather Board",
  "passage": {
    "title": "GT Set #1",
    "text": "Our class has a weather board by the door.",
    "word_count": 150
  },
  "questions": [
    {
      "id": "q1",
      "skill": "main_idea",
      "prompt": "Which choice best tells what this passage is mostly about?",
      "choices": ["A", "B", "C", "D"]
    }
  ],
  "assist": {
    "translation": {
      "lang": "ko",
      "passage_available": true,
      "question_prompt_ids": ["q1"],
      "question_choice_ids": ["q1"]
    },
    "explanation": {
      "local_rationale_available": true,
      "api_available": true,
      "available_depths": ["short", "deep"]
    },
    "tts": {
      "browser_available": true,
      "api_available": true
    }
  }
}
```

주의:

- 프론트 응답에는 `answer_index`를 넣지 않는다
- 필요하면 운영자 전용 모드에서만 별도 사용한다
- `assist`는 어떤 보조 기능이 현재 가능한지 알려주는 힌트다

## 4.2 제출 요청 계약

프론트엔드는 제출 시 아래 형태로 보낸다.

```json
{
  "pack_id": "g1_gt_0001",
  "started_at": "2026-03-01T17:07:24+09:00",
  "answers": [
    {
      "question_id": "q1",
      "chosen_index": 1
    }
  ]
}
```

## 4.3 제출 응답 계약

FastAPI는 아래 형태로 응답한다.

```json
{
  "attempt_id": "att_20260301_170724_g1_gt_0001",
  "pack_id": "g1_gt_0001",
  "started_at": "2026-03-01T17:07:24+09:00",
  "finished_at": "2026-03-01T17:15:33+09:00",
  "answers": [
    {
      "question_id": "q1",
      "chosen_index": 1,
      "is_correct": true
    }
  ],
  "score": {
    "raw": 5,
    "total": 6,
    "by_skill": {
      "main_idea": { "correct": 1, "total": 1 },
      "detail": { "correct": 2, "total": 2 },
      "inference": { "correct": 0, "total": 1 },
      "vocab_in_context": { "correct": 2, "total": 2 }
    }
  },
  "wrong_question_ids": ["q4"]
}
```

## 4.4 번역 요청 계약

API 토글이 켜져 있고 로컬 번역이 없을 때만 사용하는 선택 계약이다.

```json
{
  "pack_id": "g1_gt_0001",
  "target_lang": "ko",
  "scope": "question_choices",
  "question_id": "q1",
  "allow_external_api": true
}
```

응답 예시:

```json
{
  "source": "api_live",
  "model_used": "gemini-3.1-flash-lite-preview",
  "pack_id": "g1_gt_0001",
  "target_lang": "ko",
  "scope": "question_choices",
  "question_id": "q1",
  "translated_choices": ["선지1", "선지2", "선지3", "선지4"]
}
```

주의:

- `allow_external_api`가 `false`면 외부 API를 호출하면 안 된다
- 기본값은 항상 `false`로 본다
- 필요하면 응답에 `provider_used`를 추가로 포함할 수 있다

권장 모델:

- v1 번역은 `gemini-3.1-flash-lite-preview`를 기본으로 통일한다

## 4.5 오답 해석 요청 계약

결과 화면에서 학생이 추가 설명을 원할 때 사용하는 선택 계약이다.

```json
{
  "pack_id": "g1_gt_0001",
  "question_id": "q4",
  "chosen_index": 2,
  "target_lang": "ko",
  "detail_level": "short",
  "allow_external_api": true
}
```

응답 예시:

```json
{
  "source": "api_live",
  "model_used": "gemini-3.1-flash-lite-preview",
  "pack_id": "g1_gt_0001",
  "question_id": "q4",
  "target_lang": "ko",
  "detail_level": "short",
  "explanation": "지문은 원인보다 결과를 더 직접적으로 말하고 있어서 2번은 근거가 약하다."
}
```

주의:

- `allow_external_api`가 `false`면 외부 모델을 호출하면 안 된다
- `detail_level`은 `short` 또는 `deep`만 허용한다
- `short`는 `gemini-3.1-flash-lite-preview`를 우선 사용한다
- `deep`는 `gemini-2.5-flash`를 우선 사용한다
- 필요하면 응답에 `provider_used`를 추가로 포함할 수 있다

## 4.6 TTS 요청 계약

TTS는 브라우저 기능을 기본으로 쓰고,
학생이 직접 API TTS를 요청했을 때만 외부 TTS를 시도한다.

```json
{
  "pack_id": "g1_gt_0001",
  "scope": "passage",
  "allow_external_api": false
}
```

응답 예시 1: 브라우저 TTS 우선

```json
{
  "source": "browser_tts",
  "pack_id": "g1_gt_0001",
  "scope": "passage",
  "playback_mode": "browser",
  "voice_locale": "en-US",
  "text": "Our class has a weather board by the door."
}
```

응답 예시 2: 외부 TTS 사용

```json
{
  "source": "api_live",
  "provider_used": "mock",
  "voice_used": "alloy",
  "pack_id": "g1_gt_0001",
  "scope": "question_prompt",
  "question_id": "q1",
  "playback_mode": "external",
  "voice_locale": "en-US",
  "text": "What is this passage mostly about?",
  "audio_url": "mock://tts/g1_gt_0001/question_prompt/q1"
}
```

주의:

- `scope`는 `passage`, `question_prompt`, `question_choices` 중 하나만 허용한다
- `question_prompt`, `question_choices`는 `question_id`가 필요하다
- `allow_external_api`가 `false`면 브라우저 TTS용 정보만 반환한다
- `allow_external_api`가 `true`여도 외부 provider가 없으면 명시적 오류를 반환한다
- 기본 재생 경로는 항상 브라우저 TTS다

## 5. SQLite 저장 구조

## 5.1 목적

학생의 시도 기록, 문항별 정오답, 팔로업 데이터를 저장한다.

## 5.2 권장 테이블

### attempts

- `attempt_id`: text primary key
- `pack_id`: text
- `started_at`: text
- `finished_at`: text
- `raw_score`: integer
- `total_score`: integer

### attempt_answers

- `id`: integer primary key
- `attempt_id`: text
- `question_id`: text
- `skill`: text
- `chosen_index`: integer
- `is_correct`: integer

### follow_up_items

- `id`: integer primary key
- `attempt_id`: text
- `pack_id`: text
- `question_id`: text
- `skill`: text
- `status`: text
- `created_at`: text
- `reason`: text

## 5.3 follow_up_items 의미

이 테이블은 "나중에 다시 봐야 하는 문제"를 저장하는 용도다.

예:

- 틀린 문제
- 약한 스킬 문제
- 복습 대상 문제

1차에서는 틀린 문제를 기본으로 저장하면 충분하다.

## 6. 시간 규칙

- 시간은 ISO8601 문자열로 저장한다
- 타임존은 `+09:00`으로 고정한다

예:

```text
2026-03-01T17:15:33+09:00
```

## 7. 채점 규칙

채점은 아주 단순하다.

```text
chosen_index == answer_index
```

즉:

- 맞으면 `is_correct = true`
- 틀리면 `is_correct = false`

총점은 맞은 개수 합계다.

## 8. 저장 위치

### 문제 파일

- 위치: `packs/*.json`

### 학생 기록 DB

- 위치: `backend/data/app.db`

### 번역 파일

- 위치: `translations/*.json`

## 9. 프론트엔드 구현 메모

Next.js 프론트엔드는 DB를 직접 읽지 않는다.
반드시 FastAPI를 통해 문제를 받고 제출한다.

- 프론트 타입 정의는 이 문서를 기준으로 만든다
- 채점 결과는 FastAPI 응답을 기준으로 렌더링한다
- 프론트 실행은 `pnpm`으로 통일한다
- 프론트의 API 토글은 기본 OFF로 시작한다
- 외부 API 키는 프론트에 두지 않는다
- 외부 API를 쓸 경우 실제 모델 선택은 FastAPI가 맡는다
