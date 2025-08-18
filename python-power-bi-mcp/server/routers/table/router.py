from fastapi import APIRouter, HTTPException, Query
from server.schemas.responses import SuccessResponse
from server.storage.reports import active_reports

router = APIRouter()


@router.get("/get_tables", response_model=SuccessResponse, operation_id="get_tables")
async def get_tables(report_name: str = Query(..., description="Name of the report")):
    """List all non-hidden tables in the report's dataset"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        if report.tables is None:
            return SuccessResponse(success=True, message="No tables found", data={"tables": []})

        table_names = report.tables.list_tables()
        return SuccessResponse(success=True, message=f"Found {len(table_names)} tables", data={"tables": table_names})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tables: {str(e)}")


@router.get("/get_table_columns", response_model=SuccessResponse, operation_id="get_table_columns")
async def get_table_columns(
    report_name: str = Query(..., description="Name of the report"),
    table_name: str = Query(..., description="Name of the table"),
):
    """Get columns for a specific table with dataType and summarizeBy"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        if report.tables is None:
            raise HTTPException(status_code=404, detail="No tables found in report")

        table = report.tables.get_table(table_name)
        if table is None:
            available = report.tables.list_tables()
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found. Available: {available}",
            )

        cols = [
            {
                "name": c.name,
                "dataType": c.dataType,
                "summarizeBy": c.summarizeBy,
                "formatString": c.formatString,
                "sourceColumn": c.sourceColumn,
            }
            for c in table.data.columns
        ]
        return SuccessResponse(success=True, message=f"Found {len(cols)} columns", data={"columns": cols})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get table columns: {str(e)}")


@router.get("/get_relationships", response_model=SuccessResponse, operation_id="get_relationships")
async def get_relationships(report_name: str = Query(..., description="Name of the report")):
    """Get relationships from the dataset"""
    try:
        if report_name not in active_reports:
            available_reports = list(active_reports.keys())
            raise HTTPException(
                status_code=404,
                detail=f"Report '{report_name}' not found. Available reports: {available_reports}",
            )

        report = active_reports[report_name]
        if report.tables is None:
            return SuccessResponse(success=True, message="No relationships found", data={"relationships": []})

        rels = [
            {
                "id": r.id,
                "fromColumn": r.fromColumn,
                "toColumn": r.toColumn,
            }
            for r in report.tables.relationships
        ]
        return SuccessResponse(success=True, message=f"Found {len(rels)} relationships", data={"relationships": rels})

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get relationships: {str(e)}")
