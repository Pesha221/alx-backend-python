#!/usr/bin/env python3
"""Generic utilities and GithubOrgClient implementation.
"""
import requests
from functools import wraps
from typing import (
    Mapping,
    Sequence,
    Any,
    Dict,
    Callable,
)

__all__ = [
    "access_nested_map",
    "get_json",
    "memoize",
    "GithubOrgClient",
]


def access_nested_map(nested_map: Mapping, path: Sequence) -> Any:
    """Access nested map with key path."""
    for key in path:
        if not isinstance(nested_map, Mapping):
            raise KeyError(key)
        nested_map = nested_map[key]
    return nested_map


def get_json(url: str) -> Dict:
    """Get JSON from remote URL."""
    response = requests.get(url)
    return response.json()


def memoize(fn: Callable) -> Callable:
    """Decorator to memoize a method."""
    attr_name = "_{}".format(fn.__name__)

    @wraps(fn)
    def memoized(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)

    return property(memoized)


# ------------------------
#   GithubOrgClient Fix
# ------------------------

class GithubOrgClient:
    """Client for GitHub organization information"""

    ORG_URL = "https://api.github.com/orgs/{}"

    def __init__(self, org_name: str):
        self.org_name = org_name

    @property
    def org(self) -> Dict:
        """Return organization data from GitHub API"""
        url = self.ORG_URL.format(self.org_name)
        return get_json(url)
