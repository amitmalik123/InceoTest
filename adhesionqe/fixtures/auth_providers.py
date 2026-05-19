"""
Auth provider adapter for integrating external multi-user auth runner.

This adapter uses a subprocess to run the supplied `python-playwright-auth`
runner (no import required) and exposes two functions used by fixtures:

- `ensure_sessions()` - ensure runner has produced fresh storage files
- `find_storage(app, role, username)` - locate a storageState path for tests

The subprocess approach avoids needing to rename the pasted folder.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from config.settings import get_settings

RUNNER_SCRIPT = Path("utils/login_adhesion.py")
RUNNER_AUTH_DIR = Path("tests/.auth")
TIMESTAMP_FILE = RUNNER_AUTH_DIR / "session-timestamp.json"

# Env vars expected by the runner; used to warn when missing
REQUIRED_ENV_VARS = [
    "AUTH_LOGIN_TIMEOUT_MS",
    "AUTH_LOGIN_CONCURRENCY",
    # Common user envs (not exhaustive) - presence of storage file vars is important
    "SUPER_ADVISOR_AUTH_FILE",
    "ADHESION_USER_AUTH_FILE",
    "ADVISOR_AUTH_FILE",
    "ADHESION_AUTH_FILE",
]


def _runner_needs_refresh(force: bool = False) -> bool:
    if force or os.getenv("AUTH_FORCE_REFRESH", "").lower() in ("1", "true", "yes"):
        return True
    # If no timestamp file exists, but we already have runner-produced
    # auth files, use the earliest auth-file creation time as the
    # canonical timestamp (this records when the first session was
    # produced). Otherwise, require a refresh.
    if not TIMESTAMP_FILE.exists():
        try:
            if RUNNER_AUTH_DIR.exists():
                candidates = list(RUNNER_AUTH_DIR.glob("*.json"))
                if candidates:
                    mtimes = [int(p.stat().st_mtime * 1000) for p in candidates if p.exists()]
                    if mtimes:
                        earliest = min(mtimes)
                        TIMESTAMP_FILE.parent.mkdir(parents=True, exist_ok=True)
                        TIMESTAMP_FILE.write_text(json.dumps({"timestamp": earliest}))
                        now = int(__import__("time").time() * 1000)
                        return (now - earliest) > 24 * 60 * 60 * 1000
        except Exception:
            # If anything goes wrong, request a refresh
            return True
        return True

    try:
        data = json.loads(TIMESTAMP_FILE.read_text())
        ts = int(data.get("timestamp", 0))
        now = int(__import__("time").time() * 1000)
        # If the recorded timestamp is in the future, treat it as stale
        if ts > now:
            return True
        # 24h freshness
        return (now - ts) > 24 * 60 * 60 * 1000
    except Exception:
        return True


def ensure_sessions(env_config: Optional[dict] = None, force: bool = False) -> None:
    """Run the external runner to ensure storageState files exist.

    If the pasted `python-playwright-auth` folder exists, run it as a subprocess.
    Otherwise, this function is a noop (assume other mechanisms produce files).
    """
    if not _runner_needs_refresh(force=force):
        return

    if RUNNER_SCRIPT.exists():
        # validate env vars and warn if missing
        # If caller didn't supply overrides, try to populate from YAML auth config
        if not env_config:
            try:
                settings = get_settings()
                auth_cfg = settings.config.get("auth", {})
                env_config = {}
                if "login_concurrency" in auth_cfg:
                    env_config["AUTH_LOGIN_CONCURRENCY"] = str(auth_cfg.get("login_concurrency"))
                if "login_timeout_ms" in auth_cfg:
                    env_config["AUTH_LOGIN_TIMEOUT_MS"] = str(auth_cfg.get("login_timeout_ms"))
            except Exception:
                env_config = env_config or {}

        missing = [
            v
            for v in REQUIRED_ENV_VARS
            if not os.getenv(v) and not (env_config and v in env_config)
        ]
        if missing:
            print(f"[AUTH_PROVIDER] Warning: missing env vars for auth runner: {missing}")

        print("[AUTH_PROVIDER] Running external auth runner to refresh sessions...")
        env = os.environ.copy()
        # Allow passing env vars from env_config if provided
        if env_config:
            for k, v in env_config.items():
                if k not in env:
                    env[k] = str(v)
        # Ensure the subprocess can import repo-local modules by adding the
        # workspace root to PYTHONPATH if it's not already present.
        try:
            repo_root = str(Path(__file__).resolve().parents[2])
        except Exception:
            repo_root = os.getcwd()

        existing_pp = env.get("PYTHONPATH", "")
        if repo_root not in existing_pp.split(os.pathsep):
            env["PYTHONPATH"] = repo_root + (os.pathsep + existing_pp if existing_pp else "")

        # Use the same Python interpreter that's running the tests to avoid
        # missing-dependency issues when the runner is executed as a subprocess.
        # If caller requested a forced refresh, signal the runner via env var
        if force:
            env["AUTH_FORCE_REFRESH"] = "1"

        subprocess.check_call([sys.executable, str(RUNNER_SCRIPT)], env=env)
        # Update the timestamp to now on successful runner execution
        try:
            now_ms = int(__import__("time").time() * 1000)
            TIMESTAMP_FILE.parent.mkdir(parents=True, exist_ok=True)
            TIMESTAMP_FILE.write_text(json.dumps({"timestamp": now_ms}))
        except Exception as e:
            print(f"[AUTH_PROVIDER] Warning: failed to write timestamp file: {e}")
        return

    print("[AUTH_PROVIDER] No external runner found; skipping session refresh")


def find_storage(app: str, role: Optional[str], username: Optional[str] = None) -> Optional[str]:
    """Locate a storageState file for the given app/role/username.

    Lookup order:
      1. Environment variable matching ROLE_AUTH_FILE (e.g. ADVISOR_AUTH_FILE)
    2. Runner auth dir files (tests/.auth/*{role}*.json)
    3. Fallback to tests/.auth/{username}.json or tests/.auth/{app}_{username}.json
    """
    if role:
        env_name = f"{role.upper()}_AUTH_FILE"
        path = os.getenv(env_name)
        if path:
            return path

    # try runner auth dir
    if RUNNER_AUTH_DIR.exists() and role:
        candidates = list(RUNNER_AUTH_DIR.glob(f"*{role}*.json"))
        if candidates:
            return str(candidates[0])

    # fallback patterns
    if username:
        fallback1 = Path("tests/.auth") / f"{username}.json"
        if fallback1.exists():
            return str(fallback1)

        fallback2 = Path("tests/.auth") / f"{app}_{username}.json"
        if fallback2.exists():
            return str(fallback2)

    return None
