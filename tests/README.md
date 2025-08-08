# Tests

This directory contains all test files for the LangChain Agent project.

## Test Files

### Browser Tests
- **`test_single_session_browser.py`** - Tests the single-session browser architecture with process termination
- **`test_browser_diagnostic.py`** - Diagnostic tests for browser launching issues  
- **`test_browser_error_handling.py`** - Tests browser error handling improvements
- **`test_browser_tool_direct.py`** - Direct tests of browser tools
- **`test_browser.py`** - General browser tool tests

### Legacy Tests
- **`test_tools.py`** - Tests for the weather tool (deprecated)
- **`test_weather_removal.py`** - Tests to verify weather tool removal
- **`test_basic.py`** - Basic project structure tests

## Running Tests

### Run Individual Tests
```bash
# From project root directory
python tests/test_single_session_browser.py
python tests/test_browser_diagnostic.py
python tests/test_browser_error_handling.py
```

### Run All Tests
```bash
# Run all tests sequentially
for test in tests/test_*.py; do
    echo "Running $test..."
    python "$test"
    echo "---"
done
```

### Prerequisites
Make sure you have all dependencies installed:
```bash
pip install -r requirements.txt
```

For browser tests, also ensure:
```bash
patchright install chromium
```

## Test Categories

### 🔧 **Diagnostic Tests**
- `test_browser_diagnostic.py` - Helps identify browser setup issues
- `test_basic.py` - Validates basic project structure

### 🧪 **Functionality Tests**  
- `test_single_session_browser.py` - Tests browser architecture
- `test_browser_tool_direct.py` - Tests browser tools directly
- `test_browser_error_handling.py` - Tests error scenarios

### 🧹 **Cleanup Tests**
- `test_weather_removal.py` - Verifies weather tool removal

## Test Results

All tests should output:
- ✅ **PASS** for successful tests
- ❌ **FAIL** for failed tests  
- Detailed error information for debugging

## Notes

- Tests automatically add parent directory to Python path
- Browser tests may take longer due to browser startup time
- Some tests require active browser processes (will be cleaned up automatically)
- All browser tests use the single-session architecture with proper process termination
