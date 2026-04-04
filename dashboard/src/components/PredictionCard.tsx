import {
  explainMetric,
  formatBookmakerName,
  formatPredictionReasons,
  formatRawReasonCode,
  summarizePrediction,
} from "../lib/explain";
import { formatAmericanOdds, formatDateTime, formatPercent } from "../lib/format";
import type { Prediction } from "../lib/types";
import { StatusPill } from "./StatusPill";

type MetricItemProps = {
  label: string;
  value: string;
  note: string;
};

function MetricItem({ label, value, note }: MetricItemProps) {
  return (
    <div className="metric-item">
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

export function PredictionCard({ prediction }: { prediction: Prediction }) {
  const reasonLines = formatPredictionReasons(prediction.reasons);
  const matchupLabel = prediction.matchup_label ?? prediction.game_id ?? "Unknown matchup";

  return (
    <article className="prediction-card">
      <header className="prediction-card__header">
        <div>
          <p className="prediction-card__game">{matchupLabel}</p>
          <h3>{prediction.selected_team ?? "No side selected"}</h3>
        </div>
        <StatusPill value={prediction.decision} />
      </header>
      <div className="prediction-card__grid">
        <MetricItem
          label="EV"
          value={formatPercent(prediction.expected_value)}
          note={explainMetric("EV", prediction)}
        />
        <MetricItem
          label="Edge"
          value={formatPercent(prediction.edge_vs_stake)}
          note={explainMetric("Edge", prediction)}
        />
        <MetricItem
          label="Reference"
          value={formatAmericanOdds(prediction.stake_american)}
          note={explainMetric("Reference", prediction)}
        />
        <MetricItem
          label="Best"
          value={formatAmericanOdds(prediction.best_american)}
          note={explainMetric("Best", prediction)}
        />
        <MetricItem
          label="Model"
          value={formatPercent(prediction.model_probability)}
          note={explainMetric("Model", prediction)}
        />
        <MetricItem
          label="Market time"
          value={formatDateTime(prediction.market_timestamp)}
          note={explainMetric("Market time", prediction)}
        />
      </div>
      <div className="prediction-card__footer">
        <div className="prediction-card__callout">
          <p className="prediction-card__callout-label">What this call means</p>
          <p className="prediction-card__insight">{summarizePrediction(prediction)}</p>
        </div>
        <div className="prediction-card__callout">
          <p className="prediction-card__callout-label">Why it landed here</p>
          <ul className="reason-list prediction-card__reason-list">
            {reasonLines.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        </div>
        <p className="prediction-card__bookmaker">Reference book: {formatBookmakerName(prediction.reference_bookmaker)}</p>
        <details className="prediction-card__advanced">
          <summary>Advanced details</summary>
          <div className="prediction-card__advanced-body">
            <p>
              <strong>Game ID:</strong> {prediction.game_id ?? "n/a"}
            </p>
            <p>
              <strong>Source quality:</strong> {formatPercent(prediction.source_quality)}
            </p>
            <p>
              <strong>Raw reason codes:</strong>{" "}
              {prediction.reasons && prediction.reasons.length > 0
                ? prediction.reasons.map((reason) => formatRawReasonCode(reason)).join(", ")
                : "none"}
            </p>
          </div>
        </details>
      </div>
    </article>
  );
}
