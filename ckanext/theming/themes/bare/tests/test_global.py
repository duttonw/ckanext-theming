import fnmatch
from typing import Any, cast

import pytest
from ckanext.theming import reference
from playwright.sync_api import Page

import ckan.plugins.toolkit as tk
from ckan.types import FixtureApp, FixtureCkanConfig, TestFactory
from werkzeug.routing import Rule


@pytest.fixture
def source_data(
    user_factory: TestFactory,
    package_factory: TestFactory,
    group_factory: TestFactory,
    organization_factory: TestFactory,
    resource_factory: TestFactory,
    resource_view_factory: TestFactory,
    ckan_config: FixtureCkanConfig,
):
    source = reference.get_source()

    page_size = ckan_config["ckan.datasets_per_page"]
    users = user_factory.create_batch(page_size + 1)
    groups = group_factory.create_batch(page_size + 1, users=[{"name": users[0]["id"], "capacity": "member"}])
    organizations = organization_factory.create_batch(
        page_size + 1, users=[{"name": users[0]["id"], "capacity": "member"}]
    )
    packages = package_factory.create_batch(page_size + 1, owner_org=organizations[0]["id"])
    resources = resource_factory.create_batch(2, package_id=packages[0]["id"])
    views = resource_view_factory.create_batch(2, resource_id=resources[0]["id"])

    source.data.update(
        {
            "resource": resources[0],
            "package": packages[0],
            "resource_view": views[0],
            "group": groups[0],
            "organization": organizations[0],
            "user": users[0],
        }
    )
    return source


@pytest.mark.usefixtures("with_plugins", "clean_db", "clean_index")
class TestPages:
    def test_screenshots(  # noqa: PLR0913, C901
        self,
        page: Page,
        screenshot: Any,
        sysadmin: dict[str, Any],
        login: Any,
        app: FixtureApp,
        source_data: reference.Source,
    ):
        url_map = cast(dict[str, list[Rule]], app.flask_app.url_map._rules_by_endpoint)
        for name, rules in url_map.items():
            if any(fnmatch.fnmatch(name, pattern) for pattern in source_data.ignore):
                continue

            for rule in rules:
                if rule.methods and "GET" not in rule.methods:
                    continue

                for user in [sysadmin, ""]:
                    login(user)
                    params = reference.make_params(
                        name,
                        rule.arguments,
                        source_data,
                        rule.defaults or {},
                    )

                    url = tk.url_for(name, **params)
                    page.goto(url)
                    screenshot(name)
