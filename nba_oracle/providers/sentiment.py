from __future__ import annotations

from datetime import datetime

from nba_oracle.models import ProviderResponse
from nba_oracle.providers.base import BundleProvider


class SentimentProvider(BundleProvider):
    name = "reddit_sentiment"
    kind = "sentiment"
    section_name = "sentiment"

    def fetch_live(
        self,
        decision_time: datetime,
        context: dict[str, ProviderResponse],
    ) -> ProviderResponse:
        return self.degraded_response(
            decision_time,
            error="sentiment_deferred",
            raw_payload={},
            trust=0.0,
        )
