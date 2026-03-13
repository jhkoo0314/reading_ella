type ErrorStateCardProps = {
  title: string;
  description: string;
};


export function ErrorStateCard({ title, description }: ErrorStateCardProps) {
  return (
    <div className="state-card state-card--error" role="alert">
      <strong>{title}</strong>
      <p className="muted" style={{ marginBottom: 0 }}>
        {description}
      </p>
    </div>
  );
}
