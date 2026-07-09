from collections.abc import Callable
from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types


def get_helpers() -> dict[str, Callable[..., Any]]:
    result: dict[str, Callable[..., Any]] = {}
    scope = globals()
    for name in __all__:
        if name not in tk.h:
            result[name] = scope[name]

    return result


__all__ = [
    "get_recent_datasets",
    "get_dataset_count",
    "default_collapse_facets",
    "currently_active_facet",
]


def get_dataset_count() -> dict[str, int]:
    return tk.get_action("package_search")({}, {"rows": 0})["count"]


def get_recent_datasets(count: int = 1) -> list[dict[str, Any]]:
    """Returns a list of recently modified/created datasets."""
    context = types.Context(ignore_auth=True, for_view=True)
    data_dict = {"rows": count, "sort": "metadata_modified desc"}
    recently_updated_datasets = tk.get_action("package_search")(context, data_dict)
    return recently_updated_datasets["results"]


def default_collapse_facets():
    """Returns config option for `ckan.default_collapse_facets`.

    If true, the facets in the secondary will be collapsed by default.
    If false, the facets will all be open, unless closed by the user.
    Default is false
    """
    return tk.asbool(tk.config.get("ckan.default_collapse_facets", False))


def currently_active_facet(facet: str) -> bool:
    params_items = tk.request.args.keys()
    expanded_facet = "_" + facet + "_limit"
    return facet in params_items or expanded_facet in params_items
