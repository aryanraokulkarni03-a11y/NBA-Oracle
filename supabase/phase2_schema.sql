create table if not exists phase2_runs (
    run_id text primary key,
    decision_time timestamptz not null,
    provider_count integer not null,
    snapshot_count integer not null,
    prediction_count integer not null,
    created_at timestamptz not null default now()
);

create table if not exists phase2_provider_runs (
    id bigint generated always as identity primary key,
    run_id text not null references phase2_runs(run_id) on delete cascade,
    kind text not null,
    provider_name text not null,
    source_time timestamptz not null,
    source_version text not null,
    trust double precision not null,
    success boolean not null,
    degraded boolean not null,
    error text null,
    record_count integer not null,
    raw_payload jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists phase2_snapshots (
    id bigint generated always as identity primary key,
    run_id text not null references phase2_runs(run_id) on delete cascade,
    game_id text not null,
    decision_time timestamptz not null,
    tipoff_time timestamptz not null,
    away_team text not null,
    home_team text not null,
    market_payload jsonb not null,
    sources_payload jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists phase2_predictions (
    id bigint generated always as identity primary key,
    run_id text not null references phase2_runs(run_id) on delete cascade,
    game_id text not null,
    selected_team text not null,
    decision text not null,
    reference_bookmaker text not null,
    reference_american integer not null,
    best_american integer not null,
    close_american integer not null,
    opening_american integer null,
    market_timestamp timestamptz null,
    model_probability double precision not null,
    reference_probability double precision not null,
    best_probability double precision not null,
    close_probability double precision not null,
    expected_value double precision not null,
    edge_vs_reference double precision not null,
    source_quality double precision not null,
    reasons jsonb not null,
    source_scores jsonb not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_phase2_provider_runs_run_id
    on phase2_provider_runs (run_id);

create index if not exists idx_phase2_snapshots_run_id
    on phase2_snapshots (run_id);

create index if not exists idx_phase2_predictions_run_id
    on phase2_predictions (run_id);

alter table if exists phase2_runs enable row level security;
alter table if exists phase2_provider_runs enable row level security;
alter table if exists phase2_snapshots enable row level security;
alter table if exists phase2_predictions enable row level security;
