from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk


@pytest.mark.usefixtures("with_plugins")
class TestDatasets:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the dashboard datasets page has the correct title."""
        login(user)
        page.goto(tk.url_for("dashboard.datasets"))
        expected = title_builder("My Datasets", "Dashboard")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroups:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the dashboard groups page has the correct title."""
        login(user)
        page.goto(tk.url_for("dashboard.groups"))
        expected = title_builder("My Groups", "Dashboard")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizations:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the dashboard organizations page has the correct title."""
        login(user)
        page.goto(tk.url_for("dashboard.organizations"))
        expected = title_builder("My Organizations", "Dashboard")
        expect(page).to_have_title(expected)
