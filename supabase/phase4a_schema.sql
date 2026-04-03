create table if not exists phase4_runtime_jobs (
  job_id text primary key,
  job_name text not null,
  status text not null,
  started_at timestamptz not null,
  finished_at timestamptz not null,
  detail_payload jsonb not null default '{}'::jsonb
);

create index if not exists phase4_runtime_jobs_job_name_idx
  on phase4_runtime_jobs (job_name, finished_at desc);

create table if not exists phase4_notification_events (
  event_id text primary key,
  channel text not null,
  event_type text not null,
  success boolean not null,
  destination text not null,
  created_at timestamptz not null,
  detail_payload jsonb not null default '{}'::jsonb
);

create index if not exists phase4_notification_events_created_idx
  on phase4_notification_events (created_at desc);

create table if not exists phase4_learning_reviews (
  review_id text primary key,
  created_at timestamptz not null,
  status text not null,
  candidate_model_version text,
  learning_payload jsonb not null default '{}'::jsonb
);

create index if not exists phase4_learning_reviews_created_idx
  on phase4_learning_reviews (created_at desc);

alter table if exists phase4_runtime_jobs enable row level security;
alter table if exists phase4_notification_events enable row level security;
alter table if exists phase4_learning_reviews enable row level security;
