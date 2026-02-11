"""
SQL Server database connection endpoints.
"""
from fastapi import APIRouter, HTTPException
import uuid
from app.core.config import settings
from app.core.data_loader import HAS_SQL_SERVER_SUPPORT, register_data_source
from app.models.schemas import (
    SQLConnectionConfig,
    SQLConnectionResponse,
    TableSchema,
    ColumnInfo
)

# Optional SQL Server imports
if HAS_SQL_SERVER_SUPPORT:
    import pyodbc
    from sqlalchemy import create_engine, inspect, text
    from app.core.data_loader import SQLServerDataSource
else:
    pyodbc = None
    create_engine = None
    inspect = None
    text = None
    SQLServerDataSource = None


router = APIRouter(prefix="/database", tags=["database"])


@router.post("/connect", response_model=SQLConnectionResponse)
async def connect_to_sql_server(config: SQLConnectionConfig):
    """
    Connect to SQL Server database and list available tables.

    Args:
        config: SQL Server connection configuration

    Returns:
        SQLConnectionResponse with connection info and table list
    """
    if not HAS_SQL_SERVER_SUPPORT:
        raise HTTPException(
            status_code=501,
            detail="SQL Server support not available. Install pyodbc and sqlalchemy: pip install pyodbc sqlalchemy"
        )

    try:
        # Build connection string for testing
        if config.use_windows_auth:
            conn_str = (
                f"DRIVER={{{settings.SQL_SERVER_DRIVER}}};"
                f"SERVER={config.server},{config.port};"
                f"DATABASE={config.database};"
                f"Trusted_Connection=yes;"
            )
            sqlalchemy_conn_str = (
                f"mssql+pyodbc://@{config.server}/{config.database}"
                f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
                f"&trusted_connection=yes"
            )
        else:
            if not config.username or not config.password:
                raise HTTPException(
                    status_code=400,
                    detail="Username and password required for SQL Server authentication"
                )
            conn_str = (
                f"DRIVER={{{settings.SQL_SERVER_DRIVER}}};"
                f"SERVER={config.server},{config.port};"
                f"DATABASE={config.database};"
                f"UID={config.username};"
                f"PWD={config.password};"
            )
            sqlalchemy_conn_str = (
                f"mssql+pyodbc://{config.username}:{config.password}"
                f"@{config.server}/{config.database}"
                f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
            )

        # Test connection and get tables
        engine = create_engine(
            sqlalchemy_conn_str,
            connect_args={'timeout': settings.SQL_CONNECTION_TIMEOUT}
        )

        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()

        source_id = str(uuid.uuid4())

        return SQLConnectionResponse(
            source_id=source_id,
            server=config.server,
            database=config.database,
            tables=tables
        )

    except pyodbc.Error as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error connecting to database: {str(e)}"
        )


@router.post("/tables/{table_name}", response_model=TableSchema)
async def get_table_schema(table_name: str, config: SQLConnectionConfig):
    """
    Get schema information for a specific table and register as data source.

    Args:
        table_name: Name of the table
        config: SQL Server connection configuration

    Returns:
        TableSchema with column information
    """
    if not HAS_SQL_SERVER_SUPPORT:
        raise HTTPException(
            status_code=501,
            detail="SQL Server support not available. Install pyodbc and sqlalchemy: pip install pyodbc sqlalchemy"
        )

    try:
        # Create connection
        if config.use_windows_auth:
            sqlalchemy_conn_str = (
                f"mssql+pyodbc://@{config.server}/{config.database}"
                f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
                f"&trusted_connection=yes"
            )
        else:
            sqlalchemy_conn_str = (
                f"mssql+pyodbc://{config.username}:{config.password}"
                f"@{config.server}/{config.database}"
                f"?driver={settings.SQL_SERVER_DRIVER.replace(' ', '+')}"
            )

        engine = create_engine(
            sqlalchemy_conn_str,
            connect_args={'timeout': settings.SQL_CONNECTION_TIMEOUT}
        )

        # Get table schema
        inspector = inspect(engine)
        columns_info = inspector.get_columns(table_name)

        # Get row count
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) as cnt FROM {table_name}"))
            row_count = result.scalar()

        # Create data source
        source_id = str(uuid.uuid4())
        connection_dict = {
            'server': config.server,
            'database': config.database,
            'username': config.username,
            'password': config.password,
            'use_windows_auth': config.use_windows_auth,
            'port': config.port
        }

        data_source = SQLServerDataSource(source_id, connection_dict, table_name)
        register_data_source(data_source)

        # Convert column info to ColumnInfo schema
        columns = []
        for col in columns_info:
            columns.append(ColumnInfo(
                name=col['name'],
                dtype=str(col['type']),
                nullable=col['nullable']
            ))

        return TableSchema(
            table_name=table_name,
            columns=columns,
            row_count=row_count
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting table schema: {str(e)}"
        )
