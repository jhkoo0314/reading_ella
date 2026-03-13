type LoadingBlockProps = {
  label?: string;
};


export function LoadingBlock({ label = "불러오는 중입니다." }: LoadingBlockProps) {
  return (
    <div className="loading-block" aria-live="polite">
      <span className="loading-block__dot" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}
