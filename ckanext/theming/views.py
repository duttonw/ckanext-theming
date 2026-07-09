import os
from typing import Any

from flask import Blueprint, current_app

import ckan.plugins.toolkit as tk

from ckanext.theming.lib import get_active_theme

bp = Blueprint("theming", __name__, url_prefix="/theming")

__all__ = ["bp"]


@bp.route("/")
def index():
    return tk.render("theming/index.html")


@bp.route("/util/", defaults={"util": "attrs"})
@bp.route("/util/<util>")
def util(util: str):
    templates = current_app.jinja_env.list_templates(filter_func=lambda s: s.startswith("theming/utils/"))
    available_utils: list[str] = sorted([os.path.splitext(os.path.basename(u))[0] for u in templates])
    if util not in available_utils:
        return tk.abort(404, tk._("Utility function not found"))
    extra_vars = {"util": util, "available_utils": available_utils}
    return tk.render("theming/util.html", extra_vars)


@bp.route("/js/")
@bp.route("/js/<util>")
def js(util: str | None = None):
    templates = current_app.jinja_env.list_templates(filter_func=lambda s: s.startswith("theming/js/"))
    available_utils: list[str] = sorted([os.path.splitext(os.path.basename(u))[0] for u in templates])
    if util and util not in available_utils:
        return tk.abort(404, tk._("Utility function not found"))
    extra_vars = {"util": util, "available_utils": available_utils}

    return tk.render("theming/js.html", extra_vars)


@bp.route("/component/<component>/<example>", methods=["GET", "POST"])  # handle confirm_modal example
def component_example(component: str, example: str):
    extra_vars = {
        "component": component,
        "example": example,
    }
    if component == "list":
        _add_list_vars(extra_vars)
    return tk.render(
        "theming/component_example.html",
        extra_vars,
    )


@bp.route("/component/", defaults={"component": "accordion"})
@bp.route("/component/<component>", methods=["GET", "POST"])  # handle confirm_modal example
def component(component: str):
    templates = current_app.jinja_env.list_templates(
        filter_func=lambda s: s.startswith(("theming/components/", f"theming/examples/{component}/"))
    )

    available_components: list[str] = []
    examples: list[str] = []

    for tpl in templates:
        parts = tpl.split("/")
        if parts[1] == "components":
            available_components.append(os.path.splitext(parts[2])[0])
        elif parts[1] == "examples" and parts[2] == component:
            examples.append(os.path.splitext(parts[3])[0])

    if component not in available_components:
        return tk.abort(404, tk._("Component not found"))

    extra_vars = {
        "component": component,
        "available_components": available_components,
        "examples": examples,
        "ref": get_active_theme().component_reference(),
    }
    if component == "list":
        _add_list_vars(extra_vars)

    return tk.render("theming/component.html", extra_vars)


def _add_list_vars(extra_vars: dict[str, Any]):
    extra_vars["resources"] = tk.get_action("resource_search")({}, {"limit": 2, "query": "url:"})["results"]
    extra_vars["packages"] = tk.get_action("package_search")({}, {"rows": 2})["results"]
    extra_vars["users"] = tk.get_action("user_list")({}, {"limit": 2})[:2]
    extra_vars["organizations"] = tk.get_action("organization_list")({}, {"limit": 2, "all_fields": True})
    extra_vars["groups"] = tk.get_action("group_list")({}, {"limit": 2, "all_fields": True})
