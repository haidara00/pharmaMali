#!/usr/bin/env bash
set -euo pipefail

# build_mac.sh
# Simple helper to build a macOS `.app` using py2app.
# Usage:
#   ./build_mac.sh         # full standalone build
#   ./build_mac.sh -A      # alias (fast) build
#   ./build_mac.sh -h      # help

VENV_DIR=".venv"
PYTHON="python3"
SETUP_PY="setup.py"
REQ_FILE="requirements.txt"
ALIAS=0

usage() {
  cat <<EOF
Usage: $0 [-A] [-h]
  -A    Alias (fast) build (passes -A to py2app)
  -h    Show this help
EOF
  exit 1
}

while getopts ":Ah" opt; do
  case ${opt} in
    A ) ALIAS=1 ;;
    h ) usage ;;
    \? ) usage ;;
  esac
done

echo "[build_mac] Starting py2app build (alias=${ALIAS})"

# Create venv if missing
if [ ! -d "${VENV_DIR}" ]; then
  echo "[build_mac] Creating virtualenv in ${VENV_DIR}..."
  ${PYTHON} -m venv "${VENV_DIR}"
fi

# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

echo "[build_mac] Upgrading pip/setuptools/wheel"
pip install --upgrade pip setuptools wheel

if [ -f "${REQ_FILE}" ]; then
  echo "[build_mac] Installing project requirements from ${REQ_FILE}"
  pip install -r "${REQ_FILE}"
else
  echo "[build_mac] No ${REQ_FILE} found — skipping requirements install"
fi

echo "[build_mac] Ensuring py2app is installed"
pip install py2app

# Provide a friendly .env copy if missing
if [ ! -f .env ] && [ -f .env.example ]; then
  echo "[build_mac] .env not found — copying .env.example to .env (you may edit it)"
  cp .env.example .env
fi

echo "[build_mac] Running Django collectstatic"
${PYTHON} manage.py collectstatic --noinput

if [ ${ALIAS} -eq 1 ]; then
  echo "[build_mac] Running alias build: python ${SETUP_PY} py2app -A"
  ${PYTHON} "${SETUP_PY}" py2app -A
else
  echo "[build_mac] Running full build: python ${SETUP_PY} py2app"
  ${PYTHON} "${SETUP_PY}" py2app
fi

echo "[build_mac] Build finished. Check the 'dist' directory for the .app bundle."

deactivate || true

exit 0
