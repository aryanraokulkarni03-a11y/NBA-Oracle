import { formatRelativeStatus, toHeadline } from "../lib/format";

type StatusPillProps = {
  value?: string | null;
  tone?: "default" | "success" | "warning" | "danger" | "muted";
};

export function StatusPill({ value, tone }: StatusPillProps) {
  const normalized = (value ?? "unknown").toLowerCase();
  const resolvedTone =
    tone ??
    (normalized.includes("healthy") || normalized.includes("success")
      ? "success"
      : normalized.includes("warning") || normalized.includes("degraded") || normalized.includes("insufficient")
        ? "warning"
        : normalized.includes("fail") || normalized.includes("error") || normalized.includes("locked")
          ? "danger"
          : "default");

  return <span className={`status-pill status-pill--${resolvedTone}`}>{toHeadline(formatRelativeStatus(value))}</span>;
}
