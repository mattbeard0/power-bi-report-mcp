"""
Visual-related models for Power BI reports
"""

from typing import Optional
from pathlib import Path
from enum import Enum
from pydantic import BaseModel, Field


class VisualType(str, Enum):
    """Valid visual types for Power BI"""
    card = "card"
    barChart = "barChart"
    lineChart = "lineChart"
    # TO IMPLEMENT LATER
    # pieChart = "pieChart"
    # table = "table"
    # slicer = "slicer"
    # matrix = "matrix"
    # scatterChart = "scatterChart"
    # areaChart = "areaChart"
    # columnChart = "columnChart"
    # funnelChart = "waterfall"
    # gauge = "gauge"
    # map = "map"
    # waterfall = "waterfall"

class VisualPosition(BaseModel):
    x: float = Field(default=0.0, ge=0.0)
    y: float = Field(default=0.0, ge=0.0)
    z: float = Field(default=0.0, ge=0.0)
    height: float = Field(ge=0.0)
    width: float = Field(ge=0.0)
    angle: Optional[float] = None

class VisualVisual(BaseModel):
    visualType: VisualType
    drillFilterOtherVisuals: bool = Field(default=True)

class VisualData(BaseModel):
    api_schema: str = Field(alias="$schema", default="https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.1.0/schema.json")
    name: str
    position: VisualPosition
    visual: VisualVisual

class Visual:
    """Represents a Power BI visual with data and file management capabilities"""

    def __init__(self, file_path: Path, data: Optional[VisualData] = None):
        self.file_path = file_path
        if data:
            self.data = data
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path = self.file_path / "visual.json"
            self.write_back()
        else:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    self.data = VisualData.model_validate_json(f.read())
            else:
                raise FileNotFoundError(f"Visual file not found: {file_path}")

    def write_back(self):
        """Write the visual data back to its file"""
        if not self.file_path:
            raise ValueError("File path not set")
        
        try:
            # Ensure the parent directory exists
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.file_path, 'w') as f:
                f.write(self.data.model_dump_json(indent=2, by_alias=True, exclude_none=True))
            return True
        except Exception as e:
            print(f"Error writing visual {self.file_path}: {e}")
            return False
        
    def remove(self):
        """Remove the visual from the file system"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Visual file not found: {self.file_path}")
        
        try:
            # Remove the visual.json file
            self.file_path.unlink()
            
            # Remove the parent directory if it's empty
            parent_dir = self.file_path.parent
            if parent_dir.exists() and not any(parent_dir.iterdir()):
                parent_dir.rmdir()
                
            return True
        except Exception as e:
            print(f"Error removing visual {self.file_path}: {e}")
            return False
    
    @property
    def position(self) -> VisualPosition:
        """Get current visual position"""
        return self.data.position
    
    @position.setter
    def position(self, value: VisualPosition):
        """Set visual position"""
        self.data.position = value
        self.write_back()
    
    @property
    def visual_type(self) -> str:
        """Get visual type"""
        return self.data.visual.visualType
    
    @visual_type.setter
    def visual_type(self, value: VisualType):
        """Set visual type"""
        self.data.visual.visualType = value
        self.write_back()
    
    @property
    def x(self) -> float:
        """Get X coordinate"""
        return self.data.position.x
    
    @x.setter
    def x(self, value: float):
        """Set X coordinate"""
        self.data.position.x = value
        self.write_back()
    
    @property
    def y(self) -> float:
        """Get Y coordinate"""
        return self.data.position.y
    
    @y.setter
    def y(self, value: float):
        """Set Y coordinate"""
        self.data.position.y = value
        self.write_back()
    
    @property
    def width(self) -> float:
        """Get visual width"""
        return self.data.position.width
    
    @width.setter
    def width(self, value: float):
        """Set visual width"""
        self.data.position.width = value
        self.write_back()
    
    @property
    def height(self) -> float:
        """Get visual height"""
        return self.data.position.height
    
    @height.setter
    def height(self, value: float):
        """Set visual height"""
        self.data.position.height = value
        self.write_back()
    
    @property
    def z(self) -> float:
        """Get Z coordinate (layer)"""
        return self.data.position.z
    
    @z.setter
    def z(self, value: float):
        """Set Z coordinate (layer)"""
        self.data.position.z = value
        self.write_back()
    
    @property
    def properties(self) -> VisualVisual:
        """Get visual properties"""
        return self.data.visual
    
    @properties.setter
    def properties(self, value: VisualVisual):
        """Set visual properties"""
        self.data.visual = value
        self.write_back()

    @property
    def name(self) -> str:
        """Get the name of the visual"""
        return self.data.name
    
    @name.setter
    def name(self, value: str):
        """Set the name of the visual"""
        self.data.name = value
        self.write_back()
