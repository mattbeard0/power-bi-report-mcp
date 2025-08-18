"""
Tests for the Power BI MCP Server
"""

import pytest
import requests
import json
from pathlib import Path
import sys

# Add the server directory to the path
sys.path.append(str(Path(__file__).parent.parent))
from server.main import app
from fastapi.testclient import TestClient

# Create a test client
client = TestClient(app)

class TestPowerBIServer:
    """Test class for Power BI MCP Server endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Power BI MCP Server is running" in response.json()["message"]
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "active_reports" in response.json()
    
    def test_list_reports_empty(self):
        """Test listing reports when none exist"""
        response = client.get("/list_reports")
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert response.json()["data"]["total_reports"] == 0
    
    def test_create_report(self):
        """Test creating a new report"""
        report_data = {"name": "test_report_create"}
        response = client.post("/make_new_report", json=report_data)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "test_report_create" in response.json()["message"]
    
    def test_create_duplicate_report(self):
        """Test creating a duplicate report (should fail)"""
        report_data = {"name": "test_report_duplicate"}
        
        # Create first report
        response1 = client.post("/make_new_report", json=report_data)
        assert response1.status_code == 200
        
        # Try to create duplicate
        response2 = client.post("/make_new_report", json=report_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"]
    
    def test_get_all_pages(self):
        """Test getting all pages from a report"""
        # First create a report
        report_data = {"name": "test_report_pages"}
        client.post("/make_new_report", json=report_data)
        
        # Get pages
        response = client.get("/get_all_pages", params={"report_name": "test_report_pages"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "pages" in response.json()["data"]
    
    def test_get_page_details(self):
        """Test getting details of a specific page"""
        # First create a report
        report_data = {"name": "test_report_page_details"}
        client.post("/make_new_report", json=report_data)
        
        # Get page details (using the default page that should exist)
        response = client.get("/get_page_details", params={
            "report_name": "test_report_page_details",
            "page_name": "ReportSection"
        })
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "width" in response.json()["data"]
        assert "height" in response.json()["data"]
    
    def test_get_nonexistent_page(self):
        """Test getting details of a non-existent page"""
        # First create a report
        report_data = {"name": "test_report_nonexistent_page"}
        client.post("/make_new_report", json=report_data)
        
        # Try to get non-existent page
        response = client.get("/get_page_details", params={
            "report_name": "test_report_nonexistent_page",
            "page_name": "NonExistentPage"
        })
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_add_chart(self):
        """Test adding a chart to a page"""
        # First create a report
        report_data = {"name": "test_report_add_chart"}
        client.post("/make_new_report", json=report_data)
        
        # Add a chart
        chart_data = {
            "page_name": "ReportSection",
            "chart_type": "barChart",
            "x": 100,
            "y": 100,
            "width": 400,
            "height": 300
        }
        response = client.post("/add_chart", json=chart_data, params={"report_name": "test_report_add_chart"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "chart_id" in response.json()["data"]
    
    def test_add_chart_invalid_type(self):
        """Test adding a chart with invalid type"""
        # First create a report
        report_data = {"name": "test_report_invalid_chart"}
        client.post("/make_new_report", json=report_data)
        
        # Try to add invalid chart type
        chart_data = {
            "page_name": "ReportSection",
            "chart_type": "invalidChart",
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 200
        }
        response = client.post("/add_chart", json=chart_data, params={"report_name": "test_report_invalid_chart"})
        assert response.status_code == 400
        assert "Invalid chart type" in response.json()["detail"]
    
    def test_add_chart_to_nonexistent_page(self):
        """Test adding a chart to a non-existent page"""
        # First create a report
        report_data = {"name": "test_report_chart_nonexistent_page"}
        client.post("/make_new_report", json=report_data)
        
        # Try to add chart to non-existent page
        chart_data = {
            "page_name": "NonExistentPage",
            "chart_type": "barChart",
            "x": 0,
            "y": 0,
            "width": 200,
            "height": 200
        }
        response = client.post("/add_chart", json=chart_data, params={"report_name": "test_report_chart_nonexistent_page"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_change_chart_size(self):
        """Test changing chart size"""
        # First create a report and add a chart
        report_data = {"name": "test_report_change_size"}
        client.post("/make_new_report", json=report_data)
        
        chart_data = {
            "page_name": "ReportSection",
            "chart_type": "lineChart",
            "x": 200,
            "y": 200,
            "width": 300,
            "height": 200
        }
        chart_response = client.post("/add_chart", json=chart_data, params={"report_name": "test_report_change_size"})
        assert chart_response.status_code == 200
        
        chart_id = chart_response.json()["data"]["chart_id"]
        
        # Change chart size
        size_data = {
            "page_name": "ReportSection",
            "chart_id": chart_id,
            "width": 500,
            "height": 400
        }
        response = client.post("/change_chart_size", json=size_data, params={"report_name": "test_report_change_size"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "size updated" in response.json()["message"]
    
    def test_delete_report(self):
        """Test deleting a report from active memory"""
        # First create a report
        report_data = {"name": "test_report_delete"}
        client.post("/make_new_report", json=report_data)
        
        # Verify report exists
        list_response = client.get("/list_reports")
        assert list_response.status_code == 200
        initial_count = list_response.json()["data"]["total_reports"]
        
        # Delete report
        response = client.delete("/delete_report", params={"report_name": "test_report_delete"})
        assert response.status_code == 200
        assert response.json()["success"] is True
        
        # Verify report is deleted
        list_response_after = client.get("/list_reports")
        assert list_response_after.status_code == 200
        final_count = list_response_after.json()["data"]["total_reports"]
        assert final_count == initial_count - 1
    
    def test_delete_nonexistent_report(self):
        """Test deleting a non-existent report"""
        response = client.delete("/delete_report", params={"report_name": "nonexistent_report"})
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_tables_endpoints(self):
        """Test listing tables, columns, and relationships"""
        report_name = "test_report_tables"
        client.post("/make_new_report", json={"name": report_name})

        # list tables
        resp_tables = client.get("/get_tables", params={"report_name": report_name})
        assert resp_tables.status_code == 200
        assert resp_tables.json()["success"] is True
        assert "tables" in resp_tables.json()["data"]

        # if a known sample table exists (like DummyData), try fetching columns
        tables = resp_tables.json()["data"]["tables"]
        if tables:
            first_table = tables[0]
            resp_cols = client.get(
                "/get_table_columns",
                params={"report_name": report_name, "table_name": first_table},
            )
            assert resp_cols.status_code == 200
            assert resp_cols.json()["success"] is True
            assert "columns" in resp_cols.json()["data"]

        # relationships
        resp_rels = client.get("/get_relationships", params={"report_name": report_name})
        assert resp_rels.status_code == 200
        assert resp_rels.json()["success"] is True
        assert "relationships" in resp_rels.json()["data"]

if __name__ == "__main__":
    pytest.main([__file__])
