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
"""Command-line client for the local FcsIT TCP/JSON server."""

from __future__ import annotations

import ast
import json
import os
import socket
import sys
import uuid


def _usage() -> int:
    print("Usage: fcsit_call COMMAND [JSON_ARGUMENTS]", file=sys.stderr)
    return 2


def _parse_arguments(text: str) -> dict:
    """Parse JSON or the single-quoted object notation convenient in cmd.exe."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        try:
            value = ast.literal_eval(text)
        except (SyntaxError, ValueError) as exc:
            raise ValueError("arguments must be a valid object") from exc

    if not isinstance(value, dict):
        raise ValueError("arguments must be an object")
    try:
        json.dumps(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("arguments must contain JSON-compatible values") from exc
    return value


def main(argv: list[str] | None = None) -> int:
    """Send one command and print the server response as formatted JSON."""
    arguments = sys.argv[1:] if argv is None else argv
    if not arguments or len(arguments) > 2:
        return _usage()

    command = arguments[0]
    try:
        command_arguments = _parse_arguments(
            arguments[1] if len(arguments) == 2 else "{}"
        )
    except ValueError as exc:
        print(f"Invalid command arguments: {exc}.", file=sys.stderr)
        return 2

    try:
        port = int(os.getenv("FCSIT_TCP_PORT", "8765"))
    except ValueError:
        print("FCSIT_TCP_PORT must be an integer.", file=sys.stderr)
        return 2

    request = {
        "protocol": "fcsit-tcp-json",
        "version": "1.0",
        "id": f"cli-{uuid.uuid4().hex}",
        "command": command,
        "arguments": command_arguments,
    }
    token = os.getenv("FCSIT_TCP_TOKEN")
    if token:
        request["token"] = token

    try:
        with socket.create_connection(
            (os.getenv("FCSIT_TCP_HOST", "127.0.0.1"), port)
        ) as connection:
            stream = connection.makefile("rwb")
            stream.write(json.dumps(request, separators=(",", ":")).encode("utf-8"))
            stream.write(b"\n")
            stream.flush()
            response = stream.readline()
        if not response:
            raise ConnectionError("FcsIT closed the connection without a response.")
        decoded_response = json.loads(response.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FcsIT TCP request failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(decoded_response, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
