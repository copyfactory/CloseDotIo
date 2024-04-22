from pydantic import BaseModel

from .base import BaseResourceModel


class Meta(BaseModel):
    bulk_action_id: str | None = None
    merge_source_lead_id: str | None = None
    merge_destination_lead_id: str | None = None
    request_method: str | None = None
    request_path: str | None = None


class Event(BaseResourceModel):
    object_type: str
    object_id: str
    lead_id: str | None = None
    action: str
    changed_fields: list[str] | None = None
    data: dict | None = None
    previous_data: dict | None = None
    meta: Meta | None = Meta()


class WebhookEvent(BaseModel):
    subscription_id: str
    event: Event
