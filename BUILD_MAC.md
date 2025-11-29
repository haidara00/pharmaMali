
Mac build instructions — py2app (PharmaGestion)
=============================================

This document describes a minimal, practical flow to build a macOS `.app` using `py2app`.

Prerequisites (build on a Mac)
- Python 3.10+ installed (use the Apple-provided `py` launcher or `python3`).
- Xcode command-line tools (for native build toolchain): `xcode-select --install`.
- Build on macOS (you cannot build mac `.app` on Linux/Windows).

Recommended: create and use a virtual environment for the build:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

1) Install project requirements and py2app

```bash
# from project root
pip install -r requirements.txt
pip install py2app
```

2) Prepare static files and database

- Collect static files so WhiteNoise will serve them from the bundle (recommended):

```bash
python manage.py collectstatic --noinput
```

- If you ship with a local SQLite DB for demo/offline mode, ensure `db.sqlite3` is at project root or that your app will create/populate it on first run.

3) Build the `.app` (alias mode during development)

Alias build (fast, symlinked) — good for iteration:

```bash
python3 setup.py py2app -A
```

Full build (standalone bundle):

```bash
python3 setup.py py2app
```

This produces a `dist/PharmaGestion.app` bundle.

4) Run the built app

- Double-click `dist/PharmaGestion.app` or run from terminal:

```bash
open dist/PharmaGestion.app
```

Notes and caveats
- Environment variables: The built app runs in its own environment. If your project uses a `.env` file or requires `DJANGO_SETTINGS_MODULE`, make sure the launcher script (`waitress_server.py`) loads `.env` or use a wrapper. The current `waitress_server.py` sets `DJANGO_SETTINGS_MODULE` internally.
- Port & firewall: The first run may trigger a firewall prompt to allow incoming connections. Explain to users they should allow the app.
- Signing & notarization: To distribute an app without Gatekeeper warnings you'll need to sign and notarize the `.app` (Apple Developer account). If you skip signing, users will need to right-click → Open and confirm.
- Size: The produced `.app` will include Python and dependencies — expect tens of MBs.
- Build on macOS: py2app requires building on macOS. Use CI mac runners or a Mac build machine for automation.

Troubleshooting
- Missing modules at runtime: add them to `OPTIONS['includes']` or `OPTIONS['packages']` in `setup.py`.
- Static/template paths: If your app cannot find templates/static, ensure resources are added in `setup.py` and that the server knows the correct base path (you may need to adjust settings.py to look for files relative to the application bundle).

Next steps
- If you want, I can add a small `build_mac.sh` script that prepares the venv, installs deps, runs `collectstatic`, and invokes `py2app`.
- I can also add a wrapper to copy a `.env.example` into the bundle and/or a small first-run bootstrap that creates the DB and an admin user.
