import os


class Auth:
    """Environment-backed auth file paths for various user types."""

    adhesion_user_auth_file: str = os.getenv("ADHESION_USER_AUTH_FILE", "")
    advisor_auth_file: str = os.getenv("ADVISOR_AUTH_FILE", "")
    advisor_strategist_auth_file: str = os.getenv("ADVISOR_STRAT_AUTH_FILE", "")
    non_strat_super_advisor_auth_file: str = os.getenv("NON_STRAT_SUPER_ADVISOR_AUTH_FILE", "")
    qa_advisor_auth_file: str = os.getenv("QA_ADVISOR_AUTH_FILE", "")
    strategist_manager_auth_file: str = os.getenv("STRAT_MANAGER_AUTH_FILE", "")
    super_advisor_auth_file: str = os.getenv("SUPER_ADVISOR_AUTH_FILE", "")
    adhesion_limited_user_auth_file: str = os.getenv("ADHESION_USER_LIMITED_AUTH_FILE", "")
    branch_manager_auth_file: str = os.getenv("BRANCH_MANAGER_AUTH_FILE", "")


__all__ = ["Auth"]
