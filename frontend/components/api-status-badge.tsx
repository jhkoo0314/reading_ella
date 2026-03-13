type ApiStatusBadgeProps = {
  enabled: boolean;
};


export function ApiStatusBadge({ enabled }: ApiStatusBadgeProps) {
  return (
    <span className={`badge ${enabled ? "badge--accent" : "badge--muted"}`}>
      {enabled ? "API ON" : "API OFF"}
    </span>
  );
}
