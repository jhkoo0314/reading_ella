import { Suspense } from "react";

import { AppShell } from "@/components/app-shell";
import { LoadingBlock } from "@/components/loading-block";
import { SectionCard } from "@/components/section-card";
import { SolvePageClient } from "@/components/solve-page-client";


function SolvePageFallback() {
  return (
    <AppShell>
      <SectionCard title="문제 준비 중" description="문제 화면을 열고 있습니다.">
        <LoadingBlock label="문제 화면을 준비하는 중입니다." />
      </SectionCard>
    </AppShell>
  );
}


export default function SolvePage() {
  return (
    <Suspense fallback={<SolvePageFallback />}>
      <SolvePageClient />
    </Suspense>
  );
}
