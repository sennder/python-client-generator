import os

from pathlib import Path

import chevron


dir_path = Path(os.path.dirname(os.path.realpath(__file__)))
templates_path = dir_path / "templates"


def generate_base_client(out_file: Path, sync: bool) -> None:
    """
    Generate the root API client to be used by all other functions.
    """
    with open(templates_path / "base_client.py.mustache", "r") as f:
        toml_str = chevron.render(f, {"async": not sync})

    with open(out_file, "w+") as f:
        f.write(toml_str)
