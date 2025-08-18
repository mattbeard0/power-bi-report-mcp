from fastapi import APIRouter, HTTPException, Query

from server.schemas.requests import ReportCreateRequest
from server.schemas.responses import SuccessResponse
from server.storage.reports import active_reports

router = APIRouter()


@router.post("/make_new_report", response_model=SuccessResponse, operation_id="make_new_report")
async def make_new_report(request: ReportCreateRequest):
    """Create a new Power BI report"""
    try:
        report_name = request.name

        if report_name in active_reports:
            raise HTTPException(
                status_code=400,
                detail=f"Report '{report_name}' already exists",
            )

        # Create the report using the existing Report class
        from models.report.report import Report  # local import to avoid cycles

        report = Report(report_name)
        active_reports[report_name] = report

        return SuccessResponse(
            success=True,
            message=f"Report '{report_name}' created successfully",
            data={"report_name": report_name},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")


@router.get("/list_reports", response_model=SuccessResponse, operation_id="list_reports")
async def list_reports():
    """List all active reports"""
    try:
        report_list = []
        for name, report in active_reports.items():
            pages = report.pages
            page_count = len(pages.pages) if pages else 0
            report_list.append({"name": name, "page_count": page_count, "path": str(report.report_path)})

        return SuccessResponse(
            success=True,
            message=f"Found {len(report_list)} active reports",
            data={"reports": report_list, "total_reports": len(report_list)},
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@router.delete("/delete_report", response_model=SuccessResponse, operation_id="delete_report")
async def delete_report(report_name: str = Query(..., description="Name of the report to delete")):
    """Delete a report from active memory (doesn't delete files)"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        del active_reports[report_name]

        return SuccessResponse(
            success=True,
            message=f"Report '{report_name}' removed from active memory",
            data={"deleted_report": report_name},
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete report: {str(e)}")
