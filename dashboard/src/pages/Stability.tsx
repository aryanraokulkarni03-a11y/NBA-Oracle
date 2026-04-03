import { getStability, runStabilityReview } from "../lib/api";
import { formatPercent } from "../lib/format";
import { useAuth } from "../lib/auth";
import { useResource } from "../hooks/useResource";
import { KeyValueList } from "../components/KeyValueList";
import { OperatorActionCard } from "../components/OperatorActionCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ScreenState } from "../components/ScreenState";
import { StatusPill } from "../components/StatusPill";

export function StabilityPage() {
  const { token } = useAuth();
  const { data, isLoading, error, refresh } = useResource(getStability);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Stability"
        title="Model health and drift"
        description="Drift, timing, readiness, and containment with insufficient-data states kept visible."
        icon="stability"
      />
      <ScreenState isLoading={isLoading} error={error}>
        <section className="panel-grid panel-grid--two">
          <Panel title="Drift review" subtitle="Current backend stability report">
            <KeyValueList
              items={[
                { label: "Review ID", value: data?.review_id ?? "n/a" },
                { label: "Drift", value: <StatusPill value={data?.drift?.status} /> },
                { label: "Timing", value: <StatusPill value={data?.timing?.status} /> },
                { label: "Graded predictions", value: data?.drift?.graded_predictions ?? 0 },
                { label: "ROI", value: formatPercent(data?.drift?.outcome_metrics?.roi) },
                { label: "Average CLV", value: formatPercent(data?.drift?.outcome_metrics?.average_clv) },
                { label: "Calibration gap", value: formatPercent(data?.drift?.outcome_metrics?.calibration_gap) },
              ]}
            />
          </Panel>
          <Panel title="Readiness and containment" subtitle="Evidence-backed market locks and analyst containment stay visible.">
            <KeyValueList
              items={[
                { label: "Policy", value: data?.market_readiness?.policy ?? "n/a" },
                { label: "Analyst containment", value: <StatusPill value={data?.analyst_containment?.status} /> },
                { label: "Disagreements", value: data?.analyst_containment?.disagreement_count ?? 0 },
                { label: "Model review", value: data?.model_review?.review_status ?? "n/a" },
                { label: "Candidate model", value: data?.model_review?.candidate_model_version ?? "none" },
              ]}
            />
          </Panel>
        </section>
        <OperatorActionCard
          title="Run stability review"
          description="Re-evaluates the saved baseline, timing logs, drift status, and review bookkeeping against current stored evidence."
          confirmLabel="Run stability review"
          onRun={async () => {
            if (!token) {
              throw new Error("missing_bearer_token");
            }
            const result = await runStabilityReview(token, false);
            await refresh();
            return result;
          }}
        />
      </ScreenState>
    </div>
  );
}
