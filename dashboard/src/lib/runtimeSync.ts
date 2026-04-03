export const RUNTIME_REFRESH_EVENT = "nba-oracle-runtime-refresh";

export function dispatchRuntimeRefresh(reason: string) {
  window.dispatchEvent(new CustomEvent(RUNTIME_REFRESH_EVENT, { detail: { reason, at: Date.now() } }));
}
