#!/usr/bin/env python3
"""Integration tests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD, MockResponse


@parameterized_class([
    {
        "org_payload": payload["org_payload"],
        "repos_payload": payload["repos_payload"],
        "expected_repos": payload["expected_repos"],
        "expected_licensed_repos": payload["expected_licensed_repos"],
        "license_key": payload["license_key"],
    }
    for payload in TEST_PAYLOAD
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using parameterized_class."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get at the class level."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop class-level patches."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos without license filter."""
        client = GithubOrgClient("alx")
        self.assertEqual(client.public_repos(), self.expected_repos)

        self.mock_get.assert_any_call("https://api.github.com/orgs/alx")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self):
        """Test public_repos with license filter."""
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload),
        ]

        client = GithubOrgClient("alx")
        self.assertEqual(
            client.public_repos(self.license_key),
            self.expected_licensed_repos
        )

        self.mock_get.assert_any_call("https://api.github.com/orgs/alx")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])


class TestGithubOrgClient(unittest.TestCase):
    """Simple unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org returns correct payload."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"repos_url": "mock_url"}

        mock_get_json.return_value = expected_payload
        client = GithubOrgClient(org_name)

        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other"}}, "my_license", False),
        ({}, "my_license", False),
        ({"license": None}, "my_license", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


if __name__ == "__main__":
    unittest.main()
