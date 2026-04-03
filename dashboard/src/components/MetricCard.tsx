import { Icon } from "./Icons";

type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "success" | "warning" | "danger";
  icon?: "activity" | "spark" | "warning" | "shield" | "mail" | "providers";
};

export function MetricCard({ label, value, hint, tone = "default", icon = "activity" }: MetricCardProps) {
  const compact = value.length > 12;

  return (
    <article className={`metric-card metric-card--${tone}`}>
      <div className="metric-card__top">
        <p className="metric-card__label">{label}</p>
        <Icon name={icon} className="metric-card__icon" />
      </div>
      <p className={compact ? "metric-card__value metric-card__value--compact" : "metric-card__value"}>{value}</p>
      {hint ? <p className="metric-card__hint">{hint}</p> : null}
    </article>
  );
}
