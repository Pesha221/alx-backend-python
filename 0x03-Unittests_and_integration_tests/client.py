#!/usr/bin/env python3
"""A github org client"""

from typing import List, Dict

from utils import (
    get_json,
    access_nested_map,
    memoize,
)


class GithubOrgClient:
    """A Github org client"""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Initialize client"""
        self._org_name = org_name

    @property
    @memoize
    def org(self) -> Dict:
        """Returns the org JSON payload"""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Returns the URL to the public repos"""
        return self.org["repos_url"]

    @property
    @memoize
    def repos_payload(self) -> List[Dict]:
        """Returns the repos payload"""
        return get_json(self._public_repos_url)

    def public_repos(self, license: str = None) -> List[str]:
        """List public repos optionally filtered by license"""
        repos = self.repos_payload

        return [
            repo["name"]
            for repo in repos
            if license is None or self.has_license(repo, license)
        ]

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check if repo has the given license"""
        try:
            return access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
