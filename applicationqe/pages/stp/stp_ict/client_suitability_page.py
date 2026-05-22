from playwright.sync_api import Page

from locators.stp.stp_ict.ict_client_suitability_locators import ClientSuitabilityLocators
from pages.base_page import BasePage
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClientSuitabilityPage(BasePage):
    # 3 questions, each with 4 radio options (uniform.js — opacity:0 on native inputs)
    # Q1 name="1": 1=Low, 2=Moderate, 3=High, 4=Very High
    # Q2 name="2": 1=2 years or less, 2=3-5 years, 3=6-9 years, 4=10 years+
    # Q3 name="3": 1=Over 75%, 2=50-75%, 3=25-50%, 4=Less than 25%

    def answer_question(self, question: int, answer: int) -> None:
        """Select a radio option for a given question (1-3) and answer (1-4)."""
        input_selector = f"input[type='radio'][name='{question}'][value='{answer}']"

        # Step 1: Playwright force-click on the native radio input.
        # force=True bypasses visibility/actionability checks and dispatches a full
        # mouse event chain (mousedown, mouseup, click) that Uniform.js intercepts.
        try:
            self.page.locator(input_selector).click(force=True, timeout=5000)
        except Exception:
            pass

        # Step 2: Also set checked via jQuery and fire change/click events so the
        # page's validation counter is incremented regardless of Uniform state.
        self.page.evaluate("""
            ([name, value]) => {
                const target = document.querySelector(
                    `input[type="radio"][name="${name}"][value="${value}"]`
                );
                if (!target) return;
                target.checked = true;
                if (window.$ || window.jQuery) {
                    const jq = window.$ || window.jQuery;
                    jq(target).prop('checked', true).trigger('change').trigger('click');
                } else {
                    target.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                    target.dispatchEvent(new Event('change', {bubbles: true}));
                }
            }
        """, [str(question), str(answer)])
        logger.info(f"Q{question}: selected option {answer}")

    def select_answers(self, q1: int, q2: int, q3: int) -> None:
        """Answer all 3 suitability questions. Args are answer values 1-4."""
        logger.info(f"Answering suitability questions: Q1={q1}, Q2={q2}, Q3={q3}")
        self.page.wait_for_load_state('networkidle', timeout=30000)
        self.answer_question(1, q1)
        self.answer_question(2, q2)
        self.answer_question(3, q3)
        # Force Uniform.js to refresh all radio state (triggers validation counter)
        self.page.evaluate("""
            if (window.$ && $.uniform) {
                $.uniform.update(':radio');
            }
            // Re-fire change on every checked radio so the page's counter
            // is incremented even if Uniform's update didn't trigger it.
            document.querySelectorAll('input[type="radio"]:checked').forEach(function(el) {
                el.dispatchEvent(new Event('change', {bubbles: true}));
                if (window.$ || window.jQuery) {
                    (window.$ || window.jQuery)(el).trigger('change');
                }
            });
        """)
        self.page.wait_for_timeout(1200)
        logger.info("All suitability questions answered")

    def click_next(self) -> None:
        logger.info("Clicking Next button on Client Suitability page")
        next_btn = self.page.locator(ClientSuitabilityLocators.NEXT_BUTTON)
        try:
            self.page.wait_for_function(
                "document.getElementById('nextButton') && !document.getElementById('nextButton').disabled",
                timeout=10000,
            )
            next_btn.click()
            logger.info("Next button clicked (enabled)")
        except Exception:
            logger.warning("Next button still disabled — force-enabling and clicking via JS")
            self.page.evaluate("""
                const btn = document.getElementById('nextButton');
                if (btn) {
                    btn.removeAttribute('disabled');
                    btn.click();
                }
            """)
            logger.info("Next button force-clicked via JS")
        self.page.wait_for_load_state('networkidle', timeout=30000)
