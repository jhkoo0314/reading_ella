import Link from "next/link";


type ResultActionBarProps = {
  reviewHref: string;
};


export function ResultActionBar({ reviewHref }: ResultActionBarProps) {
  return (
    <div className="result-action-bar">
      <Link className="button button--secondary" href={reviewHref}>
        다시 복습하기
      </Link>
      <Link className="button button--secondary" href="/">
        홈으로
      </Link>
    </div>
  );
}
