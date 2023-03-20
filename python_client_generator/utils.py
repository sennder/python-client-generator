import re

from typing import Any, Dict, List


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
        if "properties" in schema:
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
