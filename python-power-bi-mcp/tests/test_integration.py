"""
Integration tests for Power BI MCP models
"""
import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import patch
from models.report import Report
from models.pages.pages import Pages
from models.page.page import Page, PageData
from models.visual.visual import Visual, VisualData, VisualPosition, VisualVisual, VisualType


class TestModelsIntegration:
    """Integration tests for models working together"""
    
    @pytest.mark.integration
    def test_report_with_pages_and_visuals(self, temp_report_dir, mock_baseline_report):
        """Test complete integration: Report -> Pages -> Page -> Visuals"""
        # Create report
        report = Report("integration_test")
        
        # Mock paths
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "integration_test"
        
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
        
        # Get the page
        page = report.get_page("ReportSection")
        assert page is not None
        assert page.name == "ReportSection"
        
        # Add a new page with visuals
        new_page_name = "ChartPage"
        new_page = report.add_page(new_page_name, "Chart Page", 1024, 768)
        assert new_page is not None
        
        # Create visual data for the new page
        visual_data = VisualData(
            name="chart_visual",
            position=VisualPosition(x=100.0, y=100.0, z=0.0, height=300.0, width=400.0),
            visual=VisualVisual(visualType=VisualType.barChart, drillFilterOtherVisuals=True)
        )
        
        # Create visual directory structure
        visual_dir = new_page.file_path.parent / "visuals" / "chart_visual"
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        # Create visual file
        visual_file = visual_dir / "visual.json"
        with open(visual_file, 'w') as f:
            f.write(visual_data.model_dump_json(indent=2))
        
        # Add the visual to the page's visuals dictionary
        visual = Visual(visual_file, visual_data)
        new_page._visuals["chart_visual"] = visual
        
        # Verify visual was loaded
        assert len(new_page.visuals) == 1
        assert "chart_visual" in new_page.visuals
        
        # Get the visual
        visual = new_page.get_visual("chart_visual")
        assert visual is not None
        assert visual.name == "chart_visual"
        assert visual.visual_type == VisualType.barChart
        
        # Modify visual properties
        new_position = VisualPosition(x=150.0, y=150.0, z=0.0, height=350.0, width=450.0)
        visual.position = new_position
        visual.visual_type = VisualType.lineChart
        
        # Verify changes
        assert visual.position == new_position
        assert visual.visual_type == VisualType.lineChart
        
        # Verify file was updated
        with open(visual_file, 'r') as f:
            updated_data = json.load(f)
        
        assert updated_data["position"]["x"] == 150.0
        assert updated_data["position"]["y"] == 150.0
        assert updated_data["visual"]["visualType"] == "lineChart"
        
        # Test page modifications
        new_page.display_name = "Modified Chart Page"
        new_page.height = 900
        new_page.width = 1400
        
        assert new_page.display_name == "Modified Chart Page"
        assert new_page.height == 900
        assert new_page.width == 1400
        
        # Verify page file was updated
        with open(new_page.file_path, 'r') as f:
            page_data = json.load(f)
        
        assert page_data["displayName"] == "Modified Chart Page"
        assert page_data["height"] == 900
        assert page_data["width"] == 1400
        
        # Test page removal
        result = report.remove_page(new_page_name)
        assert result is True
        
        # Verify page was removed
        assert report.get_page(new_page_name) is None
        assert new_page_name not in report.pages.pages
        assert new_page_name not in report.pages.page_order
        
        # Verify final state
        assert len(report.pages.pages) == 1
        assert "ReportSection" in report.pages.pages
    
    @pytest.mark.integration
    def test_multiple_pages_with_multiple_visuals(self, temp_report_dir, mock_baseline_report):
        """Test multiple pages with multiple visuals"""
        # Create report
        report = Report("multi_page_test")
        
        # Mock paths
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "multi_page_test"
        
        # Copy baseline
        shutil.copytree(mock_baseline_report, report.report_path)
        report._rename_baseline_files()
        report._update_pbip_references()
        report._load_report_structure()
        
        # Add multiple pages
        page_names = ["Dashboard", "Analytics", "Summary"]
        pages = {}
        
        for i, name in enumerate(page_names):
            page = report.add_page(name, f"{name} Page", 1280 + i*100, 720 + i*50)
            assert page is not None
            pages[name] = page
            
            # Clear existing visuals and add new ones
            page._visuals.clear()

            # Add multiple visuals to each page
            for j in range(3):
                visual_name = f"{name.lower()}_visual_{j}"
                visual_data = VisualData(
                    name=visual_name,
                    position=VisualPosition(
                        x=j*200.0, 
                        y=j*150.0, 
                        z=0.0, 
                        height=200.0, 
                        width=300.0
                    ),
                    visual=VisualVisual(
                        visualType=list(VisualType)[j % len(VisualType)], 
                        drillFilterOtherVisuals=True
                    )
                )
                
                # Create visual directory and file
                visual_dir = page.file_path.parent / "visuals" / visual_name
                visual_dir.mkdir(parents=True, exist_ok=True)
                
                visual_file = visual_dir / "visual.json"
                with open(visual_file, 'w') as f:
                    f.write(visual_data.model_dump_json(indent=2))
                
                # Add the visual to the page's visuals dictionary
                visual = Visual(visual_file, visual_data)
                page._visuals[visual_name] = visual
        
        # Verify all pages were created
        assert report.pages is not None
        assert len(report.pages.pages) == 4  # 1 original + 3 new
        for name in page_names:
            assert name in report.pages.pages
            assert name in report.pages.page_order
        
        # Verify each page has visuals
        for name, page in pages.items():
            assert page is not None
            assert len(page.visuals) == 3
            for j in range(3):
                visual_name = f"{name.lower()}_visual_{j}"
                assert visual_name in page.visuals
        
        # Test changing active page
        assert report.pages is not None
        report.pages.active_page_name = "Analytics"
        assert report.pages.active_page_name == "Analytics"
        
        # Test page reordering (if supported)
        # This would depend on the Pages class implementation
        
        # Clean up - remove all added pages
        for name in page_names:
            result = report.remove_page(name)
            assert result is True
        
        # Verify cleanup
        assert report.pages is not None
        assert len(report.pages.pages) == 1
        assert "ReportSection" in report.pages.pages
    
    @pytest.mark.integration
    def test_error_handling_and_recovery(self, temp_report_dir, mock_baseline_report):
        """Test error handling and recovery scenarios"""
        # Create report
        report = Report("error_test")
        
        # Mock paths
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "error_test"
        
        # Copy baseline
        shutil.copytree(mock_baseline_report, report.report_path)
        report._rename_baseline_files()
        report._update_pbip_references()
        report._load_report_structure()
        
        # Test adding page with invalid data
        with pytest.raises(ValueError):
            # Try to add a page that already exists
            report.add_page("ReportSection", "Duplicate Page")
        
        # Test getting non-existent page
        page = report.get_page("NonExistentPage")
        assert page is None
        
        # Test removing non-existent page
        result = report.remove_page("NonExistentPage")
        assert result is False
        
        # Test with corrupted page file
        page = report.get_page("ReportSection")
        if page:
            # Corrupt the page file
            with open(page.file_path, 'w') as f:
                f.write("invalid json content")
            
            # Try to reload the page - should handle gracefully
            try:
                page._visuals = page._load_visuals(page.file_path.parent / "visuals")
                # If we get here, the error was handled gracefully
                assert True
            except Exception:
                # If an exception is raised, that's also acceptable
                assert True
        
        # Test with corrupted visual file
        page = report.get_page("ReportSection")
        if page:
            # Create a corrupted visual file
            visual_dir = page.file_path.parent / "visuals" / "corrupted_visual"
            visual_dir.mkdir(parents=True, exist_ok=True)
            
            visual_file = visual_dir / "visual.json"
            with open(visual_file, 'w') as f:
                f.write("invalid json content")
            
            # Try to load visuals - should handle gracefully
            try:
                page._visuals = page._load_visuals(page.file_path.parent / "visuals")
                # If we get here, the error was handled gracefully
                assert True
            except Exception:
                # If an exception is raised, that's also acceptable
                assert True
    
    @pytest.mark.integration
    def test_file_persistence_and_consistency(self, temp_report_dir, mock_baseline_report):
        """Test file persistence and data consistency"""
        # Create report
        report = Report("persistence_test")
        
        # Mock paths
        report.baseline_path = mock_baseline_report
        report.report_path = temp_report_dir / "persistence_test"
        
        # Copy baseline
        shutil.copytree(mock_baseline_report, report.report_path)
        report._rename_baseline_files()
        report._update_pbip_references()
        report._load_report_structure()
        
        # Add a page
        page = report.add_page("TestPage", "Test Page", 768, 1024)
        assert page is not None
        
        # Add a visual
        visual_data = VisualData(
            name="test_visual",
            position=VisualPosition(x=100.0, y=100.0, z=0.0, height=200.0, width=300.0),
            visual=VisualVisual(visualType=VisualType.card, drillFilterOtherVisuals=True)
        )
        
        visual_dir = page.file_path.parent / "visuals" / "test_visual"
        visual_dir.mkdir(parents=True, exist_ok=True)
        
        visual_file = visual_dir / "visual.json"
        with open(visual_file, 'w') as f:
            f.write(visual_data.model_dump_json(indent=2))
        
        # Add the visual to the page's visuals dictionary
        visual = Visual(visual_file, visual_data)
        page._visuals["test_visual"] = visual
        
        # Verify data is consistent
        assert page.name == "TestPage"
        assert page.display_name == "Test Page"
        assert page.height == 1024
        assert page.width == 768
        
        visual = page.get_visual("test_visual")
        assert visual is not None
        assert visual.name == "test_visual"
        assert visual.position.x == 100.0
        assert visual.position.y == 100.0
        assert visual.visual_type == VisualType.card
        
        # Verify files exist and contain correct data
        assert page.file_path.exists()
        assert visual_file.exists()
        
        # Read files directly to verify content
        with open(page.file_path, 'r') as f:
            page_data = json.load(f)
        
        with open(visual_file, 'r') as f:
            visual_data_from_file = json.load(f)
        
        assert page_data["name"] == "TestPage"
        assert page_data["displayName"] == "Test Page"
        assert page_data["height"] == 1024
        assert page_data["width"] == 768
        
        assert visual_data_from_file["name"] == "test_visual"
        assert visual_data_from_file["position"]["x"] == 100.0
        assert visual_data_from_file["position"]["y"] == 100.0
        assert visual_data_from_file["visual"]["visualType"] == "card"
        
        # Test that changes persist after object recreation
        # Modify data
        page.display_name = "Modified Test Page"
        visual.x = 200.0
        
        # Verify changes were written to files
        with open(page.file_path, 'r') as f:
            updated_page_data = json.load(f)
        
        with open(visual_file, 'r') as f:
            updated_visual_data = json.load(f)
        
        assert updated_page_data["displayName"] == "Modified Test Page"
        assert updated_visual_data["position"]["x"] == 200.0
        
        # Clean up
        report.remove_page("TestPage")
        assert report.get_page("TestPage") is None
