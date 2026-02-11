"""
FastAPI application entry point for DataViewer.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.data_loader import HAS_SQL_SERVER_SUPPORT
from app.api import routes, upload, database


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Dynamic data visualization and EDA platform",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(routes.router, prefix=settings.API_V1_STR)
app.include_router(upload.router, prefix=settings.API_V1_STR)

# Include database router only if SQL Server support is available
if HAS_SQL_SERVER_SUPPORT:
    app.include_router(database.router, prefix=settings.API_V1_STR)

# Mount static files for uploaded data
app.mount("/data", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="data")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DataViewer API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "sql_server_support": HAS_SQL_SERVER_SUPPORT
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
