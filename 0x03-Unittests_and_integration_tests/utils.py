#!/usr/bin/env python3
"""Utils functions for GithubOrgClient."""

import requests
from typing import Any, Dict, Tuple, Callable


def get_json(url: str) -> Dict:
    """Make an HTTP GET request to the URL and return the JSON response."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def access_nested_map(data: Dict, path: Tuple) -> Any:
    """Access nested map items via sequence of keys called path.

    Args:
        data (dict): dictionary to access.
        path (tuple): sequence of keys.

    Returns:
        any: value found at nested key.

    Raises:
        KeyError: if any key in path is missing.
    """
    for key in path:
        data = data[key]
    return data


def memoize(method: Callable) -> property:
    """Decorator to cache the result of a method."""
    attr_name = f"_{method.__name__}"

    @property
    def memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, method(self))
        return getattr(self, attr_name)

    return memoized
