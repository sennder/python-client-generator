import argparse
import json
import os
import shutil

from pathlib import Path

from python_client_generator.utils import dereference_swagger

from .generate_apis import generate_apis
from .generate_base_client import generate_base_client
from .generate_models import generate_models
from .generate_pyproject import generate_pyproject


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generates an httpx-based Python client.")
    parser.add_argument("--open-api", type=str)
    parser.add_argument("--package-name", type=str)
    parser.add_argument("--project-name", type=str)
    parser.add_argument("--outdir", type=str, default="clients/")
    parser.add_argument("--group-by-tags", action="store_true")
    parser.add_argument("--sync", action="store_true")

    args = parser.parse_args()

    with open(args.open_api, "r") as f:
        swagger = json.load(f)
    dereferenced_swagger = dereference_swagger(swagger, swagger)

    # Create root directory
    path = Path(args.outdir)
    path.mkdir(parents=True, exist_ok=True)

    generate_pyproject(dereferenced_swagger, path / "pyproject.toml", args.project_name)

    # Create package directory
    package_path = path / Path(args.package_name)
    package_path.mkdir(parents=True, exist_ok=True)

    # Generate package files
    generate_models(dereferenced_swagger, package_path / "models.py")
    generate_base_client(package_path / "base_client.py", sync=args.sync)
    generate_apis(dereferenced_swagger, package_path / "apis.py", args.group_by_tags, args.sync)
    shutil.copyfile(templates_path / "__init__.py", package_path / "__init__.py")
