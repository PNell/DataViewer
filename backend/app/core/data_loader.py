"""
Data abstraction layer for handling multiple data sources (CSV, SQL Server).
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
import pandas as pd
import numpy as np
from pathlib import Path
from app.models.schemas import ColumnInfo, FilterCondition
from app.core.config import settings

# Optional SQL Server support
try:
    import pyodbc
    from sqlalchemy import create_engine, text
    HAS_SQL_SERVER_SUPPORT = True
except ImportError:
    HAS_SQL_SERVER_SUPPORT = False
    pyodbc = None
    create_engine = None
    text = None


class DataSource(ABC):
    """Abstract base class for data sources"""

    def __init__(self, source_id: str, name: str):
        self.source_id = source_id
        self.name = name
        self._df: Optional[pd.DataFrame] = None

    @abstractmethod
    def load_data(self) -> pd.DataFrame:
        """Load data from the source"""
        pass

    def get_data(self, filters: Optional[list[FilterCondition]] = None,
                 limit: Optional[int] = None, offset: int = 0,
                 columns: Optional[list[str]] = None) -> pd.DataFrame:
        """
        Retrieve data with optional filtering and pagination.

        Args:
            filters: List of filter conditions
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            columns: Specific columns to return

        Returns:
            Filtered DataFrame
        """
        if self._df is None:
            self._df = self.load_data()

        df = self._df.copy()

        # Apply filters
        if filters:
            df = self._apply_filters(df, filters)

        # Select specific columns
        if columns:
            df = df[columns]

        # Apply pagination
        if offset > 0:
            df = df.iloc[offset:]
        if limit is not None:
            df = df.iloc[:limit]

        return df

    def _apply_filters(self, df: pd.DataFrame, filters: list[FilterCondition]) -> pd.DataFrame:
        """Apply filter conditions to DataFrame"""
        mask = pd.Series([True] * len(df), index=df.index)

        for filter_cond in filters:
            column = filter_cond.column
            operator = filter_cond.operator
            value = filter_cond.value

            if column not in df.columns:
                continue

            if operator == "eq":
                mask &= df[column] == value
            elif operator == "ne":
                mask &= df[column] != value
            elif operator == "gt":
                mask &= df[column] > value
            elif operator == "lt":
                mask &= df[column] < value
            elif operator == "gte":
                mask &= df[column] >= value
            elif operator == "lte":
                mask &= df[column] <= value
            elif operator == "contains":
                mask &= df[column].astype(str).str.contains(str(value), case=False, na=False)
            elif operator == "in":
                mask &= df[column].isin(value if isinstance(value, list) else [value])
            elif operator == "between" and filter_cond.value2 is not None:
                mask &= (df[column] >= value) & (df[column] <= filter_cond.value2)

        return df[mask]

    def get_columns(self) -> list[ColumnInfo]:
        """Return column information"""
        if self._df is None:
            self._df = self.load_data()

        columns = []
        for col in self._df.columns:
            dtype_str = str(self._df[col].dtype)
            nullable = bool(self._df[col].isna().any())
            unique_count = int(self._df[col].nunique())

            # Get sample values (up to 5 unique values)
            sample_values = self._df[col].dropna().unique()[:5].tolist()

            columns.append(ColumnInfo(
                name=col,
                dtype=dtype_str,
                nullable=nullable,
                unique_count=unique_count,
                sample_values=sample_values
            ))

        return columns

    def get_summary_stats(self) -> pd.DataFrame:
        """Get summary statistics for numeric columns"""
        if self._df is None:
            self._df = self.load_data()

        return self._df.describe(include='all')

    def get_unique_values(self, column: str, limit: int = 100) -> list[Any]:
        """Get unique values for a column"""
        if self._df is None:
            self._df = self.load_data()

        if column not in self._df.columns:
            raise ValueError(f"Column '{column}' not found")

        unique_vals = self._df[column].dropna().unique()[:limit]
        return unique_vals.tolist()

    def get_data_types(self) -> dict[str, str]:
        """Infer column data types (numeric, categorical, datetime)"""
        if self._df is None:
            self._df = self.load_data()

        types = {}
        for col in self._df.columns:
            dtype = self._df[col].dtype

            if pd.api.types.is_numeric_dtype(dtype):
                types[col] = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                types[col] = "datetime"
            else:
                # Check if it could be converted to datetime
                try:
                    pd.to_datetime(self._df[col].dropna().head(100))
                    types[col] = "datetime_candidate"
                except:
                    types[col] = "categorical"

        return types

    def get_row_count(self) -> int:
        """Get total number of rows"""
        if self._df is None:
            self._df = self.load_data()
        return len(self._df)


class CSVDataSource(DataSource):
    """CSV file data source"""

    def __init__(self, source_id: str, file_path: Path):
        super().__init__(source_id, file_path.name)
        self.file_path = file_path

    def load_data(self) -> pd.DataFrame:
        """Load data from CSV file"""
        try:
            # Read CSV file
            df = pd.read_csv(self.file_path)

            # Auto-detect and convert datetime columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    try:
                        # Try to convert to datetime
                        df[col] = pd.to_datetime(df[col])
                    except:
                        # If conversion fails, keep as string
                        pass

            return df
        except Exception as e:
            raise ValueError(f"Error loading CSV file: {str(e)}")


# SQL Server DataSource - only available if pyodbc is installed
if HAS_SQL_SERVER_SUPPORT:
    class SQLServerDataSource(DataSource):
        """SQL Server database data source"""

        def __init__(self, source_id: str, connection_config: dict, table_name: str):
            super().__init__(source_id, f"{connection_config['database']}.{table_name}")
            self.connection_config = connection_config
            self.table_name = table_name
            self._engine = None

        def _get_connection_string(self) -> str:
            """Build SQL Server connection string"""
            config = self.connection_config

            if config.get('use_windows_auth', False):
                # Windows Authentication
                conn_str = (
                    f"mssql+pyodbc://@{config['server']}/{config['database']}"
                    f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
                    f"&trusted_connection=yes"
                )
            else:
                # SQL Server Authentication
                conn_str = (
                    f"mssql+pyodbc://{config['username']}:{config['password']}"
                    f"@{config['server']}/{config['database']}"
                    f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
                )

            return conn_str

        def _get_engine(self):
            """Get or create SQLAlchemy engine"""
            if self._engine is None:
                conn_str = self._get_connection_string()
                self._engine = create_engine(
                    conn_str,
                    connect_args={'timeout': settings.SQL_CONNECTION_TIMEOUT}
                )
            return self._engine

        def load_data(self) -> pd.DataFrame:
            """Load data from SQL Server table"""
            try:
                engine = self._get_engine()
                query = f"SELECT * FROM {self.table_name}"

                with engine.connect() as conn:
                    df = pd.read_sql(text(query), conn)

                return df
            except Exception as e:
                raise ValueError(f"Error loading data from SQL Server: {str(e)}")

        def get_data(self, filters: Optional[list[FilterCondition]] = None,
                     limit: Optional[int] = None, offset: int = 0,
                     columns: Optional[list[str]] = None) -> pd.DataFrame:
            """
            Override to support server-side filtering for better performance
            """
            try:
                engine = self._get_engine()

                # Build query
                select_cols = ", ".join(columns) if columns else "*"
                query = f"SELECT {select_cols} FROM {self.table_name}"

                # Add WHERE clause for filters
                if filters:
                    where_clauses = []
                    for f in filters:
                        if f.operator == "eq":
                            where_clauses.append(f"{f.column} = '{f.value}'")
                        elif f.operator == "gt":
                            where_clauses.append(f"{f.column} > {f.value}")
                        elif f.operator == "lt":
                            where_clauses.append(f"{f.column} < {f.value}")
                        elif f.operator == "contains":
                            where_clauses.append(f"{f.column} LIKE '%{f.value}%'")
                        # Add more operators as needed

                    if where_clauses:
                        query += " WHERE " + " AND ".join(where_clauses)

                # Add pagination
                if limit is not None:
                    query += f" ORDER BY (SELECT NULL) OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"

                with engine.connect() as conn:
                    df = pd.read_sql(text(query), conn)

                return df
            except Exception as e:
                # Fallback to parent implementation
                return super().get_data(filters, limit, offset, columns)
else:
    # Placeholder when SQL Server support is not available
    SQLServerDataSource = None


# Data source registry
_data_sources: dict[str, DataSource] = {}


def register_data_source(source: DataSource) -> None:
    """Register a data source"""
    _data_sources[source.source_id] = source


def get_data_source(source_id: str) -> Optional[DataSource]:
    """Get a registered data source"""
    return _data_sources.get(source_id)


def remove_data_source(source_id: str) -> None:
    """Remove a data source from registry"""
    if source_id in _data_sources:
        del _data_sources[source_id]


def list_data_sources() -> list[DataSource]:
    """List all registered data sources"""
    return list(_data_sources.values())
