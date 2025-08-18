from pathlib import Path
from typing import Dict

from models.report.report import Report

# In-memory storage for active reports
active_reports: Dict[str, Report] = {}


def load_reports() -> Dict[str, Report]:
    """Load all reports from the reports directory.

    Note: Not called automatically to keep initial state empty for tests.
    Call this explicitly if you want to preload filesystem reports.
    """
    reports: Dict[str, Report] = {}
    reports_dir = Path("reports")
    if reports_dir.exists():
        for report_dir in reports_dir.iterdir():
            if report_dir.is_dir():
                reports[report_dir.name] = Report(report_dir.name)
                print(f"DEBUG: report {report_dir.name} loaded")
    return reports

active_reports = load_reports()
