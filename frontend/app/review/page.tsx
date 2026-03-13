import { Suspense } from "react";

import { AppShell } from "@/components/app-shell";
import { LoadingBlock } from "@/components/loading-block";
import { ReviewPageClient } from "@/components/review-page-client";
import { SectionCard } from "@/components/section-card";


function ReviewPageFallback() {
  return (
    <AppShell>
      <SectionCard title="복습 준비 중" description="복습 화면을 열고 있습니다.">
        <LoadingBlock label="복습 화면을 준비하는 중입니다." />
      </SectionCard>
    </AppShell>
  );
}

export default function ReviewPage() {
  return (
    <Suspense fallback={<ReviewPageFallback />}>
      <ReviewPageClient />
    </Suspense>
  );
}
