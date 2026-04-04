import type { Prediction } from "./types";

type Definition = {
  label: string;
  meaning: string;
};

type GuideSection = {
  title: string;
  body: string;
  points: string[];
};

type GuidanceItem = {
  title: string;
  body: string;
};

const BOOKMAKER_NAMES: Record<string, string> = {
  betmgm: "BetMGM",
  draftkings: "DraftKings",
  fanduel: "FanDuel",
  caesars: "Caesars",
  espnbet: "ESPN BET",
  betrivers: "BetRivers",
  pointsbetus: "PointsBet",
  bovada: "Bovada",
  pinnacle: "Pinnacle",
};

const PROVIDER_NAMES: Record<string, string> = {
  nba_schedule_with_odds_fallback: "Official NBA schedule with odds fallback",
  the_odds_api: "The Odds API market feed",
  espn_injuries: "ESPN injuries",
  nba_team_estimated_metrics: "NBA team estimated metrics",
  reddit_sentiment: "Reddit sentiment",
};

const PROVIDER_ERRORS: Record<string, string> = {
  official_schedule_empty_using_odds_fallback:
    "The official schedule feed did not return a usable slate, so the app used the odds feed to build the matchup list.",
  sentiment_deferred: "Sentiment is intentionally deferred in live mode, so it is visible as missing rather than faked.",
  schedule_context_missing: "This provider could not run because the schedule context was missing.",
  odds_api_key_missing: "The odds provider is configured in code, but the live API key is missing.",
  stats_payload_empty: "The stats provider responded, but the payload did not contain usable team rows.",
  injury_page_parse_failed: "The injury source responded, but the page could not be parsed cleanly.",
  bundle_mode_not_supported: "This provider only supports live mode and was skipped in bundle mode.",
  live_mode_not_supported: "This provider is not available in live mode.",
};

const PROVIDER_VERSIONS: Record<string, string> = {
  "scoreboard-v1+odds-fallback-v1": "Official schedule with odds fallback",
  "the-odds-api-v4": "The Odds API v4",
  "espn-injuries-v1": "ESPN injury parser",
  "teamestimatedmetrics-v1": "NBA estimated team metrics",
  "live-v1": "Live sentiment bridge",
};

const REASON_EXPLANATIONS: Record<string, string> = {
  source_quality_below_threshold: "The supporting inputs were not strong enough to trust a bet.",
  edge_too_small: "The model does not have enough advantage over the market price.",
  stake_price_not_competitive: "The reference price was worse than the best price available in the market snapshot.",
  negative_expected_value: "The price is not mathematically worth taking even if the side is likely to win.",
  edge_is_real_but_not_strong: "There may be some value here, but not enough to qualify as a full bet.",
  high_uncertainty_context: "The setup carries too much uncertainty to trust a stronger action signal right now.",
  stale_market_context: "The market snapshot looks stale enough that the system downgraded confidence.",
  heavy_favorite_price_risk: "The team may be strong, but expensive favorite pricing makes the bet easier to overpay for.",
  all_gates_passed: "The model, price, and source-quality checks all cleared the full bet gate.",
};

const REVIEW_REASON_EXPLANATIONS: Record<string, string> = {
  insufficient_data: "There is not enough graded evidence yet to make a stronger claim.",
  no_review: "No candidate model review is open right now.",
  retraining_not_recommended: "Current evidence does not justify a model change.",
  outcome_history_too_shallow: "The graded history is still too small to support a stronger conclusion.",
  actionable_history_too_shallow: "There are not enough actionable graded bets yet to trust a stronger judgment.",
  market_readiness_locked: "The market-readiness policy is still intentionally cautious.",
  baseline_recently_refreshed: "The baseline was refreshed recently, so the system is still building comparison history.",
};

export const TODAY_GUIDANCE: GuidanceItem[] = [
  {
    title: "Start with the decision, not the win chance",
    body: "A likely winner can still be a skip if the market price is too expensive.",
  },
  {
    title: "Use EV and Edge together",
    body: "Positive EV and positive edge suggest value. Negative EV usually means pass, even on strong teams.",
  },
  {
    title: "Treat degraded inputs as caution, not failure",
    body: "Fallback or weaker data does not automatically break the workflow, but it should lower confidence.",
  },
];

export const PROVIDER_GUIDANCE: GuidanceItem[] = [
  {
    title: "Healthy means the source contributed normally",
    body: "The provider returned usable data and did not need a meaningful fallback.",
  },
  {
    title: "Degraded means usable with caution",
    body: "The source still helped, but the app had to fall back, defer, or accept weaker-than-ideal data quality.",
  },
  {
    title: "Failed means do not lean on that source",
    body: "The workflow may still run overall, but that provider did not contribute reliable input to the current run.",
  },
];

function titleCase(value: string) {
  return value
    .replace(/[_-]+/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatBookmakerName(value?: string | null) {
  if (!value) {
    return "Reference source unavailable";
  }
  return BOOKMAKER_NAMES[value.toLowerCase()] ?? titleCase(value);
}

export function formatProviderName(value?: string | null) {
  if (!value) {
    return "Unknown provider";
  }
  return PROVIDER_NAMES[value] ?? titleCase(value);
}

export function formatProviderMeaning(error?: string | null, degraded?: boolean, success?: boolean) {
  if (error && PROVIDER_ERRORS[error]) {
    return PROVIDER_ERRORS[error];
  }
  if (error) {
    return degraded
      ? "This source only partially contributed, and the backend reported a non-standard fallback condition."
      : "This source did not complete cleanly for the current run, so its data should be treated cautiously.";
  }
  if (!success) {
    return "This source failed for the current run, so its input should not be trusted.";
  }
  if (degraded) {
    return "This source still contributed, but with fallback or weaker-than-ideal data quality.";
  }
  return "This source contributed normally to the current run.";
}

export function formatProviderVersion(value?: string | null) {
  if (!value) {
    return "Version details unavailable";
  }
  return PROVIDER_VERSIONS[value] ?? "Internal provider build available in runtime logs";
}

export function formatPredictionReasons(reasons?: string[]) {
  if (!reasons || reasons.length === 0) {
    return ["No explicit reasons were reported for this decision."];
  }
  return reasons.map((reason) => REASON_EXPLANATIONS[reason] ?? titleCase(reason));
}

export function formatRawReasonCode(reason?: string) {
  if (!reason) {
    return "unknown_reason";
  }
  return reason;
}

export function summarizePrediction(prediction: Prediction) {
  const reasons = prediction.reasons ?? [];
  if (reasons.includes("negative_expected_value")) {
    return "The side may be likely to win, but the available price is still too expensive.";
  }
  if (reasons.includes("edge_too_small")) {
    return "The model is too close to the market to claim a real advantage.";
  }
  if (reasons.includes("source_quality_below_threshold")) {
    return "The supporting inputs were not strong enough to trust a bet.";
  }
  if (prediction.decision === "LEAN") {
    return "There is some value here, but not enough to promote it to a full bet.";
  }
  if (prediction.decision === "BET") {
    return "The model, price, and source checks all support a full bet signal.";
  }
  return "This call stays cautious because the value case is not strong enough yet.";
}

export function explainMetric(label: string, prediction: Prediction) {
  switch (label) {
    case "EV":
      return (prediction.expected_value ?? 0) > 0
        ? "Positive expected value suggests the price may be worth taking."
        : "Negative expected value means the price is not worth taking right now.";
    case "Edge":
      return (prediction.edge_vs_stake ?? 0) > 0
        ? "Positive edge means the model is above the market's implied view."
        : "Negative edge means the market is at least as strong as the model's number.";
    case "Reference":
      return "This is the main price the system judged first before comparing it with the best market price.";
    case "Best":
      return "This is the strongest bettor-friendly price seen in the current market snapshot.";
    case "Model":
      return "This is the model's win estimate for the selected side.";
    case "Market time":
      return "This is when the pricing snapshot used by the model was observed.";
    default:
      return "";
  }
}

export function formatEvidenceReasons(reasons?: string[]) {
  if (!reasons || reasons.length === 0) {
    return ["No additional review notes were reported."];
  }
  return reasons.map((reason) => REVIEW_REASON_EXPLANATIONS[reason] ?? titleCase(reason));
}

export const METRIC_DEFINITIONS: Definition[] = [
  {
    label: "EV",
    meaning:
      "Expected value estimates whether the current price is mathematically worth taking. A negative EV usually means skip the bet even if the team is likely to win.",
  },
  {
    label: "Edge",
    meaning:
      "Edge compares the model's win probability with the market's implied probability. Positive edge means the model sees an advantage. Negative edge means it does not.",
  },
  {
    label: "Reference",
    meaning: "Reference is the primary market price used to make the call.",
  },
  {
    label: "Best",
    meaning: "Best is the strongest price the system saw in the available market snapshot.",
  },
  {
    label: "Model",
    meaning: "Model is the system's estimated win probability for the selected side.",
  },
  {
    label: "Market time",
    meaning: "Market time tells you when the pricing snapshot was observed.",
  },
];

export const DECISION_DEFINITIONS: Definition[] = [
  {
    label: "BET",
    meaning: "The model, price, and trust filters all cleared the full action threshold.",
  },
  {
    label: "LEAN",
    meaning: "There may be some value, but not enough strength to justify a full bet signal.",
  },
  {
    label: "SKIP",
    meaning: "The system does not see a trustworthy enough price or signal to justify action.",
  },
  {
    label: "Degraded",
    meaning: "The workflow still ran, but one or more sources used fallback, arrived stale, or were intentionally deferred.",
  },
];

export const GUIDE_SECTIONS: GuideSection[] = [
  {
    title: "What NBA Oracle is doing",
    body: "NBA Oracle is not trying to pick winners only. It is trying to decide whether the available price is worth taking after checking the model, the market, and source quality together.",
    points: [
      "A side can be very likely to win and still be a skip if the price is too expensive.",
      "The dashboard is built for manual betting decisions, not auto-betting.",
      "Warnings and degraded states stay visible on purpose so confidence is never overstated.",
    ],
  },
  {
    title: "How to read the Today page",
    body: "Start with the decision, then read the summary sentence, then use EV and Edge to understand why the call landed there.",
    points: [
      "BET means the full gate passed.",
      "LEAN means there may be value, but the signal is not strong enough for a full bet.",
      "SKIP means the system does not believe the current price is worth taking.",
    ],
  },
  {
    title: "How to use the dashboard for real decisions",
    body: "The safest workflow is to begin on Overview, inspect Today for actual opportunities, check Providers for degraded inputs, and use Operations only when you need to refresh or review the operating state.",
    points: [
      "If providers are degraded, stay more cautious even if the card looks attractive.",
      "If stability or learning says insufficient data, treat that as honest uncertainty, not an error.",
      "Use the best price and the reasoning together. Do not bet off win probability alone.",
    ],
  },
  {
    title: "Why likely winners can still be skips",
    body: "A heavy favorite often carries expensive odds. If the market price already bakes in the win chance, the bet can still be mathematically weak.",
    points: [
      "High model probability does not automatically mean good value.",
      "Negative EV is often the deciding reason on very expensive favorites.",
      "That is why the app shows value metrics separately from raw win probability.",
    ],
  },
];
