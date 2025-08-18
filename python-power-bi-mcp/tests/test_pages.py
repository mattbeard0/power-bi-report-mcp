"""
Tests for the Pages class
"""
import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from models.pages.pages import Pages, PagesData
from models.page.page import Page, PageData


class TestPages:
    """Test cases for the Pages class"""
    
    @pytest.mark.unit
    def test_pages_initialization(self, temp_report_dir, mock_baseline_report):
        """Test Pages initialization"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        assert pages.file_path == pages_file
        assert isinstance(pages.data, PagesData)
        assert pages.data.pageOrder == ["ReportSection"]
        assert pages.data.activePageName == "ReportSection"
        assert len(pages.pages) == 1
        assert "ReportSection" in pages.pages
    
    @pytest.mark.unit
    def test_pages_initialization_missing_file(self, temp_report_dir):
        """Test Pages initialization with missing file"""
        missing_file = temp_report_dir / "missing_pages.json"
        
        with pytest.raises(FileNotFoundError):
            Pages(missing_file)
    
    @pytest.mark.unit
    def test_load_pages(self, temp_report_dir, mock_baseline_report):
        """Test loading pages from directory"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        assert len(pages.pages) == 1
        assert "ReportSection" in pages.pages
        assert isinstance(pages.pages["ReportSection"], Page)
    
    @pytest.mark.unit
    def test_load_pages_empty_directory(self, temp_report_dir):
        """Test loading pages from empty directory"""
        # Create empty pages structure
        empty_pages_dir = temp_report_dir / "empty_pages"
        empty_pages_dir.mkdir(parents=True, exist_ok=True)
        
        pages_json = {
            "pageOrder": [],
            "activePageName": "",
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"
        }
        
        pages_file = empty_pages_dir / "pages.json"
        with open(pages_file, 'w') as f:
            json.dump(pages_json, f, indent=2)
        
        pages = Pages(pages_file)
        
        assert len(pages.pages) == 0
    
    @pytest.mark.unit
    def test_write_back(self, temp_report_dir, mock_baseline_report):
        """Test writing pages data back to file"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        # Modify data
        pages.data.activePageName = "ModifiedPage"
        
        # Write back
        result = pages.write_back()
        assert result is True
        
        # Verify file was updated
        with open(pages_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["activePageName"] == "ModifiedPage"
    
    @pytest.mark.unit
    def test_write_back_no_file_path(self, temp_report_dir):
        """Test write_back with no file path"""
        # Create a mock pages object without proper initialization
        with patch('models.pages.pages.Pages.__init__', return_value=None):
            pages = Pages.__new__(Pages)
            # Use monkey patching to set file_path to None for testing
            object.__setattr__(pages, 'file_path', None)
            
            with pytest.raises(ValueError, match="File path not set"):
                pages.write_back()
    
    @pytest.mark.unit
    def test_page_order_property(self, temp_report_dir, mock_baseline_report):
        """Test page_order property"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        assert pages.page_order == ["ReportSection"]
    
    @pytest.mark.unit
    def test_active_page_name_property(self, temp_report_dir, mock_baseline_report):
        """Test active_page_name property"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        assert pages.active_page_name == "ReportSection"
    
    @pytest.mark.unit
    def test_active_page_name_setter(self, temp_report_dir, mock_baseline_report):
        """Test active_page_name setter"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        # Change active page
        pages.active_page_name = "NewActivePage"
        
        assert pages.active_page_name == "NewActivePage"
        
        # Verify file was updated
        with open(pages_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["activePageName"] == "NewActivePage"
    
    @pytest.mark.unit
    def test_pages_property(self, temp_report_dir, mock_baseline_report):
        """Test pages property"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        assert isinstance(pages.pages, dict)
        assert len(pages.pages) == 1
        assert "ReportSection" in pages.pages
    
    @pytest.mark.unit
    def test_get_page(self, temp_report_dir, mock_baseline_report):
        """Test getting a page by name"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        page = pages.get_page("ReportSection")
        assert page is not None
        assert page.name == "ReportSection"
    
    @pytest.mark.unit
    def test_get_page_not_found(self, temp_report_dir, mock_baseline_report):
        """Test getting a non-existent page"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"

        pages = Pages(pages_file)

        # Should return None for non-existent pages
        result = pages.get_page("NonExistentPage")
        assert result is None
    
    @pytest.mark.unit
    def test_add_page(self, temp_report_dir, mock_baseline_report):
        """Test adding a new page"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        # Create page directory
        page_dir = pages_file.parent / "NewPage"
        page_dir.mkdir(exist_ok=True)
        
        # Create page.json file
        page_data = {
            "name": "NewPage",
            "displayName": "New Page",
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
        }
        
        page_file = page_dir / "page.json"
        with open(page_file, 'w') as f:
            json.dump(page_data, f, indent=2)
        
        # Add page
        new_page = pages.add_page("NewPage", "New Page", 1024, 768)
        
        assert new_page is not None
        assert new_page.name == "NewPage"
        assert new_page.display_name == "New Page"
        assert "NewPage" in pages.pages
        assert "NewPage" in pages.page_order
    
    @pytest.mark.unit
    def test_add_page_already_exists(self, temp_report_dir, mock_baseline_report):
        """Test adding a page that already exists"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        with pytest.raises(ValueError, match="Page ReportSection already exists"):
            pages.add_page("ReportSection", "Duplicate Page")
    
    @pytest.mark.unit
    def test_remove_page(self, temp_report_dir, mock_baseline_report):
        """Test removing a page"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        # Add a page first
        page_dir = pages_file.parent / "TestPage"
        page_dir.mkdir(exist_ok=True)
        
        page_data = {
            "name": "TestPage",
            "displayName": "Test Page",
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280,
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
        }
        
        page_file = page_dir / "page.json"
        with open(page_file, 'w') as f:
            json.dump(page_data, f, indent=2)
        
        pages.add_page("TestPage", "Test Page")
        
        # Remove the page
        result = pages.remove_page("TestPage")
        
        assert result is True
        assert "TestPage" not in pages.pages
        assert "TestPage" not in pages.page_order
    
    @pytest.mark.unit
    def test_remove_page_not_found(self, temp_report_dir, mock_baseline_report):
        """Test removing a non-existent page"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        result = pages.remove_page("NonExistentPage")
        assert result is False
    
    @pytest.mark.integration
    def test_pages_lifecycle(self, temp_report_dir, mock_baseline_report):
        """Test complete pages lifecycle: create, modify, delete"""
        pages_file = mock_baseline_report / "report_sample.Report" / "definition" / "pages" / "pages.json"
        
        pages = Pages(pages_file)
        
        # Verify initial state
        assert len(pages.pages) == 1
        assert "ReportSection" in pages.pages
        assert pages.active_page_name == "ReportSection"
        
        # Add multiple pages
        for i in range(3):
            page_name = f"Page{i}"
            page_dir = pages_file.parent / page_name
            page_dir.mkdir(exist_ok=True)
            
            page_data = {
                "name": page_name,
                "displayName": f"Page {i}",
                "displayOption": "FitToPage",
                "height": 720,
                "width": 1280,
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
            }
            
            page_file = page_dir / "page.json"
            with open(page_file, 'w') as f:
                json.dump(page_data, f, indent=2)
            
            pages.add_page(page_name, f"Page {i}")
        
        # Verify pages were added
        assert len(pages.pages) == 4
        assert "Page0" in pages.pages
        assert "Page1" in pages.pages
        assert "Page2" in pages.pages
        
        # Change active page
        pages.active_page_name = "Page1"
        assert pages.active_page_name == "Page1"
        
        # Remove pages
        for i in range(3):
            page_name = f"Page{i}"
            result = pages.remove_page(page_name)
            assert result is True
        
        # Verify final state
        assert len(pages.pages) == 1
        assert "ReportSection" in pages.pages
        assert "Page0" not in pages.pages
        assert "Page1" not in pages.pages
        assert "Page2" not in pages.pages


class TestPagesData:
    """Test cases for the PagesData model"""
    
    @pytest.mark.unit
    def test_pages_data_creation(self):
        """Test PagesData model creation"""
        data = PagesData(
            pageOrder=["Page1", "Page2"],
            activePageName="Page1"
        )
        
        assert data.pageOrder == ["Page1", "Page2"]
        assert data.activePageName == "Page1"
        assert data.api_schema == "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"
    
    @pytest.mark.unit
    def test_pages_data_defaults(self):
        """Test PagesData model with defaults"""
        data = PagesData(
            pageOrder=[],
            activePageName=""
        )
        
        assert data.pageOrder == []
        assert data.activePageName == ""
        assert data.api_schema == "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json"
