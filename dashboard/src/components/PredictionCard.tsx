import { formatAmericanOdds, formatDateTime, formatPercent } from "../lib/format";
import type { Prediction } from "../lib/types";
import { StatusPill } from "./StatusPill";

export function PredictionCard({ prediction }: { prediction: Prediction }) {
  return (
    <article className="prediction-card">
      <header className="prediction-card__header">
        <div>
          <p className="prediction-card__game">{prediction.game_id ?? "Unknown game"}</p>
          <h3>{prediction.selected_team ?? "No side selected"}</h3>
        </div>
        <StatusPill value={prediction.decision} />
      </header>
      <div className="prediction-card__grid">
        <div>
          <span>EV</span>
          <strong>{formatPercent(prediction.expected_value)}</strong>
        </div>
        <div>
          <span>Edge</span>
          <strong>{formatPercent(prediction.edge_vs_stake)}</strong>
        </div>
        <div>
          <span>Reference</span>
          <strong>{formatAmericanOdds(prediction.stake_american)}</strong>
        </div>
        <div>
          <span>Best</span>
          <strong>{formatAmericanOdds(prediction.best_american)}</strong>
        </div>
        <div>
          <span>Model</span>
          <strong>{formatPercent(prediction.model_probability)}</strong>
        </div>
        <div>
          <span>Market time</span>
          <strong>{formatDateTime(prediction.market_timestamp)}</strong>
        </div>
      </div>
      <div className="prediction-card__footer">
        <p className="prediction-card__reasons">
          {(prediction.reasons ?? []).length > 0 ? (prediction.reasons ?? []).join(" • ") : "No reasons reported."}
        </p>
        <p className="prediction-card__bookmaker">{prediction.reference_bookmaker ?? "reference source unavailable"}</p>
      </div>
    </article>
  );
}
