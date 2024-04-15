from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseResourceModel(BaseModel):
    id: str | None = None
    organization_id: str | None = None
    date_updated: datetime | None = None
    date_created: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)

    def to_close_object(self, fields_to_exclude: set = None):
        # Exclude status label since we always set the preferred ID.
        default_exclude = {"date_updated", "date_created", "status_label"}
        if fields_to_exclude:
            default_exclude.update(fields_to_exclude)
        return self.model_dump(
            mode="json", by_alias=True, exclude_none=True, exclude=default_exclude
        )
