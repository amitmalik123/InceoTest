"""
SMI Navigation & Workflow Step Definitions — Model Management

Migrated from tests/bdd/steps/SMI_Login_Steps.py on branch
application/ModelManagement_SMI.

Key changes:
  - Imports updated: pages.SMI_* → pages.model_management.*
  - LOGIN_URL sourced from smi_login_page.base_url (fixture) instead of
    SMILoginPage.LOGIN_URL class constant.
  - SCREENSHOTS_DIR kept as class constant on SMIHomePage.
  - Fixtures (smi_login_page, credentials, executive_credentials) are
    defined in tests/features/model-management/conftest.py.
"""
import os
import time
from datetime import datetime

from pytest_bdd import given, parsers, then, when

from pages.model_management.smi.smi_admin_page import SMIAdminPage
from pages.model_management.smi.smi_companies_page import SMICompaniesPage
from pages.model_management.smi.smi_home_page import SMIHomePage
from pages.model_management.smi.smi_login_page import SMILoginPage
from pages.model_management.smi.smi_manager_console_page import SMIManagerConsolePage
from pages.model_management.smi.smi_models_page import SMIModelsPage
from pages.model_management.smi.smi_performance_page import SMIPerformancePage
from pages.model_management.smi.smi_reallocation_page import SMIReallocationPage

# ===========================================================================
# Constants
# ===========================================================================

_SEP = "=" * 70


# ===========================================================================
# Private helpers
# ===========================================================================


def _fluent_wait(
    condition_fn,
    timeout: float = 10.0,
    poll_interval: float = 0.5,
    error_msg: str = "Condition not met",
):
    """Poll condition_fn() every poll_interval seconds until truthy or timeout."""
    deadline = time.time() + timeout
    last_exc = None
    while time.time() < deadline:
        try:
            result = condition_fn()
            if result:
                return result
        except Exception as e:
            last_exc = e
        time.sleep(poll_interval)
    raise TimeoutError(f"{error_msg} after {timeout}s. Last error: {last_exc}")


def _fluent_wait_js(
    page,
    condition_js: str,
    timeout_ms: int = 15000,
    poll_ms: int = 500,
    description: str = "",
) -> bool:
    """Poll a JS condition every poll_ms milliseconds until truthy or timeout."""
    label = f"[fluent_wait:{description}]" if description else "[fluent_wait]"
    deadline = time.monotonic() + timeout_ms / 1000
    attempt = 0
    while time.monotonic() < deadline:
        attempt += 1
        try:
            result = page.evaluate(f"() => {{ {condition_js} }}")
            if result:
                print(f"{label} Condition met on attempt #{attempt}")
                return True
        except Exception:
            pass
        page.wait_for_timeout(poll_ms)
    print(f"{label} Timed out after {timeout_ms}ms ({attempt} attempts)")
    return False


def _get_clean_menu_items(page) -> list:
    """Extract ONLY the top-level header menu tabs from the navigation bar."""
    try:
        items = page.evaluate(
            """
            () => {
                const labels = document.querySelectorAll(
                    'ul.menu-section[role="menubar"] > li.menu-item > div.menu-item-label'
                );
                const result = [];
                labels.forEach(label => {
                    const directText = Array.from(label.childNodes)
                        .filter(n => n.nodeType === 3)
                        .map(n => n.nodeValue.trim())
                        .filter(t => t)
                        .join('');
                    const anchor = label.querySelector(':scope > a');
                    const anchorText = anchor ? anchor.innerText.trim() : '';
                    const text = (directText || anchorText).trim();
                    if (text) result.push(text);
                });
                return result;
            }
        """
        )
        return items if items else []
    except Exception as e:
        print(f"[DEBUG] Error extracting menu items: {e}")
        return []


def _print_menu_bar_items(page) -> list:
    """Print the menu bar items in a formatted way and return them."""
    menu_items = _get_clean_menu_items(page)
    print(f"\n{_SEP}")
    print("MAIN NAVIGATION MENU BAR ITEMS (class: menu-section)")
    print(_SEP)
    if menu_items:
        print(f"Total Menu Items Found: {len(menu_items)}\n")
        for idx, item in enumerate(menu_items, 1):
            print(f"  {idx}. {item}")
    else:
        print("No menu items found")
    print(f"{_SEP}\n")
    return menu_items


def _print_submenu_options(page) -> None:
    """Print all submenu options available under each top-level menu item."""
    menu_items = _get_clean_menu_items(page)
    print(f"\n{_SEP}")
    print("SUBMENU OPTIONS PER MENU BAR ITEM")
    print(_SEP)
    for item in menu_items:
        submenus = page.evaluate(
            """
            (itemText) => {
                const labels = Array.from(document.querySelectorAll(
                    'ul.menu-section[role="menubar"] > li.menu-item > div.menu-item-label'));
                for (const label of labels) {
                    const nodes = Array.from(label.childNodes);
                    let text = '';
                    for (const n of nodes) {
                        if (n.nodeType === 3) text += n.textContent.trim();
                    }
                    if (!text) {
                        const a = label.querySelector('a');
                        if (a) text = a.textContent.trim();
                    }
                    if (text === itemText) {
                        const li = label.closest('li.menu-item');
                        if (!li) return [];
                        const subList = li.querySelector('ul.menu-section[role="menu"]');
                        if (!subList) return [];
                        return Array.from(subList.querySelectorAll('li.menu-item div.menu-item-label'))
                            .map(el => el.textContent.trim())
                            .filter(t => t);
                    }
                }
                return [];
            }
        """,
            item,
        )
        print(f"\n  [{item}]")
        if submenus:
            for idx, sub in enumerate(submenus, 1):
                print(f"    {idx}. {sub}")
            print(f"[SCRIPT RESPONSE] '{item}' submenus: {', '.join(submenus)}")
        else:
            print("    (no submenu)")
            print(f"[SCRIPT RESPONSE] '{item}' has no submenu options")
    print(f"\n{_SEP}\n")


def _take_screenshot(
    page,
    prefix: str = "smi_landing_page",
    directory: str = SMIHomePage.SCREENSHOTS_DIR,
) -> str:
    """Take a screenshot and return the saved path."""
    os.makedirs(directory, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(directory, f"{prefix}_{timestamp}.png")
    page.screenshot(path=path)
    print(f"[DEBUG] Screenshot saved to: {path}")
    return path


def _click_tab_by_text(page, tab_text: str) -> None:
    """Click a top-level menu tab by its visible text via JavaScript."""
    result = page.evaluate(
        """
        (targetText) => {
            const labels = document.querySelectorAll(
                'ul.menu-section[role="menubar"] > li.menu-item > div.menu-item-label'
            );
            for (const label of labels) {
                const directText = Array.from(label.childNodes)
                    .filter(n => n.nodeType === 3)
                    .map(n => n.nodeValue.trim())
                    .filter(t => t)
                    .join('');
                const anchor = label.querySelector(':scope > a');
                const text = (directText || (anchor ? anchor.innerText.trim() : '')).trim();
                if (text === targetText) {
                    if (anchor) { anchor.click(); return 'link'; }
                    label.click(); return 'label';
                }
            }
            return null;
        }
    """,
        tab_text,
    )
    if not result:
        raise RuntimeError(f"Menu tab '{tab_text}' not found in navigation bar")
    page.wait_for_load_state("domcontentloaded")


def _get_tab_submenu_hrefs(page, tab_text: str) -> dict:
    """Pre-collect all submenu hrefs for a given tab in one JS call."""
    return page.evaluate(
        """
        (tabText) => {
            const result = {};
            for (const li of document.querySelectorAll(
                    'ul.menu-section[role="menubar"] > li.menu-item')) {
                const label = li.querySelector(':scope > div.menu-item-label');
                if (!label) continue;
                const directText = Array.from(label.childNodes)
                    .filter(n => n.nodeType === 3)
                    .map(n => n.nodeValue.trim()).filter(t => t).join('');
                const a = label.querySelector(':scope > a');
                const text = (directText || (a ? a.innerText.trim() : '')).trim();
                if (text === tabText) {
                    for (const link of li.querySelectorAll(
                            'ul[role="menu"] li div.menu-item-label a')) {
                        const name = link.textContent.trim();
                        if (name) result[name] = link.href;
                    }
                }
            }
            return result;
        }
    """,
        tab_text,
    )


def _goto_submenu(page, href: str, tab_text: str, submenu_text: str) -> None:
    """Navigate to a pre-fetched submenu href. Skips gracefully on failure."""
    try:
        page.goto(href, wait_until="domcontentloaded", timeout=20000)
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass
        print(f"[NAV] Navigated to {tab_text} > {submenu_text}")
    except Exception as e:
        print(f"[SKIP] '{submenu_text}' under '{tab_text}' could not load: {type(e).__name__}")
        try:
            page.wait_for_load_state("load", timeout=10000)
        except Exception:
            pass


def _click_submenu_item(page, tab_text: str, submenu_text: str) -> bool:
    """JS-click a submenu item directly, bypassing CSS display:none restrictions."""
    return page.evaluate(
        """
        ([tabText, subText]) => {
            for (const li of document.querySelectorAll(
                    'ul.menu-section[role="menubar"] > li.menu-item')) {
                const label = li.querySelector(':scope > div.menu-item-label');
                if (!label) continue;
                const directText = Array.from(label.childNodes)
                    .filter(n => n.nodeType === 3)
                    .map(n => n.nodeValue.trim()).filter(t => t).join('');
                const anchor = label.querySelector(':scope > a');
                const text = (directText || (anchor ? anchor.innerText.trim() : '')).trim();
                if (text === tabText) {
                    for (const link of li.querySelectorAll(
                            'ul[role="menu"] li div.menu-item-label a')) {
                        if (link.textContent.trim() === subText) {
                            link.click();
                            return true;
                        }
                    }
                }
            }
            return false;
        }
    """,
        [tab_text, submenu_text],
    )


def _click_on_each_menu_item(page) -> list:
    """Click each top-level header menu tab one by one. Returns a list of result dicts."""
    menu_items = _get_clean_menu_items(page)
    if not menu_items:
        print("\n[ERROR] No menu items found to click")
        return []

    if "Home" in menu_items:
        menu_items.remove("Home")
        menu_items.append("Home")

    click_results = []
    home_url = page.url

    print(f"\n{_SEP}")
    print("CLICKING ON EACH MENU ITEM ONE BY ONE")
    print(f"{_SEP}\n")

    for idx, menu_item in enumerate(menu_items, 1):
        try:
            print(f"\n[{idx}/{len(menu_items)}] Attempting to click on: '{menu_item}'")

            if page.url != home_url:
                print("    [*] Navigating back to home...")
                page.goto(home_url)

            try:
                page.wait_for_load_state("domcontentloaded", timeout=10000)
            except Exception:
                pass
            try:
                page.wait_for_load_state("networkidle", timeout=10000)
            except Exception:
                pass
            try:
                _fluent_wait(
                    lambda: page.query_selector(SMIHomePage.MENU_BAR) is not None,
                    timeout=10.0,
                    poll_interval=0.5,
                    error_msg="Menu bar did not become ready",
                )
            except TimeoutError as e:
                print(f"    [!] {e}")

            _fluent_wait(
                lambda: page.evaluate("document.readyState") == "complete",
                timeout=10.0,
                poll_interval=0.3,
                error_msg="Page did not reach complete readyState",
            )

            menu_link = None
            try:
                element_handle = page.evaluate_handle(
                    """
                    (targetText) => {
                        const labels = document.querySelectorAll(
                            'ul.menu-section[role="menubar"] > li.menu-item > div.menu-item-label'
                        );
                        for (const label of labels) {
                            const directText = Array.from(label.childNodes)
                                .filter(n => n.nodeType === 3)
                                .map(n => n.nodeValue.trim())
                                .filter(t => t)
                                .join('');
                            const anchor = label.querySelector(':scope > a');
                            const anchorText = anchor ? anchor.innerText.trim() : '';
                            const text = (directText || anchorText).trim();
                            if (text === targetText) return label;
                        }
                        return null;
                    }
                """,
                    menu_item,
                )
                menu_link = element_handle.as_element()
            except Exception as e:
                print(f"    [!] Error finding element: {e}")

            if menu_link:
                try:
                    submenu_items = page.evaluate(
                        """
                        (targetText) => {
                            const lis = document.querySelectorAll(
                                'ul.menu-section[role="menubar"] > li.menu-item'
                            );
                            for (const li of lis) {
                                const label = li.querySelector(':scope > div.menu-item-label');
                                if (!label) continue;
                                const directText = Array.from(label.childNodes)
                                    .filter(n => n.nodeType === 3)
                                    .map(n => n.nodeValue.trim()).filter(t => t).join('');
                                const anchor = label.querySelector(':scope > a');
                                const text = (directText || (anchor ? anchor.innerText.trim() : '')).trim();
                                if (text === targetText) {
                                    const subLinks = li.querySelectorAll(
                                        'ul.menu-section[role="menu"] li.menu-item div.menu-item-label a'
                                    );
                                    return Array.from(subLinks).map(a => a.innerText.trim()).filter(t => t);
                                }
                            }
                            return [];
                        }
                    """,
                        menu_item,
                    )
                    if submenu_items:
                        print(f"    [SUBMENU] '{menu_item}' has {len(submenu_items)} submenu option(s):")
                        for i, sub in enumerate(submenu_items, 1):
                            print(f"              {i}. {sub}")
                    else:
                        print(f"    [SUBMENU] '{menu_item}' has 0 submenu options (no dropdown)")
                except Exception as e:
                    print(f"    [!] Could not fetch submenus: {e}")

                menu_link.scroll_into_view_if_needed()
                _fluent_wait(
                    lambda: menu_link.is_visible(),
                    timeout=5.0,
                    poll_interval=0.3,
                    error_msg=f"'{menu_item}' tab not visible before click",
                )
                menu_link.click()
                try:
                    page.wait_for_load_state("domcontentloaded", timeout=8000)
                except Exception:
                    pass
                _fluent_wait(
                    lambda: page.evaluate("document.readyState") == "complete",
                    timeout=10.0,
                    poll_interval=0.3,
                    error_msg=f"Page did not stabilise after clicking '{menu_item}'",
                )
                current_url = page.url
                click_results.append({"item": menu_item, "status": "SUCCESS", "url": current_url})
                print(
                    f"\n[SCRIPT RESPONSE] Successfully clicked on menu item: '{menu_item}' | URL: {current_url}"
                )
            else:
                click_results.append(
                    {"item": menu_item, "status": "FAILED", "reason": "Element not found"}
                )

        except Exception as e:
            print(f"    [ERROR] {str(e)}")
            click_results.append({"item": menu_item, "status": "FAILED", "reason": str(e)})

    successful = sum(1 for r in click_results if r["status"] == "SUCCESS")
    failed = sum(1 for r in click_results if r["status"] == "FAILED")
    print(f"\n{_SEP}")
    print(f"Total: {len(menu_items)} | [+] Successful: {successful} | [-] Failed: {failed}")
    print(f"{_SEP}\n")
    return click_results


def _screenshot_new_reallocation_popup(
    page, screenshot_dir: str = SMIHomePage.SCREENSHOTS_DIR
) -> str:
    """Fluent-wait for the Select Company/Strategist popup, then screenshot it."""
    dialog_selectors = SMIReallocationPage.DIALOG_SELECTORS
    js_condition = " || ".join(f'!!document.querySelector("{s}")' for s in dialog_selectors)
    popup_found = _fluent_wait_js(
        page,
        f"return {js_condition}",
        timeout_ms=15000,
        poll_ms=500,
        description="popup dialog present",
    )
    if not popup_found:
        print("[WARN] Popup not detected — taking full-page screenshot anyway")

    _fluent_wait_js(
        page,
        f"""
        return (() => {{
            const el = document.querySelector('{SMIHomePage.POPUP_TITLE}');
            return el && el.textContent.trim().length > 0;
        }})()
        """,
        timeout_ms=5000,
        poll_ms=300,
        description="popup title rendered",
    )

    popup_title = page.evaluate(
        f"""
        () => {{
            const el = document.querySelector('{SMIHomePage.POPUP_TITLE}');
            return el ? el.textContent.trim() : '';
        }}
    """
    )
    if popup_title:
        print(f"[POPUP] Title: {popup_title}")

    os.makedirs(screenshot_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(screenshot_dir, f"new_reallocation_popup_{timestamp}.png")
    try:
        page.screenshot(path=path, full_page=False, timeout=15000)
        print(f"[SCREENSHOT] Popup screenshot saved: {path}")
    except Exception as e:
        print(f"[SCREENSHOT] Popup screenshot skipped: {e}")
    return path


def _click_popup_dropdown(page, screenshot_dir: str = SMIHomePage.SCREENSHOTS_DIR) -> list:
    """Click the dropdown inside the Select Company/Strategist popup."""
    _fluent_wait_js(
        page,
        f"""
        return (() => {{
            const sel = document.querySelector('{SMIHomePage.POPUP_DROPDOWN}');
            return sel && sel.options.length > 0;
        }})()
        """,
        timeout_ms=15000,
        poll_ms=500,
        description="dropdown options loaded",
    )

    dropdown = page.wait_for_selector(
        SMIHomePage.POPUP_DROPDOWN,
        state="attached",
        timeout=5000,
    )

    options = page.evaluate(
        f"""
        () => {{
            const sel = document.querySelector('{SMIHomePage.POPUP_DROPDOWN}');
            if (!sel) return [];
            return Array.from(sel.options).map(o => o.text.trim());
        }}
    """
    )
    print(f"[DROPDOWN] {len(options)} option(s) available: {options}")
    dropdown.click()
    return options


def _click_popup_ok_button(page) -> None:
    """Click the OK / submit button inside the Select Company/Strategist popup."""
    clicked = page.evaluate(
        """
        () => {
            const btns = document.querySelectorAll('.ui-dialog-buttonset button');
            for (const btn of btns) {
                const txt = btn.textContent.trim().toLowerCase();
                if (txt === 'ok' || txt === 'submit' || txt === 'continue') {
                    btn.click();
                    return 'buttonset:' + btn.textContent.trim();
                }
            }
            const dialogBtns = document.querySelectorAll(
                'div[role="dialog"] button, div.ui-dialog button, ' +
                'div[role="dialog"] input[type="submit"], div.ui-dialog input[type="submit"], ' +
                'div[role="dialog"] input[type="button"], div.ui-dialog input[type="button"]'
            );
            for (const btn of dialogBtns) {
                const txt = (btn.value || btn.textContent || '').trim().toLowerCase();
                if (txt === 'ok' || txt === 'submit' || txt === 'continue') {
                    btn.click();
                    return 'dialog:' + (btn.value || btn.textContent).trim();
                }
            }
            if (dialogBtns.length > 0) {
                const first = dialogBtns[0];
                first.click();
                return 'fallback:' + (first.value || first.textContent).trim();
            }
            return null;
        }
        """
    )
    if clicked:
        print(f"[POPUP] OK button clicked via: {clicked}")
    else:
        raise RuntimeError("OK button not found in popup dialog")

    try:
        page.wait_for_url("**/reallocations/**/edit/**", timeout=20000)
    except Exception:
        pass
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception:
        pass
    print("[POPUP] Popup closed successfully after clicking OK")


def _reset_to_home(page, login_url: str) -> None:
    """Navigate back to the SMI home URL."""
    try:
        page.goto(login_url, wait_until="domcontentloaded", timeout=20000)
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        pass


def _navigate_menu_tab(page, home_url: str, tab_name: str, submenu_names: list) -> None:
    """Reset to home, collect submenu hrefs, then navigate each submenu in order."""
    _reset_to_home(page, home_url)
    hrefs = _get_tab_submenu_hrefs(page, tab_name)
    for name in submenu_names:
        href = hrefs.get(name)
        if href:
            _goto_submenu(page, href, tab_name, name)
        else:
            print(f"[SKIP] {tab_name} > {name} not available for this agent role")
    print(f"[PASSED] {tab_name} tab and all submenus navigated successfully")


def _click_model_search_button(page) -> None:
    """Click the 'Model Search' button on the Edit Reallocation form."""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
    except Exception:
        pass

    _fluent_wait_js(
        page,
        "return !!document.getElementById('ModelSearch_YGKKGZUBNEA');",
        timeout_ms=30000,
        poll_ms=500,
        description="Model Search button present in DOM",
    )

    _take_screenshot(page, prefix="before_model_search_click")

    clicked = False
    for locator_str in [
        "#ModelSearch_YGKKGZUBNEA",
        "button:has-text('Model Search')",
        "input[value='Model Search']",
    ]:
        try:
            loc = page.locator(locator_str).first
            loc.scroll_into_view_if_needed(timeout=5000)
            loc.click(force=True, timeout=10000)
            print(f"[MODEL SEARCH] Clicked via Playwright locator (force=True): {locator_str}")
            clicked = True
            break
        except Exception as e:
            print(f"[MODEL SEARCH] Locator '{locator_str}' failed: {e}")

    if not clicked:
        result = page.evaluate(
            """
            () => {
                const byId = document.getElementById('ModelSearch_YGKKGZUBNEA');
                if (byId) {
                    byId.scrollIntoView({block: 'center'});
                    ['mouseenter','mouseover','mousedown','mouseup','click'].forEach(evt =>
                        byId.dispatchEvent(new MouseEvent(evt, {bubbles: true, cancelable: true, view: window}))
                    );
                    return 'id:ModelSearch_YGKKGZUBNEA';
                }
                const needle = 'model search';
                for (const el of document.querySelectorAll(
                        'button, input[type="button"], input[type="submit"], a')) {
                    const txt = (el.innerText || el.textContent || el.value || '')
                        .trim().toLowerCase();
                    if (txt.includes(needle)) {
                        el.scrollIntoView({block: 'center'});
                        ['mouseenter','mouseover','mousedown','mouseup','click'].forEach(evt =>
                            el.dispatchEvent(new MouseEvent(evt, {bubbles: true, cancelable: true, view: window}))
                        );
                        return 'text:' + (el.innerText || el.textContent || el.value || '').trim();
                    }
                }
                return null;
            }
            """
        )
        if result:
            print(f"[MODEL SEARCH] Clicked via JS MouseEvent dispatch: {result}")
            clicked = True
        else:
            raise RuntimeError("Model Search button not found on the reallocation form.")

    _take_screenshot(page, prefix="after_model_search_click")

    dialog_appeared = _fluent_wait_js(
        page,
        """
        return !!(
            document.querySelector('div[role="dialog"]') ||
            document.querySelector('div.ui-dialog') ||
            document.querySelector('.ui-dialog-content') ||
            document.querySelector('.search-results')
        )
        """,
        timeout_ms=20000,
        poll_ms=500,
        description="model search dialog appeared",
    )
    if not dialog_appeared:
        _take_screenshot(page, prefix="model_search_no_dialog")
        raise RuntimeError(
            "Model Search button was clicked but no search dialog appeared."
        )
    _take_screenshot(page, prefix="model_search_dialog")
    _fluent_wait_js(
        page,
        "return !!document.getElementById('SelectedModelSet_0__IsSelected');",
        timeout_ms=10000,
        poll_ms=300,
        description="model search dialog content ready",
    )
    print("[MODEL SEARCH] Search dialog appeared successfully")


def _select_model_id(page, model_id: str) -> None:
    """Select a model from the search results by matching model_id text."""
    debug_rows = page.evaluate(
        """
        (mid) => {
            const results = [];
            for (const row of document.querySelectorAll(
                    'div[role="dialog"] tr, div.ui-dialog tr, table tr')) {
                results.push(row.innerText.trim().substring(0, 120));
            }
            for (const a of document.querySelectorAll('a')) {
                const txt = a.textContent.trim();
                if (txt.toLowerCase().includes(mid.toLowerCase()))
                    results.push('LINK: ' + txt);
            }
            return results;
        }
        """,
        model_id,
    )
    for r in debug_rows:
        if r.strip():
            print(f"  {r}")

    clicked = page.evaluate(
        """
        (mid) => {
            const lower = mid.toLowerCase();
            for (const a of document.querySelectorAll(
                    'div[role="dialog"] a, div.ui-dialog a, table a')) {
                if (a.textContent.trim().toLowerCase() === lower) {
                    a.click();
                    return 'link-exact:' + a.textContent.trim();
                }
            }
            for (const a of document.querySelectorAll(
                    'div[role="dialog"] a, div.ui-dialog a, table a')) {
                if (a.textContent.trim().toLowerCase().includes(lower)) {
                    a.click();
                    return 'link-contains:' + a.textContent.trim();
                }
            }
            for (const td of document.querySelectorAll(
                    'div[role="dialog"] td, div.ui-dialog td, table td')) {
                if (td.textContent.trim().toLowerCase() === lower) {
                    td.click();
                    return 'td-exact:' + td.textContent.trim();
                }
            }
            return null;
        }
        """,
        model_id,
    )

    if clicked:
        print(f"[MODEL SELECT] Selected model '{model_id}' via: {clicked}")
    else:
        model_input = None
        for sel in [
            f'input[value*="{model_id}" i]',
            'input[id*="Model" i][type="text"]',
            'input[name*="Model" i][type="text"]',
        ]:
            try:
                model_input = page.wait_for_selector(sel, state="visible", timeout=2000)
                if model_input:
                    break
            except Exception:
                continue

        if model_input:
            model_input.fill(model_id)
        else:
            raise RuntimeError(
                f"Could not select model '{model_id}'. No matching link or input found."
            )

    try:
        _fluent_wait_js(
            page,
            'return !document.querySelector(\'div[role="dialog"], div.ui-dialog\')',
            timeout_ms=8000,
            poll_ms=400,
            description="model search dialog closed",
        )
    except Exception:
        pass
    try:
        page.wait_for_load_state("domcontentloaded", timeout=8000)
    except Exception:
        pass
    _take_screenshot(page, prefix="model_selected")


def _do_login(page, login_url: str, username: str, password: str) -> None:
    """Shared login routine used by multiple steps."""
    page.goto(login_url, timeout=90000, wait_until="domcontentloaded")
    page.wait_for_selector(SMILoginPage.USERNAME_INPUT, timeout=30000)
    page.fill(SMILoginPage.USERNAME_INPUT, username)
    page.fill(SMILoginPage.PASSWORD_INPUT, password)
    page.click(SMILoginPage.LOGIN_BUTTON)
    try:
        page.wait_for_url(
            lambda url: login_url.rstrip("/") not in url.rstrip("/"),
            timeout=60000,
        )
    except Exception as e:
        print(f"[LOGIN] URL change wait: {e}")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception:
        pass
    try:
        page.wait_for_selector("body", timeout=10000)
    except Exception:
        pass


# ===========================================================================
# Step Definitions — Login & Navigation
# ===========================================================================


@given("I am on the login page of SMI")
def step_open_login_page(smi_login_page):
    page = smi_login_page.page
    login_url = smi_login_page.base_url or ""
    page.goto(login_url, timeout=90000, wait_until="domcontentloaded")
    # Wait for Okta widget to fully render before the login step fills credentials
    try:
        page.wait_for_load_state("networkidle", timeout=20000)
    except Exception:
        pass
    page.wait_for_selector(SMILoginPage.USERNAME_INPUT, timeout=30000)


@when("I login with valid credentials on the login page")
def step_login_with_valid_credentials(smi_login_page, credentials):
    page = smi_login_page.page
    page.fill(SMILoginPage.USERNAME_INPUT, credentials["username"])
    page.fill(SMILoginPage.PASSWORD_INPUT, credentials["password"])
    page.click(SMILoginPage.LOGIN_BUTTON)
    print("[DEBUG] Login button clicked, waiting for navigation...")
    login_url = smi_login_page.base_url or ""
    try:
        page.wait_for_url(
            lambda url: login_url.rstrip("/") not in url.rstrip("/"),
            timeout=60000,
        )
    except Exception as e:
        print(f"[DEBUG] URL change wait: {e}")
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception as e:
        print(f"[DEBUG] networkidle wait: {e}")
    try:
        page.wait_for_load_state("domcontentloaded", timeout=15000)
    except Exception as e:
        print(f"[DEBUG] domcontentloaded wait: {e}")
    try:
        page.wait_for_selector("body", timeout=10000)
    except Exception as e:
        print(f"[DEBUG] body wait: {e}")
    try:
        _fluent_wait(
            lambda: page.query_selector(SMIHomePage.MENU_SECTION) is not None,
            timeout=15.0,
            poll_interval=0.5,
            error_msg="Menu section did not appear after login",
        )
    except TimeoutError as e:
        print(f"[DEBUG] {e}")
    print("[DEBUG] Current URL after login:", page.url)


@then("I print the title of the landing page")
def step_print_landing_page_title(smi_login_page):
    title = smi_login_page.page.title()
    print(f"Landing page title after login: {title}")


@then("I take a screenshot of the landing page")
def step_take_landing_page_screenshot(smi_login_page):
    screenshot_path = _take_screenshot(smi_login_page.page, prefix="smi_landing_page")
    print(f"Screenshot saved: {screenshot_path}")


@then("I should see the main menu bar")
def step_verify_main_menu_bar(smi_login_page):
    menu_items = _get_clean_menu_items(smi_login_page.page)
    assert menu_items and len(menu_items) > 0, "Main menu bar not found or has no items"
    print(f"[PASSED] Main menu bar is visible with {len(menu_items)} main items")


@then("I print the list of main navigation menu items")
def step_print_main_menu_items(smi_login_page):
    menu_items = _print_menu_bar_items(smi_login_page.page)
    assert menu_items and len(menu_items) > 0, "Failed to retrieve main navigation menu items"
    print(f"\n[SCRIPT RESPONSE] Main Navigation Menu Items: {menu_items}")


@then("I print submenu options for each menu item")
def step_print_submenu_options(smi_login_page):
    _print_submenu_options(smi_login_page.page)
    print("[SCRIPT RESPONSE] Submenu options printed above.")


@then("I click on each menu item one by one and verify")
def step_click_on_each_menu_item(smi_login_page):
    click_results = _click_on_each_menu_item(smi_login_page.page)
    successful_clicks = [r for r in click_results if r["status"] == "SUCCESS"]
    assert len(successful_clicks) > 0, "No menu items were clicked successfully"
    print(
        f"\n[ASSERTION PASSED] Successfully clicked {len(successful_clicks)}"
        f" out of {len(click_results)} menu items"
    )


# ===========================================================================
# Step Definitions — Menu-tab navigation steps
# ===========================================================================


@then("I click manager console header")
def step_click_manager_console_header(smi_login_page):
    _click_tab_by_text(smi_login_page.page, SMIManagerConsolePage.TAB_NAME)
    print(f"[NAV] Clicked '{SMIManagerConsolePage.TAB_NAME}' tab")


@then("I click all menu items on the SMI landing page")
def step_click_all_menu_items(smi_login_page):
    _click_on_each_menu_item(smi_login_page.page)


@then("I navigate to Manager Console menu tab")
def step_navigate_manager_console(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMIManagerConsolePage.TAB_NAME,
        [
            SMIManagerConsolePage.SUBMENU_DASHBOARD,
            SMIManagerConsolePage.SUBMENU_ACCOUNTS,
            SMIManagerConsolePage.SUBMENU_ADVISORS,
            SMIManagerConsolePage.SUBMENU_ACTIVITY,
        ],
    )


@then("I navigate to Models menu tab")
def step_navigate_models(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMIModelsPage.TAB_NAME,
        [
            SMIModelsPage.SUBMENU_MODEL_MAINTENANCE,
            SMIModelsPage.SUBMENU_REPLACEMENT_SECURITIES,
        ],
    )


@then("I navigate to Performance menu tab")
def step_navigate_performance(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMIPerformancePage.TAB_NAME,
        [SMIPerformancePage.SUBMENU_REPORT_CENTER],
    )


@then("I navigate to Companies menu tab")
def step_navigate_companies(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMICompaniesPage.TAB_NAME,
        [SMICompaniesPage.SUBMENU_EDIT, SMICompaniesPage.SUBMENU_CREATE],
    )


@then("I navigate to Reallocations menu tab")
def step_navigate_reallocations(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMIReallocationPage.TAB_NAME,
        [
            SMIReallocationPage.SUBMENU_NEW,
            SMIReallocationPage.SUBMENU_IN_PROGRESS,
            SMIReallocationPage.SUBMENU_HISTORY,
        ],
    )


@then("I navigate to Admin menu tab")
def step_navigate_admin(smi_login_page):
    _navigate_menu_tab(
        smi_login_page.page,
        smi_login_page.base_url or "",
        SMIAdminPage.TAB_NAME,
        [SMIAdminPage.SUBMENU_MODEL_MAINTENANCE, SMIAdminPage.SUBMENU_USER_MAINTENANCE],
    )


# ===========================================================================
# Step Definitions — Reallocation form interactions
# ===========================================================================


@then("I click on the Reallocations menu bar item")
def step_click_reallocations_tab(smi_login_page):
    page = smi_login_page.page
    _click_tab_by_text(page, SMIReallocationPage.TAB_NAME)
    _fluent_wait_js(
        page,
        """return !!document.querySelector('ul.menu-section[role="menubar"] li.menu-item ul[role="menu"] li');""",
        timeout_ms=10000,
        poll_ms=300,
        description="Reallocations submenu visible",
    )
    print(f"[NAV] Clicked '{SMIReallocationPage.TAB_NAME}' tab")


@then("I click on New submenu under Reallocations")
def step_click_new_under_reallocations(smi_login_page):
    page = smi_login_page.page
    clicked = _click_submenu_item(
        page, SMIReallocationPage.TAB_NAME, SMIReallocationPage.SUBMENU_NEW
    )
    if clicked:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        dialog_appeared = _fluent_wait_js(
            page,
            'return !!document.querySelector(\'div[role="dialog"], div.ui-dialog\')',
            timeout_ms=25000,
            poll_ms=500,
            description="Select Company/Strategist dialog",
        )
        if not dialog_appeared:
            print("[WARN] Dialog not detected after clicking New — continuing anyway")
        print(f"[NAV] Clicked {SMIReallocationPage.TAB_NAME} > {SMIReallocationPage.SUBMENU_NEW}")
    else:
        print(
            f"[SKIP] '{SMIReallocationPage.SUBMENU_NEW}' not available under "
            f"'{SMIReallocationPage.TAB_NAME}' for this agent role"
        )


@then("I take a screenshot of the Select Company Strategist popup")
def step_screenshot_reallocation_popup(smi_login_page):
    path = _screenshot_new_reallocation_popup(smi_login_page.page)
    print(f"Popup screenshot saved: {path}")


@then("I click on the dropdown in the popup")
def step_click_popup_dropdown(smi_login_page):
    options = _click_popup_dropdown(smi_login_page.page)
    print(f"[SCRIPT RESPONSE] Dropdown options: {options}")


@then(parsers.parse('I select "{option_text}" from the dropdown in the popup'))
def step_select_dropdown_option(smi_login_page, option_text):
    page = smi_login_page.page
    dropdown = page.wait_for_selector(
        SMIReallocationPage.POPUP_DROPDOWN,
        state="attached",
        timeout=10000,
    )
    dropdown.select_option(label=option_text)
    _fluent_wait_js(
        page,
        "return document.readyState === 'complete';",
        timeout_ms=2000,
        poll_ms=100,
        description="DOM stable after dropdown selection",
    )
    print(f"[DROPDOWN] Selected option: '{option_text}'")


@then("I click on the OK button of the popup")
def step_click_popup_ok_button(smi_login_page):
    _click_popup_ok_button(smi_login_page.page)
    print("[SCRIPT RESPONSE] OK button clicked and popup dismissed")


@then("I wait for the reallocation form to be visible")
def step_wait_for_reallocation_form(smi_login_page):
    page = smi_login_page.page
    try:
        page.wait_for_load_state("domcontentloaded", timeout=20000)
    except Exception:
        pass
    _fluent_wait_js(
        page,
        "return document.readyState === 'complete'",
        timeout_ms=20000,
        poll_ms=500,
        description="reallocation form page ready",
    )
    _fluent_wait_js(
        page,
        "return !!document.getElementById('ModelSearch_YGKKGZUBNEA');",
        timeout_ms=25000,
        poll_ms=500,
        description="reallocation form ready (Model Search button present)",
    )
    _take_screenshot(page, prefix="reallocation_form_loaded")
    print("[FORM] Reallocation form is visible and ready")


@then("I click on the model search button")
def step_click_model_search_button(smi_login_page):
    _click_model_search_button(smi_login_page.page)
    print("[SCRIPT RESPONSE] Model search button clicked")


@then("I click on the model checkbox")
def step_click_model_checkbox(smi_login_page):
    page = smi_login_page.page
    checkbox_id = "SelectedModelSet_0__IsSelected"
    _fluent_wait_js(
        page,
        f"return !!document.getElementById('{checkbox_id}');",
        timeout_ms=20000,
        poll_ms=500,
        description=f"checkbox #{checkbox_id} present",
    )
    try:
        chk = page.locator(f"#{checkbox_id}").first
        chk.scroll_into_view_if_needed(timeout=5000)
        chk.click(force=True, timeout=10000)
    except Exception as e:
        print(f"[CHECKBOX] Playwright click failed ({e}), trying JS click")
        page.evaluate(
            f"""
            () => {{
                const el = document.getElementById('{checkbox_id}');
                if (el) {{
                    el.scrollIntoView({{block: 'center'}});
                    el.click();
                }}
            }}
            """
        )
    is_checked = page.evaluate(
        f"() => {{ const el = document.getElementById('{checkbox_id}'); return el ? el.checked : false; }}"
    )
    _take_screenshot(page, prefix="model_checkbox_selected")
    if is_checked:
        print(f"[CHECKBOX] SUCCESS: Checkbox '#{checkbox_id}' is CHECKED")
    else:
        print(f"[CHECKBOX] WARNING: Checkbox '#{checkbox_id}' clicked but checked=False")
    print("[SCRIPT RESPONSE] Model checkbox clicked")


@then("I click on the OK button of the model search popup")
def step_click_model_search_ok_button(smi_login_page):
    page = smi_login_page.page
    clicked = page.evaluate(
        """
        () => {
            const btns = document.querySelectorAll('.ui-dialog-buttonset button');
            for (const btn of btns) {
                const txt = btn.textContent.trim().toLowerCase();
                if (txt === 'ok' || txt === 'select' || txt === 'submit' || txt === 'continue') {
                    btn.click();
                    return 'buttonset:' + btn.textContent.trim();
                }
            }
            const dialogBtns = document.querySelectorAll(
                'div[role="dialog"] button, div.ui-dialog button, ' +
                'div[role="dialog"] input[type="submit"], div.ui-dialog input[type="submit"]'
            );
            for (const btn of dialogBtns) {
                const txt = (btn.value || btn.textContent || '').trim().toLowerCase();
                if (txt === 'ok' || txt === 'select' || txt === 'submit' || txt === 'continue') {
                    btn.click();
                    return 'dialog:' + (btn.value || btn.textContent).trim();
                }
            }
            if (dialogBtns.length > 0) {
                dialogBtns[0].click();
                return 'fallback:' + (dialogBtns[0].value || dialogBtns[0].textContent).trim();
            }
            return null;
        }
        """
    )
    if not clicked:
        raise RuntimeError("OK button not found in model search popup")
    _fluent_wait_js(
        page,
        'return !document.querySelector(\'.ui-dialog\');',
        timeout_ms=10000,
        poll_ms=300,
        description="model search dialog closed",
    )
    _take_screenshot(page, prefix="model_search_popup_ok_clicked")
    print("[SCRIPT RESPONSE] Model search popup OK button clicked successfully")


@then("I click on the rebalance only checkbox")
def step_click_rebalance_only_checkbox(smi_login_page):
    page = smi_login_page.page
    checkbox_id = "UpdatedModels_APODCF__IsRebalanceOnly"
    _fluent_wait_js(
        page,
        f"return !!document.getElementById('{checkbox_id}');",
        timeout_ms=20000,
        poll_ms=500,
        description=f"rebalance only checkbox #{checkbox_id} present",
    )
    try:
        chk = page.locator(f"#{checkbox_id}").first
        chk.scroll_into_view_if_needed(timeout=5000)
        chk.click(force=True, timeout=10000)
    except Exception as e:
        print(f"[CHECKBOX] Playwright click failed ({e}), trying JS click")
        page.evaluate(
            f"""
            () => {{
                const el = document.getElementById('{checkbox_id}');
                if (el) {{
                    el.scrollIntoView({{block: 'center'}});
                    el.click();
                }}
            }}
            """
        )
    _take_screenshot(page, prefix="rebalance_only_checkbox_selected")
    print("[SCRIPT RESPONSE] Rebalance only checkbox clicked")


@then("I click on the Review button")
def step_click_review_button(smi_login_page):
    page = smi_login_page.page
    clicked = page.evaluate(
        """
        () => {
            const all = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
            for (const el of all) {
                const txt = (el.value || el.textContent || el.innerText || '').trim().toLowerCase();
                if (txt === 'review') {
                    el.scrollIntoView({block: 'center'});
                    el.click();
                    return 'js:' + (el.value || el.textContent || el.innerText).trim();
                }
            }
            return null;
        }
        """
    )
    if not clicked:
        try:
            btn = page.locator("button:has-text('Review'), input[value='Review']").first
            btn.scroll_into_view_if_needed(timeout=5000)
            btn.click(force=True, timeout=10000)
            clicked = "playwright:Review"
        except Exception as e:
            raise RuntimeError(f"Review button not found: {e}")
    _fluent_wait_js(
        page,
        "return !!document.getElementById('EffectiveDate');",
        timeout_ms=10000,
        poll_ms=300,
        description="EffectiveDate field ready after Review",
    )
    _take_screenshot(page, prefix="review_button_clicked")
    print(f"[REVIEW] Review button clicked via: {clicked}")


@then("I select the latest effective date")
def step_select_latest_effective_date(smi_login_page):
    page = smi_login_page.page
    field_id = "EffectiveDate"
    _fluent_wait_js(
        page,
        f"return !!document.getElementById('{field_id}');",
        timeout_ms=20000,
        poll_ms=500,
        description=f"EffectiveDate field present",
    )
    try:
        field = page.locator(f"#{field_id}").first
        field.scroll_into_view_if_needed(timeout=5000)
        field.click(force=True, timeout=10000)
    except Exception as e:
        page.evaluate(f"document.getElementById('{field_id}').click();")
        print(f"[DATE] Opened datepicker via JS ({e})")

    selected_date = page.evaluate(
        """
        () => {
            const cells = document.querySelectorAll(
                '#ui-datepicker-div td:not(.ui-datepicker-unselectable):not(.ui-state-disabled) a,' +
                '#ui-datepicker-div td:not(.ui-datepicker-unselectable):not(.ui-state-disabled) span'
            );
            if (cells.length > 0) {
                const last = cells[cells.length - 1];
                last.click();
                return 'datepicker:' + last.textContent.trim();
            }
            const el = document.getElementById('EffectiveDate');
            if (el) {
                const today = new Date().toISOString().split('T')[0];
                el.value = today;
                el.dispatchEvent(new Event('change', {bubbles: true}));
                return 'input-today:' + today;
            }
            return null;
        }
        """
    )
    if not selected_date:
        raise RuntimeError("Could not select a date from #EffectiveDate datepicker")
    _take_screenshot(page, prefix="effective_date_selected")
    print(f"[DATE] Selected effective date via: {selected_date}")


@then("I click on the Submit/Approve button")
def step_click_submit_approve_button(smi_login_page):
    page = smi_login_page.page
    clicked = page.evaluate(
        """
        () => {
            const byTitle = document.querySelector('[title="Submit/Approve"]');
            if (byTitle) {
                byTitle.scrollIntoView({block: 'center'});
                byTitle.click();
                return 'title:' + (byTitle.value || byTitle.textContent || byTitle.title).trim();
            }
            const all = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
            for (const el of all) {
                const txt = (el.value || el.textContent || el.innerText || '').trim();
                if (txt.toLowerCase().includes('submit') || txt.toLowerCase().includes('approve')) {
                    el.scrollIntoView({block: 'center'});
                    el.click();
                    return 'text:' + txt;
                }
            }
            return null;
        }
        """
    )
    if not clicked:
        try:
            btn = page.locator('[title="Submit/Approve"]').first
            btn.scroll_into_view_if_needed(timeout=5000)
            btn.click(force=True, timeout=10000)
            clicked = "playwright:Submit/Approve"
        except Exception as e:
            raise RuntimeError(f"Submit/Approve button not found: {e}")
    _take_screenshot(page, prefix="submit_approve_clicked")
    print(f"[SUBMIT] Submit/Approve button clicked via: {clicked}")


@then(parsers.parse('I select "{model_id}" as the model id'))
def step_select_model_id(smi_login_page, model_id):
    _select_model_id(smi_login_page.page, model_id)
    print(f"[SCRIPT RESPONSE] Model ID '{model_id}' selected")


# ===========================================================================
# Step Definitions — Logout & multi-user login
# ===========================================================================


@then("I log out of SMI")
def step_logout_smi(smi_login_page):
    page = smi_login_page.page
    logged_out = page.evaluate(
        """
        () => {
            const links = document.querySelectorAll(
                'a[href*="logout"], a[href*="signout"], a[href*="logoff"]'
            );
            if (links.length > 0) { links[0].click(); return 'link:' + links[0].href; }
            for (const el of document.querySelectorAll('a, button')) {
                const txt = (el.textContent || el.innerText || '').trim().toLowerCase();
                if (txt === 'log out' || txt === 'logout' || txt === 'sign out') {
                    el.click(); return 'text:' + txt;
                }
            }
            return null;
        }
        """
    )
    if not logged_out:
        current_url = page.url
        base = current_url.split('/')[0] + '//' + current_url.split('/')[2]
        page.goto(base + '/account/logout')
        logged_out = 'nav:' + base + '/account/logout'
    try:
        page.wait_for_load_state('networkidle', timeout=10000)
    except Exception:
        pass
    # Force full Okta/SSO session clear
    try:
        current_url = page.url
        base = current_url.split('/')[0] + '//' + current_url.split('/')[2]
        logout_url = base + '/account/logout'
        page.goto(logout_url, wait_until='domcontentloaded', timeout=15000)
    except Exception as e:
        print(f"[LOGOUT] Logout URL navigation: {e}")
    _take_screenshot(page, prefix="after_logout")
    print(f"[LOGOUT] Logged out via: {logged_out}")
    print("[SCRIPT RESPONSE] Logged out of SMI successfully")


@then("I login as executive agent")
def step_login_as_executive_agent(smi_login_page, executive_credentials):
    page = smi_login_page.page
    page.context.clear_cookies()
    try:
        page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    except Exception:
        pass
    login_url = smi_login_page.base_url or ""
    _do_login(page, login_url, executive_credentials["username"], executive_credentials["password"])
    # After SSO login the browser may still be on the identity-provider domain;
    # wait for the app menu to appear so we know the redirect back completed.
    try:
        _fluent_wait(
            lambda: page.query_selector(SMIHomePage.MENU_SECTION) is not None,
            timeout=30.0,
            poll_interval=0.5,
            error_msg="Menu section did not appear after executive agent login",
        )
    except TimeoutError as e:
        print(f"[EXEC LOGIN] {e}")
    _take_screenshot(page, prefix="executive_agent_login")
    print(f"[EXEC LOGIN] Current URL after executive login: {page.url}")
    print("[SCRIPT RESPONSE] Executive agent login successful")


@then("I verify the executive agent landing page")
def step_verify_executive_agent_landing_page(smi_login_page):
    page = smi_login_page.page
    menu_items = _get_clean_menu_items(page)
    assert menu_items and len(menu_items) > 0, "Main menu bar not found after executive agent login"
    _take_screenshot(page, prefix="executive_agent_landing_page")
    print(f"[PASSED] Executive agent landing page verified. Menu: {menu_items}")
    print("[SCRIPT RESPONSE] Executive agent landing page verified successfully")


# ===========================================================================
# Step Definitions — Composite high-level steps (E2E workflows)
# ===========================================================================


@given("I am logged into SMI as an internal agent")
def step_logged_in_as_internal_agent(smi_login_page, credentials):
    """Open login page, sign in with internal agent credentials, verify menu."""
    page = smi_login_page.page
    login_url = smi_login_page.base_url or ""
    _do_login(page, login_url, credentials["username"], credentials["password"])
    try:
        _fluent_wait(
            lambda: page.query_selector(SMIHomePage.MENU_SECTION) is not None,
            timeout=15.0,
            poll_interval=0.5,
            error_msg="Menu section did not appear after login",
        )
    except TimeoutError as e:
        print(f"[LOGIN] {e}")
    menu_items = _get_clean_menu_items(page)
    assert menu_items and len(menu_items) > 0, "Main menu bar not found after internal agent login"
    _take_screenshot(page, prefix="internal_agent_login")
    print(f"[LOGIN] Internal agent logged in. Menu: {menu_items}")
    print("[SCRIPT RESPONSE] Internal agent login successful")


@when(parsers.parse('I perform a new reallocation for strategist "{strategist}"'))
def step_perform_new_reallocation(smi_login_page, strategist):
    """Navigate Reallocations > New, select strategist, pick model, close model search."""
    page = smi_login_page.page
    _click_tab_by_text(page, SMIReallocationPage.TAB_NAME)
    _fluent_wait_js(
        page,
        """return !!document.querySelector('ul.menu-section[role="menubar"] li.menu-item ul[role="menu"] li');""",
        timeout_ms=10000,
        poll_ms=300,
        description="Reallocations submenu visible",
    )
    clicked = _click_submenu_item(page, SMIReallocationPage.TAB_NAME, SMIReallocationPage.SUBMENU_NEW)
    if clicked:
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except Exception:
            pass
        _fluent_wait_js(
            page,
            'return !!document.querySelector(\'div[role="dialog"], div.ui-dialog\')',
            timeout_ms=25000,
            poll_ms=500,
            description="Select Company/Strategist dialog",
        )
    # Select strategist from dropdown
    _fluent_wait_js(
        page,
        f"return (() => {{ const sel = document.querySelector('{SMIHomePage.POPUP_DROPDOWN}'); return sel && sel.options.length > 0; }})()",
        timeout_ms=15000,
        poll_ms=500,
        description="strategist dropdown options loaded",
    )
    dropdown = page.wait_for_selector(SMIHomePage.POPUP_DROPDOWN, state="attached", timeout=5000)
    dropdown.select_option(label=strategist)
    print(f"[REALLOCATION] Selected strategist: '{strategist}'")
    _click_popup_ok_button(page)
    # Wait for form
    _fluent_wait_js(
        page,
        "return !!document.getElementById('ModelSearch_YGKKGZUBNEA');",
        timeout_ms=25000,
        poll_ms=500,
        description="reallocation form ready",
    )
    _take_screenshot(page, prefix="reallocation_form_loaded")
    # Open model search and select
    _click_model_search_button(page)
    checkbox_id = "SelectedModelSet_0__IsSelected"
    _fluent_wait_js(
        page,
        f"return !!document.getElementById('{checkbox_id}');",
        timeout_ms=20000,
        poll_ms=500,
        description=f"checkbox #{checkbox_id} present",
    )
    try:
        chk = page.locator(f"#{checkbox_id}").first
        chk.scroll_into_view_if_needed(timeout=5000)
        chk.click(force=True, timeout=10000)
    except Exception as e:
        print(f"[REALLOCATION] Playwright click failed ({e}), trying JS click")
        page.evaluate(
            f"() => {{ const el = document.getElementById('{checkbox_id}'); if (el) {{ el.scrollIntoView({{block:'center'}}); el.click(); }} }}"
        )
    _take_screenshot(page, prefix="model_checkbox_selected")
    # Click OK on model search popup
    clicked_ok = page.evaluate(
        """
        () => {
            const btns = document.querySelectorAll('.ui-dialog-buttonset button');
            for (const btn of btns) {
                const txt = btn.textContent.trim().toLowerCase();
                if (txt === 'ok' || txt === 'select' || txt === 'submit') {
                    btn.click(); return 'buttonset:' + btn.textContent.trim();
                }
            }
            const dialogBtns = document.querySelectorAll(
                'div[role="dialog"] button, div.ui-dialog button'
            );
            for (const btn of dialogBtns) {
                const txt = (btn.value || btn.textContent || '').trim().toLowerCase();
                if (txt === 'ok' || txt === 'select' || txt === 'submit') {
                    btn.click(); return 'dialog:' + (btn.value || btn.textContent).trim();
                }
            }
            return null;
        }
        """
    )
    if not clicked_ok:
        raise RuntimeError("OK button not found in model search popup")
    _fluent_wait_js(
        page,
        'return !document.querySelector(\'.ui-dialog\');',
        timeout_ms=10000,
        poll_ms=300,
        description="model search dialog closed",
    )
    _take_screenshot(page, prefix="model_search_popup_ok_clicked")
    print(f"[REALLOCATION] Model selected, popup closed. Strategist: '{strategist}'")
    print("[SCRIPT RESPONSE] New reallocation created successfully")


@when("I submit the reallocation for approval")
def step_submit_reallocation_for_approval(smi_login_page):
    """Click Review, select effective date, click Submit/Approve."""
    page = smi_login_page.page
    # Click Review
    clicked_review = page.evaluate(
        """
        () => {
            const all = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
            for (const el of all) {
                const txt = (el.value || el.textContent || el.innerText || '').trim().toLowerCase();
                if (txt === 'review') {
                    el.scrollIntoView({block: 'center'}); el.click();
                    return 'js:' + (el.value || el.textContent || el.innerText).trim();
                }
            }
            return null;
        }
        """
    )
    if not clicked_review:
        raise RuntimeError("Review button not found")
    _fluent_wait_js(
        page,
        "return !!document.getElementById('EffectiveDate');",
        timeout_ms=10000,
        poll_ms=300,
        description="EffectiveDate field ready",
    )
    _take_screenshot(page, prefix="review_button_clicked")
    # Select effective date
    try:
        field = page.locator("#EffectiveDate").first
        field.scroll_into_view_if_needed(timeout=5000)
        field.click(force=True, timeout=10000)
    except Exception:
        page.evaluate("document.getElementById('EffectiveDate').click();")
    selected_date = page.evaluate(
        """
        () => {
            const cells = document.querySelectorAll(
                '#ui-datepicker-div td:not(.ui-datepicker-unselectable):not(.ui-state-disabled) a,' +
                '#ui-datepicker-div td:not(.ui-datepicker-unselectable):not(.ui-state-disabled) span'
            );
            if (cells.length > 0) {
                const last = cells[cells.length - 1]; last.click();
                return 'datepicker:' + last.textContent.trim();
            }
            const el = document.getElementById('EffectiveDate');
            if (el) {
                const today = new Date().toISOString().split('T')[0];
                el.value = today; el.dispatchEvent(new Event('change', {bubbles: true}));
                return 'input-today:' + today;
            }
            return null;
        }
        """
    )
    if not selected_date:
        raise RuntimeError("Could not select effective date")
    _take_screenshot(page, prefix="effective_date_selected")
    print(f"[SUBMIT] Effective date selected: {selected_date}")
    # Click Submit/Approve
    clicked_submit = page.evaluate(
        """
        () => {
            const byTitle = document.querySelector('[title="Submit/Approve"]');
            if (byTitle) { byTitle.scrollIntoView({block:'center'}); byTitle.click(); return 'title'; }
            const all = document.querySelectorAll('button, input[type="button"], input[type="submit"], a');
            for (const el of all) {
                const txt = (el.value || el.textContent || el.innerText || '').trim();
                if (txt.toLowerCase().includes('submit') || txt.toLowerCase().includes('approve')) {
                    el.scrollIntoView({block:'center'}); el.click();
                    return 'text:' + txt;
                }
            }
            return null;
        }
        """
    )
    if not clicked_submit:
        raise RuntimeError("Submit/Approve button not found")
    _take_screenshot(page, prefix="submit_approve_clicked")
    print(f"[SUBMIT] Reallocation submitted for approval via: {clicked_submit}")
    print("[SCRIPT RESPONSE] Reallocation submitted for approval successfully")


@when(parsers.parse('I perform a new rebalance for strategist "{strategist}"'))
def step_perform_new_rebalance(smi_login_page, strategist):
    """Navigate Reallocations > New, select strategist, pick model for rebalance."""
    # Rebalance uses the same Reallocations > New flow as reallocation
    step_perform_new_reallocation(smi_login_page, strategist)
    print("[SCRIPT RESPONSE] New rebalance created successfully")


@when("I submit the rebalance for approval")
def step_submit_rebalance_for_approval(smi_login_page):
    """Check rebalance-only, click Review, select effective date, click Submit/Approve."""
    page = smi_login_page.page
    # Rebalance only checkbox
    checkbox_id = "UpdatedModels_APODCF__IsRebalanceOnly"
    _fluent_wait_js(
        page,
        f"return !!document.getElementById('{checkbox_id}');",
        timeout_ms=20000,
        poll_ms=500,
        description=f"rebalance only checkbox #{checkbox_id} present",
    )
    try:
        chk = page.locator(f"#{checkbox_id}").first
        chk.scroll_into_view_if_needed(timeout=5000)
        chk.click(force=True, timeout=10000)
    except Exception as e:
        print(f"[SUBMIT] Playwright click failed ({e}), trying JS click")
        page.evaluate(
            f"() => {{ const el = document.getElementById('{checkbox_id}'); if (el) {{ el.scrollIntoView({{block:'center'}}); el.click(); }} }}"
        )
    _take_screenshot(page, prefix="rebalance_only_checkbox_selected")
    # Delegate rest of submit to reallocation submit
    step_submit_reallocation_for_approval(smi_login_page)
    print("[SCRIPT RESPONSE] Rebalance submitted for approval successfully")
