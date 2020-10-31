import json


def print_app_version():
    __version__ = '0.0.1'
    print(__version__)


def get_string_from_dict(_dict: dict) -> str:
    return json.dump(_dict)
