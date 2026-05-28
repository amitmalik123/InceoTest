"""Central registry for journal flow runner metadata."""

from dataclasses import dataclass
from typing import Iterable, List, Optional, Set, Tuple


@dataclass(frozen=True)
class FlowDefinition:
    """Metadata for a runnable journal flow."""

    name: str
    slug: str
    test_file: str
    report_dir: str


JOURNAL_FLOWS: Tuple[FlowDefinition, ...] = (
    FlowDefinition(
        name="Like2Like",
        slug="like2like",
        test_file="tests/test_like2like_journal_recorder_allure.py",
        report_dir="like2like",
    ),
    FlowDefinition(
        name="IRA",
        slug="ira",
        test_file="tests/test_ira_journal_online_flow_allure.py",
        report_dir="ira",
    ),
    FlowDefinition(
        name="Roth",
        slug="roth",
        test_file="tests/test_roth_conversion_flow_allure.py",
        report_dir="roth",
    ),
)


def available_flow_slugs() -> List[str]:
    """Return canonical flow slugs in registry order."""
    return [flow.slug for flow in JOURNAL_FLOWS]


def resolve_journal_flows(selected: Optional[Iterable[str]] = None) -> Tuple[List[FlowDefinition], List[str]]:
    """Resolve selected flow aliases to known flow definitions."""
    if not selected:
        return list(JOURNAL_FLOWS), []

    requested = [token.strip().lower() for token in selected if token and token.strip()]
    if not requested:
        return list(JOURNAL_FLOWS), []

    resolved: List[FlowDefinition] = []
    unknown: List[str] = []
    added: Set[str] = set()

    for token in requested:
        match = None
        for flow in JOURNAL_FLOWS:
            aliases = {flow.slug, flow.name.lower(), flow.report_dir.lower()}
            if token in aliases:
                match = flow
                break

        if match is None:
            unknown.append(token)
            continue

        if match.slug not in added:
            resolved.append(match)
            added.add(match.slug)

    return resolved, unknown
