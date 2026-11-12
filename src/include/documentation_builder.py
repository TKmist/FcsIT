"""Build and publish the HTML documentation bundled with FcsIT.

Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)

This file is part of the FcsIT repository.

This file is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation, either version 3 of the License, or any later version.

This file is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
for more details.

You should have received a copy of the GNU General Public License
along with this file. If not, see <https://www.gnu.org/licenses/>.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


JUPYTER_BOOK_REQUIREMENT = "jupyter-book==2.1.2"


def ensure_jupyter_book(
    python_executable: str | None = None,
    *,
    install_missing: bool = False,
) -> None:
    """Ensure that Jupyter Book is importable by the selected interpreter."""
    executable = python_executable or sys.executable
    result = subprocess.run(
        [executable, "-c", "import jupyter_book"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return
    if not install_missing:
        raise RuntimeError(
            f"{JUPYTER_BOOK_REQUIREMENT} is required to build the documentation."
        )
    subprocess.run(
        [
            executable,
            "-m",
            "pip",
            "install",
            JUPYTER_BOOK_REQUIREMENT,
            "--disable-pip-version-check",
        ],
        check=True,
    )


def prepare_jupyter_book_environment() -> dict[str, str]:
    """Provide a complete Node.js runtime for Jupyter Book."""
    environment = os.environ.copy()
    environment["BASE_URL"] = ""
    environment["JB_ALLOW_NODEENV"] = "yes"

    if shutil.which("node", path=environment.get("PATH")) and shutil.which(
        "npm", path=environment.get("PATH")
    ):
        return environment

    try:
        from jupyter_book.__main__ import NODEENV_VERSION
        from jupyter_book.nodeenv import create_nodeenv, find_nodeenv_path
    except ImportError as error:
        raise RuntimeError(
            "Jupyter Book cannot prepare its managed Node.js runtime."
        ) from error

    nodeenv_path = Path(find_nodeenv_path(NODEENV_VERSION))
    runtime_directory = nodeenv_path / ("Scripts" if os.name == "nt" else "bin")
    node_name = "node.exe" if os.name == "nt" else "node"
    npm_names = ("npm.cmd", "npm.exe", "npm") if os.name == "nt" else ("npm",)
    runtime_complete = (runtime_directory / node_name).is_file() and any(
        (runtime_directory / name).is_file() for name in npm_names
    )
    if not runtime_complete:
        shutil.rmtree(nodeenv_path, ignore_errors=True)
        print(f"Installing the Jupyter Book Node.js runtime in {nodeenv_path}")
        create_nodeenv(nodeenv_path, NODEENV_VERSION)

    environment["PATH"] = os.pathsep.join(
        [str(runtime_directory), environment.get("PATH", os.defpath)]
    )
    return environment


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _publish_directory(build_directory: Path, target_directory: Path) -> None:
    """Replace the bundled help only after a complete build is available."""
    target_directory.parent.mkdir(parents=True, exist_ok=True)
    staging_directory = Path(
        tempfile.mkdtemp(
            prefix=".fcsit-help-staging-",
            dir=target_directory.parent,
        )
    )
    backup_directory = target_directory.with_name(
        f".{target_directory.name}.previous"
    )
    target_was_moved = False
    try:
        shutil.copytree(build_directory, staging_directory, dirs_exist_ok=True)
        _remove_path(backup_directory)
        if target_directory.exists() or target_directory.is_symlink():
            target_directory.replace(backup_directory)
            target_was_moved = True
        try:
            staging_directory.replace(target_directory)
        except Exception:
            if target_was_moved and not target_directory.exists():
                backup_directory.replace(target_directory)
            raise
        _remove_path(backup_directory)
    finally:
        _remove_path(staging_directory)


def build_documentation(
    source_directory: str | os.PathLike[str],
    target_directory: str | os.PathLike[str],
    *,
    python_executable: str | None = None,
    install_missing: bool = False,
) -> Path:
    """Build the manual and atomically publish a complete HTML directory."""
    source = Path(source_directory).expanduser().resolve()
    target = Path(target_directory).expanduser().resolve()
    configuration = source / "myst.yml"
    if not configuration.is_file():
        raise FileNotFoundError(
            f"Jupyter Book configuration was not found: {configuration}"
        )

    executable = python_executable or sys.executable
    ensure_jupyter_book(executable, install_missing=install_missing)
    build_directory = source / "_build"
    html_directory = build_directory / "html"
    shutil.rmtree(build_directory, ignore_errors=True)

    subprocess.run(
        [executable, "-m", "jupyter_book", "build", "--html"],
        cwd=source,
        env=prepare_jupyter_book_environment(),
        check=True,
    )
    index_file = html_directory / "index.html"
    if not index_file.is_file():
        raise RuntimeError(f"Jupyter Book did not create {index_file}.")

    _publish_directory(html_directory, target)
    shutil.rmtree(build_directory, ignore_errors=True)
    print(f"Documentation published to: {target}")
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build and publish the HTML documentation bundled with FcsIT."
    )
    parser.add_argument("--source", required=True, help="Directory containing myst.yml")
    parser.add_argument("--target", required=True, help="Bundled HTML destination")
    parser.add_argument(
        "--install-missing",
        action="store_true",
        help="Install the pinned Jupyter Book dependency when it is unavailable.",
    )
    arguments = parser.parse_args(argv)
    build_documentation(
        arguments.source,
        arguments.target,
        install_missing=arguments.install_missing,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
