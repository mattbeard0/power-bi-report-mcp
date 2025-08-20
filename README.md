# Power BI Report MCP

A Model Context Protocol (MCP) server for Power BI report operations, providing programmatic access to create, modify, and manage Power BI reports through a FastAPI-based interface.

## 🚀 Overview

This project enables automated Power BI report creation and manipulation through a standardized API. It's designed to work with MCP clients and provides endpoints for:

- **Report Management**: Create new reports from baseline templates
- **Page Operations**: Manage report pages and their properties
- **Chart Creation**: Add line charts and bar charts with custom positioning
- **Visual Management**: Resize and modify chart dimensions
- **Table Operations**: Work with dataset tables and relationships

## ✨ Key Features

- **FastAPI Backend**: Modern, fast web framework with automatic API documentation
- **MCP Compatible**: Designed to work with Model Context Protocol clients
- **Template-Based**: Creates reports from baseline Power BI templates
- **RESTful API**: Clean, intuitive endpoints for all operations
- **Comprehensive Testing**: Unit and integration tests with pytest
- **Type Safety**: Full Pydantic models for request/response validation

## 🏃‍♂️ Quick Start

### Prerequisites

- Python 3.8+
- Power BI Desktop (for baseline template creation)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mattbeard0/power-bi-report-mcp.git
   cd power-bi-report-mcp
   ```

2. **Install dependencies**
   ```bash
   cd python-power-bi-mcp
   pip install -r requirements.txt
   ```
   
   *Note: If you encounter issues with the `tmdlparser` dependency, you may need to install it separately or use an alternative TMDL parsing solution.*

3. **Start the server**
   ```bash
   cd server
   python main.py
   ```

   The server will be available at `http://localhost:8000`

4. **Access API documentation**
   - Interactive docs: http://localhost:8000/docs
   - ReDoc format: http://localhost:8000/redoc

### Basic Usage

```bash
# Create a new report
curl -X POST "http://localhost:8000/make_new_report" \
  -H "Content-Type: application/json" \
  -d '{"name": "my_report"}'

# Add a bar chart
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

## 📁 Project Structure

```
power-bi-report-mcp/
├── python-power-bi-mcp/           # Main Python package
│   ├── baseline_report/            # Template Power BI report
│   ├── models/                     # Pydantic data models
│   ├── server/                     # FastAPI server implementation
│   │   ├── routers/               # API route handlers
│   │   ├── schemas/               # Request/response schemas
│   │   └── README.md              # Detailed server documentation
│   ├── tests/                     # Test suite
│   └── requirements.txt           # Python dependencies
├── report/                        # Generated reports directory
└── README.md                      # This file
```

## 🛠️ Development

### Running Tests

```bash
# Run all tests
cd python-power-bi-mcp
python -m pytest

# Run with coverage
python -m pytest --cov=models --cov=server

# Run specific test types
python -m pytest -m unit        # Unit tests only
python -m pytest -m integration # Integration tests only
```

### API Endpoints

The server provides several endpoint categories:

- **Report Operations**: `/make_new_report`, `/get_reports`
- **Page Management**: `/get_page_details`, `/get_pages`
- **Chart Operations**: `/add_chart`, `/change_chart_size`
- **Table Operations**: `/get_tables`, `/get_table_columns`

For complete API documentation, see [`python-power-bi-mcp/server/README.md`](python-power-bi-mcp/server/README.md).

## 🔧 Configuration

The server can be configured through environment variables or by modifying the server startup parameters in `main.py`:

- **Host**: Default `0.0.0.0`
- **Port**: Default `8000`
- **Report Templates**: Located in `baseline_report/`

## 📋 Requirements

Key dependencies include:

- FastAPI - Web framework
- fastapi-mcp - MCP integration
- Uvicorn - ASGI server
- Pydantic - Data validation
- tmdlparser - Power BI TMDL file parsing

See [`requirements.txt`](python-power-bi-mcp/requirements.txt) for the complete list.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`python -m pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is open source. Please see the repository for license details.

## 🔗 Links

- [Detailed Server Documentation](python-power-bi-mcp/server/README.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 🆘 Support

For questions, issues, or contributions, please open an issue on GitHub.