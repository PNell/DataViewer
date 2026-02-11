# DataViewer

A dynamic data visualization and exploratory data analysis (EDA) platform built with FastAPI and Vue.js. Upload CSV files or connect to SQL Server databases to generate interactive charts using Plotly.

## Features

- **Multiple Data Sources**
  - CSV file upload with drag-and-drop
  - SQL Server database connection (Windows Auth & SQL Auth)

- **Comprehensive Chart Types**
  - Basic: Line, Bar, Scatter, Histogram
  - Statistical: Box Plot, Violin Plot, Heatmap, Distribution
  - Time-Series: Time Series, Candlestick, Range Plot

- **Interactive Analysis**
  - Real-time data filtering
  - Outlier detection (IQR & Z-score methods)
  - Correlation analysis
  - Automatic chart suggestions based on data characteristics

- **User-Friendly Interface**
  - Drag-and-drop file upload
  - Interactive chart configuration
  - Multiple charts on a single dashboard
  - Data preview with statistics

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pandas** - Data manipulation and analysis
- **Plotly** - Interactive chart generation
- **SQLAlchemy & pyodbc** - SQL Server connectivity
- **Pydantic** - Data validation

### Frontend
- **Vue.js 3** - Progressive JavaScript framework
- **Pinia** - State management
- **Plotly.js** - Interactive chart rendering
- **Vite** - Build tool and dev server

## Project Structure

```
DataViewer/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Core logic (data loading, charts, analysis)
│   │   ├── models/        # Pydantic models
│   │   └── main.py        # FastAPI application
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── services/      # API client
│   │   ├── stores/        # Pinia stores
│   │   └── main.js
│   └── package.json
└── data/                  # Uploaded CSV files
```

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- SQL Server (optional, for database connectivity)
- ODBC Driver 17 for SQL Server (for SQL Server support)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd DataViewer/backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file (optional):
   ```
   # Copy from .env.example and customize if needed
   ```

5. Run the backend server:
   ```bash
   python -m app.main
   ```

   The API will be available at `http://localhost:8000`
   API documentation: `http://localhost:8000/docs`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd DataViewer/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## Usage

### 1. Upload CSV Data

1. Open the application in your browser
2. Drag and drop a CSV file into the upload area, or click "Choose File"
3. The data will be loaded and preview will be displayed

### 2. Connect to SQL Server

1. Click on "Connect to SQL Server"
2. Enter connection details:
   - Server address
   - Database name
   - Authentication (Windows or SQL Server)
3. Select a table from the dropdown
4. Data will be loaded automatically

### 3. Create Charts

1. Select chart type from the dropdown
2. Choose X and Y axis columns
3. (Optional) Select color grouping column
4. (Optional) Enter a custom chart title
5. Click "Generate Chart"

### 4. Chart Suggestions

The system automatically analyzes your data and suggests appropriate chart types:
- Time series analysis for datetime columns
- Correlation heatmaps for numeric data
- Distribution plots for continuous variables
- Box plots for categorical comparisons

### 5. Manage Charts

- View multiple charts simultaneously on the dashboard
- Remove individual charts with the "Remove" button
- Clear all charts with "Clear All Charts"

## API Endpoints

### Data Upload
- `POST /api/upload` - Upload CSV file

### Database
- `POST /api/database/connect` - Connect to SQL Server
- `POST /api/database/tables/{table_name}` - Get table schema

### Data Operations
- `POST /api/data/query` - Query data with filters
- `GET /api/data/columns/{source_id}` - Get column information
- `GET /api/data/summary/{source_id}` - Get summary statistics

### Chart Generation
- `POST /api/charts/generate` - Generate a single chart
- `POST /api/charts/batch` - Generate multiple charts

### Analysis
- `GET /api/analysis/suggestions/{source_id}` - Get chart suggestions
- `POST /api/analysis/outliers` - Detect outliers
- `GET /api/analysis/correlation/{source_id}` - Get correlation matrix

## Configuration

### Backend Configuration

Edit `backend/app/core/config.py` to customize:
- Maximum upload file size
- Allowed file extensions
- SQL Server connection timeout
- Data pagination settings

### Frontend Configuration

Edit `frontend/vite.config.js` to customize:
- Development server port
- API proxy settings
- Build options

## Development

### Running Tests

```bash
# Backend tests (to be added)
cd backend
pytest

# Frontend tests (to be added)
cd frontend
npm test
```

### Building for Production

```bash
# Backend
cd backend
# Deploy with uvicorn or gunicorn

# Frontend
cd frontend
npm run build
# Deploy the dist/ directory
```

## Troubleshooting

### SQL Server Connection Issues

1. Ensure ODBC Driver 17 for SQL Server is installed
2. Check firewall settings
3. Verify SQL Server allows remote connections
4. Test connection string manually

### CSV Upload Errors

1. Verify file is valid CSV format
2. Check file size (default limit: 100MB)
3. Ensure proper column headers

### Chart Generation Issues

1. Verify data types match chart requirements
2. Check for missing or null values
3. Ensure numeric columns for statistical charts

## Future Enhancements

- [ ] Support for additional databases (PostgreSQL, MySQL)
- [ ] Export charts as PNG/SVG/PDF
- [ ] Save and load dashboard configurations
- [ ] Advanced data transformations
- [ ] Collaborative features
- [ ] Real-time data streaming

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## Support

For questions or issues, please open an issue on the GitHub repository.
