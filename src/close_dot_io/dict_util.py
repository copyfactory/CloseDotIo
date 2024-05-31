"""
This is crazy hacky for now but gets the job done.
"""
import json


def replace_dynamic_fields(data: dict, dynamic_values: dict) -> dict:
    json_data = json.dumps(data)
    for key, value in dynamic_values.items():
        placeholder = "{{ " + key + " }}"
        escaped_value = json.dumps(value)[1:-1]
        json_data = json_data.replace(placeholder, escaped_value)
    return json.loads(json_data)
