"""APro Proposal Risk Assessment step (wizard-1)."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage
from utils.allure_logger import get_allure_logger

logger = get_allure_logger(__name__)


class ProposalRiskPage(BasePage):
    """Page object for APro proposal Risk Assessment step (wizard-1).

    Handles risk method selection (questionnaire/manual/skip) and all
    questionnaire question answering logic.
    """

    def __init__(self, page: Page, base_url: str = ""):
        super().__init__(page, base_url=base_url)

        # Step 2 (Assess Risk) container
        self.step_assess_risk_panel: Locator = page.locator("#proposal-wizard-1")

        # Risk method selection cards
        self.risk_method_cards: Locator = page.locator(".risk-method-card")
        self.risk_method_questionnaire: Locator = page.locator(".risk-method-card").filter(
            has_text="Questionnaire"
        )
        self.risk_method_manual: Locator = page.locator(".risk-method-card").filter(
            has_text="Manual"
        )
        self.risk_method_skip: Locator = page.locator(".risk-method-card").filter(has_text="Skip")

        # Questionnaire containers (rendered after selecting Questionnaire card)
        self.step_questionnaire_panel: Locator = page.locator("#proposal-wizard-1")
        self.questionnaire_container: Locator = page.locator("#questionnaire-container")
        self.questionnaire_questions: Locator = page.locator("#questionnaire-questions")

    def wait_for_assess_risk_step(self, timeout: int = 10000) -> None:
        """Wait for the Assess Risk (wizard step 2, proposal-wizard-1) to be visible."""
        logger.info("Waiting for Assess Risk (proposal-wizard-1) step to be visible")
        self.wait_for_element(self.step_assess_risk_panel, state="visible", timeout=timeout)

    def select_risk_method(self, method: str) -> None:
        """Select a risk assessment method card (questionnaire/manual/skip)."""
        logger.info(f"Selecting risk assessment method: {method}")
        mapping = {
            "questionnaire": self.risk_method_questionnaire,
            "manual": self.risk_method_manual,
            "skip": self.risk_method_skip,
        }
        card = mapping.get(method.lower())
        if card is None:
            raise ValueError(
                f"Unknown risk method: {method}. Must be one of: {list(mapping.keys())}"
            )
        self.click(card)
        logger.info(f"Risk method '{method}' selected")

    def select_manual_risk_level(self, risk_level: str) -> None:
        """Select a risk level from the Manual method radio buttons.

        Args:
            risk_level: One of "Conservative", "Growth & Income", "Balanced", "Growth", "Aggressive"
        """
        logger.info(f"Selecting manual risk level: {risk_level}")

        # Map user-friendly names to the exact radio button labels
        level_map = {
            "conservative": "Conservative (0-20)",
            "growth & income": "Growth & Income (21-40)",
            "balanced": "Balanced (41-60)",
            "growth": "Growth (61-80)",
            "aggressive": "Aggressive (81-100)",
        }

        normalized_level = risk_level.lower().strip()
        if normalized_level not in level_map:
            raise ValueError(
                f"Unknown risk level: {risk_level}. Must be one of: {list(level_map.keys())}"
            )

        exact_label = level_map[normalized_level]

        # Click the radio button with this label
        radio_button = self.page.locator(f"radio:has-text('{exact_label}')")
        self.click(radio_button)
        logger.info(f"Risk level '{exact_label}' selected")

    def wait_for_questionnaire_step(self, timeout: int = 10000) -> None:
        """Wait for the questionnaire panel to be visible."""
        logger.info("Waiting for questionnaire step to be visible")
        self.wait_for_element(self.questionnaire_questions, state="visible", timeout=timeout)

    def select_question_answer(self, question_id: int | str, value: str) -> None:
        """Select an answer option for a specific question by value."""
        logger.info(f"Selecting answer '{value}' for question {question_id}")
        qname = self._normalize_qname(question_id)
        selector = f"input[name='{qname}'][value='{value}']"
        self.page.locator(selector).click()

    def select_first_answer_for_question(self, question_id: int | str) -> None:
        """Select the first answer option for a question."""
        logger.info(f"Selecting first answer for question {question_id}")
        qname = self._normalize_qname(question_id)
        self.page.locator(f"input[name='{qname}']").first.click()

    def get_question_ids(self) -> list:
        """Extract all questionnaire question IDs from the DOM."""
        logger.info("Collecting questionnaire question ids")
        question_inputs = self.page.locator("#questionnaire-questions input[name]")
        count = question_inputs.count()

        ids = set()
        for i in range(count):
            name_attr = question_inputs.nth(i).get_attribute("name")
            if name_attr:
                ids.add(name_attr)

        return sorted(ids)

    def get_question_meta(self) -> list:
        """Return full question metadata including question number, text, and options."""
        logger.info("Retrieving questionnaire question metadata")
        meta = self.page.evaluate(
            """
            () => {
                const questions = [];
                const containers = document.querySelectorAll('#questionnaire-questions .question-group');

                containers.forEach((container, idx) => {
                    const titleEl = container.querySelector('.question-title, legend, label');
                    const title = titleEl ? titleEl.textContent.trim() : `Question ${idx + 1}`;

                    const inputs = Array.from(container.querySelectorAll('input[type="radio"]'));
                    const options = inputs.map(inp => ({
                        value: inp.value,
                        text: inp.parentElement?.textContent?.trim() || inp.value,
                        checked: inp.checked
                    }));

                    const name = inputs[0]?.name || `question_${idx}`;

                    questions.push({
                        name: name,
                        title: title,
                        options: options,
                        selected: options.find(o => o.checked)?.value || null
                    });
                });

                return questions;
            }
            """
        )
        return meta

    def _normalize_qname(self, q: int | str) -> str:
        """Normalize question identifier to its name attribute."""
        if isinstance(q, str):
            return q
        # Convert 0-based index to question name (fallback)
        return f"question_{q}"

    def answer_question_by_id(self, question_id: int | str, option_value: str) -> None:
        """Answer a question by option value."""
        logger.info(f"Answering question {question_id} with value {option_value}")
        qname = self._normalize_qname(question_id)
        self._apply_answer_to_question(qname, option_value)

    def answer_question_by_text(self, question_id: int | str, option_text: str) -> None:
        """Answer a question by option text (label)."""
        logger.info(f"Answering question {question_id} with text '{option_text}'")
        qname = self._normalize_qname(question_id)

        # Find the option by text and get its value
        option_input = self.page.locator(
            f"input[name='{qname}'] + label:has-text('{option_text}')"
        ).locator(".. input[type='radio']")

        value = option_input.get_attribute("value")
        if not value:
            raise ValueError(f"Option '{option_text}' not found for question {question_id}")

        self._apply_answer_to_question(qname, value)

    def answer_question_by_index(
        self, idx: int, option_value_or_text: str, by_text: bool = False
    ) -> None:
        """Answer a question by its position in the question list."""
        logger.info(
            f"Answering question at index {idx} with {option_value_or_text} (by_text={by_text})"
        )
        question_ids = self.get_question_ids()
        if idx >= len(question_ids):
            raise IndexError(f"Question index {idx} out of range (total: {len(question_ids)})")

        qname = question_ids[idx]
        if by_text:
            self.answer_question_by_text(qname, option_value_or_text)
        else:
            self._apply_answer_to_question(qname, option_value_or_text)

    def _get_answer_for_question(
        self, qname: str, idx: int, answers: dict | None = None
    ) -> tuple[bool, str | None]:
        """Determine which answer to apply for a question.

        Returns:
            (should_answer, answer_value) tuple
        """
        if answers and qname in answers:
            return (True, answers[qname])

        # Default behavior: select first option
        option_value = self.page.locator(f"input[name='{qname}']").first.get_attribute("value")

        return (True, option_value)

    def _apply_answer_to_question(self, qname: str, value: str | int) -> None:
        """Apply an answer to a question by clicking its radio option."""
        logger.info(f"Applying answer value '{value}' to question {qname}")
        self.page.locator(f"input[name='{qname}'][value='{value}']").click()

    def answer_all_questions(self, answers: dict | None = None, default: str = "first") -> int:
        """Answer all questionnaire questions.

        Args:
            answers: Optional dict mapping question_name -> answer_value
            default: Default behavior if no answer provided ("first", "skip", etc.)

        Returns:
            Number of questions answered
        """
        logger.info(f"Answering all questionnaire questions with default={default}")
        question_ids = self.get_question_ids()
        answered = 0

        for qname in question_ids:
            should_answer, value = self._get_answer_for_question(qname, answered, answers)

            if should_answer and value:
                self._apply_answer_to_question(qname, value)
                answered += 1
                logger.info(f"Answered question {qname} with {value}")

        logger.info(f"Successfully answered {answered}/{len(question_ids)} questions")
        return answered

    def answer_first_option_for_question(self, question_id: int | str) -> None:
        """Backwards-compatible alias for selecting the first option."""
        logger.info(f"Selecting first option for question {question_id}")
        self.select_first_answer_for_question(question_id)

    def click_next(self) -> None:
        """Click Next button to proceed to Allocation step."""
        logger.info("Clicking Next from Risk Assessment step")
        next_button = self.step_assess_risk_panel.locator("button[data-wizard-next]")

        # Wait for the button to not be disabled
        self.page.locator("#proposal-wizard-1 button[data-wizard-next]:not([disabled])").wait_for(
            state="visible", timeout=10000
        )

        # Give the form validation a moment to settle
        self.page.wait_for_timeout(1000)

        # Force click to bypass any actionability checks
        next_button.click(force=True)

    def click_previous(self) -> None:
        """Click Previous button to go back to Details step."""
        logger.info("Clicking Previous from Risk Assessment step")
        prev_button = self.step_assess_risk_panel.locator("button[data-wizard-previous]")
        prev_button.click()
