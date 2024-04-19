import re
import time
from typing import Type, TypeVar
from urllib.parse import urlencode

import requests
from pydantic import ValidationError, create_model

from .resources import BaseResourceModel, Contact, Lead, Opportunity, SmartView
from .resources.activity import BaseActivity

MAX_RETRY = 5

CAMEL_CASE_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


R = TypeVar("R", bound=BaseResourceModel)


class CloseClient:
    def __init__(
        self,
        api_key: str,
        model_depth: int = 10,
    ):
        self.base_url = "https://api.close.com/api/v1/"
        if not api_key:
            raise ValueError("No API key provided!")
        self.api_key = api_key
        self.model_depth = model_depth

        self.lead_statuses: dict = {}
        self.opportunity_statuses: dict = {}

    @staticmethod
    def get_model_fields_for_query(
        lead_resource: Type[R] = None, contact_resource: Type[R] = None
    ) -> dict:
        q = {"_fields": {}}
        if lead_resource:
            lead_fields = lead_resource.model_fields
            q["_fields"]["lead"] = list(lead_fields.keys()) + ["custom"]

        if contact_resource:
            contact_fields = contact_resource.model_fields
            q["_fields"]["contact"] = list(contact_fields.keys()) + ["custom"]
        return q

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

    def get_resource_or_none(self, resource: Type[R], data: dict) -> R | None:
        try:
            return resource(
                **data
                | {
                    "lead_statuses": self.lead_statuses,
                    "opportunity_statuses": self.opportunity_statuses,
                }
            )
        except ValidationError:
            # todo log?
            return None

    def set_opportunity_statuses(self):
        if self.opportunity_statuses:
            return
        res = self.dispatch(endpoint="/status/opportunity/").get("data")
        self.opportunity_statuses = {
            status.get("label"): status.get("id") for status in res
        }

    def set_lead_statuses(self):
        if self.lead_statuses:
            return
        res = self.dispatch(endpoint="/status/lead/").get("data")
        self.lead_statuses = {status.get("label"): status.get("id") for status in res}

    def get_base_model(self, model: Type[R] | R):
        """
        Keep checking model inheritance until we hit the model that is directly above
        'BaseResourceModel' or 'BaseActivity' as this is what we use
        to build the resource endpoint route.

        This allows for deep inheritance of Lead/Contact/Oppertunity models.
        :param model:
        :param max_depth:
        :return:
        """
        # fetch the status IDs once.
        if not self.opportunity_statuses:
            self.set_opportunity_statuses()
        if not self.lead_statuses:
            self.set_lead_statuses()
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
            if last_class in [BaseResourceModel, BaseActivity]:
                class_found = True
            else:
                model = last_class
                recur_count += 1
            if recur_count >= self.model_depth:
                break
        return model

    def resource_to_endpoint(self, resource: R, resource_id=None) -> str:
        base_model = self.get_base_model(model=resource)
        snake_case = CAMEL_CASE_PATTERN.sub("_", base_model.__name__).lower()
        if snake_case.endswith("_activity"):
            activity_object = snake_case[: snake_case.index("_activity")]
            snake_case = f"activity/{activity_object}"
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

    def run_pagination(
        self, resource_endpoint: str, max_results: int = 100, url_params: dict = None
    ) -> list:
        items = []
        url_params = url_params or {}
        limit = 100

        def fetch_data(new_url):
            res = self.dispatch(endpoint=new_url)
            items.extend(res.get("data", []))
            return res.get("has_more", False)

        while len(items) < max_results:
            encoded_params = urlencode(
                url_params | {"_skip": len(items), "_limit": limit}
            )
            url = f"{resource_endpoint}/?{encoded_params}"
            has_more = fetch_data(url)
            if not has_more:
                break

        return items[:max_results]

    def run_query(self, query: dict, max_results: int) -> list:
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
        self,
        resource: Type[R],
        query: dict,
        fields: dict = None,
        max_results: int = 100,
    ) -> list[R]:
        if self.get_base_model(resource) != Contact:
            raise ValueError(
                "Resource must be a subclass of 'Contact' to fetch contacts."
            )
        if not query:
            raise ValueError("No query provided. Maybe you meant to use '.list()'?")
        contacts = []
        fields = fields or self.get_model_fields_for_query(contact_resource=resource)
        query = query | fields
        for contact in self.run_query(query=query, max_results=max_results):
            if contact := self.get_resource_or_none(resource=resource, data=contact):
                contacts.append(contact)
        return contacts

    def get_leads(
        self,
        resource: Type[R],
        query: dict,
        fields: dict = None,
        max_results: int = 100,
    ) -> list[R]:
        leads = []
        if self.get_base_model(resource) != Lead:
            raise ValueError("Resource must be a subclass of 'Lead' to fetch leads.")
        if not query:
            raise ValueError("No query provided. Maybe you meant to use '.list()'?")
        fields = fields or self.get_model_fields_for_query(
            lead_resource=resource, contact_resource=resource.get_contact_type()
        )
        query = query | fields
        for lead in self.run_query(query=query, max_results=max_results):
            if lead := self.get_resource_or_none(resource=resource, data=lead):
                leads.append(lead)
        return leads

    def get_from_smartview(
        self,
        resource: Type[R],
        smartview_name: str = None,
        smartview_id: str = None,
        max_results: int = 100,
    ):
        if not smartview_name and not smartview_id:
            raise ValueError("One of smartview name or ID is required.")
        q, q_type = {}, None
        if smartview_id:
            sv = self.get(resource=SmartView, resource_id=smartview_id)
            if not sv:
                raise ValueError(f"SmartView '{smartview_id}' was not found.")
            q, q_type = sv.s_query, sv.type
        if not q:
            params = (
                {"type": self.resource_to_endpoint(resource)}
                if resource
                else {"type__in": "lead,contact"}
            )
            svs = self.list(resource=SmartView, url_params=params)
            for smart_view in svs:
                if smart_view.name == smartview_name:
                    q, q_type = smart_view.s_query, smart_view.type
                    break
        if not q:
            raise ValueError(f"SmartView '{smartview_name}' was not found.")
        query = q.model_dump(mode="json")
        if q_type == "lead":
            return self.get_leads(
                resource=resource, query=query, max_results=max_results
            )
        # If Lead resource passed but target return is Contact we extract out the Contact field.
        # means if you dont know if your smartview is Lead or Contact can just throw in Lead and
        # it's handled.
        if self.get_base_model(resource) == Lead:
            resource = resource.get_contact_type()
        return self.get_contacts(
            resource=resource, query=query, max_results=max_results
        )

    def list(
        self, resource: Type[R], max_results: int = 100, url_params: dict = None
    ) -> list[R]:
        items = []
        for item in self.run_pagination(
            self.resource_to_endpoint(resource),
            max_results=max_results,
            url_params=url_params,
        ):
            if item := self.get_resource_or_none(resource=resource, data=item):
                items.append(item)
        return items

    def get(
        self, resource: Type[R], resource_id: str = None, resource_instance=None
    ) -> R:
        if not resource_id and not resource_instance:
            raise ValueError("resource_id or resource_instance must be declared.")
        if resource_instance and not resource_instance.id:
            raise ValueError("Your instance does not have an ID!")
        return resource(
            **self.dispatch(
                endpoint=self.resource_to_endpoint(
                    resource, resource_id or resource_instance.id
                )
            )
        )

    def save(self, resource: R, lead_id: str = None) -> R:
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
        if base_resource == Lead:
            resource.lead_statuses = self.lead_statuses
            # if Lead we also need to save the opps if they have changed or are new.
            # Any ids remaining in the list should be deleted since they are no longer on the lead.
            current_opps = resource._opp_ids_on_init
            for opp in resource.opportunities:
                if opp.id and opp.id in current_opps:
                    current_opps.remove(opp.id)
                # if no ID we can save since we know its new.
                # if initial content hash is not the same model has changed so we can save as well.
                if not opp.id or opp.resource_hash != opp._initial_hash:
                    self.save(resource=opp)

            for opp_to_delete in current_opps:
                self.dispatch(endpoint=f"/opportunity/{opp_to_delete}", method="DELETE")

        if base_resource == Opportunity:
            resource.opportunity_statuses = self.opportunity_statuses
        data = resource.to_close_object()
        if lead_id:
            data["lead_id"] = lead_id
        res = self.dispatch(endpoint=endpoint, method=method, json_data=data)
        resource = resource.__class__(**res)
        # If target resource was a contact, grab it instead of lead.
        if base_resource == Contact and swapped_to_lead:
            resource = resource.contacts[0]
        return resource

    def delete(self, resource_instance: R) -> None:
        endpoint = self.resource_to_endpoint(
            resource=resource_instance, resource_id=resource_instance.id
        )
        if not resource_instance.id:
            raise ValueError("Can't delete without an ID.")
        self.dispatch(endpoint=endpoint, method="DELETE")
