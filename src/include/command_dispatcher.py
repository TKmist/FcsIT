# Copyright (C) 2026 TKmist (https://github.com/TKmist)
#
# This file is part of the FcsIT repository.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.
"""Transport-independent command registry and GUI dispatcher."""

from __future__ import annotations

import os
import queue
import threading
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable


CommandHandler = Callable[[dict[str, Any]], Any]
PROTOCOL_VERSION = "1.0"


class CommandError(Exception):
    """Base exception returned to command clients."""


class UnknownCommandError(CommandError):
    """Raised when a command is not present in the explicit registry."""


@dataclass(frozen=True)
class RegisteredCommand:
    """One whitelisted handler and its machine-readable public metadata."""

    handler: CommandHandler
    metadata: dict[str, Any]


@dataclass
class PendingCommand:
    """A validated command waiting for execution by the GUI dispatcher."""

    command_id: str
    name: str
    arguments: dict[str, Any]
    finished: threading.Event = field(default_factory=threading.Event)
    result: Any = None
    error: str | None = None


class CommandRegistry:
    """Explicit whitelist mapping public command names to handlers."""

    def __init__(self) -> None:
        """Initialize an empty explicit command whitelist."""
        self._commands: dict[str, RegisteredCommand] = {}

    def register(
        self,
        name: str,
        handler: CommandHandler,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register one unique handler together with normalized metadata."""
        if not isinstance(name, str) or not name or not callable(handler):
            raise ValueError("A command requires a name and a callable handler.")
        if name in self._commands:
            raise ValueError(f"Command already registered: {name}")
        self._commands[name] = RegisteredCommand(
            handler=handler,
            metadata=self._normalize_metadata(name, metadata),
        )

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a whitelisted handler with an argument object."""
        if not isinstance(arguments, dict):
            raise CommandError("Command arguments must be an object.")
        try:
            command = self._commands[name]
        except KeyError as exc:
            raise UnknownCommandError(f"Unknown command: {name}") from exc
        return command.handler(arguments)

    def names(self) -> list[str]:
        """Return all registered command names in stable sorted order."""
        return sorted(self._commands)

    def describe(self, name: str) -> dict[str, Any]:
        """Return a detached metadata object for one registered command."""

        try:
            command = self._commands[name]
        except KeyError as exc:
            raise UnknownCommandError(f"Unknown command: {name}") from exc
        return _copy_json_value(command.metadata)

    @staticmethod
    def _normalize_metadata(
        name: str, metadata: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Fill required metadata fields and derive argument classifications."""
        supplied = dict(metadata or {})
        arguments = supplied.pop("arguments", {})
        if not isinstance(arguments, dict):
            raise ValueError("Command metadata arguments must be an object.")
        normalized_arguments = {}
        for argument_name, definition in arguments.items():
            if not isinstance(definition, dict):
                raise ValueError(
                    f"Metadata for argument {argument_name} must be an object."
                )
            argument = dict(definition)
            argument.setdefault("type", "any")
            argument.setdefault("required", False)
            normalized_arguments[argument_name] = argument
        required = sorted(
            key
            for key, value in normalized_arguments.items()
            if value["required"]
        )
        optional = sorted(set(normalized_arguments) - set(required))
        category = name.split(".", 1)[0] if "." in name else "other"
        return {
            "command": name,
            "description": supplied.pop(
                "description", f"Execute the {name} command."
            ),
            "category": supplied.pop("category", category),
            "arguments": normalized_arguments,
            "required_arguments": required,
            "optional_arguments": optional,
            "returns": supplied.pop(
                "returns",
                {"type": "object", "description": "Command result object."},
            ),
            "possible_errors": supplied.pop(
                "possible_errors",
                [
                    "invalid_request",
                    "authentication_failed",
                    "unknown_command",
                    "invalid_arguments",
                    "execution_error",
                ],
            ),
            "introduced_in": supplied.pop(
                "introduced_in", PROTOCOL_VERSION
            ),
            "modifies_state": bool(supplied.pop("modifies_state", False)),
            "destructive": bool(supplied.pop("destructive", False)),
            "long_running": bool(supplied.pop("long_running", False)),
            **supplied,
        }


def _copy_json_value(value: Any) -> Any:
    """Copy JSON-like metadata without exposing mutable registry state."""

    if isinstance(value, dict):
        return {key: _copy_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_copy_json_value(item) for item in value]
    return value


class GuiCommandDispatcher:
    """Queue whitelisted commands without coupling dispatch to a transport."""

    _MAIN_THREAD_COMMANDS = {
        "gui.select_method",
    }
    _MAIN_THREAD_PREFIXES: tuple[str, ...] = ()

    def __init__(self, registry: CommandRegistry) -> None:
        """Initialize GuiCommandDispatcher for its documented use."""
        self.registry = registry
        self._queue: queue.Queue[PendingCommand] = queue.Queue()
        self._state_lock = threading.RLock()
        self._active_thread: threading.Thread | None = None

    def submit(self, name: str, arguments: dict[str, Any]) -> PendingCommand:
        """Execute submit and return the documented result."""
        if name not in self.registry.names():
            raise UnknownCommandError(f"Unknown command: {name}")
        if not isinstance(arguments, dict):
            raise CommandError("Command arguments must be an object.")
        pending = PendingCommand(str(uuid.uuid4()), name, arguments)
        self._queue.put(pending)
        return pending

    def process_pending(self, limit: int = 20) -> int:
        """Start one queued command while leaving the render thread free."""

        if limit < 1:
            return 0
        with self._state_lock:
            if self._active_thread is not None and self._active_thread.is_alive():
                return 0
            try:
                pending = self._queue.get_nowait()
            except queue.Empty:
                self._active_thread = None
                return 0
            if (
                os.getenv("FCSIT_COMMAND_MAIN_THREAD") == "1"
                or pending.name in self._MAIN_THREAD_COMMANDS
                or pending.name.startswith(self._MAIN_THREAD_PREFIXES)
            ):
                self._execute_pending(pending)
                return 1
            worker = threading.Thread(
                target=self._execute_pending,
                args=(pending,),
                name=f"FcsIT-command-{pending.command_id}",
                daemon=True,
            )
            self._active_thread = worker
            worker.start()
        return 1

    def _execute_pending(self, pending: PendingCommand) -> None:
        """Support internal execute pending processing without changing public API."""
        try:
            pending.result = self.registry.execute(pending.name, pending.arguments)
        except Exception as exc:
            pending.error = f"{type(exc).__name__}: {exc}"
        finally:
            pending.finished.set()
            self._queue.task_done()
            with self._state_lock:
                if self._active_thread is threading.current_thread():
                    self._active_thread = None


def create_default_registry(state_provider: CommandHandler) -> CommandRegistry:
    """Create the initial explicit command whitelist."""

    registry = CommandRegistry()

    def ping(arguments: dict[str, Any]) -> dict[str, Any]:
        """Return application readiness and protocol identity."""
        return {
            "application": "FcsIT",
            "ready": True,
            "protocol": "fcsit-tcp-json",
            "protocol_version": PROTOCOL_VERSION,
        }

    registry.register(
        "system.ping",
        ping,
        {
            "description": "Check whether FcsIT is ready.",
            "returns": {
                "type": "object",
                "description": "Application readiness and protocol identity.",
            },
        },
    )
    registry.register(
        "gui.get_state",
        state_provider,
        {
            "description": "Read the active module and viewport state.",
            "category": "gui",
            "returns": {
                "type": "object",
                "description": "Mounted method, available methods, and viewport size.",
            },
        },
    )
    def list_commands(arguments: dict[str, Any]) -> dict[str, Any]:
        """Return the complete sorted runtime command whitelist."""
        return {"commands": registry.names()}

    registry.register(
        "system.list_commands",
        list_commands,
        {
            "description": "List every command in the runtime whitelist.",
            "returns": {
                "type": "object",
                "description": "Alphabetically sorted command names.",
                "properties": {"commands": {"type": "array", "items": "string"}},
            },
        },
    )
    registry.register(
        "gui.list_commands",
        list_commands,
        {
            "description": "Compatibility alias for system.list_commands.",
            "category": "gui",
            "deprecated": True,
            "replacement": "system.list_commands",
            "returns": {
                "type": "object",
                "description": "Alphabetically sorted command names.",
            },
        },
    )

    def describe(arguments: dict[str, Any]) -> dict[str, Any]:
        """Return metadata for one validated fully qualified command name."""
        unknown = sorted(set(arguments) - {"command"})
        if unknown:
            raise CommandError(
                "Unknown arguments: " + ", ".join(unknown)
            )
        command_name = arguments.get("command")
        if not isinstance(command_name, str) or not command_name:
            raise CommandError(
                "The 'command' argument must be a non-empty string."
            )
        return registry.describe(command_name)

    registry.register(
        "system.describe_command",
        describe,
        {
            "description": "Return machine-readable metadata for one command.",
            "arguments": {
                "command": {
                    "type": "string",
                    "required": True,
                    "description": "Fully qualified registered command name.",
                    "constraints": {"min_length": 1},
                }
            },
            "returns": {
                "type": "object",
                "description": "Complete registered command metadata.",
            },
            "possible_errors": [
                "invalid_request",
                "authentication_failed",
                "unknown_command",
                "invalid_arguments",
            ],
        },
    )
    return registry
