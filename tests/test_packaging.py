from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

import tomllib

PACKAGE_ROOT = Path(__file__).resolve().parents[1]


def test_pyproject_uses_package_version_as_source_of_truth() -> None:
    pyproject = tomllib.loads((PACKAGE_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "edgarparser-sdk"
    assert pyproject["project"]["dynamic"] == ["version"]
    assert pyproject["tool"]["hatch"]["version"]["path"] == (
        "src/edgarparser/__init__.py"
    )


def test_wheel_contains_typed_marker_and_license(tmp_path: Path) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
            "--wheel",
            "--outdir",
            str(tmp_path),
            str(PACKAGE_ROOT),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    wheel = next(tmp_path.glob("edgarparser_sdk-*.whl"))
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    assert "edgarparser/py.typed" in names
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)
