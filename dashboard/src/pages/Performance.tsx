import { Icon } from "../components/Icons";
import { StatusPill } from "../components/StatusPill";
import { getPickHistory } from "../lib/api";
import { formatDateTime, formatPercent, formatRecord, toHeadline } from "../lib/format";
import { useResource } from "../hooks/useResource";
import { DataTable } from "../components/DataTable";
import { EmptyState } from "../components/EmptyState";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ScreenState } from "../components/ScreenState";

export function PerformancePage() {
  const { data, isLoading, error, refresh } = useResource((token) => getPickHistory(token, 12));
  const rows = data?.runs ?? [];
  const results = data?.results ?? [];
  const summary = data?.summary;

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Performance"
        title="Prediction truth"
        description="This page keeps the audit trail, but it also shows what the model predicted versus what actually happened once games were graded."
        icon="performance"
        actions={
          <button type="button" className="button button--secondary" onClick={() => void refresh()}>
            <Icon name="refresh" className="button__icon" />
            Refresh
          </button>
        }
      />
      <ScreenState isLoading={isLoading} error={error}>
        <Panel
          title="Accuracy snapshot"
          subtitle="Accuracy here measures whether the selected side matched the actual winner after grading. It is truth visibility, not ROI or bankroll advice."
        >
          {summary?.graded_count ? (
            <div className="performance-summary-grid">
              <article className="performance-stat-card">
                <span>Overall accuracy</span>
                <strong>{formatPercent(summary.overall_accuracy, 1)}</strong>
                <small>{formatRecord(summary.correct_count, summary.graded_count)} graded calls matched the winner.</small>
              </article>
              <article className="performance-stat-card">
                <span>BET accuracy</span>
                <strong>{formatPercent(summary.bet_accuracy, 1)}</strong>
                <small>{formatRecord(summary.bet_correct, summary.bet_count)} full bet calls graded so far.</small>
              </article>
              <article className="performance-stat-card">
                <span>LEAN accuracy</span>
                <strong>{formatPercent(summary.lean_accuracy, 1)}</strong>
                <small>{formatRecord(summary.lean_correct, summary.lean_count)} lean calls graded so far.</small>
              </article>
              <article className="performance-stat-card">
                <span>SKIP context</span>
                <strong>{summary.skip_count ?? 0}</strong>
                <small>Skipped calls stay visible for context, but they are not treated as bet hit rate.</small>
              </article>
            </div>
          ) : (
            <EmptyState
              title="No graded truth available yet"
              body="Accuracy appears here once finished games have been graded against the stored prediction history."
            />
          )}
        </Panel>
        <Panel
          title="Recent graded results"
          subtitle="This is the direct predicted-versus-actual ledger for the latest graded games."
        >
          {results.length === 0 ? (
            <EmptyState title="No graded results yet" body="Run outcome grading after games finish to populate the comparison table." />
          ) : (
            <DataTable
              rows={results}
              columns={[
                {
                  key: "matchup",
                  label: "Matchup",
                  render: (item) => (
                    <div className="table-matchup">
                      <strong>{item.matchup_label ?? item.game_id ?? "n/a"}</strong>
                      <span>{formatDateTime(item.tipoff_time)}</span>
                    </div>
                  ),
                },
                {
                  key: "call",
                  label: "Predicted side",
                  render: (item) => (
                    <div className="table-matchup">
                      <strong>{item.selected_team ?? "n/a"}</strong>
                      <span>{toHeadline(item.decision ?? "unknown")}</span>
                    </div>
                  ),
                },
                { key: "actual", label: "Actual winner", render: (item) => item.actual_winner ?? "n/a" },
                {
                  key: "result",
                  label: "Result",
                  render: (item) => <StatusPill value={item.won ? "won" : "lost"} tone={item.won ? "success" : "danger"} />,
                },
                { key: "run", label: "Run", render: (item) => item.run_id ?? "n/a" },
              ]}
            />
          )}
        </Panel>
        <Panel title="Recent runs" subtitle="Use this as the storage audit trail behind the graded truth above.">
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
