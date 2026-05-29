import os


class SystemOptions:
    """System-level configuration values read from environment."""

    current_proposal_quarter: str | None = os.getenv("CURRENT_SYS_PROPOSAL_QUARTER_END")
    previous_proposal_quarter: str | None = os.getenv("PREVIOUS_SYS_PROPOSAL_QUARTER_END")


__all__ = ["SystemOptions"]
