from pydantic import BaseModel, EmailStr
from pydantic_extra_types.country import CountryAlpha2

from ..enums import ContactEmailOrPhoneTypeEnum
from .base import BaseResourceModel


class ContactEmailAddress(BaseModel):
    type: ContactEmailOrPhoneTypeEnum = ContactEmailOrPhoneTypeEnum.OFFICE
    email: EmailStr
    is_unsubscribed: bool = False


class ContactPhoneNumber(BaseModel):
    country: CountryAlpha2 | None = "US"
    phone: str
    type: ContactEmailOrPhoneTypeEnum = ContactEmailOrPhoneTypeEnum.OFFICE


class Contact(BaseResourceModel):
    lead_id: str | None = None
    name: str | None = None
    title: str | None = None
    phones: list[ContactPhoneNumber] = []
    emails: list[ContactEmailAddress] = []

    @classmethod
    def create_from_email(cls, email, **other_contact_data):
        other_contact_data.pop("emails", None)
        return cls(emails=[{"email": email}], **other_contact_data)

    @property
    def first_email(self):
        if len(self.emails) > 0:
            return str(self.emails[0].email)
        return ""

    def add_email(
        self,
        email: EmailStr,
        email_type: ContactEmailOrPhoneTypeEnum = ContactEmailOrPhoneTypeEnum.OFFICE,
        is_unsubscribed: bool = False,
    ):
        self.emails.append(
            ContactEmailAddress(
                email=email, type=email_type, is_unsubscribed=is_unsubscribed
            )
        )
        return self.emails
