import asyncio
import json
import os
import time
from pathlib import Path

from playwright.async_api import async_playwright

try:
    from config.settings import get_settings

    settings = get_settings()
    BASE_URL = settings.base_url
    print(f"[AUTH RUNNER] Using base_url from YAML: {BASE_URL}")
except Exception as e:
    raise RuntimeError(
        "Auth runner requires TEST_ENV and a corresponding config/env.<TEST_ENV>.yaml file."
        " Set TEST_ENV to a valid environment and ensure its YAML exists."
    ) from e


def _int_env(key: str, default: int | None) -> int | None:
    """Return int value for env key, None if env is empty string meaning 'unlimited'.

    - If env is not set -> return default
    - If env is empty string -> return None (signal: unlimited concurrency)
    - Otherwise parse int and return, falling back to default on parse error
    """
    val = os.getenv(key)
    if val is None:
        # Try YAML fallback via settings.config for auth-related keys
        try:
            auth_cfg = settings.config.get("auth", {})
            # map env names like AUTH_LOGIN_CONCURRENCY -> possible yaml keys
            if key.startswith("AUTH_LOGIN_"):
                suffix = key[len("AUTH_LOGIN_") :].lower()
                candidates = [f"login_{suffix}", suffix]
                yaml_val = None
                for c in candidates:
                    if c in auth_cfg:
                        yaml_val = auth_cfg.get(c)
                        break
                if yaml_val is None:
                    return default
                if yaml_val == "":
                    return None
                try:
                    return int(str(yaml_val))
                except Exception:
                    return default
        except Exception:
            return default
    if val == "":
        return None
    try:
        return int(str(val))
    except Exception:
        return default


AUTH_TIMEOUT_MS = _int_env("AUTH_LOGIN_TIMEOUT_MS", 60000)
CONCURRENCY = _int_env("AUTH_LOGIN_CONCURRENCY", None)
AUTH_DIR = Path("tests/.auth")
TIMESTAMP_FILE = AUTH_DIR / "session-timestamp.json"
FORCE_REFRESH = os.getenv("AUTH_FORCE_REFRESH")


# Removed .env comment parsing: CSV must include `role` and `storage` columns.


def _sanitize_role(role: str) -> str:
    return "".join([c if c.isalnum() else "_" for c in role]).strip("_")


def _build_users_from_csv(csv_path: Path) -> list:
    import csv

    users: list[dict] = []
    if not csv_path.exists():
        return users

    with open(csv_path, newline="", encoding="utf8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # If the CSV row's username begins with '#' treat the row as commented out
            raw_username = row.get("username") or ""
            if raw_username.lstrip().startswith("#"):
                continue
            username = raw_username.strip()
            password = (row.get("password") or "").strip()
            role = (row.get("role") or "").strip()
            storage = (row.get("storage") or "").strip()
            if not username or not password:
                continue

            if not role:
                role = username

            if storage:
                # normalize slashes first
                storage = storage.replace("\\", "/")
                # if already targeted at tests/.auth, leave as-is
                if storage.startswith("tests/.auth"):
                    pass
                elif "playwright/.auth" in storage:
                    storage = storage.replace("playwright/.auth", "tests/.auth", 1)
                elif storage.startswith(".auth/"):
                    storage = storage.replace(".auth/", "tests/.auth/", 1)
                else:
                    # replace any other .auth/ occurrence but avoid duplicating tests/
                    storage = storage.replace(".auth/", "tests/.auth/")
            else:
                storage = f"tests/.auth/{_sanitize_role(role)}.json"

            expected = (row.get("expected") or "").strip()
            if not expected:
                rlow = role.lower()
                if "adhesion user limited" in rlow or "limited" in rlow:
                    expected = "/Administration/AllocationChangeList"
                elif "adhesion" in rlow:
                    expected = "/Administration/Impersonation"
                elif "strategist" in rlow or "strat" in rlow:
                    expected = "/Strategist/Dashboard"
                else:
                    expected = "/Dashboard"

            users.append(
                {
                    "role": role,
                    "username": username,
                    "password": password,
                    "expected": expected,
                    "storage": storage,
                }
            )

    return users


# Build USERS from CSV for the active TEST_ENV. Fallback: keep legacy env-driven list if CSV missing.
CSV_PATH = (
    Path(settings.test_data_csv) if "settings" in globals() else Path("data/test_data.mpstage.csv")
)
USERS = _build_users_from_csv(CSV_PATH)
if not USERS:
    raise RuntimeError(
        f"Auth runner requires a non-empty CSV at {CSV_PATH}; include username,password,role,storage columns"
    )


async def login_one(playwright, user):
    # Respect PLAYWRIGHT_HEADLESS env var: treat empty/false/0/no as headed
    headless_env = os.getenv("PLAYWRIGHT_HEADLESS")
    if headless_env is None:
        headless = True
    else:
        headless = headless_env.lower() not in ("", "0", "false", "no", "headful")
    browser = await playwright.chromium.launch(headless=headless)
    context = await browser.new_context()
    page = await context.new_page()
    try:
        print(f"🔐 Logging in as {user['username']}...")
        await page.goto(BASE_URL, timeout=AUTH_TIMEOUT_MS)

        # wait for username input (try common selectors)
        await page.wait_for_selector(
            'input[name="username"], #okta-signin-username', timeout=AUTH_TIMEOUT_MS
        )

        # fill credentials
        await page.fill('input[name="username"], #okta-signin-username', user["username"])
        await page.fill('input[name="password"], #okta-signin-password', user["password"])

        # click sign-in (common okta button or role-based)
        try:
            await page.click("#okta-signin-submit", timeout=5000)
        except Exception:
            # fallback to role-based button
            await page.click(
                'button:has-text("Sign in"), button:has-text("Sign In"), button:has-text("Log in")'
            )

        # wait for expected url path
        await page.wait_for_url(f"**{user['expected']}", timeout=AUTH_TIMEOUT_MS)

        # write storage state
        storage_path = Path(user["storage"])
        storage_path.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(storage_path))
        print(f"✅ Session for {user['username']} saved to {storage_path}")
    except Exception:
        safe = (user.get("username") or "unknown").replace("@", "_").replace("+", "_")
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        try:
            screenshot = AUTH_DIR / f"{safe}.png"
            html_file = AUTH_DIR / f"{safe}.html"
            await page.screenshot(path=str(screenshot), full_page=True)
            content = await page.content()
            html_file.write_text(content, encoding="utf8")
            print(f"🧾 Saved debug artifacts for {user['username']}: {screenshot}, {html_file}")
        except Exception as save_err:
            print("Failed to save debug artifacts:", save_err)
        raise
    finally:
        await browser.close()


async def login_all_users():
    if not FORCE_REFRESH:
        now = int(time.time() * 1000)
        if TIMESTAMP_FILE.exists():
            try:
                data = json.loads(TIMESTAMP_FILE.read_text())
                ts = data.get("timestamp")
                if isinstance(ts, int) and now - ts < 24 * 60 * 60 * 1000:
                    print("🕒 Sessions fresh; skipping login refresh")
                    return
            except Exception:
                print("⚠️ Failed to parse timestamp file; will refresh")
        else:
            print("ℹ️ Timestamp file missing. Will refresh.")
    else:
        print("⚡ Force refresh enabled via AUTH_FORCE_REFRESH")

    users = [u for u in USERS if u.get("username") and u.get("password") and u.get("storage")]
    skipped = len(USERS) - len(users)
    if skipped:
        print(f"⚠️ Skipping {skipped} user(s) with missing env values")

    failures = []
    if CONCURRENCY is not None and CONCURRENCY > 0:
        print(f"🚀 Logging in {len(users)} users with concurrency {CONCURRENCY}")
        async with async_playwright() as p:
            sem = asyncio.Semaphore(CONCURRENCY)

            async def worker(u):
                async with sem:
                    await login_one(p, u)

            tasks = [worker(u) for u in users]
            for t in asyncio.as_completed(tasks):
                try:
                    await t
                except Exception as e:
                    failures.append(str(e))
    else:
        print(f"🚀 Logging in {len(users)} users concurrently (no limit)")
        async with async_playwright() as p:
            tasks = [login_one(p, u) for u in users]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            failures = [str(r) for r in results if isinstance(r, Exception)]

    if failures:
        raise RuntimeError(f"Session refresh failed: {len(failures)} error(s)")

    # write timestamp
    try:
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        TIMESTAMP_FILE.write_text(json.dumps({"timestamp": int(time.time() * 1000)}))
        print("✅ Login sessions refreshed.")
    except Exception as e:
        print("⚠️ Failed to write timestamp file:", e)


if __name__ == "__main__":
    asyncio.run(login_all_users())
