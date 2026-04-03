import { formatReadableText } from "../lib/format";
import type { ReactNode } from "react";

export function ScreenState({
  isLoading,
  error,
  children,
}: {
  isLoading: boolean;
  error: string | null;
  children: ReactNode;
}) {
  if (isLoading) {
    return <div className="screen-state">Loading dashboard state...</div>;
  }
  if (error) {
    return (
      <div className="screen-state screen-state--error">
        {error.startsWith("rate_limited")
          ? "Too many requests are in flight. Give the dashboard a moment, then refresh."
          : formatReadableText(error)}
      </div>
    );
  }
  return <>{children}</>;
}
