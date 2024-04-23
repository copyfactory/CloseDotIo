from functools import partial
from typing import Callable, Union

from pydantic import AnyUrl, BaseModel, Field

from ..enums import (
    BulkActionWebhookActionEnum,
    CallActivityWebhookActionEnum,
    DefaultActions,
    EmailOrSMSActivityWebhookActionEnum,
    ExportWebhookActionEnum,
    ImportWebhookActionEnum,
    LeadWebhookActionEnum,
    MeetingActivityWebhookActionEnum,
    MembershipWebhookActionEnum,
    SavedSearchWebhookActionEnum,
    TaskCompletedWebhookActionEnum,
    TaskWebhookActionEnum,
    UnsubscribeEmailWebhookActionEnum,
    WebhookFilterTypeEnum,
    WebhookStatusEnum,
)
from .base import BaseResourceModel
from .event import WebhookEvent


class BasicWebhookFilter(BaseModel):
    type: WebhookFilterTypeEnum
    value: Union[str, None] = None


class FieldAccessorWebhookFilter(BaseModel):
    type: WebhookFilterTypeEnum = WebhookFilterTypeEnum.FIELD_ACCESSOR
    field: str
    filter: Union[BasicWebhookFilter, "FieldAccessorWebhookFilter"]


class AnyArrayValueWebhookFilter(BaseModel):
    type: WebhookFilterTypeEnum = WebhookFilterTypeEnum.ANY_ARRAY_VALUE
    filter: Union[BasicWebhookFilter, "FieldAccessorWebhookFilter"]


class WebhookFilter(BaseModel):
    type: WebhookFilterTypeEnum
    field: str
    filter: Union[
        BasicWebhookFilter,
        FieldAccessorWebhookFilter,
        AnyArrayValueWebhookFilter,
        list[
            Union[
                BasicWebhookFilter,
                FieldAccessorWebhookFilter,
                AnyArrayValueWebhookFilter,
            ]
        ],
    ]


class BaseWebhookEvent(BaseModel):
    object_type: str
    action: DefaultActions
    extra_filter: WebhookFilter | None = None
    event_callback: Callable | list[Callable] = Field(default=None, exclude=True)


class LeadWebhookEvent(BaseWebhookEvent):
    object_type: str = "lead"
    action: LeadWebhookActionEnum


class ContactWebhookEvent(BaseWebhookEvent):
    object_type: str = "contact"


class OpportunityWebhookEvent(BaseWebhookEvent):
    object_type: str = "opportunity"


class LeadTaskWebhookEvent(BaseWebhookEvent):
    object_type: str = "task.lead"
    action: TaskWebhookActionEnum


class EmailWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.email"
    action: EmailOrSMSActivityWebhookActionEnum


class EmailThreadWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.email_thread"


class UnsubscribeWebhookEvent(BaseWebhookEvent):
    object_type: str = "unsubscribed_email"
    action: UnsubscribeEmailWebhookActionEnum


class CallWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.call"
    action: CallActivityWebhookActionEnum


class SMSWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.sms"
    action: EmailOrSMSActivityWebhookActionEnum


class NoteWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.note"


class MeetingWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.meeting"
    action: MeetingActivityWebhookActionEnum


class LeadStatusChangeWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.lead_status_change"


class OpportunityStatusChangeWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.opportunity_status_change"


class TaskCompletedWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.task_completed"
    action: TaskCompletedWebhookActionEnum


class ImportWebhookEvent(BaseWebhookEvent):
    object_type: str = "import"
    action: ImportWebhookActionEnum


class LeadExportWebhookEvent(BaseWebhookEvent):
    object_type: str = "export.lead"
    action: ExportWebhookActionEnum


class OpportunityExportWebhookEvent(LeadExportWebhookEvent):
    object_type: str = "export.opportunity"


class BulkActionDeleteWebhookEvent(BaseWebhookEvent):
    object_type: str = "bulk_action.delete"
    action: BulkActionWebhookActionEnum


class BulkActionUpdateWebhookEvent(BulkActionDeleteWebhookEvent):
    object_type: str = "bulk_action.edit"


class BulkActionEmailWebhookEvent(BulkActionDeleteWebhookEvent):
    object_type: str = "bulk_action.email"


class BulkActionEmailEnrollmentWebhookEvent(BulkActionDeleteWebhookEvent):
    object_type: str = "bulk_action.sequence_subscription"


class LeadCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.lead"


class ContactCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.contact"


class OpportunityCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.opportunity"


class ActivityCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.activity"


class CustomObjectCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.custom_object"


class SharedCustomFieldsWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_fields.shared"


class CustomActivityTypeWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_activity_type"


class CustomActivityWebhookEvent(BaseWebhookEvent):
    object_type: str = "activity.custom_activity"


class CustomObjectTypeWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_object_type"


class CustomObjectWebhookEvent(BaseWebhookEvent):
    object_type: str = "custom_object"


class LeadStatusWebhookEvent(BaseWebhookEvent):
    object_type: str = "status.lead"


class OpportunityStatusWebhookEvent(BaseWebhookEvent):
    object_type: str = "status.opportunity"


class MembershipWebhookEvent(BaseWebhookEvent):
    object_type: str = "membership"
    action: MembershipWebhookActionEnum


class GroupWebhookEvent(BaseWebhookEvent):
    object_type: str = "group"


class SmartViewWebhookEvent(BaseWebhookEvent):
    object_type: str = "saved_search"
    action: SavedSearchWebhookActionEnum


class PhoneNumberWebhookEvent(BaseWebhookEvent):
    object_type: str = "phone_number"


class EmailTemplateWebhookEvent(BaseWebhookEvent):
    object_type: str = "email_template"


class SequenceWebhookEvent(BaseWebhookEvent):
    object_type: str = "sequence"


class SequenceSubscriptionWebhookEvent(BaseWebhookEvent):
    object_type: str = "sequence_subscription"


class CommentWebhookEvent(BaseWebhookEvent):
    object_type: str = "comment"


class CommentThreadWebhookEvent(BaseWebhookEvent):
    object_type: str = "comment_thread"


webhook_event_options = Union[
    BaseWebhookEvent,
    LeadWebhookEvent,
    ContactWebhookEvent,
    OpportunityWebhookEvent,
    LeadTaskWebhookEvent,
    EmailWebhookEvent,
    EmailThreadWebhookEvent,
    UnsubscribeWebhookEvent,
    CallWebhookEvent,
    SMSWebhookEvent,
    NoteWebhookEvent,
    MeetingWebhookEvent,
    LeadStatusChangeWebhookEvent,
    OpportunityStatusChangeWebhookEvent,
    TaskCompletedWebhookEvent,
    ImportWebhookEvent,
    LeadExportWebhookEvent,
    OpportunityExportWebhookEvent,
    BulkActionDeleteWebhookEvent,
    BulkActionUpdateWebhookEvent,
    BulkActionEmailWebhookEvent,
    BulkActionEmailEnrollmentWebhookEvent,
    LeadCustomFieldsWebhookEvent,
    ContactCustomFieldsWebhookEvent,
    OpportunityCustomFieldsWebhookEvent,
    ActivityCustomFieldsWebhookEvent,
    CustomObjectCustomFieldsWebhookEvent,
    SharedCustomFieldsWebhookEvent,
    CustomActivityTypeWebhookEvent,
    CustomActivityWebhookEvent,
    CustomObjectTypeWebhookEvent,
    CustomObjectWebhookEvent,
    LeadStatusWebhookEvent,
    OpportunityStatusWebhookEvent,
    MembershipWebhookEvent,
    GroupWebhookEvent,
    SmartViewWebhookEvent,
    PhoneNumberWebhookEvent,
    EmailTemplateWebhookEvent,
    SequenceWebhookEvent,
    SequenceSubscriptionWebhookEvent,
    CommentWebhookEvent,
    CommentThreadWebhookEvent,
]


class Webhook(BaseResourceModel):
    status: WebhookStatusEnum = WebhookStatusEnum.ACTIVE
    url: AnyUrl
    verify_ssl: bool = True
    events: list[webhook_event_options]
    signature_key: str | None = None

    def get_callbacks(self, event: WebhookEvent) -> list[partial]:
        callbacks = []
        event = event.event
        for registered_event in self.events:
            if (
                registered_event.object_type == event.object_type
                and registered_event.action.value == event.action
            ):
                if not isinstance(registered_event.event_callback, list):
                    funcs = [registered_event.event_callback]
                else:
                    funcs = registered_event.event_callback
                [callbacks.append(partial(callback, event)) for callback in funcs]
        return callbacks
