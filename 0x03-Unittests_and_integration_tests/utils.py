#!/usr/bin/env python3
"""Unit and integration tests for GithubOrgClient."""

import unittest
# IMPORT FIX: Added Mock to the import list for use in integration tests
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD, MockResponse


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
    """Integration tests for GithubOrgClient using requests.get."""

    @classmethod
    def setUpClass(cls):
        """Patch requests.get and set side effects."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        # FIX 1: Use Mock objects with json.return_value for robust side_effect handling.
        # This simulates a requests.Response object having a .json() method 
        # and prevents the common error of exhausting side_effect lists in parameterized integration tests.
        cls.mock_get.side_effect = [
            Mock(**{'json.return_value': cls.org_payload}),
            Mock(**{'json.return_value': cls.repos_payload})
        ]

    @classmethod
    def tearDownClass(cls):
        """Undo the patch."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test that public_repos returns expected repo list."""
        client = GithubOrgClient("my_org")

        self.assertEqual(client.public_repos(), self.expected_repos)

        self.mock_get.assert_any_call(
            "https://api.github.com/orgs/my_org"
        )
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self):
        """Test filtering repos by license."""
        # FIX 2: Reset side_effect for this test using Mock objects. 
        # This is necessary because the previous test run has already consumed the mock side effects 
        # set up in setUpClass, and we need a fresh pair of mocked responses.
        self.mock_get.side_effect = [
            Mock(**{'json.return_value': self.org_payload}),
            Mock(**{'json.return_value': self.repos_payload})
        ]

        client = GithubOrgClient("my_org")

        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )

        self.mock_get.assert_any_call(
            "https://api.github.com/orgs/my_org"
        )
        self.mock_get.assert_any_call(self.org_payload["repos_url"])


# ================== Unit Tests ==================

class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    # Note: Patching the internal helper method is usually safer than patching the utility function.
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that org property returns expected JSON."""
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
        """Test static method has_license."""
        self.assertEqual(
            GithubOrgClient.has_license(repo, license_key),
            expected
        )


if __name__ == "__main__":
    unittest.main()