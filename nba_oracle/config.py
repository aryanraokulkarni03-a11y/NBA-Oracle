from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
FIXTURES_DIR = DATA_DIR / "fixtures"
REPORTS_DIR = ROOT_DIR / "reports"

DEFAULT_FIXTURE_PATH = FIXTURES_DIR / "phase1_sample_slate.json"
DEFAULT_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.md"
DEFAULT_JSON_REPORT_PATH = REPORTS_DIR / "phase1_replay_report.json"

MIN_SOURCE_QUALITY = 0.55
MIN_EDGE_FOR_LEAN = 0.015
MIN_EDGE_FOR_BET = 0.03
MIN_EV_FOR_BET = 0.02
MAX_PRICE_GAP = 0.03
SOURCE_MAX_AGE_MINUTES = {
    "odds": 30,
    "injury": 90,
    "stats": 720,
    "sentiment": 120,
}

