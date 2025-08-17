"""
Power BI MCP Server - FastAPI implementation
Provides endpoints for Power BI report operations
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import uvicorn
from fastapi_mcp import FastApiMCP

# Add the parent directory to the path so we can import the models
sys.path.append(str(Path(__file__).parent.parent))

from models.report.report import Report
from models.page.page import Page
from models.visual.visual import Visual, VisualType
from models.pages.pages import Pages

app = FastAPI(
    title="Power BI MCP Server",
    description="A FastAPI server for Power BI report operations",
    version="1.0.0"
)

# In-memory storage for active reports
active_reports: Dict[str, Report] = {}

def load_reports() -> Dict[str, Report]:
    """Load all reports from the reports directory"""
    reports = {}
    for report_dir in Path("reports").iterdir():
        if report_dir.is_dir():
            reports[report_dir.name] = Report(report_dir.name)
            print(f"DEBUG: report {report_dir.name} loaded")
    return reports

active_reports = load_reports()

class ReportCreateRequest(BaseModel):
    name: str = Field(..., description="Name of the report to create")

class ChartCreateRequest(BaseModel):
    page_name: str = Field(..., description="Name of the page to add the chart to")
    chart_type: str = Field(..., description="Type of chart (lineChart or barChart)")
    x: float = Field(default=0.0, description="X coordinate for the chart")
    y: float = Field(default=0.0, description="Y coordinate for the chart")
    width: float = Field(default=400.0, description="Width of the chart")
    height: float = Field(default=300.0, description="Height of the chart")

class ChartSizeRequest(BaseModel):
    page_name: str = Field(..., description="Name of the page containing the chart")
    chart_id: str = Field(..., description="ID of the chart to resize")
    width: float = Field(..., description="New width of the chart")
    height: float = Field(..., description="New height of the chart")

class PageResizeRequest(BaseModel):
    page_name: str = Field(..., description="Name of the page to resize")
    width: float = Field(..., description="New width of the page")
    height: float = Field(..., description="New height of the page")

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict] = None

class SuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Power BI MCP Server is running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_reports": len(active_reports)}

@app.post("/make_new_report", response_model=SuccessResponse, operation_id="make_new_report")
async def make_new_report(request: ReportCreateRequest):
    """Create a new Power BI report"""
    try:
        report_name = request.name
        
        if report_name in active_reports:
            raise HTTPException(
                status_code=400, 
                detail=f"Report '{report_name}' already exists"
            )
        
        # Create the report using the existing Report class
        report = Report(report_name)
        active_reports[report_name] = report
        
        return SuccessResponse(
            success=True,
            message=f"Report '{report_name}' created successfully",
            data={"report_name": report_name}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create report: {str(e)}"
        )

@app.get("/get_all_pages", response_model=SuccessResponse, operation_id="get_all_pages")
async def get_all_pages(report_name: str = Query(..., description="Name of the report")):
    """Get all pages in a report"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        report = active_reports[report_name]
        pages = report.pages
        
        if pages is None:
            return SuccessResponse(
                success=True,
                message="No pages found in report",
                data={"pages": [], "page_names": []}
            )
        
        page_ids = [p.name for p in pages.pages.values()]
        page_names = [p.display_name for p in pages.pages.values()]
        
        return SuccessResponse(
            success=True,
            message=f"Found {len(pages.data.pageOrder)} pages in report '{report_name}'",
            data={
                "page_ids": page_ids,
                "page_names": page_names
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pages: {str(e)}"
        )

@app.get("/get_page_details", response_model=SuccessResponse, operation_id="get_page_details")
async def get_page_details(
    report_name: str = Query(..., description="Name of the report"),
    page_name: str = Query(..., description="Name of the page")
):
    """Get details of a specific page"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        report = active_reports[report_name]
        pages = report.pages
        
        if pages is None:
            raise HTTPException(
                status_code=404,
                detail="No pages found in report"
            )
        
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}"
            )
        
        page = pages.pages[page_name]
        
        return SuccessResponse(
            success=True,
            message=f"Page details retrieved for '{page_name}'",
            data={
                "name": page.name,
                "display_name": page.display_name,
                "width": page.width,
                "height": page.height,
                "display_option": page.display_option,
                "visual_count": len(page.visuals),
                "visuals": [
                    {
                        "id": visual.name,
                        "type": visual.visual_type,
                        "x": visual.x,
                        "y": visual.y,
                        "width": visual.width,
                        "height": visual.height
                    }
                    for visual in page.visuals.values()
                ]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get page details: {str(e)}"
        )
    
@app.post("/resize_page", response_model=SuccessResponse, operation_id="resize_page")
async def resize_page(report_name: str, request: PageResizeRequest):
    """Resize a page in a report"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        report = active_reports[report_name]
        pages = report.pages
        
        if pages is None:
            raise HTTPException(
                status_code=404,
                detail="No pages found in report"
            )
        
        page_name = request.page_name
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}"
            )
        
        page = pages.pages[page_name]
        
        # Update the page size
        page.width = request.width
        page.height = request.height
        
        return SuccessResponse(
            success=True,
            message=f"Page '{page_name}' resized to {request.width}x{request.height}",
            data={
                "page_name": page_name,
                "report_name": report_name,
                "new_size": {
                    "width": request.width,
                    "height": request.height
                }
            }
        )
        
    except HTTPException:
        raise

@app.post("/add_chart", response_model=SuccessResponse, operation_id="add_chart")
async def add_chart(report_name: str, request: ChartCreateRequest):
    """Add a chart to a page in a report"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        report = active_reports[report_name]
        pages = report.pages
        
        if pages is None:
            raise HTTPException(
                status_code=404,
                detail="No pages found in report"
            )
        
        page_name = request.page_name
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}"
            )
        
        # Validate chart type
        if request.chart_type not in ["lineChart", "barChart"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chart type '{request.chart_type}'. Supported types: lineChart, barChart"
            )
        
        page = pages.pages[page_name]
        
        # Convert chart type string to VisualType enum
        visual_type = VisualType(request.chart_type)
        
        # Add the visual to the page
        visual = page.add_visual(
            x=request.x,
            y=request.y,
            width=request.width,
            height=request.height,
            visual_type=visual_type
        )
        
        return SuccessResponse(
            success=True,
            message=f"Chart '{request.chart_type}' added to page '{page_name}' in report '{report_name}'",
            data={
                "chart_id": visual.name,
                "chart_type": request.chart_type,
                "position": {
                    "x": request.x,
                    "y": request.y,
                    "width": request.width,
                    "height": request.height
                },
                "page_name": page_name,
                "report_name": report_name
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add chart: {str(e)}"
        )

@app.post("/change_chart_size", response_model=SuccessResponse, operation_id="change_chart_size")
async def change_chart_size(report_name: str, request: ChartSizeRequest):
    """Change the size of a chart on a page"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        report = active_reports[report_name]
        pages = report.pages
        
        if pages is None:
            raise HTTPException(
                status_code=404,
                detail="No pages found in report"
            )
        
        page_name = request.page_name
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}"
            )
        
        page = pages.pages[page_name]
        chart_id = request.chart_id
        
        if chart_id not in page.visuals:
            available_charts = list(page.visuals.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Chart '{chart_id}' not found on page '{page_name}'. Available charts: {available_charts}"
            )
        
        visual = page.visuals[chart_id]
        
        # Update the chart size
        visual.width = request.width
        visual.height = request.height
        
        return SuccessResponse(
            success=True,
            message=f"Chart '{chart_id}' size updated to {request.width}x{request.height}",
            data={
                "chart_id": chart_id,
                "new_size": {
                    "width": request.width,
                    "height": request.height
                },
                "page_name": page_name,
                "report_name": report_name
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to change chart size: {str(e)}"
        )

@app.get("/list_reports", response_model=SuccessResponse, operation_id="list_reports")
async def list_reports():
    """List all active reports"""
    try:
        report_list = []
        for name, report in active_reports.items():
            pages = report.pages
            page_count = len(pages.pages) if pages else 0
            report_list.append({
                "name": name,
                "page_count": page_count,
                "path": str(report.report_path)
            })
        
        return SuccessResponse(
            success=True,
            message=f"Found {len(report_list)} active reports",
            data={
                "reports": report_list,
                "total_reports": len(report_list)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list reports: {str(e)}"
        )

@app.delete("/delete_report", response_model=SuccessResponse, operation_id="delete_report")
async def delete_report(report_name: str = Query(..., description="Name of the report to delete")):
    """Delete a report from active memory (doesn't delete files)"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}"
            )
        
        del active_reports[report_name]
        
        return SuccessResponse(
            success=True,
            message=f"Report '{report_name}' removed from active memory",
            data={"deleted_report": report_name}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )

if __name__ == "__main__":
    mcp = FastApiMCP(app, include_operations=["make_new_report", "get_all_pages", "get_page_details", "add_chart", "change_chart_size", "list_reports", "delete_report", "resize_page"])
    mcp.mount()
    uvicorn.run(app, host="0.0.0.0", port=8000)
