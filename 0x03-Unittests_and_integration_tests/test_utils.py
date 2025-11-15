#!/usr/bin/env python3
"""Module for testing client.py functions."""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized, parameterized_class # type: ignore
from client import GithubOrgClient # type: ignore
from fixtures import TEST_PAYLOAD # type: ignore


class TestGithubOrgClient(unittest.TestCase):
    """Tests for the GithubOrgClient class."""

    @parameterized.expand([
        ("google", {"login": "google"}),
        ("abc", {"login": "abc"}),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, expected_org: dict, mock_get_json: patch) -> None:
        """Test that GithubOrgClient.org returns the expected dictionary."""

        # Configure the mock to return the expected_org dictionary
        mock_get_json.return_value = expected_org

        # Instantiate the client
        client = GithubOrgClient(org_name)

        # Call the method
        result = client.org

        # Assertions
        # 1. Assert that the result is the expected org dictionary
        self.assertEqual(result, expected_org)

        # 2. Assert that get_json was called exactly once with the correct URL
        expected_url = (
            f"https://api.github.com/orgs/{org_name}"
        )
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """Test that _public_repos_url returns the correct repos_url from org data."""

        # Define a mock organization payload containing a 'repos_url' key
        test_org_payload = {
            "repos_url": "https://api.github.com/orgs/testorg/repos"
        }

        # Patch the org property (memoized) to return the test_org_payload
        with patch.object(GithubOrgClient, 'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = test_org_payload

            # Instantiate the client
            client = GithubOrgClient("testorg")

            # Access the property under test
            result = client._public_repos_url

            # Assertions
            # 1. Assert that the result matches the repos_url from the payload
            self.assertEqual(result, test_org_payload["repos_url"])

            # 2. Assert that the org property was accessed exactly once
            mock_org.assert_called_once()

    @patch('client.get_json')
    def test_repos_payload(self, mock_get_json: patch) -> None:
        """Test that repos_payload calls get_json with the correct URL."""

        # Define mock values for the org and repo payload
        test_repos_url = "https://api.github.com/orgs/testorg/repos"
        test_repos_payload = [{"name": "repo1"}, {"name": "repo2"}]

        # Configure the mock for get_json
        mock_get_json.return_value = test_repos_payload

        # Patch the _public_repos_url property to control the URL used
        with patch.object(GithubOrgClient, '_public_repos_url',
                          new_callable=PropertyMock) as mock_url:
            mock_url.return_value = test_repos_url

            # Instantiate the client
            client = GithubOrgClient("testorg")

            # Call the repos_payload method
            result = client.repos_payload

            # Assertions
            self.assertEqual(result, test_repos_payload)
            mock_get_json.assert_called_once_with(test_repos_url)
            mock_url.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "bsd-3-clause"}}, "apache-2.0", False),
        ({"license": {"key": "apache-2.0"}}, "bsd-3-clause", False),
        ({}, "apache-2.0", False),
        ({"license": None}, "apache-2.0", False),
    ])
    def test_has_license(self, repo: dict, license_key: str, expected: bool) -> None:
        """Test that has_license returns the expected boolean value."""
        result = GithubOrgClient.has_license(repo, license_key)
        assert result == expected

