type StickySubmitBarProps = {
  unansweredCount: number;
  disabled: boolean;
  isSubmitting: boolean;
  onSubmit: () => void;
};

export function StickySubmitBar({ unansweredCount, disabled, isSubmitting, onSubmit }: StickySubmitBarProps) {
  return (
    <div className="solve-bottom-dock slide-up">
      <div style={{ flex: 1 }}>
        <div className="dock-progress">
          {unansweredCount === 0 ? "🎉 전부 다 풀었어요!" : `🤔 남은 문제: ${unansweredCount}개`}
        </div>
        <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--text-muted)" }}>
          {unansweredCount === 0
            ? "제출하기 버튼을 눌러 점수를 확인해 볼까요?"
            : "모든 문제의 답을 골라야 제출할 수 있어요."}
        </p>
      </div>
      <button className="btn-3d btn-3d--purple" type="button" disabled={disabled} onClick={onSubmit}>
        {isSubmitting ? "채점 중..." : "🚀 제출하기"}
      </button>
    </div>
  );
}
