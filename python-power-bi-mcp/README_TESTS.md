# Power BI MCP Test Suite

This directory contains comprehensive tests for the Power BI MCP project models.

## Test Structure

The test suite is organized as follows:

- **`conftest.py`** - Pytest configuration, fixtures, and cleanup options
- **`test_report.py`** - Tests for the Report class
- **`test_pages.py`** - Tests for the Pages class
- **`test_page.py`** - Tests for the Page class
- **`test_visual.py`** - Tests for the Visual class
- **`test_integration.py`** - Integration tests for models working together

## Cleanup Options

The test suite provides three cleanup options to control what happens to test data after test runs:

### 1. Clean After Run (Default)

- **Option**: `--cleanup-option clean`
- **Behavior**: All test data is cleaned up after each test run, regardless of test results
- **Use Case**: When you want a clean environment and don't need to inspect test artifacts

### 2. Clean Expected Failures After Run

- **Option**: `--cleanup-option clean-failures`
- **Behavior**: Test data is cleaned up only for tests that pass. Failed tests leave their data for inspection
- **Use Case**: When you want to investigate test failures and see what was created

### 3. Keep All Test Data

- **Option**: `--cleanup-option keep`
- **Behavior**: No test data is cleaned up. All test artifacts remain for manual inspection
- **Use Case**: When you want to manually examine all test outputs and Power BI projects

## Running Tests

### Using the Test Runner Script

```bash
# Run all tests with default cleanup (clean after run)
python run_tests.py

# Run tests with coverage
python run_tests.py --coverage

# Run tests with verbose output
python run_tests.py --verbose

# Run tests with no cleanup
python run_tests.py --cleanup-option keep

# Run tests with cleanup only for expected failures
python run_tests.py --cleanup-option clean-failures

# Show available test markers
python run_tests.py --markers

# Collect tests without running them
python run_tests.py --collect-only
```

### Using Pytest Directly

```bash
# Run all tests
pytest tests/

# Run with specific cleanup option
pytest tests/ --cleanup-option keep

# Run specific test file
pytest tests/test_report.py

# Run tests with specific marker
pytest tests/ -m unit
pytest tests/ -m integration

# Run with coverage
pytest tests/ --cov=models --cov-report=html
```

## Test Markers

The test suite uses the following markers:

- **`@pytest.mark.unit`** - Unit tests for individual components
- **`@pytest.mark.integration`** - Integration tests for components working together
- **`@pytest.mark.slow`** - Slow-running tests
- **`@pytest.mark.cleanup`** - Tests that create test data

## Test Coverage

The test suite covers:

### Report Class

- Initialization with existing and non-existing reports
- Baseline report copying and file renaming
- PBIP file reference updates
- Report structure loading
- Page management (add, remove, get)
- File existence checks and path management

### Pages Class

- Pages metadata loading and management
- Page order and active page management
- Page addition and removal
- File persistence and error handling

### Page Class

- Page data loading and validation
- Visual loading and management
- Property getters and setters
- File operations (write, remove)
- Error handling for missing files

### Visual Class

- Visual data loading and validation
- Position and type management
- File operations (write, remove)
- Directory cleanup on removal
- Error handling for corrupted files

### Integration Tests

- Complete workflow testing
- Multiple pages with multiple visuals
- Error handling and recovery
- File persistence and consistency
- Cross-component interactions

## Test Data Management

### Mock Baseline Report

Tests use a mock baseline report structure that includes:

- Basic report structure with pages
- Sample page with metadata
- PBIP file with proper references

### Temporary Directories

Tests create temporary directories for:

- Test reports
- Test pages
- Test visuals
- Mock baseline data

### Cleanup Fixtures

The `cleanup_test_data` fixture automatically manages test data cleanup based on the selected cleanup option.

## Power BI Project Structure

Tests create and manipulate Power BI projects with the following structure:

```
test_report/
├── test_report.Report/
│   └── definition/
│       └── pages/
│           ├── pages.json
│           ├── ReportSection/
│           │   ├── page.json
│           │   └── visuals/
│           └── NewPage/
│               ├── page.json
│               └── visuals/
│                   └── visual_name/
│                       └── visual.json
├── test_report.Dataset/
└── test_report.pbip
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running tests from the project root directory
2. **File Permission Errors**: Check that the test user has write permissions to the test directory
3. **Cleanup Failures**: Some files may be locked by the OS; this is handled gracefully

### Debug Mode

To debug test issues, use the "keep" option to inspect test artifacts:

```bash
python run_tests.py --cleanup-option keep --verbose
```

This will leave all test data intact for manual inspection.

### Test Isolation

Each test function runs in isolation with its own temporary directories. Tests do not interfere with each other, ensuring reliable test results.

## Contributing

When adding new tests:

1. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
2. Follow the existing test patterns
3. Include proper cleanup in test fixtures
4. Test both success and error scenarios
5. Add comprehensive assertions for expected behavior

## Dependencies

The test suite requires:

- pytest
- pytest-cov (for coverage reports)
- pytest-mock (for mocking)
- All project dependencies from requirements.txt
