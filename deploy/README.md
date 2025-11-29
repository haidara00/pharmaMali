# Deployment notes — PharmaGestion

This folder contains simple deployment artifacts for running PharmaGestion with Gunicorn + WhiteNoise. The goal is to provide non-Docker, minimal deployment helpers (macOS launchd, Windows NSSM notes, and a Gunicorn start script).

Prerequisites
- Python 3.10+ in a virtualenv
- Install project requirements: `python3 -m pip install -r requirements.txt`
- Set environment variables (see `.env.example`) and create `.env` in project root

Common steps (Linux/macOS)

1. Create and activate virtualenv, install requirements.
2. Copy `.env.example` to `.env` and set real values.
3. Run `python3 manage.py collectstatic --noinput` to collect static files (WhiteNoise will serve them).
4. Start the service using the script:

   ./deploy/gunicorn_start.sh

   or use systemd/launchd with the provided sample plist file.

macOS (launchd)
- Edit `deploy/com.example.pharmagestion.plist` replacing `/path/to/venv` and `/path/to/project` and set `SECRET_KEY` and other env vars.
- Load with: `launchctl load ~/Library/LaunchAgents/com.example.pharmagestion.plist` (or place in `/Library/LaunchDaemons` for system-wide service).

Windows (NSSM)
- See `deploy/nssm_instructions.txt`. Consider using Waitress on Windows instead of Gunicorn.

Notes and recommendations
- Do NOT commit `.env` with secrets. Keep `DEBUG=False` in production and set `ALLOWED_HOSTS`.
- Use a proper production database (Postgres) instead of SQLite for multi-user, multi-process deployments.
- If you plan to terminate or rotate code deployments, consider a process manager (systemd, launchd, or NSSM) to auto-restart on crash.
# Deploying pharmagestion (minimal, no Docker/nginx)

This folder contains minimal artifacts and examples to run the Django app with Gunicorn + WhiteNoise and service definitions for macOS (LaunchAgent `.plist`) and Windows (NSSM instructions).

Key points:
- This setup uses Gunicorn to serve the WSGI app and WhiteNoise to serve static files from Django.
- No reverse proxy (nginx) is included — acceptable for low-traffic single-user deployments.
- You must set secure environment variables (especially the Django secret key) and set `DEBUG=False` in production.

Quick start (macOS / Linux / WSL):

1. Create and activate a Python virtualenv and install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file (copy `.env.example`) and set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, and `ALLOWED_HOSTS`.

3. Collect static files (WhiteNoise will serve them):

```bash
python3 manage.py collectstatic --noinput
```

4. Migrate (if needed):

```bash
python3 manage.py migrate
```

5. Start the app with the provided script (optionally set `VENV` to the venv path):

```bash
VENV="$PWD/.venv" ./deploy/gunicorn_start.sh
```

macOS LaunchAgent (example):

- Copy `deploy/com.example.pharmagestion.plist` to `~/Library/LaunchAgents/` and edit paths (`/path/to/project` and `/path/to/venv`) before loading:

```bash
cp deploy/com.example.pharmagestion.plist ~/Library/LaunchAgents/com.example.pharmagestion.plist
launchctl load ~/Library/LaunchAgents/com.example.pharmagestion.plist
```

Windows (NSSM):

- See `deploy/nssm_instructions.txt` — using NSSM to wrap a Python command is possible but not recommended for production; consider WSL or a Linux host.

Security recommendations:
- Keep `DJANGO_SECRET_KEY` out of source control.
- Set `DEBUG=False` and `ALLOWED_HOSTS` appropriately.
- Prefer PostgreSQL in production and configure `DATABASES` accordingly.

If you want, I can:
- Add a small `pharmagestion/settings_production.py` to demonstrate recommended production settings, or
- Add a systemd unit file template for Linux, or
- Add a GitHub Actions workflow to run tests on push (I already added a CI workflow example).
