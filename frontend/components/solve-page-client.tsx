"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter, useSearchParams } from "next/navigation";

import { AppShell } from "@/components/app-shell";
import { ErrorStateCard } from "@/components/error-state-card";
import { LoadingBlock } from "@/components/loading-block";
import { PassageSection } from "@/components/passage-section";
import { QuestionCard } from "@/components/question-card";
import { SectionCard } from "@/components/section-card";
import { SolveHeader } from "@/components/solve-header";
import { StickySubmitBar } from "@/components/sticky-submit-bar";
import { SubmitConfirmModal } from "@/components/submit-confirm-modal";
import type { TranslationPanelData, TranslationPanelState } from "@/components/translation-panel";
import { ApiClientError, getPackById, getRandomPack, requestTranslation, submitAnswers } from "@/lib/api/client";
import { buildAssistQueryString, readAssistTogglesFromSearchParams, readLevelFromSearchParams } from "@/lib/assist-query";
import { getCurrentKstIsoTimestamp } from "@/lib/kst-time";
import { buildQuestionWithChoicesSpeechText } from "@/lib/tts-text";
import { useBrowserTts } from "@/lib/use-browser-tts";
import type { Level, PackLoadResponse, TranslationResponse } from "@/lib/types/api";


const idleTranslationState: TranslationPanelState = { status: "idle" };

type QuestionTranslationMap = Record<string, TranslationPanelState>;
type OpenMap = Record<string, boolean>;


function deriveLevelFromPackId(packId: string): Level | null {
  const lowered = packId.toLowerCase();

  if (lowered.includes("_mgt_")) {
    return "MGT";
  }
  if (lowered.includes("_gt_")) {
    return "GT";
  }
  if (lowered.includes("_s_")) {
    return "S";
  }
  return null;
}


function getTranslationSourceLabel(response: TranslationResponse) {
  if (response.source === "local_overlay") {
    return "저장된 번역";
  }
  return "실시간 번역";
}


function createTranslationReadyState(data: Omit<TranslationPanelData, "sourceLabel">, response: TranslationResponse) {
  return {
    status: "ready",
    data: {
      ...data,
      sourceLabel: getTranslationSourceLabel(response),
    },
  } satisfies TranslationPanelState;
}


function buildTranslationState(response: TranslationResponse): TranslationPanelState {
  if (response.scope === "passage") {
    if (!response.translated_title && !response.translated_text) {
      return { status: "error", message: "이 지문은 아직 번역이 준비되지 않았습니다." };
    }

    return createTranslationReadyState(
      {
        title: response.translated_title ?? undefined,
        text: response.translated_text ?? undefined,
      },
      response,
    );
  }

  if (!response.translated_prompt && (!response.translated_choices || response.translated_choices.length === 0)) {
    return { status: "error", message: "이 문항 번역은 아직 준비되지 않았습니다." };
  }

  return createTranslationReadyState(
    {
      text: response.translated_prompt ?? undefined,
      choices: response.translated_choices ?? undefined,
    },
    response,
  );
}


function getLoadErrorMessage(error: unknown, needsLevel: boolean) {
  if (needsLevel) {
    return "난이도를 먼저 고른 뒤 다시 시작해주세요.";
  }
  if (error instanceof ApiClientError) {
    return error.message;
  }
  return "문제를 불러오지 못했습니다. 잠시 뒤 다시 시도해주세요.";
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


function getSubmitErrorMessage(error: unknown) {
  if (error instanceof ApiClientError) {
    return error.message;
  }
  return "제출 중 문제가 생겼습니다. 잠시 뒤 다시 시도해주세요.";
}


export function SolvePageClient() {
  const params = useParams<{ packId: string }>();
  const router = useRouter();
  const searchParams = useSearchParams();

  const routePackId = params.packId;
  const requestedLevel = readLevelFromSearchParams(searchParams);
  const { toggles } = readAssistTogglesFromSearchParams(searchParams);
  const allowExternalTranslationApi = toggles.useAssistApi && toggles.useApiTranslation;
  const shouldLoadRandomPack = routePackId === "random" || routePackId === "sample-pack";

  const [pack, setPack] = useState<PackLoadResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [passageTranslationOpen, setPassageTranslationOpen] = useState(false);
  const [passageTranslationState, setPassageTranslationState] = useState<TranslationPanelState>(idleTranslationState);
  const [questionTranslationOpenMap, setQuestionTranslationOpenMap] = useState<OpenMap>({});
  const [questionTranslationStateMap, setQuestionTranslationStateMap] = useState<QuestionTranslationMap>({});
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSubmitConfirm, setShowSubmitConfirm] = useState(false);
  const [startedAt, setStartedAt] = useState(getCurrentKstIsoTimestamp());
  const { playingKey, speakText, stopSpeech } = useBrowserTts();

  const resolvedLevel = requestedLevel ?? (pack ? deriveLevelFromPackId(pack.pack_id) : deriveLevelFromPackId(routePackId)) ?? "GT";
  const unansweredCount = pack ? pack.questions.filter((question) => answers[question.id] === undefined).length : 0;
  const submitDisabled = !pack || unansweredCount > 0 || isSubmitting;

  useEffect(() => {
    let isCancelled = false;

    setIsLoading(true);
    setLoadError(null);
    setPack(null);
    setAnswers({});
    setPassageTranslationOpen(false);
    setPassageTranslationState(idleTranslationState);
    setQuestionTranslationOpenMap({});
    setQuestionTranslationStateMap({});
    setSubmitError(null);
    setShowSubmitConfirm(false);
    stopSpeech();

    async function loadPack() {
      try {
        if (shouldLoadRandomPack && !requestedLevel) {
          throw new Error("missing-level");
        }

        const response = shouldLoadRandomPack
          ? await getRandomPack(requestedLevel as Level)
          : await getPackById(routePackId);

        if (isCancelled) {
          return;
        }

        setPack(response);
        setStartedAt(getCurrentKstIsoTimestamp());
      } catch (error) {
        if (isCancelled) {
          return;
        }

        const needsLevel = error instanceof Error && error.message === "missing-level";
        setLoadError(getLoadErrorMessage(error, needsLevel));
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadPack();

    return () => {
      isCancelled = true;
      stopSpeech();
    };
  }, [routePackId, requestedLevel, shouldLoadRandomPack, stopSpeech]);

  function handleChoiceSelect(questionId: string, choiceIndex: number) {
    setAnswers((previousAnswers) => ({
      ...previousAnswers,
      [questionId]: choiceIndex,
    }));
  }

  async function loadPassageTranslation() {
    if (!pack) {
      return;
    }

    setPassageTranslationState({ status: "loading" });

    try {
      const response = await requestTranslation({
        pack_id: pack.pack_id,
        scope: "passage",
        allow_external_api: allowExternalTranslationApi,
      });
      setPassageTranslationState(buildTranslationState(response));
    } catch (error) {
      setPassageTranslationState({ status: "error", message: getTranslationErrorMessage(error) });
    }
  }

  async function loadQuestionTranslation(questionId: string) {
    if (!pack) {
      return;
    }

    setQuestionTranslationStateMap((previousState) => ({
      ...previousState,
      [questionId]: { status: "loading" },
    }));

    try {
      const response = await requestTranslation({
        pack_id: pack.pack_id,
        scope: "question_full",
        question_id: questionId,
        allow_external_api: allowExternalTranslationApi,
      });

      setQuestionTranslationStateMap((previousState) => ({
        ...previousState,
        [questionId]: buildTranslationState(response),
      }));
    } catch (error) {
      setQuestionTranslationStateMap((previousState) => ({
        ...previousState,
        [questionId]: { status: "error", message: getTranslationErrorMessage(error) },
      }));
    }
  }

  function handleTogglePassageTranslation() {
    const nextOpen = !passageTranslationOpen;
    setPassageTranslationOpen(nextOpen);

    if (nextOpen && passageTranslationState.status === "idle") {
      void loadPassageTranslation();
    }
  }

  function handleToggleQuestionTranslation(questionId: string) {
    const nextOpen = !questionTranslationOpenMap[questionId];

    setQuestionTranslationOpenMap((previousState) => ({
      ...previousState,
      [questionId]: nextOpen,
    }));

    if (nextOpen && questionTranslationStateMap[questionId] === undefined) {
      void loadQuestionTranslation(questionId);
    }
  }

  function handleSubmitIntent() {
    if (!pack || unansweredCount > 0) {
      return;
    }

    setSubmitError(null);
    setShowSubmitConfirm(true);
  }

  async function handleSubmitConfirm() {
    if (!pack || unansweredCount > 0) {
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const response = await submitAnswers({
        pack_id: pack.pack_id,
        started_at: startedAt,
        answers: pack.questions.map((question) => ({
          question_id: question.id,
          chosen_index: answers[question.id],
        })),
      });

      stopSpeech();
      router.push(`/result/${response.attempt_id}?${buildAssistQueryString(toggles)}`);
    } catch (error) {
      setSubmitError(getSubmitErrorMessage(error));
      setShowSubmitConfirm(false);
    } finally {
      setIsSubmitting(false);
    }
  }

  if (isLoading) {
    return (
      <AppShell>
        <SectionCard title="문제 준비 중" description="선택한 난이도에 맞는 세트를 불러오고 있습니다.">
          <LoadingBlock label="문제를 준비하는 중입니다." />
        </SectionCard>
      </AppShell>
    );
  }

  if (loadError || !pack) {
    return (
      <AppShell>
        <SectionCard title="문제 화면" description="문제를 불러오지 못했을 때도 학생이 다시 시작할 수 있어야 합니다.">
          <ErrorStateCard title="문제를 불러오지 못했습니다." description={loadError ?? "잠시 뒤 다시 시도해주세요."} />
          <div className="button-row" style={{ marginTop: "1rem" }}>
            <button className="button button--secondary" type="button" onClick={() => router.push("/")}>
              홈으로 돌아가기
            </button>
          </div>
        </SectionCard>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <SolveHeader
        packId={pack.pack_id}
        level={resolvedLevel}
        topic={pack.topic}
        toggles={toggles}
        unansweredCount={unansweredCount}
        totalQuestions={pack.questions.length}
        isSubmitting={isSubmitting}
        onHomeClick={() => router.push("/")}
        onSubmitClick={handleSubmitIntent}
      />

      <div className="solve-canvas" style={{ flexDirection: 'column', height: 'auto', gap: '3rem', paddingBottom: '8rem' }}>
        <PassageSection
          title={pack.passage.title}
          text={pack.passage.text}
          topic={pack.topic}
          wordCount={pack.passage.word_count}
          translationOpen={passageTranslationOpen}
          translationState={passageTranslationState}
          isPlaying={playingKey === "passage"}
          onToggleTranslation={handleTogglePassageTranslation}
          onPlay={() => speakText("passage", pack.passage.text)}
          onStop={stopSpeech}
        />

        <div className="card-stack-container" style={{ 
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'stretch', 
          justifyContent: 'flex-start', 
          gap: '2.5rem'
        }}>
          {pack.questions.map((question, index) => (
            <QuestionCard
              key={question.id}
              style={{ position: 'relative', width: '100%' }}
              question={question}
              questionNumber={index + 1}
              selectedIndex={answers[question.id]}
              questionTranslationOpen={Boolean(questionTranslationOpenMap[question.id])}
              questionTranslationState={questionTranslationStateMap[question.id] ?? idleTranslationState}
              isQuestionBlockPlaying={playingKey === `question-block:${question.id}`}
              onSelect={(choiceIndex) => handleChoiceSelect(question.id, choiceIndex)}
              onToggleQuestionTranslation={() => handleToggleQuestionTranslation(question.id)}
              onPlayQuestionBlock={() =>
                speakText(
                  `question-block:${question.id}`,
                  buildQuestionWithChoicesSpeechText(question.prompt, question.choices),
                )
              }
              onStopTts={stopSpeech}
            />
          ))}
        </div>
      </div>

      {submitError ? (
        <div style={{ marginTop: '2rem', width: '100%' }}>
          <ErrorStateCard title="제출을 마치지 못했습니다." description={submitError} />
        </div>
      ) : null}

      <StickySubmitBar
        unansweredCount={unansweredCount}
        disabled={submitDisabled}
        isSubmitting={isSubmitting}
        onSubmit={handleSubmitIntent}
      />

      <SubmitConfirmModal
        open={showSubmitConfirm}
        isSubmitting={isSubmitting}
        onClose={() => setShowSubmitConfirm(false)}
        onConfirm={handleSubmitConfirm}
      />
    </AppShell>
  );
}
