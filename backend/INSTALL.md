# Installation Guide

## Option 1: Full Installation (CSV + SQL Server)

### Install pyodbc separately first:

```bash
# Try pre-built wheel first
pip install pyodbc

# If that fails, install Microsoft C++ Build Tools from:
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Then retry: pip install pyodbc
```

### Then install all requirements:

```bash
pip install -r requirements.txt
```

---

## Option 2: CSV-Only Installation (Recommended for Quick Start)

If you only need CSV file support and want to avoid pyodbc installation issues:

```bash
pip install -r requirements-minimal.txt
```

**Note:** SQL Server connectivity will not work, but all CSV functionality will be fully operational.

---

## Option 3: Step-by-Step Installation

Install packages one by one to identify which one is failing:

```bash
pip install fastapi
pip install uvicorn[standard]
pip install pandas
pip install numpy
pip install plotly
pip install python-multipart
pip install python-dotenv
pip install pydantic
pip install pydantic-settings
pip install aiofiles
pip install sqlalchemy

# Try pyodbc last (this is the one that usually fails)
pip install pyodbc
```

---

## Disabling SQL Server Support

If you can't install pyodbc and want to use CSV-only mode:

1. Install using `requirements-minimal.txt`
2. Comment out SQL Server imports in the code:

Edit `backend/app/main.py` and comment out the database router:

```python
# app.include_router(database.router, prefix=settings.API_V1_STR)
```

Edit `backend/app/core/data_loader.py` and comment out pyodbc import:

```python
# import pyodbc
```

---

## Troubleshooting

### Error: "Microsoft Visual C++ 14.0 or greater is required"

**Solution:** Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Select "Desktop development with C++" during installation
- Restart your terminal after installation

### Error: "Could not build wheels for pyodbc"

**Solution 1:** Use pre-compiled wheel
```bash
pip install --upgrade pip
pip install pyodbc --only-binary :all:
```

**Solution 2:** Use requirements-minimal.txt for CSV-only mode

### Error: Package version conflicts

**Solution:** Use a fresh virtual environment
```bash
# Delete old venv
rm -rf venv  # or: rmdir /s venv on Windows

# Create new venv
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install again
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

---

## Verifying Installation

After installation, verify everything works:

```bash
python -c "import fastapi, pandas, plotly; print('✓ Core packages installed')"

# Test pyodbc (if installed)
python -c "import pyodbc; print('✓ SQL Server support available')"
```

---

## Running the Application

Once installed:

```bash
# Development mode
python -m app.main

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000
