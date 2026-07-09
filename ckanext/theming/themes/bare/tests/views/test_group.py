from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins")
class TestGroupAbout:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group about page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.about", id=group["id"]))
        expected = title_builder("About", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupAdmins:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group admins page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.admins", id=group["id"]))
        expected = title_builder("Administrators", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupDelete:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group delete page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.delete", id=group["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupEdit:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group edit page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.edit", id=group["id"]))
        expected = title_builder("Edit", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupFollowers:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group followers page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.followers", id=group["id"]))
        expected = title_builder("Followers", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupIndex:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the group index page has the correct title."""
        login(sysadmin)

        page.goto(tk.url_for("group.index"))
        expected = title_builder("Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupManageMembers:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group manage members page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.manage_members", id=group["id"]))
        expected = title_builder("Members", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupMemberDelete:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        group: dict[str, Any],
        user: dict[str, Any],
    ):
        """Test that the group member delete page has the correct title."""
        login(sysadmin)
        call_action("member_create", id=group["id"], object=user["id"], object_type="user", capacity="member")
        page.goto(tk.url_for("group.member_delete", id=group["id"], user=user["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupMemberNew:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group member new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.member_new", id=group["id"]))
        expected = title_builder("Add Member", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupMembers:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group members page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.members", id=group["id"]))
        expected = title_builder("Members", group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupNew:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the group new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.new"))
        expected = title_builder("Create a Group", "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroupRead:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, group: dict[str, Any]):
        """Test that the group read page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("group.read", id=group["id"]))
        expected = title_builder(group["title"], "Groups")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationAbout:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization about page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.about", id=organization["id"]))
        expected = title_builder("About", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationAdmins:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization admins page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.admins", id=organization["id"]))
        expected = title_builder("Administrators", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationDelete:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization delete page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.delete", id=organization["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationEdit:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization edit page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.edit", id=organization["id"]))
        expected = title_builder("Edit", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationFollowers:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization followers page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.followers", id=organization["id"]))
        expected = title_builder("Followers", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationIndex:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the organization index page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.index"))
        expected = title_builder("Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationManageMembers:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization manage members page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.manage_members", id=organization["id"]))
        expected = title_builder("Members", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationMemberDelete:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        organization: dict[str, Any],
        user: dict[str, Any],
    ):
        """Test that the organization member delete page has the correct title."""
        login(sysadmin)
        call_action("member_create", id=organization["id"], object=user["id"], object_type="user", capacity="member")
        page.goto(tk.url_for("organization.member_delete", id=organization["id"], user=user["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationMemberNew:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization member new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.member_new", id=organization["id"]))
        expected = title_builder("Add Member", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationMembers:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization members page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.members", id=organization["id"]))
        expected = title_builder("Members", organization["title"], "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationNew:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the organization new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.new"))
        expected = title_builder("Create an Organization", "Organizations")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestOrganizationRead:
    def test_title(
        self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, organization: dict[str, Any]
    ):
        """Test that the organization read page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("organization.read", id=organization["id"]))
        expected = title_builder(organization["title"], "Organizations")
        expect(page).to_have_title(expected)
