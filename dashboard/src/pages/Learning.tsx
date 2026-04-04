import { getLearning, runLearningReview } from "../lib/api";
import { formatEvidenceReasons } from "../lib/explain";
import { useAuth } from "../lib/auth";
import { useResource } from "../hooks/useResource";
import { KeyValueList } from "../components/KeyValueList";
import { OperatorActionCard } from "../components/OperatorActionCard";
import { PageHeader } from "../components/PageHeader";
import { Panel } from "../components/Panel";
import { ScreenState } from "../components/ScreenState";
import { StatusPill } from "../components/StatusPill";

export function LearningPage() {
  const { token } = useAuth();
  const { data, isLoading, error, refresh } = useResource(getLearning);

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Learning"
        title="Learning review state"
        description="Candidate-only review flow, graded prediction readiness, and honest insufficient-data handling."
        icon="learning"
      />
      <ScreenState isLoading={isLoading} error={error}>
        <section className="panel-grid panel-grid--two">
          <Panel title="Current learning review" subtitle="Review-safe only. No silent promotions.">
            <KeyValueList
              items={[
                { label: "Review ID", value: data?.review_id ?? "n/a" },
                { label: "Status", value: <StatusPill value={data?.status} /> },
                { label: "Active model", value: data?.active_model_version ?? "n/a" },
                { label: "Candidate model", value: data?.candidate_model_version ?? "none" },
                { label: "Graded predictions", value: data?.graded_prediction_count ?? 0 },
                { label: "Actionable predictions", value: data?.actionable_prediction_count ?? 0 },
              ]}
            />
          </Panel>
          <Panel title="Why the current status exists" subtitle="The UI never upgrades the backend's evidence claim.">
            <ul className="reason-list">
              {formatEvidenceReasons(data?.reasons).map((reason) => (
                <li key={reason}>{reason}</li>
              ))}
            </ul>
          </Panel>
        </section>
        <OperatorActionCard
          title="Run learning review"
          description="Checks whether enough graded evidence exists to open a candidate-model review without promoting anything automatically."
          confirmLabel="Run learning review"
          onRun={async () => {
            if (!token) {
              throw new Error("missing_bearer_token");
            }
            const result = await runLearningReview(token);
            await refresh();
            return result;
          }}
        />
      </ScreenState>
    </div>
  );
}
