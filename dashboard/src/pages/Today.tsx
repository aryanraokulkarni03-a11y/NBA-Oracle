import { Icon } from "../components/Icons";
import { Panel } from "../components/Panel";
import { getToday } from "../lib/api";
import { TODAY_GUIDANCE } from "../lib/explain";
import { useResource } from "../hooks/useResource";
import { PageHeader } from "../components/PageHeader";
import { PredictionCard } from "../components/PredictionCard";
import { ScreenState } from "../components/ScreenState";

export function TodayPage() {
  const { data, isLoading, error, refresh } = useResource(getToday);
  const actionablePredictions = data?.actionable_predictions ?? data?.predictions ?? [];
  const nextUpPredictions = data?.next_up_predictions ?? [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Today"
        title="Live slate"
        description="Actionable games first, then the next stored lookahead slate. Completed games stay off this surface so the page stays useful before tipoff."
        icon="today"
        actions={
          <button type="button" className="button button--secondary" onClick={() => void refresh()}>
            <Icon name="refresh" className="button__icon" />
            Refresh
          </button>
        }
      />
      <ScreenState isLoading={isLoading} error={error}>
        <Panel
          title="How to read today's calls"
          subtitle="Use these reminders before treating a likely winner as a betting opportunity."
        >
          <div className="guide-mini-grid">
            {TODAY_GUIDANCE.map((item) => (
              <article key={item.title} className="guide-mini-card">
                <p className="eyebrow">{item.title}</p>
                <p>{item.body}</p>
              </article>
            ))}
          </div>
        </Panel>
        <section className="slate-section-stack">
          <Panel
            title="Actionable slate"
            subtitle="These are the nearest upcoming games the operator can still act on from the current stored prediction history."
            actions={<span className="panel__meta">{actionablePredictions.length} games</span>}
          >
            {actionablePredictions.length === 0 ? (
              <div className="mini-empty-state">
                <strong>No actionable games stored right now.</strong>
                <p>This is normal between slates or before a fresh pregame run has produced upcoming predictions.</p>
              </div>
            ) : (
              <section className="prediction-grid">
                {actionablePredictions.map((prediction) => (
                  <PredictionCard key={`${prediction.run_id ?? "run"}-${prediction.game_id ?? "game"}`} prediction={prediction} />
                ))}
              </section>
            )}
          </Panel>
          <Panel
            title="Next up"
            subtitle="Use this lookahead section for tomorrow's or the next stored slate so you can plan before the main actionable window opens."
            actions={<span className="panel__meta">{nextUpPredictions.length} games</span>}
          >
            {nextUpPredictions.length === 0 ? (
              <div className="mini-empty-state">
                <strong>No later slate is stored yet.</strong>
                <p>The section fills in once the backend has a future pregame run beyond the current actionable date.</p>
              </div>
            ) : (
              <section className="prediction-grid">
                {nextUpPredictions.map((prediction) => (
                  <PredictionCard key={`${prediction.run_id ?? "run"}-${prediction.game_id ?? "game"}`} prediction={prediction} />
                ))}
              </section>
            )}
          </Panel>
        </section>
      </ScreenState>
    </div>
  );
}
