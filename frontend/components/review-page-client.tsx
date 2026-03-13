"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import { ApiStatusBadge } from "@/components/api-status-badge";
import { AppShell } from "@/components/app-shell";
import { EmptyStateCard } from "@/components/empty-state-card";
import { ErrorStateCard } from "@/components/error-state-card";
import { LoadingBlock } from "@/components/loading-block";
import { PageHeader } from "@/components/page-header";
import { ReviewQuestionCard } from "@/components/review-question-card";
import { SectionCard } from "@/components/section-card";
import { ApiClientError, getReviewItems } from "@/lib/api/client";
import { readAssistTogglesFromSearchParams } from "@/lib/assist-query";
import { loadSessionDraft } from "@/lib/session-draft-storage";
import { buildQuestionWithChoicesSpeechText } from "@/lib/tts-text";
import { useBrowserTts } from "@/lib/use-browser-tts";
import type { ReviewQuestionItem } from "@/lib/types/api";
import { defaultAssistToggles, type AssistToggles } from "@/lib/types/app";


function getLoadErrorMessage(error: unknown) {
  if (error instanceof ApiClientError) {
    return error.message;
  }

  return "복습 목록을 불러오지 못했습니다. 잠시 뒤 다시 시도해주세요.";
}


export function ReviewPageClient() {
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
  const [items, setItems] = useState<ReviewQuestionItem[]>([]);
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

    async function loadReviewItems() {
      try {
        const response = await getReviewItems();

        if (isCancelled) {
          return;
        }

        setItems(response.items);
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

    void loadReviewItems();

    return () => {
      isCancelled = true;
      stopSpeech();
    };
  }, [stopSpeech]);

  if (isLoading) {
    return (
      <AppShell>
        <SectionCard title="복습 준비 중" description="저장된 오답 목록을 불러오고 있습니다.">
          <LoadingBlock label="복습 목록을 준비하는 중입니다." />
        </SectionCard>
      </AppShell>
    );
  }

  if (loadError) {
    return (
      <AppShell>
        <SectionCard title="복습 화면" description="오답 목록을 읽지 못했을 때도 홈으로 돌아갈 수 있어야 합니다.">
          <ErrorStateCard title="복습 목록을 불러오지 못했습니다." description={loadError} />
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
      <PageHeader
        eyebrow="Review"
        title="오답 복습"
        description="틀린 문제만 다시 모아 보여줍니다. 필요한 번역, 읽기, 해설은 여기서도 직접 눌러서 볼 수 있습니다."
        actions={<ApiStatusBadge enabled={toggles.useAssistApi} />}
      />

      <SectionCard
        title="복습 목록"
        description={`현재 저장된 복습 대상은 ${items.length}개입니다. 맞은 문제는 여기서 기본으로 보여주지 않습니다.`}
      >
        {items.length === 0 ? (
          <EmptyStateCard
            title="현재 복습할 오답이 없습니다."
            description="문제를 제출해서 틀린 문항이 저장되면 여기에서 다시 볼 수 있습니다."
          />
        ) : (
          <div className="question-list">
            {items.map((item) => (
              <ReviewQuestionCard
                key={`${item.attempt_id}-${item.question_id}`}
                item={item}
                toggles={toggles}
                questionBlockPlaying={playingKey === `review-question-block:${item.attempt_id}:${item.question_id}`}
                onPlayQuestionBlock={() =>
                  speakText(
                    `review-question-block:${item.attempt_id}:${item.question_id}`,
                    buildQuestionWithChoicesSpeechText(item.prompt, item.choices),
                  )
                }
                onStopTts={stopSpeech}
              />
            ))}
          </div>
        )}
      </SectionCard>
    </AppShell>
  );
}
