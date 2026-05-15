"""
DOM Inspector & Locator Generator for Playwright.

Navigates to any page in the authenticated app and produces a structured
inventory of every interactive element **with Playwright-recommended
locator suggestions** ranked by resilience.

Usage (standalone):
    $env:TEST_ENV="test11"
    pytest utils/dom_inspector.py -v -s -k "test_inspect" --page-url "/ISCT/ModifyInvestment"

Usage (from code / step definitions):
    from utils.dom_inspector import DOMInspector
    inspector = DOMInspector(page)
    report = inspector.inspect()          # current page
    inspector.save_report(report, "reports/dom_invest.json")

The JSON report for every element contains:
    {
        "tag": "BUTTON",
        "text": "Next",
        "locators": [                       # ordered best -> worst
            {"api": "get_by_role",   "code": "page.get_by_role('button', name='Next')", "rank": 1},
            {"api": "locator",       "code": "page.locator('#nextButton')",              "rank": 4},
        ],
        "attributes": {"id": "nextButton", "class": "EnabledPrimaryIsctButton", ...}
    }
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from typing import Any

from playwright.sync_api import Locator, Page

# ΓöÇΓöÇ Locator suggestion dataclass ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ


@dataclass
class LocatorSuggestion:
    api: str  # e.g. "get_by_role", "get_by_label", "locator"
    code: str  # e.g. "page.get_by_role('button', name='Next')"
    rank: int  # 1 = best, 5 = worst


@dataclass
class ElementInfo:
    tag: str
    text: str
    role: str | None = None
    locators: list[LocatorSuggestion] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    section: str = ""  # "button", "link", "input", "select", etc.


# ΓöÇΓöÇ Rank table  (lower = better, mirrors Playwright docs) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

_RANK = {
    "get_by_role": 1,
    "get_by_label": 1,
    "get_by_placeholder": 2,
    "get_by_text": 2,
    "get_by_alt_text": 2,
    "get_by_title": 2,
    "get_by_test_id": 3,
    "locator_css_id": 4,
    "locator_css_class": 5,
    "locator_xpath": 6,
}


def _escape(s: str) -> str:
    """Escape single quotes for Python code strings."""
    return s.replace("\\", "\\\\").replace("'", "\\'")


# ΓöÇΓöÇ Core inspector ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ


class DOMInspector:
    """
    Inspects the current page DOM and generates Playwright locator
    suggestions for every interactive element.
    """

    def __init__(self, page: Page):
        self.page = page

    # ΓöÇΓöÇ public API ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

    def inspect(self) -> dict[str, Any]:
        """
        Return a structured report with locator suggestions for every
        interactive element on the current page.
        """
        self.page.wait_for_load_state("domcontentloaded", timeout=30000)

        elements: list[dict] = []
        elements.extend(self._inspect_buttons())
        elements.extend(self._inspect_links())
        elements.extend(self._inspect_inputs())
        elements.extend(self._inspect_selects())
        elements.extend(self._inspect_radios_checkboxes())

        return {
            "url": self.page.url,
            "title": self.page.title(),
            "element_count": len(elements),
            "elements": elements,
        }

    def save_report(self, report: dict, path: str) -> str:
        """Save the report as pretty-printed JSON.  Returns the path."""
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, ensure_ascii=False, default=str)
        return path

    def print_summary(self, report: dict) -> str:
        """Return a human-readable summary string."""
        lines = [
            f"URL:   {report['url']}",
            f"Title: {report['title']}",
            f"Interactive elements found: {report['element_count']}",
            "",
        ]
        for el in report["elements"]:
            best = el["locators"][0] if el["locators"] else None
            lines.append(
                f"  [{el['section']:>8}] {el['tag']:<8} "
                f"text={el['text'][:50]:<50} "
                f"BEST -> {best['code'] if best else 'N/A'}"
            )
        return "\n".join(lines)

    # ΓöÇΓöÇ private: element inspectors ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

    def _inspect_buttons(self) -> list[dict]:
        results = []
        for loc in self.page.locator("button, input[type='button'], input[type='submit']").all():
            try:
                info = self._build_element_info(loc, "button")
                if info:
                    results.append(asdict(info))
            except Exception:
                pass  # nosec B110
        return results

    def _inspect_links(self) -> list[dict]:
        results = []
        for loc in self.page.locator("a[href]").all():
            try:
                info = self._build_element_info(loc, "link")
                if info:
                    results.append(asdict(info))
            except Exception:
                pass  # nosec B110
        return results

    def _inspect_inputs(self) -> list[dict]:
        results = []
        for loc in self.page.locator(
            "input[type='text'], input[type='email'], input[type='password'], "
            "input[type='search'], input[type='number'], input[type='tel'], "
            "input[type='url'], textarea"
        ).all():
            try:
                info = self._build_element_info(loc, "input")
                if info:
                    results.append(asdict(info))
            except Exception:
                pass  # nosec B110
        return results

    def _inspect_selects(self) -> list[dict]:
        results = []
        for loc in self.page.locator("select").all():
            try:
                info = self._build_element_info(loc, "select")
                if info:
                    results.append(asdict(info))
            except Exception:
                pass  # nosec B110
        return results

    def _inspect_radios_checkboxes(self) -> list[dict]:
        results = []
        for loc in self.page.locator("input[type='radio'], input[type='checkbox']").all():
            try:
                info = self._build_element_info(loc, "radio/checkbox")
                if info:
                    results.append(asdict(info))
            except Exception:
                pass  # nosec B110
        return results

    # ΓöÇΓöÇ private: locator generation per element ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ

    def _build_element_info(self, loc: Locator, section: str) -> ElementInfo | None:
        """Build an ElementInfo with ranked locator suggestions."""
        attrs = loc.evaluate(
            """el => {
            const out = {};
            for (const a of el.attributes) out[a.name] = a.value;
            out['_tag'] = el.tagName;
            out['_text'] = (el.textContent || el.value || '').trim().substring(0, 120);
            out['_type'] = el.type || '';
            // Computed accessible name via browser
            try { out['_accName'] = el.ariaLabel || ''; } catch(e){}
            // Associated label
            try {
                const lbl = el.labels && el.labels[0];
                out['_label'] = lbl ? lbl.textContent.trim().substring(0,120) : '';
            } catch(e) { out['_label'] = ''; }
            return out;
        }"""
        )

        tag = attrs.pop("_tag", "")
        text = attrs.pop("_text", "")
        el_type = attrs.pop("_type", "")
        acc_name = attrs.pop("_accName", "")
        label_text = attrs.pop("_label", "")

        suggestions: list[LocatorSuggestion] = []

        # ΓöÇΓöÇ 1. get_by_role  (rank 1) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        role = self._tag_to_role(tag, el_type, attrs)
        if role:
            name_param = acc_name or text or attrs.get("value", "")
            if name_param and len(name_param) > 1:
                safe = _escape(name_param[:80])
                suggestions.append(
                    LocatorSuggestion(
                        api="get_by_role",
                        code=f"page.get_by_role('{role}', name='{safe}')",
                        rank=_RANK["get_by_role"],
                    )
                )

        # ΓöÇΓöÇ 2. get_by_label  (rank 1) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        if label_text and section in ("input", "select", "radio/checkbox"):
            safe = _escape(label_text[:80])
            suggestions.append(
                LocatorSuggestion(
                    api="get_by_label",
                    code=f"page.get_by_label('{safe}')",
                    rank=_RANK["get_by_label"],
                )
            )

        # ΓöÇΓöÇ 3. get_by_placeholder  (rank 2) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        placeholder = attrs.get("placeholder", "")
        if placeholder:
            safe = _escape(placeholder[:80])
            suggestions.append(
                LocatorSuggestion(
                    api="get_by_placeholder",
                    code=f"page.get_by_placeholder('{safe}')",
                    rank=_RANK["get_by_placeholder"],
                )
            )

        # ΓöÇΓöÇ 4. get_by_text  (rank 2) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        if text and len(text) > 1 and section in ("link", "button"):
            safe = _escape(text[:80])
            suggestions.append(
                LocatorSuggestion(
                    api="get_by_text",
                    code=f"page.get_by_text('{safe}', exact=True)",
                    rank=_RANK["get_by_text"],
                )
            )

        # ΓöÇΓöÇ 5. get_by_test_id  (rank 3) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        test_id = attrs.get("data-testid", "") or attrs.get("data-test-id", "")
        if test_id:
            safe = _escape(test_id)
            suggestions.append(
                LocatorSuggestion(
                    api="get_by_test_id",
                    code=f"page.get_by_test_id('{safe}')",
                    rank=_RANK["get_by_test_id"],
                )
            )

        # ΓöÇΓöÇ 6. CSS ID selector  (rank 4) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        el_id = attrs.get("id", "")
        if el_id:
            suggestions.append(
                LocatorSuggestion(
                    api="locator_css_id",
                    code=f"page.locator('#{el_id}')",
                    rank=_RANK["locator_css_id"],
                )
            )

        # ΓöÇΓöÇ 7. aria-label selector  (rank 2 - like get_by_label) ΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇΓöÇ
        aria_label = attrs.get("aria-label", "")
        if aria_label and not label_text:
            safe = _escape(aria_label[:80])
            suggestions.append(
                LocatorSuggestion(
                    api="get_by_label",
                    code=f"page.get_by_label('{safe}')",
                    rank=_RANK["get_by_label"],
                )
            )

        # Sort by rank (best first)
        suggestions.sort(key=lambda s: s.rank)

        if not suggestions:
            return None

        # Clean attributes for output (remove internal _-prefixed)
        clean_attrs = {k: v for k, v in attrs.items() if not k.startswith("_") and v}

        return ElementInfo(
            tag=tag,
            text=text[:120],
            role=role,
            locators=suggestions,
            attributes=clean_attrs,
            section=section,
        )

    @staticmethod
    def _tag_to_role(tag: str, el_type: str, attrs: dict) -> str | None:
        """Map HTML tag + type to ARIA role."""
        tag_upper = tag.upper()
        role_attr = attrs.get("role", "")
        if role_attr:
            return role_attr

        mapping = {
            "BUTTON": "button",
            "A": "link",
            "TEXTAREA": "textbox",
            "SELECT": "combobox",
        }
        if tag_upper in mapping:
            return mapping[tag_upper]

        if tag_upper == "INPUT":
            type_map = {
                "button": "button",
                "submit": "button",
                "reset": "button",
                "checkbox": "checkbox",
                "radio": "radio",
                "text": "textbox",
                "email": "textbox",
                "password": "textbox",
                "search": "searchbox",
                "number": "spinbutton",
                "tel": "textbox",
                "url": "textbox",
            }
            return type_map.get(el_type)

        return None
