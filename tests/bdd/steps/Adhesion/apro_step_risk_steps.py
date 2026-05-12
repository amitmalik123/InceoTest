"""Step definitions for the APro proposal Assess Risk wizard step (step 2)."""

from pytest_bdd import parsers, then, when

from pages import AproProposalsPage
from utils.allure_logger import get_allure_logger
from utils.playwright_api_validator import PlaywrightResponseTracker

logger = get_allure_logger(__name__)


@when("I select the questionnaire risk assessment method")
@when("I select the Questionnaire risk assessment method")
@then("I select the Questionnaire risk assessment method")
def _select_questionnaire_method(proposal_page: AproProposalsPage):
    """Select the Questionnaire card on the Assess Risk step."""
    proposal_page.wait_for_assess_risk_step()
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/GetQuestionnaire" in r.url
    ) as resp_info:
        proposal_page.select_risk_method("questionnaire")
    assert (
        resp_info.value.status == 200
    ), f"GetQuestionnaire returned {resp_info.value.status}, expected 200"


@when("I skip the risk assessment")
@when("I select the Skip risk assessment method")
@then("I skip the risk assessment")
def _skip_risk_assessment(proposal_page: AproProposalsPage):
    """Select the Skip card on the Assess Risk step to bypass risk assessment."""
    logger.info("Skipping risk assessment")
    proposal_page.wait_for_assess_risk_step()
    proposal_page.select_risk_method("skip")
    logger.info("Risk assessment skipped")
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/SkipRiskAssessment" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"SkipRiskAssessment returned {resp_info.value.status}, expected 200"


@when(parsers.parse("I select Manual risk assessment with {risk_level}"))
@when(parsers.parse("I select the Manual risk assessment method as {risk_level}"))
def _select_manual_risk_method(proposal_page: AproProposalsPage, risk_level: str):
    """Select the Manual card and choose a risk level.

    Args:
        risk_level: One of "Conservative", "Growth & Income", "Balanced", "Growth", "Aggressive"
    """
    logger.info(f"Selecting Manual risk assessment with level: {risk_level}")
    proposal_page.wait_for_assess_risk_step()
    proposal_page.select_risk_method("manual")
    proposal_page.select_manual_risk_level(risk_level)
    logger.info(f"Manual risk level '{risk_level}' selected")
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/SaveManualRisk" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"SaveManualRisk returned {resp_info.value.status}, expected 200"


@when("I complete the Assess Risk step")
@then("I complete the Assess Risk step")
def _questionnaire(proposal_page: AproProposalsPage):
    """Answer all questionnaire questions and proceed to Allocation step.

    Assumes questionnaire method was already selected in prior step.
    """
    # Track ALL SaveQuestionnaireAnswer responses
    questionnaire_tracker = PlaywrightResponseTracker(proposal_page.page)
    questionnaire_tracker.start_tracking("/Proposals/Editor/SaveQuestionnaireAnswer")

    # Answer all questionnaire questions with first option (default behavior)
    proposal_page.answer_all_questions()

    questionnaire_tracker.stop_tracking()
    questionnaire_tracker.validate_all_successful(api_name="SaveQuestionnaireAnswer")

    # validate GetAllocationsData on transition to Allocation step
    with proposal_page.page.expect_response(
        lambda r: "/Proposals/Editor/GetAllocationsData" in r.url
    ) as resp_info:
        proposal_page.click_next()
    assert (
        resp_info.value.status == 200
    ), f"GetAllocationsData returned {resp_info.value.status}, expected 200"

    # Wait for network to idle to ensure all allocation-related APIs can start
    proposal_page.page.wait_for_load_state("networkidle", timeout=5000)
