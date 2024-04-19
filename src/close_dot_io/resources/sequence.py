from pydantic import BaseModel

from ..enums import SequenceStatusEnum
from .base import BaseResourceModel


class SubscriptionCountByStatus(BaseModel):
    active: int = 0
    error: int = 0
    finished: int = 0
    goal: int = 0
    paused: int = 0


class Step(BaseResourceModel):
    step_type: str
    delay: int
    email_template_id: str | None = None
    required: bool
    step_allowed_delay: str | int | None = None
    threading: str | None = None


class Sequence(BaseResourceModel):
    name: str = ""
    status: SequenceStatusEnum = SequenceStatusEnum.ACTIVE
    steps: list[Step] = []
    subscription_counts_by_status: (
        SubscriptionCountByStatus
    ) = SubscriptionCountByStatus()
