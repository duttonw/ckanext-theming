from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk


@pytest.mark.usefixtures("with_plugins")
class TestIndex:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the admin index page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("admin.index"))
        expected = title_builder("Admin")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestConfig:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the admin config page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("admin.config"))
        expected = title_builder("Config", "Admin")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestTrash:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the admin trash page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("admin.trash"))
        expected = title_builder("Trash", "Admin")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResetConfig:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the admin reset config page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("admin.reset_config"))
        expected = title_builder("Admin")
        expect(page).to_have_title(expected)
