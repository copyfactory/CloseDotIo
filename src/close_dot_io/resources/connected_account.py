from pydantic import BaseModel, EmailStr

from ..enums import ConnectedAccountTypeEnum
from .base import BaseResourceModel


class ConnectedAccountIdentify(BaseModel):
    email: EmailStr
    name: str


class ConnectedAccount(BaseResourceModel):
    identities: list[ConnectedAccountIdentify]
    synced_calendars: list[EmailStr]
    _type: ConnectedAccountTypeEnum
