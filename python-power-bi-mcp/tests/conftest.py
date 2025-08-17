"""
Pytest configuration and fixtures for Power BI MCP tests
"""
import pytest
import shutil
import json
from pathlib import Path
from typing import Generator, Dict, Any
from enum import Enum


class CleanupOption(Enum):
    """Options for cleaning up test data after test runs"""
    CLEAN_AFTER_RUN = "clean"
    CLEAN_EXPECTED_FAILURES_AFTER_RUN = "clean-failures"
    CLEAN_NONE_AFTER_RUN = "keep"


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--cleanup-option",
        action="store",
        default=CleanupOption.CLEAN_AFTER_RUN.value,
        choices=[option.value for option in CleanupOption],
        help="Cleanup option for test data: clean after run, clean expected failures after run, or clean none after run"
    )


@pytest.fixture(scope="session")
def cleanup_option(request) -> CleanupOption:
    """Get the cleanup option from command line"""
    option_value = request.config.getoption("--cleanup-option")
    return CleanupOption(option_value)


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Get the test data directory"""
    return Path("test_data")


@pytest.fixture(scope="session")
def baseline_report_path() -> Path:
    """Get the baseline report path"""
    return Path("baseline_report")


@pytest.fixture(scope="function")
def temp_report_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary directory for test reports"""
    temp_dir = tmp_path / "test_reports"
    temp_dir.mkdir(exist_ok=True)
    yield temp_dir
    # Cleanup is handled by the cleanup fixture


@pytest.fixture(scope="function")
def cleanup_test_data(request, cleanup_option: CleanupOption, test_data_dir: Path):
    """Cleanup test data based on the cleanup option"""
    yield
    
    # Determine if we should cleanup based on the option and test result
    should_clean = False
    
    if cleanup_option == CleanupOption.CLEAN_AFTER_RUN:
        should_clean = True
    elif cleanup_option == CleanupOption.CLEAN_EXPECTED_FAILURES_AFTER_RUN:
        # Only cleanup if test passed (expected failures would be marked as xfail)
        should_clean = not hasattr(request.node, '_outcome') or request.node._outcome.success
    # CLEAN_NONE_AFTER_RUN: never cleanup
    
    if should_clean and test_data_dir.exists():
        try:
            shutil.rmtree(test_data_dir)
        except Exception as e:
            print(f"Warning: Could not cleanup test data: {e}")


@pytest.fixture(scope="function")
def mock_baseline_report(tmp_path: Path, baseline_report_path: Path) -> Generator[Path, None, None]:
    """Create a mock baseline report for testing"""
    mock_baseline = tmp_path / "mock_baseline"
    
    # Create complete directory structure first
    pages_metadata_dir = mock_baseline / "report_sample.Report" / "definition" / "pages"
    pages_metadata_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the pages subdirectory where actual page files go
    pages_dir = pages_metadata_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the specific page directory
    page_dir = pages_dir / "ReportSection"
    page_dir.mkdir(parents=True, exist_ok=True)
    
    # Create visuals directory for the page
    visuals_dir = page_dir / "visuals"
    visuals_dir.mkdir(parents=True, exist_ok=True)
    
    # Create dataset directory
    dataset_dir = mock_baseline / "report_sample.Dataset" / "definition"
    dataset_dir.mkdir(parents=True, exist_ok=True)
    
    # Create basic files
    pages_json = {
        "pageOrder": ["ReportSection"],
        "activePageName": "ReportSection",
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"
    }
    
    page_json = {
        "name": "ReportSection",
        "displayName": "Report Section",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
    }
    
    pbip_json = {
        "artifacts": [
            {
                "report": {
                    "path": "report_sample.Report"
                }
            }
        ]
    }
    
    # Write files
    with open(pages_metadata_dir / "pages.json", 'w') as f:
        json.dump(pages_json, f, indent=2)
    
    with open(page_dir / "page.json", 'w') as f:
        json.dump(page_json, f, indent=2)
    
    with open(mock_baseline / "report_sample.pbip", 'w') as f:
        json.dump(pbip_json, f, indent=2)
    
    yield mock_baseline


@pytest.fixture(scope="function")
def sample_visual_data():
    """Sample visual data for testing"""
    return {
        "name": "test_visual",
        "position": {
            "x": 100.0,
            "y": 200.0,
            "z": 0.0,
            "height": 300.0,
            "width": 400.0
        },
        "visual": {
            "visualType": "card",
            "drillFilterOtherVisuals": True
        },
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.1.0/schema.json"
    }


@pytest.fixture(scope="function")
def sample_page_data():
    """Sample page data for testing"""
    return {
        "name": "test_page",
        "displayName": "Test Page",
        "displayOption": "FitToPage",
        "height": 720,
        "width": 1280,
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
    }
