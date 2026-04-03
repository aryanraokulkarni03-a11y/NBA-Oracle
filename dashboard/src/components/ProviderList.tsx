import { formatDateTime, formatPercent } from "../lib/format";
import type { ProviderRecord } from "../lib/types";
import { StatusPill } from "./StatusPill";

export function ProviderList({ providers }: { providers: ProviderRecord[] }) {
  return (
    <div className="provider-list">
      {providers.map((provider) => (
        <article key={`${provider.kind}-${provider.name}`} className="provider-card">
          <div className="provider-card__top">
            <div>
              <p className="eyebrow">{provider.kind ?? "provider"}</p>
              <h3>{provider.name ?? "Unknown provider"}</h3>
            </div>
            <StatusPill value={provider.success ? (provider.degraded ? "degraded" : "healthy") : "failed"} />
          </div>
          <div className="provider-card__meta">
            <span>Trust {formatPercent(provider.trust)}</span>
            <span>{provider.record_count ?? 0} records</span>
            <span>{provider.source_version ?? "n/a"}</span>
          </div>
          <p className="provider-card__time">{formatDateTime(provider.source_time)}</p>
          {provider.error ? <p className="provider-card__error">{provider.error}</p> : null}
        </article>
      ))}
    </div>
  );
}
