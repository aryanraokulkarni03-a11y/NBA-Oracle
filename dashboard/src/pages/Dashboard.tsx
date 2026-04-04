import { getHealth, getLearning, getProviders, getStability, getToday } from "../lib/api";
import { formatCompactId, formatCount, formatDateTime, formatReadableText } from "../lib/format";
import { useResource } from "../hooks/useResource";
import { AlertBanner } from "../components/AlertBanner";
import { MetricCard } from "../components/MetricCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ProviderList } from "../components/ProviderList";
import { ScreenState } from "../components/ScreenState";
import { StatusPill } from "../components/StatusPill";

export function DashboardPage() {
  const health = useResource(getHealth);
  const today = useResource(getToday);
  const stability = useResource(getStability);
  const learning = useResource(getLearning);
  const providers = useResource(getProviders);

  const isLoading =
    health.isLoading || today.isLoading || stability.isLoading || learning.isLoading || providers.isLoading;
  const error = health.error || today.error || stability.error || learning.error || providers.error;
  const predictions = today.data?.predictions ?? [];
  const bets = predictions.filter((item) => item.decision === "BET").length;
  const leans = predictions.filter((item) => item.decision === "LEAN").length;
  const skips = predictions.filter((item) => item.decision === "SKIP").length;
  const startup = health.data?.startup;
  const notificationEvents = health.data?.notifications?.latest_events ?? [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Overview"
        title="Operating snapshot"
        description="Live run state, model health, provider confidence, and review readiness in one clear operator view."
        icon="overview"
      />
      <ScreenState isLoading={isLoading} error={error}>
        {(providers.data?.failed_count ?? 0) > 0 || (providers.data?.degraded_count ?? 0) > 0 ? (
          <AlertBanner
            tone="warning"
            title="Some sources are degraded"
            body="A degraded source means the system had to fall back, wait on weaker data, or intentionally defer that input. The workflow is still usable, but confidence should stay measured."
          />
        ) : null}
        <section className="metric-grid">
          <MetricCard
            label="Latest run"
            value={formatCompactId(today.data?.run_id, 14, 8)}
            hint={formatDateTime(today.data?.decision_time)}
            icon="activity"
          />
          <MetricCard label="Bets" value={formatCount(bets)} tone={bets > 0 ? "success" : "default"} icon="spark" />
          <MetricCard label="Leans" value={formatCount(leans)} icon="activity" />
          <MetricCard label="Skips" value={formatCount(skips)} tone={skips > 0 ? "warning" : "default"} icon="warning" />
          <MetricCard label="Drift" value={formatReadableText(stability.data?.drift?.status ?? "n/a")} icon="shield" />
          <MetricCard label="Learning" value={formatReadableText(learning.data?.status ?? "n/a")} icon="activity" />
        </section>
        <section className="panel-grid panel-grid--two">
          <Panel title="System health" subtitle="Live service readiness from the current backend state.">
            <div className="summary-grid">
              <div className="summary-grid__item">
                <span>API</span>
                <strong>
                  {health.data?.api?.host}:{health.data?.api?.port}
                </strong>
              </div>
              <div className="summary-grid__item">
                <span>Timezone</span>
                <strong>{health.data?.api?.timezone ?? "n/a"}</strong>
              </div>
              <div className="summary-grid__item">
                <span>Telegram</span>
                <StatusPill value={health.data?.services?.telegram_configured ? "healthy" : "not_configured"} />
              </div>
              <div className="summary-grid__item">
                <span>Gmail</span>
                <StatusPill value={health.data?.services?.gmail_configured ? "healthy" : "not_configured"} />
              </div>
              <div className="summary-grid__item">
                <span>Startup status</span>
                <StatusPill value={startup?.status} />
              </div>
              <div className="summary-grid__item">
                <span>Deployment</span>
                <strong>{health.data?.deployment?.target ?? "n/a"}</strong>
              </div>
            </div>
          </Panel>
          <Panel title="Live slate summary" subtitle="This view reflects only the latest stored prediction run.">
            <div className="summary-grid">
              <div className="summary-grid__item">
                <span>Storage</span>
                <strong>{today.data?.storage_mode ?? "n/a"}</strong>
              </div>
              <div className="summary-grid__item">
                <span>Predictions</span>
                <strong>{predictions.length}</strong>
              </div>
              <div className="summary-grid__item">
                <span>Provider count</span>
                <strong>{today.data?.providers?.length ?? 0}</strong>
              </div>
              <div className="summary-grid__item">
                <span>Last refresh</span>
                <strong>{formatDateTime(health.data?.runtime_state?.updated_at)}</strong>
              </div>
            </div>
          </Panel>
        </section>
        <section className="panel-grid panel-grid--two">
          <Panel title="Stability and learning" subtitle="Evidence stays visible as it really is, including honest insufficient-data states.">
            <div className="list-stack">
              <div className="list-row">
                <span>Drift</span>
                <StatusPill value={stability.data?.drift?.status} />
              </div>
              <div className="list-row">
                <span>Timing</span>
                <StatusPill value={stability.data?.timing?.status} />
              </div>
              <div className="list-row">
                <span>Learning</span>
                <StatusPill value={learning.data?.status} />
              </div>
              <div className="list-row">
                <span>Candidate model</span>
                <strong>{learning.data?.candidate_model_version ?? "none"}</strong>
              </div>
            </div>
          </Panel>
          <Panel title="Startup and delivery" subtitle="Startup readiness and recent delivery truth stay visible in the main overview.">
            <div className="list-stack">
              <div className="list-row">
                <span>Startup warnings</span>
                <strong>{startup?.warning_count ?? 0}</strong>
              </div>
              <div className="list-row">
                <span>Startup failures</span>
                <strong>{startup?.failed_count ?? 0}</strong>
              </div>
              <div className="list-row">
                <span>Public API</span>
                <strong>{startup?.deployment?.public_api_base_url ?? "local proxy"}</strong>
              </div>
              {notificationEvents.slice(0, 2).map((event) => (
                <div className="list-row" key={event.event_id}>
                  <span>{formatReadableText(event.event_type ?? event.channel ?? "notification")}</span>
                  <strong>
                    {(event.channel ?? "channel").toUpperCase()} | {event.success ? "Success" : "Failed"}
                  </strong>
                </div>
              ))}
            </div>
          </Panel>
        </section>
        <section className="panel-grid panel-grid--two">
          <Panel title="Providers" subtitle="Source quality stays visible in the primary operator surface.">
            <ProviderList providers={(providers.data?.providers ?? []).slice(0, 3)} />
          </Panel>
          <Panel title="Startup checks" subtitle="Runtime readiness is explicit instead of being left to memory.">
            <div className="list-stack">
              {(startup?.checks ?? []).slice(0, 4).map((check) => (
                <div className="list-row" key={check.name}>
                  <span>{formatReadableText(check.name)}</span>
                  <strong>{formatReadableText(check.status)}</strong>
                </div>
              ))}
            </div>
          </Panel>
        </section>
      </ScreenState>
    </div>
  );
}
