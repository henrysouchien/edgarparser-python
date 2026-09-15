from __future__ import annotations

import subprocess
import sys
import tarfile
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
    assert pyproject["tool"]["hatch"]["build"]["targets"]["wheel"][
        "core-metadata-version"
    ] == "2.4"
    assert pyproject["tool"]["hatch"]["build"]["targets"]["sdist"][
        "core-metadata-version"
    ] == "2.4"


def test_distributions_use_compatible_metadata_and_wheel_contents(
    tmp_path: Path,
) -> None:
    subprocess.run(
        [
            sys.executable,
            "-m",
            "build",
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
        metadata_name = next(
            name for name in names if name.endswith(".dist-info/METADATA")
        )
        metadata = archive.read(metadata_name)

    assert metadata.splitlines()[0] == b"Metadata-Version: 2.4"
    assert "edgarparser/py.typed" in names
    assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)

    sdist = next(tmp_path.glob("edgarparser_sdk-*.tar.gz"))
    with tarfile.open(sdist, "r:gz") as archive:
        pkg_info_member = next(
            member
            for member in archive.getmembers()
            if member.name.endswith("/PKG-INFO")
            and len(Path(member.name).parts) == 2
        )
        pkg_info_file = archive.extractfile(pkg_info_member)
        assert pkg_info_file is not None
        pkg_info = pkg_info_file.read()

    assert pkg_info.splitlines()[0] == b"Metadata-Version: 2.4"
