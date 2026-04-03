create table if not exists phase3_baselines (
    baseline_fingerprint text primary key,
    created_at timestamptz not null,
    model_version text not null,
    schema_version text not null,
    config_fingerprint text not null,
    replay_report_fingerprint text not null,
    creation_reason text not null,
    baseline_payload jsonb not null
);

create table if not exists phase3_reviews (
    review_id text primary key,
    created_at timestamptz not null,
    baseline_fingerprint text not null references phase3_baselines(baseline_fingerprint) on delete cascade,
    model_version text not null,
    review_payload jsonb not null
);

create table if not exists phase3_timing_events (
    id bigint generated always as identity primary key,
    review_id text not null references phase3_reviews(review_id) on delete cascade,
    game_id text not null,
    event_type text not null,
    source_kind text not null,
    source_name text not null,
    event_payload jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists phase3_analyst_logs (
    id bigint generated always as identity primary key,
    review_id text not null references phase3_reviews(review_id) on delete cascade,
    game_id text not null,
    disagreement_type text not null,
    final_authority text not null,
    log_payload jsonb not null,
    created_at timestamptz not null default now()
);

create table if not exists phase3_model_reviews (
    review_id text primary key,
    created_at timestamptz not null,
    active_model_version text not null,
    candidate_model_version text null,
    review_status text not null,
    promotion_reason text null,
    rollback_reason text null,
    review_payload jsonb not null
);

create index if not exists idx_phase3_reviews_baseline_fingerprint
    on phase3_reviews (baseline_fingerprint);

create index if not exists idx_phase3_timing_events_review_id
    on phase3_timing_events (review_id);

create index if not exists idx_phase3_analyst_logs_review_id
    on phase3_analyst_logs (review_id);

alter table if exists phase3_baselines enable row level security;
alter table if exists phase3_reviews enable row level security;
alter table if exists phase3_timing_events enable row level security;
alter table if exists phase3_analyst_logs enable row level security;
alter table if exists phase3_model_reviews enable row level security;
