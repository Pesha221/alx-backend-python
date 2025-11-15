#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient using parameterized_class."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient  # type: ignore
from fixtures import TEST_PAYLOAD, MockResponse  # type: ignore


# ALX expects a LIST of dictionaries; TEST_PAYLOAD already is one.
@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration tests for GithubOrgClient using data injected from TEST_PAYLOAD.
    """

    @classmethod
    def setUpClass(cls):
        """Start a class-wide patch on requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # First call returns org_payload, second returns repos_payload
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload)
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop the patcher."""
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
        """Test public_repos() with license filter."""
        # Reset for next test (previous test already used the responses)
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
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        """Test the org property returns expected payload."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123, "repos_url": "mock_url"}

        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
        ({"license": None}, "my_license", False),
        ({}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test license-checking logic."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


if __name__ == "__main__":
    unittest.main()
