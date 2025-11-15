#!/usr/bin/env python3
"""Unit tests for utils.py, covering access_nested_map,
get_json, and memoize."""

import unittest
from unittest.mock import patch
from parameterized import parameterized # type: ignore
from utils import access_nested_map, get_json, memoize # type: ignore


class TestAccessNestedMap(unittest.TestCase):
    """Test access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns correct value."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected_key):
        """Test that access_nested_map raises KeyError with correct key."""
        with self.assertRaises(KeyError) as ctx:
            access_nested_map(nested_map, path)
        self.assertEqual(ctx.exception.args[0], expected_key)


class TestGetJson(unittest.TestCase):
    """Test get_json function with mocked HTTP calls."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(self, test_url, test_payload,
                     mock_get):
        """Test get_json returns expected payload and calls requests.get once."""
        mock_get.return_value.json.return_value = test_payload
        result = get_json(test_url)
        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Test memoize decorator."""

    def test_memoize(self):
        """Test that a memoized property caches the result and calls method once."""

        class TestClass:
            """Sample class for memoize testing."""

            def a_method(self):
                """Return a fixed value."""
                return 42

            @memoize
            def a_property(self):
                """Memoized property calling a_method."""
                return self.a_method()

        with patch.object(
            TestClass, 'a_method', return_value=42
        ) as mocked:
            obj = TestClass()
            # Access property twice
            result1 = obj.a_property
            result2 = obj.a_property

            # Assert returned values are correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            # Assert a_method called only once due to memoization
            mocked.assert_called_once()


if __name__ == '__main__':
    unittest.main()
