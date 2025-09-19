# FastAPI Backend Service

A modern FastAPI backend service with health check and file upload capabilities, using `uv` for dependency management.

## Features

- **Health Check Endpoint**: GET `/health` - Returns service status
- **File Upload Endpoint**: POST `/api/upload` - Accepts file uploads and returns filename + size
- **Multiple File Upload**: POST `/api/upload-multiple` - Handles multiple file uploads
- **Interactive API Documentation**: Available at `/docs` (Swagger UI) and `/redoc` (ReDoc)
- **CORS Support**: Configured for cross-origin requests
- **Modern Python Packaging**: Uses `uv` for fast dependency management

## Prerequisites

- Python 3.8 or higher
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (Recommended)

1. **Install uv** (if you haven't already):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # or on Windows:
   # powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install dependencies**:
   ```bash
   cd backend
   uv sync
   ```

### Using pip (Alternative)

1. **Create and activate a virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

## Running the Application

### Development Server (with auto-reload)

Using uv:
```bash
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Using pip:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

Using uv:
```bash
cd backend
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Using pip:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`

## API Endpoints

### Root Endpoint
- **URL**: `GET /`
- **Description**: Returns welcome message and API information
- **Response**: 
  ```json
  {
    "message": "Welcome to FastAPI Backend Service",
    "version": "1.0.0",
    "docs": "/docs",
    "health": "/health"
  }
  ```

### Health Check
- **URL**: `GET /health`
- **Description**: Returns service health status
- **Response**: 
  ```json
  {
    "status": "ok"
  }
  ```

### Single File Upload
- **URL**: `POST /api/upload`
- **Description**: Accepts a single file upload via multipart/form-data
- **Request**: Form data with a file field
- **Response**: 
  ```json
  {
    "filename": "example.jpg",
    "size": 12345,
    "content_type": "image/jpeg",
    "message": "File uploaded successfully"
  }
  ```

### Multiple File Upload
- **URL**: `POST /api/upload-multiple`
- **Description**: Accepts multiple file uploads via multipart/form-data
- **Request**: Form data with multiple file fields
- **Response**: 
  ```json
  {
    "files": [
      {
        "filename": "file1.jpg",
        "size": 12345,
        "content_type": "image/jpeg"
      }
    ],
    "total_files": 1,
    "total_size": 12345,
    "message": "Successfully uploaded 1 files"
  }
  ```

## Interactive API Documentation

Once the server is running, you can access:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## Testing the Endpoints

### Using curl

**Health Check:**
```bash
curl http://localhost:8000/health
```

**File Upload:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

### Using the Interactive Docs

1. Go to `http://localhost:8000/docs`
2. Click on the endpoint you want to test
3. Click "Try it out"
4. Fill in the required parameters
5. Click "Execute"

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application instance
│   └── routes/
│       ├── __init__.py
│       ├── health.py        # Health check endpoint
│       └── upload.py        # File upload endpoints
├── pyproject.toml           # uv configuration and dependencies
└── README.md               # This file
```

## Development

### Adding New Dependencies

Using uv:
```bash
uv add package-name
```

### Development Dependencies

Using uv:
```bash
uv add --dev pytest httpx pytest-asyncio
```

### Running Tests (when implemented)

```bash
uv run pytest
```

## Environment Variables

The application supports the following environment variables:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `RELOAD`: Enable auto-reload for development (default: False)

## Production Deployment

For production deployment, consider:

1. **Using a production WSGI/ASGI server** like Gunicorn with Uvicorn workers
2. **Setting appropriate CORS origins** instead of allowing all origins
3. **Adding authentication and authorization** for sensitive endpoints
4. **Implementing request rate limiting**
5. **Adding logging and monitoring**
6. **Using environment variables** for configuration

Example production command:
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.