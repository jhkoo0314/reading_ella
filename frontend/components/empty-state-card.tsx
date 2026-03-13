type EmptyStateCardProps = {
  title: string;
  description: string;
};


export function EmptyStateCard({ title, description }: EmptyStateCardProps) {
  return (
    <div className="state-card state-card--empty">
      <strong>{title}</strong>
      <p className="muted" style={{ marginBottom: 0 }}>
        {description}
      </p>
    </div>
  );
}
