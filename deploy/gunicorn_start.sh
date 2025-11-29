#!/usr/bin/env bash
# Simple Gunicorn start script for PharmaGestion
# Usage: copy to server, ensure virtualenv is activated, then run: ./gunicorn_start.sh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

# Load .env if present
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  . .env
  set +a
fi

: ${GUNICORN_WORKERS:=3}
: ${GUNICORN_BIND:=0.0.0.0:8000}
: ${DJANGO_SETTINGS_MODULE:=pharmagestion.settings}

echo "Starting Gunicorn with $GUNICORN_WORKERS workers bound to $GUNICORN_BIND"

exec gunicorn "pharmagestion.wsgi:application" \
  --workers "$GUNICORN_WORKERS" \
  --bind "$GUNICORN_BIND" \
  --log-level info \
  --access-logfile - \
  --error-logfile -
#!/usr/bin/env bash
# Simple gunicorn startup wrapper for this project.
# Usage: set environment variables (see ../.env.example) and run this script.

set -euo pipefail

# Activate virtualenv if path provided via VENV
if [ -n "${VENV:-}" ] && [ -f "$VENV/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$VENV/bin/activate"
fi

# Default bind address and worker count
if [ -z "${BIND:-}" ]; then
  BIND="0.0.0.0:8000"
fi
if [ -z "${WORKERS:-}" ]; then
  WORKERS=3
fi

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-pharmagestion.settings}

echo "Starting Gunicorn with bind=$BIND workers=$WORKERS"

exec gunicorn pharmagestion.wsgi:application \
  --bind "$BIND" \
  --workers "$WORKERS" \
  --log-level info \
  --access-logfile - \
  --error-logfile - \
  --forwarded-allow-ips='*'
