import os

from ckanext.theming.lib import Theme

here = os.path.dirname(__file__)


def make_theme(name: str = "midnight-blue-polyfill"):
    return Theme(name, here, parent="classic-polyfill")
