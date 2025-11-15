#!/usr/bin/env python3
"""
Unit tests for utils.py
"""

import unittest
from parameterized import parameterized
from unittest.mock import patch
import utils


class TestAccessNestedMap(unittest.TestCase):
    """Tests for the access_nested_map function"""

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """Test regular access"""
        self.assertEqual(utils.access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(self, nested_map, path):
        """Test that a KeyError is raised for missing keys"""
        with self.assertRaises(KeyError) as err:
            utils.access_nested_map(nested_map, path)

        # Check that the KeyError message matches the missing key
        self.assertEqual(str(err.exception), repr(path[-1]))


class TestGetJson(unittest.TestCase):
    """Tests for the get_json function"""

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    @patch("utils.requests.get")
    def test_get_json(self, test_url, test_payload, mock_get):
        """Test that get_json returns expected JSON payload"""

        # Create a mock response object with a .json() method
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = test_payload
        mock_get.return_value = mock_response

        result = utils.get_json(test_url)

        # Assertions
        self.assertEqual(result, test_payload)
        mock_get.assert_called_once_with(test_url)
