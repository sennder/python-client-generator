import json
import os

from pathlib import Path
from typing import Any, Dict

import pytest

from python_client_generator.utils import dereference_swagger, add_schema_title_if_missing

from .test_inputs.input_app import app


PATH = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def input_app_openapi_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("input") / "input_app_openapi_file.json"
    with open(path, "w") as f:
        json.dump(app.openapi(), f)
    return path


@pytest.fixture()
def input_app_openapi(input_app_openapi_file: Path) -> Dict[str, Any]:
    with open(input_app_openapi_file, "r") as f:
        swagger = json.load(f)

    add_schema_title_if_missing(swagger["components"]["schemas"])
    return dereference_swagger(swagger, swagger)


@pytest.fixture()
def input_file_openapi() -> Dict[str, Any]:
    with open(PATH / "test_inputs" / "input_openapi_petstore_file.json", "r") as f:
        swagger = json.load(f)

    add_schema_title_if_missing(swagger["components"]["schemas"])
    return dereference_swagger(swagger, swagger)
