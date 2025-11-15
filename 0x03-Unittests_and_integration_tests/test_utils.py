import unittest


class TestMemoize(unittest.TestCase):
    """Test memoize decorator."""

    def test_memoize(self):
        """Test that a memoized property caches the result and calls method once."""

        class TestClass:
            """Sample class for memoize testing."""

            def a_method(self):
                """Return a fixed value."""
                return 42

            @memoize # type: ignore
            def a_property(self):
                """Memoized property calling a_method."""
                return self.a_method()

        
        with patch.object( # type: ignore
            TestClass,
            'a_method',
            return_value=42
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

