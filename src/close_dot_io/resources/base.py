import hashlib
from datetime import datetime

from pydantic import BaseModel, ConfigDict

EXPORT_CONFIG = {
    "exclude_none": True,
    "by_alias": True,
    # Exclude status label since we always set the preferred ID.
    "exclude": {"date_updated", "date_created", "status_label"},
}


class BaseResourceModel(BaseModel):
    id: str | None = None
    organization_id: str | None = None
    date_updated: datetime | None = None
    date_created: datetime | None = None

    model_config = ConfigDict(populate_by_name=True)

    @property
    def resource_hash(self):
        return (
            hashlib.md5(self.model_dump_json(**EXPORT_CONFIG).encode("utf-8"))
            .digest()
            .hex()
        )

    def to_close_object(self, fields_to_exclude: set = None):
        config = EXPORT_CONFIG
        if fields_to_exclude:
            config["exclude"].update(fields_to_exclude)
        return self.model_dump(mode="json", **config)
