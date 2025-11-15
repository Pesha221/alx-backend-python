#!/usr/bin/env python3
"""Unit tests for client.GithubOrgClient"""

import unittest
from unittest.mock import patch, PropertyMock, MagicMock
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
        
        # Configure the mock to return the expected payload
        mock_get_json.return_value = expected_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, expected_payload)
        mock_get_json.assert_called_once_with(expected_url)

# ---

class TestGithubOrgClientRepos(unittest.TestCase):
    """Tests for public_repos and related methods."""
    
    # Define payload fixtures
    ORG_PAYLOAD = {"repos_url": "https://api.github.com/users/google/repos"}
    REPOS_PAYLOAD = [
        {"name": "repo1", "license": {"key": "apache-2.0"}},
        {"name": "repo2", "license": {"key": "mit"}},
        {"name": "repo3", "license": None},
        {"name": "repo4", "license": {"key": "apache-2.0"}},
    ]

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """Test public_repos returns the expected list of repos."""
        
        # Configure mock_get_json to return the REPOS_PAYLOAD
        mock_get_json.return_value = self.REPOS_PAYLOAD
        
        # Patch the _public_repos_url property to prevent an external call
        with patch(
            'client.GithubOrgClient._public_repos_url',
            new_callable=PropertyMock,
        ) as mock_public_repos_url:
            
            # Configure the patched property to return the mock URL
            mock_public_repos_url.return_value = self.ORG_PAYLOAD["repos_url"]
            
            client = GithubOrgClient("google")
            repos = client.public_repos()

            expected_repos = ["repo1", "repo2", "repo3", "repo4"]
            self.assertEqual(repos, expected_repos)
            
            # Assert that get_json was called with the correct repos URL
            mock_get_json.assert_called_once_with(self.ORG_PAYLOAD["repos_url"])

    @parameterized.expand([
        ({"license": {"key": "apache-2.0"}}, "apache-2.0", True),
        ({"license": {"key": "mit"}}, "apache-2.0", False),
        ({}, "apache-2.0", False),  # Missing 'license'
        ({"license": {"key": "mit"}}, "mit", True),
    ])
    def test_has_license(self, repo, license_key, expected):
        """Test the static method has_license."""
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)

# ---

class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient."""

    @classmethod
    @patch('client.get_json')
    def setUpClass(cls, mock_get_json):
        """Set up class fixtures for integration tests."""
        
        # Define payloads
        cls.ORG_PAYLOAD = {"repos_url": "https://api.github.com/users/google/repos"}
        cls.REPOS_PAYLOAD = [
            {"name": "repo1", "license": {"key": "apache-2.0"}},
            {"name": "repo2", "license": {"key": "mit"}},
        ]
        
        # Create a side_effect function to control which payload is returned
        def side_effect(url):
            if url == GithubOrgClient.ORG_URL.format(org="google"):
                return cls.ORG_PAYLOAD
            if url == cls.ORG_PAYLOAD["repos_url"]:
                return cls.REPOS_PAYLOAD
            return None

        # Apply the side_effect to the mocked get_json
        mock_get_json.side_effect = side_effect
        cls.get_json_mock = mock_get_json

    @classmethod
    def tearDownClass(cls):
        """Remove the mock after integration tests."""
        cls.get_json_mock.stop()

    def test_public_repos_with_license(self):
        """Test public_repos with a specific license filter."""
        client = GithubOrgClient("google")
        
        # Test case: Filter by 'apache-2.0'
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, ["repo1"])
        
        # Test case: Filter by 'mit'
        repos = client.public_repos(license="mit")
        self.assertEqual(repos, ["repo2"])
        
        # Test case: No license filter
        repos = client.public_repos()
        self.assertEqual(repos, ["repo1", "repo2"])

if __name__ == "__main__":
    unittest.main()