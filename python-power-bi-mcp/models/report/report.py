"""
Core Report object that contains file paths and metadata for the active project
"""
import shutil
import json
from pathlib import Path
from typing import Dict, Optional

from ..pages.pages import Pages
from ..page.page import Page

class Report:
    """Represents a Power BI report with all its components loaded into memory"""
    
    def __init__(self, name: str):
        self.name = name
        self.report_path = Path("reports") / name
        self.baseline_path = Path("baseline_report")
        
        # Initialize report if it doesn't exist
        if not self.report_path.exists():
            self._create_from_baseline()
        
        # Load pages and report structure
        self._pages: Optional[Pages] = None
        self._load_report_structure()
    
    def _create_from_baseline(self):
        """Create a new report by copying the baseline report structure"""
        if not self.baseline_path.exists():
            raise FileNotFoundError(f"Baseline report not found at {self.baseline_path}")
        
        # Create the reports directory if it doesn't exist
        self.report_path.parent.mkdir(exist_ok=True)
        
        # Copy the entire baseline report structure
        shutil.copytree(self.baseline_path, self.report_path)
        
        # Rename the baseline files to match the new report name
        self._rename_baseline_files()
        
        # Update the pbip file to reference the new report name
        self._update_pbip_references()
        
        # Update the definition.pbir file to reference the new dataset name
        self._update_definition_pbir()
    
    def _rename_baseline_files(self):
        """Rename baseline files to match the new report name"""
        # Rename the main report folder
        old_report_folder = self.report_path / "report_sample.Report"
        new_report_folder = self.report_path / f"{self.name}.Report"
        
        if old_report_folder.exists():
            old_report_folder.rename(new_report_folder)
        
        # Rename the dataset folder
        old_dataset_folder = self.report_path / "report_sample.Dataset"
        new_dataset_folder = self.report_path / f"{self.name}.Dataset"
        
        if old_dataset_folder.exists():
            old_dataset_folder.rename(new_dataset_folder)
        
        # Rename the pbip file
        old_pbip = self.report_path / "report_sample.pbip"
        new_pbip = self.report_path / f"{self.name}.pbip"
        
        if old_pbip.exists():
            old_pbip.rename(new_pbip)
    
    def _update_pbip_references(self):
        """Update the pbip file to reference the new report name"""
        pbip_file = self.report_path / f"{self.name}.pbip"
        
        if pbip_file.exists():
            with open(pbip_file, 'r') as f:
                pbip_data = json.load(f)
            
            # Update the report path in the artifacts
            if 'artifacts' in pbip_data and len(pbip_data['artifacts']) > 0:
                if 'report' in pbip_data['artifacts'][0]:
                    pbip_data['artifacts'][0]['report']['path'] = f"{self.name}.Report"
            
            # Write the updated pbip file
            with open(pbip_file, 'w') as f:
                json.dump(pbip_data, f, indent=2)
    
    def _update_definition_pbir(self):
        """Update the definition.pbir file to reference the new dataset name"""
        definition_file = self.report_path / f"{self.name}.Report" / "definition.pbir"
        
        if definition_file.exists():
            with open(definition_file, 'r') as f:
                definition_data = json.load(f)
            
            # Update the dataset reference path
            if 'datasetReference' in definition_data and 'byPath' in definition_data['datasetReference']:
                definition_data['datasetReference']['byPath']['path'] = f"../{self.name}.Dataset"
            
            # Write the updated definition file
            with open(definition_file, 'w') as f:
                json.dump(definition_data, f, indent=2)
    
    def _load_report_structure(self):
        """Load the report structure including pages and metadata"""
        report_folder = self.report_path / f"{self.name}.Report"
        
        if not report_folder.exists():
            raise FileNotFoundError(f"Report folder not found: {report_folder}")
        
        # Load pages metadata
        pages_file = report_folder / "definition" / "pages" / "pages.json"
        if pages_file.exists():
            self._pages = Pages(pages_file)
        else:
            self._pages = None
    
    @property
    def pages(self) -> Optional[Pages]:
        """Get the pages object for this report"""
        return self._pages
    
    def get_page(self, page_name: str) -> Optional[Page]:
        """Get a specific page by name"""
        if self._pages:
            return self._pages.get_page(page_name)
        return None
    
    def add_page(self, page_name: str, display_name: str, width: int = 1280, height: int = 720) -> Optional[Page]:
        """Add a new page to the report"""
        if self._pages:
            return self._pages.add_page(page_name, display_name, width, height)
        return None
    
    def remove_page(self, page_name: str) -> bool:
        """Remove a page from the report"""
        if self._pages:
            return self._pages.remove_page(page_name)
        return False
    
    def exists(self) -> bool:
        """Check if the report exists on disk"""
        return self.report_path.exists()
    
    def get_report_path(self) -> Path:
        """Get the full path to the report"""
        return self.report_path
    
    def get_report_folder(self) -> Path:
        """Get the path to the main report folder"""
        return self.report_path / f"{self.name}.Report"
        
