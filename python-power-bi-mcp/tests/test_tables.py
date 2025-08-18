"""
Unit tests for Tables and TMDL parsing
"""

import pytest
from pathlib import Path
from models.table.table import Table, Tables


@pytest.mark.unit
def test_parse_non_hidden_table(tmp_path: Path):
    """Parse a simple non-hidden table and verify columns"""
    definition = tmp_path / "definition"
    tables_dir = definition / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    tmdl = (
        "table Dummy\n"
        "\n"
        "    column A\n"
        "        dataType: string\n"
        "        summarizeBy: none\n"
        "\n"
        "    column Amount\n"
        "        dataType: double\n"
        "        summarizeBy: sum\n"
    )
    (tables_dir / "Dummy.tmdl").write_text(tmdl, encoding="utf-8")

    # Direct Table parse
    table = Table(tables_dir / "Dummy.tmdl")
    assert table.data.name == "Dummy"
    assert table.data.isHidden is False
    assert len(table.data.columns) == 2
    col_a = table.data.columns[0]
    assert col_a.name == "A"
    assert col_a.dataType == "string"
    assert col_a.summarizeBy == "none"

    # Container load
    container = Tables(definition)
    assert "Dummy" in container.tables
    assert len(container.list_tables()) == 1


@pytest.mark.unit
def test_skip_hidden_table(tmp_path: Path):
    """Hidden tables should be skipped by the Tables container"""
    definition = tmp_path / "definition"
    tables_dir = definition / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    hidden_tmdl = (
        "table HiddenOne\n"
        "    isHidden\n"
        "\n"
        "    column X\n"
        "        dataType: int64\n"
        "        summarizeBy: sum\n"
    )
    (tables_dir / "HiddenOne.tmdl").write_text(hidden_tmdl, encoding="utf-8")

    container = Tables(definition)
    assert "HiddenOne" not in container.tables
    assert len(container.list_tables()) == 0


@pytest.mark.unit
def test_parse_relationships(tmp_path: Path):
    """Parse relationships.tmdl and verify fields"""
    definition = tmp_path / "definition"
    tables_dir = definition / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # minimal table to accompany relationships (not used directly here)
    (tables_dir / "Dummy.tmdl").write_text("table Dummy\n", encoding="utf-8")

    rels_text = (
        "relationship 11111111-1111-1111-1111-111111111111\n"
        "    fromColumn: Dummy.OrderDate\n"
        "    toColumn: LocalDate.Date\n"
    )
    (definition / "relationships.tmdl").write_text(rels_text, encoding="utf-8")

    container = Tables(definition)
    assert len(container.relationships) == 1
    r = container.relationships[0]
    assert r.id == "11111111-1111-1111-1111-111111111111"
    assert r.fromColumn == "Dummy.OrderDate"
    assert r.toColumn == "LocalDate.Date"
