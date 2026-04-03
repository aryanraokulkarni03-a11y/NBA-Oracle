import { useState } from "react";
import { dispatchRuntimeRefresh } from "../lib/runtimeSync";

type OperatorActionCardProps = {
  title: string;
  description: string;
  confirmLabel: string;
  onRun: () => Promise<unknown>;
};

export function OperatorActionCard({ title, description, confirmLabel, onRun }: OperatorActionCardProps) {
  const [armed, setArmed] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const payload = await onRun();
      setResult(JSON.stringify(payload, null, 2));
      setArmed(false);
      dispatchRuntimeRefresh(title);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "unknown_error");
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <article className="operator-card">
      <div className="operator-card__copy">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
      <div className="operator-card__actions">
        {!armed ? (
          <button type="button" className="button button--secondary" onClick={() => setArmed(true)}>
            Review action
          </button>
        ) : (
          <div className="operator-card__confirm">
            <p>This runs immediately against the current backend state.</p>
            <div className="operator-card__buttons">
              <button type="button" className="button button--primary" disabled={isRunning} onClick={() => void handleRun()}>
                {isRunning ? "Running…" : confirmLabel}
              </button>
              <button type="button" className="button button--ghost" disabled={isRunning} onClick={() => setArmed(false)}>
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
      {error ? <pre className="operator-card__output operator-card__output--error">{error}</pre> : null}
      {result ? <pre className="operator-card__output">{result}</pre> : null}
    </article>
  );
}
