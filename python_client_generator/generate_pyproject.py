import os

from pathlib import Path
from typing import Any, Dict, Optional

import chevron


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def generate_pyproject(
    swagger: Dict[str, Any],
    out_file: Path,
    project_name: str,
    project_path_first: str,
    author_name: Optional[str] = None,
    author_email: Optional[str] = None,
) -> None:
    """
    Generate `pyproject.toml` file.
    """
    data = {
        "version": swagger["info"]["version"],
        "project_name": project_name,
        "project_path_first": project_path_first,
        "has_author": bool(author_name or author_email),
        "author": [author_name, author_email],
    }

    with open(templates_path / "pyproject.toml.mustache", "r") as f:
        toml_str = chevron.render(f, data)

    with open(out_file, "w+") as f:
        f.write(toml_str)
