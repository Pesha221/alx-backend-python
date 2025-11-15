# Unit Tests for utils.py

This folder contains unit tests for the utility functions in `utils.py`. These tests cover:

1. **`access_nested_map`** – Accessing values in nested dictionaries.
2. **`get_json`** – Fetching JSON data from a URL.
3. **`memoize`** – Caching the result of a method call to avoid repeated computations.

---

## 1. TestAccessNestedMap

**File:** `test_utils.py`  
**Class:** `TestAccessNestedMap`

### Purpose:
Tests the `access_nested_map` function to ensure it correctly retrieves values from nested dictionaries and raises exceptions for invalid paths.

### Tests:

- `test_access_nested_map`  
  Checks normal behavior with different nested maps and key paths:
  ```python
  nested_map={"a": 1}, path=("a",)
  nested_map={"a": {"b": 2}}, path=("a",)
  nested_map={"a": {"b": 2}}, path=("a", "b")
