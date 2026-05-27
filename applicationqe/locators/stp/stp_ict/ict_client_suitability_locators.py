class ClientSuitabilityLocators:
    # Template: input[name="{question}"][value="{answer}"]
    # question: 1, 2, or 3 | answer: 1, 2, 3, or 4
    RADIO_TEMPLATE = "input[name='{question}'][value='{answer}']"

    NEXT_BUTTON = "input#nextButton"
