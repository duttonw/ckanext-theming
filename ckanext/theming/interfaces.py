from collections.abc import Iterable
from typing import ClassVar

from ckan.plugins import IConfigurer, Interface

from ckanext.theming.base import UI, BaseTheme


class ITheme(Interface):
    """Allow extensions to provide custom themes for CKAN."""

    _reverse_iteration_order: ClassVar[bool] = IConfigurer._reverse_iteration_order

    def register_themes(self) -> Iterable[BaseTheme]:
        """Register themes provided by extension.

        Example::

            def register_themes(self):
                from ckanext.theming.lib import Theme

                return [
                    Theme("mytheme", "/path/to/mytheme"),
                    Theme(
                        "myothertheme",
                        "/path/to/myothertheme",
                        parent="templates",
                    ),
                ]

        :returns: themes provided by the extension
        :rtype: list

        """
        return []

    def get_default_theme_ui_sources(self) -> list[str]:
        """Get the list of macros with default component implementations.

        Use this hook to provide default implementations of components that
        themes can override. For example, an extension might provide a set of
        default UI components with generic implementation that works for
        everyone::

            {% macro table_row(content) %}
                <tr>{{ content }}</tr>
            {% endmacro %}

        Themes can then easily override these components by defining their own
        macros with the same names. This allows for a consistent set of UI
        components across themes while still allowing for simple
        customization.

        Theming extension provides a set of components in this way: table_row,
        table_cell, table_head, table_body, video, image, etc. Because of it,
        themes can omit implementation of these components, unless they require
        customization.

        Components registered via this method have lower priority than theme's
        components. If you need to define custom components that must not be
        accidentally overridden by themes, with higher priority than theme's
        components, you can use the
        :py:meth:`~ITheme.get_additional_theme_ui_sources`.

        The returned list should contain paths to the macro files that define
        these default components. These paths will be made available to all
        themes.

        """
        return []

    def get_additional_theme_ui_sources(self) -> list[str]:
        """Get additional UI macro files for themes.

        Extensions can use this hook to provide additional files that themes
        can use. The returned list should contain paths to the macro
        files. These paths will be made available to all themes.

        This allows for sharing common UI components across multiple
        themes. For example, an extension might provide a set of standard UI
        components that themes can utilize. Unlike
        :py:meth:`~ITheme.get_default_theme_ui_sources` which is intended for
        default implementations, this hook can be used for any additional UI
        sources that will be used by end users, not by themes.

        Components defined in these sources will have higher priority than
        components defined in themes, so they can be used to provide components
        that themes can use but not override.
        """
        return []

    def patch_theme_ui(self, theme: BaseTheme, ui: UI):  # pyright: ignore[reportUnusedParameter]
        """Customize the UI for a theme.

        This method is called for each theme UI instance is created via
        :py:meth:`~ckanext.theming.lib.Theme.build_ui`. Extensions can use this
        hook to add custom UI components, modify existing ones, or patch UI
        object in any other meaningful way.

        Example::

            def patch_theme_ui(self, theme, ui):
                ui._add_component("divider", lambda *args, **kwargs: Markup("<hr/>"))

        :param theme: The theme being built
        :type theme: :py:class:`~ckan.lib.theme.Theme`
        :param ui: The UI object to customize
        :type ui: :py:class:`~ckanext.theming.lib.UI`

        """
