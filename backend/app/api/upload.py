"""
CSV file upload endpoints.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import uuid
import aiofiles
from app.core.config import settings
from app.core.data_loader import CSVDataSource, register_data_source
from app.models.schemas import CSVUploadResponse


router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=CSVUploadResponse)
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file and register it as a data source.

    Args:
        file: CSV file to upload

    Returns:
        CSVUploadResponse with source info and preview
    """
    # Validate file extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only CSV files are allowed."
        )

    # Generate unique source ID and filename
    source_id = str(uuid.uuid4())
    safe_filename = f"{source_id}_{file.filename}"
    file_path = settings.UPLOAD_DIR / safe_filename

    try:
        # Save uploaded file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                )
            await f.write(content)

        # Create data source
        data_source = CSVDataSource(source_id, file_path)
        register_data_source(data_source)

        # Load data to get info
        df = data_source.load_data()

        # Get column information
        columns = data_source.get_columns()

        # Get preview (first 100 rows)
        preview_df = df.head(100)
        preview = preview_df.to_dict('records')

        return CSVUploadResponse(
            source_id=source_id,
            filename=file.filename,
            rows=len(df),
            columns=columns,
            preview=preview
        )

    except Exception as e:
        # Clean up file if something went wrong
        import traceback
        error_traceback = traceback.format_exc()
        print(f"ERROR uploading file: {error_traceback}")
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
