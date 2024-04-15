from typing import Literal

from pydantic import BaseModel

from .base import BaseResourceModel


class SmartViewQuery(BaseModel):
    limit: int | None = None
    query: dict = {}
    results_limit: int | None = None
    sort: list = []


class SavedSearch(BaseResourceModel):
    type: Literal["lead", "contact"] = "lead"
    name: str
    s_query: SmartViewQuery = {}
    is_shared: bool
    is_user_dependent: bool


class SmartView(SavedSearch):
    """
    Technically the resource is a 'saved_search' but it's known as a SmartView.
    """
