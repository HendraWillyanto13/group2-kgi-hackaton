# KGI Hackaton Group 2

A full-stack monorepo template with FastAPI backend and placeholder frontend directory, built with Python 3.12 development container support.

## Features

- ✅ **FastAPI Backend**: Modern, fast web framework with file upload support
- ✅ **Health Check Endpoint**: GET `/health` returning `{"status": "ok"}`
- ✅ **File Upload Endpoints**: Single and multiple file upload support
- ✅ **PDF Processing**: PDF upload, text extraction, and embeddings generation
- ✅ **Document Management**: Manage Source page with filtering, sorting, and deletion
- ✅ **FAISS Vector Storage**: Vector embeddings storage and retrieval
- ✅ **React Frontend**: Modern React application with routing and UI components
- ✅ **UV Package Manager**: Fast Python package management
- ✅ **Interactive API Docs**: Auto-generated Swagger UI and ReDoc
- ✅ **CORS Support**: Configured for cross-origin requests
- ✅ **Development Container**: Python 3.12, Node.js, SQLite support

## Project Structure

```
├── backend/                 # FastAPI service
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── routes/
│   │   │   ├── health.py   # Health check endpoint
│   │   │   ├── upload.py   # File upload endpoints
│   │   │   ├── detection.py # Object detection endpoints
│   │   │   └── pdf_embeddings.py # PDF processing and embeddings
│   │   └── utils/
│   │       ├── azure_openai_service.py # Azure OpenAI integration
│   │       ├── faiss_storage.py # FAISS vector storage
│   │       └── pdf_processor.py # PDF processing utilities
│   ├── documents/          # Processed PDF storage
│   ├── faiss/             # FAISS vector indices
│   ├── metadata/          # PDF metadata storage
│   ├── uploads/           # Uploaded image files
│   ├── pyproject.toml     # uv dependencies and configuration
│   └── README.md          # Backend-specific documentation
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Application pages
│   │   │   ├── UploadPage.jsx    # Image upload page
│   │   │   ├── UploadList.jsx    # Image list page
│   │   │   └── ManageSource.jsx  # Document management page
│   │   ├── lib/           # Utilities and API client
│   │   └── hooks/         # Custom React hooks
│   ├── package.json       # Frontend dependencies
│   └── README.md          # Frontend setup instructions
├── README.md              # This file
├── docker-compose.yml     # Docker services configuration
└── issues#1.md           # Feature requirements and tasks
```

## Quick Start

### Backend Setup

1. **Using the development container (recommended)**:
   - Open this project in VS Code
   - Install "Dev Containers" extension
   - Press `Ctrl+Shift+P` and select "Dev Containers: Reopen in Container"
   - Wait for container to build

2. **Install backend dependencies and start server**:
   ```bash
   cd backend
   uv sync
   uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**:
   - API Base: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Frontend Setup

1. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server**:
   ```bash
   npm run dev
   ```

3. **Access the frontend**:
   - Frontend App: http://localhost:5173
   - Features available:
     - Upload Image: Upload and detect objects in images
     - Upload Document: Process PDF documents with embeddings
     - Ask: Query functionality (placeholder)
     - Manage Source: Document management with filtering, sorting, and deletion

### ManageSource Feature

The Manage Source page provides comprehensive document management capabilities:

- **Document List**: View all processed PDF documents with metadata
- **Filtering**: Filter documents by name, upload date, and file size
- **Sorting**: Sort documents by name, date, or size (ascending/descending)
- **Multiple Selection**: Select multiple documents for batch operations
- **Document Preview**: Open PDF documents in a new tab for preview
- **Document Deletion**: Delete selected documents with confirmation dialog
- **Toast Notifications**: Success/failure notifications for operations
- **Navigation**: Seamless navigation between pages

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and API info |
| GET | `/health` | Health check - returns `{"status": "ok"}` |
| POST | `/api/upload` | Single file upload - returns filename + size |
| POST | `/api/upload-multiple` | Multiple file uploads |
| POST | `/api/process-pdf-embeddings` | Process PDF file and generate embeddings |
| GET | `/api/processed-pdfs` | List all processed PDF documents |
| GET | `/api/processed-pdfs/{file_hash}` | Get detailed information about a processed PDF |
| DELETE | `/api/processed-pdfs/{file_hash}` | Delete a processed PDF and all associated data |
| GET | `/api/detection/{filename}` | Get object detections for an image |
| POST | `/api/metadata/{filename}` | Update objects metadata |
| GET | `/docs` | Swagger UI documentation |
| GET | `/redoc` | ReDoc documentation |
| GET | `/documents/{filename}` | Serve processed PDF files |
| GET | `/uploads/{filename}` | Serve uploaded image files |

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# File upload
curl -X POST "http://localhost:8000/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/file.jpg"
```

### Using the Interactive Docs

1. Start the backend server
2. Go to http://localhost:8000/docs
3. Try out the endpoints directly in the browser

## Development

### Backend Development

```bash
cd backend
uv sync                    # Install dependencies
uv run uvicorn app.main:app --reload  # Start development server
```

### Adding Dependencies

```bash
cd backend
uv add package-name        # Add runtime dependency
uv add --dev package-name  # Add development dependency
```

### Using UV Package Manager

UV is a fast Python package installer and resolver:

```bash
# Install packages
uv pip install package_name

# Install from requirements.txt  
uv pip install -r requirements.txt

# Create a virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate
```

## Development Container Features

This project uses a VS Code development container with:
- **Base Image**: `mcr.microsoft.com/devcontainers/python:1-3.12-bookworm`
- **Python 3.12**: Latest Python version
- **Node.js LTS**: For frontend development
- **SQLite**: Database support
- **UV Package Manager**: Fast Python package management
- **Port Forwarding**: Ports 3000, 5173, 8000 automatically forwarded

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running the FastAPI application
- **Python Multipart**: For handling file uploads
- **UV**: Fast Python package installer and resolver

### Development Environment
- **Python 3.12**: Latest Python version
- **VS Code Dev Containers**: Consistent development environment
- **GitHub Copilot**: AI-powered coding assistance
- **SQLite**: Database support
- **Node.js**: For frontend development

## Production Considerations

For production deployment:

1. **Security**: Configure proper CORS origins, add authentication
2. **Performance**: Use Gunicorn with Uvicorn workers
3. **Monitoring**: Add logging, metrics, and health monitoring
4. **Rate Limiting**: Implement request rate limiting
5. **File Storage**: Consider cloud storage for uploaded files
6. **Environment Variables**: Use proper configuration management

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test your changes
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## Getting Help

- Check the backend README: `backend/README.md`
- View API documentation: http://localhost:8000/docs (when server is running)
- FastAPI Documentation: https://fastapi.tiangolo.com/
- UV Documentation: https://docs.astral.sh/uv/

## License

This project is licensed under the MIT License.
