from datetime import datetime
from typing import Any

from pydantic import Field, computed_field

from ..enums import OpportunityPeriod, OpportunityStatus
from .base import BaseResourceModel


class Opportunity(BaseResourceModel):
    status_type: OpportunityStatus = OpportunityStatus.ACTIVE
    lead_id: str
    lead_name: str | None = None
    contact_id: str | None = None

    confidence: int | None = None
    status_label: str | None = None
    pipeline_id: str | None = None
    pipeline_name: str | None = None

    value: int | float | None = None
    value_period: OpportunityPeriod = OpportunityPeriod.ONE_TIME
    value_formatted: str | None = None
    value_currency: str | None = None
    expected_value: int | float | None = None
    annualized_value: int | float | None = None
    annualized_expected_value: int | float | None = None

    note: str | None = None
    date_won: datetime | None = None

    opportunity_statuses: dict = Field(exclude=True, default={}, repr=False)

    _initial_hash: bytes = None

    def model_post_init(self, __context: Any) -> None:
        self._initial_hash = self.resource_hash

    @property
    def is_won(self):
        return self.status_type == OpportunityStatus.WON

    @property
    def is_lost(self):
        return self.status_type == OpportunityStatus.LOST

    @property
    def is_active(self):
        return self.status_type == OpportunityStatus.ACTIVE

    @computed_field
    @property
    def status_id(self) -> str | None:
        if not self.status_label:
            return None
        if self.status_label in self.opportunity_statuses:
            return self.opportunity_statuses[self.status_label]
