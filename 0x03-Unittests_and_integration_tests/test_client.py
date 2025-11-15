#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient # type: ignore


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class."""

    # --- test_org ---
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct payload
        and calls get_json exactly once.
        """
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123, "repos_url": "mock_url"}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    # --- test_public_repos_url ---
    def test_public_repos_url(self):
        """
        Tests that the result of _public_repos_url is the expected one
        based on the mocked payload returned by the .org property.
        """
        mock_org_payload = {
            "repos_url": "https://api.github.com/orgs/alx/repos"
        }

        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value=mock_org_payload
        ) as mock_org:
            client = GithubOrgClient("alx")
            result_url = client._public_repos_url
            self.assertEqual(result_url, mock_org_payload["repos_url"])
            mock_org.assert_called_once()
            
    # --- test_public_repos ---
    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """
        Unit test for GithubOrgClient.public_repos.
        Mocks get_json and _public_repos_url and verifies calls and results.
        """
        # 1. Define the payload that get_json will return (the list of repos)
        repos_payload = [
            {"name": "repo_a"},
            {"name": "repo_b"},
            {"name": "repo_c"},
        ]
        mock_get_json.return_value = repos_payload
        
        # 2. Define the URL that _public_repos_url will return
        mock_repos_url = "https://api.github.com/mock/repos"

        # 3. Patch _public_repos_url property using a context manager
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            # Configure the patched property to return the mock URL
            mock_public_repos_url.return_value = mock_repos_url
            client = GithubOrgClient("testorg")
            # Call the method under test
            repos = client.public_repos()
            # 4. Test that the list of repos is as expected
            expected_repos = ["repo_a", "repo_b", "repo_c"]
            self.assertEqual(repos, expected_repos)
            # 5. Test that the mocked property was called once
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_repos_url)

    # --- test_has_license (FIXED: Moved inside the class) ---
    @parameterized.expand([
        # Scenario 1: License matches
        ({"license": {"key": "my_license"}}, "my_license", True),
        # Scenario 2: License does not match
        ({"license": {"key": "other_license"}}, "my_license", False),
        # Add a case for missing license key
        ({"license": {"key": "my_license"}}, "wrong_license", False),
        # Add a case for repo having no license field
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """
        Unit test for the static method GithubOrgClient.has_license.
        Tests if a repository payload correctly identifies a license key.
        """
        # Note: Since has_license is a @staticmethod, we call it directly on the class.
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

# Add the standard unittest entry point to ensure it runs
if __name__ == "__main__":
    unittest.main()
        