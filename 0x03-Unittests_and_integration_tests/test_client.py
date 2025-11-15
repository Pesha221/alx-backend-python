#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient using parameterized_class."""

import unittest
import requests
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient # type: ignore
# Assuming fixtures.py provides MockResponse and TEST_PAYLOAD
from fixtures import TEST_PAYLOAD, MockResponse # type: ignore


# The TestIntegrationGithubOrgClient class addresses the requirements:
# 1. Uses @parameterized_class decorator. 
# We simplify the usage by passing the list of dictionaries directly.
# The keys in TEST_PAYLOAD match the class attributes required.
@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Tests GithubOrgClient using class-level patching and parameterized data.
    The test data (e.g., self.org_payload) is available directly on 'self' 
    due to the @parameterized_class decorator.
    """

    # 2. Has setUpClass and tearDownClass class methods.
    # 3. self.get_patcher is a patcher of requests.get, managed at the class level.
    @classmethod
    def setUpClass(cls):
        """Sets up class-level mocking for requests.get."""
        cls.get_patcher = patch('requests.get')
        # Start the patcher and store the mock object
        cls.mock_get = cls.get_patcher.start()

        # Configure the mock_get's side_effect for the two API calls per test run:
        # The list must be reset for each test iteration if side_effect is used.
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload), 
            MockResponse(cls.repos_payload) 
        ]

    @classmethod
    def tearDownClass(cls):
        """Stops the class-level mocking."""
        cls.get_patcher.stop()

    # --- test_public_repos (Integration Test) ---
    def test_public_repos(self):
        """
        Tests the GithubOrgClient.public_repos method without a license filter.
        """
        client = GithubOrgClient("alx")
        
        # Verify that the full list of repos is returned 
        self.assertEqual(client.public_repos(), self.expected_repos)
        
        # Verify the correct URLs were requested
        org_url = f"https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]
        
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)


    # --- test_public_repos_with_license (Integration Test) ---
    def test_public_repos_with_license(self):
        """
        Tests the GithubOrgClient.public_repos method with a license filter.
        """
        # Re-initialize the mock's side_effect for the new test run 
        # since the previous test consumed the mock's responses.
        self.mock_get.side_effect = [
            MockResponse(self.org_payload), # ORG call
            MockResponse(self.repos_payload) # REPOS call
        ]
        
        client = GithubOrgClient("alx")

        # Verify that the filtered list of repos is returned
        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )
        
        # Verify correct URL calls were made
        org_url = f"https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]
        
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)


# --- Test class for non-parameterized, simple unit tests ---

class TestGithubOrgClient(unittest.TestCase):
    """Simple unit tests that don't require the parameterized_class setup."""

    # --- test_org ---
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct payload."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123, "repos_url": "mock_url"}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        # client.org is a property call
        self.assertEqual(client.org, expected_payload) 
        mock_get_json.assert_called_once_with(expected_url)

    # --- test_has_license ---
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Unit test for the static method GithubOrgClient.has_license."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

# Add the standard unittest entry point to ensure it runs
if __name__ == "__main__":
    unittest.main()