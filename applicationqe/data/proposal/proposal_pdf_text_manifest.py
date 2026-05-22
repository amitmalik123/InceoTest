"""
Proposal PDF text validation manifest configuration.
Converted from TypeScript: proposalPdfTextManifest.ts

Defines proposal section requirements and snippet validation rules
for comprehensive PDF content validation.
"""

import logging
from typing import Optional
from pages.proposal.proposal_pdf_utils import (
    ProposalTextValidationOptions,
    ProposalSectionSnippetRule,
)

logger = logging.getLogger(__name__)

# Mandatory sections that must appear in every proposal
MANDATORY_PROPOSAL_SECTIONS = [
    "Your Financial Analysis",
    "Recommended Investment Portfolio",
    "Annual Portfolio Fees",
    "Important Information and Standardized Performance Returns",
    "Disclosures Regarding Compensation",
]

# All common proposal sections (mandatory + optional)
COMMON_PROPOSAL_SECTIONS = [
    "Introduction",
    "Pursue Your Goals With Confidence",
    "Your Investment Team",
    "Ongoing Review of Your Portfolio",
    "Your Financial Analysis",
    "Recommended Investment Portfolio",
    "Annual Portfolio Fees",
    "Important Information and Standardized Performance Returns",
    "Disclosures Regarding Compensation",
    "Tax Management Services",
    "Client Signature",
    "Investment Policy Statement",
]

# Optional sections (those not mandatory)
OPTIONAL_PROPOSAL_SECTIONS = [
    section
    for section in COMMON_PROPOSAL_SECTIONS
    if section not in MANDATORY_PROPOSAL_SECTIONS
]

# Section snippet overrides - required text snippets per section
_SECTION_SNIPPET_OVERRIDES = {
    "Introduction": {
        "must_contain_all": ["Dear Guy"],
    },
    "Pursue Your Goals With Confidence": {
        "must_contain_all": [
            "Equities have been the best asset class",
            "The cycle of emotions may impact",
            "Getting out at the wrong time",
        ],
    },
    "Your Investment Team": {
        "must_contain_all": [
            "Whether you are saving for a specific goal",
            "Your portfolio strategist",
            "Your custodian",
        ],
    },
    "Ongoing Review of Your Portfolio": {
        "must_contain_all": [],
    },
    "Your Financial Analysis": {
        "must_contain_all": ["Through our Discovery process"],
    },
    "Recommended Investment Portfolio": {
        "must_contain_all": [
            "Based on your investment goals and circumstances",
            "The chart and table below show the depth",
            "The displayed Exchange Traded Funds",
            "Estimated account yield is a measure",
            "While there is no guarantee",
            "Looking at annualized rates",
            "The following table helps you evaluate",
            "A diversified portfolio can help",
            "Designing a portfolio is a balancing act",
        ],
    },
    "Annual Portfolio Fees": {
        "must_contain_all": [
            "The Summary fee is based on a Portfolio Value of",
            "The expense ratio is the annual fee",
        ],
    },
    "Important Information and Standardized Performance Returns": {
        "must_contain_all": [
            "This investment proposal was prepared for you based on"
        ],
    },
    "Disclosures Regarding Compensation": {
        "must_contain_all": ["1. Financial Advisor"],
    },
    "Tax Management Services": {
        "must_contain_all": [
            "Keep more of what you earn",
            "The estimated tax savings",
        ],
    },
    "Client Signature": {
        "must_contain_all": [
            "This investment proposal is not a contract"
        ],
    },
    "Investment Policy Statement": {
        "must_contain_all": [
            "The purpose of the Investment Policy Statement",
            "You have selected Profile",
            "The performance of the asset classes",
            "All information contained in this proposal is intended only for",
        ],
    },
}


def _build_common_proposal_section_snippet_rules() -> list[ProposalSectionSnippetRule]:
    """Build snippet validation rules for all common proposal sections."""
    rules = []
    for section in COMMON_PROPOSAL_SECTIONS:
        overrides = _SECTION_SNIPPET_OVERRIDES.get(section, {})
        rule = ProposalSectionSnippetRule(
            section=section,
            must_contain_all=overrides.get("must_contain_all", []),
            must_contain_any=overrides.get("must_contain_any"),
            forbid=overrides.get("forbid"),
        )
        rules.append(rule)
    return rules


# Template rules for all common sections
COMMON_PROPOSAL_SECTION_SNIPPET_RULES_TEMPLATE = (
    _build_common_proposal_section_snippet_rules()
)


def _build_section_snippet_rules_for_included_sections(
    sections: list[str],
) -> list[ProposalSectionSnippetRule]:
    """
    Build section snippet rules for specified sections.

    Args:
        sections: List of section names to build rules for

    Returns:
        List of ProposalSectionSnippetRule objects
    """
    # Create a map of lowercase section names to template rules
    template_by_section = {
        rule.section.lower(): rule for rule in COMMON_PROPOSAL_SECTION_SNIPPET_RULES_TEMPLATE
    }

    rules = []
    for section in sections:
        template_rule = template_by_section.get(section.lower())

        if template_rule is None:
            rule = ProposalSectionSnippetRule(
                section=section,
                must_contain_all=[],
            )
        else:
            rule = ProposalSectionSnippetRule(
                section=template_rule.section,
                must_contain_all=[
                    *(template_rule.must_contain_all or [])
                ],
                must_contain_any=template_rule.must_contain_any,
                forbid=template_rule.forbid,
            )

        rules.append(rule)

    return rules


def build_proposal_text_validation_manifest(
    include_table_of_contents: bool = True,
    included_sections: Optional[list[str]] = None,
    excluded_sections: Optional[list[str]] = None,
    appendix_sections: Optional[list[str]] = None,
    toc_sections: Optional[list[str]] = None,
    include_snippet_validation: bool = False,
) -> ProposalTextValidationOptions:
    """
    Build proposal text validation manifest for comprehensive PDF validation.

    Args:
        include_table_of_contents: Whether to validate table of contents
        included_sections: Sections to include (defaults to all common sections)
        excluded_sections: Sections to exclude
        appendix_sections: Additional appendix sections
        toc_sections: Specific sections for TOC validation
        include_snippet_validation: Whether to validate snippet content (default False for now)

    Returns:
        ProposalTextValidationOptions configured for validation
    """
    base_sections = included_sections or COMMON_PROPOSAL_SECTIONS

    appendix_secs = appendix_sections or []
    final_included_sections = [*base_sections, *appendix_secs]
    final_excluded_sections = excluded_sections or []
    final_toc_sections = toc_sections or base_sections

    logger.debug(
        f"Building validation manifest with {len(final_included_sections)} "
        f"included sections and {len(final_excluded_sections)} excluded sections"
    )

    return ProposalTextValidationOptions(
        included_sections=final_included_sections,
        excluded_sections=final_excluded_sections,
        include_table_of_contents=include_table_of_contents,
        toc_sections=final_toc_sections,
        section_snippet_rules=_build_section_snippet_rules_for_included_sections(
            final_included_sections
        ) if include_snippet_validation else [],
    )


def build_proposal_text_validation_manifest_excluding_tms(
    include_table_of_contents: bool = True,
) -> ProposalTextValidationOptions:
    """
    Build proposal text validation manifest excluding Tax Management Services section.
    Skips snippet validation and validates only that sections appear in TOC.

    Args:
        include_table_of_contents: Whether to validate table of contents

    Returns:
        ProposalTextValidationOptions without TMS section (TOC only validation)
    """
    base_sections = [
        section
        for section in COMMON_PROPOSAL_SECTIONS
        if section != "Tax Management Services"
    ]

    logger.debug(
        f"Building validation manifest excluding TMS with {len(base_sections)} sections (TOC only)"
    )

    return build_proposal_text_validation_manifest(
        include_table_of_contents=include_table_of_contents,
        included_sections=base_sections,
        toc_sections=base_sections,
        include_snippet_validation=False,
    )


def build_mandatory_proposal_text_validation_manifest(
    include_table_of_contents: bool = True,
) -> ProposalTextValidationOptions:
    """
    Build proposal text validation manifest for mandatory sections only.

    Args:
        include_table_of_contents: Whether to validate table of contents

    Returns:
        ProposalTextValidationOptions with only mandatory sections
    """
    logger.debug(
        f"Building mandatory validation manifest with {len(MANDATORY_PROPOSAL_SECTIONS)} sections"
    )

    return build_proposal_text_validation_manifest(
        include_table_of_contents=include_table_of_contents,
        included_sections=MANDATORY_PROPOSAL_SECTIONS,
        toc_sections=MANDATORY_PROPOSAL_SECTIONS,
    )
