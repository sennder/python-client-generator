import typing as t

from contextlib import contextmanager

import pytest

from python_client_generator.exceptions import UnsupportedOpenAPISpec
from python_client_generator.utils import (
    add_schema_title_if_missing,
    assert_openapi_version,
    dereference_swagger,
)


@contextmanager
def does_not_raise() -> t.Generator:
    yield


@pytest.mark.parametrize(
    "raw_schema, expected_schema",
    [
        (
            {"X": {"type": "string", "enum": ["A", "B"]}},
            {
                "X": {
                    "title": "X",
                    "type": "string",
                    "enum": ["A", "B"],
                }
            },
        ),  # Should add title to enum schema
        (
            {
                "X": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "b": {"type": "string"},
                    },
                }
            },
            {
                "X": {
                    "title": "X",
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "b": {"type": "string"},
                    },
                }
            },
        ),  # Should add title to object schema
        (
            {
                "X": {
                    "title": "X",
                    "type": "string",
                    "enum": ["A", "B"],
                }
            },
            {
                "X": {
                    "title": "X",
                    "type": "string",
                    "enum": ["A", "B"],
                }
            },
        ),  # Shouldn't fail if title is already present
    ],
)
def test_add_schema_title_if_missing(
    raw_schema: t.Dict[str, t.Any], expected_schema: t.Dict[str, t.Any]
) -> None:
    assert add_schema_title_if_missing(raw_schema) == expected_schema


@pytest.mark.parametrize(
    "schema, expectation",
    [
        ({"openapi": "3.0.0"}, does_not_raise()),  # Should not raise for 3.x.x
        ({"openapi": "2.0.0"}, pytest.raises(UnsupportedOpenAPISpec)),  # Should raise for 2.x.x
        ({}, pytest.raises(UnsupportedOpenAPISpec)),  # Should raise for missing openapi key
    ],
)
def test_assert_openapi_version(schema: t.Dict[str, t.Any], expectation: t.Any) -> None:
    with expectation:
        assert_openapi_version(schema)


class TestDereferenceSwagger:
    def test_dereference_swagger_with_dict_containing_ref(self) -> None:
        original: t.Dict[str, t.Any] = {
            "a": {
                "$ref": "#/schemas/X",
            },
            "schemas": {
                "X": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "b": {"type": "integer"},
                    },
                }
            },
        }
        expected: t.Dict[str, t.Any] = original.copy()
        expected["a"] = original["schemas"]["X"]

        assert dereference_swagger(original, original) == expected

    def test_dereference_swagger_with_dict_not_containing_ref(self) -> None:
        original: t.Dict[str, t.Any] = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
        }

        assert dereference_swagger(original, original) == original

    def test_dereference_swagger_with_list(self) -> None:
        original: t.Dict[str, t.Any] = {
            "a": {
                "$ref": "#/schemas/X",
            },
            "b": [
                {"$ref": "#/schemas/X"},
                {"$ref": "#/schemas/X"},
            ],
            "schemas": {
                "X": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "b": {"type": "integer"},
                    },
                }
            },
        }
        current: t.Dict[str, t.Any] = original.copy()

        expected: t.Dict[str, t.Any] = original.copy()
        expected["a"] = original["schemas"]["X"]
        expected["b"] = [original["schemas"]["X"], original["schemas"]["X"]]

        assert dereference_swagger(current, original) == expected
