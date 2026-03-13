"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ApiStatusBadge } from "@/components/api-status-badge";
import { AppShell } from "@/components/app-shell";
import { EmptyStateCard } from "@/components/empty-state-card";
import { ErrorStateCard } from "@/components/error-state-card";
import { LoadingBlock } from "@/components/loading-block";
import { PageHeader } from "@/components/page-header";
import { ResultActionBar } from "@/components/result-action-bar";
import { ReviewQuestionCard } from "@/components/review-question-card";
import { ScoreSummaryCard } from "@/components/score-summary-card";
import { SectionCard } from "@/components/section-card";
import { SkillScoreGrid } from "@/components/skill-score-grid";
import { getAttemptResult, ApiClientError } from "@/lib/api/client";
import { buildAssistQueryString, readAssistTogglesFromSearchParams } from "@/lib/assist-query";
import { loadSessionDraft } from "@/lib/session-draft-storage";
import { buildQuestionWithChoicesSpeechText } from "@/lib/tts-text";
import { useBrowserTts } from "@/lib/use-browser-tts";
import type { AttemptResultResponse } from "@/lib/types/api";
import { defaultAssistToggles, type AssistToggles } from "@/lib/types/app";


type ResultPageClientProps = {
  attemptId: string;
};


function getLoadErrorMessage(error: unknown) {
  if (error instanceof ApiClientError) {
    return error.message;
  }

  return "결과를 불러오지 못했습니다. 잠시 뒤 다시 시도해주세요.";
}


export function ResultPageClient({ attemptId }: ResultPageClientProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const assistParam = searchParams.get("assist");
  const translationParam = searchParams.get("translation");
  const ttsParam = searchParams.get("tts");
  const explainParam = searchParams.get("explain");
  const queryToggleState = useMemo(
    () =>
      readAssistTogglesFromSearchParams({
        get(key: string) {
          if (key === "assist") {
            return assistParam;
          }
          if (key === "translation") {
            return translationParam;
          }
          if (key === "tts") {
            return ttsParam;
          }
          if (key === "explain") {
            return explainParam;
          }
          return null;
        },
      }),
    [assistParam, translationParam, ttsParam, explainParam],
  );
  const { toggles: queryToggles, hasExplicitParams } = queryToggleState;
  const [toggles, setToggles] = useState<AssistToggles>(queryToggles);
  const [result, setResult] = useState<AttemptResultResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const { playingKey, speakText, stopSpeech } = useBrowserTts();

  useEffect(() => {
    if (hasExplicitParams) {
      setToggles(queryToggles);
      return;
    }

    setToggles(loadSessionDraft().toggles ?? { ...defaultAssistToggles });
  }, [hasExplicitParams, queryToggles]);

  useEffect(() => {
    let isCancelled = false;

    setIsLoading(true);
    setLoadError(null);

    async function loadResult() {
      try {
        const response = await getAttemptResult(attemptId);

        if (isCancelled) {
          return;
        }

        setResult(response);
      } catch (error) {
        if (isCancelled) {
          return;
        }

        setLoadError(getLoadErrorMessage(error));
      } finally {
        if (!isCancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadResult();

    return () => {
      isCancelled = true;
      stopSpeech();
    };
  }, [attemptId, stopSpeech]);

  if (isLoading) {
    return (
      <AppShell>
        <SectionCard title="결과 준비 중" description="채점 결과와 오답 목록을 불러오고 있습니다.">
          <LoadingBlock label="결과를 준비하는 중입니다." />
        </SectionCard>
      </AppShell>
    );
  }

  if (loadError || !result) {
    return (
      <AppShell>
        <SectionCard title="결과 화면" description="결과를 찾지 못했을 때도 홈으로 돌아갈 수 있어야 합니다.">
          <ErrorStateCard title="결과를 불러오지 못했습니다." description={loadError ?? "잠시 뒤 다시 시도해주세요."} />
          <div className="button-row" style={{ marginTop: "1rem" }}>
            <button className="button button--secondary" type="button" onClick={() => router.push("/")}>
              홈으로 돌아가기
            </button>
          </div>
        </SectionCard>
      </AppShell>
    );
  }

  const reviewHref = `/review?${buildAssistQueryString(toggles)}`;

  return (
    <AppShell>
      <PageHeader
        eyebrow="Result"
        title={`${result.passage_title} 결과`}
        description="총점, 스킬별 결과, 틀린 문항을 한 화면에서 보고 필요한 설명만 버튼으로 열 수 있게 구성했습니다."
        actions={<ApiStatusBadge enabled={toggles.useAssistApi} />}
      />

      <div className="grid grid--two">
        <ScoreSummaryCard result={result} />
        <SkillScoreGrid score={result.score} />
      </div>

      <SectionCard title="틀린 문항" description="오답만 먼저 보여주고, 설명과 번역은 눌렀을 때만 열립니다.">
        {result.wrong_questions.length === 0 ? (
          <EmptyStateCard
            title="현재 다시 볼 오답이 없습니다."
            description="모든 문항을 맞혔습니다. 다음 세트로 넘어가도 좋습니다."
          />
        ) : (
          <div className="question-list">
            {result.wrong_questions.map((item) => (
              <ReviewQuestionCard
                key={`${item.attempt_id}-${item.question_id}`}
                item={item}
                toggles={toggles}
                questionBlockPlaying={playingKey === `result-question-block:${item.attempt_id}:${item.question_id}`}
                onPlayQuestionBlock={() =>
                  speakText(
                    `result-question-block:${item.attempt_id}:${item.question_id}`,
                    buildQuestionWithChoicesSpeechText(item.prompt, item.choices),
                  )
                }
                onStopTts={stopSpeech}
              />
            ))}
          </div>
        )}
      </SectionCard>

      <ResultActionBar reviewHref={reviewHref} />
    </AppShell>
  );
}
