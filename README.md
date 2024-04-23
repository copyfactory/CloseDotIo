# Close[.]io

[![PyPI - Version](https://img.shields.io/pypi/v/close-dot-io.svg)](https://pypi.org/project/close-dot-io)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/close-dot-io.svg)](https://pypi.org/project/close-dot-io)

-----

Simpler and saner interface for working with the [Close](https://close.com/) API

Features:

 - Automatic create or update of a resource.
 - Automatic schema creation for (most) Close resources with IDE autocomplete.
 - Extendable `Lead`, `Contact`, `Opportunity` and `Activity` model to match your Close custom fields.
 - Retry/rate-limit handling.
 - Webhook validation and callbacks.

<!-- TOC -->
* [Close[.]io](#closeio)
  * [Installation](#installation)
  * [Basic Usage](#basic-usage)
      * [Getting a list of a resource](#getting-a-list-of-a-resource)
      * [Getting a list of leads based on a smartview.](#getting-a-list-of-leads-based-on-a-smartview)
      * [Creating/Updating/Cloning a new contact/lead](#creatingupdatingcloning-a-new-contactlead)
      * [Extending the Contact and Lead resource](#extending-the-contact-and-lead-resource)
      * [Working with Opportunities](#working-with-opportunities)
      * [Webhooks](#webhooks)
  * [License](#license)
<!-- TOC -->

## Installation


```console

pip install close-dot-io

```

## Basic Usage

All methods will ask for which resource you are looking to interact with.

The `Lead` and `Contact` resource can be subclassed to add your own custom fields and logic.

Further down is an example of how to do that.

#### Getting a list of a resource

```python
from close_dot_io import CloseClient, Lead

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(api_key=CLOSE_API_KEY)

# Get 200 leads.
# You get a list of 'Lead' object with the expected Python data types.
leads = client.list(resource=Lead, max_results=200)

print(leads)
# > [
#   Lead(
#       id='lead_xxx',
#       status_label='Cold',
#       description='A sales automation ...',
#       html_url='https://app.close.com/leads/lead_xx',
#       organization_id='orga_xxx',
#       date_updated=datetime.datetime(2024, 4, 14, 17, 43, 38, 77000, tzinfo=TzInfo(UTC)),
#       date_created=datetime.datetime(2024, 2, 29, 11, 3, 12, 544000, tzinfo=TzInfo(UTC)),
#       name='Copyfactory Technologies',
#       contacts=[
#           Contact(id='cont_xxx',
#           organization_id='orga_xxx',
#           date_updated=datetime.datetime(2024, 4, 10, 19, 1, 30, 512000, tzinfo=TzInfo(UTC)),
#           date_created=datetime.datetime(2024, 2, 29, 11, 3, 12, 557000, tzinfo=TzInfo(UTC)),
#           name='Eric Morris',
#           title='co-founder',
#           opportunities=[],
#           phones=[
#               ContactPhoneNumber(
#                   country='CA',
#                   phone='+16xxx',
#                   type=<ContactEmailOrPhoneTypeEnum.OFFICE: 'office'>
#               )
#           ],
#           emails=[
#               ContactEmailAddress(
#                   type=<ContactEmailOrPhoneTypeEnum.OFFICE: 'office'>,
#                   email='eric@cf.io',
#                   is_unsubscribed=False
#              )
#          ]
#      )
#  ])] ...


# Get the first leads ID.
# All `Lead` fields will autocomplete in your IDE.
first_lead = leads[0].id

# Iterate over leads and contacts
for lead in leads:
    for contact in lead.contacts:
        ...

```

Currently supported resources are:

```python
from close_dot_io import (
    Lead,
    Contact,
    Opportunity,
    ConnectedAccount,
    Sequence,
    CallActivity,
    CreatedActivity,
    EmailActivity,
    EmailThreadActivity,
    LeadStatusChangeActivity,
    MeetingActivity,
    NoteActivity,
    OpportunityStatusChangeActivity,
    SMSActivity,
    TaskCompletedActivity,
    SmartView,
)
```
#### Getting a list of leads based on a smartview.

```python
from close_dot_io import CloseClient,Lead

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(api_key=CLOSE_API_KEY)
# By id
leads = client.get_from_smartview(resource=Lead, smartview_id="save_xxx", max_results=10)

# Or search by name (slower since we need to fetch the smartviews to grab the ID)
leads = client.get_from_smartview(resource=Lead, smartview_name="People to follow up with", max_results=1000)

```

#### Creating/Updating/Cloning a new contact/lead

```python
from close_dot_io import CloseClient, Contact, Lead

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(api_key=CLOSE_API_KEY)

# Create using only an Email.
new_contact = Contact.create_from_email(email="j@acme.com", title='CEO')

# Assign contact to lead.
new_lead = Lead.create_from_contact(new_contact, name="Acme Corp")

# Notice how these are bare objects since they do not have a Close id.
print(new_lead.id)
print(new_contact.id)
# > None
# > None

# Lets save the new Lead to Close.
new_lead = client.save(resource=new_lead)

# Now if we print out the ID again we have an ID!
print(new_lead.id)
# >  lead_xxx

# We can now easily edit our new lead
new_lead.name = "Acme Corp Edited from API!"
# And save it. Since the resource has an ID an update is performed.
updated_lead = client.save(resource=new_lead)

# This means cloning is very easy. Just reset the ID and save it again.
updated_lead.id = None
cloned_lead = client.save(resource=new_lead)


```

#### Extending the Contact and Lead resource

You likely have some custom fields that you want to use for your Contacts and Leads.

Here is how to do that.

Under the hood [Pydantic](https://docs.pydantic.dev/) is used to validate models and type annotations.


```python
from close_dot_io import Contact, Lead, CloseClient
from pydantic import Field
from enum import Enum

# Subclass the base Contact object
class MyCustomContact(Contact):
    # The field name can be anything you want.
    # The only required steps are to (1) set the 'alias' parameter with the custom field ID.
    # and (2) set a type annotation to the field.
    # You can copy the ID in the Close custom field settings.
    # **Important** you must prefix the custom field ID with 'custom.{my-id}'
    # Its recommended to set the default to None since your field is likely optional.
    # If you don't set a default and ask for a Contact that doesn't have that field the model will not be created
    # since it would be deemed invalid.
    some_custom_field: str | None = Field(
        alias="custom.cf_xxx",
        default=None,
        description="My awesome custom field.",
    )

    # Number fields are also fine. Set a default if its applicable.
    external_funding: int | None = Field(
        alias="custom.cf_xxx",
        default=0,
        description="Enrichment field for if the contact has received funding.",
    )

    # Decimals are fine too.
    customer_discount: float | None = Field(
        alias="custom.cf_xxx",
        default=0.1,
        description="The discount amount a customer is to receive",
    )


class CustomerServiceRep(Enum):
    ALICE = "rep_id_1"
    CAM = "rep_id_2"


# You can also 'nest' your own models based on your use case or contact pipeline stages.
class PostCustomerContactModel(MyCustomContact):
    # Choices also work.
    customer_rep: CustomerServiceRep | None = Field(
        alias="custom.cf_xxx",
        default=CustomerServiceRep.ALICE,
        description="The ID of the CS rep asigned to this contact.",
    )

# Same exact logic applies to a Lead.
class CustomLead(Lead):
    lead_score: int | None = Field(alias="custom.cf_xxx", default=None)
    # Set the type of contacts you want
    # to have a full Lead representation.
    contacts: list[PostCustomerContactModel] = []

# Now you just create these as you would any other object.
new_contact = PostCustomerContactModel.create_from_email(
    email="j@customer.com",
    title='CEO',
    customer_rep=CustomerServiceRep.CAM
)
new_lead = CustomLead.create_from_contact(
    new_contact,
    status_label='Customer',
    name="Acme Corp",
    lead_score=1
)

CLOSE_API_KEY = "MY-KEY-HERE"

client = CloseClient(api_key=CLOSE_API_KEY)

# Save the new lead with our custom fields
client.save(new_lead)

# Fetch Leads from a smartview using the custom Resource.
leads = client.get_from_smartview(
    resource=CustomLead,
    smartview_name="People to follow up with",
    max_results=10
)
# We now have lead score!
print(leads[0].lead_score)


```

#### Working with Opportunities

Opportunities behave like any other resource and also has support for custom fields.

```python
from close_dot_io import Opportunity
from pydantic import Field


class CustomOpportunity(Opportunity):
    my_custom_opp_field:str | None = Field(default=None, alias="custom.cf_xxx")

```

Extending the custom lead example from earlier we can set our CustomOpportunity class
so that whenever we fetch or interact with the Close API this is the model we are working with.

```python
from close_dot_io import Opportunity, Lead, CloseClient
from pydantic import Field

class CustomLead(Lead):
    lead_score: int | None = Field(alias="custom.cf_xxx", default=None)
    # Set the type of opportunities you want
    # to have a full Lead representation.
    opportunities: list[CustomOpportunity] = []

```
Just like contacts, opportunities are automatically saved when updating a Lead in the Close API.

Adding and updating a new opportunity to a lead.
```python
CLOSE_API_KEY = "MY-KEY-HERE"

client = CloseClient(api_key=CLOSE_API_KEY)

# First get an instance of a Lead
lead = client.get(resource=CustomLead, resource_id="lead_xxx")

# Update the note of the first opportunity
lead.opportunities[0].note = "Updated note from the API"

# Now create your opportunity
my_opp_data = {
    "note": "i hope this deal closes...",
    "confidence": 90,
    "lead_id": lead.id,
    "value_period": "monthly",
    "status": "Active",
    "value": 500,
    "my_custom_opp_field": "My custom value"
}
new_opp = CustomOpportunity(**my_opp_data)

# Add the opportunity to the lead
lead.opportunities.append(new_opp)

# Save it
client.save(lead)
```

Deleting all opportunities on a lead.
```python
CLOSE_API_KEY = "MY-KEY-HERE"

client = CloseClient(api_key=CLOSE_API_KEY)

# First get an instance of a Lead
lead = client.get(resource=CustomLead, resource_id="lead_xxx")

# Set the opportunities to an empty list.
lead.opportunities = []

# Save it
client.save(lead)
```

Deleting all opportunities on a lead that are closed-lost
```python
CLOSE_API_KEY = "MY-KEY-HERE"

client = CloseClient(api_key=CLOSE_API_KEY)

# First get an instance of a Lead
lead = client.get(resource=CustomLead, resource_id="lead_xxx")

# Set the opportunities to only ones that are not closed lost.
lead.opportunities = [opp for opp in lead.opportunities if not opp.is_lost]

# Save it
client.save(lead)
```

#### Webhooks

Webhooks are at the core of all the sales automation we do. Here are some of the ways we use currently use them at Copyfactory:

1. Classifying emails
2. Updating lead and contact custom fields
3. Automating enrollment into sequences
4. Fetching product or user data from other APIs
5. Delegating tasks to priority accounts

This package simplifies the webhook experience by attaching callback functions to events you want to listen to.

We use FastAPI but the process is similar for any other web framework.

[All of the events](https://developer.close.com/resources/event-log/list-of-events/) from the
Close event list are currently supported.

For this example we are going to listen on new notes on a lead.

```python
from close_dot_io import (
  NoteWebhookEvent, Webhook, Event, NoteActivity, BasicWebhookFilter,
  CloseClient, Lead, WebhookFilter, WebhookFilterTypeEnum, FieldAccessorWebhookFilter
)

# all events follow the nomenclature of '{resource}WebhookEvent'
# Check the documentation for the supported actions for that event. The default are 'created' 'updated' 'deleted'
event = NoteWebhookEvent(action="created")

# Extra filters are also supported depending on the granularity you need.
extra_filter = WebhookFilter(
        type=WebhookFilterTypeEnum.FIELD_ACCESSOR,
        field="data",
        filter=FieldAccessorWebhookFilter(
          field=Lead.field("name"),
            filter=BasicWebhookFilter(
                type=WebhookFilterTypeEnum.EQUALS,
                value="user_lAm7YqrzZj10t1GLK5eTOaRgPkaChswxydbhUhGRbbM"
            )
        )
    )
event_with_filter = NoteWebhookEvent(action="created", extra_filter=extra_filter)

```

On its own this is not very useful. Let's attach a function so that when this event occurs, we can run our custom logic.

```python
from close_dot_io import (
  NoteWebhookEvent, Webhook, Event, NoteActivity, BasicWebhookFilter,
  CloseClient, Lead, WebhookFilter, WebhookFilterTypeEnum, FieldAccessorWebhookFilter
)

CLOSE_API_KEY = "MY-KEY-HERE"

client = CloseClient(api_key=CLOSE_API_KEY)

# all functions (referred to as 'callbacks')  will receive an Event object which you can use.
def handle_new_note(event: Event):
  # With the event object we can create a partial NoteActivity
  partial_note = NoteActivity(**event.data)
  # We can iterate over the fields that changed
  for field in event.changed_fields:
    print(field)
  # We can see the previous object
  previous_note = NoteActivity(**event.previous_data)
  # Finally if we need the full lead object we can of course fetch it using the API.
  lead = client.get(resource=Lead, resource_id=event.lead_id)
  # Or even the object that we received
  note = client.get(resource=NoteActivity, resource_id=event.object_id)


# Now all we need to do is attach the function to the event.
event = NoteWebhookEvent(action="created", event_callback=[handle_new_note])

# Next we create the webhook.
wh = Webhook(url="{MY-DOMAIN-HERE}/process_close_webhook", events=[event])
# **IMPORTANT** When you create the webhook you will receive a 'signature_key', copy that as it won't be shown again.
# **IMPORTANT** You only need to create the webhook once!
wh = client.save(resource=wh)
print(wh.signature_key)

```

At this point we have:

1. Defined the events we want to run logic against
2. Created a webhook that Close will start sending those events to.
3. Copied a `signature_key` and pasted it somewhere so that we can secure our endpoint.

Next we need to connect our webframework to these events. The following example uses FastAPI and puts all the code
together.

```python
from close_dot_io import (
  NoteWebhookEvent, Webhook, Event, NoteActivity, BasicWebhookFilter,
  CloseClient, Lead, WebhookFilter, WebhookFilterTypeEnum, FieldAccessorWebhookFilter, WebhookEvent
)
from close_dot_io.security import is_webhook_data_valid

from typing import Annotated
from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException, Header, Body
import os

CLOSE_API_KEY = "MY-KEY-HERE"


# all functions (referred to as 'callbacks')  will receive an Event object which you can use.
def handle_new_note(event: Event):
    partial_note = NoteActivity(**event.data)
    print(partial_note)

# Now all we need to do is attach the function to the event.
event = NoteWebhookEvent(action="created", event_callback=[handle_new_note])
my_webhook = Webhook(url="{MY-DOMAIN-HERE}/process_close_webhook", events=[event])

# Create a function to validate the incoming request. For FastAPI it would look like this.
async def validate_close_signature(
        close_sig_timestamp: Annotated[str, Header()], close_sig_hash: Annotated[str, Header()], event: Annotated[dict, Body()]
):
    if not is_webhook_data_valid(
        close_sig_timestamp=close_sig_timestamp, close_sig_hash=close_sig_hash, payload=event,
        # This is the signature key you copied when you first created the webhook. We store it in our .env file.
        signature_key=os.environ["CLOSE_WEBHOOK_SIGNATURE_KEY"]
    ):
        raise HTTPException(status_code=422, detail="Webhook signature is not valid.")

app = FastAPI()

# Create the route which will always be a POST request with the payload being the WebhookEvent.
# This example uses the FastAPI background tasks functionality to run our callbacks but you could easily
# Pass this off to a message broker or worker process.
@app.post("/process_close_webhook", dependencies=[Depends(validate_close_signature)])
async def process_close_webhook(event: WebhookEvent, background_tasks: BackgroundTasks):
    # The webhook has a method `get_callbacks` which returns a list of function partials that match the target
    # event action and resource type.
    callbacks = my_webhook.get_callbacks(event=event)
    for callback in callbacks:
        background_tasks.add_task(callback.func, *callback.args, **callback.keywords)
    return {}

```

> Huge thank you to the Close team for creating a best-in-class product and API!

Close API documentation: https://developer.close.com/


## License

`close-dot-io` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
