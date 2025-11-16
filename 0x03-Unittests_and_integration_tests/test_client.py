#!/usr/bin/env python3
"""Integration and unit tests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient  # type: ignore

# ------------------ Fixtures ------------------

# MockResponse to simulate requests responses
class MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

# TEST_PAYLOAD must be a list of dicts with ALL required keys
TEST_PAYLOAD = [
    {
        "org_payload": {"repos_url": "https://api.github.com/orgs/alx/repos"},
        "repos_payload": [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": None}
        ],
        "expected_repos": ["repo1", "repo2", "repo3"],
        "expected_licensed_repos": ["repo1"],
        "license_key": "mit"
    }
]

# ---------------- Integration Tests ----------------

@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using the TEST_PAYLOAD fixtures."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # Mock API responses: org → repos
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos without license filter."""
        client = GithubOrgClient("alx")
        self.assertEqual(client.public_repos(), self.expected_repos)

        self.mock_get.assert_any_call("https://api.github.com/orgs/alx")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self):
        """Test public_repos with license filter."""
        # Reset side_effect because previous test consumed it
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload),
        ]

        client = GithubOrgClient("alx")
        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )

        self.mock_get.assert_any_call("https://api.github.com/orgs/alx")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

# ---------------- Unit Tests ----------------

class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        """Test GithubOrgClient.org returns correct JSON."""
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
        """Test has_license static method."""
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)

# ---------------- Run Tests ----------------

if __name__ == "__main__":
    unittest.main()
    