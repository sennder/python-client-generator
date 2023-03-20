import os
import re

from pathlib import Path
from typing import Any, Dict, List

import chevron

from .utils import resolve_type, sanitize_name, serialize_to_python_code


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def resolve_field_args(property: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map OpenAPI properties to Pydantic Field function args
    """
    args = {}
    if "maxLength" in property:
        args["max_length"] = property["maxLength"]
    if "minLength" in property:
        args["min_length"] = property["minLength"]
    # TODO: decide later if we want the description field or a comment above the line
    # if "description" in property:
    #     args_dict["description"] = property["description"]
    if "default" in property:
        args["default"] = property["default"]

    return args


def serialize_args_dict(args_dict: Dict[str, Any]) -> str:
    args_list = [f"{k}={serialize_to_python_code(v)}" for k, v in args_dict.items()]
    return ", ".join(args_list)


def _get_schema_references(schema: Dict[str, Any]) -> List[str]:
    union_keys = list(set(["allOf", "anyOf", "oneOf"]) & set(schema.keys()))
    if union_keys:
        arr = []
        for p_sub_schema in schema[union_keys[0]]:
            arr += _get_schema_references(p_sub_schema)
        return arr
    elif "type" not in schema:
        return []
    elif schema["type"] == "array":
        return _get_schema_references(schema["items"])
    elif schema["type"] == "object" or "enum" in schema:
        return [schema["title"]]
    else:
        return []


def get_references(model: Dict[str, Any]) -> List[str]:
    """
    Get a list of dependencies for a model

    These come from either their properties or unionized referencing.
    """
    refs = []
    union_keys = list(set(["allOf", "anyOf", "oneOf"]) & set(model.keys()))
    if union_keys:
        return _get_schema_references(model)
    else:
        # Must have properties
        for p_schema in model["properties"].values():
            refs += _get_schema_references(p_schema)

    return [sanitize_name(r) for r in refs]


def get_fields(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    union_keys = list(set(["allOf", "anyOf", "oneOf"]) & set(schema.keys()))
    if union_keys:
        # Handle union cases by creating a __root__ defined model
        return [{"name": "__root__", "type": resolve_type(schema)}]
    else:
        return [
            {
                "name": k,
                "type": resolve_type(v, use_literals=True),
                "optional": "required" not in schema or k not in schema["required"],
                "field_args": serialize_args_dict(resolve_field_args(v)),
            }
            for k, v in schema["properties"].items()
        ]


def _strip_nonexistant_refs(objects: List[Dict[str, Any]]) -> None:
    """
    Remove any references to names not in the objects list
    """
    names = [o["name"] for o in objects]
    for o in objects:
        o["refs"] = [ref for ref in o["refs"] if ref in names]


def _get_ref_index(objects: List[Dict[str, Any]], name: str) -> int:
    return next(i for i, o in enumerate(objects) if o["name"] == name)


def _object_has_binary_properties(object: Dict[str, Any]) -> bool:
    """
    Determine if an object has some properties which are binary
    """
    for p in object.get("properties", {}).values():
        if p.get("type") == "string" and p.get("format") == "binary":
            return True
    return False


def _sort_models(objects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolve object dependencies by walking through the objects list
    and moving any dependencies which are further along in the list
    ahead of us.
    """
    i = 0
    while i < len(objects):
        sorted = False
        for ref in objects[i]["refs"]:
            ref_index = _get_ref_index(objects, ref)
            if ref_index > i:
                objects.insert(i, objects.pop(ref_index))
                sorted = True

        if not sorted:
            i += 1  # Ensure shifted references reprocessed

    return objects


def get_models(schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    objects = (v for v in schemas.values() if "type" not in v or v["type"] == "object")

    models = []
    for o in objects:
        # Skip models with "binary" properties as these are related to file uploads
        # and we handle them with function arguments on the API
        if _object_has_binary_properties(o):
            continue

        p: Dict[str, Any] = {}
        p["refs"] = get_references(o)
        p["name"] = sanitize_name(o["title"])
        p["fields"] = get_fields(o)
        models.append(p)

    _strip_nonexistant_refs(models)
    _sort_models(models)
    return models


def _enum_val_to_name(value: Any) -> str:
    """
    Generate name for each enumeration value.
    """
    if isinstance(value, (int, float)):
        return "NUMBER_" + str(float(value)).replace(".", "_DOT_")
    elif isinstance(value, (str)):
        # TODO: use proper regex replace to insure we don't create variable names non
        # compliant with Python syntax
        char_list = [" ", "-", ".", ",", "&"]
        for c in char_list:
            value = value.replace(c, "_")
        return "".join(re.findall(r"[A-Za-z0-9]+[A-Za-z0-9_]*", value.upper()))
    else:
        raise Exception(f"Unsupported enum value type: {value.__class__}")


def get_enums(schemas: Dict[str, Any]) -> List[Dict[str, Any]]:
    objects = {k: v for k, v in schemas.items() if "enum" in v}

    enums = []
    for _, o in objects.items():
        p: Dict[str, Any] = {}
        p["name"] = sanitize_name(o["title"])
        p["type"] = resolve_type(o)
        p["fields"] = [
            {
                "name": _enum_val_to_name(v),
                "value": serialize_to_python_code(v),
            }
            for v in o["enum"]
        ]
        enums.append(p)

    return enums


def generate_models(swagger: Dict[str, Any], out_file: Path) -> None:
    """
    Generate enums and Pydantic models from the dereferenced OpenAPI file.
    """
    schemas = swagger["components"]["schemas"]

    models = get_models(schemas)
    enums = get_enums(schemas)

    with open(templates_path / "models.py.mustache", "r") as f:
        models_str = chevron.render(f, {"enums": enums, "models": models})

    with open(out_file, "w+") as f:
        f.write(models_str)
