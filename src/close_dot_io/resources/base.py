from datetime import datetime

from pydantic import BaseModel


class BaseResourceModel(BaseModel):
    id: str | None = None
    organization_id: str | None = None
    date_updated: datetime | None = None
    date_created: datetime | None = None

    def to_close_object(self, fields_to_exclude: set = None):
        default_exclude = {"date_updated", "date_created"}
        if fields_to_exclude:
            default_exclude.update(fields_to_exclude)
        return self.model_dump(
            mode="json", by_alias=True, exclude_none=True, exclude=default_exclude
        )
