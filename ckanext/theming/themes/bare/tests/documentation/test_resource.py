from typing import Any

from playwright.sync_api import Page

from ckan import types
from ckan.tests.helpers import call_action

from ckanext.theming.themes.bare.tests.conftest import ElementLocator


def test_read(
    doc_screenshot: Any,
    page: Page,
    resource: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test resource read page."""
    main = locator.locate_main_content()

    page.goto("/dataset/" + resource["package_id"] + "/resource/" + resource["id"])
    doc_screenshot("resource-read")

    info = page.get_by_role("button", name="additional info")
    info.click()
    info.scroll_into_view_if_needed()
    doc_screenshot("resource-read-info", clip=main.bounding_box())

    login(sysadmin["name"])
    page.reload()
    edit_btn = locator.locate_edit_resource_button()
    edit_btn.scroll_into_view_if_needed()

    doc_screenshot("resource-read-edit-button")


def test_new(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test resource create page."""
    login(sysadmin["name"])
    page.goto("/dataset/" + package["id"] + "/resource/new")
    doc_screenshot("resource-new")


def test_edit(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    resource: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
):
    """Test resource edit page."""
    login(sysadmin["name"])
    page.goto("/dataset/" + resource["package_id"] + "/resource/" + resource["id"] + "/edit")
    doc_screenshot("resource-edit")

    page.fill("input[name='name']", "")
    page.click("button[type='submit']")
    doc_screenshot("resource-edit-errors", full_page=False)


def test_confirm_delete(
    doc_screenshot: Any,
    page: Page,
    resource: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test resource delete confirmation page."""
    login(sysadmin["name"])
    page.goto("/dataset/" + resource["package_id"] + "/resource/" + resource["id"] + "/delete")
    doc_screenshot("dataset-confirm-delete-resource")


def test_views(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    resource: dict[str, Any],
    resource_view_factory: types.TestFactory,
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test resource views management page."""
    resource_view_factory.create_batch(2, resource_id=resource["id"])

    login(sysadmin["name"])
    page.goto("/dataset/" + package["name"] + "/resource/" + resource["id"] + "/views")
    doc_screenshot("resource-views")

    add_btn = page.get_by_text("New view")
    add_btn.scroll_into_view_if_needed()
    doc_screenshot("resource-views-add")


def test_dictionary(
    doc_screenshot: Any,
    page: Page,
    package: dict[str, Any],
    sysadmin: dict[str, Any],
    login: Any,
    locator: ElementLocator,
):
    """Test resource data dictionary page."""
    result = call_action(
        "datastore_create",
        {"user": sysadmin["name"]},
        resource={"package_id": package["id"]},
        fields=[{"id": "value", "type": "int"}],
    )
    login(sysadmin["name"])
    page.goto("/dataset/" + package["name"] + "/dictionary/" + result["resource_id"])
    doc_screenshot("resource-dictionary")
