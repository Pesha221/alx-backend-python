#!/usr/bin/env python3
"""Unit tests for utils.py, covering access_nested_map, get_json,
and memoize.
"""

import unittest
from typing import Any, Dict, Tuple
from unittest.mock import patch
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """Unit tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict,
        path: Tuple[str, ...],
        expected: Any
    ) -> None:
        """Test that access_nested_map returns the expected value."""
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), "a"),
        ({"a": 1}, ("a", "b"), "b"),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict,
        path: Tuple[str, ...],
        expected_key: str
    ) -> None:
        """Test that access_nested_map raises KeyError with the correct key."""
        with self.assertRaises(KeyError) as ctx:
            access_nested_map(nested_map, path)
        self.assertEqual(ctx.exception.args[0], expected_key)


class TestGetJson(unittest.TestCase):
    """Unit tests for the get_json function with mocked HTTP calls."""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch('utils.requests.get')
    def test_get_json(  # E501: Split arguments onto separate lines
        self,
        test_url: str,
        test_payload: Dict[str, Any],
        mock_get: patch
    ) -> None:
        """
        Test get_json returns the expected JSON payload and
        calls requests.get once.  # E501: Split line
        
        Args:
            test_url: URL to fetch.
            test_payload: Expected JSON response from the mock.
            mock_get: Mocked requests.get method.
        """
        mock_get.return_value.json.return_value = test_payload
        result = get_json(test_url)
        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)


class TestMemoize(unittest.TestCase):
    """Unit tests for the memoize decorator."""

    def test_memoize(self) -> None:
        """Test that a memoized property caches the result and calls method once."""

        class TestClass:
            """Sample class to test memoization behavior."""

            def a_method(self) -> int:
                """Return a fixed integer value."""
                return 42

            @memoize
            def a_property(self) -> int:
                """Memoized property that calls a_method once."""
                return self.a_method()

        with patch.object(
            TestClass,
            'a_method',
            return_value=42
        ) as mocked:
            obj = TestClass()
            result1 = obj.a_property
            result2 = obj.a_property

            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mocked.assert_called_once()


if __name__ == '__main__':
    unittest.main()







