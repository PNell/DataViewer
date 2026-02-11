"""
Pydantic models for request/response schemas.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any, Literal
from enum import Enum


class DataSourceType(str, Enum):
    """Data source types"""
    CSV = "csv"
    SQL_SERVER = "sql_server"


class ColumnInfo(BaseModel):
    """Column information"""
    name: str
    dtype: str
    nullable: bool = True
    unique_count: Optional[int] = None
    sample_values: Optional[list[Any]] = None


class DataSourceConfig(BaseModel):
    """Abstract data source configuration"""
    source_id: str
    source_type: DataSourceType
    name: str
    columns: list[ColumnInfo] = []


class CSVUploadResponse(BaseModel):
    """Response for CSV upload"""
    source_id: str
    filename: str
    rows: int
    columns: list[ColumnInfo]
    preview: list[dict[str, Any]]


class SQLConnectionConfig(BaseModel):
    """SQL Server connection configuration"""
    server: str
    database: str
    username: Optional[str] = None
    password: Optional[str] = None
    use_windows_auth: bool = False
    port: int = 1433


class SQLConnectionResponse(BaseModel):
    """Response for SQL Server connection"""
    source_id: str
    server: str
    database: str
    tables: list[str]


class TableSchema(BaseModel):
    """Database table schema"""
    table_name: str
    columns: list[ColumnInfo]
    row_count: Optional[int] = None


class FilterCondition(BaseModel):
    """Single filter condition"""
    column: str
    operator: Literal["eq", "ne", "gt", "lt", "gte", "lte", "contains", "in", "between"]
    value: Any
    value2: Optional[Any] = None  # For 'between' operator


class DataQueryRequest(BaseModel):
    """Request for querying data"""
    source_id: str
    filters: list[FilterCondition] = []
    limit: int = Field(default=100, le=10000)
    offset: int = Field(default=0, ge=0)
    columns: Optional[list[str]] = None


class DataQueryResponse(BaseModel):
    """Response for data query"""
    data: list[dict[str, Any]]
    total_rows: int
    returned_rows: int


class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    VIOLIN = "violin"
    HEATMAP = "heatmap"
    DISTRIBUTION = "distribution"
    TIME_SERIES = "time_series"
    CANDLESTICK = "candlestick"
    RANGE_PLOT = "range_plot"


class ChartRequest(BaseModel):
    """Request for generating a chart"""
    source_id: str
    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    color_column: Optional[str] = None
    size_column: Optional[str] = None
    group_column: Optional[str] = None
    filters: list[FilterCondition] = []
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    options: dict[str, Any] = {}

    @field_validator('chart_type')
    @classmethod
    def validate_chart_type(cls, v):
        """Validate chart type"""
        if v not in ChartType.__members__.values():
            raise ValueError(f"Invalid chart type: {v}")
        return v


class ChartResponse(BaseModel):
    """Response for chart generation"""
    chart_id: str
    chart_type: str
    figure: dict[str, Any]  # Plotly figure JSON


class SummaryStats(BaseModel):
    """Summary statistics for a column"""
    column: str
    count: int
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    q25: Optional[float] = None
    median: Optional[float] = None
    q75: Optional[float] = None
    unique_values: Optional[int] = None
    null_count: int = 0


class DataSummaryResponse(BaseModel):
    """Response for data summary"""
    source_id: str
    row_count: int
    column_count: int
    stats: list[SummaryStats]


class OutlierDetectionRequest(BaseModel):
    """Request for outlier detection"""
    source_id: str
    column: str
    method: Literal["iqr", "zscore"] = "iqr"
    threshold: float = 1.5


class OutlierDetectionResponse(BaseModel):
    """Response for outlier detection"""
    column: str
    method: str
    outlier_count: int
    outlier_indices: list[int]
    outlier_values: list[Any]


class ChartSuggestion(BaseModel):
    """Chart suggestion"""
    chart_type: ChartType
    x_column: Optional[str] = None
    y_column: Optional[str] = None
    reason: str
    priority: int  # 1 = highest


class ChartSuggestionsResponse(BaseModel):
    """Response for chart suggestions"""
    source_id: str
    suggestions: list[ChartSuggestion]
