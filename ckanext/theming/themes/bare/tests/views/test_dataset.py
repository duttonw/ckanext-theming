from typing import Any

import pytest
from playwright.sync_api import Page, expect

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action


@pytest.mark.usefixtures("with_plugins")
class TestCollaboratorDelete:
    def test_title(
        self,
        page: Page,
        login: Any,
        sysadmin: dict[str, Any],
        title_builder: Any,
        package: dict[str, Any],
        user: dict[str, Any],
    ):
        """Test that various dataset-related pages have the correct title."""
        call_action("package_collaborator_create", id=package["id"], user_id=user["id"], capacity="member")
        login(sysadmin)
        page.goto(tk.url_for("dataset.collaborator_delete", id=package["id"], user_id=user["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestCollaboratorsRead:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the collaborators read page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.collaborators_read", id=package["id"]))
        expected = title_builder("Collaborators", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestDelete:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the dataset delete page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.delete", id=package["id"]))
        expected = title_builder("Confirm Delete")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestEdit:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the dataset edit page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.edit", id=package["id"]))
        expected = title_builder("Edit", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestFollowers:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the dataset followers page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.followers", id=package["id"]))
        expected = title_builder("Followers", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestGroups:
    def test_title(self, page: Page, title_builder: Any, package: dict[str, Any]):
        """Test that the dataset groups page has the correct title."""
        page.goto(tk.url_for("dataset.groups", id=package["id"]))
        expected = title_builder("Groups", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestNew:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any):
        """Test that the dataset new page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.new"))
        expected = title_builder("Create Dataset", "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestNewCollaborator:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the dataset new collaborator page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.new_collaborator", id=package["id"]))
        expected = title_builder("Add Collaborator", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestRead:
    def test_title(self, page: Page, title_builder: Any, package: dict[str, Any]):
        """Test that the dataset read page has the correct title."""
        page.goto(tk.url_for("dataset.read", id=package["id"]))
        expected = title_builder(package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestResources:
    def test_title(self, page: Page, login: Any, sysadmin: dict[str, Any], title_builder: Any, package: dict[str, Any]):
        """Test that the dataset resources page has the correct title."""
        login(sysadmin)
        page.goto(tk.url_for("dataset.resources", id=package["id"]))
        expected = title_builder("Resources", package["title"], "Datasets")
        expect(page).to_have_title(expected)


@pytest.mark.usefixtures("with_plugins")
class TestSearch:
    def test_title(self, page: Page, title_builder: Any):
        """Test that the dataset search page has the correct title."""
        page.goto(tk.url_for("dataset.search"))
        expected = title_builder("Datasets")
        expect(page).to_have_title(expected)
