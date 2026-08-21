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
# Complete FcsIT protocol command names from the running command registry.

_fcsit_call_completion() {
    # Offer runtime command names only for the first fcsit_call argument.
    local current_word
    local client_command
    local response
    local commands
    local cache_directory
    local cache_file
    local temporary_cache

    if [[ "$COMP_CWORD" -ne 1 ]]; then
        return
    fi

    current_word="${COMP_WORDS[COMP_CWORD]}"
    client_command="${COMP_WORDS[0]}"
    if [[ ! -x "$client_command" ]]; then
        client_command="$(command -v fcsit_call 2>/dev/null)" || return
    fi

    cache_directory="${XDG_CACHE_HOME:-$HOME/.cache}/fcsit"
    cache_file="$cache_directory/commands"
    response="$(
        timeout "${FCSIT_COMPLETION_TIMEOUT:-3}" \
            "$client_command" system.list_commands 2>/dev/null
    )"
    commands="$(jq -r '.result.commands[]?' <<<"$response" 2>/dev/null)"
    if [[ -n "$commands" ]]; then
        mkdir -p -m 700 "$cache_directory" 2>/dev/null
        temporary_cache="$cache_file.$$"
        if printf '%s\n' "$commands" >"$temporary_cache" 2>/dev/null; then
            chmod 600 "$temporary_cache" 2>/dev/null
            mv -f "$temporary_cache" "$cache_file" 2>/dev/null
        fi
    elif [[ -r "$cache_file" ]]; then
        commands="$(<"$cache_file")"
    else
        return
    fi
    mapfile -t COMPREPLY < <(compgen -W "$commands" -- "$current_word")
}

complete -F _fcsit_call_completion fcsit_call
complete -F _fcsit_call_completion ./fcsit_call
