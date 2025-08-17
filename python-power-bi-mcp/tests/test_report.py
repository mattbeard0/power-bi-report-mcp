"""
Tests for the Report class
"""
import pytest
import shutil
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from models.report import Report
from models.pages.pages import Pages


class TestReport:
    """Test cases for the Report class"""
    
    @pytest.mark.unit
    def test_report_initialization_with_existing_report(self, temp_report_dir, mock_baseline_report):
        """Test Report initialization when report already exists"""
        # Create a test report directory
        test_report_path = temp_report_dir / "test_report"
        shutil.copytree(mock_baseline_report, test_report_path)
        
        # Rename files to match test_report
        old_report_folder = test_report_path / "report_sample.Report"
        new_report_folder = test_report_path / "test_report.Report"
        old_report_folder.rename(new_report_folder)
        
        old_dataset_folder = test_report_path / "report_sample.Dataset"
        new_dataset_folder = test_report_path / "test_report.Dataset"
        old_dataset_folder.rename(new_dataset_folder)
        
        old_pbip = test_report_path / "report_sample.pbip"
        new_pbip = test_report_path / "test_report.pbip"
        old_pbip.rename(new_pbip)
        
        # Update pbip references
        with open(new_pbip, 'r') as f:
            pbip_data = json.load(f)
        pbip_data['artifacts'][0]['report']['path'] = "test_report.Report"
        with open(new_pbip, 'w') as f:
            json.dump(pbip_data, f, indent=2)
        
        # Create report first, then set the baseline path
        report = Report("test_report")
        report.baseline_path = test_report_path
        
        assert report.name == "test_report"
        assert report.report_path == Path("reports") / "test_report"
        assert report.exists()
    
    @pytest.mark.unit
    def test_report_initialization_without_existing_report(self, temp_report_dir, mock_baseline_report):
        """Test Report initialization when report doesn't exist"""
        # Create report first, then set the paths
        report = Report("new_report")
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "new_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files and load structure
        report._rename_baseline_files()
        report._update_pbip_references()
        report._load_report_structure()
        
        assert report.name == "new_report"
        assert report.exists()
    
    @pytest.mark.unit
    def test_create_from_baseline_missing_baseline(self, temp_report_dir):
        """Test error when baseline report is missing"""
        # Create report first, then set invalid baseline path
        report = Report("test_report")
        report.baseline_path = Path("nonexistent")
        
        # Try to create from baseline - this should fail
        with pytest.raises(FileNotFoundError, match="Baseline report not found"):
            report._create_from_baseline()
    
    @pytest.mark.unit
    def test_rename_baseline_files(self, temp_report_dir, mock_baseline_report):
        """Test renaming of baseline files"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Call the rename method
        report._rename_baseline_files()
        
        # Check that files were renamed
        assert (report.report_path / "test_report.Report").exists()
        assert (report.report_path / "test_report.Dataset").exists()
        assert (report.report_path / "test_report.pbip").exists()
        
        # Check that old names don't exist
        assert not (report.report_path / "report_sample.Report").exists()
        assert not (report.report_path / "report_sample.Dataset").exists()
        assert not (report.report_path / "report_sample.pbip").exists()
    
    @pytest.mark.unit
    def test_update_pbip_references(self, temp_report_dir, mock_baseline_report):
        """Test updating pbip file references"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Update pbip references
        report._update_pbip_references()
        
        # Check that pbip file was updated
        pbip_file = report.report_path / "test_report.pbip"
        with open(pbip_file, 'r') as f:
            pbip_data = json.load(f)
        
        assert pbip_data['artifacts'][0]['report']['path'] == "test_report.Report"
    
    @pytest.mark.unit
    def test_load_report_structure(self, temp_report_dir, mock_baseline_report):
        """Test loading report structure"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        assert report._pages is not None
        assert isinstance(report._pages, Pages)
    
    @pytest.mark.unit
    def test_load_report_structure_missing_report_folder(self, temp_report_dir):
        """Test error when report folder is missing"""
        report = Report("test_report")
        report.report_path = temp_report_dir / "test_report"
        
        with pytest.raises(FileNotFoundError, match="Report folder not found"):
            report._load_report_structure()
    
    @pytest.mark.unit
    def test_pages_property(self, temp_report_dir, mock_baseline_report):
        """Test pages property"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        assert report.pages is not None
        assert isinstance(report.pages, Pages)
    
    @pytest.mark.unit
    def test_get_page(self, temp_report_dir, mock_baseline_report):
        """Test getting a specific page"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        page = report.get_page("ReportSection")
        assert page is not None
        assert page.name == "ReportSection"
    
    @pytest.mark.unit
    def test_get_page_not_found(self, temp_report_dir, mock_baseline_report):
        """Test getting a non-existent page"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        page = report.get_page("NonExistentPage")
        assert page is None
    
    @pytest.mark.unit
    def test_add_page(self, temp_report_dir, mock_baseline_report):
        """Test adding a new page"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        new_page = report.add_page("NewPage", "New Page", 1024, 768)
        assert new_page is not None
        assert new_page.name == "NewPage"
        assert new_page.display_name == "New Page"
    
    @pytest.mark.unit
    def test_remove_page(self, temp_report_dir, mock_baseline_report):
        """Test removing a page"""
        report = Report("test_report")
        
        # Mock the baseline path and report path
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "test_report"
        
        # Copy baseline to report path
        shutil.copytree(mock_baseline_report, report.report_path)
        
        # Rename files first
        report._rename_baseline_files()
        
        # Load report structure
        report._load_report_structure()
        
        # Add a page first
        report.add_page("TestPage", "Test Page")
        
        # Remove the page
        result = report.remove_page("TestPage")
        assert result is True
        
        # Verify page is gone
        assert report.get_page("TestPage") is None
    
    @pytest.mark.unit
    def test_exists(self, temp_report_dir):
        """Test exists method"""
        report = Report("test_report")
        report.report_path = temp_report_dir / "test_report"
        
        # Initially doesn't exist
        assert not report.exists()
        
        # Create directory
        report.report_path.mkdir(parents=True, exist_ok=True)
        
        # Now exists
        assert report.exists()
    
    @pytest.mark.unit
    def test_get_report_path(self, temp_report_dir):
        """Test get_report_path method"""
        report = Report("test_report")
        report.report_path = temp_report_dir / "test_report"
        
        path = report.get_report_path()
        assert path == temp_report_dir / "test_report"
    
    @pytest.mark.unit
    def test_get_report_folder(self, temp_report_dir):
        """Test get_report_folder method"""
        report = Report("test_report")
        report.report_path = temp_report_dir / "test_report"
        
        folder = report.get_report_folder()
        assert folder == temp_report_dir / "test_report" / "test_report.Report"
    
    @pytest.mark.integration
    def test_full_report_lifecycle(self, temp_report_dir, mock_baseline_report):
        """Test complete report lifecycle: create, modify, delete"""
        # Create report
        report = Report("lifecycle_test")
        
        # Mock paths
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "lifecycle_test"
        
        # Copy baseline
        shutil.copytree(mock_baseline_report, report.report_path)
        report._rename_baseline_files()
        report._update_pbip_references()
        report._load_report_structure()
        
        # Verify initial state
        assert report.exists()
        assert report.pages is not None
        assert len(report.pages.pages) == 1
        assert "ReportSection" in report.pages.pages
        
        # Add a new page
        new_page = report.add_page("NewPage", "New Page", 1024, 768)
        assert new_page is not None
        assert report.pages is not None
        assert len(report.pages.pages) == 2
        
        # Modify page properties
        new_page.display_name = "Modified Page"
        assert new_page.display_name == "Modified Page"
        
        # Remove page
        result = report.remove_page("NewPage")
        assert result is True
        assert report.pages is not None
        assert len(report.pages.pages) == 1
        
        # Verify final state
        assert report.exists()
        assert report.pages is not None
        assert "ReportSection" in report.pages.pages
        assert "NewPage" not in report.pages.pages
