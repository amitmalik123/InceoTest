**Critical Path Validation for proposal flow** (Combining into one test since they are all from same flow and proposal does not allow skipping steps so would need to copmlete a proposal up to each step per test anyways)

**Required Field Validation on Details**

_Cases_

- Missing Name (first/last) for prospect
- Missing Investment Amount
- investment amount < $1
- Missing Custodian
- Missing Account Type
- Missing Advisor for prospect

_Expected_

- “Next” button unclickable with clear validation message under invalid field
- Unable to move to later step by clicking top nav
- No partial creation that leaves orphan records (or if record is created, it remains in Draft with correct status and fields null)

**Questionnaire Completion Gating**

Scenario: Attempt “Next” without answering all questions.

_Expected_

- Progress blocked i.e. Next button disabled
- Unable to click to later step from top nav
- Guidance to complete to unanswered questions

**Risk Range Filtering & Allocation Selection Integrity**

Scenario: Questionnaire results should constrain available allocations (advisor risk range).

_Expected_

Only eligible composites appear/selectable

Selected composite persists and drives reports

**Fee Suppression + Explanation Compliance**

Scenario: User toggles “Suppress Advisor Fee” but omits explanation.

_Expected_

- Cannot save fee suppression without explanation
- Firm-based permissioning respected (if applicable)

**Proposal Generation / Preview & Generated Timestamp**

Scenario: Generate preview without benchmark / with invalid report selection.

_Expected_

- Benchmark required before preview
- Errors messages provide actionable information (not generic)
- Preview output matches selected reports and ordering

**Finish Locks Proposal Permanently**
Scenario: After Finish, user attempts to edit any section.

_Expected_

- All proposal sections read-only
- Only Copying a Proposal can create an editable version
- No “silent saves”

**Prospects List Grid Reflects True State (Data Contract)**

Scenario: After each milestone (create, questionnaire complete, generate, finish), the Prospects List must update correctly.

_Expected_

- Status and timestamps reflect reality; no stale caching
- Sorting by Date Created behaves correctly

**History/Actions Options Behave Correctly by Status**

Scenario: Actions vary based on whether a proposal is draft/finished/hidden.

_Expected_

- View/Email action buttons become available when generation possible/complete
- Copy Proposal available for finished proposals
- Hide/Unhide toggles visibility without deleting
- Enroll Account routes to legacy enroll/edit without corrupting proposal data

**Session timeout dialog + redirect safety**
Why critical: The code enforces a timeout popup at 2 hours and redirects after 60s. This can nuke in-progress work.

_Expected_

- Timeout dialog opens reliably (no JS errors).
- Countdown updates and redirects to /Proposals/Home/Exit at expiry.
- “Keep Alive” successfully extends session and returns user to work without data loss.
- No accidental “Finish”/state transitions triggered by timeout events.
