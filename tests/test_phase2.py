from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from nba_oracle.config import DEFAULT_LIVE_BUNDLE_PATH
from nba_oracle.runs.build_live_slate import build_live_slate


class Phase2Tests(unittest.TestCase):
    def test_build_live_slate_creates_predictions(self) -> None:
        result = build_live_slate(DEFAULT_LIVE_BUNDLE_PATH)
        self.assertEqual(len(result.snapshots), 3)
        self.assertEqual(len(result.predictions), 3)
        self.assertTrue(any(item.decision == "BET" for item in result.predictions))

    def test_sentiment_can_fail_without_stopping_slate_build(self) -> None:
        payload = json.loads(DEFAULT_LIVE_BUNDLE_PATH.read_text(encoding="utf-8"))
        payload["sentiment"]["success"] = False
        payload["sentiment"]["degraded"] = True
        payload["sentiment"]["error"] = "sentiment_down"
        payload["sentiment"]["records"] = []
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "bundle.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = build_live_slate(path)
            self.assertEqual(len(result.snapshots), 3)
            self.assertTrue(any(provider.kind == "sentiment" and provider.degraded for provider in result.providers))


if __name__ == "__main__":
    unittest.main()
