from pathlib import Path

from nba_oracle.env import get_env_value


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"
LIVE_SOURCES_DIR = DATA_DIR / "live_sources"
RUNTIME_DIR = DATA_DIR / "runtime"
REPORTS_DIR = ROOT_DIR / "reports"

DEFAULT_FIXTURE_PATH = FIXTURES_DIR / "phase1_sample_slate.json"
DEFAULT_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.md"
DEFAULT_JSON_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.json"
DEFAULT_LIVE_BUNDLE_PATH = LIVE_SOURCES_DIR / "phase2_sample_bundle.json"
DEFAULT_LIVE_REPORT_PATH = REPORTS_DIR / "phase2_live_slate_report.md"
DEFAULT_LIVE_JSON_REPORT_PATH = REPORTS_DIR / "phase2_live_slate_report.json"

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
NBA_TEAM_ESTIMATED_METRICS_URL = "https://stats.nba.com/stats/teamestimatedmetrics"
ESPN_NBA_INJURIES_URL = "https://www.espn.com/nba/injuries"
HTTP_TIMEOUT_SECONDS = 20
SUPABASE_RUNS_TABLE = "phase2_runs"
SUPABASE_PROVIDER_TABLE = "phase2_provider_runs"
SUPABASE_SNAPSHOTS_TABLE = "phase2_snapshots"
SUPABASE_PREDICTIONS_TABLE = "phase2_predictions"
