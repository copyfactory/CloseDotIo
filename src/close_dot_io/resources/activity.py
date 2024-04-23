from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field

from ..enums import (
    ActivityDirectionEnum,
    ActivityMeetingAttendeeStatusEnum,
    ActivityMeetingStatusEnum,
    ActivityTypeEnum,
)
from .base import BaseResourceModel


class BaseActivity(BaseResourceModel):
    type: ActivityTypeEnum = Field(alias="_type")
    lead_id: str


class CustomActivity(BaseActivity):
    """
    Subclass this model to create your own custom Activities.
    """

    pass


class CallActivity(BaseActivity):
    recording_url: AnyUrl | None = None
    voicemail_url: AnyUrl | None = None
    voicemail_duration: int | None = None
    direction: ActivityDirectionEnum = ActivityDirectionEnum.OUTBOUND
    disposition: str
    source: str
    note_html: str | None = None
    note: str | None = None
    local_phone: str | None = None
    duration: int | None = None
    call_method: str | None = None
    cost: int | None = None
    local_country_iso: str | None = None
    remote_country_iso: str | None = None


class CreatedActivity(BaseActivity):
    contact_id: str | None = None
    source: str | None = None


class EmailEnvelopeEntry(BaseModel):
    email: str
    name: str = ""


class EmailEnvelope(BaseModel):
    sent_from: list[EmailEnvelopeEntry] = Field(alias="from")
    sender: list[EmailEnvelopeEntry]
    to: list[EmailEnvelopeEntry]
    cc: list[EmailEnvelopeEntry] | list[str] = []
    bcc: list[str] = []
    reply_to: list[EmailEnvelopeEntry] | list[str] = []
    date: str
    in_reply_to: list[EmailEnvelopeEntry] | str | None = None
    message_id: str
    subject: str


class AttachmentEntry(BaseModel):
    url: AnyUrl
    filename: str
    content_type: str
    size: int


class EmailActivity(BaseActivity):
    contact_id: str | None = None
    direction: ActivityDirectionEnum
    sender: str
    to: list[str]
    cc: list[str] = []
    bcc: list[str] = []
    subject: str
    envelope: EmailEnvelope
    body_text: str
    body_html: str
    attachments: list[AttachmentEntry] = []
    status: str
    opens: list = []
    template_id: str | None = None
    sequence_subscription_id: str | None = None
    sequence_id: str | None = None
    sequence_name: str | None = None


class EmailThreadActivity(BaseActivity):
    emails: list[EmailActivity] = []
    latest_normalized_subject: str
    n_emails: int
    participants: list[EmailEnvelopeEntry]
    contact_id: str | None = None


class LeadStatusChangeActivity(BaseActivity):
    contact_id: str | None = None
    new_status_id: str | None = None
    new_status_label: str | None = None
    old_status_id: str | None = None
    old_status_label: str | None = None


class MeetingAttendee(BaseModel):
    status: (
        ActivityMeetingAttendeeStatusEnum
    ) = ActivityMeetingAttendeeStatusEnum.NO_REPLY
    user_id: str | None = None
    name: str | None = None
    contact_id: str | None = None
    is_organizer: bool = False
    email: str | None = None


class MeetingActivity(BaseActivity):
    title: str | None = None
    calendar_event_link: AnyUrl | None = None
    note: str | None = None
    source: str | None = None
    location: AnyUrl | str = None
    status: ActivityMeetingStatusEnum = ActivityMeetingStatusEnum.UPCOMING
    contact_id: str | None = None
    duration: int | None = None
    attendees: list[MeetingAttendee] = []
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_recurring: bool = False


class NoteActivity(BaseActivity):
    note_html: str | None = None
    note: str | None = None
    contact_id: str | None = None


class OpportunityStatusChangeActivity(BaseActivity):
    new_status_id: str | None = None

    new_status_label: str | None = None
    new_status_type: str | None = None
    new_pipeline_id: str | None = None
    old_status_id: str | None = None
    old_status_label: str | None = None
    old_status_type: str | None = None
    old_pipeline_id: str | None = None
    opportunity_date_won: datetime | None = None
    opportunity_id: str | None = None
    opportunity_value: int | None = None
    opportunity_value_formatted: int | None = None
    opportunity_value_currency: str | None = None


class SMSActivity(BaseActivity):
    date_sent: datetime | None = None
    direction: ActivityDirectionEnum = ActivityDirectionEnum.OUTBOUND
    status: str | None = None
    cost: str | None = None
    local_phone: str | None = None
    local_country_iso: str | None = None
    text: str | None = None
    contact_id: str | None = None
    attachments: list[AttachmentEntry] = []


class TaskCompletedActivity(BaseActivity):
    task_id: str
    task_text: str
