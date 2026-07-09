import abc
import datetime
from collections.abc import Iterable
from typing import Any, Protocol

from jinja2.runtime import Macro
from markupsafe import Markup

from ckan import types

from . import reference


class PElement(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Markup: ...


class BaseUtil(abc.ABC):
    @abc.abstractmethod
    def __init__(self, theme: 'BaseTheme'): ...

    @abc.abstractmethod
    def augment_attrs(self, kwargs: dict[str, Any], defaults: dict[str, Any] | None = None, /) -> dict[str, Any]: ...

    @abc.abstractmethod
    def attrs(self, kwargs: dict[str, Any], defaults: dict[str, Any] | None = None) -> str: ...

    @abc.abstractmethod
    def tag(self, content: str, tag: str, is_void: bool = False, /, **kwargs: Any) -> str: ...

    @abc.abstractmethod
    def call(self, el: PElement, /, *args: Any, caller: Macro, **kwargs: Any) -> str: ...

    @abc.abstractmethod
    def map(self, el: PElement, items: Iterable[Any], /, *args: Any, **kwargs: Any) -> str: ...

    @abc.abstractmethod
    def now(self, tz: datetime.timezone = datetime.timezone.utc) -> datetime.datetime: ...

    @abc.abstractmethod
    def id(self, value: str | None = None, prefix: str = "id-") -> str: ...

    @abc.abstractmethod
    def keep_item(self, category: str, key: str, value: Any) -> None: ...

    @abc.abstractmethod
    def pop_items(
        self, category: str, key: str | None = None, default: Any = None, /, keep: bool = False
    ) -> dict[str, Any] | Any: ...

    @abc.abstractmethod
    def icon(self, name: str) -> str: ...


class UI(Iterable[str], abc.ABC):
    """Abstract base class for theme UIs.

    A UI provides access to a set of function that can be used in
    templates. Each function corresponds to a UI element, such as buttons,
    links, forms, etc. The UI class maintains an inventory of available
    elements that can be accessed by name.

    """

    util: BaseUtil

    @abc.abstractmethod
    def __init__(self, app: types.CKANApp, theme: 'BaseTheme', util: BaseUtil): ...

    @abc.abstractmethod
    def _add_component(self, name: str, component: PElement): ...


class BaseTheme(abc.ABC):
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

    template_folder: str
    public_folder: str
    asset_folder: str
    ui_factory: type[UI]
    util_factory: type[BaseUtil]
    icon_map: dict[str, str]

    @abc.abstractmethod
    def build_ui(self, app: types.CKANApp) -> UI: ...

    @abc.abstractmethod
    def template_path(self) -> str | None: ...

    @abc.abstractmethod
    def public_path(self) -> str | None: ...

    @abc.abstractmethod
    def asset_path(self) -> str | None: ...

    @abc.abstractmethod
    def component_reference(self) -> reference.Glossary[str, reference.Component]: ...
