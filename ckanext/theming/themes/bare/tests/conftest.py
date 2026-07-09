from pathlib import Path
from typing import Any

import pytest
from flask_login import encode_cookie  # pyright: ignore[reportUnknownVariableType]
from playwright.sync_api import BrowserContext, Page

from ckan import types

_here = Path(__file__).parent


@pytest.fixture
def clean_db(reset_db: Any, migrate_db_for: Any):
    reset_db()
    migrate_db_for("activity")


@pytest.fixture
def browser_context_args(browser_context_args: dict[str, Any], ckan_config: dict[str, Any]):
    """Modify playwright's standard configuration of browser's context."""
    browser_context_args["base_url"] = ckan_config["ckan.site_url"]
    return browser_context_args


@pytest.fixture
def token_login(api_token_factory: Any, page: Page):
    """Provides a function for authentication using API token.

    Usage:
        def test_example(page: Page, token_login):
            token_login("myuser")

    This will set the Authorization header for subsequent requests made by the page. To
    log out, call token_login with `None` or empty string, e.g., `token_login(None)`.
    """

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        token: str = api_token_factory(user=user)["token"] if user else ""

        _page.set_extra_http_headers({"Authorization": token})

    return authenticator


@pytest.fixture
def login(page: Page, context: BrowserContext, ckan_config: types.FixtureCkanConfig, with_request_context: Any):
    """Provides a function for authentication by setting the remember cookie.

    Usage:
        def test_example(page: Page, login):
            login("testuser")
            page.goto("http://example.com/protected")

    This will set the remember cookie for 'testuser', allowing access to protected pages. To
    log out, call login with `None` or empty string, e.g., `login(None)`.
    """

    def authenticator(user: str | dict[str, Any], _page: Page | None = None):
        if _page is None:
            _page = page

        if isinstance(user, dict):
            user = user["name"]

        key = ckan_config["REMEMBER_COOKIE_NAME"]
        url = ckan_config["ckan.site_url"]

        if user:
            context.clear_cookies()
            context.add_cookies([{"name": key, "value": encode_cookie(user), "url": url}])
        else:
            context.clear_cookies()

    return authenticator


@pytest.fixture
def screenshots_dir():
    return _here / ".." / ".test-screenshots"


@pytest.fixture
def screenshot(page: Page, request: pytest.FixtureRequest, screenshots_dir: Path):
    """Fixture to take screenshots during a test.

    Usage:
        def test_example(page: Page, screenshot):
            page.goto("http://example.com")
            screenshot("homepage")

    This will save a screenshot to 'screenshots/{test_name}__0001_homepage.jpeg'. Each
    subsequent call to screenshot within the same test will increment the step number.
    """
    step = 1

    def func(name: str, _page: Page | None = None, /, **kwargs: Any):
        """Takes a screenshot and saves it to the test-results directory."""
        nonlocal step
        node = request.node  # pyright: ignore[reportUnknownVariableType]
        if _page is None:
            _page = page

        prefix: str = node.originalname[5:]  # pyright: ignore[reportUnknownVariableType]
        if "path" not in kwargs:
            kwargs["path"] = f"{screenshots_dir}/{prefix}__{step:04d}_{name}.jpeg"
        step += 1
        kwargs.setdefault("full_page", True)
        return _page.screenshot(**kwargs)

    return func


class ElementLocator:
    page: Page

    def __init__(self, page: Page):
        self.page = page

    def locate_main_content(self):
        """Locate the main block element, which typically contains the primary content of the page."""
        return self.page.locator("#main")

    def locate_sidebar(self):
        """Locate the secondary block element, which typically contains side content or navigation."""
        return self.page.locator("#sidebar")

    def locate_breadcrumbs(self):
        """Locate the breadcrumbs element."""
        return self.page.locator("nav[aria-label='Breadcrumb']")

    def locate_add_dataset_button(self):
        """Locate the "Add dataset" button."""
        return self.page.get_by_role("link", name="Add dataset")

    def locate_edit_dataset_button(self):
        """Locate the "Edit dataset" button."""
        return self.page.get_by_role("link", name="Manage")

    def locate_edit_resource_button(self):
        """Locate the 'Edit' button on resource page."""
        return self.page.get_by_role("link", name="Edit")

    def locate_follow_button(self):
        """Locate the "Follow" button, which is typically used to follow a dataset or user for updates."""
        follow = self.page.get_by_role("button", name="Follow")
        unfollow = self.page.get_by_role("button", name="Unfollow")
        return follow.or_(unfollow)

    def locate_add_organization_button(self):
        """Locate the 'Add Organization' button."""
        return self.page.get_by_role("link", name="Add Organization")

    def locate_edit_organization_button(self):
        """Locate the 'Edit' button on organization page."""
        return self.page.get_by_role("link", name="Edit")

    def locate_add_group_button(self):
        """Locate the 'Add Group' button."""
        return self.page.get_by_role("link", name="Add Group")

    def locate_edit_group_button(self):
        """Locate the 'Edit' button on group page."""
        return self.page.get_by_role("link", name="Edit")

    def locate_edit_user_button(self):
        """Locate the 'Edit' button on user profile page."""
        return self.page.get_by_role("link", name="Edit")


@pytest.fixture
def locator(page: Page):
    return ElementLocator(page)
