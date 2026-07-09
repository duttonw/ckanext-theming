import pytest

from ckan import types

from ckanext.theming import lib


@pytest.fixture
def util():
    return lib.Util(lib.Theme("test", None))


def test_init(app: types.CKANApp):
    """Util class initialized in new UI."""
    theme = lib.Theme("test", None, ui_factory=lib.MacroUI)
    ui = theme.build_ui(app.flask_app)
    assert isinstance(ui.util, lib.Util)


class TestUtilAttrs:
    def test_escape(self, util: lib.Util):
        """Attrs method properly escapes attribute values."""
        result = util.attrs({"attrs": {"hello": 'wor&"><hr id="'}})
        assert result == '''hello="wor&amp;&quot;><hr id=&quot;"'''

    def test_none(self, util: lib.Util):
        """Attrs method returns empty string if no attrs provided."""
        result = util.attrs({})
        assert result == ""

    def test_empty(self, util: lib.Util):
        """Attrs method returns empty string if empty attrs provided."""
        result = util.attrs({"attrs": {}})
        assert result == ""

    def test_non_string(self, util: lib.Util):
        """Attrs method converts non-string values to strings."""
        result = util.attrs({"attrs": {"number": 42, "boolean": True}})
        assert result == 'number="42" boolean="True"'

    def test_no_attrs_key(self, util: lib.Util):
        """Attrs method returns empty string if no 'attrs' key provided."""
        result = util.attrs({"not_attrs": {"hello": "world"}})
        assert result == ""

    def test_with_defaults(self, util: lib.Util):
        """Attrs method includes default attributes."""
        result = util.attrs({"attrs": {"hello": "world"}}, {"class": "my-class"})
        assert sorted(result.split()) == ['class="my-class"', 'hello="world"']

    def test_with_defaults_override(self, util: lib.Util):
        """Attrs method overrides default attributes."""
        result = util.attrs({"attrs": {"class": "my-class"}}, {"class": "default-class"})
        assert result == 'class="my-class"'

    def test_with_only_defaults(self, util: lib.Util):
        """Attrs method works with only default attributes."""
        result = util.attrs({}, {"class": "default-class"})
        assert result == 'class="default-class"'

    def test_with_empty_defaults(self, util: lib.Util):
        """Attrs method works with empty default attributes."""
        result = util.attrs({"attrs": {"hello": "world"}}, {})
        assert result == 'hello="world"'

    def test_with_extra_classes(self, util: lib.Util):
        """Attrs method combines extra classes with existing class attribute."""
        result = util.attrs({"_extra_class": "my-class"}, {"class": "existing-class"})
        assert result == 'class="existing-class my-class"'

    def test_prefixes(self, util: lib.Util):
        """Attrs method handles prefixes correctly."""
        result = util.attrs(
            {
                "attrs": {"hello": "ATTR"},
                "aria": {"hello": "ARIA"},
                "data": {"hello": "DATA"},
                "hx": {"hello": "HX"},
                "on": {"hello": "ON"},
            }
        )
        assert sorted(result.split()) == [
            'aria-hello="ARIA"',
            'data-hello="DATA"',
            'hello="ATTR"',
            'hx-hello="HX"',
            'onhello="ON"',
        ]


class TestUtilTag:
    def test_tag(self, util: lib.Util):
        """Tag method generates correct HTML tag."""
        result = util.tag("Hello, world!", "div", attrs={"class": "my-class"})
        assert result == '<div class="my-class">Hello, world!</div>'

    def test_void_tag(self, util: lib.Util):
        """Tag method generates correct void HTML tag."""
        result = util.tag("", "br", True, attrs={"id": "break"})
        assert result == '<br id="break"/>'

    def test_no_tag(self, util: lib.Util):
        """Tag method generates correct HTML tag with empty tag name."""
        result = util.tag("Hello world!", "", attrs={"class": "empty"})
        assert result == "Hello world!"
