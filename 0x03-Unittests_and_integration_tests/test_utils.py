#!/usr/bin/env python3
"""
Unit tests for utils.access_nested_map.
Test cases verify correct access to values
in nested mappings using a key path.
"""

import unittest
from parameterized import parameterized # pyright: ignore[reportMissingImports]
from utils import access_nested_map # pyright: ignore[reportMissingImports]


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function."""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test that access_nested_map returns the correct value."""
        self.assertEqual(access_nested_map(nested_map, path), expected)


if __name__ == "__main__":
    unittest.main()
