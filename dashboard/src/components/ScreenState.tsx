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
    return <div className="screen-state">Loading dashboard state…</div>;
  }
  if (error) {
    return <div className="screen-state screen-state--error">{formatReadableText(error)}</div>;
  }
  return <>{children}</>;
}
