import os
import re

from setuptools import find_packages, setup

version_path = "VERSION"

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
]
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
    python_requires='>=3.11.5',
    author='TKmist',
    license='GPL-3.0+',

)
