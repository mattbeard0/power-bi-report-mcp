"""
Tests for the Visual class
"""
import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from models.visual.visual import Visual, VisualData, VisualPosition, VisualVisual, VisualType


class TestVisual:
    """Test cases for the Visual class"""
    
    @pytest.mark.unit
    def test_visual_initialization_with_data(self, temp_report_dir, sample_visual_data):
        """Test Visual initialization with provided data"""
        visual_file = temp_report_dir / "test_visual.json"
        
        # Create visual data
        visual_data = VisualData(**sample_visual_data)
        
        visual = Visual(visual_file, visual_data)
        
        assert visual.file_path == visual_file
        assert visual.data == visual_data
        assert visual.name == "test_visual"
        assert visual.position.x == 100.0
        assert visual.position.y == 200.0
        assert visual.position.height == 300.0
        assert visual.position.width == 400.0
        assert visual.visual_type == "card"
    
    @pytest.mark.unit
    def test_visual_initialization_from_file(self, temp_report_dir, sample_visual_data):
        """Test Visual initialization from file"""
        visual_file = temp_report_dir / "test_visual.json"
        
        # Write visual data to file
        with open(visual_file, 'w') as f:
            json.dump(sample_visual_data, f, indent=2)
        
        visual = Visual(visual_file)
        
        assert visual.file_path == visual_file
        assert visual.name == "test_visual"
        assert visual.position.x == 100.0
        assert visual.position.y == 200.0
        assert visual.position.height == 300.0
        assert visual.position.width == 400.0
        assert visual.visual_type == "card"
    
    @pytest.mark.unit
    def test_visual_initialization_missing_file(self, temp_report_dir):
        """Test Visual initialization with missing file"""
        missing_file = temp_report_dir / "missing_visual.json"
        
        with pytest.raises(FileNotFoundError):
            Visual(missing_file)
    
    @pytest.mark.unit
    def test_write_back(self, temp_report_dir, sample_visual_data):
        """Test writing visual data back to file"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Modify data
        visual.data.position.x = 150.0
        
        # Write back
        result = visual.write_back()
        assert result is True
        
        # Verify file was updated
        with open(visual_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["position"]["x"] == 150.0
    
    @pytest.mark.unit
    def test_write_back_no_file_path(self, temp_report_dir, sample_visual_data):
        """Test write_back with no file path"""
        visual_data = VisualData(**sample_visual_data)
        visual = Visual.__new__(Visual)
        visual.data = visual_data
        # Use monkey patching to set file_path to None for testing
        object.__setattr__(visual, 'file_path', None)
        
        with pytest.raises(ValueError, match="File path not set"):
            visual.write_back()
    
    @pytest.mark.unit
    def test_write_back_error(self, temp_report_dir, sample_visual_data):
        """Test write_back with write error"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Mock file write to raise an error
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = visual.write_back()
            assert result is False
    
    @pytest.mark.unit
    def test_remove(self, temp_report_dir, sample_visual_data):
        """Test removing a visual"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Verify file exists
        assert visual_file.exists()
        
        # Remove visual
        result = visual.remove()
        assert result is True
        
        # Verify file was removed
        assert not visual_file.exists()
    
    @pytest.mark.unit
    def test_remove_missing_file(self, temp_report_dir, sample_visual_data):
        """Test removing a visual that doesn't exist"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Remove file first
        if visual_file.exists():
            visual_file.unlink()
        
        with pytest.raises(FileNotFoundError, match="Visual file not found"):
            visual.remove()
    
    @pytest.mark.unit
    def test_remove_error(self, temp_report_dir, sample_visual_data):
        """Test removing a visual with error"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Mock file removal to raise an error
        with patch('pathlib.Path.unlink', side_effect=PermissionError("Permission denied")):
            result = visual.remove()
            assert result is False
    
    @pytest.mark.unit
    def test_remove_cleanup_empty_directory(self, temp_report_dir, sample_visual_data):
        """Test removing a visual and cleaning up empty directory"""
        visual_file = temp_report_dir / "test_visual.json"
        visual_dir = visual_file.parent
        
        # Create visual directory
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Verify directory exists
        assert visual_dir.exists()
        
        # Remove visual
        result = visual.remove()
        assert result is True
        
        # Verify file was removed
        assert not visual_file.exists()
        # Verify directory was cleaned up (since it's empty)
        assert not visual_dir.exists()
    
    @pytest.mark.unit
    def test_position_property(self, temp_report_dir, sample_visual_data):
        """Test position property"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        assert isinstance(visual.position, VisualPosition)
        assert visual.position.x == 100.0
        assert visual.position.y == 200.0
        assert visual.position.z == 0.0
        assert visual.position.height == 300.0
        assert visual.position.width == 400.0
    
    @pytest.mark.unit
    def test_position_setter(self, temp_report_dir, sample_visual_data):
        """Test position setter"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Create new position
        new_position = VisualPosition(x=200.0, y=300.0, z=1.0, height=400.0, width=500.0)
        
        # Change position
        visual.position = new_position
        
        assert visual.position == new_position
        assert visual.data.position == new_position
        
        # Verify file was updated
        with open(visual_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["position"]["x"] == 200.0
        assert updated_data["position"]["y"] == 300.0
        assert updated_data["position"]["z"] == 1.0
        assert updated_data["position"]["height"] == 400.0
        assert updated_data["position"]["width"] == 500.0
    
    @pytest.mark.unit
    def test_visual_type_property(self, temp_report_dir, sample_visual_data):
        """Test visual_type property"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        assert visual.visual_type == "card"
    
    @pytest.mark.unit
    def test_visual_type_setter(self, temp_report_dir, sample_visual_data):
        """Test visual_type setter"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Change visual type
        visual.visual_type = VisualType.barChart
        
        assert visual.visual_type == VisualType.barChart
        assert visual.data.visual.visualType == VisualType.barChart
        
        # Verify file was updated
        with open(visual_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["visual"]["visualType"] == "barChart"
    
    @pytest.mark.unit
    def test_name_property(self, temp_report_dir, sample_visual_data):
        """Test name property"""
        visual_file = temp_report_dir / "test_visual.json"
        
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        assert visual.name == "test_visual"
    
    @pytest.mark.integration
    def test_visual_lifecycle(self, temp_report_dir, sample_visual_data):
        """Test complete visual lifecycle: create, modify, delete"""
        visual_file = temp_report_dir / "test_visual.json"
        
        # Create visual
        visual_data = VisualData(**sample_visual_data)
        visual = Visual(visual_file, visual_data)
        
        # Verify initial state
        assert visual.name == "test_visual"
        assert visual.position.x == 100.0
        assert visual.position.y == 200.0
        assert visual.visual_type == "card"
        
        # Modify properties
        new_position = VisualPosition(x=150.0, y=250.0, z=0.0, height=350.0, width=450.0)
        visual.position = new_position
        visual.visual_type = VisualType.lineChart
        
        assert visual.position == new_position
        assert visual.visual_type == VisualType.lineChart
        
        # Verify file was updated
        with open(visual_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["position"]["x"] == 150.0
        assert updated_data["position"]["y"] == 250.0
        assert updated_data["visual"]["visualType"] == "lineChart"
        
        # Remove visual
        result = visual.remove()
        assert result is True
        assert not visual_file.exists()


class TestVisualData:
    """Test cases for the VisualData model"""
    
    @pytest.mark.unit
    def test_visual_data_creation(self):
        """Test VisualData model creation"""
        data = VisualData(
            name="test_visual",
            position=VisualPosition(x=100.0, y=200.0, z=0.0, height=300.0, width=400.0),
            visual=VisualVisual(visualType=VisualType.card, drillFilterOtherVisuals=True)
        )
        
        assert data.name == "test_visual"
        assert data.position.x == 100.0
        assert data.position.y == 200.0
        assert data.visual.visualType == VisualType.card
        assert data.visual.drillFilterOtherVisuals is True
        assert data.schema == "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.1.0/schema.json"
    
    @pytest.mark.unit
    def test_visual_data_defaults(self):
        """Test VisualData model with defaults"""
        data = VisualData(
            name="test_visual",
            position=VisualPosition(height=300.0, width=400.0),
            visual=VisualVisual(visualType=VisualType.card)
        )
        
        assert data.name == "test_visual"
        assert data.position.x == 0.0
        assert data.position.y == 0.0
        assert data.position.z == 0.0
        assert data.position.height == 300.0
        assert data.position.width == 400.0
        assert data.visual.visualType == VisualType.card
        assert data.visual.drillFilterOtherVisuals is True


class TestVisualPosition:
    """Test cases for the VisualPosition model"""
    
    @pytest.mark.unit
    def test_visual_position_creation(self):
        """Test VisualPosition model creation"""
        position = VisualPosition(
            x=100.0,
            y=200.0,
            z=1.0,
            height=300.0,
            width=400.0
        )
        
        assert position.x == 100.0
        assert position.y == 200.0
        assert position.z == 1.0
        assert position.height == 300.0
        assert position.width == 400.0
    
    @pytest.mark.unit
    def test_visual_position_defaults(self):
        """Test VisualPosition model with defaults"""
        position = VisualPosition(
            height=300.0,
            width=400.0
        )
        
        assert position.x == 0.0
        assert position.y == 0.0
        assert position.z == 0.0
        assert position.height == 300.0
        assert position.width == 400.0
    
    @pytest.mark.unit
    def test_visual_position_validation(self):
        """Test VisualPosition model validation"""
        # Test with invalid x (negative)
        with pytest.raises(ValueError):
            VisualPosition(x=-100.0, height=300.0, width=400.0)
        
        # Test with invalid y (negative)
        with pytest.raises(ValueError):
            VisualPosition(y=-100.0, height=300.0, width=400.0)
        
        # Test with invalid height (negative)
        with pytest.raises(ValueError):
            VisualPosition(height=-100.0, width=400.0)
        
        # Test with invalid width (negative)
        with pytest.raises(ValueError):
            VisualPosition(height=300.0, width=-100.0)


class TestVisualVisual:
    """Test cases for the VisualVisual model"""
    
    @pytest.mark.unit
    def test_visual_visual_creation(self):
        """Test VisualVisual model creation"""
        visual = VisualVisual(
            visualType=VisualType.barChart,
            drillFilterOtherVisuals=False
        )
        
        assert visual.visualType == VisualType.barChart
        assert visual.drillFilterOtherVisuals is False
    
    @pytest.mark.unit
    def test_visual_visual_defaults(self):
        """Test VisualVisual model with defaults"""
        visual = VisualVisual(
            visualType=VisualType.card
        )
        
        assert visual.visualType == VisualType.card
        assert visual.drillFilterOtherVisuals is True


class TestVisualType:
    """Test cases for the VisualType enum"""
    
    @pytest.mark.unit
    def test_visual_type_values(self):
        """Test VisualType enum values"""
        assert VisualType.card == "card"
        assert VisualType.barChart == "barChart"
        assert VisualType.lineChart == "lineChart"
        assert VisualType.pieChart == "pieChart"
        assert VisualType.table == "table"
        assert VisualType.slicer == "slicer"
        assert VisualType.matrix == "matrix"
        assert VisualType.scatterChart == "scatterChart"
        assert VisualType.areaChart == "areaChart"
        assert VisualType.columnChart == "columnChart"
        assert VisualType.funnelChart == "waterfall"
        assert VisualType.gauge == "gauge"
        assert VisualType.map == "map"
        assert VisualType.waterfall == "waterfall"
    
    @pytest.mark.unit
    def test_visual_type_inheritance(self):
        """Test VisualType enum inheritance"""
        assert issubclass(VisualType, str)
        assert isinstance(VisualType.card, str)
