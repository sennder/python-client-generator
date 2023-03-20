import json
import os

from pathlib import Path
from typing import Any, Dict

import pytest

from python_client_generator.utils import dereference_swagger

from .input_app import app


PATH = Path(os.path.dirname(os.path.realpath(__file__)))


@pytest.fixture(scope="session")
def openapi_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    path = tmp_path_factory.mktemp("input") / "input_openapi.json"
    with open(path, "w") as f:
        json.dump(app.openapi(), f)
    return path


@pytest.fixture()
def openapi(openapi_file: Path) -> Dict[str, Any]:
    with open(openapi_file, "r") as f:
        swagger = json.load(f)
    return dereference_swagger(swagger, swagger)
