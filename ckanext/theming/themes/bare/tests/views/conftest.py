import re

import pytest

from ckan import types


@pytest.fixture
def title_builder(ckan_config: types.FixtureCkanConfig):
    """Provides a function to build page titles based on CKAN configuration.

    Usage:
        def test_example(page: Page, title_builder):
            expected_title = title_builder("Section", "Page")
            assert page.title() == expected_title

    """
    delimiter = " " + ckan_config["ckan.template_title_delimiter"] + " "

    def builder(*parts: str, pattern: bool = False):
        value = delimiter.join(parts + (ckan_config["ckan.site_title"],))
        if pattern:
            value = re.compile(value)

        return value

    return builder
