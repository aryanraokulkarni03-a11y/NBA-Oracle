from __future__ import annotations

from nba_oracle.providers.base import BundleProvider


class StatsProvider(BundleProvider):
    name = "stats_bundle"
    kind = "stats"
    section_name = "stats"

