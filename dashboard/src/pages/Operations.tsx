import { runLearningReview, runLiveSlate, runOutcomeGrading, runScheduler, runStabilityReview } from "../lib/api";
import { useAuth } from "../lib/auth";
import { OperatorActionCard } from "../components/OperatorActionCard";
import { PageHeader } from "../components/PageHeader";

export function OperationsPage() {
  const { token } = useAuth();

  function ensureToken() {
    if (!token) {
      throw new Error("missing_bearer_token");
    }
    return token;
  }

  return (
    <div className="page-stack">
      <PageHeader
        eyebrow="Operations"
        title="Operator actions"
        description="Every job is explicit, confirmable, and returns the real backend payload."
        icon="operations"
      />
      <section className="operations-grid">
        <OperatorActionCard
          title="Run live slate"
          description="Builds the latest live slate and generates a fresh prediction report against current providers."
          confirmLabel="Run live slate"
          onRun={() => runLiveSlate(ensureToken(), true)}
        />
        <OperatorActionCard
          title="Run scheduler once"
          description="Executes the scheduler decision pass using the current runtime state and due-job logic."
          confirmLabel="Run scheduler once"
          onRun={() => runScheduler(ensureToken(), false)}
        />
        <OperatorActionCard
          title="Grade outcomes"
          description="Attempts to backfill official winners into eligible finished predictions and update grading reports."
          confirmLabel="Grade outcomes"
          onRun={() => runOutcomeGrading(ensureToken())}
        />
        <OperatorActionCard
          title="Review stability"
          description="Runs the current stability review to inspect drift, timing, readiness, and containment state."
          confirmLabel="Review stability"
          onRun={() => runStabilityReview(ensureToken(), false)}
        />
        <OperatorActionCard
          title="Run learning review"
          description="Checks whether enough graded evidence exists to open a candidate-only model review."
          confirmLabel="Run learning review"
          onRun={() => runLearningReview(ensureToken())}
        />
      </section>
    </div>
  );
}
