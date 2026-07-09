from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan import types


@pytest.mark.usefixtures("with_plugins")
class TestResourceDelete:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, resource: dict[str, Any]
    ):
        """Test that the resource delete page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("resource.delete", id=resource["package_id"], resource_id=resource["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResourceEdit:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        resource_factory: types.TestFactory,
        package: dict[str, Any],
    ):
        """Test that the resource edit page has the correct title."""
        login(sysadmin)
        resource = resource_factory(package_id=package["id"])
        page.goto(tk.url_for("resource.edit", id=resource["package_id"], resource_id=resource["id"]))
        expected = title_builder("Edit", resource["name"], package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResourceNew:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the resource new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("resource.new", id=package["id"]))
        expected = title_builder("Add data to the dataset", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResourceRead:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        resource_factory: types.TestFactory,
        package: dict[str, Any],
    ):
        """Test that the resource read page has the correct title."""
        login(sysadmin)
        resource = resource_factory(package_id=package["id"])
        page.goto(tk.url_for("resource.read", id=resource["package_id"], resource_id=resource["id"]))
        expected = title_builder(resource["name"], package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResourceViews:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        resource_factory: types.TestFactory,
        package: dict[str, Any],
    ):
        """Test that the resource views page has the correct title."""
        login(sysadmin)
        resource = resource_factory(package_id=package["id"])
        page.goto(tk.url_for("resource.views", id=resource["package_id"], resource_id=resource["id"]))
        expected = title_builder("View", resource["name"], package["title"], "Datasets")
        expect(page).to_have_title(expected)
