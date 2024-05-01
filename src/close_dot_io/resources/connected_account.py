from pydantic import BaseModel, EmailStr

from ..enums import ConnectedAccountTypeEnum
from .base import BaseResourceModel


class ConnectedAccountIdentify(BaseModel):
    email: EmailStr
    name: str


class ConnectedAccount(BaseResourceModel):
    # todo turns out the _type has a different model for each. Need to handle that better.
    identities: list[ConnectedAccountIdentify] = []
    synced_calendars: dict | list[str] | None = None
    _type: ConnectedAccountTypeEnum
