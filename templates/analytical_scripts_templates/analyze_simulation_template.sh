#!/usr/bin/env bash

set -euo pipefail

# Directory containing TXT files from one simulation dataset.
DATA_DIR="${1:-/path/to/simulation_data}"
OUTPUT_DIR="${2:-${DATA_DIR}/FcsIT_results}"
CHUNKS="${CHUNKS:-15}"

if ! command -v fcsit_call >/dev/null 2>&1; then
    echo "Error: fcsit_call is not available in PATH." >&2
    exit 1
fi

if [[ ! -d "${DATA_DIR}" ]]; then
    echo "Error: data directory does not exist: ${DATA_DIR}" >&2
    exit 1
fi

if ! find "${DATA_DIR}" -maxdepth 1 -type f -name '*.txt' -print -quit \
    | grep -q .; then
    echo "Error: no TXT simulation data found in ${DATA_DIR}." >&2
    exit 1
fi

mkdir -p -- "${OUTPUT_DIR}"

printf -v load_arguments \
    '{"directory":"%s","output_directory":"%s"}' \
    "${DATA_DIR}" "${OUTPUT_DIR}"
printf -v parameter_arguments \
    '{"time_bin":0.000001,"points":150,"chunks":%d,"tau_min":0.001,"tau_max":100,"cross_correlation":false}' \
    "${CHUNKS}"

fcsit_call system.ping
fcsit_call gui.select_method '{"name":"time_bin_corr"}'
fcsit_call time_bin_corr.load_directory "${load_arguments}"
fcsit_call time_bin_corr.set_parameters "${parameter_arguments}"
fcsit_call time_bin_corr.correlate_all

echo "Completed simulation analysis: ${OUTPUT_DIR}"
