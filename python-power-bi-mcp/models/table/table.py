"""
Table-related models for Power BI dataset (TMDL parsing)
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ColumnData(BaseModel):
    name: str
    dataType: Optional[str] = None
    summarizeBy: Optional[str] = None
    formatString: Optional[str] = None
    sourceColumn: Optional[str] = None


class TableData(BaseModel):
    name: str
    isHidden: bool = False
    columns: List[ColumnData] = Field(default_factory=list)


class Table:
    """Represents a Dataset table parsed from a .tmdl file"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = self._parse_tmdl(file_path)

    @staticmethod
    def _parse_tmdl(file_path: Path) -> TableData:
        if not file_path.exists():
            raise FileNotFoundError(f"Table TMDL not found: {file_path}")
        text = file_path.read_text(encoding="utf-8")

        lines = [ln.rstrip() for ln in text.splitlines()]
        # First line: table <Name>
        if not lines:
            raise ValueError(f"Empty TMDL file: {file_path}")
        first = lines[0].strip()
        if not first.lower().startswith("table "):
            raise ValueError(f"Invalid TMDL header in {file_path}: {first}")
        name = first.split(" ", 1)[1].strip().strip("'")

        # Detect isHidden at top-level before the first 'column'/'partition'/'hierarchy'
        is_hidden = False
        for l in lines[1:]:
            s = l.strip()
            if s.startswith("column ") or s.startswith("partition ") or s.startswith("hierarchy "):
                break
            if s == "isHidden":
                is_hidden = True
                break

        columns: List[ColumnData] = []
        current_col: Optional[ColumnData] = None
        in_column_block = False

        def finalize_column():
            nonlocal current_col, in_column_block
            if current_col is not None:
                columns.append(current_col)
            current_col = None
            in_column_block = False

        for raw in lines[1:]:
            s = raw.strip()
            if not s:
                continue
            if s.startswith("column "):
                # starting a new column block
                if current_col is not None:
                    finalize_column()
                col_name = s.split(" ", 1)[1].strip().strip("'")
                current_col = ColumnData(name=col_name)
                in_column_block = True
                continue

            if s.startswith("variation "):
                # new nested block irrelevant for our current extraction; skip until next column
                continue

            if in_column_block and ":" in s and current_col is not None:
                # property line like 'dataType: string' or 'summarizeBy: sum'
                key, val = [p.strip() for p in s.split(":", 1)]
                if key == "dataType":
                    current_col.dataType = val
                elif key == "summarizeBy":
                    current_col.summarizeBy = val
                elif key == "formatString":
                    current_col.formatString = val
                elif key == "sourceColumn":
                    current_col.sourceColumn = val
                # ignore others
                continue

            # End of column block heuristics: encountering another top-level construct
            if in_column_block and (s.startswith("column ") or s.startswith("partition ") or s.startswith("table ")):
                finalize_column()

        # finalize last column if any
        if in_column_block:
            finalize_column()

        return TableData(name=name, isHidden=is_hidden, columns=columns)


class Relationship(BaseModel):
    id: str
    fromColumn: str
    toColumn: str
    # You can extend with cardinality, crossFilterDirection, etc. when needed


class Tables:
    """Container that loads all tables and relationships for a report's dataset"""

    def __init__(self, dataset_definition_path: Path):
        # dataset_definition_path -> <report>.Dataset/definition
        self.definition_path = dataset_definition_path
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []
        self._load()

    def _load(self):
        tables_dir = self.definition_path / "tables"
        if tables_dir.exists():
            for tmdl in tables_dir.glob("*.tmdl"):
                try:
                    table = Table(tmdl)
                    if not table.data.isHidden:  # skip hidden tables
                        self.tables[table.data.name] = table
                except Exception as e:
                    print(f"Error parsing table {tmdl}: {e}")
        else:
            print(f"DEBUG: tables directory not found: {tables_dir}")

        # Load relationships
        rel_file = self.definition_path / "relationships.tmdl"
        if rel_file.exists():
            self.relationships = self._parse_relationships(rel_file)
        else:
            print(f"DEBUG: relationships file not found: {rel_file}")

    @staticmethod
    def _parse_relationships(file_path: Path) -> List[Relationship]:
        text = file_path.read_text(encoding="utf-8")
        lines = [ln.rstrip() for ln in text.splitlines()]
        rels: List[Relationship] = []
        current_id: Optional[str] = None
        from_col: Optional[str] = None
        to_col: Optional[str] = None

        def finalize():
            nonlocal current_id, from_col, to_col
            if current_id and from_col and to_col:
                rels.append(Relationship(id=current_id, fromColumn=from_col, toColumn=to_col))
            current_id = None
            from_col = None
            to_col = None

        for raw in lines:
            s = raw.strip()
            if not s:
                continue
            if s.startswith("relationship "):
                # start new relationship block
                if current_id is not None:
                    finalize()
                current_id = s.split(" ", 1)[1].strip()
                continue
            if s.startswith("fromColumn:"):
                from_col = s.split(":", 1)[1].strip()
                continue
            if s.startswith("toColumn:"):
                to_col = s.split(":", 1)[1].strip()
                continue
        # finalize last
        if current_id is not None:
            finalize()
        return rels

    def get_table(self, name: str) -> Optional[Table]:
        return self.tables.get(name)

    def list_tables(self) -> List[str]:
        return list(self.tables.keys())
