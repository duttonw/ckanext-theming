from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk

from ckanext.theming.themes.bare.tests.conftest import ElementLocator


@pytest.mark.usefixtures("with_plugins")
class TestAbout:
    """Test the About page."""

    def test_title(self, page: Page, title_builder: Any):
        """Test the title of the About page."""
        page.goto(tk.url_for("home.about"))
        expected = title_builder("About")
        expect(page).to_have_title(expected)

    def test_breadcrumbs(self, locator: ElementLocator, page: Page):
        """Test the breadcrumbs of the About page."""
        page.goto(tk.url_for("home.about"))
        breadcrumbs = locator.locate_breadcrumbs()
        expect(breadcrumbs).to_contain_text("Home")
        expect(breadcrumbs).to_contain_text("About")


@pytest.mark.usefixtures("with_plugins")
class TestIndex:
    """Test the Home page."""

    def test_title(self, page: Page, title_builder: Any):
        """Test the title of the Home page."""
        page.goto(tk.url_for("home.index"))
        expected = title_builder("Welcome")
        expect(page).to_have_title(expected)
