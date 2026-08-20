#!/usr/bin/env bash

set -euo pipefail

# Directory containing PTU files from one experimental acquisition.
DATA_DIR="${1:-/path/to/experimental_acquisition}"
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

mkdir -p -- "${OUTPUT_DIR}"

printf -v load_arguments '{"directory":"%s"}' "${DATA_DIR}"
printf -v parameter_arguments \
    '{"points":150,"chunks":%d,"tau_min":0.001,"tau_max":100,"cross_correlation":false,"time_gate":true,"background_correction":true}' \
    "${CHUNKS}"
printf -v corr_export_arguments \
    '{"directory":"%s","format":"corr"}' "${OUTPUT_DIR}"
printf -v dat_export_arguments \
    '{"directory":"%s","format":"dat"}' "${OUTPUT_DIR}"

fcsit_call system.ping
fcsit_call gui.select_method '{"name":"ptu_corr"}'
fcsit_call ptu_corr.load_directory "${load_arguments}"
fcsit_call ptu_corr.forget_all_measurements
fcsit_call ptu_corr.set_parameters "${parameter_arguments}"
fcsit_call ptu_corr.calculate_filters_all
fcsit_call ptu_corr.select_tab '{"tab":"correlation"}'
fcsit_call ptu_corr.correlate_all
fcsit_call ptu_corr.export_all "${corr_export_arguments}"
fcsit_call ptu_corr.export_all "${dat_export_arguments}"

echo "Completed experimental analysis: ${OUTPUT_DIR}"
