import type { ScoreSummary } from "@/lib/types/api";
import { SectionCard } from "@/components/section-card";


type SkillScoreGridProps = {
  score: ScoreSummary;
};


const skillLabels: Record<string, string> = {
  main_idea: "🌟 주제 찾기",
  detail: "🔍 자세히 보기",
  inference: "💡 생각 넓히기",
  vocab_in_context: "📖 단어 뜻 알기",
};


export function SkillScoreGrid({ score }: SkillScoreGridProps) {
  return (
    <SectionCard
      title="🧩 어떤 문제를 잘 풀었을까요?"
      description="영역별로 내가 몇 개를 맞혔는지 확인해 보세요."
    >
      <div className="skill-score-grid">
        {Object.entries(score.by_skill).map(([skill, value]) => (
          <div key={skill} className="skill-score-card">
            <span className="selection-summary__label">{skillLabels[skill] ?? skill}</span>
            <strong>
              {value.correct} / {value.total}
            </strong>
          </div>
        ))}
      </div>
    </SectionCard>
  );
}
