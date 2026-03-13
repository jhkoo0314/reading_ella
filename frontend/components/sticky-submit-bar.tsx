type StickySubmitBarProps = {
  unansweredCount: number;
  disabled: boolean;
  isSubmitting: boolean;
  onSubmit: () => void;
};

export function StickySubmitBar({ unansweredCount, disabled, isSubmitting, onSubmit }: StickySubmitBarProps) {
  return (
    <div className="solve-bottom-dock slide-up">
      <div className="dock-progress">
        {unansweredCount === 0 ? "✨ 전부 풀었어요!" : `🔥 ${unansweredCount}문제 남음`}
      </div>
      <button className="btn-3d btn-3d--purple" type="button" disabled={disabled} onClick={onSubmit}>
        {isSubmitting ? "채점중..." : "🚀 제출"}
      </button>
    </div>
  );
}
