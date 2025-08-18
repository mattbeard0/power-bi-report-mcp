"""
Page-related models for Power BI reports
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from ..page.page import Page, PageData


class PagesData(BaseModel):
    """Page metadata including page order and active page"""
    pageOrder: List[str] = Field(default_factory=list)
    activePageName: str
    api_schema: str = Field(alias="$schema", default="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json")



class Pages:
    """Holds the metadata for the pages"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        with open(file_path, 'r') as f:
            self.data = PagesData.model_validate_json(f.read())

        self._pages: Dict[str, Page] = self._load_pages(file_path.parent)
        print(f"DEBUG: pages loaded: {self._pages}")
    
    def _load_pages(self, file_path: Path) -> Dict[str, Page]:
        """Load all pages for this report"""
        if not file_path.exists():
            print(f"DEBUG: file path does not exist: {file_path}")
            return {}
        
        pages = {}
        
        for page_folder in file_path.iterdir():
            if page_folder.is_dir():
                page_file = page_folder / "page.json"
                if page_file.exists():
                    try:
                        with open(page_file, 'r') as f:
                            page_model = Page(page_file)
                            pages[page_model.name] = page_model
                    except Exception as e:
                        print(f"Error loading page {page_folder}: {e}")
        return pages
    
    def write_back(self):
        """Write the page data back to its file"""
        if not self.file_path:
            raise ValueError("File path not set")
        
        try:
            with open(self.file_path, 'w') as f:
                f.write(self.data.model_dump_json(indent=2, by_alias=True, exclude_none=True))
            return True
        except Exception as e:
            print(f"Error writing page {self.file_path}: {e}")
            return False
        
    
    @property
    def page_order(self) -> List[str]:
        """Get the page order"""
        return self.data.pageOrder
    
    @property
    def active_page_name(self) -> str:
        """Get the active page name"""
        return self.data.activePageName
    
    @active_page_name.setter
    def active_page_name(self, value: str):
        """Set the active page name"""
        self.data.activePageName = value
        self.write_back()
    
    @property
    def pages(self) -> Dict[str, Page]:
        """Get all pages"""
        return self._pages
    
    def get_page(self, page_name: str) -> Optional[Page]:
        """Get a page by its name"""
        return self._pages.get(page_name)
    
    def add_page(self, page_name: str, display_name: str, width: int = 1280, height: int = 720) -> Page:
        """Add a new page to the report"""
        if page_name in self._pages:
            raise ValueError(f"Page {page_name} already exists")
        
        page_data = PageData(name=page_name, displayName=display_name, width=width, height=height)
        page = Page(self.file_path.parent / "pages" / page_name, page_data)
        self._pages[page_name] = page
        self.data.pageOrder.append(page_name)
        self.write_back()
        return page
    
    def remove_page(self, page_name: str) -> bool:
        """Remove a page from the report"""
        page = self._pages.get(page_name)
        if not page:
            return False  # Return False instead of raising exception
        
        page.remove()
        del self._pages[page_name]
        self.data.pageOrder.remove(page_name)
        self.write_back()
        return True
    
    def bring_page_to_front(self, page_name: str):
        """Bring a page to the front of the report"""
        page = self._pages.get(page_name)
        if not page:
            raise ValueError(f"Page {page_name} not found")
        
        self.data.pageOrder.remove(page_name)
        self.data.pageOrder.insert(0, page_name)
        self.write_back()
        return True
    
    def send_page_to_back(self, page_name: str):
        """Send a page to the back of the report"""
        page = self._pages.get(page_name)
        if not page:
            raise ValueError(f"Page {page_name} not found")
        
        self.data.pageOrder.remove(page_name)
        self.data.pageOrder.append(page_name)
        self.write_back()
        return True
    
    def order_pages(self, page_names: List[str]):
        """Order the pages in the report"""
        missing_pages = [page for page in page_names if page not in self._pages]

        self.data.pageOrder = page_names + missing_pages
        self.write_back()
        return True
    
    def __str__(self):
        """Return a string representation of the pages"""
        return f"Pages(file_path={self.file_path}, data={self.data})"
    
    def __repr__(self):
        """Return a string representation of the pages"""
        return self.__str__()