from __future__ import annotations

from nba_oracle.providers.base import BundleProvider


class SentimentProvider(BundleProvider):
    name = "sentiment_bundle"
    kind = "sentiment"
    section_name = "sentiment"

