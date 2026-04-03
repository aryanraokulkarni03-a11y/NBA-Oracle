from __future__ import annotations

from nba_oracle.providers.base import BundleProvider


class ScheduleProvider(BundleProvider):
    name = "schedule_bundle"
    kind = "schedule"
    section_name = "schedule"

