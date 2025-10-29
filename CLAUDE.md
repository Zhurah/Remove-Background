# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project provides two components for AI-powered background removal using the `rembg` library:

1. **Jupyter Notebook Environment** - Interactive testing and experimentation (`test_rembg.ipynb`)
2. **REST API** (`rembg-api/`) - FastAPI-based production service for background removal

Both components use the same core `rembg` library but serve different purposes: notebooks for exploration/testing, API for integration.

## Environment Setup

**Python Version:** 3.10 to 3.13 recommended (avoid 3.12 for numba compatibility, 3.14 not supported)

### Notebook Environment Setup

```bash
# Create virtual environment
python3 -m venv venv_rembg

# Activate on macOS/Linux
source venv_rembg/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### API Environment Setup

```bash
cd rembg-api

# Create virtual environment (preferably Python 3.11)
python3.11 -m venv venv_rembg

# Activate
source venv_rembg/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Important Dependency Notes:**
- NumPy version conflicts may occur: `rembg` requires numpy 2.x, but some dependencies require numpy 1.x
- If you encounter `AttributeError: _ARRAY_API not found`, downgrade: `pip install "numpy<2.0"`
- First run downloads AI models (~180MB) which may take time

## Development Workflows

### Running Jupyter Notebooks

```bash
# Start Jupyter Lab (recommended)
jupyter lab

# Or Jupyter Notebook
jupyter notebook
```

**Key Notebook:** `test_rembg.ipynb`
- Batch image processing with statistics tracking
- Side-by-side comparison visualization with transparency checkerboard
- URL-based image processing support
- Performance metrics (processing time, file sizes, dimensions)

**Workflow:**
1. Place test images in `images_test/` directory
2. Run notebook cells sequentially
3. Processed images saved to `images_output/` with `_no_bg.png` suffix

### Running the API

```bash
cd rembg-api

# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: run directly with Python
python -m app.main

# Production mode (multiple workers)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## API Architecture

The FastAPI application follows a standard layered architecture:

```
rembg-api/
├── app/
│   ├── main.py              # FastAPI app initialization, CORS, middleware, lifecycle
│   ├── routers/             # API endpoints (background.py)
│   ├── services/            # Business logic (image_processor.py with rembg integration)
│   ├── models/              # Pydantic schemas for request/response validation
│   └── utils/               # Helper utilities
├── tests/                   # pytest test suite
├── requirements.txt
└── README.md               # Comprehensive API documentation
```

**Key Architectural Patterns:**
- **Dependency Injection:** FastAPI's dependency system for clean separation
- **Request/Response Models:** Pydantic for validation and serialization
- **Middleware Chain:** CORS, logging, custom request/response processing
- **Async Handlers:** All endpoints are async for better concurrency

**API Endpoints:**
- `POST /api/v1/remove-background` - Accept base64-encoded images, return JSON
- `POST /api/v1/remove-background-file` - Accept multipart file upload, return PNG binary
- `GET /api/v1/health` - Health check endpoint

**Processing Options:**
- `post_process` parameter: Enables alpha matting for cleaner edges (slower but higher quality)
- `output_format`: base64, binary, or url (url not implemented, returns 501)

**Limits:**
- Max image size: 16 megapixels (4096x4096)
- Min dimensions: 10x10 pixels
- Request timeout: 30 seconds

## Image Processing Details

**Supported Input Formats:** PNG, JPEG/JPG, WEBP, BMP

**Output Format:** PNG with RGBA (transparency support)

**Performance Metrics (CPU):**
- 800x600 image: ~2-3 seconds
- 1920x1080 image: ~5-8 seconds
- 4000x3000 image: ~15-25 seconds

**Optimization Opportunities:**
- GPU acceleration: Install `onnxruntime-gpu` for 3-5x speedup
- Image resizing: Reduce dimensions before processing
- Disable `post_process` for faster results
- Caching: Store results to avoid reprocessing
- Async queues: Celery + Redis for background processing

## Testing

### API Tests
```bash
cd rembg-api
pytest tests/ -v
```

### Manual API Testing

**Using curl:**
```bash
# File upload endpoint
curl -X POST "http://localhost:8000/api/v1/remove-background-file" \
  -F "file=@image.jpg" \
  -F "post_process=true" \
  --output result.png

# Base64 endpoint
curl -X POST "http://localhost:8000/api/v1/remove-background" \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "'$(base64 -i image.jpg)'", "output_format": "base64"}'
```

**Using Swagger UI:**
1. Navigate to http://localhost:8000/docs
2. Click endpoint, then "Try it out"
3. Upload image and click "Execute"

## Git Configuration

**Main Branch:** `main`

**Untracked Files:**
- `.gitignore` - Should be committed
- `images_test/` - Test images directory
- `rembg-api/` - API implementation
- `requirements.txt` - Root level dependencies

## Common Issues

**NumPy Version Conflicts:**
- Symptom: `AttributeError: _ARRAY_API not found`
- Solution: `pip install "numpy<2.0"`

**"No module named 'app'" Error:**
- Cause: Incorrect working directory
- Solution: Run uvicorn from `rembg-api/` directory or use `cd rembg-api && uvicorn app.main:app`

**Slow API Performance:**
- Large images (>2000x2000) are CPU-intensive
- Consider: resizing images, disabling post_process, or GPU acceleration

**numba Compatibility Issue:**
- Symptom: Import errors with numba
- Solution: Use Python 3.11 instead of 3.12

## Platform Notes

- Developed on macOS (Darwin 24.6.0, Apple Silicon ARM architecture)
- Project should be cross-platform compatible
- Virtual environments are excluded from git (`venv_rembg/`)
