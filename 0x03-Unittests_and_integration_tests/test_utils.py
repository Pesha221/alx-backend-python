#!/usr/bin/env python3
"""Module for testing utils.py functions."""
import unittest
from parameterized import parameterized
from unittest.mock import patch
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
        ({"a": {"b": {"c": 3}}}, ("a", "b", "c"), 3),
    ])
    def test_access_nested_map(self, nested_map: dict, path: tuple, expected: any) -> None:
        """Test that access_nested_map returns the expected value."""
        self.assertEqual(access_nested_map(nested_map, list(path)), expected)

    @parameterized.expand([
        ({}, ("a",), KeyError),
        ({"a": 1}, ("a", "b"), KeyError),
    ])
    def test_access_nested_map_exception(self, nested_map: dict, path: tuple, expected_exception: type) -> None:
        """Test that access_nested_map raises KeyError for invalid paths."""
        with self.assertRaises(expected_exception) as cm:
            access_nested_map(nested_map, list(path))
        
        # Verify that the correct key that caused the error is in the exception message
        # For the first case: KeyError: 'a', for the second: KeyError: 'b'
        self.assertIn(path[-1], str(cm.exception))


class TestGetJson(unittest.TestCase):
    """Tests for the get_json function."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"status": "ok"}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url: str, test_payload: dict, mock_get: patch) -> None: # type: ignore
        """Test that get_json returns the expected JSON payload."""
        
        # Configure the mock object to return a mock response object
        # The mock response object must have a .json() method that returns the test_payload
        mock_response = mock_get.return_value
        mock_response.json.return_value = test_payload

        # Call the function under test
        result = get_json(test_url)

        # Assertions
        # 1. Assert that requests.get was called exactly once with the test_url
        mock_get.assert_called_once_with(test_url)
        # 2. Assert that the result matches the expected payload
        self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """Tests the memoize decorator."""

    def test_memoize(self) -> None:
        """Test that memoize correctly caches the result of a method."""

        class TestClass:
            """Test class for memoize."""

            def a_method(self) -> int:
                """Method to be memoized."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Property decorated with memoize."""
                return self.a_method()

        # Create an instance of the TestClass
        obj = TestClass()

        # Patch a_method to spy on its calls
        with patch.object(obj, 'a_method', return_value=42) as mock_method:
            # 1. First access: Should call a_method
            result1 = obj.a_property
            
            # 2. Second access: Should use the cached result, NOT call a_method
            result2 = obj.a_property

            # Assertions
            # a_method should have been called only once
            mock_method.assert_called_once()
            # Both results should be the expected value (42)
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)


if __name__ == '__main__':
    unittest.main()