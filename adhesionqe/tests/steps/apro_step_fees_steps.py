"""Step definitions for the APro proposal Fees wizard step (step 6)."""

from pytest_bdd import then, when

from pages import AproProposalsPage


@when("I complete the Fees step")
@then("I complete the Fees step")
def _fees(proposal_page: AproProposalsPage):
    """Confirm we reached Fees (step 6) and click Next — placeholder step."""
    proposal_page.wait_for_fees_step()
    # validate GetProposalSummary API call on transition to Generate Proposal step
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/GetProposalSummary" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"GetProposalSummary returned {resp_info.value.status}, expected 200"
