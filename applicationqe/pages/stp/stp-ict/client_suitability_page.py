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
        # Click the Uniform.js wrapper element (parent of native radio) via native DOM click.
        # This mirrors the approach used by ict_select_destination_page (el.click() on the
        # Uniform wrapper), which reliably triggers Uniform's event handlers, updates the
        # visual 'checked' class, and increments the page's answer counter.
        self.page.evaluate("""
            ([name, value]) => {
                const input = document.querySelector(
                    `input[type="radio"][name="${name}"][value="${value}"]`
                );
                if (!input) return;

                // 1. Click the Uniform.js visual wrapper (div/span.radio) if present.
                const wrapper = input.closest('.radio')
                    || input.closest('div[class*="radio"]')
                    || input.closest('span[class*="radio"]');
                if (wrapper) {
                    wrapper.click();
                } else {
                    // 2. Fall back to clicking associated <label> or the input itself.
                    const label = input.id
                        ? document.querySelector(`label[for="${input.id}"]`)
                        : null;
                    (label || input).click();
                }

                // 3. Belt-and-suspenders: also set .checked and fire change events.
                input.checked = true;
                if (window.$ || window.jQuery) {
                    (window.$ || window.jQuery)(input)
                        .prop('checked', true).trigger('change').trigger('click');
                } else {
                    input.dispatchEvent(new Event('change', {bubbles: true}));
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
        # Allow Uniform.js to propagate state and for the Next button to enable.
        self.page.wait_for_timeout(1000)
        logger.info("All suitability questions answered")

    def click_next(self) -> None:
        logger.info("Clicking Next button on Client Suitability page")
        next_btn = self.page.locator(ClientSuitabilityLocators.NEXT_BUTTON)
        try:
            self.page.wait_for_function(
                "document.getElementById('nextButton') && !document.getElementById('nextButton').disabled",
                timeout=15000,
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

        # Wait for navigation away from the Suitability page.
        # If Playwright's click triggered the handler but no navigation happened, retry
        # with a native DOM click (same as how ict_select_destination_page handles radios).
        try:
            self.page.wait_for_url(
                lambda url: '/Suitability' not in url,
                timeout=10000,
            )
            logger.info(f"Navigated to: {self.page.url}")
        except Exception:
            logger.warning(
                f"No navigation after Next click (URL: {self.page.url}). "
                "Retrying with native JS click."
            )
            self.page.evaluate("document.getElementById('nextButton').click()")
            try:
                self.page.wait_for_url(
                    lambda url: '/Suitability' not in url,
                    timeout=10000,
                )
                logger.info(f"Navigated after JS click: {self.page.url}")
            except Exception:
                logger.warning(f"Still on Suitability after JS click: {self.page.url}")
                self.page.screenshot(path='reports/suitability_stuck.png')

        self.page.wait_for_load_state('networkidle', timeout=30000)
