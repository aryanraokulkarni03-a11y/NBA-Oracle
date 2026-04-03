from __future__ import annotations

from nba_oracle.providers.base import BundleProvider


class OddsProvider(BundleProvider):
    name = "odds_bundle"
    kind = "odds"
    section_name = "odds"

