#!/usr/bin/env python3
import unittest
from unittest.mock import patch
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient # type: ignore
from fixtures import TEST_PAYLOAD, MockResponse # type: ignore

@parameterized.expand([
    {
        "org_payload": TEST_PAYLOAD[0]["org_payload"],
        "repos_payload": TEST_PAYLOAD[0]["repos_payload"],
        "expected_repos": TEST_PAYLOAD[0]["expected_repos"],
        "expected_licensed_repos": TEST_PAYLOAD[0]["expected_licensed_repos"],
        "license_key": TEST_PAYLOAD[0]["license_key"],
    }
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests"""

    @classmethod
    def setUpClass(cls):
        """Set up requests.get patcher"""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()

        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Tear down requests.get patcher"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        client = GithubOrgClient("alx")

        self.assertEqual(client.public_repos(), self.expected_repos)
        self.mock_get.assert_any_call("https://api.github.com/orgs/alx")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self):
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


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests"""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.GithubOrgClient._get_json")
    def test_org(self, org_name, mock_get_json):
        expected_payload = {"id": 1, "repos_url": "http://example.com"}
        expected_url = f"https://api.github.com/orgs/{org_name}"

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
        self.assertEqual(GithubOrgClient.has_license(repo, license_key), expected)


if __name__ == "__main__":
    unittest.main()
        