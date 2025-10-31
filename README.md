# RemoveBG - AI-Powered Background Removal

A full-stack application for automated background removal using state-of-the-art deep learning models. Built with FastAPI, React, and the rembg library for production-ready image processing.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.1-61DAFB.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.1-646CFF.svg)](https://vitejs.dev/)

---

## Overview

RemoveBG provides three integrated components for AI-powered background removal:

- **REST API** - Production-ready FastAPI service with comprehensive endpoints
- **Web Interface** - Modern React frontend with drag-and-drop support
- **Jupyter Notebooks** - Interactive environment for experimentation and batch processing

The system leverages the [rembg](https://github.com/danielgatis/rembg) library, which uses the U^2-Net model for accurate foreground/background segmentation without requiring manual annotations.

## Key Features

- **Multiple Input Methods** - Base64 encoding, file upload, or batch processing
- **High-Quality Output** - PNG with alpha transparency, optional alpha matting for refined edges
- **RESTful API** - OpenAPI/Swagger documentation, CORS-enabled for web integration
- **Modern UI** - Responsive React interface with real-time preview
- **Flexible Deployment** - Run locally, containerize, or deploy to cloud platforms
- **Performance Optimized** - Async handlers, GPU support, configurable processing options

## Quick Start

### Prerequisites

- Python 3.11+ (avoid 3.12 due to numba compatibility)
- Node.js 18+ and npm
- 4GB+ RAM recommended
- (Optional) CUDA-capable GPU for 3-5x performance boost

### Run the Full Stack

```bash
# 1. Clone the repository
git clone <repository-url>
cd RemoveBG

# 2. Start the API
cd rembg-api
python3.11 -m venv venv_rembg
source venv_rembg/bin/activate  # On Windows: venv_rembg\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Start the frontend (new terminal)
cd rembg-frontend
npm install
npm run dev

# 4. Access the application
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
```

On first run, the rembg library will download the U^2-Net model (~180MB). This is a one-time operation.

## Architecture

### System Design

```
┌─────────────────┐      HTTP/REST      ┌──────────────────┐
│                 │ ←─────────────────→ │                  │
│  React Frontend │                     │   FastAPI Backend│
│   (Vite + SPA)  │                     │   (Async Python) │
│                 │                     │                  │
└─────────────────┘                     └────────┬─────────┘
                                                 │
                                                 ▼
                                        ┌─────────────────┐
                                        │  rembg Library  │
                                        │  (U^2-Net DL)   │
                                        └─────────────────┘
```

### Backend Architecture

The API follows a layered architecture with clear separation of concerns:

```
rembg-api/
├── app/
│   ├── main.py              # FastAPI app, CORS, middleware, lifecycle hooks
│   ├── routers/
│   │   └── background.py    # REST endpoints, request/response handling
│   ├── services/
│   │   └── image_processor.py  # Business logic, rembg integration
│   ├── models/
│   │   └── schemas.py       # Pydantic models for validation
│   └── utils/
│       └── validators.py    # Input validation utilities
```

**Design Patterns:**
- **Service Layer Pattern** - Business logic isolated from HTTP concerns
- **Dependency Injection** - Clean separation via FastAPI's DI system
- **Singleton Service** - Single shared ImageProcessingService instance
- **Async/Await** - Non-blocking I/O for concurrent request handling

### Frontend Architecture

```
rembg-frontend/
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Root component
│   ├── pages/
│   │   └── Home.jsx          # Main page container
│   └── components/
│       └── ImageUploader.jsx # Core upload/processing component
```

**Component Hierarchy:** `App → Home → ImageUploader`

## API Documentation

### Endpoints

#### POST `/api/v1/remove-background`

Remove background from base64-encoded image.

**Request:**
```json
{
  "image_base64": "iVBORw0KGgoAAAANSUhEU...",
  "output_format": "base64",
  "post_process": true
}
```

**Response:**
```json
{
  "success": true,
  "output_format": "base64",
  "image_data": "iVBORw0KGgoAAAANSUhEU...",
  "processing_time": 2.35,
  "original_size": [1920, 1080],
  "message": "Image traitée avec succès"
}
```

#### POST `/api/v1/remove-background-file`

Remove background from uploaded file (returns PNG binary).

**Request:** `multipart/form-data` with `file` and optional `post_process` boolean

**Response:** PNG image with transparency (Content-Type: `image/png`)

#### GET `/api/v1/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "background-removal-api",
  "version": "1.0.0"
}
```

### Processing Options

- **post_process** (boolean, default: false)
  - When enabled, applies alpha matting for cleaner edge refinement
  - Adds ~30% processing time but significantly improves quality
  - Recommended for portraits and subjects with fine details (hair, fur)

### Limits

- **Max image size:** 16 megapixels (4096x4096)
- **Min dimensions:** 10x10 pixels
- **Supported formats:** PNG, JPEG, WEBP, BMP
- **Request timeout:** 30 seconds

### Interactive Documentation

Once the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs (try endpoints directly)
- **ReDoc:** http://localhost:8000/redoc (detailed documentation)
- **OpenAPI Schema:** http://localhost:8000/openapi.json

## Development Setup

### Backend Development

```bash
cd rembg-api

# Create and activate virtual environment
python3.11 -m venv venv_rembg
source venv_rembg/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: run directly
python -m app.main
```

**Development workflow:**
1. Modify code in `app/`
2. Server auto-reloads on file changes (--reload flag)
3. Test via Swagger UI or curl
4. Check logs in terminal

### Frontend Development

```bash
cd rembg-frontend

# Install dependencies
npm install

# Start dev server with HMR
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

**Development workflow:**
1. Ensure API is running on port 8000
2. Modify React components in `src/`
3. Browser auto-refreshes via Vite HMR
4. Test in browser at http://localhost:5173

### Jupyter Notebook Environment

```bash
# Create virtual environment (root directory)
python3 -m venv venv_rembg
source venv_rembg/bin/activate

# Install dependencies
pip install -r requirements.txt

# Launch Jupyter
jupyter lab
```

**Notebook workflow:**
1. Place images in `images_test/` directory
2. Open and run `test_rembg.ipynb`
3. View processed images in `images_output/`
4. Analyze performance metrics in notebook output

## Testing

### API Tests

```bash
cd rembg-api
pytest tests/ -v

# Run specific test file
pytest tests/test_image_processor.py -v

# Run with coverage
pytest --cov=app tests/
```

### Manual Testing with curl

```bash
# Test file upload endpoint
curl -X POST "http://localhost:8000/api/v1/remove-background-file" \
  -F "file=@test_image.jpg" \
  -F "post_process=true" \
  --output result.png

# Test base64 endpoint
curl -X POST "http://localhost:8000/api/v1/remove-background" \
  -H "Content-Type: application/json" \
  -d '{
    "image_base64": "'$(base64 -i test_image.jpg)'",
    "output_format": "base64",
    "post_process": false
  }' | jq
```

### Integration Testing

```bash
# Start API and frontend, then test via browser
# 1. Upload image via UI
# 2. Verify result displays correctly
# 3. Check browser console for errors
# 4. Monitor API logs for request/response
```

## Performance

### Benchmarks (CPU - Apple Silicon M1)

| Image Size | Processing Time | Post-Process |
|-----------|----------------|--------------|
| 800x600 | 2-3 seconds | +0.8s |
| 1920x1080 | 5-8 seconds | +2.0s |
| 4000x3000 | 15-25 seconds | +7.0s |

### Optimization Strategies

1. **GPU Acceleration** (3-5x speedup)
   ```bash
   pip install onnxruntime-gpu
   ```

2. **Image Preprocessing**
   - Resize large images before processing
   - Compress JPEG quality to reduce file size

3. **Caching**
   - Implement Redis cache for repeat requests
   - Use content-based hashing (MD5) as cache key

4. **Async Queue Processing**
   - Integrate Celery + Redis for background jobs
   - Return job ID immediately, poll for results

5. **Production Deployment**
   ```bash
   # Run with multiple workers
   uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
   ```

## Troubleshooting

### Common Issues

**NumPy Version Conflicts**
```
Error: AttributeError: _ARRAY_API not found
Solution: pip install "numpy<2.0"
```

**Module Not Found: 'app'**
```
Error: ModuleNotFoundError: No module named 'app'
Solution: Run uvicorn from rembg-api/ directory
```

**Slow Processing**
```
Issue: Images taking >30 seconds to process
Solutions:
  1. Resize images to max 2000x2000 before upload
  2. Disable post_process parameter
  3. Install GPU acceleration (onnxruntime-gpu)
  4. Check CPU/memory usage (htop, top)
```

**CORS Errors in Frontend**
```
Error: Access to fetch blocked by CORS policy
Solution: Verify API CORS middleware in app/main.py:
  - allow_origins should include frontend URL
  - For dev: allow_origins=["*"]
  - For prod: allow_origins=["https://yourdomain.com"]
```

**Frontend Port Already in Use**
```
Error: Port 5173 is already in use
Solution: Vite will try next available port (5174, 5175...)
Or: Kill process using port: lsof -ti:5173 | xargs kill -9
```

## Deployment

### Docker Deployment (Recommended)

```dockerfile
# API Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY rembg-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY rembg-api/app ./app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t rembg-api .
docker run -p 8000:8000 rembg-api
```

### Production Considerations

1. **Environment Variables**
   - Use `.env` for configuration (API keys, database URLs)
   - Never commit `.env` to version control

2. **Security**
   - Restrict CORS to specific domains
   - Add API authentication (API keys, JWT)
   - Implement rate limiting (slowapi)
   - Validate file types server-side

3. **Monitoring**
   - Add logging to cloud service (CloudWatch, Datadog)
   - Implement health check endpoint
   - Track processing times and error rates

4. **Scalability**
   - Use load balancer for multiple API instances
   - Implement message queue for async processing
   - Consider serverless deployment (AWS Lambda + API Gateway)

## Technology Stack

### Backend
- **Framework:** FastAPI 0.104
- **Web Server:** Uvicorn (ASGI)
- **ML Library:** rembg 2.0.56 (U^2-Net model)
- **Image Processing:** Pillow 10.1, NumPy 1.26
- **Validation:** Pydantic 2.5
- **Testing:** pytest 7.4

### Frontend
- **Framework:** React 19.1
- **Build Tool:** Vite 7.1
- **HTTP Client:** Axios 1.13
- **Language:** JavaScript (ES6+)
- **Styling:** CSS3 (custom)

### ML Model
- **Architecture:** U^2-Net (Salient Object Detection)
- **Framework:** ONNX Runtime
- **Model Size:** ~180MB
- **Input:** RGB images (any size)
- **Output:** Alpha matte (transparency mask)

## Contributing

Contributions are welcome! This project is open to improvements in:

- Performance optimization (caching, GPU acceleration)
- Additional image processing features (batch upload, multiple formats)
- UI/UX enhancements
- Test coverage expansion
- Documentation improvements

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Update documentation if needed
7. Submit a pull request

### Code Standards

- **Python:** Follow PEP 8, use type hints
- **JavaScript:** Use ESLint configuration provided
- **Documentation:** Add docstrings to all functions/classes
- **Testing:** Maintain >80% test coverage

## License

This project is open source and available under the MIT License.

## Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) - Background removal library by Daniel Gatis
- [U^2-Net](https://github.com/xuebinqin/U-2-Net) - Deep learning architecture by Xuebin Qin et al.
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework by Sebastián Ramírez
- [React](https://reactjs.org/) - UI library by Meta

## Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing documentation in `/rembg-api/README.md`
- Review the CLAUDE.md file for development guidance

---

**Note:** This is a development/research project. For production use, implement proper authentication, rate limiting, and error handling based on your specific requirements.
