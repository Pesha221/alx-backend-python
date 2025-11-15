#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient using parameterized_class."""

import unittest
import requests
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient  # type: ignore
from fixtures import TEST_PAYLOAD, MockResponse  # type: ignore


# ALX expects EXACTLY this:
# TEST_PAYLOAD is already a list of dictionaries
@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient using API fixtures.
    Each set of data is injected via @parameterized_class.
    """

    @classmethod
    def setUpClass(cls):
        """Start class-level patch for requests.get with controlled side_effect."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Each class instance gets its own MockResponse set
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload)
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patched requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos() without license filter."""
        client = GithubOrgClient("alx")
        self.assertEqual(client.public_repos(), self.expected_repos)

        org_url = "https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]

        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)

    def test_public_repos_with_license(self):
        """Test public_repos() with license filtering."""
        # Reset side_effect for this test
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload)
        ]

        client = GithubOrgClient("alx")

        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )

        org_url = "https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]

        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)


class TestGithubOrgClient(unittest.TestCase):
    """Simple unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        """Test the org property."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123, "repos_url": "mock_url"}

        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Unit test for has_license static method."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


if __name__ == "__main__":
    unittest.main()
