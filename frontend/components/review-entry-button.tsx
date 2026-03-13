import Link from "next/link";


export function ReviewEntryButton() {
  return (
    <div className="stack">
      <Link className="button button--secondary" href="/review">
        오답 복습
      </Link>
      <p className="inline-help" style={{ margin: 0 }}>
        아직 복습 데이터가 없으면 빈 복습 화면이 열립니다.
      </p>
    </div>
  );
}
