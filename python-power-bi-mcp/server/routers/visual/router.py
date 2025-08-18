from fastapi import APIRouter, HTTPException

from server.schemas.requests import ChartCreateRequest, ChartSizeRequest
from server.schemas.responses import SuccessResponse
from server.storage.reports import active_reports
from models.visual.visual import VisualType

router = APIRouter()


@router.post("/add_visual", response_model=SuccessResponse, operation_id="add_visual")
async def add_visual(report_name: str, request: ChartCreateRequest):
    """Add a chart to a page in a report"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        pages = report.pages

        if pages is None:
            raise HTTPException(status_code=404, detail="No pages found in report")

        page_name = request.page_name
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}",
            )

        # Validate chart type
        if request.chart_type not in ["lineChart", "barChart"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chart type '{request.chart_type}'. Supported types: lineChart, barChart",
            )

        page = pages.pages[page_name]

        # Convert chart type string to VisualType enum
        visual_type = VisualType(request.chart_type)

        # Add the visual to the page
        visual = page.add_visual(
            x=request.x, y=request.y, width=request.width, height=request.height, visual_type=visual_type
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
                    "height": request.height,
                },
                "page_name": page_name,
                "report_name": report_name,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add chart: {str(e)}")
    
@router.post("/remove_visual", response_model=SuccessResponse, operation_id="remove_visual")
async def remove_visual(report_name: str, visual_id: str):
    """Remove a visual from a page in a report"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        pages = report.pages

        if pages is None:
            raise HTTPException(status_code=404, detail="No pages found in report")

        # Find the visual to remove
        for page in pages.pages.values():
            if visual_id in page.visuals:
                page.remove_visual(visual_id)
                return SuccessResponse(
                    success=True,
                    message=f"Visual '{visual_id}' removed from report '{report_name}'",
                    data={"visual_id": visual_id, "page_name": page.name}
                )

        raise HTTPException(status_code=404, detail=f"Visual '{visual_id}' not found in report '{report_name}'")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove visual: {str(e)}")


@router.post("/change_chart_size", response_model=SuccessResponse, operation_id="change_chart_size")
async def change_chart_size(report_name: str, request: ChartSizeRequest):
    """Change the size of a chart on a page"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        pages = report.pages

        if pages is None:
            raise HTTPException(status_code=404, detail="No pages found in report")

        page_name = request.page_name
        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}",
            )

        page = pages.pages[page_name]
        chart_id = request.chart_id

        if chart_id not in page.visuals:
            available_charts = list(page.visuals.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Chart '{chart_id}' not found on page '{page_name}'. Available charts: {available_charts}",
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
                "new_size": {"width": request.width, "height": request.height},
                "page_name": page_name,
                "report_name": report_name,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to change chart size: {str(e)}")
