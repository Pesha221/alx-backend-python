#!/usr/bin/env python3
"""Integration and unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD, MockResponse

@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using parameterized_class."""

    @classmethod
    def setUpClass(cls):
        # Patch requests.get for the whole class
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        # Set the side_effect for requests.get: org, then repos
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload)
        ]

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("alx")
        self.assertEqual(client.public_repos(), self.expected_repos)
        org_url = f"https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)

    def test_public_repos_with_license(self):
        # Reset the mock for this test run
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload)
        ]
        client = GithubOrgClient("alx")
        self.assertEqual(
            client.public_repos(license=self.license_key),
            self.expected_licensed_repos
        )
        org_url = f"https://api.github.com/orgs/alx"
        repos_url = self.org_payload["repos_url"]
        self.mock_get.assert_any_call(org_url)
        self.mock_get.assert_any_call(repos_url)

class TestGithubOrgClient(unittest.TestCase):
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123456, "repos_url": "mock_url"}
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
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

if __name__ == "__main__":
    unittest.main()