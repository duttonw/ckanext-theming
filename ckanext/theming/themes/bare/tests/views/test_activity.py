from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDashboard:
    def test_title(self, page: Page, title_builder: Any, user: dict[str, Any], login: Any):
        """Test that the dashboard title is correct."""
        login(user)
        page.goto(tk.url_for("activity.dashboard"))
        expected = title_builder("Dashboard", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestGroupActivity:
    def test_title(self, page: Page, title_builder: Any, group: dict[str, Any]):
        """Test that the group activity title is correct."""
        page.goto(tk.url_for("activity.group_activity", id=group["name"]))
        expected = title_builder("Activity Stream", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestGroupChanges:
    def test_title(
        self, page: Page, login: Any, title_builder: Any, group: dict[str, Any], faker: Faker, sysadmin: dict[str, Any]
    ):
        """Test that the group changes title is correct."""
        login(sysadmin)
        new_name = faker.name()
        call_action("group_patch", {"user": sysadmin["name"]}, id=group["id"], title=new_name)
        activity_id = call_action("group_activity_list", id=group["id"])[0]["id"]
        page.goto(tk.url_for("activity.group_changes", id=activity_id))
        expected = title_builder("Changes", new_name, "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestOrganizationActivity:
    def test_title(self, page: Page, title_builder: Any, organization: dict[str, Any]):
        """Test that the organization activity title is correct."""
        page.goto(tk.url_for("activity.organization_activity", id=organization["name"]))
        expected = title_builder("Activity Stream", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestOrganizationChanges:
    def test_title(
        self,
        page: Page,
        login: Any,
        title_builder: Any,
        organization: dict[str, Any],
        faker: Faker,
        sysadmin: dict[str, Any],
    ):
        """Test that the organization changes title is correct."""
        login(sysadmin)
        new_name = faker.name()
        call_action("organization_patch", {"user": sysadmin["name"]}, id=organization["id"], title=new_name)
        activity_id = call_action("organization_activity_list", id=organization["id"])[0]["id"]
        page.goto(tk.url_for("activity.organization_changes", id=activity_id))
        expected = title_builder("Changes", new_name, "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestPackageActivity:
    def test_title(self, page: Page, title_builder: Any, package: dict[str, Any]):
        """Test that the package activity title is correct."""
        page.goto(tk.url_for("activity.package_activity", id=package["name"]))
        expected = title_builder("Activity Stream", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestPackageChanges:
    def test_title(
        self,
        page: Page,
        login: Any,
        title_builder: Any,
        package: dict[str, Any],
        faker: Faker,
        sysadmin: dict[str, Any],
    ):
        """Test that the organization changes title is correct."""
        login(sysadmin)
        new_name = faker.name()
        call_action("package_patch", {"user": sysadmin["name"]}, id=package["id"], title=new_name)
        activity_id = call_action("package_activity_list", id=package["id"])[0]["id"]
        page.goto(tk.url_for("activity.package_changes", id=activity_id))
        expected = title_builder("Changes", new_name, "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.ckan_config("ckan.plugins", ["activity"])
@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestUserActivity:
    def test_title(self, page: Page, title_builder: Any, user: dict[str, Any], login: Any):
        """Test that the user activity title is correct."""
        login(user)
        page.goto(tk.url_for("activity.user_activity", id=user["name"]))

        expected = title_builder("Activity Stream", user["fullname"], "Users")
        expect(page).to_have_title(expected)
