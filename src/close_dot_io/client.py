import re
import time

import requests
from pydantic import ValidationError, create_model

from .resources import BaseResourceModel, Contact, Lead

MAX_RETRY = 5

CAMEL_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


class CloseClient:
    def __init__(
        self,
        api_key: str,
        contact_model: type[Contact] = Contact,
        lead_model: type[Lead] = Lead,
        model_depth: int = 5,
    ):
        self.base_url = "https://api.close.com/api/v1/"
        if not api_key:
            raise ValueError("No API key provided!")
        self.api_key = api_key
        self.contact_model = contact_model
        self.lead_model = lead_model
        self.model_depth = model_depth

    @staticmethod
    def _get_rate_limit_sleep_time(response):
        """Get rate limit window expiration time from response if the response
        status code is 429.
        """
        try:
            if "error" in response.json():
                return int(float(response.json()["error"]["rate_reset"]))
        except (AttributeError, KeyError, ValueError, Exception):
            return 60

    @staticmethod
    def get_resource_or_none(resource, data: dict):
        try:
            return resource(**data)
        except ValidationError:
            # todo log?
            return None

    def get_base_model(self, model):
        """
        Keep checking model inheritance until we hit the model that is directly above
        'BaseResourceModel' as this is what we use to build the resource endpoint route.

        This allows for deep inheritance of Lead/Contact/Oppertunity models.
        :param model:
        :param max_depth:
        :return:
        """
        class_found = False
        recur_count = 0
        while not class_found:
            try:
                last_class = model.__bases__
            # handle instance of class
            except AttributeError:
                last_class = model.__class__
            if last_class:
                if isinstance(last_class, tuple):
                    last_class = last_class[0]
            if last_class == BaseResourceModel:
                class_found = True
            else:
                model = last_class
                recur_count += 1
            if recur_count >= self.model_depth:
                break
        return model

    def resource_to_endpoint(self, resource, resource_id=None):
        base_model = self.get_base_model(model=resource)
        snake_case = CAMEL_CASE_PATTERN.sub("_", base_model.__name__).lower()
        return f"{snake_case}/{resource_id}" if resource_id else snake_case

    def dispatch(self, endpoint, method="GET", params=None, json_data=None):
        url = f"{self.base_url}{endpoint}"
        request_data = {
            "auth": (self.api_key, ""),
            "headers": {"content-type": "application/json"},
            "params": params,
            "url": url,
            "json": json_data,
        }
        for _ in range(MAX_RETRY):
            try:
                res = requests.request(method=method.upper(), **request_data)
                if res.ok:
                    return res.json()
                elif res.status_code == 429:
                    sleep_time = self._get_rate_limit_sleep_time(res)
                    time.sleep(sleep_time)
                    continue
            except Exception as e:
                raise e
        return {}

    def get_model_fields_for_query(self, include_lead=True, include_contact=True):
        q = {"_fields": {}}
        if include_lead:
            lead_fields = self.lead_model.model_fields
            q["_fields"]["lead"] = list(lead_fields.keys()) + ["custom"]

        if include_contact:
            contact_fields = self.contact_model.model_fields
            q["_fields"]["contact"] = list(contact_fields.keys()) + ["custom"]
        return q

    def run_pagination(self, resource, max_results: int = 100):
        items = []
        limit = 100
        url = f"{resource}/?_skip={len(items)}&_limit={limit}"
        res = self.dispatch(endpoint=url)
        items += res.get("data", [])
        has_more = res.get("has_more", False)
        if has_more:
            while not len(items) >= max_results:
                url = f"{resource}/?_skip={len(items)}&_limit={limit}"
                res = self.dispatch(endpoint=url)
                items += res.get("data", [])
                has_more = res.get("has_more", False)
                if not has_more:
                    break
        return items[:max_results]

    def run_query(self, query: dict, max_results: int):
        max_results = min(max_results, 9500)
        items = []
        query["_limit"] = 100
        res = self.dispatch(method="POST", json_data=query, endpoint="data/search/")
        items += res.get("data", [])
        cursor = res.get("cursor", None)
        while cursor is not None:
            if len(items) >= max_results:
                break
            query["cursor"] = cursor
            res = self.dispatch(method="POST", json_data=query, endpoint="data/search/")
            items += res.get("data", [])
            cursor = res.get("cursor", None)
        return items[:max_results]

    def get_contacts(
        self, query: dict, fields: dict = None, max_results: int = 100
    ) -> list[type[Contact]]:
        contacts = []
        fields = fields or self.get_model_fields_for_query(include_lead=False)
        query = query | fields
        for contact in self.run_query(query=query, max_results=max_results):
            if contact := self.get_resource_or_none(
                resource=self.contact_model, data=contact
            ):
                contacts.append(contact)
        return contacts

    def get_leads(
        self, query: dict, fields: dict = None, max_results: int = 100
    ) -> list[type[Lead]]:
        leads = []
        fields = fields or self.get_model_fields_for_query()
        query = query | fields
        for lead in self.run_query(query=query, max_results=max_results):
            if lead := self.get_resource_or_none(resource=self.lead_model, data=lead):
                leads.append(lead)
        return leads

    def list(self, resource, max_results: int = 100):
        items = []
        for item in self.run_pagination(
            self.resource_to_endpoint(resource), max_results=max_results
        ):
            if item := self.get_resource_or_none(resource=resource, data=item):
                items.append(item)
        return items

    def get(self, resource, resource_id: str = None, resource_instance=None):
        if not resource_id and not resource_instance:
            raise ValueError("model_id or model_instance must be declared.")
        if resource_instance and not resource_instance.id:
            raise ValueError("Your instance does not have an ID!")
        return resource(
            **self.dispatch(
                endpoint=self.resource_to_endpoint(
                    resource, resource_id or resource_instance.id
                )
            )
        )

    def save(self, resource, lead_id: str = None):
        base_resource = self.get_base_model(resource)
        swapped_to_lead = False
        # check if trying to create direct Contact, if so make Lead.
        if base_resource == Contact and resource.id is None and lead_id is None:
            # gen Lead model using Contact field schema.
            dynamic_lead_model = create_model(
                "Lead",
                contacts=(list[resource], None),
                __base__=Lead,
            )
            swapped_to_lead = True
            resource = dynamic_lead_model.create_from_contact(contact=resource)
        endpoint = self.resource_to_endpoint(resource=resource, resource_id=resource.id)
        method = "PUT" if resource.id else "POST"
        data = resource.to_close_object()
        if lead_id:
            data["lead_id"] = lead_id
        res = self.dispatch(endpoint=endpoint, method=method, json_data=data)
        resource = resource.__class__(**res)
        # If target resource was a contact, grab it instead of lead.
        if base_resource == Contact and swapped_to_lead:
            resource = resource.contacts[0]
        return resource

    def delete(self, resource_instance) -> None:
        endpoint = self.resource_to_endpoint(
            resource=resource_instance, resource_id=resource_instance.id
        )
        if not resource_instance.id:
            raise ValueError("Can't delete without an ID.")
        self.dispatch(endpoint=endpoint, method="DELETE")
