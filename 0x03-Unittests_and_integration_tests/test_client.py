#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock
from parameterized import parameterized
from client import GithubOrgClient # type: ignore


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient class."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch("client.get_json")
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns correct payload
        and calls get_json exactly once.
        """
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"id": 123, "repos_url": "mock_url"}
        
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

    # New method implementation starts here
    def test_public_repos_url(self):
        """
        Tests that the result of _public_repos_url is the expected one
        based on the mocked payload returned by the .org property.
        """
        # Define the payload that the client.org method is expected to return
        # The key we are interested in is 'repos_url'
        mock_org_payload = {
            "repos_url": "https://api.github.com/orgs/alx/repos"
        }

        # Use patch as a context manager to mock the 'org' method/property
        with patch(
            "client.GithubOrgClient.org",
            new_callable=PropertyMock, # Use PropertyMock since it's a memoized method/property
            return_value=mock_org_payload
        ):
            client = GithubOrgClient("alx")
            
            # Access the property under test
            result_url = client._public_repos_url
            
            # Assert that the result matches the value from the mocked payload
            self.assertEqual(result_url, mock_org_payload["repos_url"])
            
            
            client.org.assert_called_once()