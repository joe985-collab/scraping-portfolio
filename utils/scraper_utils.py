"""Shared scraper utilities for Playwright-based scrapers."""

from typing import Optional, Callable, Any
from playwright.sync_api import Page, Locator


def safe_extract(locator: Locator, method: str = 'inner_text', default: Any = None) -> Any:
    """Safely extract text or attribute from a locator.

    Args:
        locator: Playwright locator to extract from
        method: Extraction method ('inner_text', 'text_content', 'get_attribute')
        default: Default value if extraction fails

    Returns:
        Extracted value or default
    """
    try:
        if locator.count() == 0:
            return default

        if method == 'inner_text':
            value = locator.first.inner_text()
        elif method == 'text_content':
            value = locator.first.text_content()
        elif method == 'get_attribute':
            value = locator.first.get_attribute('href')
        else:
            value = locator.first.inner_text()

        return value.strip() if value else default
    except Exception:
        return default


def wait_for_content(page: Page, selector: str, timeout: int = 10000) -> bool:
    """Wait for content to be visible on page.

    Args:
        page: Playwright page object
        selector: CSS selector to wait for
        timeout: Maximum wait time in milliseconds

    Returns:
        True if content found, False otherwise
    """
    try:
        page.wait_for_selector(selector, timeout=timeout, state='visible')
        return True
    except Exception:
        return False


def has_next_page(page: Page, next_selector: str) -> bool:
    """Check if a next page link exists and is clickable.

    Args:
        page: Playwright page object
        next_selector: Selector for the next button/link

    Returns:
        True if next page available, False otherwise
    """
    try:
        next_btn = page.locator(next_selector)
        if next_btn.count() == 0:
            return False

        # Check if button is disabled
        is_disabled = next_btn.first.get_attribute('disabled')
        if is_disabled is not None:
            return False

        # Check visibility
        return next_btn.first.is_visible()
    except Exception:
        return False


def click_next_page(page: Page, next_selector: str, wait_selector: str, timeout: int = 10000) -> bool:
    """Click the next page button and wait for new content.

    Args:
        page: Playwright page object
        next_selector: Selector for the next button/link
        wait_selector: Selector to wait for after clicking
        timeout: Maximum wait time in milliseconds

    Returns:
        True if navigation successful, False otherwise
    """
    try:
        next_btn = page.locator(next_selector)
        if next_btn.count() == 0 or not next_btn.first.is_visible():
            return False

        next_btn.first.click()
        page.wait_for_selector(wait_selector, timeout=timeout, state='visible')
        return True
    except Exception:
        return False


def extract_from_js(page: Page, script: str, default: Any = None) -> Any:
    """Execute JavaScript to extract data from page.

    Useful for bulk extraction to avoid Python loops over locators.

    Args:
        page: Playwright page object
        script: JavaScript code to execute
        default: Default value if extraction fails

    Returns:
        Result of JavaScript execution or default
    """
    try:
        return page.evaluate(script)
    except Exception:
        return default
