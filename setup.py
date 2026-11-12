# Copyright (C) 2026 Tomasz Kalwarczyk (https://github.com/TKmist)
#
# This file is part of the FcsIT repository.
#
# This file is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or any later version.
#
# This file is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file. If not, see <https://www.gnu.org/licenses/>.

import os
import re
import subprocess
import sys
from pathlib import Path

from setuptools import Command, find_packages, setup


ROOT_DIR = Path(__file__).resolve().parent
DOCS_SOURCE_DIR = ROOT_DIR / "docs"
DOCS_TARGET_DIR = ROOT_DIR / "src" / "doc" / "assets" / "help_html"

version_path = ROOT_DIR / "VERSION"

with open(version_path, "r", encoding="utf-8") as file:
    APP_VERSION = file.read().strip()


def to_pep440_version(version):
    """Convert FcsIT's optional letter suffix to a valid PEP 440 version."""
    match = re.fullmatch(
        r"[vV]?(\d+)\.(\d+)\.(\d+)(?:(rc\d+)|([a-zA-Z]))?",
        version,
    )
    if match is None:
        raise ValueError(f"Invalid FcsIT version: {version!r}")

    major, minor, patch, release_candidate, letter = match.groups()
    normalized = f"{major}.{minor}.{patch}"
    if release_candidate is not None:
        return normalized + release_candidate.lower()
    if letter is not None:
        development_number = ord(letter.lower()) - ord("a") + 1
        return f"{normalized}.dev{development_number}"
    return normalized


PACKAGE_VERSION = to_pep440_version(APP_VERSION)


def read_requirements(path):
    """Read non-empty, non-comment requirement lines from a text file."""
    return [
        line
        for raw_line in Path(path).read_text(encoding="utf-8").splitlines()
        if (line := raw_line.strip()) and not line.startswith("#")
    ]


class BuildDocs(Command):
    """Compatibility wrapper for the standalone documentation builder."""

    description = "build and install the bundled HTML documentation"
    user_options = [
        ("source-dir=", None, "Jupyter Book source directory"),
        ("target-dir=", None, "destination for generated HTML files"),
    ]

    def initialize_options(self):
        self.source_dir = None
        self.target_dir = None

    def finalize_options(self):
        self.source_dir = str(
            Path(self.source_dir).resolve()
            if self.source_dir
            else DOCS_SOURCE_DIR
        )
        self.target_dir = str(
            Path(self.target_dir).resolve()
            if self.target_dir
            else DOCS_TARGET_DIR
        )

    def run(self):
        builder = ROOT_DIR / "src" / "include" / "documentation_builder.py"
        if not builder.is_file():
            raise RuntimeError(f"Documentation builder not found: {builder}")
        subprocess.run(
            [
                sys.executable,
                str(builder),
                "--source",
                self.source_dir,
                "--target",
                self.target_dir,
            ],
            cwd=ROOT_DIR,
            check=True,
        )

win_packages = ['pywin32']
basic_packages = [
"dearpygui<2.0.0",
    "numpy==1.26.4",
    "pandas==2.2.3",
    "matplotlib==3.9.2",
    "scipy==1.15.3",
    'colorama',
    "sympy",
    "Pillow",
    "lmfit",
    "multipletau",
    "screeninfo==0.8.1",
    "numba==0.60.0",
    "requests==2.32.3",
    "decorator==5.2.1",
    "opencv-python==4.11.0.86",
    "scikit-image==0.25.2",
    "phconvert>=0.9.1",
] + read_requirements(ROOT_DIR / "docs" / "requirements.txt")
req_pack = []
if os.name == 'nt':
    req_pack = basic_packages + win_packages
elif os.name == 'posix':
    req_pack = basic_packages


setup(
    name='FcsIT',
    version=PACKAGE_VERSION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=req_pack,
    cmdclass={"build_docs": BuildDocs},
    python_requires='>=3.11.5',
    author='TKmist',
    license='GPL-3.0+',

)
