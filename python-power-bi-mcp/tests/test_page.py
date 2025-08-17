"""
Tests for the Page class
"""
import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from models.page.page import Page, PageData, Pages


class TestPage:
    """Test cases for the Page class"""
    
    @pytest.mark.unit
    def test_page_initialization_with_data(self, temp_report_dir, sample_page_data):
        """Test Page initialization with provided data"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create page data
        page_data = PageData(**sample_page_data)
        
        page = Page(page_file, page_data)
        
        assert page.file_path == page_file
        assert page.data == page_data
        assert page.name == "test_page"
        assert page.display_name == "Test Page"
        assert page.display_option == "FitToPage"
        assert page.height == 720
        assert page.width == 1280
    
    @pytest.mark.unit
    def test_page_initialization_from_file(self, temp_report_dir, sample_page_data):
        """Test Page initialization from file"""
        page_file = temp_report_dir / "test_page.json"
        
        # Write page data to file
        with open(page_file, 'w') as f:
            json.dump(sample_page_data, f, indent=2)
        
        page = Page(page_file)
        
        assert page.file_path == page_file
        assert page.name == "test_page"
        assert page.display_name == "Test Page"
        assert page.display_option == "FitToPage"
        assert page.height == 720
        assert page.width == 1280
    
    @pytest.mark.unit
    def test_page_initialization_missing_file(self, temp_report_dir):
        """Test Page initialization with missing file"""
        missing_file = temp_report_dir / "missing_page.json"
        
        with pytest.raises(FileNotFoundError):
            Page(missing_file)
    
    @pytest.mark.unit
    def test_load_visuals(self, temp_report_dir, sample_page_data, sample_visual_data):
        """Test loading visuals for a page"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create page directory structure
        visuals_dir = temp_report_dir / "visuals"
        visual_dir = visuals_dir / "test_visual"
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visual.json file
        visual_file = visual_dir / "visual.json"
        with open(visual_file, 'w') as f:
            json.dump(sample_visual_data, f, indent=2)
        
        # Create page with visuals directory
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock the visuals directory path
        page._visuals = page._load_visuals(visuals_dir)
        
        assert len(page._visuals) == 1
        assert "test_visual" in page._visuals
    
    @pytest.mark.unit
    def test_load_visuals_empty_directory(self, temp_report_dir, sample_page_data):
        """Test loading visuals from empty directory"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create empty visuals directory
        visuals_dir = temp_report_dir / "visuals"
        visuals_dir.mkdir(exist_ok=True)
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock the visuals directory path
        page._visuals = page._load_visuals(visuals_dir)
        
        assert len(page._visuals) == 0
    
    @pytest.mark.unit
    def test_load_visuals_missing_directory(self, temp_report_dir, sample_page_data):
        """Test loading visuals from missing directory"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock the visuals directory path
        missing_visuals_dir = temp_report_dir / "missing_visuals"
        page._visuals = page._load_visuals(missing_visuals_dir)
        
        assert len(page._visuals) == 0
    
    @pytest.mark.unit
    def test_write_back(self, temp_report_dir, sample_page_data):
        """Test writing page data back to file"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Modify data
        page.data.displayName = "Modified Page"
        
        # Write back
        result = page.write_back()
        assert result is True
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["displayName"] == "Modified Page"
    
    @pytest.mark.unit
    def test_write_back_no_file_path(self, temp_report_dir, sample_page_data):
        """Test write_back with no file path"""
        page_data = PageData(**sample_page_data)
        page = Page.__new__(Page)
        page.data = page_data
        # Use monkey patching to set file_path to None for testing
        object.__setattr__(page, 'file_path', None)
        
        with pytest.raises(ValueError, match="File path not set"):
            page.write_back()
    
    @pytest.mark.unit
    def test_write_back_error(self, temp_report_dir, sample_page_data):
        """Test write_back with write error"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock file write to raise an error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = page.write_back()
            assert result is False
    
    @pytest.mark.unit
    def test_remove(self, temp_report_dir, sample_page_data):
        """Test removing a page"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Verify file exists
        assert page_file.exists()
        
        # Remove page
        result = page.remove()
        assert result is True
        
        # Verify file was removed
        assert not page_file.exists()
    
    @pytest.mark.unit
    def test_remove_missing_file(self, temp_report_dir, sample_page_data):
        """Test removing a page that doesn't exist"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Remove file first
        if page_file.exists():
            page_file.unlink()
        
        with pytest.raises(FileNotFoundError, match="Page file not found"):
            page.remove()
    
    @pytest.mark.unit
    def test_remove_error(self, temp_report_dir, sample_page_data):
        """Test removing a page with error"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock file removal to raise an error
        with patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied")):
            result = page.remove()
            assert result is False
    
    @pytest.mark.unit
    def test_name_property(self, temp_report_dir, sample_page_data):
        """Test name property"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        assert page.name == "test_page"
    
    @pytest.mark.unit
    def test_display_name_property(self, temp_report_dir, sample_page_data):
        """Test display_name property"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        assert page.display_name == "Test Page"
    
    @pytest.mark.unit
    def test_display_name_setter(self, temp_report_dir, sample_page_data):
        """Test display_name setter"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Change display name
        page.display_name = "New Display Name"
        
        assert page.display_name == "New Display Name"
        assert page.data.displayName == "New Display Name"
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["displayName"] == "New Display Name"
    
    @pytest.mark.unit
    def test_display_option_property(self, temp_report_dir, sample_page_data):
        """Test display_option property"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        assert page.display_option == "FitToPage"
    
    @pytest.mark.unit
    def test_display_option_setter(self, temp_report_dir, sample_page_data):
        """Test display_option setter"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Change display option
        page.display_option = "ActualSize"
        
        assert page.display_option == "ActualSize"
        assert page.data.displayOption == "ActualSize"
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["displayOption"] == "ActualSize"
    
    @pytest.mark.unit
    def test_height_property(self, temp_report_dir, sample_page_data):
        """Test height property"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        assert page.height == 720
        assert page.data.height == 720
    
    @pytest.mark.unit
    def test_height_setter(self, temp_report_dir, sample_page_data):
        """Test height setter"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Change height
        page.height = 1024
        
        assert page.height == 1024
        assert page.data.height == 1024
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["height"] == 1024
    
    @pytest.mark.unit
    def test_width_property(self, temp_report_dir, sample_page_data):
        """Test width property"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        assert page.width == 1280
        assert page.data.width == 1280
    
    @pytest.mark.unit
    def test_width_setter(self, temp_report_dir, sample_page_data):
        """Test width setter"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Change width
        page.width = 1920
        
        assert page.width == 1920
        assert page.data.width == 1920
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["width"] == 1920
    
    @pytest.mark.unit
    def test_visuals_property(self, temp_report_dir, sample_page_data, sample_visual_data):
        """Test visuals property"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create page directory structure
        visuals_dir = temp_report_dir / "visuals"
        visual_dir = visuals_dir / "test_visual"
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visual.json file
        visual_file = visual_dir / "visual.json"
        with open(visual_file, 'w') as f:
            json.dump(sample_visual_data, f, indent=2)
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock the visuals directory path
        page._visuals = page._load_visuals(visuals_dir)
        
        assert isinstance(page.visuals, dict)
        assert len(page.visuals) == 1
        assert "test_visual" in page.visuals
    
    @pytest.mark.unit
    def test_get_visual(self, temp_report_dir, sample_page_data, sample_visual_data):
        """Test getting a visual by name"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create page directory structure
        visuals_dir = temp_report_dir / "visuals"
        visual_dir = visuals_dir / "test_visual"
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visual.json file
        visual_file = visual_dir / "visual.json"
        with open(visual_file, 'w') as f:
            json.dump(sample_visual_data, f, indent=2)
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Mock the visuals directory path
        page._visuals = page._load_visuals(visuals_dir)
        
        visual = page.get_visual("test_visual")
        assert visual is not None
        assert visual.name == "test_visual"
    
    @pytest.mark.unit
    def test_get_visual_not_found(self, temp_report_dir, sample_page_data):
        """Test getting a non-existent visual"""
        page_file = temp_report_dir / "test_page.json"
        
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        visual = page.get_visual("NonExistentVisual")
        assert visual is None
    
    @pytest.mark.integration
    def test_page_lifecycle(self, temp_report_dir, sample_page_data):
        """Test complete page lifecycle: create, modify, delete"""
        page_file = temp_report_dir / "test_page.json"
        
        # Create page
        page_data = PageData(**sample_page_data)
        page = Page(page_file, page_data)
        
        # Verify initial state
        assert page.name == "test_page"
        assert page.display_name == "Test Page"
        assert page.height == 720
        assert page.width == 1280
        
        # Modify properties
        page.display_name = "Modified Page"
        page.height = 1024
        page.width = 1920
        
        assert page.display_name == "Modified Page"
        assert page.height == 1024
        assert page.width == 1920
        
        # Verify file was updated
        with open(page_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["displayName"] == "Modified Page"
        assert updated_data["height"] == 1024
        assert updated_data["width"] == 1920
        
        # Remove page
        result = page.remove()
        assert result is True
        assert not page_file.exists()


class TestPageData:
    """Test cases for the PageData model"""
    
    @pytest.mark.unit
    def test_page_data_creation(self):
        """Test PageData model creation"""
        data = PageData(
            name="test_page",
            displayName="Test Page",
            displayOption="FitToPage",
            height=720,
            width=1280
        )
        
        assert data.name == "test_page"
        assert data.displayName == "Test Page"
        assert data.displayOption == "FitToPage"
        assert data.height == 720
        assert data.width == 1280
        assert data.schema == "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
    
    @pytest.mark.unit
    def test_page_data_defaults(self):
        """Test PageData model with defaults"""
        data = PageData(
            name="test_page",
            displayName="Test Page"
        )
        
        assert data.name == "test_page"
        assert data.displayName == "Test Page"
        assert data.displayOption == "FitToPage"
        assert data.height == 720
        assert data.width == 1280
        assert data.schema == "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json"
    
    @pytest.mark.unit
    def test_page_data_validation(self):
        """Test PageData model validation"""
        # Test with invalid height (negative)
        with pytest.raises(ValueError):
            PageData(
                name="test_page",
                displayName="Test Page",
                height=-100
            )
        
        # Test with invalid width (negative)
        with pytest.raises(ValueError):
            PageData(
                name="test_page",
                displayName="Test Page",
                width=-100
            )
