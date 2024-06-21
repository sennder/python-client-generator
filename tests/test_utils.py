import pytest
import typing as t
from python_client_generator.utils import add_schema_title_if_missing


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
def test_add_schema_title_if_missing(raw_schema: t.Dict[str, t.Any], expected_schema) -> None:
    assert add_schema_title_if_missing(raw_schema) == expected_schema
