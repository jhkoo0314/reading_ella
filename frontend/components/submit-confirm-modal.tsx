type SubmitConfirmModalProps = {
  open: boolean;
  isSubmitting: boolean;
  onClose: () => void;
  onConfirm: () => void;
};


export function SubmitConfirmModal({ open, isSubmitting, onClose, onConfirm }: SubmitConfirmModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="submit-modal-backdrop" role="presentation" onClick={onClose}>
      <div
        className="submit-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="submit-modal-title"
        onClick={(event) => event.stopPropagation()}
      >
        <h2 className="submit-modal__title" id="submit-modal-title">
          ✨ 다 풀었나요?
        </h2>
        <p className="submit-modal__description">지금 제출하고 점수를 확인해 볼까요?</p>
        <div className="button-row">
          <button className="button button--secondary" type="button" disabled={isSubmitting} onClick={onClose}>
            한 번 더 볼게요
          </button>
          <button className="button button--primary" type="button" disabled={isSubmitting} onClick={onConfirm}>
            {isSubmitting ? "채점 중..." : "🚀 네, 제출할게요!"}
          </button>
        </div>
      </div>
    </div>
  );
}
