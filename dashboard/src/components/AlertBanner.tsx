import { Icon } from "./Icons";

type AlertBannerProps = {
  tone?: "warning" | "danger" | "info";
  title: string;
  body: string;
};

export function AlertBanner({ tone = "info", title, body }: AlertBannerProps) {
  return (
    <div className={`alert-banner alert-banner--${tone}`}>
      <div className="alert-banner__title-row">
        <Icon name={tone === "warning" ? "warning" : "spark"} className="alert-banner__icon" />
        <strong>{title}</strong>
      </div>
      <p>{body}</p>
    </div>
  );
}
