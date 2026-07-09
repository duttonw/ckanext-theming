from typing import Any

import pytest
from playwright.sync_api import Page

from ckan import types


def test_dashboard(
    doc_screenshot: Any,
    page: Page,
    user: dict[str, Any],
    package_factory: types.TestFactory,
    login: Any,
):
    """Test main dashboard page."""
    login(user["name"])
    package_factory(user=user)

    page.goto("/dashboard")
    doc_screenshot("dashboard")


@pytest.mark.usefixtures("clean_index")
def test_datasets(
    doc_screenshot: Any,
    page: Page,
    user: dict[str, Any],
    package_factory: types.TestFactory,
    login: Any,
):
    """Test dashboard datasets page."""
    login(user["name"])
    package_factory.create_batch(3, user=user)

    page.goto("/dashboard/datasets")
    doc_screenshot("dashboard-datasets")


def test_organizations(
    doc_screenshot: Any,
    page: Page,
    user: dict[str, Any],
    organization_factory: types.TestFactory,
    login: Any,
):
    """Test dashboard organizations page."""
    organization_factory(users=[{"name": user["name"], "capacity": "member"}])

    login(user["name"])
    page.goto("/dashboard/organizations")
    doc_screenshot("dashboard-organizations")


def test_groups(
    doc_screenshot: Any,
    page: Page,
    user: dict[str, Any],
    group_factory: types.TestFactory,
    login: Any,
):
    """Test dashboard groups page."""
    group_factory(users=[{"name": user["name"], "capacity": "member"}])

    login(user["name"])
    page.goto("/dashboard/groups")
    doc_screenshot("dashboard-groups")
