from pathlib import Path

from nba_oracle.env import get_env_value


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"
LIVE_SOURCES_DIR = DATA_DIR / "live_sources"
RUNTIME_DIR = DATA_DIR / "runtime"
STABILITY_DIR = DATA_DIR / "stability"
RUNTIME_STATE_DIR = DATA_DIR / "runtime_state"
LEARNING_DIR = DATA_DIR / "learning"
AUTH_DIR = DATA_DIR / "auth"
REPORTS_DIR = ROOT_DIR / "reports"

DEFAULT_FIXTURE_PATH = FIXTURES_DIR / "phase1_sample_slate.json"
DEFAULT_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.md"
DEFAULT_JSON_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.json"
DEFAULT_LIVE_BUNDLE_PATH = LIVE_SOURCES_DIR / "phase2_sample_bundle.json"
DEFAULT_LIVE_REPORT_PATH = REPORTS_DIR / "phase2_live_slate_report.md"
DEFAULT_LIVE_JSON_REPORT_PATH = REPORTS_DIR / "phase2_live_slate_report.json"
DEFAULT_STABILITY_REPORT_PATH = REPORTS_DIR / "phase3_stability_report.md"
DEFAULT_STABILITY_JSON_REPORT_PATH = REPORTS_DIR / "phase3_stability_report.json"
DEFAULT_OUTCOME_REPORT_PATH = REPORTS_DIR / "phase3_outcome_grading_report.md"
DEFAULT_OUTCOME_JSON_REPORT_PATH = REPORTS_DIR / "phase3_outcome_grading_report.json"
DEFAULT_LEARNING_REPORT_PATH = REPORTS_DIR / "phase4_learning_report.md"
DEFAULT_LEARNING_JSON_REPORT_PATH = REPORTS_DIR / "phase4_learning_report.json"

MIN_SOURCE_QUALITY = 0.55
MIN_EDGE_FOR_LEAN = 0.015
MIN_EDGE_FOR_BET = 0.03
MIN_EV_FOR_BET = 0.02
MAX_PRICE_GAP = 0.03
CALIBRATION_MIN_ACTIONABLE_COUNT = 6
CALIBRATION_MIN_POPULATED_BINS = 2
CALIBRATION_MAX_MEAN_ABS_GAP = 0.12
CALIBRATION_MAX_BIN_ABS_GAP = 0.18
SOURCE_MAX_AGE_MINUTES = {
    "odds": 30,
    "injury": 90,
    "stats": 720,
    "sentiment": 120,
}

DEFAULT_STORAGE_MODE = "local"
DEFAULT_ODDS_PROVIDER = "the_odds_api"
DEFAULT_INJURY_PROVIDER = "espn_nba_api"
DEFAULT_SENTIMENT_PROVIDER = "reddit_only"
DEFAULT_ALLOWED_ORIGINS = "http://127.0.0.1:3000,http://localhost:3000"


def _env_int(name: str, default: int) -> int:
    raw_value = get_env_value(name)
    if raw_value in {None, ""}:
        return default
    return int(raw_value)


def _env_bool(name: str, default: bool) -> bool:
    raw_value = get_env_value(name)
    if raw_value in {None, ""}:
        return default
    return str(raw_value).strip().lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str) -> tuple[str, ...]:
    raw_value = get_env_value(name, default) or default
    return tuple(item.strip() for item in raw_value.split(",") if item.strip())

ODDS_API_KEY = get_env_value("ODDS_API_KEY")
SUPABASE_URL = get_env_value("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = get_env_value("SUPABASE_SERVICE_ROLE_KEY")
STORAGE_MODE = get_env_value(
    "ORACLE_STORAGE_MODE",
    "dual" if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY else DEFAULT_STORAGE_MODE,
) or DEFAULT_STORAGE_MODE
ODDS_API_BASE_URL = "https://api.the-odds-api.com/v4"
ODDS_API_SPORT = "basketball_nba"
ODDS_API_REGIONS = "us"
ODDS_API_MARKETS = "h2h"
ODDS_API_ODDS_FORMAT = "american"
ODDS_REFERENCE_BOOKMAKER = get_env_value("ODDS_REFERENCE_BOOKMAKER")
NBA_SCOREBOARD_URL = "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"
NBA_SCOREBOARD_V2_URL = "https://stats.nba.com/stats/scoreboardv2"
NBA_TEAM_ESTIMATED_METRICS_URL = "https://stats.nba.com/stats/teamestimatedmetrics"
ESPN_NBA_INJURIES_URL = "https://www.espn.com/nba/injuries"
HTTP_TIMEOUT_SECONDS = 20
SUPABASE_RUNS_TABLE = "phase2_runs"
SUPABASE_PROVIDER_TABLE = "phase2_provider_runs"
SUPABASE_SNAPSHOTS_TABLE = "phase2_snapshots"
SUPABASE_PREDICTIONS_TABLE = "phase2_predictions"

PHASE3_DRIFT_WINDOW_RUNS = _env_int("PHASE3_DRIFT_WINDOW_RUNS", 30)
PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN = _env_int("PHASE3_MIN_GRADED_PICKS_FOR_RETRAIN", 100)
PHASE3_MARKET_UNLOCK_MIN_SAMPLE = _env_int("PHASE3_MARKET_UNLOCK_MIN_SAMPLE", 100)
PHASE3_MARKET_UNLOCK_POLICY = get_env_value("PHASE3_MARKET_UNLOCK_POLICY", "strict") or "strict"
PHASE3_ANALYST_LOGGING_ENABLED = _env_bool("PHASE3_ANALYST_LOGGING_ENABLED", True)
PHASE3_AUTO_REFRESH_BASELINE = _env_bool("PHASE3_AUTO_REFRESH_BASELINE", True)
PHASE3_MIN_LIVE_RUNS_FOR_DRIFT = _env_int("PHASE3_MIN_LIVE_RUNS_FOR_DRIFT", 3)
PHASE3_MAX_PROVIDER_DEGRADATION_RATE = float(
    get_env_value("PHASE3_MAX_PROVIDER_DEGRADATION_RATE", "0.35") or "0.35"
)
PHASE3_MAX_ROI_DELTA = float(get_env_value("PHASE3_MAX_ROI_DELTA", "0.25") or "0.25")
PHASE3_MAX_CLV_DELTA = float(get_env_value("PHASE3_MAX_CLV_DELTA", "0.03") or "0.03")
PHASE3_MAX_CALIBRATION_GAP_DELTA = float(
    get_env_value("PHASE3_MAX_CALIBRATION_GAP_DELTA", "0.10") or "0.10"
)
PHASE3_MAX_SKIP_RATE_DELTA = float(get_env_value("PHASE3_MAX_SKIP_RATE_DELTA", "0.20") or "0.20")
PHASE3_MAX_ACTIVE_BET_RATE_DELTA = float(
    get_env_value("PHASE3_MAX_ACTIVE_BET_RATE_DELTA", "0.15") or "0.15"
)
PHASE3_MAX_SOURCE_QUALITY_DELTA = float(
    get_env_value("PHASE3_MAX_SOURCE_QUALITY_DELTA", "0.08") or "0.08"
)
PHASE3_MAX_EDGE_DELTA = float(get_env_value("PHASE3_MAX_EDGE_DELTA", "0.02") or "0.02")
PHASE3_BASELINE_SCHEMA_VERSION = get_env_value("PHASE3_BASELINE_SCHEMA_VERSION", "1.1") or "1.1"
PHASE3_BASELINES_TABLE = "phase3_baselines"
PHASE3_REVIEWS_TABLE = "phase3_reviews"
PHASE3_TIMING_EVENTS_TABLE = "phase3_timing_events"
PHASE3_ANALYST_LOGS_TABLE = "phase3_analyst_logs"
PHASE3_MODEL_REVIEWS_TABLE = "phase3_model_reviews"
PHASE3_OUTCOME_GRADES_TABLE = "phase3_outcome_grades"

ORACLE_API_HOST = get_env_value("ORACLE_API_HOST", "127.0.0.1") or "127.0.0.1"
ORACLE_API_PORT = _env_int("ORACLE_API_PORT", 8000)
ORACLE_DASHBOARD_PORT = _env_int("ORACLE_DASHBOARD_PORT", 3000)
ORACLE_TIMEZONE = get_env_value("ORACLE_TIMEZONE", "Asia/Calcutta") or "Asia/Calcutta"
ORACLE_ALLOWED_ORIGINS = _env_list("ORACLE_ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
ORACLE_PUBLIC_API_BASE_URL = get_env_value("ORACLE_PUBLIC_API_BASE_URL", "") or ""
ORACLE_DEPLOYMENT_TARGET = get_env_value("ORACLE_DEPLOYMENT_TARGET", "vercel-cloudflare-supabase") or "vercel-cloudflare-supabase"
ORACLE_LOCAL_AUTOSTART_MODE = get_env_value("ORACLE_LOCAL_AUTOSTART_MODE", "login") or "login"
ORACLE_LOCAL_DASHBOARD_BEHAVIOR = get_env_value("ORACLE_LOCAL_DASHBOARD_BEHAVIOR", "manual") or "manual"
ORACLE_FAILURE_ALERT_POLICY = get_env_value("ORACLE_FAILURE_ALERT_POLICY", "telegram-primary") or "telegram-primary"
ORACLE_PASSWORD_HASH = get_env_value("ORACLE_PASSWORD_HASH")
ORACLE_SECRET_KEY = get_env_value("ORACLE_SECRET_KEY")
ORACLE_TOKEN_TTL_MINUTES = _env_int("ORACLE_TOKEN_TTL_MINUTES", 60 * 24)
ORACLE_AUTH_MAX_FAILED_ATTEMPTS = _env_int("ORACLE_AUTH_MAX_FAILED_ATTEMPTS", 5)
ORACLE_AUTH_LOCKOUT_SECONDS = _env_int("ORACLE_AUTH_LOCKOUT_SECONDS", 60)
ORACLE_API_RATE_LIMIT_PER_MINUTE = _env_int("ORACLE_API_RATE_LIMIT_PER_MINUTE", 60)

TELEGRAM_BOT_TOKEN = get_env_value("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = get_env_value("TELEGRAM_CHAT_ID")
GMAIL_SENDER = get_env_value("GMAIL_SENDER")
GMAIL_APP_PASSWORD = get_env_value("GMAIL_APP_PASSWORD")
GMAIL_RECIPIENT = get_env_value("GMAIL_RECIPIENT")
ORACLE_NOTIFY_MIDNIGHT = _env_bool("ORACLE_NOTIFY_MIDNIGHT", True)
ORACLE_NOTIFY_COMPLETION = _env_bool("ORACLE_NOTIFY_COMPLETION", True)
ORACLE_NOTIFY_FAILURE = _env_bool("ORACLE_NOTIFY_FAILURE", True)
ORACLE_NOTIFY_WEEKLY = _env_bool("ORACLE_NOTIFY_WEEKLY", False)
ORACLE_SCHEDULER_LIVE_TARGET_MINUTES = _env_int("ORACLE_SCHEDULER_LIVE_TARGET_MINUTES", 120)
ORACLE_SCHEDULER_LIVE_WINDOW_MINUTES = _env_int("ORACLE_SCHEDULER_LIVE_WINDOW_MINUTES", 30)

LEARNING_MIN_GRADED_PICKS = _env_int("LEARNING_MIN_GRADED_PICKS", 100)
LEARNING_PATTERN_MIN_SAMPLE = _env_int("LEARNING_PATTERN_MIN_SAMPLE", 15)
LEARNING_ENABLE_AUTO_REVIEW = _env_bool("LEARNING_ENABLE_AUTO_REVIEW", True)
LEARNING_REVIEW_ONLY = _env_bool("LEARNING_REVIEW_ONLY", True)

PHASE4_RUNTIME_JOBS_TABLE = "phase4_runtime_jobs"
PHASE4_LEARNING_REVIEWS_TABLE = "phase4_learning_reviews"
PHASE4_NOTIFICATION_EVENTS_TABLE = "phase4_notification_events"
