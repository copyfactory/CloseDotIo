from datetime import datetime
from enum import Enum

from pydantic import AnyUrl, BaseModel, Field

from .base import BaseResourceModel


class ActivityTypeEnum(Enum):
    CALL = "Call"
    CREATED = "Created"
    EMAIL = "Email"
    EMAIL_THREAD = "EmailThread"
    LEAD_STATUS_CHANGE = "LeadStatusChange"
    MEETING = "Meeting"
    NOTE = "Note"
    OPPORTUNITY_STATUS_CHANGE = "OpportunityStatusChange"
    SMS = "SMS"
    TASK_COMPLETED = "TaskCompleted"


class DirectionEnum(Enum):
    INBOUND = "inbound"
    OUTBOUND = "outgoing"


class BaseActivity(BaseResourceModel):
    _type: ActivityTypeEnum
    lead_id: str


class CallActivity(BaseActivity):
    recording_url: AnyUrl | None = None
    voicemail_url: AnyUrl | None = None
    voicemail_duration: int | None = None
    direction: DirectionEnum = DirectionEnum.OUTBOUND
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
    cc: list[str] = []
    bcc: list[str] = []
    reply_to: list[str] = []
    date: str
    in_reply_to: str | None = None
    message_id: str
    subject: str


class AttachmentEntry(BaseModel):
    url: AnyUrl
    filename: str
    content_type: str
    size: int


class EmailActivity(BaseActivity):
    contact_id: str | None = None
    direction: DirectionEnum
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


class MeetingStatusEnum(Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DECLINED_BY_LEAD = "declined-by-lead"
    DECLINED_BY_ORG = "declined-by-org"


class AttendeeStatusEnum(Enum):
    NO_REPLY = "noreply"
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"


class MeetingAttendee(BaseModel):
    status: AttendeeStatusEnum = AttendeeStatusEnum.NO_REPLY
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
    status: MeetingStatusEnum = MeetingStatusEnum.UPCOMING
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
    direction: DirectionEnum = DirectionEnum.OUTBOUND
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
