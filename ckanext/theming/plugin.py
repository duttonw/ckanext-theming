import logging
from typing import Any, cast

from flask import Blueprint
from jinja2 import pass_context
from jinja2.runtime import Context
from typing_extensions import override

import ckan.plugins.toolkit as tk
from ckan import plugins as p
from ckan import types

from . import config as cfg
from . import lib, views
from .interfaces import ITheme
from .themes import make_bare_theme, make_classic_polyfill, make_mb_polyfill

log = logging.getLogger(__name__)


class ThemingMixin(ITheme, p.IConfigurer, p.IMiddleware):
    @override
    def update_config(self, config: Any):
        if not _is_main_implementation(self, config):
            return

        tk.add_resource("assets", "theming")
        tk.add_template_directory(config, "templates")

        if theme := lib.get_active_theme():
            lib.enable_theme(theme, config)

    @override
    def register_themes(self) -> list[lib.Theme]:
        if not _is_main_implementation(self, tk.config):
            return []

        return [make_classic_polyfill(), make_mb_polyfill()]

    @override
    def get_default_theme_ui_sources(self) -> list[str]:
        if not _is_main_implementation(self, tk.config):
            return []

        return ["macros/theming_default_ui.html"]

    @override
    def make_middleware(self, app: types.CKANApp, config: Any) -> types.CKANApp:
        if not _is_main_implementation(self, tk.config):
            return app

        if hasattr(app, "jinja_env"):
            app.jinja_env.globals.update({"ui": cast(Any, lib.ui)})
        else:
            log.warning("Cannot initialize UI in the non-flask application")
        return app


def _is_main_implementation(self: ThemingMixin, config: types.CKANConfig):
    """Check if the current plugin instance is the main implementation of ThemingMixin.

    The main implementations is either the theming plugin itself it it's
    loaded, or the last loaded plugin that extends ThemingMixin.
    """
    if p.plugin_loaded("theming"):
        return self.name == "theming"

    for name in reversed(config["ckan.plugins"]):
        plugin = p.get_plugin(name)
        if not isinstance(plugin, ThemingMixin):
            continue
        return plugin == self


@tk.blanket.cli
@tk.blanket.config_declarations
class ThemingPlugin(ThemingMixin, p.IBlueprint, p.SingletonPlugin):
    @override
    def register_themes(self):
        return super().register_themes() + [make_bare_theme()]

    @override
    def make_middleware(self, app: types.CKANApp, config: Any) -> types.CKANApp:
        super().make_middleware(app, config)

        if hasattr(app, "jinja_env"):
            app.jinja_env.add_extension("jinja2.ext.debug")
            app.jinja_env.filters["render_string"] = _render_string_filter  # pyright: ignore[reportArgumentType]
        return app

    @override
    def get_blueprint(self) -> list[Blueprint]:
        if cfg.enable_views():
            return [views.bp]
        return []


@pass_context
def _render_string_filter(context: Context, source_string: str, scope: dict[str, Any] | None = None):
    """Evaluates a raw string as a live Jinja template using the active context."""
    # Convert context to a flat dictionary
    ctx_dict = context.get_all()
    if scope:
        ctx_dict.update(scope)
    # Use the environment to compile and render the string
    return context.environment.from_string(source_string).render(**ctx_dict)
