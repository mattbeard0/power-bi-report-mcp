"""
Page-related models for Power BI reports
"""

from pathlib import Path
from typing import Dict, List, Optional
import uuid
from pydantic import BaseModel, Field
from ..visual.visual import Visual, VisualData, VisualPosition, VisualType, VisualVisual


class Pages(BaseModel):
    """Page metadata including page order and active page"""
    pageOrder: List[str] = Field(default_factory=list)
    activePageName: Optional[str] = None
    api_schema: str = Field(alias="$schema", default="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json")


class PageData(BaseModel):
    api_schema: str = Field(alias="$schema", default="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.0.0/schema.json")
    name: str
    displayName: str
    displayOption: str = Field(default="FitToPage")
    height: float = Field(default=720, gt=0)
    width: float = Field(default=1280, gt=0)

class Page:
    """Represents a Power BI page with visuals and file management capabilities"""
    
    def __init__(self, file_path: Path, data: Optional[PageData] = None):
        self.file_path = file_path
        if data:
            self.data = data
            # Ensure the directory exists and write the file
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.write_back()
        else:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.data = PageData.model_validate_json(f.read())
            else:
                raise FileNotFoundError(f"Page file not found: {file_path}")

        self._visuals: Dict[str, Visual] = self._load_visuals(file_path.parent / "visuals")
    
    def _load_visuals(self, file_path: Path) -> Dict[str, Visual]:
        """Load all visuals for this page"""
        if not file_path.exists():
            return {}
        
        visuals = {}
        
        for visual_folder in file_path.iterdir():
            if visual_folder.is_dir():
                visual_file = visual_folder / "visual.json"
                if visual_file.exists():
                    try:
                        with open(visual_file, 'r') as f:
                            visual_model = Visual(visual_file)
                            visuals[visual_model.name] = visual_model
                    except Exception as e:
                        print(f"Error loading visual {visual_file}: {e}")
        return visuals
    
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
        
    def remove(self):
        """Remove the page from the file system"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Page file not found: {self.file_path}")
        
        try:
            self.file_path.unlink()
    
            return True
        except Exception as e:
            print(f"Error removing page {self.file_path}: {e}")
            return False
    
    @property
    def name(self) -> str:
        """Get the name of the page"""
        return self.data.name
    
    @property
    def display_name(self) -> str:
        """Get the display name of the page"""
        return self.data.displayName
    
    @display_name.setter
    def display_name(self, value: str):
        """Set the display name of the page"""
        self.data.displayName = value
        self.write_back()
    
    @property
    def display_option(self) -> str:
        """Get the display option of the page"""
        return self.data.displayOption
    
    @display_option.setter
    def display_option(self, value: str):
        """Set the display option of the page"""
        self.data.displayOption = value
        self.write_back()
    
    @property
    def height(self) -> float:
        """Get the height of the page"""
        return self.data.height
    
    @height.setter
    def height(self, value: float):
        """Set the height of the page"""
        self.data.height = value
        self.write_back()

    @property
    def width(self) -> float:
        """Get the width of the page"""
        return self.data.width
    
    @width.setter
    def width(self, value: float):
        """Set the width of the page"""
        self.data.width = value
        self.write_back()

    @property
    def visuals(self) -> Dict[str, Visual]:
        """Get all visuals on this page"""
        return self._visuals
    
    def get_visual(self, visual_id: str) -> Optional[Visual]:
        """Get a visual by its ID"""
        return self._visuals.get(visual_id)
    
    def add_visual(self, x: float, y: float, width: float, height: float, visual_type: VisualType, z: float = 0.0) -> Visual:
        name = str(uuid.uuid4())[:8]
        file_path = self.file_path.parent / "visuals" / name

        visual_position = VisualPosition(x=x, y=y, z=z, width=width, height=height)
        visual_visual = VisualVisual(visualType=visual_type, drillFilterOtherVisuals=True)
        visual_data = VisualData(name=name, position=visual_position, visual=visual_visual)

        visual = Visual(file_path, visual_data)
        visual.write_back()
        self._visuals[visual.name] = visual
        return visual
    
    def remove_visual(self, visual_id: str):
        """Remove a visual by its ID"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.remove()
            del self._visuals[visual_id]

    def set_visual_to_percentage_page_width(self, visual_id: str, percentage: float):
        """Set a visual to a percentage width"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.width = self.width * percentage
            visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
    def set_visual_to_percentage_page_height(self, visual_id: str, percentage: float):
        """Set a visual to a percentage height"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.height = self.height * percentage
            visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
    def set_visual_to_percentage_page_width_and_height(self, visual_id: str, percentage_width: float, percentage_height: float):
        """Set a visual to a percentage width and height"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.width = self.width * percentage_width
            visual.height = self.height * percentage_height
            visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
    def check_visual_overlaps(self, visual_id: str) -> Dict[str, VisualPosition]:
        """Check if the visual overlaps with all other visuals, and return those visual IDs and positions."""
        overlaps = {}
        
        for visual_name, visual in self._visuals.items():
            if visual_name == visual_id:
                continue
            if visual.x + visual.width > visual.x and visual.y + visual.height > visual.y:
                overlaps[visual_name] = visual.position
        return overlaps

    def bring_visual_to_front(self, visual_id: str):
        """Bring a visual to the front of the page"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.z = max(visual.z for visual in self._visuals.values()) + 1
            visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
    def send_visual_to_back(self, visual_id: str):
        """Send a visual to the back of the page"""
        for visual_name, visual in self._visuals.items():
            visual.z += 1
            visual.write_back()
        
        target_visual = self._visuals.get(visual_id)
        if target_visual:
            target_visual.z = 0
            target_visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
    def move_visual_to_position(self, visual_id: str, x: float, y: float):
        """Move a visual to a position"""
        visual = self._visuals.get(visual_id)
        if visual:
            visual.x = x
            visual.y = y
            visual.write_back()
            return
        raise ValueError(f"Visual {visual_id} not found")
    
