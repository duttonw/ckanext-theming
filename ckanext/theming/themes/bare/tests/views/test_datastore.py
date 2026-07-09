from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins")
class TestDictionary:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the datastore dictionary page has the correct title."""
        login(sysadmin)
        result = call_action("datastore_create", {"user": sysadmin["name"]}, resource={"package_id": package["id"]})

        page.goto(tk.url_for("datastore.dictionary", id=package["id"], resource_id=result["resource_id"]))
        expected = title_builder("Data Dictionary", ".*", package["title"], "Datasets", pattern=True)
        expect(page).to_have_title(expected)
