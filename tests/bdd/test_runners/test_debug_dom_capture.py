"""
Debug script: Captures the DOM snapshot of the account holding page.

Run with:
    $env:TEST_ENV="test11"; pytest tests/bdd/test_runners/test_debug_dom_capture.py -v --headed

This will:
1. Login
2. Navigate to clients → account list
3. Search and select the account
4. Capture the full page HTML to reports/dom_snapshot_holding_page.html
5. Also capture a screenshot to reports/dom_screenshot_holding_page.png
"""

from playwright.sync_api import Page


def test_capture_holding_page_dom(  # noqa: C901
    authenticated_page: Page, clients_page, account_list_page, test_context
):
    """Navigate to the holding page and capture the DOM."""
    import os

    reports_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)

    # Step 1: Verify login
    current_url = authenticated_page.url
    print(f"\n[DEBUG] Current URL after auth: {current_url}")
    assert "login" not in current_url.lower(), "Not logged in!"

    # Step 2: Navigate to Clients → Account List
    clients_page.navigate()
    clients_page.click_clients()
    clients_page.click_account_list()
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    print(f"[DEBUG] On Account List page: {authenticated_page.url}")

    # Step 3: Search for client
    client_id = test_context["test_data"]["client_id"]
    account_name = test_context["test_data"]["account_name"]
    account_list_page.search_client(client_id)
    print(f"[DEBUG] Searched for client: {client_id}")

    # Step 4: Select the account → navigate to holding page
    account_list_page.select_account(account_name, client_id)
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    # Wait a bit more for dynamic content to load
    authenticated_page.wait_for_timeout(3000)
    print(f"[DEBUG] On holding page: {authenticated_page.url}")

    # Step 5: Capture screenshot
    screenshot_path = os.path.join(reports_dir, "dom_screenshot_holding_page.png")
    authenticated_page.screenshot(path=screenshot_path, full_page=True)
    print(f"[DEBUG] Screenshot saved: {screenshot_path}")

    # Step 6: Capture full DOM HTML
    html_content = authenticated_page.content()
    html_path = os.path.join(reports_dir, "dom_snapshot_holding_page.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[DEBUG] DOM snapshot saved: {html_path}")
    print(f"[DEBUG] DOM size: {len(html_content)} characters")

    # Step 7: Also capture just the key interactive elements for quick analysis
    summary_path = os.path.join(reports_dir, "dom_elements_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"URL: {authenticated_page.url}\n")
        f.write(f"Title: {authenticated_page.title()}\n")
        f.write(f"DOM Size: {len(html_content)} chars\n\n")

        # Capture all clickable elements
        f.write("=== BUTTONS ===\n")
        buttons = authenticated_page.locator(
            "button, input[type='button'], input[type='submit']"
        ).all()
        for i, btn in enumerate(buttons):
            try:
                tag = btn.evaluate("el => el.tagName")
                text = btn.text_content() or ""
                attrs = btn.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, name: el.name, type: el.type, role: el.getAttribute('role'), 'data-testid': el.getAttribute('data-testid'), 'aria-label': el.getAttribute('aria-label')})"
                )
                f.write(f"  [{i}] <{tag}> text='{text.strip()[:80]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== LINKS ===\n")
        links = authenticated_page.locator("a").all()
        for i, link in enumerate(links):
            try:
                text = link.text_content() or ""
                href = link.get_attribute("href") or ""
                attrs = link.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, role: el.getAttribute('role'), 'data-testid': el.getAttribute('data-testid')})"
                )
                f.write(f"  [{i}] text='{text.strip()[:80]}' href='{href[:100]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== DROPDOWNS / SELECT / MENUS ===\n")
        dropdowns = authenticated_page.locator(
            "select, [role='menu'], [role='menubar'], [role='listbox'], [role='combobox'], [class*='dropdown'], [class*='menu'], [id*='dropdown'], [id*='menu']"
        ).all()
        for i, dd in enumerate(dropdowns):
            try:
                tag = dd.evaluate("el => el.tagName")
                text = dd.text_content() or ""
                outer = dd.evaluate("el => el.outerHTML.substring(0, 300)")
                f.write(f"  [{i}] <{tag}> text='{text.strip()[:80]}'\n    HTML: {outer}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== TABS ===\n")
        tabs = authenticated_page.locator(
            "[role='tab'], .tab, [class*='tab'], .nav-link, .nav-item"
        ).all()
        for i, tab in enumerate(tabs):
            try:
                text = tab.text_content() or ""
                attrs = tab.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, role: el.getAttribute('role'), 'aria-selected': el.getAttribute('aria-selected')})"
                )
                f.write(f"  [{i}] text='{text.strip()[:80]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        # Look specifically for anything with "Client Management", "Change", "Investment"
        f.write("\n=== ELEMENTS CONTAINING 'client management' / 'change' / 'investment' ===\n")
        for keyword in [
            "Client Management",
            "Change Investments",
            "Change",
            "Investment",
            "Holding",
        ]:
            elements = authenticated_page.locator(f"text='{keyword}'").all()
            f.write(f"\n  Keyword: '{keyword}' → {len(elements)} match(es)\n")
            for i, el in enumerate(elements):
                try:
                    tag = el.evaluate("el => el.tagName")
                    outer = el.evaluate("el => el.outerHTML.substring(0, 500)")
                    parent = el.evaluate(
                        "el => el.parentElement ? el.parentElement.outerHTML.substring(0, 500) : 'no parent'"
                    )
                    f.write(f"    [{i}] <{tag}> HTML: {outer}\n")
                    f.write(f"         Parent: {parent}\n")
                except Exception:
                    pass  # nosec B110

    print(f"[DEBUG] Elements summary saved: {summary_path}")

    # Step 8: Click Account Wizard to capture the next page
    print("\n[DEBUG] === NOW CLICKING ACCOUNT WIZARD ===")
    account_wizard_link = authenticated_page.locator("#clientDetailAccountDetailAnchor")
    account_wizard_link.click()
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=30000)
    authenticated_page.wait_for_timeout(3000)
    print(f"[DEBUG] Account Wizard page URL: {authenticated_page.url}")

    # Capture Account Wizard page screenshot
    aw_screenshot = os.path.join(reports_dir, "dom_screenshot_account_wizard.png")
    authenticated_page.screenshot(path=aw_screenshot, full_page=True)
    print(f"[DEBUG] Account Wizard screenshot saved: {aw_screenshot}")

    # Capture Account Wizard DOM
    aw_html = authenticated_page.content()
    aw_html_path = os.path.join(reports_dir, "dom_snapshot_account_wizard.html")
    with open(aw_html_path, "w", encoding="utf-8") as f:
        f.write(aw_html)
    print(f"[DEBUG] Account Wizard DOM saved: {aw_html_path} ({len(aw_html)} chars)")

    # Capture Account Wizard elements summary
    aw_summary_path = os.path.join(reports_dir, "dom_elements_account_wizard.txt")
    with open(aw_summary_path, "w", encoding="utf-8") as f:
        f.write(f"URL: {authenticated_page.url}\n")
        f.write(f"Title: {authenticated_page.title()}\n\n")

        # All text on the page (for finding "Client Management", "Change Investments")
        f.write("=== ALL VISIBLE TEXT (first 5000 chars) ===\n")
        body_text = authenticated_page.locator("body").text_content() or ""
        f.write(body_text[:5000] + "\n")

        f.write("\n=== BUTTONS ===\n")
        buttons = authenticated_page.locator(
            "button, input[type='button'], input[type='submit']"
        ).all()
        for i, btn in enumerate(buttons):
            try:
                tag = btn.evaluate("el => el.tagName")
                text = btn.text_content() or ""
                attrs = btn.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, name: el.name, type: el.type, 'aria-label': el.getAttribute('aria-label'), onclick: (el.getAttribute('onclick')||'').substring(0,100)})"
                )
                f.write(f"  [{i}] <{tag}> text='{text.strip()[:80]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== LINKS ===\n")
        links = authenticated_page.locator("a").all()
        for i, link in enumerate(links):
            try:
                text = link.text_content() or ""
                href = link.get_attribute("href") or ""
                attrs = link.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, onclick: (el.getAttribute('onclick')||'').substring(0,150)})"
                )
                f.write(f"  [{i}] text='{text.strip()[:100]}' href='{href[:150]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== RADIO BUTTONS / CHECKBOXES ===\n")
        radios = authenticated_page.locator("input[type='radio'], input[type='checkbox']").all()
        for i, r in enumerate(radios):
            try:
                attrs = r.evaluate(
                    "el => JSON.stringify({id: el.id, name: el.name, value: el.value, type: el.type, checked: el.checked, 'data-label': el.getAttribute('data-label')})"
                )
                label = ""
                with contextlib.suppress(Exception):
                    label = r.evaluate(
                        "el => { const lbl = el.closest('label') || document.querySelector('label[for=\"'+el.id+'\"]"); return lbl ? lbl.textContent.trim() : ''; }"
                    )
                f.write(f"  [{i}] {attrs} label='{label[:80]}'\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== LIST ITEMS (li) ===\n")
        lis = authenticated_page.locator("li").all()
        for i, li in enumerate(lis):
            try:
                text = li.text_content() or ""
                attrs = li.evaluate("el => JSON.stringify({id: el.id, class: el.className})")
                if text.strip():
                    f.write(f"  [{i}] text='{text.strip()[:100]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        # Search specifically for "Change", "Investment", "Client Management"
        f.write("\n=== KEYWORD SEARCH ===\n")
        for keyword in [
            "Client Management",
            "Change Investments",
            "Change",
            "Investment",
            "Rebalance",
            "Trade",
            "Transfer",
        ]:
            elements = authenticated_page.locator(f"text='{keyword}'").all()
            f.write(f"\n  '{keyword}' → {len(elements)} match(es)\n")
            for i, el in enumerate(elements[:5]):
                try:
                    outer = el.evaluate("el => el.outerHTML.substring(0, 500)")
                    parent = el.evaluate(
                        "el => el.parentElement ? el.parentElement.outerHTML.substring(0, 300) : 'none'"
                    )
                    f.write(f"    [{i}] HTML: {outer}\n")
                    f.write(f"         Parent: {parent}\n")
                except Exception:
                    pass  # nosec B110

    print(f"[DEBUG] Account Wizard elements saved: {aw_summary_path}")

    # Step 9: Click "Change Investments" and capture the resulting page
    print("\n[DEBUG] === NOW CLICKING CHANGE INVESTMENTS ===")
    change_inv_link = authenticated_page.locator("#ctl00_cphContentArea_lnkChangeInvestments")
    change_inv_link.wait_for(state="visible", timeout=15000)
    change_inv_link.click()
    authenticated_page.wait_for_load_state("domcontentloaded", timeout=60000)
    authenticated_page.wait_for_timeout(5000)
    print(f"[DEBUG] Change Investments page URL: {authenticated_page.url}")

    # Capture Change Investments page screenshot
    ci_screenshot = os.path.join(reports_dir, "dom_screenshot_change_investments.png")
    authenticated_page.screenshot(path=ci_screenshot, full_page=True)
    print(f"[DEBUG] Change Investments screenshot saved: {ci_screenshot}")

    # Capture Change Investments DOM
    ci_html = authenticated_page.content()
    ci_html_path = os.path.join(reports_dir, "dom_snapshot_change_investments.html")
    with open(ci_html_path, "w", encoding="utf-8") as f:
        f.write(ci_html)
    print(f"[DEBUG] Change Investments DOM saved: {ci_html_path} ({len(ci_html)} chars)")

    # Capture Change Investments elements summary
    ci_summary_path = os.path.join(reports_dir, "dom_elements_change_investments.txt")
    with open(ci_summary_path, "w", encoding="utf-8") as f:
        f.write(f"URL: {authenticated_page.url}\n")
        f.write(f"Title: {authenticated_page.title()}\n\n")

        f.write("=== ALL VISIBLE TEXT (first 8000 chars) ===\n")
        body_text = authenticated_page.locator("body").text_content() or ""
        f.write(body_text[:8000] + "\n")

        f.write("\n=== BUTTONS ===\n")
        buttons = authenticated_page.locator(
            "button, input[type='button'], input[type='submit']"
        ).all()
        for i, btn in enumerate(buttons):
            try:
                tag = btn.evaluate("el => el.tagName")
                text = btn.text_content() or ""
                attrs = btn.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, name: el.name, type: el.type, 'aria-label': el.getAttribute('aria-label'), onclick: (el.getAttribute('onclick')||'').substring(0,150)})"
                )
                f.write(f"  [{i}] <{tag}> text='{text.strip()[:80]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== LINKS ===\n")
        links = authenticated_page.locator("a").all()
        for i, link in enumerate(links):
            try:
                text = link.text_content() or ""
                href = link.get_attribute("href") or ""
                attrs = link.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, onclick: (el.getAttribute('onclick')||'').substring(0,150)})"
                )
                f.write(f"  [{i}] text='{text.strip()[:100]}' href='{href[:150]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== TABLES ===\n")
        tables = authenticated_page.locator("table").all()
        for i, tbl in enumerate(tables):
            try:
                attrs = tbl.evaluate("el => JSON.stringify({id: el.id, class: el.className})")
                rows = tbl.locator("tr").count()
                header_text = ""
                with contextlib.suppress(Exception):
                    header_text = tbl.locator("thead, tr:first-child").first.text_content() or ""
                f.write(f"  [{i}] {attrs} rows={rows} header='{header_text.strip()[:200]}'\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== TABS / NAV ELEMENTS ===\n")
        tabs = authenticated_page.locator(
            "[role='tab'], .tab, .nav-link, .nav-item, [class*='tab']"
        ).all()
        for i, tab in enumerate(tabs):
            try:
                text = tab.text_content() or ""
                attrs = tab.evaluate(
                    "el => JSON.stringify({id: el.id, class: el.className, role: el.getAttribute('role'), 'aria-selected': el.getAttribute('aria-selected')})"
                )
                if text.strip():
                    f.write(f"  [{i}] text='{text.strip()[:100]}' {attrs}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== RADIO BUTTONS / CHECKBOXES ===\n")
        radios = authenticated_page.locator("input[type='radio'], input[type='checkbox']").all()
        for i, r in enumerate(radios):
            try:
                attrs = r.evaluate(
                    "el => JSON.stringify({id: el.id, name: el.name, value: el.value, type: el.type, checked: el.checked})"
                )
                label = ""
                with contextlib.suppress(Exception):
                    label = r.evaluate(
                        "el => { const lbl = el.closest('label') || document.querySelector('label[for=\"'+el.id+'\"]'); return lbl ? lbl.textContent.trim().substring(0,150) : ''; }"
                    )
                f.write(f"  [{i}] {attrs} label='{label}'\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== SELECT DROPDOWNS ===\n")
        selects = authenticated_page.locator("select").all()
        for i, sel in enumerate(selects):
            try:
                attrs = sel.evaluate(
                    "el => JSON.stringify({id: el.id, name: el.name, class: el.className})"
                )
                options = sel.locator("option").all()
                option_texts = [opt.text_content().strip()[:80] for opt in options[:10]]
                f.write(f"  [{i}] {attrs} options={option_texts}\n")
            except Exception:
                pass  # nosec B110

        f.write("\n=== IFRAMES ===\n")
        iframes = authenticated_page.locator("iframe").all()
        for i, iframe in enumerate(iframes):
            try:
                attrs = iframe.evaluate(
                    "el => JSON.stringify({id: el.id, name: el.name || '', src: (el.src||'').substring(0,200), class: el.className})"
                )
                f.write(f"  [{i}] {attrs}\n")
            except Exception:
                pass  # nosec B110

        # Search for key elements related to Change Investments
        f.write("\n=== KEYWORD SEARCH ===\n")
        for keyword in [
            "Account Number",
            "Investment Selection",
            "Destination",
            "Select New",
            "account",
            "investment",
            "modal",
            "strategy",
            "allocation",
            "fund",
            "model",
        ]:
            elements = authenticated_page.locator(f"text='{keyword}'").all()
            f.write(f"\n  '{keyword}' → {len(elements)} match(es)\n")
            for j, el in enumerate(elements[:5]):
                try:
                    outer = el.evaluate("el => el.outerHTML.substring(0, 500)")
                    parent = el.evaluate(
                        "el => el.parentElement ? el.parentElement.outerHTML.substring(0, 300) : 'none'"
                    )
                    f.write(f"    [{j}] HTML: {outer}\n")
                    f.write(f"         Parent: {parent}\n")
                except Exception:
                    pass  # nosec B110

    print(f"[DEBUG] Change Investments elements saved: {ci_summary_path}")
    print("\n[DEBUG] DOM capture complete! Check reports/ folder.")
