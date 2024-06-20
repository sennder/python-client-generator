import os

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import chevron

from .utils import resolve_type, sanitize_name, serialize_to_python_code, to_python_name


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def resolve_property_type(property: Dict[str, Any]) -> str:
    type_ = resolve_type(property["schema"])
    return (
        f"Optional[{type_}]"
        if property.get("required") is False and property["schema"].get("type") != "boolean"
        else type_
    )


def resolve_property_default(property: Dict[str, Any]) -> Optional[str]:
    if property.get("required") is not False:
        return None

    if "default" in property["schema"]:
        return serialize_to_python_code(property["schema"]["default"])

    return "None"


def get_return_type(responses: Dict[str, Any]) -> Optional[str]:
    def check_if_valid_success_response(key: str) -> bool:
        if key == "default":
            return True

        if key == "2XX":
            return True

        if int(key) >= 200 and int(key) < 300:
            return True

        return False

    # Only consider successful responses
    successful_responses_raw = {
        k: v for k, v in responses.items() if check_if_valid_success_response(k)
    }

    if len(successful_responses_raw) == 0:
        return None

    # Pop the default response if there are multiple successful responses (e.g. 200, 201, 204)
    if len(successful_responses_raw) > 1:
        successful_responses_raw.pop("default", None)

    # Map the responses to a list
    successful_responses = [v for _, v in successful_responses_raw.items()]

    # Not all successful responses have a content key, see: https://spec.openapis.org/oas/v3.0.3#responses-object
    if "content" not in successful_responses[0]:
        return None

    content = successful_responses[0]["content"]

    if "application/json" not in content:
        return None

    schema = successful_responses[0]["content"]["application/json"].get("schema")
    if schema is None:
        return None

    if "type" not in schema:
        return sanitize_name(schema["title"]) if "title" in schema else None

    if schema["type"] == "array":
        return f"List[{resolve_type(schema['items'])}]"
    if schema["type"] == "object":
        return sanitize_name(schema.get("title", "Dict[str, Any]"))


def _get_request_body_params(method: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Only handful of media types are supported:
    - application/json
    - multipart/form-data
    - */* (all types)(only if schema is an object and defined with properties)

    Media types' ranges are not supported at the moment (e.g. 'application/*').
    """
    args = []
    content = method["requestBody"]["content"]

    if "application/json" in content:
        schema = content["application/json"]["schema"]
        args.append(
            {
                "name": "body",  # TODO: think about naming
                "schema": schema,
            }
        )
    elif "multipart/form-data" in content:
        schema = content["multipart/form-data"].get("schema")

        # If schema is not defined with properties, we can't generate arguments
        if schema is None or "properties" not in schema:
            return args

        # Create argument for each multipart upload property
        for k, v in schema["properties"].items():
            args.append({"name": k, "schema": v})
    elif "*/*" in content:
        # Attempt to create argument for all types of request bodies if the schema is of an object and defined with properties
        # See: https://swagger.io/docs/specification/describing-request-body/

        schema = content["*/*"].get("schema")

        if schema is None or "properties" not in schema:
            return args

        for k, v in schema["properties"].items():
            args.append({"name": k, "schema": v})

    return args


def get_function_args(method: Dict[str, Any]) -> List[Dict[str, Any]]:
    params = []

    # Get request body argument(s)
    if "requestBody" in method:
        params += _get_request_body_params(method)

    # Get path, query, and header parameters - sorting first by required and then non-required
    keys = ["path", "query", "header"]
    parameters = method.get("parameters", [])
    for k in keys:
        params += [p for p in parameters if p["in"] == k and p.get("required", False)]
    for k in keys:
        params += [p for p in parameters if p["in"] == k and not p.get("required", False)]

    # Convert params to args format required for templating
    return [
        {
            "name": to_python_name(p["name"]),
            "type": resolve_property_type(p),
            "default": resolve_property_default(p),
            "has_default": resolve_property_default(p) is not None,
        }
        for p in params
    ]


def get_params_by_type(method: Dict[str, Any], type_: str) -> List[Dict[str, str]]:
    """
    :param str type_: `query` or `header`
    """
    params = method.get("parameters", [])
    return [
        {
            "name": p["name"],
            "python_name": to_python_name(p["name"]),
        }
        for p in params
        if p["in"] == type_
    ]


def has_json_body(method: Dict[str, Any]) -> bool:
    try:
        _ = method["requestBody"]["content"]["application/json"]
        return True
    except KeyError:
        return False


def get_multipart_properties(
    method: Dict[str, Any]
) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
    """
    Parse method for any multipart form upload file and data properties.
    """
    try:
        schema = method["requestBody"]["content"]["multipart/form-data"]["schema"]
    except KeyError:
        return ([], [])

    files, data = [], []
    for k, v in schema["properties"].items():
        if v.get("type") == "string" and v.get("format") == "binary":
            files.append({"name": k})
        else:
            data.append({"name": k})

    return (files, data)


@dataclass
class TaggedEndpointDefinition:
    path_name: str
    method_name: str
    method: Dict[str, Any]


def get_endpoints(
    endpoint_defs: Iterable[TaggedEndpointDefinition], sync: bool
) -> List[Dict[str, Any]]:
    endpoints: List[Dict[str, Any]] = []

    for e_def in endpoint_defs:
        e: Dict[str, Any] = {}
        files, data = get_multipart_properties(e_def.method)
        e["name"] = e_def.method["operationId"]
        e["method"] = e_def.method_name.upper()
        e["async"] = not sync
        e["args"] = get_function_args(e_def.method)
        e["path"] = f'f"{e_def.path_name}"' if "{" in e_def.path_name else f'"{e_def.path_name}"'
        e["return_type"] = get_return_type(e_def.method["responses"])
        e["docs"] = e_def.method.get("description", "").replace("\n", "\n        ")
        e["query_params"] = get_params_by_type(e_def.method, "query")
        e["has_query_params"] = len(e["query_params"]) > 0
        e["header_params"] = get_params_by_type(e_def.method, "header")
        e["has_header_params"] = len(e["header_params"]) > 0
        e["has_json_body"] = has_json_body(e_def.method)
        e["multipart_data"] = data
        e["has_multipart_data"] = len(data) > 0
        e["multipart_files"] = files
        e["has_multipart_files"] = len(files) > 0

        endpoints.append(e)

    return endpoints


def get_apis(swagger: Dict[str, Any], group_by_tags: bool, sync: bool) -> List[Dict[str, Any]]:
    paths = swagger["paths"]

    # Group endpoints by tags
    api_groups: Dict[Optional[str], List[TaggedEndpointDefinition]] = {}
    for path_name, path in paths.items():
        for method_name, method in path.items():
            tags = method.get("tags", []) if group_by_tags else [None]
            for tag in tags:
                if tag not in api_groups:
                    api_groups[tag] = []
                api_groups[tag].append(TaggedEndpointDefinition(path_name, method_name, method))

    # Create groups of "apis":
    return [
        {
            "class_name": f"{tag.capitalize() if tag else ''}Api",
            "tag": tag,
            "async": not sync,
            "endpoints": get_endpoints(endpoint_defs, sync),
        }
        for tag, endpoint_defs in api_groups.items()
    ]


def generate_apis(swagger: Dict[str, Any], out_file: Path, group_by_tags: bool, sync: bool) -> None:
    """
    Generate functions for each path in the dereferenced OpenAPI input file.
    """
    apis = get_apis(swagger, group_by_tags, sync)

    with open(templates_path / "apis.py.mustache", "r") as f:
        models_str = chevron.render(f, {"apis": apis})

    with open(out_file, "w+") as f:
        f.write(models_str)
