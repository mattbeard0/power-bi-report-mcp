from pydantic import BaseModel, Field
from typing import Optional, Dict

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
