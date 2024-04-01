from pydantic import Field

from .base import BaseResourceModel
from .contact import Contact


class Lead(BaseResourceModel):
    name: str | None = Field(alias="display_name", default=None)
    contacts: list[Contact] = []

    @classmethod
    def create_from_contact(cls, contact: Contact, **other_lead_data):
        other_lead_data.pop("contacts", None)
        return cls(contacts=[contact], **other_lead_data)
