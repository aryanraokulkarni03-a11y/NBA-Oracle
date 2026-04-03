from __future__ import annotations

from nba_oracle.providers.base import BundleProvider


class InjuryProvider(BundleProvider):
    name = "injuries_bundle"
    kind = "injury"
    section_name = "injuries"

