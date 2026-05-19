## Stack

- **System under test:** `Adhesion Platform` — Website for firms/advisors to manage client assets.
- **Primary QA artifacts:** Markdown test plans, Gherkin scenarios, feature files, step files, Page Object Models (POM), test runners, bug reports, and handoff notes under `docs/`.
- **Automation Path:** pytest with Playwright via the Playwright MCP.
- **Reference docs:** Workspace files first, MCP-connected docs only when a lab explicitly asks for them.

## Test case format

- All test cases are written in **Gherkin** (`Given / When / Then`). One scenario per behavior.
- Scenarios belong to a `Feature:` that names the user-visible capability (e.g., "Feature: Delete a book"), not the implementation module.
- Each scenario has a one-line title in the imperative: `Scenario: Deleting a book requires explicit confirmation`.
- Preconditions go in a `Background:` block if they're shared across scenarios.
- Never embed implementation details in scenarios ("clicks the `#save-btn` element" is wrong — "submits the Add Book form" is right). Selectors live in POM, not in Gherkin.
- All assertions should occur in the step file, never in the POM.

## Bug report format

Every bug report **must** include all of the following. Missing sections block triage.

- **Summary** — one sentence, specific, no jargon.
- **Steps to reproduce** — numbered, imperative, reproducible by a reader with no context.
- **Expected** — what the spec says (or what a reasonable user expects).
- **Actual** — what happened. Quote error messages verbatim.
- **Environment** — browser + version, page URL, and any relevant test data.
- **Evidence** — screenshot, short clip, or written observation. Playwright trace if available.
- **Severity** — `Blocker / Critical / Major / Minor / Trivial`. Defined below.

Severity definitions:

| Severity | Definition                                                                    |
| -------- | ----------------------------------------------------------------------------- |
| Blocker  | Prevents a core flow. Data loss or unrecoverable state. No workaround.        |
| Critical | Core flow broken with an ugly workaround. Security or compliance risk.        |
| Major    | Non-core flow broken, or core flow has visible defect that users will report. |
| Minor    | Visible defect a user can work around without help.                           |
| Trivial  | Cosmetic. Copy, alignment, non-functional.                                    |

## Test naming

- Feature files: `C:\Users\aaron.skipper\git\qeautomation\tests\bdd\features\Adhesion` With name of th feature tested
- Step Files: `C:\Users\aaron.skipper\git\qeautomation\tests\bdd\steps\Adhesion` with the same base name as the feature file.
- Test Runners: `C:\Users\aaron.skipper\git\qeautomation\tests\bdd\runners\Adhesion` with the same base name as the feature file.
- POM: `C:\Users\aaron.skipper\git\qeautomation\tests\bdd\pages\Adhesion` with the same base name as the feature file, if the page is unique to that feature. If the page is shared across features, it should be named for the page, not the feature (e.g., `AddBookPage.py`).
- If you later create Playwright specs, their `test('...')` titles should mirror the scenario titles.

## Coverage expectations

For any new user-visible feature in BooksAdminUI, your QA coverage must cover at minimum:

1. **Happy path** — the most common success flow, end to end.
2. **Negative path** — at least one invalid-input path per form field.
3. **Critical Path** — any path that, if broken, would cause a Blocker or Critical bug. This is not necessarily the same as the happy path but may be on the way (e.g. being able to submit a proposal without having to select a custodian).
 <!-- 3. **Destructive action confirmation** — any action that mutates or deletes MUST have an explicit confirmation step, and MUST have a test that verifies the confirmation dialog appears.
4. **Empty state** — what the UI shows when the data source is empty (e.g., no books, no search results).
5. **Loading and error state** — what the UI shows while data is loading, and what it shows when a save or load action fails.
6. **Keyboard-only** — at least one scenario must be runnable by keyboard-only input (tab/enter). Accessibility is not optional. -->

## When in doubt

- If a user asks you to produce a test that skips one of the coverage expectations above, **ask**. Do not silently produce partial coverage.
- If a user asks you to file a bug without Evidence or Environment, **ask**. Do not submit an incomplete report just because the user didn't provide the fields.
- If a spec / ticket is silent on expected behavior for a feature **ask**. A silent spec is not an invitation to guess.
