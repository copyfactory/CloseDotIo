from enum import Enum


class ContactEmailOrPhoneTypeEnum(Enum):
    OFFICE = "office"
    MOBILE = "mobile"
    HOME = "home"
    DIRECT = "direct"
    FAX = "fax"
    URL = "url"
    OTHER = "other"


class ConnectedAccountTypeEnum(Enum):
    GOOGLE = "google"
    CUSTOM_EMAIL = "custom_email"
    ZOOM = "zoom"
    MICROSOFT = "microsoft"
    CALENDLY = "calendly"


class OpportunityStatus(Enum):
    ACTIVE = "active"
    WON = "won"
    LOST = "lost"


class OpportunityPeriod(Enum):
    ONE_TIME = "one_time"
    MONTH = "monthly"
    ANNUAL = "annual"


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
    CUSTOM = "CustomActivity"


class ActivityDirectionEnum(Enum):
    INBOUND = "incoming"
    OUTBOUND = "outgoing"


class SequenceStatusEnum(Enum):
    ACTIVE = "active"
    ERROR = "error"
    FINISHED = "finished"
    GOAL = "goal"
    PAUSED = "paused"


class ActivityMeetingStatusEnum(Enum):
    UPCOMING = "upcoming"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DECLINED_BY_LEAD = "declined-by-lead"
    DECLINED_BY_ORG = "declined-by-org"


class ActivityMeetingAttendeeStatusEnum(Enum):
    NO_REPLY = "noreply"
    YES = "yes"
    NO = "no"
    MAYBE = "maybe"


class WebhookStatusEnum(Enum):
    ACTIVE = "active"
    PAUSED = "paused"


class WebhookFilterTypeEnum(Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    IS_NULL = "is_null"
    NON_NULL = "non_null"
    CONTAINS = "contains"
    AND = "and"
    OR = "or"
    NOT = "not"
    FIELD_ACCESSOR = "field_accessor"
    ANY_ARRAY_VALUE = "any_array_value"


class DefaultActions(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"


class LeadWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    MERGED = "merged"


class TaskWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    COMPLETED = "completed"


class EmailOrSMSActivityWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    SENT = "sent"


class UnsubscribeEmailWebhookActionEnum(Enum):
    CREATED = "created"
    DELETED = "deleted"


class CallActivityWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    ANSWERED = "answered"
    COMPLETED = "completed"


class MeetingActivityWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    SCHEDULED = "scheduled"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskCompletedWebhookActionEnum(Enum):
    CREATED = "created"
    DELETED = "deleted"


class ImportWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    REVERTING = "reverting"
    REVERTED = "reverted"


class ExportWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"


class BulkActionWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
    COMPLETED = "completed"
    PAUSED = "paused"


class MembershipWebhookActionEnum(Enum):
    ACTIVATED = "activated"
    DEACTIVATED = "deactivated"


class SavedSearchWebhookActionEnum(Enum):
    CREATED = "created"
    UPDATED = "updated"
