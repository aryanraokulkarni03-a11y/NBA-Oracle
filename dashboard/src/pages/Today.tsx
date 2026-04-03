import { Icon } from "../components/Icons";
import { getToday } from "../lib/api";
import { useResource } from "../hooks/useResource";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { PredictionCard } from "../components/PredictionCard";
import { ScreenState } from "../components/ScreenState";

export function TodayPage() {
  const { data, isLoading, error, refresh } = useResource(getToday);
  const predictions = data?.predictions ?? [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Today"
        title="Live slate"
        description="Current calls, value signals, and plain-language reasons behind each decision."
        icon="today"
        actions={
          <button type="button" className="button button--secondary" onClick={() => void refresh()}>
            <Icon name="refresh" className="button__icon" />
            Refresh
          </button>
        }
      />
      <ScreenState isLoading={isLoading} error={error}>
        {predictions.length === 0 ? (
          <EmptyState
            title="No live predictions available"
            body="This can be valid on no-slate windows or before the latest live-slate job has produced the current run."
          />
        ) : (
          <section className="prediction-grid">
            {predictions.map((prediction) => (
              <PredictionCard key={prediction.game_id} prediction={prediction} />
            ))}
          </section>
        )}
      </ScreenState>
    </div>
  );
}
