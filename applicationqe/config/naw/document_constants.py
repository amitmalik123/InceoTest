"""Expected document names for PDF validation on View Documents page."""

# TDA (Schwab) Tradition indi- With Retain Account
TDA_RETAIN_ACCOUNT_DOCUMENTS = [
    "Account Set Up and Application",
    "Client Billing Authorization",
    "Limited Power of Attorney (LPOA) for Investment Advisor",
    "Account Agreements and Disclosures",
    "Asset-Based Pricing (ABP) Addendum",
    "Investment Management Services Agreement",
    "Client Relationship Summary",    
    "Platform Disclosure Packet",
    "Schedule of Charges",
    "Charles Schwab Pricing Guide",
    "Privacy Policy",
]

# TDA (Schwab) Tradition indi - Without Retain Account
TDA_NO_RETAIN_ACCOUNT_DOCUMENTS = [
    "Account Set Up and Application",
    "Client Billing Authorization",
    "Account Agreements and Disclosures",
    "IRA Account Application",
    "Beneficiary Designation Form for IRA and 403(b)(7) Accounts",
    "Investment Management Services Agreement",
    "Client Relationship Summary",
    "Platform Disclosure Packet",
    "Schedule of Charges",
    "Charles Schwab Pricing Guide",
    "Privacy Policy",
    "Planning and Consulting Fee Account Billing Authorization",
    "Planning and Consulting Fee ACH Billing Authorization",
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
    "IRA Distribution",
    "Beneficiary Designation Form",
    "State Income Tax Withholding Information",
]

# Fidelity Tradition indi - With Retain Account
FIDELITY_RETAIN_ACCOUNT_DOCUMENTS = [
    "Account Set Up and Application",
    "Add or Remove an Authorized agent/Advisor",
    "Client Billing Authorization",
    "Separately Managed Account Addendum",
    "Account Agreements and Disclosures",
    "Client Relationship Summary",
    "Investment Management Services Agreement",
    "Platform Disclosure Packet",
    "Privacy Policy",
    "Schedule of charges",
]


# Fidelity Tradition indi - Without Retain Account
FIDELITY_NO_RETAIN_ACCOUNT_DOCUMENTS = [
    "Account Set Up and Application",
    "Client Billing Authorization",
    "Separately Managed Premiere Select",
    "Signature and Date",
    "Account Agreements and Disclosures",
    "Client Relationship Summary",
    "Investment Management Services Agreement",
    "Platform Disclosure Packet",
    "Privacy Policy",
    "Schedule of charges",
    "Planning and Consulting Fee Account Billing Authorization",
    "Planning and Consulting Fee ACH Billing Authorization",
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
    "Periodic Investments",
    "Standing Periodic Journal Instructions for Separately Managed Accounts",
    "Power of Attorney New York",
    "Power of Attorney All states except New York",
    "Standing Payment Instructions",
    "IRA Periodic Distribution Request",
    "Premier Select IRA Periodic Distribution Request Form- IRA SWP",
]

# Individual
GNW_DOCUMENTS = [
    "Individual or Joint Application",
    "Additional Account Holder",
    "Duplicate Statements",
    "Investment Instructions",
    "Acknowledgements and Agreements",
    "Account Signatures",    
    "Client Billing Disclosure",
    "Account Agreements and Disclosures",
    "Investment Management Services Agreement",
    "Client Relationship Summary",
    "Platform Disclosure Brochure",
    "Custody Agreement",
    "AssetMark Trust Company Disclosures",
    "Privacy Policy",
    "Power of Attorney",
    "Planning and Consulting Fee ACH Billing Authorization",
    "Planning and Consulting Fee - Account Billing Authorization",
    "Cash Advantage Bancorp Checking Account",
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
    "Standing Letter of Authorization for ACH/Wire",
    "One-Time Contribution via ACH",
    "Dollar Cost Average",
    "Automatic Investment Plan",
]

# Individual
PRS_DOCUMENTS = [
    "Client Billing Authorization",
    "Open an Account",
    "Agreements Disclosures Cover Page",
    "Investment Management Services Agreement",
    "Client Relationship Summary",
    "Referral Disclosure Packet",
    "Terms and Conditions",
    "Platform Disclosure Packet",
    "Schedule of charges",
    "Privacy Policy",
    "Planning and Consulting Fee Account Billing Authorization",
    "Planning and Consulting Fee ACH Billing Authorization",
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
    "IRA Distribution",
    "ACH Standing Instructions",
    "IRA Systematic Withdrawal",
    "Standing Payment Instructions",
]

SWB_DIRECT_DOCUMENTS = [
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
]

FIDELITY_DIRECT_DOCUMENTS = [
    "Short -Term Cash Restriction Request",
    "Account Suspension Request",
]


def get_expected_documents(custodian: str, retain_account: bool) -> list[str]:
    """
    Get expected document list based on custodian and retain account flag.

    Args:
        custodian: Custodian name (e.g., "Schwab", "Fidelity")
        retain_account: Whether this is a retain account scenario

    Returns:
        List of expected document names
    """
    custodian_lower = custodian.strip().lower()

    if custodian_lower in ("schwab", "tda"):
        return TDA_RETAIN_ACCOUNT_DOCUMENTS if retain_account else TDA_NO_RETAIN_ACCOUNT_DOCUMENTS
    elif custodian_lower == "fidelity":
        return FIDELITY_RETAIN_ACCOUNT_DOCUMENTS if retain_account else FIDELITY_NO_RETAIN_ACCOUNT_DOCUMENTS
    elif custodian_lower in ("gnw", "assetmark trust", "assetmark trust company"):
        return GNW_DOCUMENTS
    elif custodian_lower in ("prs", "psr", "pershing", "pershing advisor solutions"):
        return PRS_DOCUMENTS
    elif custodian_lower in ("schwab direct", "swb direct", "swb"):
        return SWB_DIRECT_DOCUMENTS
    elif custodian_lower in ("fidelity direct", "fdd"):
        return FIDELITY_DIRECT_DOCUMENTS
    else:
        raise ValueError(f"Unknown custodian: {custodian}")
