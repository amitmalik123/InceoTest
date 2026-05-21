from playwright.sync_api import Page
from playwright.sync_api import expect


# Only forms that always appear regardless of TMS applicability
REQUIRED_FORMS = [
    'Investment Solution Change Request Form (Additional information required)',
    'Client Suitability Form',
]


class CreateFormsValidations:
    def __init__(self, page: Page):
        self.page = page

    def validate_required_forms_present(self) -> None:
        """Assert that each required form label is visible on the page."""
        for form_label in REQUIRED_FORMS:
            locator = self.page.get_by_text(form_label)
            expect(locator.first).to_be_visible()
