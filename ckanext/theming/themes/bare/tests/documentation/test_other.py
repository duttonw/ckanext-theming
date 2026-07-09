from typing import Any

import pytest
from playwright.sync_api import Page

from ckan import types


def test_error_404(
    doc_screenshot: Any,
    page: Page,
):
    """Test 404 error page."""
    page.goto("/nonexistent-page-12345")
    doc_screenshot("error-404")


def test_error_403(
    doc_screenshot: Any,
    page: Page,
):
    """Test 403 error page."""
    page.goto("/ckan-admin")
    doc_screenshot("error-403")


@pytest.mark.usefixtures("clean_index")
def test_stats(
    doc_screenshot: Any,
    page: Page,
    package_factory: types.TestFactory,
    user_factory: types.TestFactory,
    organization_factory: types.TestFactory,
    group_factory: types.TestFactory,
):
    """Test statistics page."""
    package_factory.create_batch(5)
    user_factory.create_batch(3)
    organization_factory.create_batch(2)
    group_factory.create_batch(2)

    page.goto("/stats")
    doc_screenshot("stats")
