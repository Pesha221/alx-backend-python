#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient # type: ignore
from fixtures import TEST_PAYLOAD # type: ignore # Import comprehensive test data


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
        # Note: calling .org as a property (no parentheses)
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
            # Patch the org property in the client class
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value=mock_org_payload
        ) as mock_org:
            client = GithubOrgClient("alx")
            # Note: calling ._public_repos_url as a property (no parentheses)
            result_url = client._public_repos_url
            self.assertEqual(result_url, mock_org_payload["repos_url"])
            mock_org.assert_called_once()
            
    # --- test_public_repos (Updated to use fixtures) ---
    @parameterized.expand(TEST_PAYLOAD)
    @patch("client.get_json")
    def test_public_repos(self, org_payload, repos_payload, expected_all_repos, *args, mock_get_json):
        """
        Unit test for GithubOrgClient.public_repos without license filter.
        Uses parameterized data from fixtures.
        """
        # Set the mock to return the list of repositories from the fixture (index 1)
        mock_get_json.return_value = repos_payload
        
        # Get the mocked repos URL from the fixture (index 0)
        mock_repos_url = org_payload.get("repos_url")

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = mock_repos_url
            client = GithubOrgClient("testorg")
            
            # Call the method under test without a license argument
            repos = client.public_repos()
            
            # The expected result is the list of all repo names (index 2)
            self.assertEqual(repos, expected_all_repos)
            
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_repos_url)

    # --- test_public_repos_with_license (NEW TEST) ---
    @parameterized.expand(TEST_PAYLOAD)
    @patch("client.get_json")
    def test_public_repos_with_license(self, org_payload, repos_payload, _, license_key, expected_licensed_repos, mock_get_json):
        """
        Unit test for GithubOrgClient.public_repos with license filter.
        Uses parameterized data from fixtures.
        """
        # Set the mock to return the list of repositories from the fixture
        mock_get_json.return_value = repos_payload
        
        # Get the mocked repos URL from the fixture
        mock_repos_url = org_payload.get("repos_url")

        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = mock_repos_url
            client = GithubOrgClient("testorg")
            
            # Call the method under test WITH the license key (index 3)
            repos = client.public_repos(license=license_key)
            
            # The expected result is the list of filtered repo names (index 4)
            self.assertEqual(repos, expected_licensed_repos)
            
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with(mock_repos_url)

    # --- test_has_license ---
    @parameterized.expand([
        # Scenario 1: License matches
        ({"license": {"key": "my_license"}}, "my_license", True),
        # Scenario 2: License does not match
        ({"license": {"key": "other_license"}}, "my_license", False),
        # Scenario 3: License key is missing in repo payload
        ({"license": None}, "my_license", False),
        # Scenario 4: Repo is missing the entire 'license' field
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
        