from typing import Any, TypeVar

from pydantic import AnyUrl, Field, computed_field

from .base import BaseResourceModel
from .contact import Contact
from .opportunity import Opportunity

T = TypeVar("T", bound=Contact)
Opp = TypeVar("Opp", bound=Opportunity)


class Lead(BaseResourceModel):
    name: str | None = None
    status_label: str | None = None

    contacts: list[T] = []
    opportunities: list[Opp] = []

    description: str | None = None
    html_url: AnyUrl | None = None

    lead_statuses: dict = Field(exclude=True, default={}, repr=False)
    _opp_ids_on_init: set[str] | None = None

    @classmethod
    def create_from_contact(cls, contact: T, **other_lead_data):
        other_lead_data.pop("contacts", None)
        return cls(contacts=[contact], **other_lead_data)

    def model_post_init(self, __context: Any) -> None:
        if not self.opportunities:
            self._opp_ids_on_init = set()
            return
        self._opp_ids_on_init = {opp.id for opp in self.opportunities if opp.id}

    @computed_field
    @property
    def display_name(self) -> str | None:
        return self.name

    @computed_field
    @property
    def status_id(self) -> str | None:
        if not self.status_label:
            return None
        if self.status_label in self.lead_statuses:
            return self.lead_statuses[self.status_label]

    @classmethod
    def get_contact_type(cls):
        # Get the 'Contact' type from the Lead.
        contact_resource = cls.__annotations__["contacts"]
        return contact_resource.__args__[0]
