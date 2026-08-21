#!/usr/bin/env bash

set -euo pipefail

# Directory containing correlation files from one experimental dataset.
CORRELATION_DIR="${1:-/path/to/experimental_correlations/AutoCorr_ch1}"
MODEL="${MODEL:-One-component simple diffusion}"

if ! command -v fcsit_call >/dev/null 2>&1; then
    echo "Error: fcsit_call is not available in PATH." >&2
    exit 1
fi

if [[ ! -d "${CORRELATION_DIR}" ]]; then
    echo "Error: correlation directory does not exist: ${CORRELATION_DIR}" >&2
    exit 1
fi

fit_format() {
    local format="$1"
    local data_type result_path load_arguments model_arguments export_arguments

    case "${format}" in
        corr) data_type='bin' ;;
        dat) data_type='3C' ;;
        *) echo "Error: unsupported format: ${format}" >&2; return 1 ;;
    esac

    if ! find "${CORRELATION_DIR}" -maxdepth 1 -type f -name "*.${format}" \
        -print -quit | grep -q .; then
        echo "Skipping missing ${format^^} data: ${CORRELATION_DIR}" >&2
        return
    fi

    result_path="${CORRELATION_DIR}/results_${format}.csv"
    rm -f -- "${CORRELATION_DIR}/workspace.dct"

    printf -v load_arguments \
        '{"directory":"%s","data_type":"%s"}' \
        "${CORRELATION_DIR}" "${data_type}"
    printf -v model_arguments '{"model":"%s"}' "${MODEL}"
    printf -v export_arguments '{"path":"%s"}' "${result_path}"

    fcsit_call fitting.reset_results
    fcsit_call fitting.load_directory "${load_arguments}"
    fcsit_call fitting.reset_workspace
    fcsit_call fitting.set_model "${model_arguments}"
    fcsit_call fitting.set_options '{"weights":true}'
    fcsit_call fitting.reset_tau_range
    fcsit_call fitting.fit_all
    fcsit_call fitting.export_results "${export_arguments}"
}

printf -v plot_arguments '{"directory":"%s"}' "${CORRELATION_DIR}"

fcsit_call system.ping
fcsit_call gui.select_method '{"name":"fitting"}'
fit_format corr
fit_format dat
fcsit_call fitting.plot_all "${plot_arguments}"

echo "Completed experimental fitting: ${CORRELATION_DIR}"
