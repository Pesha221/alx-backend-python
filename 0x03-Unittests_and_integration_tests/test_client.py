#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient."""
import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from client import GithubOrgClient
from utils import get_json


class TestGithubOrgClient(unittest.TestCase):
    """Tests for GithubOrgClient.org property."""

    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """Test that GithubOrgClient.org returns the correct organization."""
        expected_url = f"https://api.github.com/orgs/{org_name}"
        expected_payload = {"org": org_name}

        # Mock get_json return value
        mock_get_json.return_value = expected_payload

        # Create client instance
        client = GithubOrgClient(org_name)

        # Access the .org property
        result = client.org

        # Assertions
        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)


if __name__ == "__main__":
    unittest.main()

