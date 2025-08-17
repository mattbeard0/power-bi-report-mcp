"""
Test script for the Power BI MCP Server
Run this after starting the server to test all endpoints
"""

import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an endpoint and return the response"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, params=params)
        else:
            print(f"Unsupported method: {method}")
            return None
            
        print(f"\n{method.upper()} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success:")
            print(json.dumps(result, indent=2))
            return result
        else:
            print("❌ Error:")
            print(response.text)
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Could not connect to {url}")
        print("Make sure the server is running with: python main.py")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    """Run all tests"""
    print("🧪 Testing Power BI MCP Server")
    print("=" * 50)
    
    # Test 1: Health check
    test_endpoint("GET", "/health")
    
    # Test 2: List reports (should be empty initially)
    test_endpoint("GET", "/list_reports")
    
    # Test 3: Create a new report
    report_data = {"name": "test_report"}
    test_endpoint("POST", "/make_new_report", data=report_data)
    
    # Test 4: List reports again (should have one report)
    test_endpoint("GET", "/list_reports")
    
    # Test 5: Get all pages in the report
    test_endpoint("GET", "/get_all_pages", params={"report_name": "test_report"})
    
    # Test 6: Get page details (using the first page found)
    test_endpoint("GET", "/get_page_details", params={"report_name": "test_report", "page_name": "ReportSection"})
    
    # Test 7: Add a bar chart
    chart_data = {
        "page_name": "ReportSection",
        "chart_type": "barChart",
        "x": 100,
        "y": 100,
        "width": 400,
        "height": 300
    }
    chart_response = test_endpoint("POST", "/add_chart", data=chart_data)
    
    # Test 8: Add a line chart
    line_chart_data = {
        "page_name": "ReportSection",
        "chart_type": "lineChart",
        "x": 550,
        "y": 100,
        "width": 400,
        "height": 300
    }
    line_chart_response = test_endpoint("POST", "/add_chart", data=line_chart_data)
    
    # Test 9: Get page details again (should show the new charts)
    test_endpoint("GET", "/get_page_details", params={"report_name": "test_report", "page_name": "ReportSection"})
    
    # Test 10: Change chart size (if we have a chart)
    if chart_response and chart_response.get("data", {}).get("chart_id"):
        chart_id = chart_response["data"]["chart_id"]
        size_data = {
            "page_name": "ReportSection",
            "chart_id": chart_id,
            "width": 500,
            "height": 400
        }
        test_endpoint("POST", "/change_chart_size", data=size_data)
        
        # Verify the size change
        test_endpoint("GET", "/get_page_details", params={"report_name": "test_report", "page_name": "ReportSection"})
    
    # Test 11: Try to add chart to non-existent page (should fail)
    invalid_chart_data = {
        "page_name": "NonExistentPage",
        "chart_type": "barChart",
        "x": 0,
        "y": 0,
        "width": 200,
        "height": 200
    }
    test_endpoint("POST", "/add_chart", data=invalid_chart_data)
    
    # Test 12: Try to get details of non-existent page (should fail)
    test_endpoint("GET", "/get_page_details", params={"report_name": "test_report", "page_name": "NonExistentPage"})
    
    # Test 13: Try to create duplicate report (should fail)
    test_endpoint("POST", "/make_new_report", data=report_data)
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")
    print("\nTo clean up, you can delete the test report:")
    print(f"DELETE {BASE_URL}/delete_report?report_name=test_report")

if __name__ == "__main__":
    main()
