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
"""Versioned newline-delimited JSON server for the FcsIT command protocol."""

from __future__ import annotations

import hmac
import json
import os
import socketserver
import threading
from pathlib import Path
from typing import Any

from include.command_dispatcher import CommandError, GuiCommandDispatcher


PROTOCOL_NAME = "fcsit-tcp-json"
PROTOCOL_VERSION = "1.0"
SUPPORTED_PROTOCOL_VERSIONS = frozenset({PROTOCOL_VERSION})
DEFAULT_MAX_REQUEST_BYTES = 1024 * 1024


def _json_default(value: Any) -> Any:
    """Convert supported scientific result values into JSON-compatible data."""
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "to_dict"):
        return value.to_dict()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


class _TCPRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        """Read bounded JSON requests and write one response for each request."""
        while True:
            raw_request = self.rfile.readline(self.server.max_request_bytes + 1)
            if not raw_request:
                return
            if len(raw_request) > self.server.max_request_bytes:
                response = self.server.protocol.error_response(
                    None, "Request exceeds the configured size limit."
                )
                self._write(response)
                return
            try:
                request = json.loads(raw_request.decode("utf-8"))
                response = self.server.protocol.handle_request(request)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                response = self.server.protocol.error_response(
                    None, f"Invalid JSON request: {exc}"
                )
            except Exception as exc:
                response = self.server.protocol.error_response(
                    None, f"{type(exc).__name__}: {exc}"
                )
            self._write(response)

    def _write(self, response: dict[str, Any]) -> None:
        """Serialize and write one newline-delimited protocol response."""
        payload = json.dumps(
            response, ensure_ascii=False, default=_json_default
        ).encode("utf-8") + b"\n"
        self.wfile.write(payload)


class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


class TCPJSONCommandServer:
    """Expose a dispatcher through the local FcsIT TCP/JSON protocol."""

    def __init__(
        self,
        dispatcher: GuiCommandDispatcher,
        host: str = "127.0.0.1",
        port: int = 8765,
        timeout: float = 300.0,
        token: str | None = None,
        max_request_bytes: int = DEFAULT_MAX_REQUEST_BYTES,
    ) -> None:
        """Initialize TCPJSONCommandServer for its documented use."""
        if host not in {"127.0.0.1", "localhost"}:
            raise ValueError("The TCP server may listen only on IPv4 localhost.")
        if max_request_bytes < 256:
            raise ValueError("The request size limit must be at least 256 bytes.")
        self.dispatcher = dispatcher
        self.host = host
        self.port = port
        self.timeout = timeout
        self.token = token if token is not None else os.getenv("FCSIT_TCP_TOKEN")
        self.max_request_bytes = max_request_bytes
        self._server: _ThreadingTCPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Execute start and return the documented result."""
        if self._server is not None:
            return
        self._server = _ThreadingTCPServer(
            (self.host, self.port), _TCPRequestHandler
        )
        self._server.protocol = self
        self._server.max_request_bytes = self.max_request_bytes
        self.port = self._server.server_address[1]
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            name="FcsIT-tcp-json-server",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        """Execute stop and return the documented result."""
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        self._server = None
        self._thread = None

    def error_response(self, request_id: Any, error: str) -> dict[str, Any]:
        """Execute error response and return the documented result."""
        return {
            "protocol": PROTOCOL_NAME,
            "version": PROTOCOL_VERSION,
            "id": request_id,
            "status": "error",
            "error": error,
        }

    def handle_request(self, request: Any) -> dict[str, Any]:
        """Execute handle request and return the documented result."""
        if not isinstance(request, dict):
            return self.error_response(None, "Request must be a JSON object.")
        request_id = request.get("id")
        if not isinstance(request_id, (str, int)) or isinstance(request_id, bool):
            return self.error_response(None, "The 'id' field must be a string or integer.")
        if request.get("protocol") != PROTOCOL_NAME:
            return self.error_response(request_id, "Unsupported or missing protocol.")
        if request.get("version") not in SUPPORTED_PROTOCOL_VERSIONS:
            return self.error_response(request_id, "Unsupported protocol version.")
        if self.token:
            supplied = request.get("token")
            if not isinstance(supplied, str) or not hmac.compare_digest(
                supplied, self.token
            ):
                return self.error_response(request_id, "Authentication failed.")
        name = request.get("command")
        arguments = request.get("arguments")
        if not isinstance(name, str) or not name:
            return self.error_response(
                request_id, "The 'command' field must be a non-empty string."
            )
        if not isinstance(arguments, dict):
            return self.error_response(
                request_id, "The 'arguments' field must be an object."
            )
        try:
            pending = self.dispatcher.submit(name, arguments)
        except CommandError as exc:
            return self.error_response(request_id, str(exc))
        if not pending.finished.wait(self.timeout):
            return {
                "protocol": PROTOCOL_NAME,
                "version": PROTOCOL_VERSION,
                "id": request_id,
                "command_id": pending.command_id,
                "status": "accepted",
            }
        if pending.error:
            response = self.error_response(request_id, pending.error)
            response["command_id"] = pending.command_id
            return response
        return {
            "protocol": PROTOCOL_NAME,
            "version": PROTOCOL_VERSION,
            "id": request_id,
            "command_id": pending.command_id,
            "status": "completed",
            "result": pending.result,
        }
