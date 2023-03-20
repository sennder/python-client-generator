import os

from pathlib import Path
from typing import Any, Dict

import chevron


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def generate_pyproject(swagger: Dict[str, Any], out_file: Path, project_name: str) -> None:
    """
    Generate `pyproject.toml` file.
    """
    version = swagger["info"]["version"]

    with open(templates_path / "pyproject.toml.mustache", "r") as f:
        toml_str = chevron.render(f, {"version": version, "project_name": project_name})

    with open(out_file, "w+") as f:
        f.write(toml_str)
