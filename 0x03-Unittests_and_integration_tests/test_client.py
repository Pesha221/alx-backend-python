#!/usr/bin/env python3
"""Integration and unit tests for client.GithubOrgClient."""

import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient  # type: ignore
from fixtures import TEST_PAYLOAD, MockResponse  # type: ignore


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for GithubOrgClient."""

    @parameterized(("google",), ("abc",))
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct data."""
        mock_get_json.return_value = {"payload": True}
        client = GithubOrgClient(org_name)
        result = client.org
        self.assertEqual(result, {"payload": True})
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    @patch("client.GithubOrgClient.org", new_callable=MagicMock)
    def test_public_repos_url(self, mock_org):
        """Test _public_repos_url returns correct repos_url."""
        mock_org.return_value = {"repos_url": "http://example.com/repos"}
        client = GithubOrgClient("google")
        self.assertEqual(client._public_repos_url,
                         "http://example.com/repos")

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns correct list."""
        mock_get_json.return_value = [{"name": "repo1"}, {"name": "repo2"}]
        client = GithubOrgClient("google")

        with patch.object(
            GithubOrgClient,
            "_public_repos_url",
            new_callable=MagicMock,
            return_value="http://example.com/repos",
        ):
            result = client.public_repos()
            self.assertEqual(result, ["repo1", "repo2"])

    @parameterized(
        ({"license": {"key": "my_key"}}, "my_key", True),
        ({"license": {"key": "other"}}, "my_key", False),
    )
    def test_has_license(self, repo, license_key, expected):
        """Test GithubOrgClient.has_license returns correct boolean."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos",
     "license_key", "expected_licensed_repos"),
    [
        {
            "org_payload": TEST_PAYLOAD[0]["org_payload"],
            "repos_payload": TEST_PAYLOAD[0]["repos_payload"],
            "expected_repos": TEST_PAYLOAD[0]["expected_repos"],
            "license_key": TEST_PAYLOAD[0]["license_key"],
            "expected_licensed_repos":
                TEST_PAYLOAD[0]["expected_licensed_repos"],
        }
    ],
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using fixtures."""

    @classmethod
    def setUpClass(cls):
        """Start patching requests.get."""
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),
            MockResponse(cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patching requests.get."""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos using fixture payload."""
        client = GithubOrgClient("alx")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)

    def test_public_repos_with_license(self):
        """Test public_repos with license filtering."""
        # Reset for second call
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload),
        ]

        client = GithubOrgClient("alx")
        result = client.public_repos(license=self.license_key)
        self.assertEqual(result, self.expected_licensed_repos)
