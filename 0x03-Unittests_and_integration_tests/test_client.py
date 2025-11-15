#!/usr/bin/env python3
"""
Unit tests for GithubOrgClient
"""
import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """Unit tests for the GithubOrgClient.org method"""

    @parameterized(
        [
            ("google",),
            ("abc",),
        ]
    )
    @patch("client.requests.get")
    def test_org(self, org_name, mock_get):
        """Test org returns expected data"""
        mock_get.return_value.json.return_value = org_payload
        client = GithubOrgClient(org_name)
        self.assertEqual(client.org, org_payload)
        mock_get.assert_called_once_with(
            "https://api.github.com/orgs/{}".format(org_name)
        )


class TestPublicRepos(unittest.TestCase):
    """Tests for GithubOrgClient.public_repos"""

    @patch("client.GithubOrgClient.org", new_callable=PropertyMock)
    @patch("client.requests.get")
    def test_public_repos(self, mock_get, mock_org):
        """Test the public repos list"""
        mock_org.return_value = org_payload
        mock_get.return_value.json.return_value = repos_payload

        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), expected_repos)

        mock_org.assert_called_once()
        mock_get.assert_called_once_with(org_payload.get("repos_url"))

    @patch("client.requests.get")
    def test_public_repos_url(self, mock_get):
        """Tests the _public_repos_url property"""
        mock_get.return_value.json.return_value = org_payload
        client = GithubOrgClient("google")
        self.assertEqual(client._public_repos_url, org_payload["repos_url"])


class TestHasLicense(unittest.TestCase):
    """Tests for has_license"""

    def test_has_license(self):
        repo = {"license": {"key": "apache-2.0"}}
        self.assertTrue(GithubOrgClient.has_license(repo, "apache-2.0"))
        self.assertFalse(GithubOrgClient.has_license(repo, "bsd-3"))


@parameterized_class(
    [
        {
            "org_payload": org_payload,
            "repos_payload": repos_payload,
            "expected_repos": expected_repos,
            "apache2_repos": apache2_repos,
        }
    ]
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests using fixtures"""

    @classmethod
    def setUpClass(cls):
        """Start patchers"""
        cls.get_patcher = patch("requests.get")
        mock_get = cls.get_patcher.start()

        mock_get.side_effect = [
            unittest.mock.Mock(json=lambda: cls.org_payload),
            unittest.mock.Mock(json=lambda: cls.repos_payload),
        ]

    @classmethod
    def tearDownClass(cls):
        """Stop patchers"""
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test all public repos"""
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """Test filtering repos by license"""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos("apache-2.0"), self.apache2_repos
        )
