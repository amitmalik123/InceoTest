**Create Client Proposal (End-to-End)**

Goal: Advisor produces a finished proposal with preview and history entry for an existing client.

Steps

Access Proposal Tool (any entry point)

Client Data prefilled; adjust Investment Amount if needed

Current Holdings prefill; edit a holding; save

Complete Questionnaire

Composite Selection: choose an allocation within risk range

(Optional) Add Fee Options

Proposal Generation: select “All Reports” (or template), choose benchmark, Preview Proposal

Finish Proposal

History/Actions: View/Email Proposal (URL/PDF) and verify delivery options

**Create Prospect Proposal (End-to-End via Prospects List)**

Goal: Prospect proposal appears in Prospects List grid and can be completed.

Steps

Navigate: Prospects → Create New Prospect Proposal

Enter required Client Data (Name, Investment Amount default $1 acceptable, Advisor required)

Add holdings (manual or import)

Complete questionnaire

Select composite

Preview, then Finish

Confirm proposal appears and updates in Prospects List Grid

**Create prospect from Actions dropdown (entry point)**

“Create Prospect” action triggers openAddProposalModal().

Flow

Prospects List → Actions → Create Prospect.

Editor modal loads; user completes wizard.

Pass criteria

Action launches modal reliably.

No double-open even with rapid clicking.

**Global Search → Account row hover → Actions menu → ProposalSystem**

Global search results populate accounts with metadata flags and dynamically load action menu items from /Actions/ActionsDynamicDropdown. “ProposalSystem” routes to /Accounts/ProposalViaAction/{id}.

Flow

Use Smart Search Bar, type valid account.

Hover account row → actions list loads.

Choose “ProposalSystem” action.

Proposal flow opens for that account.

Pass criteria

Actions menu appears and contains Proposal-related actions when expected.

Navigation opens correct context (account-based proposal).

**Resume proposal creation from Prospects List**

Flow

Prospects List loads.

Click a prospect name hyperlink in the grid.

Proposal editor modal loads for that proposal.

Wizard initializes, validation “wakes up” (the forced input change event).

User proceeds through steps and saves/finishes.

Pass Criteria

Modal loads once and renders correct proposal data.

Wizard step navigation works; validation works without manual refresh.

No duplicate modals; no stuck loading overlay.

**Smart Filter usage on Prospects List (stateful UX)**

Flow

Expand/collapse Smart Filter panel.

Select one Status filter (e.g., “Questionnaire Completed”).

Grid refreshes (server filtering), icon changes to “filter-full”.

Clear filters (uncheck all) → icon returns to empty filter, grid returns to baseline.

Pass criteria

Filter panel state persists after refresh (when preference save succeeds).

Grid updates are consistent with serverFiltering + criteria.

**Export Prospects Grid (with and without filters)**

Flow

Export with no filters → full list export.

Apply a filter → export again → export reflects filtered set.

Pass criteria

Export completes successfully; output matches current filters.

Export doesn’t degrade grid behavior afterward (column widths, layout).

**Import Holdings Successfully**

Goal: Import tool loads holdings accurately.

Steps

Open Import

Paste correctly ordered columns (Symbols, Description, Acquisition Date, Shares, Total Cost, Price per Share)

Preview

Submit

Holdings appear; edit one symbol and save

**Copy Proposal (Post-Finish)**

Goal: New editable proposal created from a finished one.

Steps

Open finished proposal → Copy Proposal

Update holdings

Regenerate preview

Finish copied proposal
