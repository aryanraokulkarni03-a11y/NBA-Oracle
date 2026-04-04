import { getHealth, getProviders } from "../lib/api";
import { PROVIDER_GUIDANCE } from "../lib/explain";
import { formatDateTime } from "../lib/format";
import { useResource } from "../hooks/useResource";
import { EmptyState } from "../components/EmptyState";
import { KeyValueList } from "../components/KeyValueList";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ProviderList } from "../components/ProviderList";
import { ScreenState } from "../components/ScreenState";
import { StatusPill } from "../components/StatusPill";

export function ProvidersPage() {
  const providers = useResource(getProviders);
  const health = useResource(getHealth);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Providers"
        title="Source and runtime health"
        description="Source health, fallback usage, and what degraded inputs actually mean for operator confidence."
        icon="providers"
      />
      <ScreenState isLoading={providers.isLoading || health.isLoading} error={providers.error || health.error}>
        <Panel title="How to read provider health" subtitle="Provider status is a confidence signal, not background noise.">
          <div className="guide-mini-grid">
            {PROVIDER_GUIDANCE.map((item) => (
              <article key={item.title} className="guide-mini-card">
                <p className="eyebrow">{item.title}</p>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </Panel>
        <section className="panel-grid panel-grid--two">
          <Panel title="Runtime summary" subtitle="Live API and service readiness from /api/health">
            <KeyValueList
              items={[
                { label: "Latest run", value: health.data?.latest_live?.run_id ?? "n/a" },
                { label: "Predictions", value: health.data?.latest_live?.prediction_count ?? 0 },
                { label: "Storage", value: health.data?.latest_live?.storage_mode ?? "n/a" },
                { label: "Runtime updated", value: formatDateTime(health.data?.runtime_state?.updated_at) },
                { label: "Deployment", value: health.data?.deployment?.target ?? "n/a" },
                { label: "Startup", value: <StatusPill value={health.data?.startup?.status} /> },
                { label: "Telegram", value: <StatusPill value={health.data?.services?.telegram_configured ? "healthy" : "not_configured"} /> },
                { label: "Gmail", value: <StatusPill value={health.data?.services?.gmail_configured ? "healthy" : "not_configured"} /> },
              ]}
            />
          </Panel>
          <Panel title="Provider summary" subtitle="Degradation and failure counts are first-class signals.">
            <KeyValueList
              items={[
                { label: "Run ID", value: providers.data?.run_id ?? "n/a" },
                { label: "Providers", value: providers.data?.providers?.length ?? 0 },
                { label: "Degraded", value: providers.data?.degraded_count ?? 0 },
                { label: "Failed", value: providers.data?.failed_count ?? 0 },
              ]}
            />
          </Panel>
        </section>
        {providers.data?.providers && providers.data.providers.length > 0 ? (
          <ProviderList providers={providers.data.providers} />
        ) : (
          <EmptyState
            title="No provider health available"
            body="Provider status appears here after the backend has produced a live slate report."
          />
        )}
      </ScreenState>
    </div>
  );
}
