export type ApiErrorPayload = {
  detail?: string;
};

export type AuthLoginResponse = {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  role: string;
};

export type RuntimeJob = {
  job_id?: string;
  status?: string;
  finished_at?: string;
  detail?: Record<string, unknown>;
};

export type RuntimeJobHistoryItem = {
  job_id?: string;
  job_name?: string;
  status?: string;
  started_at?: string;
  finished_at?: string;
  detail?: Record<string, unknown>;
};

export type HealthSnapshot = {
  api?: {
    host?: string;
    port?: number;
    timezone?: string;
  };
  deployment?: {
    target?: string;
  };
  services?: {
    telegram_configured?: boolean;
    gmail_configured?: boolean;
  };
  startup?: {
    created_at?: string;
    status?: string;
    failed_count?: number;
    warning_count?: number;
    deployment?: {
      target?: string;
      public_api_base_url?: string | null;
      allowed_origins?: string[];
      local_autostart_mode?: string;
      local_dashboard_behavior?: string;
      failure_alert_policy?: string;
    };
    checks?: Array<{
      name?: string;
      status?: string;
      detail?: string;
    }>;
  };
  runtime_state?: {
    updated_at?: string | null;
    last_jobs?: Record<string, RuntimeJob>;
    job_history?: RuntimeJobHistoryItem[];
  };
  notifications?: {
    latest_events?: Array<{
      event_id?: string;
      channel?: string;
      event_type?: string;
      success?: boolean;
      destination?: string;
      created_at?: string;
      detail?: Record<string, unknown>;
    }>;
  };
  latest_live?: {
    run_id?: string | null;
    prediction_count?: number;
    provider_count?: number;
    storage_mode?: string | null;
  } | null;
  latest_stability?: {
    review_id?: string | null;
    drift_status?: string | null;
    timing_status?: string | null;
  } | null;
  latest_learning?: {
    review_id?: string | null;
    status?: string | null;
    graded_prediction_count?: number | null;
  } | null;
  latest_outcomes?: {
    newly_graded?: number | null;
    pending_unfinished?: number | null;
  } | null;
  auth?: {
    bootstrapped?: boolean;
  };
};

export type ProviderRecord = {
  name?: string;
  kind?: string;
  source_time?: string;
  source_version?: string;
  trust?: number;
  success?: boolean;
  degraded?: boolean;
  record_count?: number;
  error?: string | null;
};

export type Prediction = {
  game_id?: string;
  matchup_label?: string;
  away_team?: string;
  home_team?: string;
  selected_team?: string;
  decision?: "BET" | "LEAN" | "SKIP" | string;
  reference_bookmaker?: string | null;
  stake_american?: number | null;
  best_american?: number | null;
  close_american?: number | null;
  opening_american?: number | null;
  market_timestamp?: string | null;
  model_probability?: number | null;
  stake_probability?: number | null;
  best_probability?: number | null;
  close_probability?: number | null;
  expected_value?: number | null;
  edge_vs_stake?: number | null;
  source_quality?: number | null;
  reasons?: string[];
};

export type TodayResponse = {
  run_id?: string;
  decision_time?: string;
  storage_mode?: string;
  providers?: ProviderRecord[];
  predictions?: Prediction[];
  stored_paths?: string[];
};

export type PickHistoryRun = {
  run_id?: string;
  prediction_count?: number;
  bet_count?: number;
  lean_count?: number;
  skip_count?: number;
  path?: string;
};

export type PickHistoryResponse = {
  runs: PickHistoryRun[];
};

export type StabilityResponse = {
  review_id?: string;
  created_at?: string;
  drift?: {
    status?: string;
    live_runs_considered?: number;
    graded_predictions?: number;
    retraining_recommended?: boolean;
    reasons?: string[];
    outcome_metrics?: {
      graded_bet_count?: number;
      graded_actionable_count?: number;
      roi?: number | null;
      average_clv?: number | null;
      calibration_gap?: number | null;
    };
  };
  timing?: {
    status?: string;
    runs_considered?: number;
    stale_source_count?: number;
    average_source_age_minutes?: number;
    average_market_age_minutes?: number;
    schedule_fallback_rate?: number;
    notes?: string[];
  };
  market_readiness?: {
    policy?: string;
    markets?: Array<{
      market: string;
      status: string;
      reasons?: string[];
    }>;
  };
  analyst_containment?: {
    status?: string;
    disagreement_count?: number;
    notes?: string[];
  };
  model_review?: {
    review_status?: string;
    candidate_model_version?: string | null;
    reasons?: string[];
  };
  stored_paths?: string[];
};

export type LearningResponse = {
  review_id?: string;
  created_at?: string;
  status?: string;
  active_model_version?: string;
  candidate_model_version?: string | null;
  graded_prediction_count?: number;
  actionable_prediction_count?: number;
  review_only?: boolean;
  weights?: Array<Record<string, unknown>>;
  patterns?: Array<Record<string, unknown>>;
  reasons?: string[];
  stored_paths?: string[];
};

export type ProvidersHealthResponse = {
  run_id?: string;
  providers?: ProviderRecord[];
  degraded_count?: number;
  failed_count?: number;
};

export type OperatorLiveSlateResponse = {
  markdown_report?: string;
  json_report?: string;
  run_id?: string;
  snapshot_count?: number;
  prediction_count?: number;
  storage_mode?: string;
};

export type OperatorSchedulerResponse = {
  ran_at?: string;
  forced?: boolean;
  decisions?: Array<Record<string, unknown>>;
  executed_jobs?: Array<Record<string, unknown>>;
};

export type OutcomeResponse = {
  newly_graded?: number;
  pending_unfinished?: number;
  markdown_report?: string;
  json_report?: string;
};

export type LearningOperatorResponse = {
  review_id?: string;
  status?: string;
  candidate_model_version?: string | null;
  markdown_report?: string;
  json_report?: string;
};
