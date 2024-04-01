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
