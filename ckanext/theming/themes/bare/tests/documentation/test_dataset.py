from typing import Any

import pytest
from faker import Faker
from playwright.sync_api import Page

from ckan import types
from ckan.tests.helpers import call_action

from ckanext.theming.themes.bare.tests.conftest import ElementLocator


@pytest.mark.usefixtures("clean_index")
def test_search(
    doc_screenshot: Any,
    page: Page,
    package_factory: types.TestFactory,
    resource: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    package = package_factory.create_batch(3)[0]
    page.goto("/dataset")
    doc_screenshot("dataset-search-normal")

    page.goto("/dataset?q=" + package["title"])
    doc_screenshot("dataset-search-query-applied")

    page.goto("/dataset?res_format=" + resource["format"])
    doc_screenshot("dataset-search-facet-applied")

    login(sysadmin["name"])
    page.goto("/dataset")
    button = locator.locate_add_dataset_button()
    button.scroll_into_view_if_needed()
    doc_screenshot("dataset-search-add-button")


def test_read(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    resource_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    main = locator.locate_main_content()
    sidebar = locator.locate_sidebar()

    resource_factory.create_batch(3, package_id=package["id"])
    page.goto("/dataset/" + package["name"])
    doc_screenshot("dataset-read-normal")

    resources = page.get_by_role("button", name="resources")
    resources.scroll_into_view_if_needed()
    resources.click()
    doc_screenshot("dataset-read-resources", clip=main.bounding_box())

    page.reload()

    info = page.get_by_role("button", name="additional details")
    info.scroll_into_view_if_needed()
    info.click()
    doc_screenshot("dataset-read-additional-info", clip=main.bounding_box())

    login(sysadmin["name"])
    page.reload()
    button = locator.locate_edit_dataset_button()
    button.scroll_into_view_if_needed()
    doc_screenshot("dataset-read-manage-button", clip=main.bounding_box())

    login(sysadmin["name"])
    page.reload()

    button = locator.locate_follow_button()
    button.scroll_into_view_if_needed()

    doc_screenshot("dataset-read-follow-button", clip=sidebar.bounding_box())

    with page.expect_request("/dataset/follow/" + package["id"]):
        button.click()

    doc_screenshot("dataset-read-unfollow-button", clip=sidebar.bounding_box())


def test_new(
    doc_screenshot: Any,
    page: Page,
    sysadmin: dict[str, Any],
    login: Any,
    faker: Faker,
    organization: dict[str, Any],
):
    """Test dataset creation page."""
    login(sysadmin["name"])
    page.goto("/dataset/new")
    page.fill("input[name='title']", faker.sentence())
    page.fill("textarea[name='notes']", faker.paragraph())
    doc_screenshot("dataset-new-form")


def test_edit(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test dataset edit page."""
    login(sysadmin["name"])
    page.goto("/dataset/edit/" + package["name"])
    doc_screenshot("dataset-edit-form")

    # Show validation errors
    page.fill("input[name='name']", "*#$%")

    page.get_by_role("button", name="update dataset").click()
    doc_screenshot("dataset-edit-errors", full_page=False)


def test_activity(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    faker: Faker,
):
    """Test dataset activity stream page."""
    login(sysadmin["name"])
    call_action("package_patch", {"user": sysadmin["name"]}, id=package["id"], title=faker.sentence())
    call_action("package_patch", {"user": sysadmin["name"]}, id=package["id"], notes=faker.paragraph())
    page.goto("/dataset/activity/" + package["name"])
    doc_screenshot("dataset-activity-stream")


def test_followers(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    user_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test dataset followers page."""
    login(sysadmin["name"])
    page.goto("/dataset/followers/" + package["name"])
    doc_screenshot("dataset-followers-empty")

    for user in user_factory.create_batch(3):
        call_action("follow_dataset", {"user": user["name"]}, id=package["id"])

    page.reload()
    doc_screenshot("dataset-followers-with-followers")


def test_groups(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    group_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test dataset groups page."""
    group_factory.create_batch(3)

    login(sysadmin["name"])
    page.goto("/dataset/groups/" + package["name"])
    doc_screenshot("dataset-groups-empty")

    button = page.get_by_role("button", name="add to group")
    button.click()
    button.click()
    doc_screenshot("dataset-groups")


def test_resources_manage(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    resource_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test dataset resources management page."""
    resources = resource_factory.create_batch(3, package_id=package["id"])

    login(sysadmin["name"])
    page.goto("/dataset/resources/" + package["name"])
    doc_screenshot("dataset-resources-list")

    main = locator.locate_main_content()
    first = main.get_by_text(resources[0]["name"])
    last = main.get_by_text(resources[-1]["name"])

    first.hover()
    page.mouse.down()
    page.mouse.move(
        first.bounding_box()["x"],
        last.bounding_box()["y"],
    )
    doc_screenshot("dataset-resources-reorder")


def test_confirm_delete(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test dataset delete confirmation page."""
    login(sysadmin["name"])
    page.goto("/dataset/delete/" + package["name"])
    doc_screenshot("dataset-confirm-delete")


def test_collaborators(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    user_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test dataset collaborators page."""
    login(sysadmin["name"])
    page.goto("/dataset/collaborators/" + package["name"])
    doc_screenshot("dataset-collaborators-empty")

    for user in user_factory.create_batch(3):
        call_action("package_collaborator_create", id=package["id"], user_id=user["id"], capacity="member")

    page.reload()
    doc_screenshot("dataset-collaborators-with-collaborator")
