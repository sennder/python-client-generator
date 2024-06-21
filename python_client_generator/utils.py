import re

from typing import Any, Dict, List

import semver

from python_client_generator.exceptions import UnsupportedOpenAPISpec


def lookup_by_ref_parts(obj: Dict[str, Any], ref_parts: List[str]) -> Dict[str, Any]:
    child = obj[ref_parts[0]]
    if len(ref_parts) == 1:
        return child
    else:
        return lookup_by_ref_parts(child, ref_parts[1:])


def dereference(schema: Dict[str, Any], ref: str) -> Dict[str, Any]:
    ref_parts = ref.split("/")[1:]
    return lookup_by_ref_parts(schema, ref_parts)


def dereference_swagger(current: Any, original: Dict[str, Any]) -> Any:
    """
    Dereference an OpenAPI file in place.
    Note: We only dereference the references that are values of a dict, not a list
    """
    if isinstance(current, dict):
        if "$ref" in current:
            current = dereference(original, current["$ref"])

        return {k: dereference_swagger(v, original) for k, v in current.items()}

    elif isinstance(current, list):
        return [dereference_swagger(v, original) for v in current]
    else:
        return current


def serialize_to_python_code(obj: Any) -> str:
    # TODO: Support List/Dict nesting
    if isinstance(obj, (int, float, bool, list, dict)):
        return str(obj)
    else:
        return f'"{obj}"'


def sanitize_name(name: str) -> str:
    return "".join(re.findall(r"[A-Za-z0-9]+[A-Za-z0-9_]*", name))


def to_python_name(name: str) -> str:
    name = name.replace("-", "_")  # Un-dash
    name = re.sub(r"^\d*", "", name)  # Remove digits fom beginning
    return name


def resolve_type(schema: Dict[str, Any], depth: int = 0, use_literals: bool = False) -> str:
    """
    Resolve Python type for a given schema
    """

    if "title" in schema and depth > 0:
        # Just return title for any nested types to prevent elaborating
        # Unions, etc.
        return schema["title"]

    union_keys = list(set(["allOf", "anyOf", "oneOf"]) & set(schema.keys()))
    if union_keys:
        # Handle union cases
        result: List[str] = []
        for sub_schema in schema[union_keys[0]]:
            type_ = resolve_type(sub_schema, depth + 1)
            result.append(type_)
        if len(result) > 1:
            return f"Union[{', '.join(result)}]"
        elif len(result) == 1:
            return result[0]
        else:
            raise Exception(f"Empty union type detected for '{schema['title']}'")
    elif "type" not in schema:
        return "Any"
    elif schema["type"] == "object":
        # If a schema has properties and a title, we can use the title as the type
        # name. Otherwise, we just return a generic Dict[str, Any]
        # This happens when a schema has an object in the properties that doesn't reference another schema.  # noqa E501
        # Example:
        # {
        #    "Schema_Name": {
        #        "title": "Schema_Name",
        #        "type": "object",
        #        "properties": {
        #            "property_name": {
        #                "type": "object",
        #                "properties": {
        #                    "nested_property": {
        #                        "type": "string"
        #                    }
        #                }
        #            }
        #        }
        #    }
        # }

        if "properties" in schema and "title" in schema:
            return sanitize_name(schema["title"])
        else:
            return "Dict[str, Any]"
    elif schema["type"] == "string":
        if schema.get("format") == "date-time":
            return "datetime"
        elif schema.get("format") == "uuid":
            return "UUID"
        elif schema.get("format") == "binary":
            return "httpx._types.FileTypes"
        elif use_literals and len(schema.get("enum", [])) == 1:
            return f"Literal['{schema['enum'][0]}']"
        else:
            return "str"
    elif schema["type"] == "boolean":
        return "bool"
    elif schema["type"] == "integer":
        return "int"
    elif schema["type"] == "number":
        return "float"
    elif schema["type"] == "array":
        return "List[" + resolve_type(schema["items"], depth + 1) + "]"

    raise Exception("property: ", schema)


def assert_openapi_version(schema: Dict[str, Any]) -> None:
    if not schema.get("openapi") or semver.Version.parse(schema.get("openapi")).major != 3:  # type: ignore # noqa: E501
        raise UnsupportedOpenAPISpec("OpenAPI file provided is not version 3.x")


def add_schema_title_if_missing(schemas: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add 'title' key to schemas if missing to prevent issues with type resolution.
    Only adds title to object and enum schemas.

    Args:
        schemas (Dict[str, Any]): Swagger schemas under components.schemas
    Returns:
        Dict[str, Any]: Schemas with 'title' key added if missing

    Raises:
        ValueError: If schema is missing 'type' key
    """

    for k, v in schemas.items():
        if "title" not in v and isinstance(v, dict):
            schema_type = v.get("type")

            if not schema_type:
                raise ValueError(f"Schema {k} is missing 'type' key")

            if schema_type == "object" or (schema_type == "string" and "enum" in v):
                v["title"] = k

    return schemas
