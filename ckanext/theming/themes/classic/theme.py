import os

from ckanext.theming.lib import Theme

here = os.path.dirname(__file__)


def make_theme(name: str = "classic-polyfill"):
    return Theme(name, here)
