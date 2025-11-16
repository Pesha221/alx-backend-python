#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient # type: ignore
from fixtures import TEST_PAYLOAD # type: ignore


# ================== Integration Tests ==================

@parameterized_class(
    (
        "org_payload",
        "repos_payload",
        "expected_repos",
        "expected_licensed_repos",
        "license_key",
    ),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using requests.get patching."""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        cls.mock_get.side_effect = [
            cls.org_payload,        # First call → org info
            cls.repos_payload       # Second call → repos list
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test GithubOrgClient.public_repos returns correct repo list."""
        client = GithubOrgClient("org")

        self.assertEqual(client.public_repos(), self.expected_repos)

        self.mock_get.assert_any_call(
            "https://api.github.com/orgs/org"
        )
        self.mock_get.assert_any_call(
            self.org_payload["repos_url"]
        )

    def test_public_repos_with_license(self):
        """Test public_repos returns only licensed repos."""
        # Reset side_effect (because previous test consumed responses)
        self.mock_get.side_effect = [
            self.org_payload,
            self.repos_payload
        ]

        client = GithubOrgClient("org")

        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )

        self.mock_get.assert_any_call(
            "https://api.github.com/orgs/org"
        )
        self.mock_get.assert_any_call(
            self.org_payload["repos_url"]
        )


# ================== Unit Tests ==================

class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org property calls get_json with the correct URL."""
        expected_payload = {"payload": True}
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)

        self.assertEqual(client.org, expected_payload)
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @parameterized.expand([
        ({"license": {"key": "my_key"}}, "my_key", True),
        ({"license": {"key": "other"}}, "my_key", False),
        ({}, "my_key", False),
        ({"license": None}, "my_key", False),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test has_license static method."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


if __name__ == "__main__":
    unittest.main()
