#!/usr/bin/env python3
"""Unittests for client.py."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class

from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """Test cases for GithubOrgClient."""

    @parameterized.expand([
        ("google",),
        ("abc",)
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test org method."""
        client = GithubOrgClient(org_name)
        client.org()
        mock_get_json.assert_called_once_with(
            f"https://api.github.com/orgs/{org_name}"
        )

    def test_public_repos_url(self):
        """Test the _public_repos_url property."""
        payload = {"repos_url": "http://example.com/repos"}
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock,
            return_value=payload
        ):
            client = GithubOrgClient("test")
            self.assertEqual(client._public_repos_url, payload["repos_url"])

    @patch("client.get_json")
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns expected repository names."""
        mock_get_json.return_value = TEST_PAYLOAD[0]["repos_payload"]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
            return_value="http://example.com/repos"
        ):
            client = GithubOrgClient("test")
            self.assertEqual(
                client.public_repos(),
                TEST_PAYLOAD[0]["expected_repos"]
            )
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ("apache-2.0", TEST_PAYLOAD[0]["expected_licensed_repos"]),
    ])
    @patch("client.get_json")
    def test_public_repos_with_license(self, license_key,
                                       expected, mock_get_json):
        """Test public_repos with license filtering."""
        mock_get_json.return_value = TEST_PAYLOAD[0]["repos_payload"]
        with patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
            return_value="http://example.com/repos"
        ):
            client = GithubOrgClient("test")
            self.assertEqual(
                client.public_repos(license=license_key),
                expected
            )
            mock_get_json.assert_called_once()


class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests."""

    @classmethod
    def setUpClass(cls):
        """Start patchers."""
        cls.get_json_patch = patch("client.get_json",
                                   return_value=TEST_PAYLOAD[0]["org_payload"])
        cls.get_json_mock = cls.get_json_patch.start()

        cls.public_repos_url_patch = patch(
            "client.GithubOrgClient._public_repos_url",
            new_callable=PropertyMock,
            return_value="http://example.com/repos"
        )
        cls.public_repos_url_mock = cls.public_repos_url_patch.start()

    @classmethod
    def tearDownClass(cls):
        """Stop patchers."""
        cls.get_json_patch.stop()
        cls.public_repos_url_patch.stop()

    @patch("client.get_json",
           return_value=TEST_PAYLOAD[0]["repos_payload"])
    def test_public_repos(self, mock_get_json):
        """Integration test for public_repos."""
        client = GithubOrgClient("google")
        self.assertEqual(
            client.public_repos(),
            TEST_PAYLOAD[0]["expected_repos"]
        )
