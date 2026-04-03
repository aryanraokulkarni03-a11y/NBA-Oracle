import { formatProviderMeaning, formatProviderName, formatProviderVersion } from "../lib/explain";
import { formatDateTime, formatPercent, toHeadline } from "../lib/format";
import type { ProviderRecord } from "../lib/types";
import { StatusPill } from "./StatusPill";

export function ProviderList({ providers }: { providers: ProviderRecord[] }) {
  return (
    <div className="provider-list">
      {providers.map((provider) => (
        <article key={`${provider.kind}-${provider.name}`} className="provider-card">
          <div className="provider-card__top">
            <div>
              <p className="eyebrow">{toHeadline(provider.kind ?? "provider")}</p>
              <h3>{formatProviderName(provider.name)}</h3>
            </div>
            <StatusPill value={provider.success ? (provider.degraded ? "degraded" : "healthy") : "failed"} />
          </div>
          <div className="provider-card__meta">
            <span>Trust {formatPercent(provider.trust)}</span>
            <span>{provider.record_count ?? 0} records</span>
            <span>{formatProviderVersion(provider.source_version)}</span>
          </div>
          <p className="provider-card__time">{formatDateTime(provider.source_time)}</p>
          <p className="provider-card__meaning">{formatProviderMeaning(provider.error, provider.degraded, provider.success)}</p>
        </article>
      ))}
    </div>
  );
}
