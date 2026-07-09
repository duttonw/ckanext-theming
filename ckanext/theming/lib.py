"""Theme and UI classes for CKAN theming system.

A theme is a directory containing templates and static files, and
optionally extending a parent theme. A UI provides access to a set of
functions that can be used in templates for building the user interface.

Themes can be registered by CKAN plugins using the ITheme interface.

Example usage::

    from ckanext.theming import config as cfg
    theme = get_theme(cfg.theme())
    ui = theme.build_ui(app)
    btn = ui.link("Click me!", href="https://ckan.org")
"""

import dataclasses
import datetime
import logging
import os
import uuid
from collections import defaultdict
from collections.abc import Iterable, Iterator
from typing import Any, cast

from flask import current_app
from jinja2 import Undefined
from jinja2.runtime import Macro
from markupsafe import Markup
from typing_extensions import override
from werkzeug.local import LocalProxy

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import types
from ckan.exceptions import CkanConfigurationException
from ckan.lib.helpers import helper_functions as h

from . import config as cfg
from . import reference
from .base import UI, BaseTheme, BaseUtil, PElement
from .interfaces import ITheme

log = logging.getLogger(__name__)

NAMESPACE_UI = uuid.uuid5(uuid.NAMESPACE_OID, "ui")


class Util(BaseUtil):
    _storage_key: str = "ui_storage"
    _theme: 'Theme'
    _extra_class_attr: str = "_extra_class"
    _attr_groups: list[tuple[str, str]] = [
        ("aria", "aria-"),
        ("data", "data-"),
        ("on", "on"),
        ("hx", "hx-"),
    ]

    def _escape_attr_value(self, value: str) -> str:
        """Escape a string for safe inclusion in HTML attributes."""
        return value.replace("&", "&amp;").replace('"', "&quot;")

    @override
    def __init__(self, theme: 'Theme'):
        self._theme = theme

    @override
    def augment_attrs(
        self,
        kwargs: dict[str, Any],
        defaults: dict[str, Any] | None = None,
        /,
        key: str | None = "attrs",
        extra_class: str | None = None,
    ) -> dict[str, Any]:
        """Helper method to combine provided attributes with default attributes."""
        if defaults:
            data = kwargs.setdefault(key, {}) if key else kwargs
            # overwrite defaults with existing values
            defaults.update(data)

            # write augmented dictionary back to source
            data.update(defaults)

        if extra_class:
            cls = kwargs.get(self._extra_class_attr) or ""
            kwargs[self._extra_class_attr] = f"{cls} {extra_class}".lstrip()

        return kwargs

    @override
    def attrs(self, kwargs: dict[str, Any], defaults: dict[str, Any] | None = None) -> str:
        """Helper method to render HTML attributes from a dictionary.

        This method takes a dictionary of attributes and their values, and an
        optional dictionary of default attributes. It combines the two
        dictionaries, giving precedence to the provided attributes, and renders
        them as a string of HTML attributes.

        If kwargs contain an "_extra_class" key, its value is appended to the
        "class" attribute. In this way additional classes can be added to the
        list of default classes provided by component. Example:

            # definition
            {% macro button(content) %}
              {% set defaults = {"class": "btn btn-primary"} %}
              <button {{ ui.attrs(kwargs, defaults) }}>{{ content }}</button>
            {% endmacro %}

            # call
            {{ ui.button("Click me!", _extra_class="custom-button-class") }}

            # result
            <button class="btn btn-primary custom-button-class">Click me!</button>

        :param kwargs: A dictionary of attributes to render.
        :param defaults: An optional dictionary of default attributes.
        :return: A Markup object containing the rendered HTML attributes.

        """
        kwargs = self.augment_attrs(kwargs, defaults)
        if not kwargs:
            return ""

        attrs = kwargs.setdefault("attrs", {}).copy()
        # skip the loop if attrs is the only item in the dictionary
        if len(kwargs) > 1:
            for key, prefix in self._attr_groups:
                group = kwargs.get(key, {})
                if not group:
                    continue

                for k, v in group.items():
                    attrs[f"{prefix}{k}"] = v

            if extra_class := kwargs.get(self._extra_class_attr):
                cls = attrs.get("class", "")
                attrs["class"] = f"{cls} {extra_class}"

        parts = [
            k if v is None else f'{k}="{self._escape_attr_value(str(v))}"'
            for k, v in attrs.items()
            if not isinstance(v, Undefined)
        ]

        return h.literal(" ".join(parts)) if parts else ""

    @override
    def tag(self, content: str, tag: str, is_void: bool = False, /, **kwargs: Any) -> str:
        """Helper method to render an HTML tag with the specified content, tag name, and attributes.

        Empty tag name will render content without any wrapper - this can be
        used to apply wrapper conditionally. For example, `ui.util.tag(content,
        tag if condition else "")` will render `content` wrapped in `tag` if
        `condition` is True, and just `content` without wrapper otherwise.

        If `is_void` is True, renders a void tag (e.g., <img />) instead of a
        normal tag(e.g., <img></img>).

        :param content: The content to be enclosed within the tag.
        :param tag: The name of the HTML tag to render.
        :param is_void: If True, renders a void tag (e.g., <img />). Defaults to False.
        :param kwargs: Additional attributes for the tag.
        :return: A Markup object containing the rendered HTML tag.

        """
        if not tag:
            return content

        attrs = self.attrs(kwargs)
        if is_void:
            return h.literal(f"<{tag} {attrs}/>")

        return h.literal(f"<{tag} {attrs}>{content}</{tag}>")

    @override
    def call(self, el: PElement, /, *args: Any, caller: Macro, **kwargs: Any) -> Markup:
        """Call an inline element as a block element.

        Allows passing complex content into an element using a Jinja2
        caller. For example, following simple macro does not contain `caller()`::

            {% macro button(content) %}
                <button>{{ content }}</button>
            {% endmacro %}

        As result, it cannot be called in form `{% call ui.button() %}` and
        rendering button with nested HTML turns into a verbose task. But using
        `ui.util.call`, `button` can be used with `call`::

            {% call ui.util.call(ui.button) %}
                <i class="icon"/>
                Click!
            {% endcall %}

        The content of the `call` block will be passed as a first argument into
        the target macro. Any other positional and named arguments of the
        `ui.util.call` will be redirected into `ui.button` as well.
        """
        if caller.catch_kwargs:
            log.error("Rename `kwargs` outside the call block and use alias instead")
            msg = "`kwargs` inside call block shadows outer `kwargs`"
            raise ValueError(msg)

        return el(caller(), *args, **kwargs)

    @override
    def map(self, el: PElement, items: Iterable[Any], /, *args: Any, **kwargs: Any) -> Markup:
        """Map an element over a collection of items.

        Renders the specified element for each item in the collection and
        concatenates the results.

        :param el: The element to render for each item.
        :param items: The collection of items.
        :param args: Positional arguments to pass to the element.
        :param kwargs: Named arguments to pass to the element.
        :return: A Markup object containing the concatenated results.
        """
        return Markup().join(el(item, *args, **kwargs) for item in items)

    @override
    def now(self, tz: datetime.timezone = datetime.timezone.utc) -> datetime.datetime:
        """Get the current UTC datetime.

        :param tz: Timezone for the returned datetime. Defaults to UTC.
        :return: Current datetime with the specified timezone.
        """
        return datetime.datetime.now(tz)

    @override
    def id(self, value: str | None = None, prefix: str = "id-"):
        """Generate a unique identifier.

        If `value` is provided, a UUID5 based on the value is generated,
        otherwise a random UUID4 is generated.

        Useful for generating unique HTML element IDs.

        :param value: Optional value to base the UUID5 on.
        :param prefix: Prefix to prepend to the identifier.
        :return: An identifier string.
        """
        result = uuid.uuid5(NAMESPACE_UI, value) if value else uuid.uuid4()
        return f"{prefix}{result.hex}"

    @override
    def keep_item(self, category: str, key: str, value: Any):
        """Keep an item in the UI storage under the specified category.

        This method allows storing arbitrary items in a per-request storage
        associated with the UI. Items can be retrieved later during the same
        request.

        :param category: The category under which to store the item.
        :param key: The key for the item.
        :param value: The item to store.
        """
        storage = tk.g.setdefault(self._storage_key, defaultdict(dict))
        storage[category][key] = value

    @override
    def pop_items(
        self, category: str, key: str | None = None, default: Any = None, /, keep: bool = False
    ) -> dict[str, Any] | Any:
        """Pop items from the UI storage under the specified category.

        :param category: The category from which to pop items.
        :param key: Optional key of the item to pop. If not provided, all items
                    under the category are popped.
        :param default: Default value to return if the key is not found.
        :param keep: If True, items will not be removed from storage after popping.
        :return: The popped item(s) from the UI storage.
        """
        storage = tk.g.setdefault(self._storage_key, defaultdict(dict))
        items = storage[category]
        if key:
            if keep:
                return items.get(key, default)
            return items.pop(key, default)

        if not keep:
            del storage[category]

        return items

    @override
    def icon(self, name: str) -> str:
        """Normalize icon name.

        Maps common icon names to their corresponding names in the theme's icon
        set. If no mapping exists, returns the original name. This allows using
        consistent icon names across different themes. For example, "search" is
        mapped to "magnifying-glass" if the theme does not have icon with ID
        `search`. Themes can override these mappings as needed.

        :param name: Common name of the icon.
        :return: The name of the corresponding icon provided by theme

        """
        theme = self._theme
        while True:
            if icon := theme.icon_map.get(name):
                return icon

            if theme.parent:
                theme = get_theme(theme.parent)
            else:
                return name


class MacroUI(UI):
    """A UI implementation that loads macros from a Jinja2 template.

    The template should define macros for each UI element. The default template
    is "macros/ui.html".

    :param source: The path to the Jinja2 template containing the macros.
    """

    util: BaseUtil
    __sources: list[str]
    _base_sources: list[str] = ["macros/ui.html"]
    _inv: dict[str, PElement]

    @override
    def __init__(self, app: types.CKANApp, theme: 'Theme', util: Util):
        self.util = util

        self._inv = {}
        if hasattr(app, "_wsgi_app"):
            app = cast(types.CKANApp, app._wsgi_app)  # pyright: ignore[reportAttributeAccessIssue]

        self.__env = app.jinja_env

        default: list[str] = []
        additional: list[str] = []
        for plugin in p.PluginImplementations(ITheme):
            default += plugin.get_default_theme_ui_sources()
            additional += plugin.get_additional_theme_ui_sources()

        self.__sources = default + self._base_sources + additional
        self._collect_macros()

    @override
    def __iter__(self) -> Iterator[str]:
        """Return an iterable of element names provided by this UI.

        :return: An iterable of element names.
        """
        return iter(self._inv)

    def _collect_macros(self):
        for tpl in (self.__env.get_template(source) for source in self.__sources):
            mod = tpl.module
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                component = getattr(mod, name)
                if name in self._inv:
                    component._theming_chain = self._inv[name]

                self._add_component(name, component)

    @override
    def _add_component(self, name: str, component: PElement):
        """Add a new component to the UI inventory.

        :param name: The name of the component.
        :param component: A callable that produces the component.
        """
        self._inv[name] = component

    def __getattr__(self, name: str):
        # reset macro cache at the beginning of the request in debug mode. This
        # allows to edit UI macros without restarting the server.
        if tk.config["debug"] and not getattr(tk.g, "_ui_compiled", False):
            for tpl in (self.__env.get_template(source) for source in self.__sources):
                tpl._module = tpl.make_module()  # pyright: ignore[reportPrivateUsage]

            self._inv.clear()
            self._collect_macros()
            tk.g._ui_compiled = True

        if name not in self._inv:
            raise AttributeError(name)

        return self._inv[name]


@dataclasses.dataclass
class Theme(BaseTheme):
    """Information about a theme.

    :param name: Name of the theme.
    :param path: Path to the theme directory.
    :param parent: Name of the parent theme, or None.
    :param template_folder: Subdirectory for templates.
    :param public_folder: Subdirectory for public static files.
    :param asset_folder: Subdirectory for asset files.
    :param ui_factory: Factory class for creating the UI instance.
    :param util_factory: Factory class for creating the Util instance.
    :param icon_map: Mapping of common icon names to theme-specific names.
    """

    name: str
    path: str | None
    parent: str | None = None

    template_folder: str = "templates"
    public_folder: str = "public"
    asset_folder: str = "assets"
    ui_factory: type[UI] = MacroUI
    util_factory: type[BaseUtil] = Util
    icon_map: dict[str, str] = dataclasses.field(default_factory=dict)

    @override
    def build_ui(self, app: types.CKANApp) -> UI:
        """Build a UI instance for this theme.

        :param app: The CKAN application instance.
        :return: A UI instance.
        """
        ui = self.ui_factory(app, self, self.util_factory(self))
        for plugin in p.PluginImplementations(ITheme):
            plugin.patch_theme_ui(self, ui)

        return ui

    @override
    def template_path(self):
        """Get the path to the theme's templates directory."""
        if self.path:
            return os.path.join(self.path, self.template_folder)

    @override
    def public_path(self):
        """Get the path to the theme's public directory."""
        if self.path:
            return os.path.join(self.path, self.public_folder)

    @override
    def asset_path(self):
        """Get the path to the theme's assets directory."""
        if self.path:
            return os.path.join(self.path, self.asset_folder)

    @override
    def component_reference(self) -> reference.Glossary[str, reference.Component]:
        theme = self
        chain: list[BaseTheme] = [theme]

        while theme.parent:
            theme = get_theme(theme.parent)
            chain.append(theme)

        ref = reference.components.clone()

        for theme in reversed(chain):
            if theme.path:
                source = os.path.join(theme.path, "components.yaml")
                if os.path.isfile(source):
                    for key, value in reference.parse_components(source).items():
                        ref[key] = value

        return ref


def get_theme(name: str):
    """Get theme by name.

    :raises KeyError: if theme not found
    """
    return _themes[name]


_themes: dict[str, BaseTheme] = {}


def _collect_themes() -> None:
    """Collect available themes from core and plugins."""
    # ckan_root = os.path.dirname(os.path.abspath(ckan.__file__))
    _themes.clear()
    for plugin in p.PluginImplementations(ITheme):
        _themes.update({theme.name: theme for theme in plugin.register_themes()})


def resolve_paths(theme: str | None) -> list[str]:
    """Resolve theme paths including parent themes.

    :raises KeyError: if the parent theme is not found
    """
    paths: list[str] = []
    while theme:
        info = get_theme(theme)
        if info.path:
            paths.append(info.path)
        theme = info.parent

    return paths


def get_active_theme():
    theme = cfg.theme()
    if not theme:
        if tk.config.get("ckan.base_templates_folder") == "templates-midnight-blue":
            theme = "midnight-blue-polyfill"
        else:
            theme = "classic-polyfill"

    if not _themes:
        _collect_themes()

    try:
        return get_theme(theme)
    except KeyError as err:
        msg = f"Active theme '{theme}' is not recognised."
        raise CkanConfigurationException(msg) from err


def enable_theme(theme: BaseTheme, config_: Any):
    """Enable the specified theme.

    This function updates the CKAN configuration to include template and
    static file directories from the specified theme and its parent themes.

    :param name: The name of the theme to switch to.
    :param config: The CKAN configuration dictionary.
    :raises CkanConfigurationException: if the theme or its parent is not found

    """
    enabled_themes: list[BaseTheme] = [theme]
    seen_names: list[str] = [theme.name]

    while theme.parent:
        try:
            theme = get_theme(theme.parent)
        except KeyError as err:
            msg = f"Parent theme '{theme.parent}' is not recognised."
            raise CkanConfigurationException(msg) from err

        if theme.name in seen_names:
            chain = " <- ".join(seen_names)
            msg = f"Cannot extend '{theme.name}' theme because it's already present in theme chain: {chain}"
            raise CkanConfigurationException(msg)

        seen_names.append(theme.name)
        enabled_themes.append(theme)

    here = os.path.dirname(__file__)

    for theme in reversed(enabled_themes):
        if (path := theme.template_path()) and os.path.isdir(path):
            tk.add_template_directory(config_, os.path.relpath(path, here))

        if (path := theme.asset_path()) and os.path.isdir(path):
            tk.add_resource(os.path.relpath(path, here), f"theming/{theme.name}")

        if (path := theme.public_path()) and os.path.isdir(path):
            tk.add_public_directory(config_, os.path.relpath(path, here))

    UIManager.reset()


class UIManager:
    ui: UI | None = None

    @classmethod
    def get(cls):
        """Get the current UI instance. Creates one if it doesn't exist."""
        if cls.ui is None:
            cls.set(cfg.theme())

        return cls.ui

    @classmethod
    def set(cls, theme: str, app: types.CKANApp = current_app):  # pyright: ignore[reportArgumentType]
        """Set the UI instance to a new theme."""
        cls.ui = get_theme(theme).build_ui(app)

    @classmethod
    def reset(cls):
        """Reset the UI instance to None."""
        cls.ui = None


ui = LocalProxy(UIManager.get)
