import { Icon } from "../components/Icons";
import { getPickHistory } from "../lib/api";
import { useResource } from "../hooks/useResource";
import { DataTable } from "../components/DataTable";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ScreenState } from "../components/ScreenState";

export function PerformancePage() {
  const { data, isLoading, error, refresh } = useResource((token) => getPickHistory(token, 12));
  const rows = data?.runs ?? [];

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Performance"
        title="Run history"
        description="Recent run summaries only. No fabricated ROI, just the backend truth we actually store today."
        icon="performance"
        actions={
          <button type="button" className="button button--secondary" onClick={() => void refresh()}>
            <Icon name="refresh" className="button__icon" />
            Refresh
          </button>
        }
      />
      <ScreenState isLoading={isLoading} error={error}>
        <Panel title="Recent runs" subtitle="Run summaries pulled from /api/picks/history">
          {rows.length === 0 ? (
            <EmptyState title="No history available" body="Run history will appear here after live slate jobs generate prediction artifacts." />
          ) : (
            <DataTable
              rows={rows}
              columns={[
                { key: "run_id", label: "Run", render: (item) => item.run_id ?? "n/a" },
                { key: "predictions", label: "Predictions", render: (item) => item.prediction_count ?? 0 },
                { key: "bets", label: "Bets", render: (item) => item.bet_count ?? 0 },
                { key: "leans", label: "Leans", render: (item) => item.lean_count ?? 0 },
                { key: "skips", label: "Skips", render: (item) => item.skip_count ?? 0 },
                { key: "path", label: "Artifact", render: (item) => item.path ?? "n/a" },
              ]}
            />
          )}
        </Panel>
      </ScreenState>
    </div>
  );
}
