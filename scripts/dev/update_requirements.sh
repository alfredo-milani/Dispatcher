#!/usr/bin/env bash

declare -r -i EXIT_SUCCESS=0
declare -r -i EXIT_FAILURE=1
declare -r NULL='/dev/null'

declare -r rel_project_root='Dispatcher'
declare -r abs_project_root=$(basename "$(pwd)")


if [[ "${rel_project_root}" != "${abs_project_root}" ]]; then
    echo "[ERROR] To excecute this script the working directory must be project root (${rel_project_root}), current: $(pwd)"
    exit ${EXIT_FAILURE}
fi

pip_tools='pip-tools'
pip_compile='pip-compile'
pip_sync='pip-sync'
if ! command -v "${pip_compile}" &> ${NULL} || ! command -v "${pip_sync}" &> ${NULL}; then
    echo "[ERROR] Missing tool: ${pip_tools}"
    echo "Install with \"python -m pip install pip-tools\" and retry"
    exit ${EXIT_FAILURE}
fi


echo "- Current directory: $(pwd)"

# Update requirements.txt file with libs from requirements.in
echo "- Updating requirements.txt file"
pip-compile --output-file=requirements.txt requirements.in

# Sync libs
echo "- Syncing libs"
pip-sync

exit ${EXIT_SUCCESS}
