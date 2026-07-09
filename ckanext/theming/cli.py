import contextlib
import fnmatch
import inspect
import json
import logging
import os
import pprint
import random
import re
import shutil
import string
import textwrap
import time
from collections import Counter, defaultdict
from collections.abc import Callable, Collection
from typing import Any

import click
import flask.signals
import msgspec
from jinja2 import Environment, Template, TemplateNotFound
from jinja2.exceptions import UndefinedError
from jinja2.runtime import Macro
from werkzeug.exceptions import NotFound
from werkzeug.routing import BuildError, Rule

import ckan.plugins.toolkit as tk
from ckan import model, types

from . import config as cfg
from . import lib, reference

log = logging.getLogger(__name__)

__all__ = ["theme"]

RE_COMPONENT = re.compile(r"(?<!\.)\bui\.(?!util\.)(?P<name>\w+)")

RE_EXTEND = re.compile(
    r"""
    \{%-?\s*		(?# tag start)
    extends\s+		(?# tag name)
    (?P<name>.+?)	(?# template name. Non-greedy match to exclude leading whitespace)
    \s*-?%\}		(?# tag end)
""",
    re.X,
)

RE_CKAN_EXTEND = re.compile(
    r"""
    \{%-?\s*		(?# tag start)
    ckan_extends\s+	(?# tag name)
    \s*-?%\}		(?# tag end)
""",
    re.X,
)


RE_INCLUDE = re.compile(
    r"""
    \{%-?\s*		(?# tag start)
    include\s+		(?# tag name)
    (?P<name>.+?)	(?# template name)
    \s*-?%\}		(?# tag end)
    """,
    re.X,
)


@click.group(name="theme", short_help="Theme related commands.")
def theme():
    pass


def theme_callback(ctx: click.Context, param: click.Parameter, name: str | None):  # pyright: ignore[reportUnusedParameter]
    if not name:
        name = cfg.theme()

    if not name:
        tk.error_shout("Theme is not configured")
        raise click.Abort

    try:
        return lib.get_theme(name)
    except KeyError as err:
        tk.error_shout(f"Theme {name} is not registered")
        raise click.Abort from err


theme_option = click.option("-t", "--theme", callback=theme_callback)


@contextlib.contextmanager
def _make_ui(ctx: click.Context, theme: lib.Theme):
    """Context manager to build the UI for a theme within a Flask app context."""
    with ctx.meta["flask_app"].app_context() as app_context:
        yield theme.build_ui(app_context.app)


@theme.command("list")
def list_themes():
    """List available themes."""
    themes = lib._themes  # pyright: ignore[reportPrivateUsage]
    for name, info in themes.items():
        click.echo(name)
        click.echo(f"  Path: {info.path}")

        lineage = []
        parent = info.parent
        while parent:
            if parent_info := themes.get(parent):
                lineage.append(parent)
                parent = parent_info.parent
            else:
                lineage.append(click.style(parent, fg="red"))

        if lineage:
            click.secho(f"  Extends: {' -> '.join(lineage)}")


@theme.command("create")
@click.argument("name")
@click.argument("location", required=False)
@click.option("--base", default="bare", help="Base theme to copy structure and templates from.")
def theme_create(name: str, location: str, base: str):
    """Create a new theme with all required structure and templates."""
    if not location:
        location = os.getcwd()
        if not click.confirm(f"No location provided, theme will be created inside `{location}`"):
            raise click.Abort
    theme = lib.get_theme(base)
    if not theme.path:
        tk.error_shout(f"{base} theme does not have a filesystem path to copy from")
        if theme.parent:
            click.echo(f"Consider using `{theme.parent}` as the base theme instead.")

        raise click.Abort

    shutil.copytree(
        theme.path,
        os.path.join(location, name),
        ignore=lambda d, f: ["node_modules", "package-lock.json", ".benchmarks", ".test-screenshots"],
    )


@theme.group()
def component():
    """Component-level commands."""


@component.command("list")
@click.pass_context
@theme_option
def component_list(ctx: click.Context, theme: lib.Theme):
    """List available components."""
    with _make_ui(ctx, theme) as ui:
        for item in ui:
            click.echo(item)


@component.command("analyze")
@click.pass_context
@click.option("-c", "--category", help="Filter components by category.", type=reference.Category)
@click.option("--with-custom-args", type=click.Choice(["both", "missing", "additional"]))
@theme_option
@click.argument("components", nargs=-1)
def component_analyze(  # noqa: C901, PLR0912, PLR0915
    ctx: click.Context,
    components: Collection[str],
    theme: lib.Theme,
    with_custom_args: str | None,
    category: reference.Category | None,
):  # noqa: C901
    """Analyze UI components and their implementations."""
    with _make_ui(ctx, theme) as ui:
        if not components:
            components = sorted(ui)

        for component in components:
            comp_func = getattr(ui, component, None)
            if not comp_func:
                tk.error_shout(f"Unknown component {component}")
                continue

            ref = lib.get_active_theme().component_reference()[component]
            if category and ref.category != category:
                continue
            # Try to get the source or signature information
            if isinstance(comp_func, Macro):
                standard_arguments = []
                additional_arguments = []

                for arg in comp_func.arguments:
                    if arg in ref.arguments:
                        standard_arguments.append(
                            click.style(arg, italic=True)
                            if arg == "content"
                            else f"{arg}: {click.style(ref.arguments[arg].type, italic=True)}"
                        )
                    else:
                        additional_arguments.append(click.style(f"+{arg}", fg="green", bold=True))

                missing_arguments = [
                    click.style(f"-{arg}: {click.style(ref.arguments[arg].type, italic=True)}", fg="red")
                    for arg in set(ref.arguments) - set(comp_func.arguments)
                ]
                if with_custom_args == "both" and not additional_arguments and not missing_arguments:
                    continue

                if with_custom_args == "additional" and not additional_arguments:
                    continue

                if with_custom_args == "missing" and not missing_arguments:
                    continue

                sig = ", ".join(standard_arguments + additional_arguments + missing_arguments)

                if comp_func.catch_varargs:
                    sig = ", ".join([sig, "*varargs"])

                if comp_func.catch_kwargs:
                    sig = ", ".join([sig, "**kwargs"])

                sig = f"({sig})"
                comp_type = "Callable macro" if comp_func.caller else "Macro"
                source_file = inspect.getsourcefile(comp_func._func)  # pyright: ignore[reportPrivateUsage]
            else:
                sig = str(inspect.signature(comp_func))
                comp_type = type(comp_func).__name__
                source_file = inspect.getsourcefile(comp_func)

            chain: list[str | None] = []
            chain_member = comp_func
            while chain_parent := getattr(chain_member, "_theming_chain", None):
                chain.append(inspect.getsourcefile(chain_parent._func))
                chain_member = chain_parent

            click.secho(f"{component}", bold=True)
            click.secho(click.style("Type: ", fg="yellow") + comp_type)
            click.secho(click.style("Category: ", fg="yellow") + ref.category.name)
            if ref.description:
                click.secho(
                    click.style("Description: \n", fg="yellow")
                    + textwrap.fill(ref.description, initial_indent="\t", subsequent_indent="\t")
                )
            click.secho(click.style("Signature: ", fg="yellow") + sig)

            if ref.arguments:
                no_description = click.style("description is missing", dim=True)
                click.secho(click.style("Standard arguments:", fg="yellow"))
                for key, spec in ref.arguments.items():
                    description = (
                        textwrap.fill(spec.description, subsequent_indent="\t    ")
                        if spec.description
                        else no_description
                    )
                    click.secho(f"\t{key}: {description}")

            if source_file:
                click.secho(click.style("Defined in: ", fg="yellow") + os.path.relpath(source_file))

            if chain:
                click.secho(click.style("Overrides: ", fg="yellow"))
                for item in chain:
                    if item:
                        click.echo(f"\t{os.path.relpath(item)}")

            click.echo()


@component.command("check")
@theme_option
@click.pass_context
def component_check(ctx: click.Context, theme: lib.Theme):  # noqa: C901
    """Verify that a theme implements all required UI components."""
    categorized: dict[reference.Category, set[str]] = defaultdict(set)
    component_ref = lib.get_active_theme().component_reference()
    for name, info in component_ref.items():
        categorized[info.category].add(name)

    with _make_ui(ctx, theme) as ui:
        # Get all components from this theme
        theme_components = set(ui)
        missing_components = {name: sorted(items - theme_components) for name, items in categorized.items()}

        extra_components = sorted(theme_components.difference(component_ref))

        click.echo(f"Theme implements {len(theme_components)} components")

        for category, items in categorized.items():
            if missing_components[category]:
                click.secho(
                    f"Missing {len(missing_components[category])} out of"
                    + f" {len(items)} in category {category.name}",
                    fg="yellow",
                )
                click.secho("\t" + ", ".join(missing_components[category]), fg="red")

            else:
                click.secho(f"All components in category {category.name} are implemented", fg="green")
        if extra_components:
            click.secho(f"Extra components ({len(extra_components)})", fg="yellow")
            click.secho("\t" + ", ".join(extra_components), fg="blue")

        with ctx.meta["flask_app"].test_request_context():
            args = {
                "".join(random.sample(string.ascii_letters, 10)): random.randint(0, 100),  # noqa: S311
            }
            rigid: dict[type, dict[str, Exception]] = defaultdict(dict)
            allow_rigid = {"user", "group", "package", "resource", "organization", "activity", "license"}

            for name in sorted(theme_components):
                func = getattr(ui, name)
                try:
                    func(**args)
                except Exception as err:  # noqa: BLE001
                    if isinstance(err, UndefinedError) and name in allow_rigid:
                        continue
                    rigid[type(err)][name] = err

            if rigid:
                rigid_count = sum(map(len, rigid.values()))
                click.secho(
                    f"{rigid_count} components produced an error when called with random arguments."
                    + "\nIdeally, components should not fail in this case",
                    fg="yellow",
                )
                for key, values in rigid.items():
                    click.secho(f"\t{key.__name__}:", bold=False)
                    for name, err in values.items():
                        click.secho(f"\t  {click.style(name, bold=True)}: {err}")


@theme.group()
def template():
    """Template-level commands."""


@template.command("list")
@theme_option
def template_list(theme: lib.Theme):
    """List template files in the theme."""
    root = theme.template_path()
    if not root:
        tk.error_shout(f"{theme.name} does not register templates")
        raise click.Abort
    for path, _, files in os.walk(root):
        relpath = os.path.relpath(path, root)
        if relpath == ".":
            relpath = ""

        for file in files:
            tpl_name = os.path.join(relpath, file)
            reference.templates[tpl_name]
            click.echo(tpl_name)


@template.command("check")
@click.option("-e", "--show-extra", is_flag=True, help="Show custom templates")
@theme_option
def template_check(theme: lib.Theme, show_extra: bool):
    """Verify that a theme contains all required templates."""
    categorized: dict[reference.Category, set[str]] = defaultdict(set)
    for name, info in reference.templates.items():
        categorized[info.category].add(name)

    root = theme.template_path()
    if not root:
        tk.error_shout(f"{theme.name} does not register templates")
        raise click.Abort
    templates = {os.path.relpath(os.path.join(path, file), root) for path, _, files in os.walk(root) for file in files}

    click.echo(f"Theme contains {len(templates)} templates")

    missing = {name: sorted(items - templates) for name, items in categorized.items()}
    extra = sorted(templates.difference(reference.templates))

    for category, items in categorized.items():
        if missing[category]:
            click.secho(
                f"  Missing {len(missing[category])} out of" + f" {len(items)} in category {category.name}",
                fg="yellow",
            )
            click.secho("    " + ", ".join(missing[category]), fg="red")

        else:
            click.secho(f"  All templates in category {category.name} are present", fg="green")
    if extra and show_extra:
        click.secho(f"  Extra templates ({len(extra)})", fg="yellow")
        click.secho("    " + "\n    ".join(extra), fg="blue")


@template.command("analyze")
@click.pass_context
@theme_option
@click.argument("templates", nargs=-1)
@click.option("--relative-filename", is_flag=True)
@click.option("--hierarchy-blocks", is_flag=True)
def template_analyze(  # noqa: C901
    ctx: click.Context,
    templates: Collection[str],
    theme: lib.Theme,
    relative_filename: bool,
    hierarchy_blocks: bool,
):
    """Analyze theme templates."""
    root = theme.template_path()
    if not root:
        tk.error_shout(f"{theme.name} does not register templates")
        raise click.Abort
    if not templates:
        templates = {
            os.path.relpath(os.path.join(path, file), root) for path, _, files in os.walk(root) for file in files
        }
        click.secho(f"Available templates({len(templates)}):")

    env = ctx.meta["flask_app"].jinja_env
    for name in sorted(templates):
        try:
            tpl = env.get_template(name)
        except TemplateNotFound:
            tk.error_shout(f"Template {name} does not exist")
            continue

        ref = reference.templates[name]
        click.secho(f"{name}", bold=True)
        click.secho(click.style("Category: ", fg="yellow") + ref.category.name)
        click.secho(
            click.style("Filename: ", fg="yellow") + os.path.relpath(tpl.filename, os.getcwd())
            if relative_filename
            else os.path.normpath(tpl.filename)
        )

        with open(tpl.filename) as src:
            content = src.read()

        if includes := RE_INCLUDE.findall(content):
            click.secho(click.style("Includes: ", fg="yellow") + ", ".join(i for i in sorted(set(includes))))

        all_blocks: dict[str | None, set[str]] = {tpl.filename: set(tpl.blocks)}
        hierarchy: list[str] = []

        hierarchy_break = _discover_template_hierarchy(env, tpl, hierarchy, all_blocks)

        # click.secho(click.style("Extends: ", fg="yellow") + parent_name)
        if hierarchy:
            click.secho("Hierarchy: ", fg="yellow")
            for item in hierarchy:
                click.echo(f"    {os.path.relpath(item, os.getcwd()) if relative_filename else item}")
                if hierarchy_blocks:
                    click.secho(f"        {', '.join(sorted(all_blocks[item]))}", bold=True)

        if hierarchy_break:
            click.secho(click.style("Hierarchy detection interrupted on: ", fg="red") + hierarchy_break)

        if tpl.blocks:
            click.secho(click.style("Explicit blocks: ", fg="yellow") + ", ".join(sorted(tpl.blocks)))

        implicit_blocks = {block for blocks in all_blocks.values() for block in blocks} - set(tpl.blocks)
        if implicit_blocks:
            click.secho(click.style("Implicit blocks: ", fg="yellow") + ", ".join(sorted(implicit_blocks)))

        click.echo()


def _discover_template_hierarchy(
    env: Environment, tpl: Template, hierarchy: list[str], all_blocks: dict[str | None, set[str]] | None = None
) -> str | None:
    parent_name = None

    with open(tpl.filename) as src:  # pyright: ignore[reportArgumentType]
        content = src.read()

    if extends := RE_EXTEND.search(content):
        parent_name = extends.group("name").strip("\"'")

    elif RE_CKAN_EXTEND.search(content):
        clean_name = tpl.name.rsplit("*", 1)[-1]  # pyright: ignore[reportOptionalMemberAccess]
        dirname = tpl.filename[: -len(clean_name) - 1]  # pyright: ignore[reportOptionalSubscript, reportUnknownVariableType]
        parent_name = f"*{dirname}*{clean_name}"

    else:
        return None

    try:
        parent_tpl = env.get_template(parent_name)
    except TemplateNotFound:
        return parent_name

    canonical: str = os.path.normpath(parent_tpl.filename)  # pyright: ignore[reportArgumentType, reportCallIssue, reportUnknownVariableType]
    hierarchy.append(canonical)
    if all_blocks is not None:
        all_blocks[canonical] = set(parent_tpl.blocks)

    return _discover_template_hierarchy(env, parent_tpl, hierarchy, all_blocks)


@template.command("component-usage")
@theme_option
@click.pass_context
@click.option("--include-frequency", is_flag=True, help="Include component usage frequency.")
@click.option("--show-unused", is_flag=True, help="Show components that are not used in any template.")
@click.option("--path", default="/", help="Only analyze templates under the specified path.")
def template_component_usage(  # noqa: C901, PLR0912
    ctx: click.Context, theme: lib.Theme, include_frequency: bool, path: str, show_unused: bool
):  # noqa: C901, PLR0912
    """Analyze component usage in templates."""
    env: Environment = ctx.meta["flask_app"].jinja_env
    used: dict[str, set[str]] = defaultdict(set)
    counter: Counter[str] = Counter()

    all_templates: set[str] = set()

    path = os.path.abspath(path)
    for name in env.list_templates():
        if not name.endswith(".html"):
            continue
        tpl = env.get_template(name)
        filename: str = os.path.normpath(tpl.filename)  # pyright: ignore[reportCallIssue, reportArgumentType, reportUnknownVariableType]
        if os.path.normpath(filename).startswith(path):
            all_templates.add(filename)

        hierarchy: list[str] = []
        _discover_template_hierarchy(env, tpl, hierarchy)
        all_templates.update(filename for filename in hierarchy if filename.startswith(path))

    for filename in all_templates:
        with open(filename) as src:
            for component_name in RE_COMPONENT.findall(src.read()):
                used[component_name].add(filename)
                counter.update([component_name])

    with _make_ui(ctx, theme) as ui:
        existing = set(ui)

    unused = existing - set(used)
    unknown = set(used) - existing
    unimplemented = unknown & set(lib.get_active_theme().component_reference())

    if show_unused:
        if unused:
            click.secho(click.style(f"Unused components({len(unused)}): ", fg="yellow") + ", ".join(sorted(unused)))
        else:
            click.secho("No unused components", fg="green")

    if unimplemented:
        click.secho(f"Standard components with missing implementation({len(unimplemented)}): ", fg="yellow")
        for name in sorted(unimplemented):
            click.echo(f"  {name}:")
            for tpl_name in sorted(used[name]):
                click.echo(f"    {tpl_name}")

    if unknown := (unknown - unimplemented):
        click.secho(f"Unknown components({len(unknown)}): ", fg="yellow")
        for name in sorted(unknown):
            click.echo(f"  {name}:")
            for tpl_name in sorted(used[name]):
                click.echo(f"    {tpl_name}")

    else:
        click.secho("No unknown components", fg="green")

    if include_frequency:
        click.secho("Component frequency:", fg="yellow")
        for name, count in sorted(counter.items(), key=lambda pair: pair[::-1], reverse=True):
            click.echo(f"{count:> 5}: {name}")


@theme.group()
def endpoint():
    """Endpoint-level commands."""


@endpoint.command("list")
@click.pass_context
def endpoint_list(ctx: click.Context):
    """List registered Flask endpoints."""
    app = ctx.meta["flask_app"]
    for name in app.view_functions:
        click.echo(name)


@endpoint.command("variants")
@click.pass_context
@click.argument("endpoints", nargs=-1)
def endpoint_variants(ctx: click.Context, endpoints: Collection[str]):
    """List variants of Flask endpoints."""
    app = ctx.meta["flask_app"]
    grouped: dict[str, list[Rule]] = app.url_map._rules_by_endpoint
    if not endpoints:
        endpoints = tuple(grouped)

    for name in endpoints:
        if name not in grouped:
            tk.error_shout(f"Endpoint {name} does not exist")
            continue

        click.secho(name, bold=True)
        for variant in grouped[name]:
            click.secho(click.style("Rule: ", fg="yellow") + variant.rule)
            click.secho(click.style("Methods: ", fg="yellow") + ", ".join(variant.methods or []))
            if variant.arguments:
                click.secho(click.style("Arguments: ", fg="yellow") + ", ".join(variant.arguments))
            if variant.defaults:
                click.secho(click.style("Defaults: ", fg="yellow") + repr(variant.defaults))
            click.echo()


class RenderInterceptionError(Exception):
    """Exception raised to intercept Jinja2 template rendering."""


def _render_intercept(condition: Callable[[dict[str, Any]], bool] = lambda kwargs: True):
    """Create a Jinja2 render interceptor that raises an exception when a condition is met."""

    def interceptor(sender: types.CKANApp, **kwargs: Any):  # pyright: ignore[reportUnusedParameter]
        if condition(kwargs):
            raise RenderInterceptionError(kwargs)

    return interceptor


def _observe_endpoint(
    endpoint: str,
    params: dict[str, Any],
    app: types.CKANApp,
    user: model.User | None = None,
    method: str = "get",
) -> dict[str, Any]:
    """Observe the template and context variables used by a Flask endpoint."""
    try:
        url = tk.url_for(endpoint, **params)
    except BuildError as err:
        tk.error_shout(err)
        raise click.Abort from err

    with app.test_request_context(url, method=method):  # noqa: SIM117
        with flask.signals.before_render_template.connected_to(_render_intercept()):
            if user:
                tk.login_user(user)

            try:
                app.full_dispatch_request()

            except NotFound as err:
                tk.error_shout(err)
                raise click.Abort from err

            except RenderInterceptionError as err:
                return err.args[0]

            log.warning("Endpoint %s did not render any template", endpoint)
            return {"template": Template(""), "context": {}}


@endpoint.command("observe", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
@click.pass_context
@click.argument("endpoint")
@click.option("--auth-user")
@click.option("--method", default="get")
@click.option("-v", "--verbose", is_flag=True, help="Show full context variables.")
@click.option("--ignore", default=("request", "session", "g", "csrf_token", "current_user"), multiple=True)
def endpoint_observe(  # noqa: PLR0913
    ctx: click.Context,
    endpoint: str,
    auth_user: str,
    verbose: bool,
    ignore: tuple[str, ...],
    method: str,
):
    """Observe the template and context variables used by a Flask endpoint."""
    app = ctx.meta["flask_app"]
    user = model.User.get(auth_user)

    with app.app_context():
        try:
            params = dict(arg.split("=") for arg in ctx.args)
        except ValueError as err:
            tk.error_shout("Extra arguments must follow the format: NAME=VALUE")
            raise click.Abort from err

        data = _observe_endpoint(endpoint, params, app, user=user, method=method)

        click.secho(f"{click.style('Template: ', fg='yellow')}{data['template'].name}")
        click.secho(
            click.style("Context types(use `-v` to see values): ", fg="yellow")
            + pprint.pformat({key: type(value) for key, value in data["context"].items() if key not in ignore})
        )
        if verbose:
            click.secho(
                click.style("Context variables: ", fg="yellow")
                + pprint.pformat({key: value for key, value in data["context"].items() if key not in ignore})
            )


def _profile_endpoint(  # noqa: C901, PLR0913
    endpoint: str,
    params: dict[str, Any],
    app: types.CKANApp,
    output: str,
    lib: str,
    user: model.User | None = None,
):
    import cProfile  # noqa: PLC0415

    import pyinstrument  # noqa: PLC0415

    try:
        url = tk.url_for(endpoint, **params)
    except BuildError as err:
        tk.error_shout(err)
        raise click.Abort from err

    # build jinja's render cache to standardize performance of following requests
    with app.test_request_context(url):
        if user:
            tk.login_user(user)
        try:
            app.full_dispatch_request()
        except NotFound as err:
            tk.error_shout(err)
            raise click.Abort from err

    profilers: dict[str, Any] = {}

    def start_render(app: Any, template: Template, context: dict[str, Any]):  # pyright: ignore[reportUnusedParameter]
        if lib == "cprofile":
            profilers[endpoint].disable()
            pr = cProfile.Profile()
            profilers[template.name or ""] = pr
            pr.enable()

    def end_render(app: Any, template: Template, context: dict[str, Any]):  # pyright: ignore[reportUnusedParameter]
        if lib == "cprofile":
            profilers[template.name or ""].disable()

    with app.test_request_context(url):  # noqa: SIM117
        with flask.signals.before_render_template.connected_to(start_render):
            with flask.signals.template_rendered.connected_to(end_render):
                if user:
                    tk.login_user(user)
                if lib == "pyinstrument":
                    profilers[endpoint] = pyinstrument.Profiler()
                    profilers[endpoint].start()
                elif lib == "cprofile":
                    profilers[endpoint] = cProfile.Profile()
                    profilers[endpoint].enable()
                app.full_dispatch_request()
                if lib == "pyinstrument":
                    profilers[endpoint].stop()

    for tpl, pr in profilers.items():
        name = tpl.replace("/", "__")
        if lib == "pyinstrument":
            with open(os.path.join(output, f"{name}.html"), "w") as dest:
                click.echo(pr.output_html(), file=dest)
        elif lib == "cprofile":
            pr.dump_stats(os.path.join(output, f"{name}.profile"))


@endpoint.command("profile", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
@click.pass_context
@click.argument("endpoint")
@click.option("--auth-user")
@click.option("--output", default=".")
@click.option("--lib", default="cprofile", type=click.Choice(["cprofile", "pyinstrument"]))
def endpoint_profile(  # noqa: PLR0913
    ctx: click.Context, endpoint: str, auth_user: str, output: str, lib: str
):
    """Profile the render time of templates used by a Flask endpoint."""
    app = ctx.meta["flask_app"]
    user = model.User.get(auth_user)

    os.makedirs(output, exist_ok=True)
    with app.app_context():
        try:
            params = dict(arg.split("=") for arg in ctx.args)
        except ValueError as err:
            tk.error_shout("Extra arguments must follow the format: NAME=VALUE")
            raise click.Abort from err

        _profile_endpoint(endpoint, params, app, output, lib, user=user)


def _benchmark_endpoint(
    endpoint: str,
    params: dict[str, Any],
    app: types.CKANApp,
    user: model.User | None = None,
    timeout: int = 5,
) -> dict[str, Any]:
    try:
        url = tk.url_for(endpoint, **params)
    except BuildError as err:
        tk.error_shout(err)
        raise click.Abort from err

    # build jinja's render cache to standardize performance of following requests
    with app.test_request_context(url):
        if user:
            tk.login_user(user)
        try:
            app.full_dispatch_request()
        except NotFound as err:
            tk.error_shout(err)
            raise click.Abort from err

    measurements: Counter[str] = Counter()
    moments = {}

    def start_request(app: Any):  # pyright: ignore[reportUnusedParameter]
        moments[endpoint] = time.time()

    def start_render(app: Any, template: Template, context: dict[str, Any]):  # pyright: ignore[reportUnusedParameter]
        measurements[endpoint] += time.time() - moments[endpoint]
        moments[template.name] = time.time()

    def end_render(app: Any, template: Template, context: dict[str, Any]):  # pyright: ignore[reportUnusedParameter]
        measurements[template.name or ""] += time.time() - moments[template.name]

    start = time.time()
    step = 0

    with click.progressbar(range(100), show_percent=True) as bar:
        while True:
            step += 1
            with app.test_request_context(url):  # noqa: SIM117
                with flask.signals.request_started.connected_to(start_request):
                    with flask.signals.before_render_template.connected_to(start_render):
                        with flask.signals.template_rendered.connected_to(end_render):
                            if user:
                                tk.login_user(user)
                            app.full_dispatch_request()

            spent = time.time() - start
            bar.pos = int(spent / timeout * 100)
            bar.render_progress()

            if spent > timeout:
                break

    return {"measurements": {name: time / step for name, time in measurements.items()}, "iterations": step}


@endpoint.command("benchmark", context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
@click.pass_context
@click.argument("endpoint")
@click.option("--auth-user")
@click.option("--timeout", default=5, type=int)
def endpoint_benchmark(  # noqa: PLR0913
    ctx: click.Context, endpoint: str, auth_user: str, timeout: int
):
    """Benchmark the render time of templates used by a Flask endpoint."""
    app = ctx.meta["flask_app"]
    user = model.User.get(auth_user)

    with app.app_context():
        try:
            params = dict(arg.split("=") for arg in ctx.args)
        except ValueError as err:
            tk.error_shout("Extra arguments must follow the format: NAME=VALUE")
            raise click.Abort from err

        data = _benchmark_endpoint(endpoint, params, app, user=user, timeout=timeout)
        click.echo(f"Total number of iterations: {data['iterations']}")
        click.echo("Average time:")
        for name, time_data in data["measurements"].items():
            if name == endpoint:
                name += "(without template rendering)"  # noqa: PLW2901
            click.echo(f"\t{name}: {time_data * 100:.3f}ms")


def _dump_encoder(value: Any):
    return f"<INVALID JSON: {value}>"


@endpoint.command("dump")
@click.pass_context
@click.option("--user")
@click.option("--ignore", default=("request", "session", "g", "csrf_token", "current_user"), multiple=True)
@click.option("--endpoints", multiple=True)
@click.option("--source")
@click.option("--show-source", is_flag=True)
@click.option("-v", "--verbose", is_flag=True)
def endpoint_dump(  # noqa: PLR0912, PLR0913, C901
    ctx: click.Context,
    user: str | None,
    ignore: tuple[str, ...],
    endpoints: tuple[str, ...],
    verbose: bool,
    source: str,
    show_source: bool,
):
    """Dump templates and context variables used by Flask endpoints in JSON format."""
    app = ctx.meta["flask_app"]
    url_map: dict[str, list[Rule]] = app.url_map._rules_by_endpoint

    auth_obj = model.User.get(user)
    source_data = reference.get_source(source)
    if show_source:
        click.echo(msgspec.yaml.encode(source_data))
        return

    result: dict[str, Any] = {}

    with app.app_context():
        for name, rules in url_map.items():
            if endpoints and name not in endpoints:
                continue

            if any(fnmatch.fnmatch(name, pattern) for pattern in source_data.ignore):
                continue

            for rule in rules:
                if rule.methods and "GET" not in rule.methods:
                    continue

                params = reference.make_params(name, rule.arguments, source_data, rule.defaults or {})
                # TODO: handle different variants
                params.update(source_data.args.get("name", {}))

                try:
                    data = _observe_endpoint(name, params, app, user=auth_obj)
                except tk.ObjectNotFound as err:
                    tk.error_shout(f"Endpoint {name} with params {params} caused 404")
                    raise click.Abort from err

                result[name] = {
                    "template": data["template"].name,
                    "context_types": {
                        key: type(value).__name__ for key, value in data["context"].items() if key not in ignore
                    },
                }
                if verbose:
                    result[name]["context_variables"] = {
                        key: value for key, value in data["context"].items() if key not in ignore
                    }

    click.echo(json.dumps(result, default=_dump_encoder))
