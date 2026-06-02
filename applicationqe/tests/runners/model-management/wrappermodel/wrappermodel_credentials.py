"""WrapperModel credential resolver.

Resolves test credentials by environment and optional username override.
All values are scoped to WrapperModel test runner usage.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CredentialRecord:
    username: str
    password: str
    aplid: str
    environment: str


_CREDENTIALS: tuple[CredentialRecord, ...] = (
    CredentialRecord("Sample_agent_es4", "QAAdminUser_33a", "AGBFDE", "Prod"),
    CredentialRecord("testwrappermodeluser", "Wrappermodel1!", "AGBFDH", "Prod"),
    CredentialRecord("T11_AG8959_Perf", "QAAdminUser_33a", "AG8959", "test01"),
    CredentialRecord("sampleadvisorlogin", "amkF1n@nc23S", "AGAGCB", "test01"),
    CredentialRecord("sampleadvisorlogin", "amkF1n@nc23S", "AGAGCB", "Dev01 - D12"),
    CredentialRecord("AGBJTZ_AGWMTest1", "QAwm123$", "AGBJTZ", "T11"),
    CredentialRecord("AGWMTest2_T11", "QAwm123$", "AGBJU0", "T11"),
    CredentialRecord("AGWMTest3", "QAwm123$", "AGBJU1", "T11"),
    CredentialRecord("AGWMTest4_T11", "QAwm123$", "AGBJU2", "T11"),
    CredentialRecord("AGWMTest_T11", "QAwm123$", "AGBJU3", "T11"),
    CredentialRecord("AGWMTest6_T11", "QAwm123$", "AGBJU4", "T11"),
)


def _normalize_env(value: str) -> str:
    raw = (value or "").strip().lower()
    compact = "".join(ch for ch in raw if ch.isalnum())

    if any(token in compact for token in ("prod",)):
        return "prod"
    if any(token in compact for token in ("dev01", "d12", "dev")):
        return "dev01"
    if any(token in compact for token in ("test01", "tes01")):
        return "test01"
    if any(token in compact for token in ("test11", "t11", "qa")):
        return "t11"

    return compact


def _record_env_key(record: CredentialRecord) -> str:
    return _normalize_env(record.environment)


def resolve_wrappermodel_credentials(runtime_env: str, requested_username: str | None = None) -> dict[str, str]:
    """Resolve credentials by runtime env and optional username.

    Selection rules:
    1) If username is provided, choose that user in matching environment when possible,
       otherwise choose that user from any environment.
    2) If username is not provided, pick the first configured record for the environment.
    3) Fallback to legacy default credentials.
    """

    env_key = _normalize_env(runtime_env)
    username = (requested_username or "").strip()

    if username:
        for row in _CREDENTIALS:
            if row.username.lower() == username.lower() and _record_env_key(row) == env_key:
                return {
                    "username": row.username,
                    "password": row.password,
                    "aplid": row.aplid,
                    "environment": row.environment,
                }
        for row in _CREDENTIALS:
            if row.username.lower() == username.lower():
                return {
                    "username": row.username,
                    "password": row.password,
                    "aplid": row.aplid,
                    "environment": row.environment,
                }

    for row in _CREDENTIALS:
        if _record_env_key(row) == env_key:
            return {
                "username": row.username,
                "password": row.password,
                "aplid": row.aplid,
                "environment": row.environment,
            }

    return {
        "username": "T11_AG8959_Perf",
        "password": "QAAdminUser_33a",
        "aplid": "AG8959",
        "environment": "test01",
    }
