import { Suspense } from "react";

import { AppShell } from "@/components/app-shell";
import { LoadingBlock } from "@/components/loading-block";
import { ResultPageClient } from "@/components/result-page-client";
import { SectionCard } from "@/components/section-card";

type ResultPageProps = {
  params: Promise<{
    attemptId: string;
  }>;
};


function ResultPageFallback() {
  return (
    <AppShell>
      <SectionCard title="결과 준비 중" description="결과 화면을 열고 있습니다.">
        <LoadingBlock label="결과 화면을 준비하는 중입니다." />
      </SectionCard>
    </AppShell>
  );
}

export default async function ResultPage({ params }: ResultPageProps) {
  const { attemptId } = await params;

  return (
    <Suspense fallback={<ResultPageFallback />}>
      <ResultPageClient attemptId={attemptId} />
    </Suspense>
  );
}
