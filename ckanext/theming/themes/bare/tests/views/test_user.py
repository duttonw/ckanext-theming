from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins")
class TestApiTokens:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the user API tokens page has the correct title."""
        login(user)
        page.goto(tk.url_for("user.api_tokens", id=user["name"]))
        expected = title_builder("API Tokens", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestDelete:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the user delete page has the correct title."""
        login(user)
        page.goto(tk.url_for("user.delete", id=user["name"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestEdit:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the user edit page has the correct title."""
        login(user)
        page.goto(tk.url_for("user.edit", id=user["name"]))
        expected = title_builder("Edit Profile", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestFollowers:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any, sysadmin: dict[str, Any]):
        """Test that the user followers page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("user.followers", id=user["name"]))
        expected = title_builder("Followers", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestIndex:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the user index page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("user.index"))
        expected = title_builder("All Users", "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestLoggedOutPage:
    def test_title(self, page: Page, title_builder: Any):
        """Test that the user logged out page has the correct title."""
        page.goto(tk.url_for("user.logged_out_page"))
        expected = title_builder("Logged Out", "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestLogin:
    def test_title(self, page: Page, title_builder: Any):
        """Test that the user login page has the correct title."""
        page.goto(tk.url_for("user.login"))
        expected = title_builder("Login", "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestRead:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any):
        """Test that the user read page has the correct title."""
        login(user)
        page.goto(tk.url_for("user.read", id=user["name"]))
        expected = title_builder(user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestReadGroups:
    def test_title(self, page: Page, login: Any, user: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the user read groups page has the correct title."""
        login(user)
        call_action("member_create", id=group["id"], object=user["id"], object_type="user", capacity="member")

        page.goto(tk.url_for("user.read_groups", id=user["name"]))
        expected = title_builder("Groups", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestReadOrganizations:
    def test_title(
        self, page: Page, login: Any, user: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the user read organizations page has the correct title."""
        login(user)
        call_action("member_create", id=organization["id"], object=user["id"], object_type="user", capacity="member")
        page.goto(tk.url_for("user.read_organizations", id=user["name"]))
        expected = title_builder("Organizations", user["fullname"], "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestRegister:
    def test_title(self, page: Page, title_builder: Any):
        """Test that the user register page has the correct title."""
        page.goto(tk.url_for("user.register"))
        expected = title_builder("Register", "Users")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestRequestReset:
    def test_title(self, page: Page, title_builder: Any):
        """Test that the user request reset page has the correct title."""
        page.goto(tk.url_for("user.request_reset"))
        expected = title_builder("Reset your password", "Users")
        expect(page).to_have_title(expected)
