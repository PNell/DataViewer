"""
Main API routes for data operations and chart generation.
"""
from fastapi import APIRouter, HTTPException
import uuid
from app.core.data_loader import get_data_source
from app.core.chart_generator import ChartGenerator
from app.core.data_analyzer import DataAnalyzer
from app.models.schemas import (
    DataQueryRequest,
    DataQueryResponse,
    ChartRequest,
    ChartResponse,
    DataSummaryResponse,
    OutlierDetectionRequest,
    OutlierDetectionResponse,
    ChartSuggestionsResponse
)


router = APIRouter(tags=["data"])


@router.post("/data/query", response_model=DataQueryResponse)
async def query_data(request: DataQueryRequest):
    """
    Query data from a data source with optional filtering and pagination.

    Args:
        request: Data query request

    Returns:
        DataQueryResponse with filtered data
    """
    data_source = get_data_source(request.source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        # Get filtered data
        df = data_source.get_data(
            filters=request.filters,
            limit=request.limit,
            offset=request.offset,
            columns=request.columns
        )

        # Convert to records
        data = df.to_dict('records')

        # Get total row count (without filters for pagination)
        total_rows = data_source.get_row_count()

        return DataQueryResponse(
            data=data,
            total_rows=total_rows,
            returned_rows=len(data)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying data: {str(e)}")


@router.get("/data/columns/{source_id}")
async def get_columns(source_id: str):
    """
    Get column information for a data source.

    Args:
        source_id: Data source ID

    Returns:
        List of column information
    """
    data_source = get_data_source(source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        columns = data_source.get_columns()
        data_types = data_source.get_data_types()

        return {
            "columns": columns,
            "data_types": data_types
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting columns: {str(e)}")


@router.get("/data/summary/{source_id}", response_model=DataSummaryResponse)
async def get_data_summary(source_id: str):
    """
    Get summary statistics for all columns in a data source.

    Args:
        source_id: Data source ID

    Returns:
        DataSummaryResponse with statistics
    """
    data_source = get_data_source(source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        df = data_source.get_data()

        stats = DataAnalyzer.get_summary_stats_list(df)

        return DataSummaryResponse(
            source_id=source_id,
            row_count=len(df),
            column_count=len(df.columns),
            stats=stats
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting summary: {str(e)}")


@router.post("/data/filter-options")
async def get_filter_options(source_id: str, column: str, limit: int = 100):
    """
    Get unique values for a column (for filter dropdowns).

    Args:
        source_id: Data source ID
        column: Column name
        limit: Maximum number of values to return

    Returns:
        List of unique values
    """
    data_source = get_data_source(source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        values = data_source.get_unique_values(column, limit)
        return {"column": column, "values": values}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting filter options: {str(e)}")


@router.post("/charts/generate", response_model=ChartResponse)
async def generate_chart(request: ChartRequest):
    """
    Generate a chart from data source.

    Args:
        request: Chart generation request

    Returns:
        ChartResponse with Plotly figure JSON
    """
    data_source = get_data_source(request.source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        # Get filtered data
        df = data_source.get_data(filters=request.filters)

        if df.empty:
            raise HTTPException(status_code=400, detail="No data available after filtering")

        # Generate chart
        figure = ChartGenerator.generate_chart(
            chart_type=request.chart_type,
            data=df,
            x=request.x_column,
            y=request.y_column,
            color=request.color_column,
            size=request.size_column,
            title=request.title,
            x_label=request.x_label,
            y_label=request.y_label,
            **request.options
        )

        chart_id = str(uuid.uuid4())

        return ChartResponse(
            chart_id=chart_id,
            chart_type=request.chart_type.value,
            figure=figure
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


@router.post("/charts/batch")
async def generate_charts_batch(requests: list[ChartRequest]):
    """
    Generate multiple charts in a single request.

    Args:
        requests: List of chart requests

    Returns:
        List of chart responses
    """
    responses = []

    for request in requests:
        try:
            response = await generate_chart(request)
            responses.append(response)
        except HTTPException as e:
            responses.append({
                "error": e.detail,
                "chart_type": request.chart_type.value
            })

    return responses


@router.get("/analysis/suggestions/{source_id}", response_model=ChartSuggestionsResponse)
async def get_chart_suggestions(source_id: str, max_suggestions: int = 10):
    """
    Get chart suggestions based on data characteristics.

    Args:
        source_id: Data source ID
        max_suggestions: Maximum number of suggestions

    Returns:
        ChartSuggestionsResponse with suggestions
    """
    data_source = get_data_source(source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        df = data_source.get_data()

        suggestions = DataAnalyzer.suggest_chart_types(df, max_suggestions)

        return ChartSuggestionsResponse(
            source_id=source_id,
            suggestions=suggestions
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")


@router.post("/analysis/outliers", response_model=OutlierDetectionResponse)
async def detect_outliers(request: OutlierDetectionRequest):
    """
    Detect outliers in a column.

    Args:
        request: Outlier detection request

    Returns:
        OutlierDetectionResponse with outlier information
    """
    data_source = get_data_source(request.source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        df = data_source.get_data()

        outlier_indices, outlier_values = DataAnalyzer.detect_outliers(
            df,
            request.column,
            request.method,
            request.threshold
        )

        return OutlierDetectionResponse(
            column=request.column,
            method=request.method,
            outlier_count=len(outlier_indices),
            outlier_indices=outlier_indices,
            outlier_values=outlier_values
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting outliers: {str(e)}")


@router.get("/analysis/correlation/{source_id}")
async def get_correlation(source_id: str):
    """
    Get correlation matrix for numeric columns.

    Args:
        source_id: Data source ID

    Returns:
        Correlation matrix as nested dictionary
    """
    data_source = get_data_source(source_id)
    if not data_source:
        raise HTTPException(status_code=404, detail="Data source not found")

    try:
        df = data_source.get_data()

        corr_matrix = DataAnalyzer.get_correlation_matrix(df)

        return {
            "correlation_matrix": corr_matrix.to_dict(),
            "columns": corr_matrix.columns.tolist()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating correlation: {str(e)}")
