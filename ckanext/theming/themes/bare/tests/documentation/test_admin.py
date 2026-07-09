from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page

from ckan import types

from ckanext.theming.themes.bare.tests.conftest import ElementLocator


@pytest.mark.usefixtures("clean_index")
def test_sysadmins(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test admin page."""
    login(sysadmin["name"])
    page.goto("/ckan-admin")
    doc_screenshot("admin-sysadmins")


@pytest.mark.usefixtures("clean_index")
def test_config(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    login: Any,
    faker: Faker,
):
    """Test admin config page."""
    login(sysadmin["name"])
    page.goto("/ckan-admin/config")
    doc_screenshot("admin-config")


@pytest.mark.usefixtures("clean_index")
def test_confirm_reset(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test admin confirm reset configuration page."""
    login(sysadmin["name"])
    page.goto("/ckan-admin/reset_config")
    doc_screenshot("admin-confirm-reset")


@pytest.mark.usefixtures("clean_index")
def test_trash(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    package_factory: types.TestFactory,
    login: Any,
    locator: ElementLocator,
):
    """Test admin trash page."""
    package_factory(state="deleted")
    login(sysadmin["name"])
    page.goto("/ckan-admin/trash")
    doc_screenshot("admin-trash")
