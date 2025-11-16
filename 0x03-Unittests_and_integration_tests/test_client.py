import unittest
from unittest.mock import patch
from parameterized import parameterized_class
from client import GithubOrgClient  # Your implementation
from fixtures import TEST_PAYLOAD, MockResponse  # Your fixtures

@parameterized_class(TEST_PAYLOAD)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """Integration tests for GithubOrgClient using requests.get patching."""

    @classmethod
    def setUpClass(cls):
        cls.get_patcher = patch("requests.get")
        cls.mock_get = cls.get_patcher.start()
        # Patch responses to return actual MockResponse objects
        cls.mock_get.side_effect = [
            MockResponse(cls.org_payload),   # First call should be org info
            MockResponse(cls.repos_payload) # Second call gets repos list
        ]

    @classmethod
    def tearDownClass(cls):
        cls.get_patcher.stop()

    def test_public_repos(self):
        """Test public_repos returns correct repo list based on fixtures."""
        client = GithubOrgClient("org")
        result = client.public_repos()
        self.assertEqual(result, self.expected_repos)
        self.mock_get.assert_any_call("https://api.github.com/orgs/org")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

    def test_public_repos_with_license(self):
        """Test public_repos with license='apache-2.0' returns correct filter."""
        # Reset responses for second test
        self.mock_get.side_effect = [
            MockResponse(self.org_payload),
            MockResponse(self.repos_payload)
        ]
        client = GithubOrgClient("org")
        result = client.public_repos(license="apache-2.0")
        self.assertEqual(result, self.expected_licensed_repos)
        self.mock_get.assert_any_call("https://api.github.com/orgs/org")
        self.mock_get.assert_any_call(self.org_payload["repos_url"])

if __name__ == "__main__":
    unittest.main()


