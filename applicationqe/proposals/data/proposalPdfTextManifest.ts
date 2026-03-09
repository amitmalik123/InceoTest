import type { ProposalTextValidationOptions, ProposalSectionSnippetRule } from '../utils/pdfUtils';

export const mandatoryProposalSections = [
    'Your Financial Analysis',
    'Recommended Investment Portfolio',
    'Annual Portfolio Fees',
    'Important Information and Standardized Performance Returns',
    'Disclosures Regarding Compensation',
];

const commonProposalSections = [
    'Introduction',
    'Pursue Your Goals With Confidence',
    'Your Investment Team',
    'Ongoing Review of Your Portfolio',
    'Your Financial Analysis',
    'Recommended Investment Portfolio',
    'Annual Portfolio Fees',
    'Important Information and Standardized Performance Returns',
    'Disclosures Regarding Compensation',
    'Tax Management Services',
    'Client Signature',
    'Investment Policy Statement',
];

export const optionalProposalSections = commonProposalSections.filter(
    section => !mandatoryProposalSections.includes(section)
);

const sectionSnippetOverrides: Record<string, Omit<ProposalSectionSnippetRule, 'section'>> = {
    Introduction: {
        mustContainAll: ['Dear Guy'],
    },
    'Pursue Your Goals With Confidence': {
        mustContainAll: [
            'Equities have been the best asset class',
            'The cycle of emotions may impact',
            'Getting out at the wrong time',
        ],
    },
    'Your Investment Team': {
        mustContainAll: ['Whether you are saving for a specific goal', 'Your portfolio strategist', 'Your custodian'],
    },
    'Ongoing Review of Your Portfolio': {
        mustContainAll: [],
    },
    'Your Financial Analysis': {
        mustContainAll: ['Through our Discovery process'],
    },
    'Recommended Investment Portfolio': {
        mustContainAll: [
            'Based on your investment goals and circumstances',
            'The chart and table below show the depth',
            'The displayed Exchange Traded Funds',
            'Estimated account yield is a measure',
            'While there is no guarantee',
            'Looking at annualized rates',
            'The following table helps you evaluate',
            'A diversified portfolio can help',
            'Designing a portfolio is a balancing act',
        ],
    },
    'Annual Portfolio Fees': {
        mustContainAll: ['The Summary fee is based on a Portfolio Value of', 'The expense ratio is the annual fee'],
    },
    'Important Information and Standardized Performance Returns': {
        mustContainAll: ['This investment proposal was prepared for you based on'],
    },
    'Disclosures Regarding Compensation': {
        mustContainAll: ['1. Financial Advisor'],
    },
    'Tax Management Services': {
        mustContainAll: ['Keep more of what you earn', 'The estimated tax savings'],
    },
    'Client Signature': {
        mustContainAll: ['This investment proposal is not a contract'],
    },
    'Investment Policy Statement': {
        mustContainAll: [
            'The purpose of the Investment Policy Statement',
            'You have selected Profile',
            'The performance of the asset classes',
            'All information contained in this proposal is intended only for',
        ],
    },
};

export const commonProposalSectionSnippetRulesTemplate: ProposalSectionSnippetRule[] = commonProposalSections.map(
    section => ({
        section,
        ...(sectionSnippetOverrides[section] ?? { mustContainAll: [] }),
    })
);

function buildSectionSnippetRulesForIncludedSections(sections: string[]): ProposalSectionSnippetRule[] {
    const templateBySection = new Map(
        commonProposalSectionSnippetRulesTemplate.map(rule => [rule.section.toLowerCase(), rule])
    );

    return sections.map(section => {
        const templateRule = templateBySection.get(section.toLowerCase());
        if (!templateRule) {
            return {
                section,
                mustContainAll: [],
            };
        }

        return {
            section: templateRule.section,
            mustContainAll: [...(templateRule.mustContainAll ?? [])],
            mustContainAny: templateRule.mustContainAny ? [...templateRule.mustContainAny] : undefined,
            forbid: templateRule.forbid ? [...templateRule.forbid] : undefined,
        };
    });
}

export function buildProposalTextValidationManifest(options: {
    includeTableOfContents?: boolean;
    includedSections?: string[];
    excludedSections?: string[];
    appendixSections?: string[];
    tocSections?: string[];
}): ProposalTextValidationOptions {
    const baseSections = options.includedSections ?? commonProposalSections;

    const appendixSections = options.appendixSections ?? [];
    const includedSections = [...baseSections, ...appendixSections];
    const excludedSections = options.excludedSections ?? [];
    const tocSections = options.tocSections ?? baseSections;

    return {
        includedSections,
        excludedSections,
        includeTableOfContents: options.includeTableOfContents ?? true,
        // TOC in your examples documents section pages and does not list every appendix page.
        // Keep TOC checks focused on selected sections, not total PDF page count.
        tocSections,
        // Section snippet rules are canonical: if a section is included, it always uses the same rule set.
        sectionSnippetRules: buildSectionSnippetRulesForIncludedSections(includedSections),
    };
}

export function buildMandatoryProposalTextValidationManifest(options: {
    includeTableOfContents?: boolean;
}): ProposalTextValidationOptions {
    const baseSections = mandatoryProposalSections;

    return buildProposalTextValidationManifest({
        includeTableOfContents: options.includeTableOfContents,
        includedSections: baseSections,
        tocSections: baseSections,
    });
}

export function buildProposalTextValidationManifestExcludingTMS(options: {
    includeTableOfContents?: boolean;
}): ProposalTextValidationOptions {
    const baseSections = commonProposalSections.filter(section => section !== 'Tax Management Services');

    return buildProposalTextValidationManifest({
        includeTableOfContents: options.includeTableOfContents,
        includedSections: baseSections,
        tocSections: baseSections,
    });
}
