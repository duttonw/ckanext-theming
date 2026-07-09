import ckan.plugins.toolkit as tk

THEME = "ckan.ui.theme"
ENABLE_VIEWS = "ckan.ui.enable_theming_views"


def theme() -> str:
    """Returns the name of the active theme, or empty string if no theme is active."""
    theme = tk.config.get(THEME)
    if not theme:
        if tk.config.get("ckan.base_templates_folder") == "templates-midnight-blue":
            theme = "midnight-blue-polyfill"
        else:
            theme = "classic-polyfill"

    return theme


def enable_views() -> bool:
    """Returns True if the theming views are enabled, False otherwise."""
    return tk.asbool(tk.config.get(ENABLE_VIEWS))
