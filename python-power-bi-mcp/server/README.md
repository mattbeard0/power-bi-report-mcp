# Power BI MCP Server

A FastAPI server that provides endpoints for Power BI report operations, designed to be compatible with Model Context Protocol (MCP) clients.

## Features

- **Create Reports**: Generate new Power BI reports from baseline templates
- **Manage Pages**: Get page information and details
- **Add Charts**: Add line charts and bar charts to pages with custom positioning
- **Resize Charts**: Modify chart dimensions dynamically
- **Error Handling**: Comprehensive error messages with helpful suggestions

## Quick Start

### 1. Install Dependencies

```bash
pip install -r ../requirements.txt
```

### 2. Start the Server

**Windows:**

```bash
start_server.bat
```

**Manual:**

```bash
python main.py
```

The server will start at `http://localhost:8000`

### 3. Access API Documentation

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Core Operations

| Method | Endpoint        | Description             |
| ------ | --------------- | ----------------------- |
| `GET`  | `/`             | Server status           |
| `GET`  | `/health`       | Health check            |
| `GET`  | `/list_reports` | List all active reports |

### Report Management

| Method   | Endpoint           | Description               |
| -------- | ------------------ | ------------------------- |
| `POST`   | `/make_new_report` | Create a new report       |
| `DELETE` | `/delete_report`   | Remove report from memory |

### Page Operations

| Method | Endpoint            | Description                   |
| ------ | ------------------- | ----------------------------- |
| `GET`  | `/get_all_pages`    | Get all pages in a report     |
| `GET`  | `/get_page_details` | Get detailed page information |

### Chart Operations

| Method | Endpoint             | Description             |
| ------ | -------------------- | ----------------------- |
| `POST` | `/add_chart`         | Add a chart to a page   |
| `POST` | `/change_chart_size` | Modify chart dimensions |

## Usage Examples

### Create a New Report

```bash
curl -X POST "http://localhost:8000/make_new_report" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_report"}'
```

### Add a Bar Chart

```bash
curl -X POST "http://localhost:8000/add_chart?report_name=my_report" \
  -H "Content-Type: application/json" \
  -d '{
    "page_name": "ReportSection",
    "chart_type": "barChart",
    "x": 100,
    "y": 100,
    "width": 400,
    "height": 300
  }'
```

### Get Page Details

```bash
curl "http://localhost:8000/get_page_details?report_name=my_report&page_name=ReportSection"
```

## Testing

### Run Manual Tests

```bash
python test_server.py
```

### Run Pytest Tests

```bash
cd ..
pytest tests/test_server.py -v
```

## Error Handling

The server provides detailed error messages that include:

- **Available Options**: Lists valid reports, pages, or charts when operations fail
- **Clear Descriptions**: Explains what went wrong and how to fix it
- **HTTP Status Codes**: Proper REST API status codes for different error types

## Chart Types Supported

- `lineChart` - Line charts
- `barChart` - Bar charts

## Positioning

- **X, Y coordinates**: Optional positioning (defaults to 0,0 if not specified)
- **Width/Height**: Chart dimensions in pixels
- **Z-index**: Layer ordering for overlapping charts

## Integration with Claude Desktop

This server is designed to work with Claude Desktop through MCP. The endpoints provide:

1. **Simple JSON responses** that are easy to parse
2. **Consistent error handling** with helpful messages
3. **RESTful API design** following standard conventions
4. **Comprehensive documentation** via FastAPI's auto-generated docs

## File Structure

```
server/
├── main.py              # Main FastAPI application
├── test_server.py       # Manual testing script
├── start_server.bat     # Windows startup script
└── README.md           # This file
```

## Dependencies

- FastAPI - Web framework
- Uvicorn - ASGI server
- Pydantic - Data validation
- Requests - HTTP client (for testing)
- HTTPX - HTTP client (for pytest)

## Notes

- Reports are created from the `baseline_report` template
- All operations are performed in memory and persisted to disk
- The server maintains an active session of loaded reports
- Chart positioning uses pixel coordinates relative to the page
