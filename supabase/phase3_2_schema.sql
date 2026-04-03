create table if not exists phase3_outcome_grades (
    id bigint generated always as identity primary key,
    run_id text not null,
    game_id text not null,
    actual_winner text not null,
    selected_team text not null,
    decision text not null,
    won boolean not null,
    game_status text not null,
    source_name text not null,
    source_version text not null,
    tipoff_time timestamptz not null,
    graded_at timestamptz not null,
    grade_payload jsonb not null,
    created_at timestamptz not null default now(),
    unique (run_id, game_id)
);

create index if not exists idx_phase3_outcome_grades_run_id
    on phase3_outcome_grades (run_id);

create index if not exists idx_phase3_outcome_grades_graded_at
    on phase3_outcome_grades (graded_at);
