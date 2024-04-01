def replace_dynamic_fields(data: dict, dynamic_values: dict):
    """
    Recursively traverse the JSON data and replace any '{{ dynamic }}' fields
    with values from the dynamic_values dictionary.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str) and "{{" in value and "}}" in value:
                # Replace '{{ dynamic }}' with corresponding value
                placeholder = value.replace("{{", "").replace("}}", "").strip()
                if placeholder in dynamic_values:
                    data[key] = dynamic_values[placeholder]
            else:
                replace_dynamic_fields(value, dynamic_values)
    elif isinstance(data, list):
        for i in range(len(data)):
            replace_dynamic_fields(data[i], dynamic_values)

    return data
