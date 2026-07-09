from typing import Any

from playwright.sync_api import Page


def test_homepage(doc_screenshot: Any, page: Page):
    page.goto("/")
    doc_screenshot("home-home")


def test_about(doc_screenshot: Any, page: Page):
    page.goto("/about")
    doc_screenshot("home-about")
