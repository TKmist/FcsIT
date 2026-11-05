import os
import re
import shutil
import subprocess
import sys
import sysconfig
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


def find_jupyter_book_executable():
    """Locate the Jupyter Book executable belonging to this Python runtime."""
    executable_name = "jupyter-book.exe" if os.name == "nt" else "jupyter-book"
    candidates = [
        Path(sysconfig.get_path("scripts")) / executable_name,
        Path(sys.executable).resolve().parent / executable_name,
    ]
    discovered = shutil.which("jupyter-book")
    if discovered:
        candidates.append(Path(discovered))
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise RuntimeError(
        "Jupyter Book is not installed for the active Python environment."
    )


def prepare_jupyter_book_environment():
    """Prepare the Node.js runtime required by Jupyter Book 2."""
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
            "Jupyter Book is not installed for the active Python environment."
        ) from error

    nodeenv_path = Path(find_nodeenv_path(NODEENV_VERSION))
    runtime_dir = nodeenv_path / ("Scripts" if os.name == "nt" else "bin")
    node_name = "node.exe" if os.name == "nt" else "node"
    npm_names = ("npm.cmd", "npm.exe", "npm") if os.name == "nt" else ("npm",)
    runtime_complete = (runtime_dir / node_name).is_file() and any(
        (runtime_dir / name).exists() for name in npm_names
    )
    if not runtime_complete:
        shutil.rmtree(nodeenv_path, ignore_errors=True)
        print(f"Installing the Jupyter Book Node.js runtime in {nodeenv_path}")
        create_nodeenv(nodeenv_path, NODEENV_VERSION)

    environment["PATH"] = os.pathsep.join(
        [str(runtime_dir), environment.get("PATH", os.defpath)]
    )
    return environment


def replace_directory(source, target):
    """Atomically replace a directory while retaining rollback on failure."""
    source = Path(source)
    target = Path(target)
    staging = target.with_name(f".{target.name}.staging")
    backup = target.with_name(f".{target.name}.backup")
    shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(backup, ignore_errors=True)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, staging)

    if target.exists():
        target.rename(backup)
    try:
        staging.rename(target)
    except Exception:
        if backup.exists() and not target.exists():
            backup.rename(target)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    shutil.rmtree(backup, ignore_errors=True)


class BuildDocs(Command):
    """Build the local Jupyter Book and install its HTML assets."""

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
        source_dir = Path(self.source_dir)
        target_dir = Path(self.target_dir)
        build_root = source_dir / "_build"
        html_dir = build_root / "html"
        if not (source_dir / "myst.yml").is_file():
            raise RuntimeError(
                f"Jupyter Book configuration not found in {source_dir}."
            )

        shutil.rmtree(build_root, ignore_errors=True)
        subprocess.run(
            [str(find_jupyter_book_executable()), "build", "--html"],
            cwd=source_dir,
            env=prepare_jupyter_book_environment(),
            check=True,
        )
        if not (html_dir / "index.html").is_file():
            raise RuntimeError(
                f"Jupyter Book did not create {html_dir / 'index.html'}."
            )
        replace_directory(html_dir, target_dir)
        shutil.rmtree(build_root, ignore_errors=True)
        print(f"Installed documentation: {target_dir}")

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
