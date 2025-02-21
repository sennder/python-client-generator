import filecmp
import os

from pathlib import Path
from typing import Any, Dict

from python_client_generator.generate_apis import generate_apis
from python_client_generator.generate_base_client import generate_base_client
from python_client_generator.generate_models import generate_models
from python_client_generator.generate_pyproject import generate_pyproject


EXPECTED_PATH = (
    Path(os.path.dirname(os.path.realpath(__file__))) / "expected/swagger_petstore_client"
)


def test_models(swagger_petstore_openapi: Dict[str, Any], tmp_path: Path) -> None:
    generate_models(swagger_petstore_openapi, tmp_path / "models.py")
    assert (
        filecmp.cmp(
            EXPECTED_PATH / "test_project" / "models.py",
            tmp_path / "models.py",
            shallow=False,
        )
        is True
    )


def test_base_client(tmp_path: Path) -> None:
    generate_base_client(tmp_path / "base_client.py", sync=False)
    assert (
        filecmp.cmp(
            EXPECTED_PATH / "test_project" / "base_client.py",
            tmp_path / "base_client.py",
            shallow=False,
        )
        is True
    )


def test_apis(swagger_petstore_openapi: Dict[str, Any], tmp_path: Path) -> None:
    generate_apis(swagger_petstore_openapi, tmp_path / "apis.py", group_by_tags=False, sync=False)
    assert (
        filecmp.cmp(
            EXPECTED_PATH / "test_project" / "apis.py",
            tmp_path / "apis.py",
            shallow=False,
        )
        is True
    )


def test_pyproject(swagger_petstore_openapi: Dict[str, Any], tmp_path: Path) -> None:
    generate_pyproject(
        swagger_petstore_openapi,
        tmp_path / "pyproject.toml",
        project_name="test-project",
        project_path_first="test_project",
        author_name="Test User",
        author_email="test@example.com",
    )
    assert (
        filecmp.cmp(EXPECTED_PATH / "pyproject.toml", tmp_path / "pyproject.toml", shallow=False)
        is True
    )
