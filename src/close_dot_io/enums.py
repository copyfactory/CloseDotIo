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
