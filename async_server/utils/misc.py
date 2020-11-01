import json
import os
import posixpath
from urllib.parse import unquote


def print_app_version():
    __version__ = '0.0.1'
    print(__version__)


def get_string_from_dict(_dict: dict) -> str:
    return json.dumps(_dict)


def translate_path(path):
    """Translate a /-separated PATH to the local filename syntax.
    """
    path = path.split('?', 1)[0]
    path = path.split('#', 1)[0]
    path = posixpath.normpath(unquote(path))
    words = path.split('/')
    words = filter(None, words)
    path = os.getcwd()
    for word in words:
        drive, word = os.path.splitdrive(word)
        head, word = os.path.split(word)
        if word in (os.curdir, os.pardir):
            continue
        path = os.path.join(path, word)
    return path
