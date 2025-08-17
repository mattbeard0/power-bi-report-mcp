from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class ExpressionSourceRef(BaseModel):
    Entity: str = Field(description="The entity reference")


class ColumnExpression(BaseModel):
    SourceRef: ExpressionSourceRef = Field(description="Source reference for the expression")


class FieldColumn(BaseModel):
    Expression: ColumnExpression = Field(description="Column expression")
    Property: str = Field(description="Column property")


class FieldAggregation(BaseModel):
    Expression: FieldColumn = Field(description="Aggregation expression")
    Function: int = Field(description="Aggregation function identifier")


class FieldDefinition(BaseModel):
    Column: Optional[FieldColumn] = Field(None, description="Column field definition")
    Aggregation: Optional[FieldAggregation] = Field(None, description="Aggregation field definition")


class Projection(BaseModel):
    field: FieldDefinition = Field(description="Field definition for the projection")
    queryRef: str = Field(description="Query reference")
    nativeQueryRef: str = Field(description="Native query reference")
    active: Optional[bool] = Field(None, description="Whether the projection is active")


class QueryStateCategory(BaseModel):
    projections: List[Projection] = Field(description="List of projections for the category")


class QueryStateY(BaseModel):
    projections: List[Projection] = Field(description="List of projections for the Y axis")


class QueryState(BaseModel):
    Category: QueryStateCategory = Field(description="Category query state")
    Y: QueryStateY = Field(description="Y axis query state")


class SortField(BaseModel):
    field: FieldDefinition = Field(description="Field to sort by")
    direction: Literal["Ascending", "Descending"] = Field(description="Sort direction")


class SortDefinition(BaseModel):
    sort: List[SortField] = Field(description="List of sort fields")
    isDefaultSort: bool = Field(description="Whether this is the default sort", default=True)


class Query(BaseModel):
    queryState: QueryState = Field(description="Query state containing category and Y axis definitions")
    sortDefinition: SortDefinition = Field(description="Sort definition for the query")
