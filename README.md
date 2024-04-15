# Close[.]io

[![PyPI - Version](https://img.shields.io/pypi/v/close-dot-io.svg)](https://pypi.org/project/close-io-flows)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/close-dot-io.svg)](https://pypi.org/project/close-io-flows)

-----

Simpler and saner interface for working with the [Close](https://close.com/) API

Features:

 - Automatic create or update of a resource.
 - Automatic schema creation for (most) Close resources with IDE autocomplete.
 - Extendable Lead and Contact model to match your Close custom fields.
 - Retry/rate-limit handling.


## Installation


```console

pip install close-dot-io

```

## Basic Usage

#### Getting a list of a resource

```python
from close_dot_io import CloseClient, Lead

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(
    api_key=CLOSE_API_KEY
)

# Get 200 leads.
# You get a list of 'Lead' object with the expected Python data types.
leads:list[Lead] = client.list(resource=Lead, max_results=200)

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
    SmartView
)
```
#### Getting a list of leads based on a smartview.

```python
from close_dot_io import CloseClient

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(
    api_key=CLOSE_API_KEY
)
# By id
leads = client.get_from_smartview(smartview_id="save_xxx", max_results=10)

# Or search by name (slower since we need to fetch the smartviews to grab the ID)
leads = client.get_from_smartview(smartview_name="People to follow up with", max_results=10)

```

#### Creating/Updating/Cloning a new contact/lead

```python
from close_dot_io import CloseClient, Contact, Lead

CLOSE_API_KEY = "MY-KEY-HERE"

# Create a connection to Close.
client = CloseClient(
    api_key=CLOSE_API_KEY
)

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
    # The name can be anything you want.
    # The only required steps are to (1) set the 'alias' parameter with the custom field ID.
    # and (2) set a type annotation to the field.
    # You can copy the ID in the Close custom field settings.
    # **Important** you must prefix the custom field ID with 'custom.{my-id}'
    # Its recommended to set the default to None since your field is likely optional.
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

# To save you need to bind your custom Contact and Lead models to the client.
# Now whenever you ask for Leads or Contacts
# you will get the bound object returned with all the custom fields automatically transposed.
client = CloseClient(
    api_key=CLOSE_API_KEY,
    contact_model=PostCustomerContactModel,
    lead_model=CustomLead
)

client.save(new_lead)

```


> Huge thank you to the Close team for creating a best-in-class product and API!

Close API documentation: https://developer.close.com/


## License

`close-dot-io` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
