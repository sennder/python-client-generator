import json
import os

from pathlib import Path
from typing import Any, Dict

import pytest

from python_client_generator.utils import (
    add_schema_title_if_missing,
    dereference_swagger,
)

from .inputs.fastapi_app import app


PATH = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def fastapi_app_openapi_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("input") / "fastapi_app_openapi.json"
    with open(path, "w") as f:
        json.dump(app.openapi(), f)
    return path


@pytest.fixture()
def fastapi_app_openapi(fastapi_app_openapi_file: Path) -> Dict[str, Any]:
    with open(fastapi_app_openapi_file, "r") as f:
        swagger = json.load(f)

    add_schema_title_if_missing(swagger["components"]["schemas"])
    return dereference_swagger(swagger, swagger)


@pytest.fixture()
def swagger_petstore_openapi() -> Dict[str, Any]:
    with open(PATH / "inputs" / "swagger-petstore.json", "r") as f:
        swagger = json.load(f)

    add_schema_title_if_missing(swagger["components"]["schemas"])
    return dereference_swagger(swagger, swagger)
