import type { AttemptResultResponse } from "@/lib/types/api";
import { SectionCard } from "@/components/section-card";


type ScoreSummaryCardProps = {
  result: AttemptResultResponse;
};


function getSummaryMessage(raw: number, total: number) {
  if (raw === total) {
    return "와아! 전부 다 맞혔어요! 정말 대단해요! 🎉";
  }
  if (raw === 0) {
    return "조금 헷갈렸나요? 괜찮아요, 다시 보면 더 잘할 수 있어요! 💪";
  }
  return `우와, ${total}개 중에서 ${raw}개나 맞혔어요! 틀린 문제도 다시 볼까요? ✨`;
}


export function ScoreSummaryCard({ result }: ScoreSummaryCardProps) {
  return (
    <SectionCard
      title="🏆 내 점수 확인하기"
      description="자, 내가 오늘 얼마나 잘했는지 같이 볼까요?"
    >
      <div className="score-summary-card">
        <div className="score-summary-card__score" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <strong style={{ fontSize: '4rem', color: 'var(--color-primary)', lineHeight: 1 }}>{result.score.raw}</strong>
          <span style={{ fontSize: '1.2rem', color: 'var(--color-text-light)' }}>/ {result.score.total}</span>
        </div>
        <p className="score-summary-card__message">{getSummaryMessage(result.score.raw, result.score.total)}</p>
        <div className="selection-summary">
          <div className="selection-summary__item">
            <span className="selection-summary__label">난이도</span>
            <strong>{result.level}</strong>
          </div>
          <div className="selection-summary__item">
            <span className="selection-summary__label">세트</span>
            <strong>{result.pack_id}</strong>
          </div>
          <div className="selection-summary__item">
            <span className="selection-summary__label">완료 시각</span>
            <strong>{result.finished_at}</strong>
          </div>
        </div>
      </div>
    </SectionCard>
  );
}
