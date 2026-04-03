from pathlib import Path


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
