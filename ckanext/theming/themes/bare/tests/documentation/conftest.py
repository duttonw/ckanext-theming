from pathlib import Path
from typing import Any

import pytest

_here = Path(__file__).parent


@pytest.fixture
def screenshots_dir():
    return _here / ".." / ".." / "docs" / "screenshots"


@pytest.fixture
def doc_screenshot(screenshot: Any, screenshots_dir: Any):
    def fixture(name: str, *args: Any, **kwargs: Any):
        kwargs.setdefault("path", f"{screenshots_dir}/{name}.jpeg")
        return screenshot(name, *args, **kwargs)

    return fixture
