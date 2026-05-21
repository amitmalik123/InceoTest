"""Settings loader — reads environment configuration from a YAML file.

Path resolution (only one env var needed):
  1. TEST_CONFIG_PATH  — explicit path set by CI pipeline or local .env
                         e.g. config/stp/stp-journals/env.test11.yaml
  2. RuntimeError with clear instructions if not set.

Local .env (add one line for your team):
    TEST_CONFIG_PATH=config/stp/stp-journals/env.test11.yaml

CI: team-stage.yml sets TEST_CONFIG_PATH automatically from the configDir parameter:
    TEST_CONFIG_PATH=config/{configDir}/env.{environment}.yaml
"""
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from utils.logger import setup_logger

_REPO_ROOT = Path(__file__).resolve().parent.parent  # applicationqe/

# Load .env from applicationqe root for local dev. CI env-vars always take precedence.
load_dotenv(_REPO_ROOT / ".env")


def _resolve_config_path() -> Path:
    """Resolve config YAML path from TEST_CONFIG_PATH. Fails fast with clear instructions."""
    path = os.getenv("TEST_CONFIG_PATH")
    if path:
        return _REPO_ROOT / path
    raise RuntimeError(
        "\n"
        "Cannot load config — TEST_CONFIG_PATH is not set.\n"
        "\n"
        "Add one of the following to your .env file:\n"
        "  TEST_CONFIG_PATH=config/stp/stp-journals/env.test11.yaml\n"
        "  TEST_CONFIG_PATH=config/stp/stp-ict/env.test11.yaml\n"
        "\n"
        "Or pass it on the command line:\n"
        "  TEST_CONFIG_PATH=config/stp/stp-ict/env.test11.yaml pytest tests/...\n"
        "\n"
        "In CI, team-stage.yml sets this automatically via the configDir parameter.\n"
    )


class Settings:
    """Loads and exposes environment configuration from a team YAML file."""

    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config_dir  = config_path.parent
        # derive env name from filename: env.test11.yaml → "test11"
        self.env = config_path.stem.split(".")[-1]
        self.logger = setup_logger(__name__)
        self.config = self._load_config()
        self._mail_config = self._load_mail_config()
        self._queries = self._load_queries()

    # ── loaders ───────────────────────────────────────────────────────────────

    def _load_config(self) -> dict:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                "Verify TEST_CONFIG_PATH points to an existing YAML file."
            )
        with open(self.config_path, "r") as f:
            return yaml.safe_load(f)

    def _load_mail_config(self) -> dict:
        """Load mail_config.properties from the same folder as the env YAML, if present."""
        mail_path = self.config_dir / "mail_config.properties"
        cfg = {}
        if not mail_path.exists():
            return cfg
        try:
            with open(mail_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    cfg[k.strip()] = v.strip()
        except Exception as e:
            self.logger.error(f"Error loading mail config: {e}")
        return cfg

    def _load_queries(self) -> dict:
        """Load SQL queries from queries/sql_queries.yaml (repo-level, shared across teams)."""
        queries_path = _REPO_ROOT / "queries" / "sql_queries.yaml"
        if not queries_path.exists():
            self.logger.warning(f"Queries file not found: {queries_path}")
            return {}
        with open(queries_path, "r") as f:
            return yaml.safe_load(f) or {}

    # ── application ───────────────────────────────────────────────────────────

    @property
    def base_url(self) -> str:
        return self.config["application"]["base_url"]

    @property
    def login_url(self) -> str:
        return self.config["application"].get("login_url", self.base_url)

    @property
    def timeout(self) -> int:
        return self.config["application"]["timeout"]

    # ── browser ───────────────────────────────────────────────────────────────

    @property
    def browser_type(self) -> str:
        return self.config["browser"]["browser_type"]

    @property
    def headless(self) -> bool:
        return self.config["browser"]["headless"]

    @property
    def viewport(self) -> dict:
        return self.config["browser"]["viewport"]

    @property
    def browser_args(self) -> list:
        return self.config["browser"].get("args", [])

    # ── data ──────────────────────────────────────────────────────────────────

    @property
    def test_data_csv(self) -> Path:
        return _REPO_ROOT / self.config["data"]["test_data_csv"]

    @property
    def test_data_excel(self):
        p = self.config.get("data", {}).get("test_data_excel")
        return (_REPO_ROOT / p) if p else None

    # ── reporting ─────────────────────────────────────────────────────────────

    @property
    def allure_results_dir(self) -> Path:
        return _REPO_ROOT / self.config["reporting"]["allure_results"]

    # ── test ──────────────────────────────────────────────────────────────────

    @property
    def screenshot_each_step(self) -> bool:
        return self.config.get("test", {}).get("screenshot_each_step", False)

    # ── api ───────────────────────────────────────────────────────────────────

    @property
    def api_auth_token(self) -> str:
        return (
            os.getenv(f"{self.env.upper()}_API_AUTH_TOKEN")
            or os.getenv("API_AUTH_TOKEN")
            or self.config.get("api", {}).get("auth_token", "")
        )

    # ── database / vault ──────────────────────────────────────────────────────

    @property
    def database_config(self) -> dict:
        return self.config.get("database", {})

    @property
    def vault_databases(self) -> dict:
        return self.config.get("database", {}).get("vault_databases", {})

    @property
    def database_queries(self) -> dict:
        return self._queries

    def get_vault_connection_string(self, secret_name: str) -> str | None:
        """Fetch a connection string from the environment variable mapped from Key Vault."""
        env_var = secret_name.upper().replace("-", "_")
        value = os.getenv(env_var)
        if value:
            self.logger.info(f"Connection string resolved from env var: {env_var}")
        return value

    def get_vault_db_config(self, alias: str) -> dict:
        """Get vault database config by alias from the YAML vault_databases section."""
        if alias not in self.vault_databases:
            raise ValueError(
                f"Vault DB alias '{alias}' not found in config. "
                f"Available: {list(self.vault_databases)}"
            )
        return self.vault_databases[alias]

    # ── outlook / mail ────────────────────────────────────────────────────────

    @property
    def outlook_email(self) -> str:
        from utils.crypto_utils import decrypt_value
        raw = self._mail_config.get("outlook.email", "")
        if raw:
            try:
                return decrypt_value(raw)
            except Exception:
                pass
        return os.getenv("OUTLOOK_EMAIL") or self.config.get("outlook", {}).get("email", "")

    @property
    def outlook_password(self) -> str:
        from utils.crypto_utils import decrypt_value
        raw = self._mail_config.get("outlook.password", "")
        if raw:
            try:
                return decrypt_value(raw)
            except Exception:
                pass
        return (
            os.getenv("OUTLOOK_PASSWORD")
            or self.config.get("outlook", {}).get("password", "")
        )

    @property
    def outlook_imap_server(self) -> str:
        return (
            self._mail_config.get("outlook.imap_server")
            or os.getenv("OUTLOOK_IMAP_SERVER")
            or self.config.get("outlook", {}).get("imap_server", "outlook.office365.com")
        )

    @property
    def outlook_imap_port(self) -> int:
        raw = self._mail_config.get("outlook.imap_port") or os.getenv("OUTLOOK_IMAP_PORT")
        if raw:
            try:
                return int(raw)
            except ValueError:
                pass
        return self.config.get("outlook", {}).get("imap_port", 993)

    # ── encryption ────────────────────────────────────────────────────────────

    @property
    def secret_key(self) -> str:
        return self.config.get("secret_key", "") or os.getenv("ENCRYPTION_SECRET_KEY", "")


# ── Lazy singleton ─────────────────────────────────────────────────────────────

_instance: "Settings | None" = None


def get_settings() -> Settings:
    """Return the lazily-created Settings singleton (created once per process)."""
    global _instance
    if _instance is None:
        _instance = Settings(_resolve_config_path())
    return _instance


def __getattr__(name: str):
    """PEP 562 — allows: from config.settings import settings"""
    if name == "settings":
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
