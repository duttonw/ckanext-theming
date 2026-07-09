from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page

from ckan import types
from ckan.tests.helpers import call_action

from ckanext.theming.themes.bare.tests.conftest import ElementLocator


def test_index(
    doc_screenshot: Any,
    page: Page,
    group_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test group list page."""
    group_factory.create_batch(3)
    page.goto("/group")
    doc_screenshot("group-index")

    page.goto("/group?q=nonexistent")
    doc_screenshot("group-index-search-empty")


@pytest.mark.usefixtures("clean_index")
def test_read(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    package_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test group read page."""
    package_factory.create_batch(3, groups=[{"id": group["id"]}])

    page.goto("/group/" + group["name"])
    doc_screenshot("group-read")


def test_about(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
):
    """Test group about page."""
    page.goto("/group/about/" + group["name"])
    doc_screenshot("group-about")


def test_new(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    login: Any,
    faker: Faker,
):
    """Test group creation page."""
    login(sysadmin["name"])
    page.goto("/group/new")
    page.fill("input[name='title']", faker.sentence())
    page.fill("textarea[name='description']", faker.paragraph())
    doc_screenshot("group-new-form")


def test_edit(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group edit page."""
    login(sysadmin["name"])
    page.goto("/group/edit/" + group["name"])
    doc_screenshot("group-edit-form")


def test_confirm_delete(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group delete confirmation page."""
    login(sysadmin["name"])
    page.goto("/group/delete/" + group["name"])
    doc_screenshot("group-confirm-delete")


def test_members(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    user: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group members page."""
    call_action("group_member_create", {"user": sysadmin["name"]}, id=group["id"], username=user["name"], role="member")

    page.goto("/group/members/" + group["name"])
    doc_screenshot("group-members")


def test_member_new(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group add member page."""
    login(sysadmin["name"])
    page.goto("/group/member_new/" + group["name"])
    doc_screenshot("group-member-new")


def test_manage_members(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    user: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group manage members page."""
    call_action("group_member_create", {"user": sysadmin["name"]}, id=group["id"], username=user["name"], role="member")

    login(sysadmin["name"])
    page.goto("/group/manage_members/" + group["name"])
    doc_screenshot("group-manage-members")


def test_confirm_delete_member(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    user: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group delete member confirmation page."""
    call_action("group_member_create", {"user": sysadmin["name"]}, id=group["id"], username=user["name"], role="member")

    login(sysadmin["name"])
    page.goto("/group/member_delete/" + group["name"] + "?user=" + sysadmin["name"])
    doc_screenshot("group-confirm-delete-member")


def test_admins(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
):
    """Test group administrators page."""
    page.goto("/group/admins/" + group["name"])
    doc_screenshot("group-admins")


def test_activity(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    faker: Faker,
):
    """Test group activity stream page."""
    login(sysadmin["name"])
    call_action("group_patch", {"user": sysadmin["name"]}, id=group["id"], title=faker.sentence())
    call_action("group_patch", {"user": sysadmin["name"]}, id=group["id"], description=faker.paragraph())

    page.goto("/group/activity/" + group["name"])
    doc_screenshot("group-activity")


def test_followers(
    doc_screenshot: Any,
    page: Page,
    group: dict[str, Any],
    user_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test group followers page."""
    login(sysadmin["name"])

    for user in user_factory.create_batch(3):
        call_action("follow_group", {"user": user["name"]}, id=group["id"])

    page.goto("/group/followers/" + group["name"])
    doc_screenshot("group-followers")
