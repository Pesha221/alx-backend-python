#!/usr/bin/env python3
"""Integration and unit tests for GithubOrgClient."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient  # type: ignore
from fixtures import TEST_PAYLOAD, MockResponse  # type: ignore


# -------------------------------
# Integration Tests (Parameterized)
# -------------------------------

@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using parameterized_class."""

    @classmethod
    def setUpClass(cls):
        """Class-level mock for requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Side effects: first call = org payload, second call = repos payload
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patcher."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos with no license filter."""
        client = GithubOrgClient("alx")

        self.assertEqual(client.public_repos(), self.expected_repos)

        org_url = "https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]

        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)

    def test_public_repos_with_license(self):
        """Test public_repos with a license filter."""
        # Reset side effects for second test
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload),
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


# ---------------------------
# Unit Tests for Client Class
# ---------------------------

class TestGithubOrgClient(unittest.TestCase):
    """Unit tests not requiring parameterized_class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that .org returns the correct payload."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 1, "repos_url": "example.com"}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)

        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "mit"}}, "apache-2.0", False),
        ({"license": None}, "apache-2.0", False),
        ({}, "apache-2.0", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test the static has_license method."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
