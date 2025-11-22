#!/usr/bin/env python3
"""Github org client
"""

from typing import List, Dict
from utils import get_json, access_nested_map, memoize # type: ignore


class GithubOrgClient:
    """Github Org Client"""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org_name: str) -> None:
        """Initialize client"""
        self._org_name = org_name

    @memoize
    def org(self) -> Dict:
        """Return org data"""
        return get_json(self.ORG_URL.format(org=self._org_name))

    @property
    def _public_repos_url(self) -> str:
        """Return repos_url from org"""
        return self.org.get("repos_url")

    def public_repos(self, license: str = None) -> List[str]:
        """List of public repos, optionally filtered by license"""
        repos = get_json(self._public_repos_url)

        repo_names = [
            repo["name"]
            for repo in repos
            if license is None or self.has_license(repo, license)
        ]

        return repo_names

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check whether repo has a given license"""
        try:
            return access_nested_map(repo, ("license", "key")) == license_key
        except KeyError:
            return False
