from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright

URL = "http://127.0.0.1:4173/index.html"
OUT = Path(os.environ.get("QA_OUT", "/tmp/list-only-cleaning-badge-qa"))
OUT.mkdir(parents=True, exist_ok=True)
WIDTHS = [320, 390, 768, 1440]
HEIGHT = 1000


def click_visible(page: Page, selector: str) -> None:
    locator = page.locator(selector)
    for index in range(locator.count()):
        candidate = locator.nth(index)
        if candidate.is_visible():
            candidate.click()
            return
    raise AssertionError(f"No visible match for selector: {selector}")


def login_admin(page: Page) -> None:
    page.goto(URL, wait_until="domcontentloaded")
    page.wait_for_selector("#login-form")
    page.locator("#login-id").fill("admin")
    page.locator("#login-password").fill("admin1234")
    page.locator('#login-form button[type="submit"]').click()
    page.wait_for_function(
        "() => [...document.querySelectorAll('[data-action=\"nav\"]')].some(el => el.offsetParent !== null)"
    )


def horizontal_overflow(page: Page) -> float:
    return float(
        page.evaluate(
            """
            () => Math.max(
              document.documentElement.scrollWidth - document.documentElement.clientWidth,
              document.body.scrollWidth - document.body.clientWidth
            )
            """
        )
    )


def wait_for_room_count(page: Page, expected: int) -> None:
    page.wait_for_function(
        "expected => document.querySelectorAll('.room-list-item').length === expected",
        expected,
    )


def badge_boundary_report(page: Page) -> list[dict[str, Any]]:
    return page.evaluate(
        r"""
        () => [...document.querySelectorAll(
          '.assignment-table .assignment-source, .assignment-table .schedule-priority-badge'
        )]
          .filter(el => el.offsetParent !== null)
          .map(el => {
            const cell = el.closest('td');
            const rect = el.getBoundingClientRect();
            const cellRect = cell ? cell.getBoundingClientRect() : null;
            return {
              text: (el.textContent || '').replace(/\s+/g, ' ').trim(),
              left: rect.left,
              right: rect.right,
              width: rect.width,
              cellLeft: cellRect?.left ?? null,
              cellRight: cellRect?.right ?? null,
              cellWidth: cellRect?.width ?? null,
              overflowLeft: cellRect ? Math.max(0, cellRect.left - rect.left) : 999,
              overflowRight: cellRect ? Math.max(0, rect.right - cellRect.right) : 999,
            };
          })
        """
    )


def qa_viewport(browser, width: int) -> dict[str, Any]:
    context = browser.new_context(viewport={"width": width, "height": HEIGHT})
    page = context.new_page()
    console_messages: list[str] = []
    page_errors: list[str] = []

    def on_console(message) -> None:
        if message.type in {"warning", "error"}:
            console_messages.append(f"{message.type}: {message.text}")

    page.on("console", on_console)
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    login_admin(page)
    assert page.url.startswith(URL), page.url
    assert page.title().strip(), "Page title is blank"
    body_after_login = page.locator("body").inner_text()
    assert len(body_after_login.strip()) > 80, "Signed-in app body is unexpectedly blank"

    # Rooms -> list-only.
    click_visible(page, '[data-action="nav"][data-view="rooms"]')
    page.wait_for_selector(".room-list-item")
    wait_for_room_count(page, 121)
    assert page.locator(".room-card-v2").count() == 0
    assert page.locator('[data-action="set-room-view"]').count() == 0
    assert page.get_by_text("카드 보기", exact=True).count() == 0
    assert page.get_by_text("리스트 보기", exact=True).count() == 0
    assert page.locator(".room-list-header span:last-child").inner_text().strip() == "PIN 관리"
    assert horizontal_overflow(page) <= 1, f"rooms overflow at {width}px"

    if width == 1440:
        action_widths = page.locator(".room-list-item").first.locator(".room-list-actions .btn").evaluate_all(
            "els => els.map(el => el.getBoundingClientRect().width)"
        )
        assert len(action_widths) == 4
        assert max(action_widths) - min(action_widths) <= 1.1, action_widths

    search = page.locator("#room-search")
    search.fill("350")
    wait_for_room_count(page, 1)
    assert page.locator('.room-list-item[data-room="350"]').count() == 1
    page.locator("#room-search").fill("")
    wait_for_room_count(page, 121)

    first_room = page.locator('.room-list-item[data-room="350"]')
    first_room.locator('[data-action="pin-show"]').click()
    page.wait_for_selector('.room-list-item[data-room="350"] [data-action="pin-hide"]')
    first_room = page.locator('.room-list-item[data-room="350"]')
    assert first_room.locator(".room-list-pin-copy strong").inner_text().strip() != "••••"
    first_room.locator('[data-action="pin-hide"]').click()
    page.wait_for_selector('.room-list-item[data-room="350"] [data-action="pin-show"]')

    page.screenshot(path=str(OUT / f"rooms-list-only-{width}.png"), full_page=False)

    # Cleaning -> tomorrow assignment -> badge containment.
    click_visible(page, '[data-action="nav"][data-view="cleaning"]')
    page.wait_for_selector('[data-action="cleaning-tab"][data-tab="assignment-tomorrow"]')
    click_visible(page, '[data-action="cleaning-tab"][data-tab="assignment-tomorrow"]')
    page.wait_for_selector('.assignment-table [data-assignment-room="552"]')
    row = page.locator('.assignment-table [data-assignment-room="552"]')
    assert "552호" in row.inner_text()
    assert row.locator(".assignment-source").count() >= 1
    assert row.locator(".schedule-priority-badge").count() >= 1

    report = badge_boundary_report(page)
    assert report, "No assignment source/schedule badges were rendered"
    offenders = [
        item
        for item in report
        if item["overflowLeft"] > 1.1 or item["overflowRight"] > 1.1
    ]
    assert not offenders, json.dumps(offenders, ensure_ascii=False, indent=2)
    assert horizontal_overflow(page) <= 1, f"cleaning overflow at {width}px"

    row.scroll_into_view_if_needed()
    page.wait_for_timeout(150)
    page.screenshot(path=str(OUT / f"cleaning-badge-contained-{width}.png"), full_page=False)

    body_text = page.locator("body").inner_text()
    for overlay_text in ["Internal Server Error", "Unhandled Runtime Error", "Vite Error", "Webpack Error"]:
        assert overlay_text not in body_text
    assert not console_messages, console_messages
    assert not page_errors, page_errors

    result = {
        "width": width,
        "title": page.title(),
        "url": page.url,
        "rooms": 121,
        "room_overflow": 0,
        "cleaning_overflow": 0,
        "badge_count": len(report),
        "badge_max_right_overflow": max(item["overflowRight"] for item in report),
        "console_messages": console_messages,
        "page_errors": page_errors,
    }
    context.close()
    return result


def main() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        results = [qa_viewport(browser, width) for width in WIDTHS]
        browser.close()
    (OUT / "qa-summary.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print("List-only room view and cleaning badge containment rendered QA: passed")


if __name__ == "__main__":
    main()
