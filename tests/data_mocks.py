import json
from typing import Any, Dict

with open("./generate/openapi.json", "r") as file:
    OPENAPI_SPEC = json.load(file)


def generate_data(model: str):
    model_def = OPENAPI_SPEC["components"]["schemas"][model]
    data: Dict[str, Any] = {}
    for property_name, property in model_def["properties"].items():
        if "anyOf" in property:
            property = property["anyOf"][0]
        property_type = property["type"]
        if property_type == "string":
            if property.get("format") == "date-time":
                data[property_name] = "2000-01-01T00:00:00+00:00"
                continue
            else:
                if property_name == "version":
                    data[property_name] = "1.0.0"
                else:
                    data[property_name] = "mock string"
                continue
        elif property_type == "integer":
            data[property_name] = 1
            continue
        elif property_type == "array":
            if "anyOf" in property["items"]:
                component_ref = property["items"]["anyOf"][0]["$ref"]
            else:
                component_ref = property["items"]["$ref"]
            data[property_name] = [generate_data(component_ref.split("/")[-1])]
            continue
        elif property_type == "object":
            if property.get("additionalProperties", {}).get("type") == "number":
                data[property_name] = {"mock_key": 1}
                continue
        elif property_type == "boolean":
            data[property_name] = True
            continue

        raise TypeError(f"Unsupported type {property_type}")
    return data


class FakeResponse:
    def __init__(self, data):
        if "next_page" in data:
            data["next_page"] = None
        self.data = json.dumps(data, default=str).encode()
        self.status = 200
        self.reason = None
        self.headers = {}
