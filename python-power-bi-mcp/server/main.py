"""
Power BI MCP Server - FastAPI implementation
Provides endpoints for Power BI report operations
"""

import sys
from pathlib import Path
from fastapi import FastAPI
import uvicorn
from fastapi_mcp import FastApiMCP

# Ensure project root is on sys.path for model imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

# Routers and shared state
from server.routers.report.router import router as report_router
from server.routers.page.router import router as page_router
from server.routers.visual.router import router as visual_router
from server.storage.reports import active_reports

app = FastAPI(
    title="Power BI MCP Server",
    description="A FastAPI server for Power BI report operations",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "active_reports": len(active_reports)}

# Mount routers (paths unchanged)
app.include_router(report_router)
app.include_router(page_router)
app.include_router(visual_router)

if __name__ == "__main__":
    mcp = FastApiMCP(app, exclude_operations=[])
    mcp.mount_http()
    uvicorn.run(app, host="0.0.0.0", port=8000)
