#!/usr/bin/env python3
"""GithubOrgClient module"""

import requests
from typing import Dict, List


class GithubOrgClient:
    """A Github organization client"""

    ORG_URL = "https://api.github.com/orgs/{org}"

    def __init__(self, org: str) -> None:
        self._org = org

    @property
    def org(self) -> Dict:
        """Return org data"""
        url = self.ORG_URL.format(org=self._org)
        return requests.get(url).json()

    @property
    def _public_repos_url(self) -> str:
        """Returns the URL for the org's repos endpoint"""
        return self.org.get("repos_url")

    def public_repos(self, license: str = None) -> List[str]:
        """Return list of repo names, optionally filtered by license"""
        repos = requests.get(self._public_repos_url).json()
        repo_names = []

        for repo in repos:
            if license is None:
                repo_names.append(repo["name"])
            else:
                repo_license = repo.get("license", {}).get("key")
                if repo_license == license:
                    repo_names.append(repo["name"])

        return repo_names

    @staticmethod
    def has_license(repo: Dict, license_key: str) -> bool:
        """Check if repo has a given license"""
        repo_license = repo.get("license", {}).get("key")
        return repo_license == license_key
