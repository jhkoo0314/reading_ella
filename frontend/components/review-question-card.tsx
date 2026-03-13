"use client";

import { useState } from "react";

import { ExplanationPanel, type ExplanationPanelState } from "@/components/explanation-panel";
import { TranslationPanel, type TranslationPanelState } from "@/components/translation-panel";
import { TtsControls } from "@/components/tts-controls";
import { ApiClientError, requestExplanation, requestTranslation } from "@/lib/api/client";
import type { ExplanationDetailLevel, ExplanationResponse, ReviewQuestionItem, TranslationResponse } from "@/lib/types/api";
import type { AssistToggles } from "@/lib/types/app";


const idleTranslationState: TranslationPanelState = { status: "idle" };
const idleExplanationState: ExplanationPanelState = { status: "idle" };

type ReviewQuestionCardProps = {
  item: ReviewQuestionItem;
  toggles: AssistToggles;
  questionBlockPlaying: boolean;
  onPlayQuestionBlock: () => void;
  onStopTts: () => void;
};


function getSkillLabel(skill: ReviewQuestionItem["skill"]) {
  if (skill === "main_idea") {
    return "🌟 주제 찾기";
  }
  if (skill === "detail") {
    return "🔍 자세히 보기";
  }
  if (skill === "inference") {
    return "💡 생각 넓히기";
  }
  return "📖 단어 뜻 알기";
}


function getTranslationState(response: TranslationResponse): TranslationPanelState {
  if (response.scope === "question_prompt") {
    if (!response.translated_prompt) {
      return { status: "error", message: "이 문항 번역은 아직 준비되지 않았습니다." };
    }

    return {
      status: "ready",
      data: {
        text: response.translated_prompt,
        sourceLabel: response.source === "local_overlay" ? "저장된 번역" : "실시간 번역",
      },
    };
  }

  if (!response.translated_choices || response.translated_choices.length === 0) {
    return { status: "error", message: "이 보기 번역은 아직 준비되지 않았습니다." };
  }

  return {
    status: "ready",
    data: {
      choices: response.translated_choices,
      sourceLabel: response.source === "local_overlay" ? "저장된 번역" : "실시간 번역",
    },
  };
}


function getTranslationErrorMessage(error: unknown) {
  if (error instanceof ApiClientError) {
    if (error.status === 403) {
      return "저장된 번역이 없고 API 번역이 꺼져 있어서 지금은 번역을 열 수 없습니다.";
    }
    if (error.status === 501) {
      return "이 번역 기능은 아직 연결되지 않았습니다.";
    }
    return error.message;
  }

  return "번역을 불러오지 못했습니다.";
}


function getExplanationState(response: ExplanationResponse): ExplanationPanelState {
  return {
    status: "ready",
    data: {
      explanation: response.explanation,
      sourceLabel: response.source === "local_rationale" ? "저장된 해설" : "실시간 해설",
      modelLabel: response.model_used ?? undefined,
    },
  };
}


function getExplanationErrorMessage(error: unknown) {
  if (error instanceof ApiClientError) {
    if (error.status === 403) {
      return "저장된 해설이 없고 API 해설이 꺼져 있어서 지금은 해설을 열 수 없습니다.";
    }
    if (error.status === 501) {
      return "이 해설 기능은 아직 연결되지 않았습니다.";
    }
    return error.message;
  }

  return "해설을 불러오지 못했습니다.";
}


export function ReviewQuestionCard({
  item,
  toggles,
  questionBlockPlaying,
  onPlayQuestionBlock,
  onStopTts,
}: ReviewQuestionCardProps) {
  const [promptTranslationOpen, setPromptTranslationOpen] = useState(false);
  const [promptTranslationState, setPromptTranslationState] = useState<TranslationPanelState>(idleTranslationState);
  const [choiceTranslationOpen, setChoiceTranslationOpen] = useState(false);
  const [choiceTranslationState, setChoiceTranslationState] = useState<TranslationPanelState>(idleTranslationState);
  const [explanationState, setExplanationState] = useState<ExplanationPanelState>(idleExplanationState);

  const allowExternalTranslationApi = toggles.useAssistApi && toggles.useApiTranslation;
  const allowExternalExplanationApi = toggles.useAssistApi && toggles.useApiExplain;

  async function loadTranslation(scope: "question_prompt" | "question_choices") {
    const setState = scope === "question_prompt" ? setPromptTranslationState : setChoiceTranslationState;
    setState({ status: "loading" });

    try {
      const response = await requestTranslation({
        pack_id: item.pack_id,
        scope,
        question_id: item.question_id,
        allow_external_api: allowExternalTranslationApi,
      });
      setState(getTranslationState(response));
    } catch (error) {
      setState({ status: "error", message: getTranslationErrorMessage(error) });
    }
  }

  async function loadExplanation(detailLevel: ExplanationDetailLevel) {
    setExplanationState({ status: "loading" });

    try {
      const response = await requestExplanation({
        pack_id: item.pack_id,
        question_id: item.question_id,
        chosen_index: item.chosen_index,
        detail_level: detailLevel,
        allow_external_api: allowExternalExplanationApi,
      });
      setExplanationState(getExplanationState(response));
    } catch (error) {
      setExplanationState({ status: "error", message: getExplanationErrorMessage(error) });
    }
  }

  function handleTogglePromptTranslation() {
    const nextOpen = !promptTranslationOpen;
    setPromptTranslationOpen(nextOpen);

    if (nextOpen && promptTranslationState.status === "idle") {
      void loadTranslation("question_prompt");
    }
  }

  function handleToggleChoiceTranslation() {
    const nextOpen = !choiceTranslationOpen;
    setChoiceTranslationOpen(nextOpen);

    if (nextOpen && choiceTranslationState.status === "idle") {
      void loadTranslation("question_choices");
    }
  }

  return (
    <article className="review-card">
      <div className="review-card__meta">
        <span className="badge badge--accent">🎈 질문 {item.question_number}</span>
        <span className="badge">{getSkillLabel(item.skill)}</span>
        <span className="badge badge--muted">{item.pack_id}</span>
      </div>

      <div className="review-card__header">
        <div>
          <h3 className="review-card__title">{item.prompt}</h3>
          <p className="review-card__subtitle">
            {item.topic} · {item.finished_at}
          </p>
        </div>
      </div>

      <div className="answer-compare-grid">
        <div className="answer-compare-card answer-compare-card--mine">
          <span className="selection-summary__label">🙋‍♀️ 내가 고른 답</span>
          <strong>{item.chosen_text}</strong>
        </div>
        <div className="answer-compare-card answer-compare-card--correct">
          <span className="selection-summary__label">🎯 진짜 정답</span>
          <strong>{item.correct_text}</strong>
        </div>
      </div>

      <div className="inline-button-row">
        <button className="inline-button" type="button" onClick={() => void loadExplanation("short")}>
          💡 힌트 보기
        </button>
        <button className="inline-button" type="button" onClick={() => void loadExplanation("deep")}>
          🕵️‍♀️ 선생님 설명 듣기
        </button>
        <button className="inline-button" type="button" onClick={handleTogglePromptTranslation}>
          {promptTranslationOpen ? "🙈 문제 해석 숨기기" : "👀 문제 해석 보기"}
        </button>
        <button className="inline-button" type="button" onClick={handleToggleChoiceTranslation}>
          {choiceTranslationOpen ? "🙈 보기 해석 숨기기" : "👀 보기 해석 보기"}
        </button>
      </div>

      <div className="question-card__tts">
        <TtsControls playLabel="문항 전체 읽기" isPlaying={questionBlockPlaying} onPlay={onPlayQuestionBlock} onStop={onStopTts} />
      </div>

      {promptTranslationOpen ? <TranslationPanel state={promptTranslationState} /> : null}
      {choiceTranslationOpen ? <TranslationPanel state={choiceTranslationState} /> : null}
      <ExplanationPanel state={explanationState} />
    </article>
  );
}
