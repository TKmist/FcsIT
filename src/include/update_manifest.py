"""
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

"""Validate and execute declarative FcsIT dependency migrations."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


SUPPORTED_SCHEMA_VERSION = 1
_ALLOWED_FIELDS = {
    "schema_version",
    "migration_id",
    "message",
    "python_packages",
    "copy_files",
    "remove_files",
    "requires_restart",
}
_REQUIREMENT_RE = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9_.-]*"
    r"(?:[<>=!~]=?[A-Za-z0-9.*+!<>=~,-]+)?$"
)
_IMPORT_NAME_RE = re.compile(
    r"^[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*$"
)


class UpdateManifestError(ValueError):
    """Report an invalid or unsafe update manifest."""


class UpdateMigrationError(RuntimeError):
    """Report a failed dependency installation or cleanup operation."""


@dataclass(frozen=True)
class PythonPackageRequirement:
    """Describe one approved Python package and its import name."""

    requirement: str
    import_name: str


@dataclass(frozen=True)
class FileCopyOperation:
    """Describe one platform-specific file copied during migration."""

    source: Path
    target: Path
    platform: str
    executable: bool
    satisfied_by_text: str | None


@dataclass(frozen=True)
class UpdateManifest:
    """Represent one validated declarative update migration."""

    schema_version: int
    migration_id: str
    message: str
    python_packages: tuple[PythonPackageRequirement, ...]
    copy_files: tuple[FileCopyOperation, ...]
    remove_files: tuple[Path, ...]
    requires_restart: bool

    @classmethod
    def from_mapping(cls, value: Any) -> "UpdateManifest":
        """Validate a decoded JSON value and return an immutable manifest."""
        if not isinstance(value, dict):
            raise UpdateManifestError("The update manifest must be a JSON object.")

        unknown = sorted(set(value) - _ALLOWED_FIELDS)
        if unknown:
            raise UpdateManifestError(
                "Unknown update manifest fields: " + ", ".join(unknown)
            )

        required = {"schema_version", "migration_id", "message"}
        missing = sorted(required - set(value))
        if missing:
            raise UpdateManifestError(
                "Missing update manifest fields: " + ", ".join(missing)
            )

        schema_version = value["schema_version"]
        if schema_version != SUPPORTED_SCHEMA_VERSION:
            raise UpdateManifestError(
                f"Unsupported update manifest schema: {schema_version!r}."
            )

        migration_id = _non_empty_string(value["migration_id"], "migration_id")
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", migration_id):
            raise UpdateManifestError(
                "migration_id may contain lowercase letters, digits, '_' and '-'."
            )
        message = _non_empty_string(value["message"], "message")

        package_values = value.get("python_packages", [])
        if not isinstance(package_values, list):
            raise UpdateManifestError("python_packages must be an array.")
        packages = tuple(_parse_package(item) for item in package_values)
        if len({item.import_name for item in packages}) != len(packages):
            raise UpdateManifestError("python_packages contains duplicate imports.")

        copy_values = value.get("copy_files", [])
        if not isinstance(copy_values, list):
            raise UpdateManifestError("copy_files must be an array.")
        copy_files = tuple(_parse_copy_operation(item) for item in copy_values)

        remove_values = value.get("remove_files", [])
        if not isinstance(remove_values, list):
            raise UpdateManifestError("remove_files must be an array.")
        remove_files = tuple(_safe_relative_path(item) for item in remove_values)
        if len(set(remove_files)) != len(remove_files):
            raise UpdateManifestError("remove_files contains duplicate paths.")

        requires_restart = value.get("requires_restart", True)
        if not isinstance(requires_restart, bool):
            raise UpdateManifestError("requires_restart must be Boolean.")

        if not packages and not copy_files and not remove_files:
            raise UpdateManifestError("The update manifest contains no operations.")

        return cls(
            schema_version=schema_version,
            migration_id=migration_id,
            message=message,
            python_packages=packages,
            copy_files=copy_files,
            remove_files=remove_files,
            requires_restart=requires_restart,
        )


class UpdateManifestReader:
    """Load update manifests without executing embedded or arbitrary code."""

    @staticmethod
    def load(path: str | Path) -> UpdateManifest:
        """Read and validate one UTF-8 JSON manifest from disk."""
        manifest_path = Path(path)
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise UpdateManifestError(
                f"Cannot read update manifest {manifest_path}: {exc}"
            ) from exc
        return UpdateManifest.from_mapping(payload)

    @staticmethod
    def loads(text: str) -> UpdateManifest:
        """Decode and validate manifest JSON received from a trusted transport."""
        try:
            payload = json.loads(text)
        except json.JSONDecodeError as exc:
            raise UpdateManifestError(f"Invalid update manifest JSON: {exc}") from exc
        return UpdateManifest.from_mapping(payload)


class UpdateMigrationExecutor:
    """Inspect and execute a user-approved manifest inside one installation."""

    def __init__(
        self,
        manifest: UpdateManifest,
        install_root: str | Path,
        *,
        python_executable: str | Path | None = None,
    ) -> None:
        self.manifest = manifest
        self.install_root = Path(install_root).resolve()
        self.python_executable = str(python_executable or sys.executable)

    def missing_packages(self) -> tuple[PythonPackageRequirement, ...]:
        """Return requirements whose import cannot be resolved."""
        missing = []
        for package in self.manifest.python_packages:
            try:
                available = importlib.util.find_spec(package.import_name)
            except (ImportError, ModuleNotFoundError, AttributeError):
                available = None
            if available is None:
                missing.append(package)
        return tuple(missing)

    def removable_files(self) -> tuple[Path, ...]:
        """Return existing cleanup targets resolved below the installation root."""
        return tuple(
            path
            for relative in self.manifest.remove_files
            if (path := self._resolve_target(relative)).is_file()
        )

    def is_required(self) -> bool:
        """Return whether dependency installation or file cleanup remains."""
        return bool(
            self.missing_packages()
            or self.pending_file_copies()
            or self.removable_files()
        )

    def pending_file_copies(self) -> tuple[FileCopyOperation, ...]:
        """Return host-platform files whose installed copies differ."""
        pending = []
        for operation in self.manifest.copy_files:
            if not self._matches_platform(operation.platform):
                continue
            source = self._resolve_source(operation.source)
            target = self._resolve_target(operation.target, allow_install_parent=True)
            if not target.is_file():
                pending.append(operation)
                continue
            if operation.satisfied_by_text is not None:
                try:
                    target_text = target.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    pending.append(operation)
                    continue
                if operation.satisfied_by_text in target_text:
                    continue
            if source.read_bytes() != target.read_bytes():
                pending.append(operation)
        return tuple(pending)

    def execute(self) -> dict[str, Any]:
        """Install missing packages, verify imports, then remove obsolete files."""
        installed: list[str] = []
        copied: list[str] = []
        removed: list[str] = []

        for package in self.missing_packages():
            result = subprocess.run(
                [
                    self.python_executable,
                    "-m",
                    "pip",
                    "install",
                    package.requirement,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip()
                raise UpdateMigrationError(
                    f"Failed to install {package.requirement}: {detail[-2000:]}"
                )
            verification = subprocess.run(
                [
                    self.python_executable,
                    "-c",
                    f"import {package.import_name}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if verification.returncode != 0:
                detail = (verification.stderr or verification.stdout).strip()
                raise UpdateMigrationError(
                    f"Installed {package.requirement}, but import verification "
                    f"failed: {detail[-2000:]}"
                )
            installed.append(package.requirement)

        for operation in self.pending_file_copies():
            source = self._resolve_source(operation.source)
            target = self._resolve_target(operation.target, allow_install_parent=True)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if operation.executable and not sys.platform.startswith("win"):
                target.chmod(target.stat().st_mode | 0o111)
            copied.append(str(operation.target))

        for target in self.removable_files():
            target.unlink()
            removed.append(str(target.relative_to(self.install_root)))

        return {
            "migration_id": self.manifest.migration_id,
            "installed_packages": installed,
            "copied_files": copied,
            "removed_files": removed,
            "requires_restart": self.manifest.requires_restart,
        }

    def _resolve_source(self, relative: Path) -> Path:
        """Resolve a migration source strictly inside the application tree."""
        source = (self.install_root / relative).resolve()
        if self.install_root not in source.parents or not source.is_file():
            raise UpdateManifestError(f"Invalid migration source: {relative}")
        return source

    def _resolve_target(
        self, relative: Path, *, allow_install_parent: bool = False
    ) -> Path:
        """Resolve a validated relative target and enforce installation scope."""
        target = (self.install_root / relative).resolve()
        allowed_root = self.install_root.parent if allow_install_parent else self.install_root
        if target != allowed_root and allowed_root not in target.parents:
            raise UpdateManifestError(
                f"Cleanup target escapes the FcsIT installation: {relative}"
            )
        return target

    @staticmethod
    def _matches_platform(platform: str) -> bool:
        if platform == "all":
            return True
        if platform == "windows":
            return sys.platform.startswith("win")
        return platform == "linux" and not sys.platform.startswith("win")


def _non_empty_string(value: Any, field: str) -> str:
    """Validate and normalize a required non-empty string."""
    if not isinstance(value, str) or not value.strip():
        raise UpdateManifestError(f"{field} must be a non-empty string.")
    return value.strip()


def _parse_package(value: Any) -> PythonPackageRequirement:
    """Validate one package declaration without allowing URLs or pip options."""
    if not isinstance(value, dict) or set(value) != {"requirement", "import_name"}:
        raise UpdateManifestError(
            "Each python_packages entry requires requirement and import_name only."
        )
    requirement = _non_empty_string(value["requirement"], "requirement")
    import_name = _non_empty_string(value["import_name"], "import_name")
    if not _REQUIREMENT_RE.fullmatch(requirement):
        raise UpdateManifestError(
            f"Unsafe or unsupported Python requirement: {requirement!r}."
        )
    if not _IMPORT_NAME_RE.fullmatch(import_name):
        raise UpdateManifestError(f"Invalid Python import name: {import_name!r}.")
    return PythonPackageRequirement(requirement, import_name)


def _parse_copy_operation(value: Any) -> FileCopyOperation:
    """Validate one constrained platform-specific file copy."""
    required_fields = {"source", "target", "platform", "executable"}
    allowed_fields = required_fields | {"satisfied_by_text"}
    if (
        not isinstance(value, dict)
        or not required_fields.issubset(value)
        or not set(value).issubset(allowed_fields)
    ):
        raise UpdateManifestError(
            "Each copy_files entry requires source, target, platform and "
            "executable; satisfied_by_text is optional."
        )
    source = _safe_relative_path(value["source"])
    target_text = _non_empty_string(value["target"], "copy target")
    target = Path(target_text)
    if target.is_absolute() or target == Path(".."):
        raise UpdateManifestError(f"Unsafe copy target: {target_text!r}.")
    parent_parts = [part for part in target.parts if part == ".."]
    if len(parent_parts) > 1 or (parent_parts and target.parts[0] != ".."):
        raise UpdateManifestError(f"Unsafe copy target: {target_text!r}.")
    platform = _non_empty_string(value["platform"], "platform")
    if platform not in {"all", "linux", "windows"}:
        raise UpdateManifestError(f"Unsupported copy platform: {platform!r}.")
    executable = value["executable"]
    if not isinstance(executable, bool):
        raise UpdateManifestError("copy_files executable must be Boolean.")
    satisfied_by_text = value.get("satisfied_by_text")
    if satisfied_by_text is not None:
        satisfied_by_text = _non_empty_string(
            satisfied_by_text, "satisfied_by_text"
        )
        if "\n" in satisfied_by_text or "\r" in satisfied_by_text:
            raise UpdateManifestError(
                "satisfied_by_text must contain a single text fragment."
            )
    return FileCopyOperation(
        source, target, platform, executable, satisfied_by_text
    )


def _safe_relative_path(value: Any) -> Path:
    """Validate a cleanup path as a normalized relative file path."""
    text = _non_empty_string(value, "remove_files entry")
    path = Path(text)
    if path.is_absolute() or ".." in path.parts or path == Path("."):
        raise UpdateManifestError(f"Unsafe cleanup path: {text!r}.")
    return path
