from fastapi import APIRouter, HTTPException, Query

from server.schemas.requests import PageResizeRequest
from server.schemas.responses import SuccessResponse
from server.storage.reports import active_reports

router = APIRouter()


@router.get("/get_all_pages", response_model=SuccessResponse, operation_id="get_all_pages")
async def get_all_pages(report_name: str = Query(..., description="Name of the report")):
    """Get all pages in a report"""
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
            return SuccessResponse(
                success=True,
                message="No pages found in report",
                data={"pages": [], "page_names": []},
            )

        page_ids = [p.name for p in pages.pages.values()]
        page_names = [p.display_name for p in pages.pages.values()]

        return SuccessResponse(
            success=True,
            message=f"Found {len(pages.data.pageOrder)} pages in report '{report_name}'",
            data={"pages": page_ids, "page_ids": page_ids, "page_names": page_names},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pages: {str(e)}")


@router.get("/get_page_details", response_model=SuccessResponse, operation_id="get_page_details")
async def get_page_details(
    report_name: str = Query(..., description="Name of the report"),
    page_name: str = Query(..., description="Name of the page"),
):
    """Get details of a specific page"""
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

        if page_name not in pages.pages:
            available_pages = list(pages.pages.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Page '{page_name}' not found in report '{report_name}'. Available pages: {available_pages}",
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
                        "height": visual.height,
                    }
                    for visual in page.visuals.values()
                ],
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get page details: {str(e)}")


@router.post("/resize_page", response_model=SuccessResponse, operation_id="resize_page")
async def resize_page(report_name: str, request: PageResizeRequest):
    """Resize a page in a report"""
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

        # Update the page size
        page.width = request.width
        page.height = request.height

        return SuccessResponse(
            success=True,
            message=f"Page '{page_name}' resized to {request.width}x{request.height}",
            data={
                "page_name": page_name,
                "report_name": report_name,
                "new_size": {"width": request.width, "height": request.height},
            },
        )

    except HTTPException:
        raise
