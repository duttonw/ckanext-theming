"""Reference definitions for components used in the system."""

import copy
import dataclasses
import enum
import fnmatch
import os
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterator, Mapping, MutableMapping
from typing import Any, TypeVar

import msgspec
from typing_extensions import override


class Matcher(msgspec.Struct):
    pattern: str
    path: list[str]

    def matches(self, arg: str, endpoint: str):
        return fnmatch.fnmatch(f"{arg}:{endpoint}", self.pattern)

    def get(self, arg: str, endpoint: str, data: dict[str, dict[str, Any]]):
        if not self.matches(arg, endpoint):
            return None

        value = data
        for step in self.path:
            value = value[step]
        return value


class Source(msgspec.Struct):
    data: dict[str, dict[str, Any]]
    ignore: list[str]
    matchers: list[Matcher]
    args: dict[str, Any] = msgspec.field(default_factory=dict)


class Category(enum.Enum):
    ESSENTIAL = "essential"
    RECOMMENDED = "recommended"
    EXPERIMENTAL = "experimental"
    PLUGIN = "plugin"
    CUSTOM = "custom"


@dataclasses.dataclass(frozen=True)
class MacroArgument:
    description: str = ""
    type: str = "any"


@dataclasses.dataclass(frozen=True)
class Component:
    category: Category = Category.CUSTOM
    description: str = ""
    arguments: dict[str, MacroArgument] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass(frozen=True)
class Template:
    category: Category = dataclasses.field(default=Category.CUSTOM)


def get_source(filename: str | None = None) -> Source:
    if not filename:
        filename = os.path.join(os.path.dirname(__file__), "dump_source.yaml")

    with open(filename, "rb") as src:
        return msgspec.yaml.decode(src.read(), type=Source)


def make_params(endpoint: str, args: set[str], source: Source, defaults: Mapping[str, Any]):  # noqa: C901
    params: dict[str, Any] = {}
    for arg in args:
        for matcher in source.matchers:
            if value := matcher.get(arg, endpoint, source.data):
                params[arg] = value
                break
        else:
            if arg in source.data:
                params[arg] = source.data[arg]
            elif arg in defaults:
                params[arg] = defaults[arg]
            else:
                raise KeyError(f"{arg}:{endpoint}")
    return params


K = TypeVar("K", bound=Hashable)
V = TypeVar("V", bound=Hashable)


class Glossary(MutableMapping[K, V]):
    __components: dict[K, V]
    default_factory: Callable[[], V] | None

    def __init__(self, data: dict[K, V] | None = None, default_factory: Callable[[], V] | None = None):
        if data is None:
            data = {}
        self.__components = data
        self.default_factory = default_factory

    @override
    def __delitem__(self, key: K):
        del self.__components[key]

    @override
    def __setitem__(self, key: K, value: V):
        self.__components[key] = value

    @override
    def __getitem__(self, key: K) -> V:
        if key in self.__components:
            return self.__components[key]

        if self.default_factory:
            return self.default_factory()

        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[K]:
        yield from self.__components

    @override
    def __len__(self):
        return len(self.__components)

    def clone(self):
        return type(self)(copy.deepcopy(self.__components), default_factory=self.default_factory)


def parse_components(source: str):
    with open(source, "rb") as src:
        return msgspec.yaml.decode(src.read(), type=dict[str, Component])


components: Glossary[str, Component] = Glossary(default_factory=Component)
components.update(parse_components(os.path.join(os.path.dirname(__file__), "components.yaml")))


templates: dict[str, Template] = defaultdict(Template)

with open(os.path.join(os.path.dirname(__file__), "templates.yaml"), "rb") as src:
    templates.update(msgspec.yaml.decode(src.read(), type=dict[str, Template]))
